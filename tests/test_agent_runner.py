"""
End-to-end unit tests for the Agent Runner.
Verifies complete execution cycle, error containment, batch processing, and run history logging.
"""

import os
import unittest
import tempfile
from typing import List, Optional
from backend.models.customer import CustomerRecord, CustomerUpdate
from backend.data.customer_repository import CustomerRepository
from backend.storage.database import DatabaseManager
from backend.agent.email_generator import EmailGenerator
from backend.agent.email_sender import EmailSender
from backend.agent.agent_runner import AgentRunner
from backend.models.notification import DeliveryStatus
from backend.models.agent_run import RunStatus


class InMemoryCustomerRepository(CustomerRepository):
    """Mock in-memory repository for isolated unit testing."""
    def __init__(self, records: List[CustomerRecord]):
        self.records = records

    def get_all(self) -> List[CustomerRecord]:
        return list(self.records)

    def get_by_land_number(self, land_number: str) -> Optional[CustomerRecord]:
        for r in self.records:
            if r.land_number == land_number:
                return r
        return None

    def get_suspended(self) -> List[CustomerRecord]:
        return [r for r in self.records if r.is_suspended()]

    def update_customer(self, land_number: str, update_data: CustomerUpdate) -> Optional[CustomerRecord]:
        for i, r in enumerate(self.records):
            if r.land_number == land_number:
                dump = r.model_dump()
                if update_data.status is not None:
                    dump["status"] = update_data.status
                if update_data.remark is not None:
                    dump["remark"] = update_data.remark
                self.records[i] = CustomerRecord(**dump)
                return self.records[i]
        return None

    def save_all(self, records: List[CustomerRecord]) -> None:
        self.records = list(records)

    def clear(self) -> None:
        self.records = []



class TestAgentRunner(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

        # 4 test customers:
        # 1 Active (skip)
        # 1 Suspended with bill overdue (notify)
        # 1 Suspended with tech issue (notify)
        # 1 Suspended with missing email (Case G - skip safely)
        self.customers = [
            CustomerRecord(
                land_number="0116789001",
                customer_name="Customer 001",
                whatsapp_number="+94770000001",
                email="customer001@example.com",
                status="Active",
                remark="Account in good standing",
            ),
            CustomerRecord(
                land_number="0116789002",
                customer_name="Customer 002",
                whatsapp_number="+94770000002",
                email="customer002@example.com",
                status="Suspended",
                remark="Bill overdue",
            ),
            CustomerRecord(
                land_number="0116789005",
                customer_name="Customer 005",
                whatsapp_number="+94770000005",
                email="customer005@example.com",
                status="Suspended",
                remark="Technical issue",
            ),
            CustomerRecord(
                land_number="0116789007",
                customer_name="Customer 007",
                whatsapp_number="+94770000007",
                email="",  # Missing email
                status="Suspended",
                remark="Bill overdue",
            ),
        ]
        self.repo = InMemoryCustomerRepository(self.customers)
        self.email_gen = EmailGenerator(gemini_api_key=None)
        self.email_sender = EmailSender(test_mode=True)  # Safe simulation mode
        self.runner = AgentRunner(
            repository=self.repo,
            db=self.db,
            email_generator=self.email_gen,
            email_sender=self.email_sender,
        )

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_complete_first_and_second_agent_runs(self):
        # FIRST RUN
        run_1 = self.runner.run()
        self.assertEqual(run_1.run_status, RunStatus.COMPLETED)
        self.assertEqual(run_1.customers_checked, 4)
        self.assertEqual(run_1.active_customers, 1)
        self.assertEqual(run_1.suspended_customers, 3)
        self.assertEqual(run_1.notifications_sent, 2)  # Customer 002 and 005
        self.assertEqual(run_1.notifications_skipped, 1)  # Customer 007 (missing email)
        self.assertEqual(run_1.notifications_failed, 0)

        # Check notification records in DB
        notifs = self.db.get_notifications()
        self.assertEqual(len(notifs), 3)  # 2 simulated + 1 skipped (for missing email)
        simulated = [n for n in notifs if n.delivery_status == DeliveryStatus.SIMULATED]
        skipped = [n for n in notifs if n.delivery_status == DeliveryStatus.SKIPPED]
        self.assertEqual(len(simulated), 2)
        self.assertEqual(len(skipped), 1)

        # SECOND RUN IMMEDIATELY AFTERWARDS
        run_2 = self.runner.run()
        self.assertEqual(run_2.run_status, RunStatus.COMPLETED)
        self.assertEqual(run_2.customers_checked, 4)
        self.assertEqual(run_2.active_customers, 1)
        self.assertEqual(run_2.suspended_customers, 3)
        self.assertEqual(run_2.notifications_sent, 0)  # DUPLICATES PREVENTED!
        self.assertEqual(run_2.notifications_skipped, 3)  # All 3 suspended skipped
        self.assertEqual(run_2.notifications_failed, 0)


if __name__ == "__main__":
    unittest.main()
