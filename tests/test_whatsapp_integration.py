"""
Unit and integration tests for WhatsApp Meta Cloud API functionality.
"""

import os
import tempfile
import unittest
from backend.agent.whatsapp_generator import WhatsAppGenerator
from backend.agent.whatsapp_sender import WhatsAppSender
from backend.models.notification import DeliveryStatus, NotificationRecord
from backend.models.customer import CustomerRecord
from backend.storage.database import DatabaseManager
from backend.agent.agent_runner import AgentRunner
from backend.agent.email_generator import EmailGenerator
from backend.agent.email_sender import EmailSender


class DummyCustomerRepo:
    def __init__(self, records):
        self.records = records

    def get_all(self):
        return self.records


class TestWhatsAppIntegration(unittest.TestCase):

    def setUp(self):
        self.generator = WhatsAppGenerator(template_name="service_suspension_notice")
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_phone_sanitization_formats(self):
        """Test sanitizing various Sri Lankan number formats into Meta E.164 digits."""
        # Standard +94
        valid, phone = self.generator.sanitize_phone_number("+94770000001")
        self.assertTrue(valid)
        self.assertEqual(phone, "94770000001")

        # Domestic 077 format
        valid, phone = self.generator.sanitize_phone_number("0771234567")
        self.assertTrue(valid)
        self.assertEqual(phone, "94771234567")

        # Formatted with spaces and hyphens
        valid, phone = self.generator.sanitize_phone_number("+94 77-000-0002")
        self.assertTrue(valid)
        self.assertEqual(phone, "94770000002")

        # Invalid short string
        valid, err = self.generator.sanitize_phone_number("123")
        self.assertFalse(valid)

        # Blank string
        valid, err = self.generator.sanitize_phone_number("")
        self.assertFalse(valid)

    def test_meta_payload_structure(self):
        """Verify the generated Meta Cloud API payload matches official requirements."""
        payload = self.generator.generate_meta_payload(
            recipient_phone="+94770000001",
            customer_name="Akarsha Jayakody",
            land_number="0116789001",
            reason="Bill overdue",
        )
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["to"], "94770000001")
        self.assertEqual(payload["type"], "template")
        self.assertEqual(payload["template"]["name"], "service_suspension_notice")
        params = payload["template"]["components"][0]["parameters"]
        self.assertEqual(len(params), 3)
        self.assertEqual(params[0]["text"], "Akarsha Jayakody")
        self.assertEqual(params[1]["text"], "0116789001")
        self.assertEqual(params[2]["text"], "Bill overdue")

    def test_safe_simulation_mode(self):
        """WhatsAppSender in test_mode returns SIMULATED and does not call network."""
        sender = WhatsAppSender(test_mode=True)
        status, err = sender.send_notification(
            recipient_phone="+94770000001",
            customer_name="Sample User",
            land_number="0116789001",
            reason="Bill overdue",
        )
        self.assertEqual(status, DeliveryStatus.SIMULATED)
        self.assertIsNone(err)

    def test_live_mode_unconfigured_error(self):
        """WhatsAppSender in real mode without credentials returns FAILED with clear message."""
        sender = WhatsAppSender(test_mode=False, phone_number_id="", access_token="")
        status, err = sender.send_notification(
            recipient_phone="+94770000001",
            customer_name="Sample User",
            land_number="0116789001",
            reason="Bill overdue",
        )
        self.assertEqual(status, DeliveryStatus.FAILED)
        self.assertIn("not configured", err)

    def test_dual_channel_agent_runner(self):
        """Verify AgentRunner dispatches both Email and WhatsApp notifications to database."""
        cust = CustomerRecord(
            land_number="0116789001",
            customer_name="Sanuvi Akarsha",
            whatsapp_number="+94770000001",
            email="sanuvi@example.com",
            status="Suspended",
            remark="Bill overdue",
        )
        repo = DummyCustomerRepo([cust])
        email_gen = EmailGenerator(gemini_api_key=None)
        email_sender = EmailSender(test_mode=True)
        wa_sender = WhatsAppSender(test_mode=True)
        wa_gen = WhatsAppGenerator()

        runner = AgentRunner(
            repository=repo,
            db=self.db,
            email_generator=email_gen,
            email_sender=email_sender,
            whatsapp_sender=wa_sender,
            whatsapp_generator=wa_gen,
        )

        run_record = runner.run()
        self.assertEqual(run_record.notifications_sent, 2)  # 1 email + 1 whatsapp

        # Check DB audit history
        notifs = self.db.get_notifications()
        self.assertEqual(len(notifs), 2)
        channels = {n.channel for n in notifs}
        self.assertIn("EMAIL", channels)
        self.assertIn("WHATSAPP", channels)

        # Check WhatsApp specific fields
        wa_notif = next(n for n in notifs if n.channel == "WHATSAPP")
        self.assertEqual(wa_notif.whatsapp_number, "+94770000001")
        self.assertEqual(wa_notif.delivery_status, DeliveryStatus.SIMULATED)
        self.assertIn("0116789001", wa_notif.email_content)


if __name__ == "__main__":
    unittest.main()
