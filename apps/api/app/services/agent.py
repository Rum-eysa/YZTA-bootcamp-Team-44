"""Agent service for future AI agent integration"""
import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, TypeVar

import redis.asyncio as redis

from app.config import settings
from app.logging_config import get_logger
from app.models.agent import AgentTask, AgentWorkflow

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class AgentTelemetry:
    """Stores lightweight runtime telemetry for agent executions."""

    runtime_ms: float = 0.0
    token_count: int = 0
    last_error: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0
    total_executions: int = 0
    memory_usage_mb: Optional[float] = None

    def record_success(self, runtime_ms: float, token_count: int = 0) -> None:
        """Record a successful execution"""
        self.runtime_ms = runtime_ms
        self.token_count = token_count
        self.success_count += 1
        self.total_executions += 1

    def record_failure(self, error: str) -> None:
        """Record a failed execution"""
        self.last_error = error
        self.failure_count += 1
        self.total_executions += 1


class AgentContextManager(AbstractContextManager):
    """Enhanced context store for agent execution state with memory tracking."""

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._history: list[Dict[str, Any]] = []
        self._max_history = 100

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._save_to_history()
        self.clear()
        return False

    def set(self, key: str, value: Any) -> None:
        """Set a context value"""
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value"""
        return self._store.get(key, default)

    def delete(self, key: str) -> None:
        """Delete a context value"""
        if key in self._store:
            del self._store[key]

    def clear(self) -> None:
        """Clear all context values"""
        self._store.clear()

    def get_all(self) -> Dict[str, Any]:
        """Get all context values"""
        return self._store.copy()

    def _save_to_history(self) -> None:
        """Save current state to history"""
        if self._store:
            self._history.append(self._store.copy())
            if len(self._history) > self._max_history:
                self._history.pop(0)

    def get_history(self) -> list[Dict[str, Any]]:
        """Get execution history"""
        return self._history.copy()


class RetryStrategy:
    """Retry strategy configuration with exponential backoff"""

    def __init__(
        self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = self.base_delay * (2 ** (attempt - 1))
        return min(delay, self.max_delay)

    async def wait(self, attempt: int) -> None:
        """Wait with exponential backoff"""
        delay = self.get_delay(attempt)
        await asyncio.sleep(delay)


class BaseAgent(Generic[T], ABC):
    """Abstract base class for AI agents with lifecycle hooks, telemetry, and retries."""

    def __init__(
        self,
        name: str,
        max_retries: int = 3,
        retry_strategy: Optional[RetryStrategy] = None,
    ):
        self.name = name
        self.retry_strategy = retry_strategy or RetryStrategy(max_retries=max_retries)
        self.retry_count = 0
        self.context_manager = AgentContextManager()
        self.telemetry = AgentTelemetry()
        self.lifecycle_events: Dict[str, int] = {
            "before_execute": 0,
            "after_execute": 0,
            "on_error": 0,
            "on_retry": 0,
            "on_success": 0,
        }
        self.logger = logger.bind(agent=self.name)
        self._is_cancelled = False

    async def execute(self, payload: Any) -> T:
        """Execute the agent with retry logic and lifecycle hooks"""
        self.lifecycle_events["before_execute"] += 1
        self.logger.info(
            "starting_agent_execution",
            payload_type=type(payload).__name__,
            agent=self.name,
        )

        started_at = time.perf_counter()

        # Before execute hooks (internal + optional public override)
        await self._before_execute(payload)
        if type(self).before_execute is not BaseAgent.before_execute:
            await self.before_execute(payload)

        while True:
            try:
                # Execute the agent logic
                result = await self._run(payload)

                # Calculate runtime
                runtime_ms = round((time.perf_counter() - started_at) * 1000, 2)

                # Record telemetry (single success entry)
                token_count = self._estimate_token_usage(payload, result)
                self.telemetry.record_success(runtime_ms, token_count)

                # After execute hooks (internal + optional public override)
                await self._after_execute(payload, result)
                has_after_hook = type(self).after_execute is not BaseAgent.after_execute
                if has_after_hook:
                    await self.after_execute(payload, result)

                self.lifecycle_events["after_execute"] += 1
                self.lifecycle_events["on_success"] += 1
                self.logger.info(
                    "agent_execution_completed",
                    agent=self.name,
                    runtime_ms=runtime_ms,
                    token_count=self.telemetry.token_count,
                )

                return result

            except Exception as exc:
                self.logger.exception(
                    "agent_execution_failed", error=str(exc), agent=self.name
                )

                # Check if we should retry
                if (
                    self.retry_count < self.retry_strategy.max_retries
                    and not self._is_cancelled
                ):
                    self.retry_count += 1
                    self.lifecycle_events["on_retry"] += 1

                    # Wait with exponential backoff
                    delay = self.retry_strategy.get_delay(self.retry_count)
                    self.logger.warning(
                        "agent_retry_scheduled",
                        attempt=self.retry_count,
                        max_retries=self.retry_strategy.max_retries,
                        delay_s=delay,
                        agent=self.name,
                    )

                    await self.retry_strategy.wait(self.retry_count)

                    # Retry hook
                    await self._on_retry(payload, exc, self.retry_count)

                    # Continue loop (retry)
                    continue

                # All retries exhausted — record single failure entry and raise
                self.lifecycle_events["on_error"] += 1
                self.telemetry.record_failure(str(exc))
                await self._on_error(payload, exc)
                raise

    @abstractmethod
    async def _run(self, payload: Any) -> T:
        """Abstract method to be implemented by concrete agents"""
        raise NotImplementedError("Subclasses must implement _run method")

    async def _before_execute(self, payload: Any) -> None:
        """Internal lifecycle hook called before execution"""
        self.context_manager.set("payload", payload)
        self.context_manager.set("start_time", time.time())

    async def before_execute(self, payload: Any) -> None:
        """Optional public hook — override in subclasses for custom pre-execution logic"""
        pass

    async def _after_execute(self, payload: Any, result: T) -> None:
        """Internal lifecycle hook called after successful execution"""
        self.context_manager.set("result", result)
        self.context_manager.set("end_time", time.time())

    async def after_execute(self, payload: Any, result: T) -> None:
        """Optional public hook — override in subclasses for custom post-execution logic"""
        pass

    async def _on_error(self, payload: Any, error: Exception) -> None:
        """Lifecycle hook called on error"""
        self.context_manager.set("error", str(error))

    async def _on_retry(self, payload: Any, error: Exception, attempt: int) -> None:
        """Lifecycle hook called before retry"""
        self.context_manager.set(f"retry_{attempt}_error", str(error))

    def _estimate_token_usage(self, payload: Any, result: T) -> int:
        """Estimate token usage based on payload and result size"""
        try:
            payload_str = (
                json.dumps(payload, default=str)
                if not isinstance(payload, str)
                else payload
            )
            result_str = (
                json.dumps(result, default=str)
                if not isinstance(result, str)
                else result
            )
            total_chars = len(payload_str) + len(result_str)
            return total_chars // 4  # Rough estimate: 1 token ≈ 4 characters
        except Exception:
            return 0

    def cancel(self) -> None:
        """Cancel the current agent execution"""
        self._is_cancelled = True
        self.logger.warning("agent_execution_cancelled", agent=self.name)

    def reset(self) -> None:
        """Reset agent state"""
        self.retry_count = 0
        self._is_cancelled = False
        self.context_manager.clear()
        self.logger.info("agent_state_reset", agent=self.name)

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "retry_count": self.retry_count,
            "is_cancelled": self._is_cancelled,
            "telemetry": {
                "runtime_ms": self.telemetry.runtime_ms,
                "token_count": self.telemetry.token_count,
                "success_count": self.telemetry.success_count,
                "failure_count": self.telemetry.failure_count,
                "total_executions": self.telemetry.total_executions,
            },
            "lifecycle_events": self.lifecycle_events.copy(),
            "context_size": len(self.context_manager.get_all()),
        }


class AgentService:
    """Service for managing AI agent tasks and workflows with BaseAgent integration"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._tasks: Dict[str, AgentTask] = {}
        self._agents: Dict[str, BaseAgent] = {}
        self._workflows: Dict[str, AgentWorkflow] = {}

    async def initialize_redis(self):
        """Initialize Redis connection for task queue"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a BaseAgent instance for task execution"""
        self._agents[agent.name] = agent
        logger.info("agent_registered", agent_name=agent.name)

    async def execute_agent_task(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a task using a registered BaseAgent"""
        if agent_name not in self._agents:
            raise ValueError(f"Agent '{agent_name}' not registered")

        agent = self._agents[agent_name]
        task_id = task_id or str(uuid.uuid4())

        # Create task record
        task = AgentTask(
            id=task_id,
            task_type=agent_name,
            payload=json.dumps(payload),
            agent_id=agent.name,
        )
        self._tasks[task_id] = task

        try:
            # Execute agent
            result = await agent.execute(payload)

            # Update task with success
            task.mark_completed(
                result=json.dumps(result, default=str),
                runtime_ms=agent.telemetry.runtime_ms,
                token_count=agent.telemetry.token_count,
            )

            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "telemetry": agent.telemetry.__dict__,
            }

        except Exception as e:
            # Update task with failure
            task.mark_failed(str(e))
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "telemetry": agent.telemetry.__dict__,
            }

    async def create_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        application_id: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 5,
    ) -> AgentTask:
        """Create a new agent task and initialize its basic lifecycle state."""
        task = AgentTask(
            id=str(uuid.uuid4()),
            task_type=task_type,
            payload=json.dumps(payload),
            application_id=application_id,
            user_id=user_id,
            priority=priority,
        )
        task.mark_started()
        self._tasks[task.id] = task
        return task

    async def enqueue_task(self, task: AgentTask) -> bool:
        """Add task to Redis queue for processing"""
        if not self.redis_client:
            await self.initialize_redis()

        # Placeholder for Redis queue operation
        # await self.redis_client.lpush(f"agent_queue:{task.task_type}", task.id)
        return True

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and result from the in-memory task object."""
        task = self._tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.id,
            "status": task.status,
            "task_type": task.task_type,
            "result": task.result,
            "error_message": task.error_message,
            "retry_count": task.retry_count,
            "runtime_ms": task.runtime_ms,
            "token_count": task.token_count,
        }

    async def create_workflow(
        self,
        workflow_type: str,
        config: Dict[str, Any],
        application_id: Optional[str] = None,
        triggered_by: Optional[str] = None,
    ) -> AgentWorkflow:
        """Create a new multi-agent workflow"""
        workflow = AgentWorkflow(
            workflow_type=workflow_type,
            config=json.dumps(config),
            application_id=application_id,
            triggered_by=triggered_by,
        )
        self._workflows[workflow.id] = workflow
        return workflow

    async def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a registered agent"""
        if agent_name not in self._agents:
            return None
        return self._agents[agent_name].get_status()

    async def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents"""
        return {name: agent.get_status() for name, agent in self._agents.items()}

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()


# Global agent service instance
agent_service = AgentService()
