"""
Agent API Endpoints.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.models.agent_run import AgentRunRecord

router = APIRouter(prefix="/agent", tags=["Agent"])


def get_dependencies():
    from backend.main import agent_runner, db_manager
    return agent_runner, db_manager


@router.post("/run")
def trigger_agent_run():
    """
    Trigger a full cycle execution of the Intelligent Notification Agent.
    """
    runner, db = get_dependencies()
    if runner.is_running:
        raise HTTPException(status_code=409, detail="Agent is already executing a run cycle.")

    run_record = runner.run()
    return {
        "message": "Agent execution cycle completed.",
        "run": run_record.model_dump(),
    }


@router.get("/status")
def get_agent_status():
    """Get current agent operational status and last execution timestamp."""
    runner, db = get_dependencies()
    latest_run = db.get_latest_agent_run()

    return {
        "status": "RUNNING" if runner.is_running else "IDLE",
        "is_busy": runner.is_running,
        "last_run": latest_run.model_dump() if latest_run else None,
    }


@router.get("/runs")
def list_agent_runs(limit: int = 50):
    """Retrieve history of previous agent executions."""
    _, db = get_dependencies()
    runs = db.get_agent_runs(limit=limit)
    return {
        "total": len(runs),
        "items": [r.model_dump() for r in runs],
    }
