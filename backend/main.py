# SLT Notification Agent Backend - Live Configuration
import os
import sys

# Ensure project root is in sys.path regardless of launch directory
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.data.customer_repository import CsvCustomerRepository
from backend.storage.database import DatabaseManager
from backend.agent.email_generator import EmailGenerator
from backend.agent.email_sender import EmailSender
from backend.agent.whatsapp_generator import WhatsAppGenerator
from backend.agent.whatsapp_sender import WhatsAppSender
from backend.agent.agent_runner import AgentRunner

# Global service singletons
customer_repo = None
db_manager = None
email_generator = None
email_sender = None
whatsapp_sender = None
whatsapp_generator = None
agent_runner = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global customer_repo, db_manager, email_generator, email_sender, whatsapp_sender, whatsapp_generator, agent_runner

    # Initialize components (CsvCustomerRepository works with uploaded CSV files)
    customer_repo = CsvCustomerRepository(settings.dataset_path)
    db_manager = DatabaseManager(settings.database_path)
    email_generator = EmailGenerator(gemini_api_key=settings.gemini_api_key or settings.llm_api_key)
    email_sender = EmailSender(
        test_mode=settings.email_test_mode,
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password=settings.smtp_password,
        sender_email=settings.sender_email,
    )
    whatsapp_generator = WhatsAppGenerator(template_name=settings.meta_whatsapp_template_name)
    whatsapp_sender = WhatsAppSender(
        test_mode=settings.whatsapp_test_mode,
        api_version=settings.meta_whatsapp_api_version,
        phone_number_id=settings.meta_whatsapp_phone_number_id,
        access_token=settings.meta_whatsapp_access_token,
        template_name=settings.meta_whatsapp_template_name,
    )
    agent_runner = AgentRunner(
        repository=customer_repo,
        db=db_manager,
        email_generator=email_generator,
        email_sender=email_sender,
        whatsapp_sender=whatsapp_sender,
        whatsapp_generator=whatsapp_generator,
        channel_strategy=settings.notification_channel_strategy,
    )

    yield


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Intelligent Customer Suspension Notification Agent API (SLT Internship Proof-of-Concept)",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
from backend.api.routes_customers import router as customers_router
from backend.api.routes_agent import router as agent_router
from backend.api.routes_notifications import router as notifications_router
from backend.api.routes_settings import router as settings_router

app.include_router(customers_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(settings_router, prefix="/api")


@app.get("/")
def root():
    return {
        "title": settings.app_title,
        "version": settings.app_version,
        "status": "online",
        "mode": "synthetic-proof-of-concept",
        "disclaimer": "Fictional data only. No connection to real SLT infrastructure.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
