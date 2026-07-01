import pytest

from app.services.agent import BaseAgent, AgentContextManager


class SampleAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="sample-agent")
        self.run_calls = 0

    async def _run(self, payload: str) -> str:
        self.run_calls += 1
        self.context_manager.set("payload", payload)
        return payload.upper()


class FailingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="failing-agent", max_retries=2)
        self.run_calls = 0

    async def _run(self, payload: str) -> str:
        self.run_calls += 1
        if self.run_calls < 2:
            raise ValueError("temporary failure")
        return payload.upper()


@pytest.mark.asyncio
async def test_base_agent_executes_lifecycle_and_tracks_context():
    agent = SampleAgent()

    result = await agent.execute("hello")

    assert result == "HELLO"
    assert agent.run_calls == 1
    assert agent.context_manager.get("payload") == "hello"
    assert agent.telemetry.runtime_ms >= 0
    assert agent.telemetry.token_count >= 0
    assert agent.lifecycle_events["before_execute"] == 1
    assert agent.lifecycle_events["after_execute"] == 1


@pytest.mark.asyncio
async def test_base_agent_retries_on_failure_and_records_retry_state():
    agent = FailingAgent()

    result = await agent.execute("retry")

    assert result == "RETRY"
    assert agent.run_calls == 2
    assert agent.retry_count == 1
    assert agent.lifecycle_events["on_retry"] == 1


def test_context_manager_works_as_a_simple_memory_store():
    with AgentContextManager() as context:
        context.set("answer", 42)
        assert context.get("answer") == 42

    assert context.get("answer") is None
