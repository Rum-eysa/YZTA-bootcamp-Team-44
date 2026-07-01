"""Tests for Agent System - BaseAgent, Context Manager, Telemetry, Retry Logic"""
import pytest
from unittest.mock import Mock, patch
from app.services.agent import (
    BaseAgent,
    AgentContextManager,
    AgentTelemetry,
    RetryStrategy,
    agent_service,
)


class MockAgent(BaseAgent):
    """Mock agent for testing"""

    def __init__(self, name: str = "test_agent", max_retries: int = 3, should_fail: bool = False):
        super().__init__(name, max_retries)
        self.should_fail = should_fail
        self.call_count = 0

    async def _run(self, payload):
        self.call_count += 1
        if self.should_fail:
            raise ValueError("Simulated failure")
        return {"result": f"processed_{payload}"}


@pytest.mark.asyncio
async def test_agent_context_manager():
    """Test AgentContextManager basic operations"""
    ctx = AgentContextManager()

    with ctx:
        ctx.set("key1", "value1")
        ctx.set("key2", {"nested": "value"})
        assert ctx.get("key1") == "value1"
        assert ctx.get("key2") == {"nested": "value"}
        assert ctx.get("nonexistent") is None
        assert ctx.get_all() == {"key1": "value1", "key2": {"nested": "value"}}

    # Context should be cleared after exit
    assert ctx.get_all() == {}


@pytest.mark.asyncio
async def test_agent_context_manager_history():
    """Test AgentContextManager history tracking"""
    ctx = AgentContextManager()

    with ctx:
        ctx.set("key1", "value1")

    with ctx:
        ctx.set("key2", "value2")

    history = ctx.get_history()
    assert len(history) == 2
    assert history[0] == {"key1": "value1"}
    assert history[1] == {"key2": "value2"}


@pytest.mark.asyncio
async def test_agent_telemetry():
    """Test AgentTelemetry recording"""
    telemetry = AgentTelemetry()

    telemetry.record_success(150.5, 100)
    assert telemetry.runtime_ms == 150.5
    assert telemetry.token_count == 100
    assert telemetry.success_count == 1
    assert telemetry.total_executions == 1

    telemetry.record_failure("Test error")
    assert telemetry.last_error == "Test error"
    assert telemetry.failure_count == 1
    assert telemetry.total_executions == 2


@pytest.mark.asyncio
async def test_retry_strategy():
    """Test RetryStrategy exponential backoff"""
    strategy = RetryStrategy(max_retries=3, base_delay=1.0, max_delay=10.0)

    # Test delay calculation
    assert strategy.get_delay(1) == 1.0
    assert strategy.get_delay(2) == 2.0
    assert strategy.get_delay(3) == 4.0
    assert strategy.get_delay(4) == 8.0
    assert strategy.get_delay(5) == 10.0  # Capped at max_delay


@pytest.mark.asyncio
async def test_base_agent_successful_execution():
    """Test BaseAgent successful execution with lifecycle hooks"""
    agent = MockAgent("test_agent", max_retries=3, should_fail=False)

    result = await agent.execute("test_payload")

    assert result == {"result": "processed_test_payload"}
    assert agent.call_count == 1
    assert agent.lifecycle_events["before_execute"] == 1
    assert agent.lifecycle_events["after_execute"] == 1
    assert agent.lifecycle_events["on_success"] == 1
    assert agent.lifecycle_events["on_error"] == 0
    assert agent.lifecycle_events["on_retry"] == 0
    assert agent.telemetry.success_count == 1
    assert agent.telemetry.runtime_ms > 0


@pytest.mark.asyncio
async def test_base_agent_retry_logic():
    """Test BaseAgent retry logic with exponential backoff"""
    agent = MockAgent("test_agent", max_retries=2, should_fail=True)

    with pytest.raises(ValueError, match="Simulated failure"):
        await agent.execute("test_payload")

    assert agent.call_count == 3  # Initial + 2 retries
    assert agent.retry_count == 2
    assert agent.lifecycle_events["on_error"] == 3
    assert agent.lifecycle_events["on_retry"] == 2
    assert agent.telemetry.failure_count == 1


