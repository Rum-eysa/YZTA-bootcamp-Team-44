from app.models.agent import AgentTask, AgentTaskStatus, AgentWorkflow


def test_agent_task_state_helpers_update_status_and_timestamps():
    task = AgentTask(task_type="analyze", payload="{}")

    task.mark_started()
    assert task.status == AgentTaskStatus.PROCESSING
    assert task.started_at is not None

    task.mark_completed("done", runtime_ms=12.5, token_count=100)
    assert task.status == AgentTaskStatus.COMPLETED
    assert task.result == "done"
    assert task.runtime_ms == 12
    assert task.token_count == 100

    task.mark_failed("boom")
    assert task.status == AgentTaskStatus.FAILED
    assert task.error_message == "boom"


def test_agent_workflow_state_helpers_update_status():
    workflow = AgentWorkflow(workflow_type="review", config="{}")

    workflow.mark_started()
    assert workflow.status == AgentTaskStatus.PROCESSING

    workflow.mark_completed("workflow done")
    assert workflow.status == AgentTaskStatus.COMPLETED
    assert workflow.result == "workflow done"
