"""
Unit tests for Customer Data Access Layer (CsvCustomerRepository).
"""

import os
import unittest
import tempfile
import csv
from backend.models.customer import CustomerUpdate
from backend.data.customer_repository import CsvCustomerRepository


class TestCustomerRepository(unittest.TestCase):

    def setUp(self):
        self.temp_csv = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", newline="", encoding="utf-8")
        fieldnames = ["land_number", "customer_name", "whatsapp_number", "email", "status", "remark"]
        writer = csv.DictWriter(self.temp_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "land_number": "0116789001",
            "customer_name": "Customer 001",
            "whatsapp_number": "+94770000001",
            "email": "customer001@example.com",
            "status": "Active",
            "remark": "In good standing",
        })
        writer.writerow({
            "land_number": "0116789002",
            "customer_name": "Customer 002",
            "whatsapp_number": "+94770000002",
            "email": "customer002@example.com",
            "status": "Suspended",
            "remark": "Bill overdue",
        })
        self.temp_csv.close()
        self.repo = CsvCustomerRepository(self.temp_csv.name)

    def tearDown(self):
        if os.path.exists(self.temp_csv.name):
            try:
                os.remove(self.temp_csv.name)
            except Exception:
                pass

    def test_get_all_and_get_by_land_number(self):
        records = self.repo.get_all()
        self.assertEqual(len(records), 2)

        c1 = self.repo.get_by_land_number("0116789001")
        self.assertIsNotNone(c1)
        self.assertEqual(c1.customer_name, "Customer 001")
        self.assertTrue(c1.is_active())

    def test_get_suspended(self):
        suspended = self.repo.get_suspended()
        self.assertEqual(len(suspended), 1)
        self.assertEqual(suspended[0].land_number, "0116789002")

    def test_update_customer_status(self):
        # Update Customer 001 from Active to Suspended with new remark
        updated = self.repo.update_customer(
            land_number="0116789001",
            update_data=CustomerUpdate(status="Suspended", remark="Payment not received")
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "Suspended")
        self.assertEqual(updated.remark, "Payment not received")

        # Verify persistence from disk
        reloaded = self.repo.get_by_land_number("0116789001")
        self.assertEqual(reloaded.status, "Suspended")
        self.assertEqual(reloaded.remark, "Payment not received")

    def test_nonexistent_file_handling(self):
        nonexistent_path = os.path.join(tempfile.gettempdir(), "test_nonexistent_customers_99999.csv")
        if os.path.exists(nonexistent_path):
            os.remove(nonexistent_path)
        repo = CsvCustomerRepository(nonexistent_path)
        self.assertEqual(repo.get_all(), [])
        self.assertEqual(repo.get_suspended(), [])
        self.assertIsNone(repo.get_by_land_number("0110000000"))

    def test_clear_repository(self):
        self.assertEqual(len(self.repo.get_all()), 2)
        self.repo.clear()
        self.assertEqual(self.repo.get_all(), [])
        self.assertEqual(self.repo.get_suspended(), [])


if __name__ == "__main__":
    unittest.main()
