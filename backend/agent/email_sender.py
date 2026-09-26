"""
Email Dispatch Service supporting Safe Simulation Mode and Real SMTP.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple
from backend.models.notification import DeliveryStatus

logger = logging.getLogger("agent.email_sender")


class EmailSender:
    """Dispatches or simulates emails based on configuration."""

    def __init__(
        self,
        test_mode: bool = True,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        sender_email: Optional[str] = None,
    ):
        self.test_mode = test_mode
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.sender_email = sender_email or "notifications@example.com"

    def send_notification(
        self,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> Tuple[DeliveryStatus, Optional[str]]:
        """
        Send or simulate email dispatch.
        Returns: (DeliveryStatus, Optional[error_message])
        """
        # Validate recipient email format
        if not recipient_email or "@" not in recipient_email:
            return DeliveryStatus.FAILED, "Invalid recipient email address format."

        # MODE 1: Safe Simulation Mode (Default)
        if self.test_mode:
            logger.info(
                f"[SIMULATION MODE] Notification would be sent to: {recipient_email} | Subject: '{subject}'"
            )
            return DeliveryStatus.SIMULATED, None

        # MODE 2: Real SMTP Delivery
        if not self.smtp_host:
            return DeliveryStatus.FAILED, "SMTP host is not configured for real email delivery."

        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"[REAL EMAIL SENT] Notification delivered to {recipient_email}")
            return DeliveryStatus.SENT, None

        except Exception as e:
            error_msg = f"SMTP dispatch failed: {str(e)}"
            logger.error(error_msg)
            return DeliveryStatus.FAILED, error_msg
