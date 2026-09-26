"""
Customer data models for Intelligent Customer Suspension Notification Agent.
"""

from typing import Optional
from pydantic import BaseModel, Field


class CustomerRecord(BaseModel):
    """Represents a customer record from the repository."""
    land_number: str = Field(..., description="Fictional Sri Lankan landline number, e.g. 0116789001")
    customer_name: str = Field(..., description="Customer full name, e.g. Customer 001")
    whatsapp_number: Optional[str] = Field(default="", description="WhatsApp contact number")
    email: Optional[str] = Field(default="", description="Contact email address")
    status: str = Field(..., description="Service status: Active or Suspended")
    remark: Optional[str] = Field(default="", description="Operational remark or suspension reason")

    def is_active(self) -> bool:
        return self.status.strip().lower() == "active"

    def is_suspended(self) -> bool:
        return self.status.strip().lower() == "suspended"

    def has_valid_email(self) -> bool:
        if not self.email:
            return False
        clean = self.email.strip()
        return bool(clean and "@" in clean and "." in clean)

    def has_valid_whatsapp(self) -> bool:
        if not self.whatsapp_number:
            return False
        clean = self.whatsapp_number.strip()
        return len(clean) >= 9


class CustomerUpdate(BaseModel):
    """Schema for updating customer status and remark (e.g. during live demonstration)."""
    status: Optional[str] = None
    remark: Optional[str] = None
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
