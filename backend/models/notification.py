"""
Notification data models and delivery status definitions.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DeliveryStatus(str, Enum):
    SENT = "SENT"
    SIMULATED = "SIMULATED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class NotificationRecord(BaseModel):
    """Represents a recorded notification in persistent history."""
    notification_id: str = Field(..., description="Unique notification identifier")
    customer_id: str = Field(..., description="Customer identifier (land number)")
    land_number: str = Field(..., description="Customer landline number")
    customer_name: str = Field(..., description="Customer name")
    email: Optional[str] = Field(default="", description="Recipient email address")
    whatsapp_number: Optional[str] = Field(default="", description="Recipient WhatsApp contact number")
    channel: str = Field(default="EMAIL", description="Notification delivery channel: EMAIL or WHATSAPP")
    notification_type: str = Field(..., description="Suspension category, e.g. BILL_OVERDUE")
    suspension_reason: str = Field(..., description="Raw remark from customer record")
    subject: str = Field(..., description="Email subject line or WhatsApp title")
    email_content: str = Field(..., description="Body content of the notification message")
    created_at: str = Field(..., description="ISO timestamp of generation")
    sent_at: Optional[str] = Field(default=None, description="ISO timestamp when sent/simulated")
    delivery_status: DeliveryStatus = Field(..., description="SENT, SIMULATED, SKIPPED, or FAILED")
    error_message: Optional[str] = Field(default=None, description="Error detail if skipped or failed")
    suspension_event_id: str = Field(..., description="Unique suspension event cycle ID")
