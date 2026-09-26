"""
Meta WhatsApp Cloud API Dispatcher.
Supports Safe Simulation Mode and Real Meta Graph API HTTP dispatch.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Tuple, Dict, Any
from backend.models.notification import DeliveryStatus
from backend.agent.whatsapp_generator import WhatsAppGenerator

logger = logging.getLogger("agent.whatsapp_sender")


class WhatsAppSender:
    """Dispatches or simulates WhatsApp messages via Meta WhatsApp Cloud API."""

    def __init__(
        self,
        test_mode: bool = True,
        api_version: str = "v20.0",
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
        template_name: str = "service_suspension_notice",
    ):
        self.test_mode = test_mode
        self.api_version = api_version or "v20.0"
        self.phone_number_id = (phone_number_id or "").strip()
        self.access_token = (access_token or "").strip()
        self.template_name = template_name or "service_suspension_notice"
        self.generator = WhatsAppGenerator(template_name=self.template_name)

    def is_configured_for_real_delivery(self) -> bool:
        """Returns True if minimum Meta API credentials are provided."""
        return bool(self.phone_number_id and self.access_token)

    def send_notification(
        self,
        recipient_phone: str,
        customer_name: str,
        land_number: str,
        reason: str,
    ) -> Tuple[DeliveryStatus, Optional[str]]:
        """
        Dispatches or simulates WhatsApp notification via Meta Cloud API.
        Returns: (DeliveryStatus, Optional[error_message])
        """
        # Validate and sanitize phone number
        is_valid, clean_phone = self.generator.sanitize_phone_number(recipient_phone)
        if not is_valid:
            return DeliveryStatus.FAILED, f"Invalid WhatsApp number: {clean_phone}"

        human_preview = self.generator.generate_human_preview(
            customer_name=customer_name,
            land_number=land_number,
            reason=reason,
        )

        # MODE 1: Safe Simulation Mode (Default)
        if self.test_mode:
            logger.info(
                f"[WHATSAPP SIMULATION] Recipient: +{clean_phone} ({recipient_phone})\n"
                f"--- Message Body ---\n{human_preview}\n--------------------"
            )
            return DeliveryStatus.SIMULATED, None

        # MODE 2: Real Meta Cloud API Dispatch
        if not self.is_configured_for_real_delivery():
            return (
                DeliveryStatus.FAILED,
                "Meta WhatsApp credentials (Phone Number ID or Access Token) are not configured.",
            )

        endpoint_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        payload = self.generator.generate_meta_payload(
            recipient_phone=clean_phone,
            customer_name=customer_name,
            land_number=land_number,
            reason=reason,
        )

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint_url,
                data=req_data,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "SLT-Suspension-Agent/1.0",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=12) as response:
                resp_body = response.read().decode("utf-8")
                resp_json = json.loads(resp_body) if resp_body else {}
                messages = resp_json.get("messages", [])
                wamid = messages[0].get("id") if messages else "sent"
                logger.info(f"[META WHATSAPP SENT] Delivered to {clean_phone} (WAMID: {wamid})")
                return DeliveryStatus.SENT, None

        except urllib.error.HTTPError as http_err:
            error_body = ""
            try:
                error_body = http_err.read().decode("utf-8")
                err_json = json.loads(error_body)
                meta_msg = err_json.get("error", {}).get("message", error_body)
            except Exception:
                meta_msg = error_body or str(http_err)

            error_msg = f"Meta Cloud API HTTP {http_err.code}: {meta_msg}"
            logger.error(f"Meta WhatsApp dispatch error: {error_msg}")
            return DeliveryStatus.FAILED, error_msg

        except Exception as e:
            error_msg = f"Meta WhatsApp network error: {str(e)}"
            logger.error(error_msg)
            return DeliveryStatus.FAILED, error_msg
