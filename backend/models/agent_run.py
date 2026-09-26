"""
Agent run logging models.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    FAILED = "FAILED"


class AgentRunRecord(BaseModel):
    """Represents an execution run of the intelligent notification agent."""
    run_id: str = Field(..., description="Unique run identifier, e.g. RUN-20260916-103000")
    started_at: str = Field(..., description="ISO timestamp of run initiation")
    completed_at: Optional[str] = Field(default=None, description="ISO timestamp of completion")
    customers_checked: int = Field(default=0, description="Total customers inspected")
    active_customers: int = Field(default=0, description="Active customers skipped")
    suspended_customers: int = Field(default=0, description="Suspended customers found")
    notifications_sent: int = Field(default=0, description="Notifications sent or simulated")
    notifications_skipped: int = Field(default=0, description="Notifications skipped (e.g. duplicate or missing email)")
    notifications_failed: int = Field(default=0, description="Notifications failed due to errors")
    run_status: RunStatus = Field(default=RunStatus.COMPLETED, description="Status of the agent run")
    error_summary: Optional[str] = Field(default=None, description="Summary of errors encountered")
