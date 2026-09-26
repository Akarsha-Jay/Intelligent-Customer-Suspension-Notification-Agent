"""
Notification Decision Engine.

Coordinates the evaluation of customer status, remark analysis, and lifecycle
state to produce a deterministic notification decision.
"""

from typing import Optional
from pydantic import BaseModel
from backend.models.customer import CustomerRecord
from backend.agent.suspension_analyzer import SuspensionAnalyzer, SuspensionAnalysisResult, SuspensionCategory
from backend.agent.state_tracker import StateTracker, DecisionAction


class DecisionOutcome(BaseModel):
    action: DecisionAction
    category: Optional[SuspensionCategory] = None
    analysis: Optional[SuspensionAnalysisResult] = None
    suspension_event_id: Optional[str] = None
    reason: str


class NotificationDecisionEngine:
    """Evaluates whether a notification should be generated, skipped, or logged."""

    def __init__(self, state_tracker: StateTracker):
        self.state_tracker = state_tracker
        self.analyzer = SuspensionAnalyzer()

    def evaluate(self, customer: CustomerRecord) -> DecisionOutcome:
        """Evaluate customer record and determine next agent step."""
        # 1. Check lifecycle & status with StateTracker
        action, event_id, reason = self.state_tracker.evaluate_customer(customer)

        if action == DecisionAction.SKIP_ACTIVE:
            return DecisionOutcome(
                action=action,
                category=None,
                analysis=None,
                suspension_event_id=None,
                reason=reason,
            )

        # Customer is suspended; analyze remark
        analysis = self.analyzer.analyze(customer.remark)

        if action == DecisionAction.SKIP_DUPLICATE:
            return DecisionOutcome(
                action=action,
                category=analysis.category,
                analysis=analysis,
                suspension_event_id=event_id,
                reason=reason,
            )

        if action == DecisionAction.SKIP_MISSING_EMAIL:
            return DecisionOutcome(
                action=action,
                category=analysis.category,
                analysis=analysis,
                suspension_event_id=event_id,
                reason=reason,
            )

        return DecisionOutcome(
            action=DecisionAction.PROCEED_NOTIFICATION,
            category=analysis.category,
            analysis=analysis,
            suspension_event_id=event_id,
            reason=reason,
        )
