"""
Unit tests for Duplicate Notification Prevention and Customer Lifecycle Transitions.
Verifies the exact demonstration workflow (Active -> Suspended -> duplicate prevention -> Active -> Suspended).
"""

import os
import unittest
import tempfile
from backend.models.customer import CustomerRecord
from backend.storage.database import DatabaseManager
from backend.agent.state_tracker import StateTracker, DecisionAction


class TestDuplicatePrevention(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
        self.state_tracker = StateTracker(self.db)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_lifecycle_and_duplicate_prevention_flow(self):
        """
        Tests the 11-step lifecycle workflow:
        1. Customer starts Active
        2. Becomes Suspended -> Notification allowed with Event ID 1
        3. Notification sent -> Event 1 marked as notified
        4. Next run, customer still Suspended -> DUPLICATE PREVENTED!
        5. Customer returns to Active -> State updated, event cleared
        6. Customer becomes Suspended again -> NEW Event ID 2 generated -> Notification allowed!
        """
        land_number = "0116789001"
        cust_name = "Customer 001"

        # Step 1: Customer is Active
        customer_active = CustomerRecord(
            land_number=land_number,
            customer_name=cust_name,
            whatsapp_number="+94770000001",
            email="customer001@example.com",
            status="Active",
            remark="In good standing",
        )
        action, event_id, _ = self.state_tracker.evaluate_customer(customer_active)
        self.assertEqual(action, DecisionAction.SKIP_ACTIVE)
        self.assertIsNone(event_id)

        # Step 2: Transition to Suspended (First suspension event)
        customer_suspended_1 = CustomerRecord(
            land_number=land_number,
            customer_name=cust_name,
            whatsapp_number="+94770000001",
            email="customer001@example.com",
            status="Suspended",
            remark="Bill overdue",
        )
        action_1, event_id_1, _ = self.state_tracker.evaluate_customer(customer_suspended_1)
        self.assertEqual(action_1, DecisionAction.PROCEED_NOTIFICATION)
        self.assertIsNotNone(event_id_1)
        self.assertTrue(event_id_1.startswith(f"EVT-{land_number}"))

        # Step 3: Notification dispatched/simulated -> Mark event 1 as notified
        self.state_tracker.mark_event_notified(land_number, event_id_1)

        # Step 4: Next run -> Customer is STILL Suspended (Same event)
        action_dup, event_id_dup, reason_dup = self.state_tracker.evaluate_customer(customer_suspended_1)
        self.assertEqual(action_dup, DecisionAction.SKIP_DUPLICATE)
        self.assertEqual(event_id_dup, event_id_1)
        self.assertIn("Duplicate prevented", reason_dup)

        # Step 5: Customer changes back: Suspended -> Active
        customer_reactivated = CustomerRecord(
            land_number=land_number,
            customer_name=cust_name,
            whatsapp_number="+94770000001",
            email="customer001@example.com",
            status="Active",
            remark="Payment settled, service restored",
        )
        action_act, event_id_act, _ = self.state_tracker.evaluate_customer(customer_reactivated)
        self.assertEqual(action_act, DecisionAction.SKIP_ACTIVE)

        # Step 6: Customer changes back: Active -> Suspended (Second suspension event)
        customer_suspended_2 = CustomerRecord(
            land_number=land_number,
            customer_name=cust_name,
            whatsapp_number="+94770000001",
            email="customer001@example.com",
            status="Suspended",
            remark="Payment not received",
        )
        action_2, event_id_2, _ = self.state_tracker.evaluate_customer(customer_suspended_2)
        self.assertEqual(action_2, DecisionAction.PROCEED_NOTIFICATION)
        self.assertIsNotNone(event_id_2)
        # Verify this is a distinct new event
        self.assertNotEqual(event_id_1, event_id_2)


if __name__ == "__main__":
    unittest.main()
