"""
Configuration and Environment Settings for the application.
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""
    app_title: str = "Intelligent Customer Suspension Notification Agent"
    app_version: str = "1.0.0"
    
    # Dataset & Storage
    dataset_path: str = "data/customers.csv"
    database_path: str = "backend/storage/agent_data.db"
    
    # Email Delivery (Default: Safe Simulation Mode)
    email_test_mode: bool = True
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    sender_email: str = "notifications@example.com"
    
    # WhatsApp Delivery (Default: Safe Simulation Mode)
    whatsapp_test_mode: bool = True
    meta_whatsapp_api_version: str = "v20.0"
    meta_whatsapp_phone_number_id: str = ""
    meta_whatsapp_access_token: str = ""
    meta_whatsapp_template_name: str = "service_suspension_notice"
    
    # Active Notification Channel Strategy: "BOTH", "EMAIL_ONLY", or "WHATSAPP_ONLY"
    notification_channel_strategy: str = "BOTH"
    
    # LLM Integration
    gemini_api_key: str = ""
    llm_api_key: str = ""
    
    # CORS
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
