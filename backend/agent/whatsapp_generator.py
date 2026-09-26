"""
WhatsApp Message and Meta Cloud API Payload Generator.
Formats phone numbers and prepares template payloads for Meta WhatsApp Cloud API.
"""

import re
from typing import Dict, Any, Optional, Tuple


class WhatsAppGenerator:
    """Generates sanitized phone numbers and Meta Cloud API compliant payloads."""

    def __init__(self, template_name: str = "service_suspension_notice"):
        self.template_name = template_name

    @staticmethod
    def sanitize_phone_number(raw_phone: Optional[str]) -> Tuple[bool, str]:
        """
        Sanitizes phone numbers into international E.164 digits-only format required by Meta Cloud API.
        Example:
          '+94 77 000 0001' -> '94770000001'
          '0770000001' -> '94770000001'
          '0112345678' -> '94112345678'
        Returns:
          (is_valid, cleaned_digits_or_error)
        """
        if not raw_phone:
            return False, "Phone number is empty"

        # Remove spaces, hyphens, brackets, plus signs
        cleaned = re.sub(r"[\s\-\(\)\+]", "", str(raw_phone).strip())

        # If starts with domestic zero (e.g. 077... or 011...), convert to Sri Lanka country code 94
        if cleaned.startswith("0") and len(cleaned) == 10:
            cleaned = "94" + cleaned[1:]

        # Validate digits only and valid international length (9 to 15 digits per E.164 standard)
        if not cleaned.isdigit() or len(cleaned) < 9 or len(cleaned) > 15:
            return False, f"Invalid phone format: '{raw_phone}' (must be a valid mobile number with country code)"

        return True, cleaned

    def generate_human_preview(
        self,
        customer_name: str,
        land_number: str,
        reason: str,
    ) -> str:
        """
        Generates a readable preview with WhatsApp markdown (*bold*, _italic_)
        for logs, simulated deliveries, and UI inspection.
        """
        clean_reason = reason.strip() if reason else "Administrative suspension"
        return (
            f"*IMPORTANT NOTICE: Service Suspension*\n\n"
            f"Dear *{customer_name}*,\n\n"
            f"Your landline service (*{land_number}*) has been temporarily suspended.\n"
            f"- *Reason*: {clean_reason}\n\n"
            f"To restore your connection, please settle any outstanding dues online "
            f"or contact customer care at 1212.\n\n"
            f"_Telecom Services Automation Agent_"
        )

    def generate_meta_payload(
        self,
        recipient_phone: str,
        customer_name: str,
        land_number: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Generates official Meta Cloud API template payload.
        Meta requires business-initiated messages to use pre-approved templates.
        """
        is_valid, clean_phone = self.sanitize_phone_number(recipient_phone)
        if not is_valid:
            raise ValueError(clean_phone)

        clean_reason = reason.strip() if reason else "Administrative suspension"

        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {
                    "code": "en_US"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": customer_name},
                            {"type": "text", "text": land_number},
                            {"type": "text", "text": clean_reason},
                        ],
                    }
                ],
            },
        }
