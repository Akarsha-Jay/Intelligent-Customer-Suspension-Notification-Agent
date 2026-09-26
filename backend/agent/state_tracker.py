"""
Customer Lifecycle State Tracker & Duplicate Notification Prevention.

Enforces:
1. Active customers are always skipped.
2. If Active -> Suspended: Triggers a new suspension event.
3. If Suspended -> Suspended (subsequent agent run): Duplicate is detected and skipped.
4. If Suspended -> Active -> Suspended: Reactivation followed by suspension triggers
   a NEW suspension event with a distinct ID, allowing a new notification.
"""

import time
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, Tuple
from backend.models.customer import CustomerRecord
from backend.storage.database import DatabaseManager


class DecisionAction(str, Enum):
    PROCEED_NOTIFICATION = "PROCEED_NOTIFICATION"
    SKIP_ACTIVE = "SKIP_ACTIVE"
    SKIP_DUPLICATE = "SKIP_DUPLICATE"
    SKIP_MISSING_EMAIL = "SKIP_MISSING_EMAIL"


class StateTracker:
    """Tracks customer lifecycle states and manages suspension event IDs."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def evaluate_customer(self, customer: CustomerRecord) -> Tuple[DecisionAction, Optional[str], str]:
        """
        Evaluate customer status against lifecycle state history.
        Returns: (DecisionAction, suspension_event_id, reasoning_message)
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        land_number = customer.land_number.strip()
        state = self.db.get_lifecycle_state(land_number)

        # 1. Customer is Active
        if customer.is_active():
            # If customer was previously suspended, close the suspension cycle
            prev_status = state.get("last_seen_status") if state else None
            last_change = state.get("last_status_change_at") if state else now_iso
            
            if prev_status != "Active":
                last_change = now_iso

            self.db.upsert_lifecycle_state(
                land_number=land_number,
                last_seen_status="Active",
                current_event_id=None,
                last_notified_event_id=None,
                last_status_change_at=last_change,
                updated_at=now_iso,
            )
            return (
                DecisionAction.SKIP_ACTIVE,
                None,
                f"Customer {customer.customer_name} ({land_number}) is Active. Suspension notification not required.",
            )

        # 2. Customer is Suspended
        if customer.is_suspended():
            prev_status = state.get("last_seen_status") if state else None
            prev_event_id = state.get("current_event_id") if state else None
            last_notified_id = state.get("last_notified_event_id") if state else None
            last_change = state.get("last_status_change_at") if state else now_iso

            # Check if this is a new suspension transition (either first time seen, or transition from Active)
            is_new_transition = (prev_status != "Suspended") or (prev_event_id is None)

            if is_new_transition:
                # Mint a new unique suspension event ID
                timestamp_ms = int(time.time() * 1000)
                event_id = f"EVT-{land_number}-{timestamp_ms}"
                last_change = now_iso
                
                self.db.upsert_lifecycle_state(
                    land_number=land_number,
                    last_seen_status="Suspended",
                    current_event_id=event_id,
                    last_notified_event_id=None,
                    last_status_change_at=last_change,
                    updated_at=now_iso,
                )
            else:
                event_id = prev_event_id

            # Check for duplicate: has this event already received a notification?
            if last_notified_id == event_id:
                return (
                    DecisionAction.SKIP_DUPLICATE,
                    event_id,
                    f"Customer {customer.customer_name} ({land_number}) already notified for suspension event {event_id}. Duplicate prevented.",
                )

            # Check email availability (Case G)
            if not customer.has_valid_email():
                return (
                    DecisionAction.SKIP_MISSING_EMAIL,
                    event_id,
                    f"Customer {customer.customer_name} ({land_number}) is suspended but has no valid email address.",
                )

            return (
                DecisionAction.PROCEED_NOTIFICATION,
                event_id,
                f"Customer {customer.customer_name} ({land_number}) is suspended and requires notification for event {event_id}.",
            )

        # Other status fallback
        return (
            DecisionAction.SKIP_ACTIVE,
            None,
            f"Customer {customer.customer_name} has status '{customer.status}'. Skipped.",
        )

    def mark_event_notified(self, land_number: str, event_id: str) -> None:
        """Record that a notification was successfully sent or simulated for the event."""
        now_iso = datetime.now(timezone.utc).isoformat()
        state = self.db.get_lifecycle_state(land_number)
        last_change = state.get("last_status_change_at") if state else now_iso
        
        self.db.upsert_lifecycle_state(
            land_number=land_number,
            last_seen_status="Suspended",
            current_event_id=event_id,
            last_notified_event_id=event_id,
            last_status_change_at=last_change,
            updated_at=now_iso,
        )
