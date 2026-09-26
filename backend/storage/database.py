"""
Persistent SQLite database storage for notifications, agent runs, and lifecycle tracking.
Survives application restarts.
"""

import os
import sqlite3
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.models.notification import NotificationRecord, DeliveryStatus
from backend.models.agent_run import AgentRunRecord, RunStatus


class DatabaseManager:
    """Manages SQLite persistent storage for agent operations."""

    def __init__(self, db_path: str = "backend/storage/agent_data.db"):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    land_number TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    email TEXT,
                    whatsapp_number TEXT DEFAULT '',
                    channel TEXT NOT NULL DEFAULT 'EMAIL',
                    notification_type TEXT NOT NULL,
                    suspension_reason TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    email_content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    sent_at TEXT,
                    delivery_status TEXT NOT NULL,
                    error_message TEXT,
                    suspension_event_id TEXT NOT NULL
                )
            """)

            # Gracefully migrate existing notifications table if columns missing
            cursor.execute("PRAGMA table_info(notifications)")
            existing_cols = [col[1] for col in cursor.fetchall()]
            if "channel" not in existing_cols:
                cursor.execute("ALTER TABLE notifications ADD COLUMN channel TEXT NOT NULL DEFAULT 'EMAIL'")
            if "whatsapp_number" not in existing_cols:
                cursor.execute("ALTER TABLE notifications ADD COLUMN whatsapp_number TEXT DEFAULT ''")

            # Agent Runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    customers_checked INTEGER DEFAULT 0,
                    active_customers INTEGER DEFAULT 0,
                    suspended_customers INTEGER DEFAULT 0,
                    notifications_sent INTEGER DEFAULT 0,
                    notifications_skipped INTEGER DEFAULT 0,
                    notifications_failed INTEGER DEFAULT 0,
                    run_status TEXT NOT NULL,
                    error_summary TEXT
                )
            """)

            # Customer Lifecycle State table (for reliable duplicate prevention)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_lifecycle_state (
                    land_number TEXT PRIMARY KEY,
                    last_seen_status TEXT NOT NULL,
                    current_event_id TEXT,
                    last_notified_event_id TEXT,
                    last_status_change_at TEXT,
                    updated_at TEXT NOT NULL
                )
            """)

            # Create indices for query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_land ON notifications(land_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_event ON notifications(suspension_event_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notif_channel ON notifications(channel)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_started ON agent_runs(started_at DESC)")
            conn.commit()

    # --- Notification Operations ---

    def insert_notification(self, record: NotificationRecord) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notifications (
                    notification_id, customer_id, land_number, customer_name,
                    email, whatsapp_number, channel, notification_type,
                    suspension_reason, subject, email_content, created_at,
                    sent_at, delivery_status, error_message, suspension_event_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.notification_id,
                record.customer_id,
                record.land_number,
                record.customer_name,
                record.email,
                record.whatsapp_number or "",
                record.channel or "EMAIL",
                record.notification_type,
                record.suspension_reason,
                record.subject,
                record.email_content,
                record.created_at,
                record.sent_at,
                record.delivery_status.value if isinstance(record.delivery_status, DeliveryStatus) else str(record.delivery_status),
                record.error_message,
                record.suspension_event_id,
            ))
            conn.commit()

    def get_notifications(
        self, limit: int = 100, offset: int = 0, status: Optional[str] = None, channel: Optional[str] = None
    ) -> List[NotificationRecord]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            if status:
                conditions.append("delivery_status = ?")
                params.append(status.upper())
            if channel:
                conditions.append("channel = ?")
                params.append(channel.upper())

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            query = f"SELECT * FROM notifications {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [NotificationRecord(**dict(row)) for row in rows]

    def get_notification_by_id(self, notification_id: str) -> Optional[NotificationRecord]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notifications WHERE notification_id = ?", (notification_id,))
            row = cursor.fetchone()
            return NotificationRecord(**dict(row)) if row else None

    def get_latest_notification_for_customer(self, land_number: str) -> Optional[NotificationRecord]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM notifications WHERE land_number = ? ORDER BY created_at DESC LIMIT 1",
                (land_number,)
            )
            row = cursor.fetchone()
            return NotificationRecord(**dict(row)) if row else None

    # --- Agent Run Operations ---

    def insert_agent_run(self, record: AgentRunRecord) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute("""
                INSERT INTO agent_runs (
                    run_id, started_at, completed_at, customers_checked,
                    active_customers, suspended_customers, notifications_sent,
                    notifications_skipped, notifications_failed, run_status,
                    error_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.run_id,
                record.started_at,
                record.completed_at,
                record.customers_checked,
                record.active_customers,
                record.suspended_customers,
                record.notifications_sent,
                record.notifications_skipped,
                record.notifications_failed,
                record.run_status.value if isinstance(record.run_status, RunStatus) else str(record.run_status),
                record.error_summary,
            ))
            conn.commit()

    def update_agent_run(self, record: AgentRunRecord) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute("""
                UPDATE agent_runs SET
                    completed_at = ?,
                    customers_checked = ?,
                    active_customers = ?,
                    suspended_customers = ?,
                    notifications_sent = ?,
                    notifications_skipped = ?,
                    notifications_failed = ?,
                    run_status = ?,
                    error_summary = ?
                WHERE run_id = ?
            """, (
                record.completed_at,
                record.customers_checked,
                record.active_customers,
                record.suspended_customers,
                record.notifications_sent,
                record.notifications_skipped,
                record.notifications_failed,
                record.run_status.value if isinstance(record.run_status, RunStatus) else str(record.run_status),
                record.error_summary,
                record.run_id,
            ))
            conn.commit()

    def get_agent_runs(self, limit: int = 50) -> List[AgentRunRecord]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_runs ORDER BY started_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [AgentRunRecord(**dict(row)) for row in rows]

    def get_latest_agent_run(self) -> Optional[AgentRunRecord]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_runs ORDER BY started_at DESC LIMIT 1")
            row = cursor.fetchone()
            return AgentRunRecord(**dict(row)) if row else None

    # --- Customer Lifecycle Operations ---

    def get_lifecycle_state(self, land_number: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customer_lifecycle_state WHERE land_number = ?", (land_number,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def upsert_lifecycle_state(
        self,
        land_number: str,
        last_seen_status: str,
        current_event_id: Optional[str],
        last_notified_event_id: Optional[str],
        last_status_change_at: str,
        updated_at: str,
    ) -> None:
        with self._lock, self._get_connection() as conn:
            conn.execute("""
                INSERT INTO customer_lifecycle_state (
                    land_number, last_seen_status, current_event_id,
                    last_notified_event_id, last_status_change_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(land_number) DO UPDATE SET
                    last_seen_status = excluded.last_seen_status,
                    current_event_id = excluded.current_event_id,
                    last_notified_event_id = excluded.last_notified_event_id,
                    last_status_change_at = excluded.last_status_change_at,
                    updated_at = excluded.updated_at
            """, (
                land_number,
                last_seen_status,
                current_event_id,
                last_notified_event_id,
                last_status_change_at,
                updated_at,
            ))
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM notifications")
            total_notifications = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM notifications WHERE delivery_status IN ('SENT', 'SIMULATED')")
            sent_or_simulated = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM notifications WHERE delivery_status = 'SKIPPED'")
            skipped = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM notifications WHERE delivery_status = 'FAILED'")
            failed = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM agent_runs")
            total_runs = cursor.fetchone()[0]

            return {
                "total_notifications": total_notifications,
                "sent_or_simulated": sent_or_simulated,
                "skipped_notifications": skipped,
                "failed_notifications": failed,
                "total_agent_runs": total_runs,
            }

    # --- Cache and Data Reset Operations ---

    def clear_lifecycle_states(self) -> int:
        """
        Delete all customer lifecycle state records (duplicate prevention cache).
        This ensures that when a new CSV dataset is uploaded, all customer accounts
        are evaluated freshly and not skipped as duplicates from previous runs.
        """
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customer_lifecycle_state")
            cleared = cursor.rowcount
            conn.commit()
            return cleared

    def clear_notifications(self) -> int:
        """Delete all notification records from persistent storage."""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications")
            cleared = cursor.rowcount
            conn.commit()
            return cleared

    def clear_agent_runs(self) -> int:
        """Delete all agent run history from persistent storage."""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM agent_runs")
            cleared = cursor.rowcount
            conn.commit()
            return cleared

    def clear_all_cache(self, clear_logs: bool = False) -> Dict[str, int]:
        """
        Clear duplicate prevention cache and optionally dispatch logs and runs.
        """
        lifecycle_cleared = self.clear_lifecycle_states()
        notifs_cleared = self.clear_notifications() if clear_logs else 0
        runs_cleared = self.clear_agent_runs() if clear_logs else 0
        return {
            "lifecycle_cleared": lifecycle_cleared,
            "notifications_cleared": notifs_cleared,
            "runs_cleared": runs_cleared,
        }
