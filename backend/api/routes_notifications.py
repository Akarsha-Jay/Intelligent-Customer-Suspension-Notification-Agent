"""
Notifications API Endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.models.notification import DeliveryStatus

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_dependencies():
    from backend.main import db_manager
    return db_manager


@router.get("")
def list_notifications(
    status: Optional[str] = Query(None, description="Filter by delivery status: SENT, SIMULATED, SKIPPED, FAILED"),
    channel: Optional[str] = Query(None, description="Filter by channel: EMAIL or WHATSAPP"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    db = get_dependencies()
    notifs = db.get_notifications(limit=limit, offset=offset, status=status, channel=channel)
    return {
        "count": len(notifs),
        "limit": limit,
        "offset": offset,
        "items": [n.model_dump() for n in notifs],
    }


@router.get("/{notification_id}")
def get_notification_detail(notification_id: str):
    db = get_dependencies()
    notif = db.get_notification_by_id(notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail=f"Notification {notification_id} not found.")
    return notif.model_dump()
