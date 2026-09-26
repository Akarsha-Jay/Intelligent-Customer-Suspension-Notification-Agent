"""
Unit tests for Suspension Analyzer.
Tests Cases B, C, D, E, F and synonyms/edge cases.
"""

import unittest
from backend.agent.suspension_analyzer import SuspensionAnalyzer, SuspensionCategory


class TestSuspensionAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SuspensionAnalyzer()

    def test_case_b_bill_overdue(self):
        """Case B: Suspended because of bill."""
        remarks = ["Bill overdue", "Unpaid bill", "Outstanding payment", "Overdue bill amount"]
        for r in remarks:
            result = self.analyzer.analyze(r)
            self.assertEqual(result.category, SuspensionCategory.BILL_OVERDUE, f"Failed for: {r}")
            self.assertTrue(result.is_payment_related)

    def test_case_c_payment_not_received(self):
        """Case C: Suspended because payment was not received."""
        remarks = ["Payment not received", "Non-payment of monthly charges", "Payment pending"]
        for r in remarks:
            result = self.analyzer.analyze(r)
            self.assertEqual(result.category, SuspensionCategory.PAYMENT_NOT_RECEIVED, f"Failed for: {r}")
            self.assertTrue(result.is_payment_related)

    def test_case_d_customer_requested(self):
        """Case D: Customer requested temporary suspension."""
        remarks = [
            "Customer requested temporary suspension",
            "Customer requested service suspension",
            "Temporary suspension requested by customer",
            "Client requested hold",
        ]
        for r in remarks:
            result = self.analyzer.analyze(r)
            self.assertEqual(result.category, SuspensionCategory.CUSTOMER_REQUESTED, f"Failed for: {r}")
            self.assertFalse(result.is_payment_related)

    def test_case_e_technical_issue(self):
        """Case E: Technical issue."""
        remarks = ["Technical issue", "Service issue", "Line maintenance", "Network maintenance"]
        for r in remarks:
            result = self.analyzer.analyze(r)
            self.assertEqual(result.category, SuspensionCategory.TECHNICAL_ISSUE, f"Failed for: {r}")
            self.assertFalse(result.is_payment_related)

    def test_case_f_account_issue(self):
        """Case F: Account / Verification issue."""
        remarks = ["Account issue", "Verification required", "Identity verification pending"]
        for r in remarks:
            result = self.analyzer.analyze(r)
            self.assertEqual(result.category, SuspensionCategory.ACCOUNT_ISSUE, f"Failed for: {r}")

    def test_unknown_and_empty_remarks(self):
        """Fallback to UNKNOWN for unrecognized or missing remarks."""
        empty_res = self.analyzer.analyze("")
        self.assertEqual(empty_res.category, SuspensionCategory.UNKNOWN)

        none_res = self.analyzer.analyze(None)
        self.assertEqual(none_res.category, SuspensionCategory.UNKNOWN)

        random_res = self.analyzer.analyze("Some completely unmapped text 12345")
        self.assertEqual(random_res.category, SuspensionCategory.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
