"""
Unit tests for Dataset Upload & Smart Column Mapping.
"""

import unittest
from backend.api.routes_settings import _detect_column_mapping, _clean_header_key


class TestDatasetUploadMapping(unittest.TestCase):

    def test_clean_header_key(self):
        self.assertEqual(_clean_header_key("Land_Number"), "landnumber")
        self.assertEqual(_clean_header_key("TELE-NO (#)"), "teleno")
        self.assertEqual(_clean_header_key("Customer  Name "), "customername")

    def test_standard_headers_mapping(self):
        headers = ["land_number", "customer_name", "whatsapp_number", "email", "status", "remark"]
        mapping = _detect_column_mapping(headers)
        self.assertEqual(mapping["land_number"], "land_number")
        self.assertEqual(mapping["customer_name"], "customer_name")
        self.assertEqual(mapping["email"], "email")
        self.assertEqual(mapping["status"], "status")
        self.assertEqual(mapping["remark"], "remark")

    def test_slt_custom_headers_mapping(self):
        headers = ["TELE_NO", "NAME", "MAIL", "MOBILE", "SERVICE_STATE", "SUSPENSION_REASON"]
        mapping = _detect_column_mapping(headers)
        self.assertEqual(mapping["land_number"], "TELE_NO")
        self.assertEqual(mapping["customer_name"], "NAME")
        self.assertEqual(mapping["email"], "MAIL")
        self.assertEqual(mapping["whatsapp_number"], "MOBILE")
        self.assertEqual(mapping["status"], "SERVICE_STATE")
        self.assertEqual(mapping["remark"], "SUSPENSION_REASON")


class TestUploadCacheClearing(unittest.TestCase):
    """Verifies that uploading a new CSV dataset clears duplicate prevention cache."""

    def setUp(self):
        import tempfile
        from backend.storage.database import DatabaseManager
        from backend.agent.state_tracker import StateTracker
        from backend.models.customer import CustomerRecord

        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
        self.tracker = StateTracker(self.db)

    def tearDown(self):
        import os
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_clear_lifecycle_states_clears_duplicate_block(self):
        from backend.models.customer import CustomerRecord
        from backend.agent.state_tracker import DecisionAction

        cust = CustomerRecord(
            land_number="0112345678",
            customer_name="Test Customer",
            whatsapp_number="+94770000000",
            email="test@example.com",
            status="Suspended",
            remark="Bill overdue",
        )

        # 1. First evaluation: should proceed with notification
        action1, evt1, _ = self.tracker.evaluate_customer(cust)
        self.assertEqual(action1, DecisionAction.PROCEED_NOTIFICATION)
        self.assertIsNotNone(evt1)

        # 2. Mark event as notified
        self.tracker.mark_event_notified("0112345678", evt1)

        # 3. Second evaluation: should be skipped as duplicate
        action2, evt2, _ = self.tracker.evaluate_customer(cust)
        self.assertEqual(action2, DecisionAction.SKIP_DUPLICATE)
        self.assertEqual(evt2, evt1)

        # 4. Clear lifecycle cache (simulating what occurs when a new CSV is uploaded)
        cleared_count = self.db.clear_lifecycle_states()
        self.assertEqual(cleared_count, 1)

        # 5. Third evaluation after cache clearance: should proceed fresh, NOT skip!
        action3, evt3, _ = self.tracker.evaluate_customer(cust)
        self.assertEqual(action3, DecisionAction.PROCEED_NOTIFICATION)
        self.assertIsNotNone(evt3)
        self.assertNotEqual(evt3, evt1)


class TestDatasetUploadEndpoints(unittest.TestCase):
    """Verifies API endpoints for upload and cache clearing."""

    def test_clear_cache_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.main import app

        with TestClient(app) as client:
            res = client.post("/api/cache/clear")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data.get("success"))
            self.assertIn("details", data)

    def test_upload_endpoint_clears_cache_by_default(self):
        import io
        from fastapi.testclient import TestClient
        from backend.main import app

        csv_content = (
            "land_number,customer_name,whatsapp_number,email,status,remark\n"
            "0119999999,Upload Test Subscriber,+94770000000,test@example.com,Suspended,Bill overdue\n"
        )
        file_obj = io.BytesIO(csv_content.encode("utf-8"))

        with TestClient(app) as client:
            res = client.post(
                "/api/dataset/upload",
                files={"file": ("test_upload.csv", file_obj, "text/csv")},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data.get("success"))
            self.assertTrue(data.get("cache_cleared"))
            self.assertIn("lifecycle_records_cleared", data)

    def test_clear_dataset_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.main import app

        with TestClient(app) as client:
            res = client.post("/api/dataset/clear")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data.get("success"))
            self.assertEqual(data.get("count"), 0)


if __name__ == "__main__":
    unittest.main()
