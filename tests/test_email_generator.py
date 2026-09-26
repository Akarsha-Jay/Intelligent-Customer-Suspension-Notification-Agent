"""
Unit tests for Email Generation and Fallback Engine.
"""

import unittest
from backend.agent.email_generator import EmailGenerator
from backend.agent.suspension_analyzer import SuspensionCategory


class TestEmailGenerator(unittest.TestCase):

    def setUp(self):
        # Generator without LLM key (testing robust template fallback)
        self.generator = EmailGenerator(gemini_api_key=None)

    def test_bill_overdue_email_generation(self):
        result = self.generator.generate(
            customer_name="Customer 002",
            land_number="0116789002",
            category=SuspensionCategory.BILL_OVERDUE,
            remark="Bill overdue",
        )
        self.assertEqual(result.generation_mode, "TEMPLATE_FALLBACK")
        self.assertIn("Customer 002", result.body)
        self.assertIn("0116789002", result.body)
        self.assertIn("Bill overdue", result.body)
        self.assertIn("Outstanding Bill", result.subject)

    def test_customer_requested_email_generation(self):
        result = self.generator.generate(
            customer_name="Customer 004",
            land_number="0116789004",
            category=SuspensionCategory.CUSTOMER_REQUESTED,
            remark="Customer requested temporary suspension",
        )
        self.assertIn("Customer 004", result.body)
        self.assertIn("0116789004", result.body)
        self.assertIn("temporary suspension", result.body.lower())

    def test_no_invented_details(self):
        """Verify that email does not invent monetary amounts, phone numbers, or due dates."""
        result = self.generator.generate(
            customer_name="Customer 003",
            land_number="0116789003",
            category=SuspensionCategory.PAYMENT_NOT_RECEIVED,
            remark="Payment not received",
        )
        body = result.body
        # Should not invent specific rupees/dollar amounts or dates
        self.assertNotIn("Rs.", body)
        self.assertNotIn("LKR", body)
        self.assertNotIn("$", body)
        self.assertNotIn("within 7 days", body)
        self.assertNotIn("within 14 days", body)
        self.assertNotIn("legal action", body)


if __name__ == "__main__":
    unittest.main()
