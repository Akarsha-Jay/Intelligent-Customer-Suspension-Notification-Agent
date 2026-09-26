"""
Intelligent Customer Suspension Notification Agent Runner.

Orchestrates:
1. Loading customer records via CustomerRepository
2. Evaluating each customer status & remark
3. Filtering Active vs Suspended
4. Preventing duplicate notifications for the same suspension event
5. Generating professional emails (template or optional LLM)
6. Safe email simulation/dispatch
7. Recording persistent notification history and execution run logs
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.data.customer_repository import CustomerRepository
from backend.storage.database import DatabaseManager
from backend.agent.suspension_analyzer import SuspensionAnalyzer
from backend.agent.state_tracker import StateTracker, DecisionAction
from backend.agent.notification_decision import NotificationDecisionEngine
from backend.agent.email_generator import EmailGenerator
from backend.agent.email_sender import EmailSender
from backend.agent.whatsapp_generator import WhatsAppGenerator
from backend.agent.whatsapp_sender import WhatsAppSender
from backend.models.notification import NotificationRecord, DeliveryStatus
from backend.models.agent_run import AgentRunRecord, RunStatus

logger = logging.getLogger("agent.runner")


class AgentRunner:
    """Core intelligent agent execution orchestrator."""

    def __init__(
        self,
        repository: CustomerRepository,
        db: DatabaseManager,
        email_generator: EmailGenerator,
        email_sender: EmailSender,
        whatsapp_sender: Optional[WhatsAppSender] = None,
        whatsapp_generator: Optional[WhatsAppGenerator] = None,
        channel_strategy: str = "BOTH",
    ):
        self.repository = repository
        self.db = db
        self.email_generator = email_generator
        self.email_sender = email_sender
        self.whatsapp_sender = whatsapp_sender
        self.whatsapp_generator = whatsapp_generator or WhatsAppGenerator()
        self.channel_strategy = (channel_strategy or "BOTH").upper()
        self.state_tracker = StateTracker(self.db)
        self.decision_engine = NotificationDecisionEngine(self.state_tracker)
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def run(self) -> AgentRunRecord:
        """
        Execute a complete cycle of the Intelligent Notification Agent.
        """
        if self._is_running:
            raise RuntimeError("Agent is already running another execution cycle.")

        self._is_running = True
        run_id = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        started_at = datetime.now(timezone.utc).isoformat()

        run_record = AgentRunRecord(
            run_id=run_id,
            started_at=started_at,
            run_status=RunStatus.COMPLETED,
        )
        self.db.insert_agent_run(run_record)

        error_logs = []

        try:
            customers = self.repository.get_all()
            run_record.customers_checked = len(customers)

            for customer in customers:
                try:
                    if customer.is_active():
                        run_record.active_customers += 1
                        # Notify state tracker to close any open suspension events
                        self.state_tracker.evaluate_customer(customer)
                        continue

                    if customer.is_suspended():
                        run_record.suspended_customers += 1

                    # Evaluate decision
                    decision = self.decision_engine.evaluate(customer)

                    if decision.action == DecisionAction.SKIP_ACTIVE:
                        continue

                    if decision.action == DecisionAction.SKIP_DUPLICATE:
                        run_record.notifications_skipped += 1
                        logger.info(f"Duplicate prevented: {customer.land_number} ({decision.suspension_event_id})")
                        continue

                    if decision.action == DecisionAction.SKIP_MISSING_EMAIL:
                        run_record.notifications_skipped += 1
                        # Record a skipped notification record in audit history (Case G)
                        notif_id = f"NOTIF-{customer.land_number}-{uuid.uuid4().hex[:6].upper()}"
                        skipped_notif = NotificationRecord(
                            notification_id=notif_id,
                            customer_id=customer.land_number,
                            land_number=customer.land_number,
                            customer_name=customer.customer_name,
                            email=customer.email or "",
                            whatsapp_number=customer.whatsapp_number or "",
                            channel="EMAIL",
                            notification_type=decision.category.value if decision.category else "UNKNOWN",
                            suspension_reason=customer.remark or "",
                            subject="Service Suspension Notification",
                            email_content="[Notification skipped: recipient contact details are missing or invalid]",
                            created_at=datetime.now(timezone.utc).isoformat(),
                            sent_at=None,
                            delivery_status=DeliveryStatus.SKIPPED,
                            error_message="Customer contact details (email and WhatsApp) are missing or invalid.",
                            suspension_event_id=decision.suspension_event_id or "UNKNOWN",
                        )
                        self.db.insert_notification(skipped_notif)
                        # Mark event as evaluated so it does not loop infinitely
                        if decision.suspension_event_id:
                            self.state_tracker.mark_event_notified(customer.land_number, decision.suspension_event_id)
                        continue

                    if decision.action == DecisionAction.PROCEED_NOTIFICATION:
                        dispatched_any = False
                        now_iso = datetime.now(timezone.utc).isoformat()
                        allow_email = self.channel_strategy in ("BOTH", "EMAIL_ONLY")
                        allow_whatsapp = self.channel_strategy in ("BOTH", "WHATSAPP_ONLY") and (self.whatsapp_sender is not None)

                        # --- Channel 1: Email Dispatch ---
                        if allow_email and customer.has_valid_email():
                            generated = self.email_generator.generate(
                                customer_name=customer.customer_name,
                                land_number=customer.land_number,
                                category=decision.category,
                                remark=customer.remark or "",
                            )

                            delivery_status, error_msg = self.email_sender.send_notification(
                                recipient_email=customer.email,
                                subject=generated.subject,
                                body=generated.body,
                            )

                            email_notif_id = f"NOTIF-{customer.land_number}-EML-{uuid.uuid4().hex[:4].upper()}"
                            email_notif_record = NotificationRecord(
                                notification_id=email_notif_id,
                                customer_id=customer.land_number,
                                land_number=customer.land_number,
                                customer_name=customer.customer_name,
                                email=customer.email,
                                whatsapp_number=customer.whatsapp_number or "",
                                channel="EMAIL",
                                notification_type=decision.category.value,
                                suspension_reason=customer.remark or "",
                                subject=generated.subject,
                                email_content=generated.body,
                                created_at=now_iso,
                                sent_at=now_iso if delivery_status in (DeliveryStatus.SENT, DeliveryStatus.SIMULATED) else None,
                                delivery_status=delivery_status,
                                error_message=error_msg,
                                suspension_event_id=decision.suspension_event_id,
                            )
                            self.db.insert_notification(email_notif_record)

                            if delivery_status in (DeliveryStatus.SENT, DeliveryStatus.SIMULATED):
                                run_record.notifications_sent += 1
                                dispatched_any = True
                            else:
                                run_record.notifications_failed += 1
                                error_logs.append(f"Customer {customer.land_number} (Email): {error_msg}")

                        # --- Channel 2: WhatsApp Dispatch ---
                        if allow_whatsapp and customer.has_valid_whatsapp():
                            wa_preview = self.whatsapp_generator.generate_human_preview(
                                customer_name=customer.customer_name,
                                land_number=customer.land_number,
                                reason=customer.remark or "",
                            )

                            wa_status, wa_error = self.whatsapp_sender.send_notification(
                                recipient_phone=customer.whatsapp_number,
                                customer_name=customer.customer_name,
                                land_number=customer.land_number,
                                reason=customer.remark or "",
                            )

                            wa_notif_id = f"NOTIF-{customer.land_number}-WAP-{uuid.uuid4().hex[:4].upper()}"
                            wa_notif_record = NotificationRecord(
                                notification_id=wa_notif_id,
                                customer_id=customer.land_number,
                                land_number=customer.land_number,
                                customer_name=customer.customer_name,
                                email=customer.email or "",
                                whatsapp_number=customer.whatsapp_number,
                                channel="WHATSAPP",
                                notification_type=decision.category.value,
                                suspension_reason=customer.remark or "",
                                subject="WhatsApp Suspension Notice",
                                email_content=wa_preview,
                                created_at=now_iso,
                                sent_at=now_iso if wa_status in (DeliveryStatus.SENT, DeliveryStatus.SIMULATED) else None,
                                delivery_status=wa_status,
                                error_message=wa_error,
                                suspension_event_id=decision.suspension_event_id,
                            )
                            self.db.insert_notification(wa_notif_record)

                            if wa_status in (DeliveryStatus.SENT, DeliveryStatus.SIMULATED):
                                run_record.notifications_sent += 1
                                dispatched_any = True
                            else:
                                run_record.notifications_failed += 1
                                error_logs.append(f"Customer {customer.land_number} (WhatsApp): {wa_error}")

                        # If user requested WhatsApp only but customer lacks WhatsApp
                        if self.channel_strategy == "WHATSAPP_ONLY" and not customer.has_valid_whatsapp():
                            run_record.notifications_skipped += 1
                            wa_notif_id = f"NOTIF-{customer.land_number}-WAP-{uuid.uuid4().hex[:4].upper()}"
                            self.db.insert_notification(NotificationRecord(
                                notification_id=wa_notif_id,
                                customer_id=customer.land_number,
                                land_number=customer.land_number,
                                customer_name=customer.customer_name,
                                email=customer.email or "",
                                whatsapp_number="",
                                channel="WHATSAPP",
                                notification_type=decision.category.value,
                                suspension_reason=customer.remark or "",
                                subject="WhatsApp Suspension Notice",
                                email_content="[Notification skipped: missing WhatsApp contact number]",
                                created_at=now_iso,
                                delivery_status=DeliveryStatus.SKIPPED,
                                error_message="Customer missing WhatsApp contact number.",
                                suspension_event_id=decision.suspension_event_id,
                            ))

                        # Mark event notified for duplicate prevention
                        if decision.suspension_event_id and (dispatched_any or run_record.notifications_failed > 0 or not allow_email):
                            self.state_tracker.mark_event_notified(customer.land_number, decision.suspension_event_id)

                except Exception as cust_err:
                    run_record.notifications_failed += 1
                    err_text = f"Error processing customer {customer.land_number}: {str(cust_err)}"
                    logger.error(err_text)
                    error_logs.append(err_text)

        except Exception as e:
            run_record.run_status = RunStatus.FAILED
            run_record.error_summary = f"Fatal agent error: {str(e)}"
            logger.error(f"Fatal error in agent run: {e}")
        finally:
            run_record.completed_at = datetime.now(timezone.utc).isoformat()
            if run_record.run_status != RunStatus.FAILED:
                if run_record.notifications_failed > 0:
                    run_record.run_status = RunStatus.COMPLETED_WITH_ERRORS
                else:
                    run_record.run_status = RunStatus.COMPLETED

            if error_logs:
                run_record.error_summary = "; ".join(error_logs[:5])

            self.db.update_agent_run(run_record)
            self._is_running = False

        return run_record

    def test_single_customer_notification(self, land_number: str) -> Dict[str, Any]:
        """
        Manually trigger and preview notification evaluation for a single customer.
        Useful for live demonstrations.
        """
        customer = self.repository.get_by_land_number(land_number)
        if not customer:
            return {"success": False, "error": f"Customer with land number {land_number} not found."}

        decision = self.decision_engine.evaluate(customer)
        if decision.action == DecisionAction.SKIP_ACTIVE:
            return {
                "success": True,
                "action": decision.action.value,
                "message": "Customer is Active. No notification required.",
                "customer": customer.model_dump(),
            }

        if decision.action == DecisionAction.SKIP_DUPLICATE:
            return {
                "success": True,
                "action": decision.action.value,
                "message": f"Already notified for suspension event {decision.suspension_event_id}. Duplicate prevented.",
                "customer": customer.model_dump(),
                "event_id": decision.suspension_event_id,
            }

        if decision.action == DecisionAction.SKIP_MISSING_EMAIL:
            return {
                "success": False,
                "action": decision.action.value,
                "message": "Customer is suspended but email address is missing.",
                "customer": customer.model_dump(),
                "category": decision.category.value if decision.category else "UNKNOWN",
            }

        # Generate preview email
        generated = self.email_generator.generate(
            customer_name=customer.customer_name,
            land_number=customer.land_number,
            category=decision.category,
            remark=customer.remark or "",
        )

        return {
            "success": True,
            "action": decision.action.value,
            "category": decision.category.value,
            "analysis": decision.analysis.model_dump() if decision.analysis else None,
            "event_id": decision.suspension_event_id,
            "email_preview": generated.model_dump(),
            "customer": customer.model_dump(),
        }
