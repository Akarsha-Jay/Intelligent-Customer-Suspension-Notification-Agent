"""
Quick diagnostic script to verify SMTP credentials and send a test email.
"""

import sys
import os

# Set project root in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.config import settings
from backend.agent.email_sender import EmailSender

def main():
    print("=" * 60)
    print("SLT NOTIFICATION AGENT - SMTP CONNECTION TEST")
    print("=" * 60)
    print(f"SMTP Host:     {settings.smtp_host or '(Not configured)'}")
    print(f"SMTP Port:     {settings.smtp_port}")
    print(f"Sender Email:  {settings.sender_email}")
    print(f"SMTP Username: {settings.smtp_username}")
    print(f"Test Mode:     {settings.email_test_mode}")
    print("=" * 60)

    if settings.email_test_mode:
        print("\n[WARNING] EMAIL_TEST_MODE is still set to 'true' in .env.")
        print("Please set EMAIL_TEST_MODE=false in .env to send real emails.\n")
        return

    if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password or "YOUR_16" in settings.smtp_password:
        print("\n[ERROR] SMTP password has not been filled in .env yet.")
        print("Please open .env and set your 16-character Google App Password in SMTP_PASSWORD.\n")
        return

    recipient = settings.sender_email
    print(f"\nAttempting to send a test verification email to: {recipient} ...")

    sender = EmailSender(
        test_mode=False,
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password=settings.smtp_password,
        sender_email=settings.sender_email,
    )

    status, err = sender.send_notification(
        recipient_email=recipient,
        subject="[SLT Agent Verification] Test Notification Delivery",
        body=(
            f"Hello Akarsha,\n\n"
            f"This is a test notification from your SLT Intelligent Customer Suspension Notification Agent.\n\n"
            f"Your outbound SMTP mail server is functioning properly! The agent is now ready to dispatch real suspension notices to customer inboxes.\n\n"
            f"Sender: {settings.sender_email}\n"
            f"Delivery Status: SUCCESS"
        ),
    )

    if status.value == "SENT":
        print(f"\n[SUCCESS] Test email successfully delivered to {recipient}!")
        print("Check your Gmail inbox (and Spam/Promotions folder just in case).\n")
    else:
        print(f"\n[FAILED] Email dispatch failed:")
        print(f"Error: {err}\n")
        print("Troubleshooting tips:")
        print("1. Did you use your 16-character Google App Password (not your regular Gmail password)?")
        print("2. Is 2-Step Verification turned ON in your Google Account?")
        print("3. Check that your email in SMTP_USERNAME and SENDER_EMAIL matches.\n")

if __name__ == "__main__":
    main()
