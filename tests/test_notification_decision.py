"""
Unit tests for Notification Decision Engine and Case G handling.
"""

import os
import unittest
import tempfile
from backend.models.customer import CustomerRecord
from backend.storage.database import DatabaseManager
from backend.agent.state_tracker import StateTracker, DecisionAction
from backend.agent.notification_decision import NotificationDecisionEngine
from backend.agent.suspension_analyzer import SuspensionCategory


class TestNotificationDecision(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
        self.state_tracker = StateTracker(self.db)
        self.decision_engine = NotificationDecisionEngine(self.state_tracker)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_case_a_active_customer_skipped(self):
        """CASE A: Active customer must be skipped without sending an email."""
        customer = CustomerRecord(
            land_number="0116789001",
            customer_name="Customer 001",
            whatsapp_number="+94770000001",
            email="customer001@example.com",
            status="Active",
            remark="Account active",
        )
        decision = self.decision_engine.evaluate(customer)
        self.assertEqual(decision.action, DecisionAction.SKIP_ACTIVE)

    def test_suspended_customer_evaluated(self):
        """CASE B: Suspended customer proceeds with appropriate category."""
        customer = CustomerRecord(
            land_number="0116789002",
            customer_name="Customer 002",
            whatsapp_number="+94770000002",
            email="customer002@example.com",
            status="Suspended",
            remark="Bill overdue",
        )
        decision = self.decision_engine.evaluate(customer)
        self.assertEqual(decision.action, DecisionAction.PROCEED_NOTIFICATION)
        self.assertEqual(decision.category, SuspensionCategory.BILL_OVERDUE)
        self.assertIsNotNone(decision.suspension_event_id)

    def test_case_g_missing_email_handled_safely(self):
        """CASE G: Missing or blank email is handled safely without crashing."""
        customer_no_email = CustomerRecord(
            land_number="0116789007",
            customer_name="Customer 007",
            whatsapp_number="+94770000007",
            email="",
            status="Suspended",
            remark="Bill overdue",
        )
        decision = self.decision_engine.evaluate(customer_no_email)
        self.assertEqual(decision.action, DecisionAction.SKIP_MISSING_EMAIL)
        self.assertEqual(decision.category, SuspensionCategory.BILL_OVERDUE)

    def test_case_g_invalid_email_handled(self):
        """CASE G variant: Malformed email without @ or domain."""
        customer_bad_email = CustomerRecord(
            land_number="0116789008",
            customer_name="Customer 008",
            whatsapp_number="+94770000008",
            email="notanemail",
            status="Suspended",
            remark="Technical issue",
        )
        decision = self.decision_engine.evaluate(customer_bad_email)
        self.assertEqual(decision.action, DecisionAction.SKIP_MISSING_EMAIL)


if __name__ == "__main__":
    unittest.main()