@pytest.mark.asyncio
async def test_base_agent_cancel():
    """Test BaseAgent cancellation"""
    agent = MockAgent("test_agent", max_retries=3, should_fail=True)

    # Cancel after first failure
    original_run = agent._run

    async def cancel_after_first(payload):
        if agent.call_count == 1:
            agent.cancel()
        return await original_run(payload)

    agent._run = cancel_after_first

    with pytest.raises(ValueError, match="Simulated failure"):
        await agent.execute("test_payload")

    assert agent.call_count == 1  # Should not retry after cancellation
    assert agent._is_cancelled is True


@pytest.mark.asyncio
async def test_base_agent_reset():
    """Test BaseAgent state reset"""
    agent = MockAgent("test_agent", max_retries=3, should_fail=True)

    try:
        await agent.execute("test_payload")
    except ValueError:
        pass

    assert agent.retry_count > 0
    assert len(agent.context_manager.get_all()) > 0

    agent.reset()

    assert agent.retry_count == 0
    assert agent._is_cancelled is False
    assert len(agent.context_manager.get_all()) == 0


@pytest.mark.asyncio
async def test_base_agent_get_status():
    """Test BaseAgent status reporting"""
    agent = MockAgent("test_agent", max_retries=3, should_fail=False)

    await agent.execute("test_payload")

    status = agent.get_status()
    assert status["name"] == "test_agent"
    assert status["retry_count"] == 0
    assert status["is_cancelled"] is False
    assert status["telemetry"]["success_count"] == 1
    assert status["telemetry"]["total_executions"] == 1
    assert "lifecycle_events" in status


@pytest.mark.asyncio
async def test_agent_service_register_agent():
    """Test AgentService agent registration"""
    agent = MockAgent("test_agent", max_retries=3)

    agent_service.register_agent(agent)

    status = await agent_service.get_agent_status("test_agent")
    assert status is not None
    assert status["name"] == "test_agent"


@pytest.mark.asyncio
async def test_agent_service_execute_task():
    """Test AgentService task execution with registered agent"""
    agent = MockAgent("test_agent", max_retries=3, should_fail=False)
    agent_service.register_agent(agent)

    result = await agent_service.execute_agent_task("test_agent", {"data": "test"})

    assert result["status"] == "completed"
    assert result["result"] == {"result": "processed_{\"data\": \"test\"}"}
    assert "telemetry" in result
    assert result["telemetry"]["success_count"] == 1


@pytest.mark.asyncio
async def test_agent_service_execute_task_failure():
    """Test AgentService task execution with failure"""
    agent = MockAgent("failing_agent", max_retries=1, should_fail=True)
    agent_service.register_agent(agent)

    result = await agent_service.execute_agent_task("failing_agent", {"data": "test"})

    assert result["status"] == "failed"
    assert "error" in result
    assert result["telemetry"]["failure_count"] == 1


@pytest.mark.asyncio
async def test_agent_service_get_all_agents_status():
    """Test AgentService get all agents status"""
    agent1 = MockAgent("agent1", max_retries=3)
    agent2 = MockAgent("agent2", max_retries=3)

    agent_service.register_agent(agent1)
    agent_service.register_agent(agent2)

    all_status = await agent_service.get_all_agents_status()
    assert "agent1" in all_status
    assert "agent2" in all_status
    assert len(all_status) == 2


@pytest.mark.asyncio
async def test_agent_service_nonexistent_agent():
    """Test AgentService with non-existent agent"""
    with pytest.raises(ValueError, match="Agent 'nonexistent' not registered"):
        await agent_service.execute_agent_task("nonexistent", {"data": "test"})

    status = await agent_service.get_agent_status("nonexistent")
    assert status is None
