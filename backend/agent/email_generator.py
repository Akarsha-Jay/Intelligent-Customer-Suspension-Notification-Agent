"""
Email Generation Service for Customer Suspension Notification Agent.

Adheres strictly to business guidelines:
- Uses ONLY: customer name, land number, suspension category, and suspension remark.
- NEVER invents payment amounts, due dates, contact numbers, restoration periods, or policies.
- Optional LLM generation with reliable, immediate fallback to deterministic templates.
"""

import os
import logging
from typing import Optional, Dict
from pydantic import BaseModel
from backend.agent.suspension_analyzer import SuspensionCategory

logger = logging.getLogger("agent.email_generator")


class GeneratedEmail(BaseModel):
    subject: str
    body: str
    generation_mode: str  # "TEMPLATE_FALLBACK" or "LLM_GENERATED"


class EmailGenerator:
    """Generates customer suspension notification emails."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        self._llm_client = None
        if self.api_key:
            self._init_llm()

    def _init_llm(self) -> None:
        try:
            from google import genai
            self._llm_client = genai.Client(api_key=self.api_key)
            logger.info("Initialized Google GenAI LLM client.")
        except Exception as e:
            logger.warning(f"Failed to initialize GenAI client: {e}. Fallback templates will be used.")
            self._llm_client = None

    def generate(
        self,
        customer_name: str,
        land_number: str,
        category: SuspensionCategory,
        remark: str,
    ) -> GeneratedEmail:
        """
        Generate email content. Tries LLM if configured, falls back to deterministic template.
        """
        # Try LLM if available
        if self._llm_client:
            try:
                llm_result = self._generate_with_llm(customer_name, land_number, category, remark)
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM generation failed ({e}). Falling back to template.")

        # Deterministic Template Fallback
        return self._generate_with_template(customer_name, land_number, category, remark)

    def _generate_with_template(
        self,
        customer_name: str,
        land_number: str,
        category: SuspensionCategory,
        remark: str,
    ) -> GeneratedEmail:
        """Deterministic, professional template generator."""
        clean_name = customer_name.strip()
        clean_remark = remark.strip() if remark else "Service suspended"

        subject_map = {
            SuspensionCategory.BILL_OVERDUE: "Service Suspension Notification - Outstanding Bill",
            SuspensionCategory.PAYMENT_NOT_RECEIVED: "Service Suspension Notification - Payment Notice",
            SuspensionCategory.CUSTOMER_REQUESTED: "Service Suspension Confirmation - Customer Request",
            SuspensionCategory.TECHNICAL_ISSUE: "Service Notification - Technical Maintenance",
            SuspensionCategory.ACCOUNT_ISSUE: "Account Notice - Service Suspension",
            SuspensionCategory.UNKNOWN: "Service Suspension Notification",
        }
        subject = subject_map.get(category, "Service Suspension Notification")

        body_action_map = {
            SuspensionCategory.BILL_OVERDUE: "Please review your outstanding billing records and settle any pending balance through your regular payment channels to restore connectivity.",
            SuspensionCategory.PAYMENT_NOT_RECEIVED: "Please check your recent payment transactions or submit your payment receipt for verification to resume your service.",
            SuspensionCategory.CUSTOMER_REQUESTED: "As requested, your service has been placed on temporary suspension. If you wish to reactivate your connection, please reach out to customer service.",
            SuspensionCategory.TECHNICAL_ISSUE: "Our technical operations team has placed this line on temporary hold to address service maintenance. Further updates will follow once operations are completed.",
            SuspensionCategory.ACCOUNT_ISSUE: "Please provide the requested account verification details to complete your profile review and resume service.",
            SuspensionCategory.UNKNOWN: "Please review your account status and follow the applicable procedure for your service.",
        }
        action_text = body_action_map.get(category, "Please review your account details and contact customer care.")

        body = (
            f"Dear {clean_name},\n\n"
            f"We would like to inform you that the telecommunication service associated with land number {land_number} "
            f"is currently suspended.\n\n"
            f"Reason: {clean_remark}.\n\n"
            f"{action_text}\n\n"
            f"Thank you,\n"
            f"Customer Care Support Team"
        )

        return GeneratedEmail(
            subject=subject,
            body=body,
            generation_mode="TEMPLATE_FALLBACK",
        )

    def _generate_with_llm(
        self,
        customer_name: str,
        land_number: str,
        category: SuspensionCategory,
        remark: str,
    ) -> Optional[GeneratedEmail]:
        """Generate email using LLM with strict guardrail prompt."""
        prompt = (
            f"You are a professional customer notification agent for a telecom provider.\n"
            f"Generate a polite, concise, and professional service suspension email for the following customer:\n"
            f"- Customer Name: {customer_name}\n"
            f"- Landline Number: {land_number}\n"
            f"- Suspension Category: {category.value}\n"
            f"- Recorded Remark: {remark}\n\n"
            f"STRICT RULES:\n"
            f"1. DO NOT invent payment amounts, due dates, contact phone numbers, restoration hours, bank accounts, or penalties.\n"
            f"2. Use ONLY the provided details.\n"
            f"3. Return the output in this exact format:\n"
            f"SUBJECT: <subject line>\n"
            f"BODY:\n"
            f"<email body text>"
        )

        response = self._llm_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text or ""
        
        if "SUBJECT:" in text and "BODY:" in text:
            parts = text.split("BODY:")
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body_part = parts[1].strip()
            return GeneratedEmail(
                subject=subject_part,
                body=body_part,
                generation_mode="LLM_GENERATED",
            )
        return None
