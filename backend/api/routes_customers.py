"""
Customer API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from backend.models.customer import CustomerRecord, CustomerUpdate
from backend.data.customer_repository import CustomerRepository
from backend.storage.database import DatabaseManager

router = APIRouter(prefix="/customers", tags=["Customers"])


def get_dependencies():
    # Will be assigned from main.py
    from backend.main import customer_repo, db_manager, agent_runner
    return customer_repo, db_manager, agent_runner


@router.get("")
def list_customers(
    status: Optional[str] = Query(None, description="Filter by status: Active or Suspended"),
    search: Optional[str] = Query(None, description="Search query across name or land number"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    repo, db, _ = get_dependencies()
    records = repo.get_all()

    # Filter status
    if status:
        stat_clean = status.strip().lower()
        records = [r for r in records if r.status.lower() == stat_clean]

    # Filter search
    if search:
        s = search.strip().lower()
        records = [
            r for r in records
            if s in r.land_number.lower() or s in r.customer_name.lower() or s in (r.email or "").lower()
        ]

    total_count = len(records)
    paginated = records[offset : offset + limit]

    # Enrich with latest notification info
    enriched = []
    for r in paginated:
        latest_notif = db.get_latest_notification_for_customer(r.land_number)
        lifecycle = db.get_lifecycle_state(r.land_number)
        is_notified = bool(
            lifecycle
            and lifecycle.get("last_notified_event_id")
            and latest_notif
            and lifecycle.get("last_notified_event_id") == latest_notif.suspension_event_id
        )
        enriched.append({
            **r.model_dump(),
            "latest_notification": latest_notif.model_dump() if (is_notified and latest_notif) else None,
            "last_notified_at": latest_notif.created_at if (is_notified and latest_notif) else None,
            "notification_status": latest_notif.delivery_status.value if (is_notified and latest_notif) else ("PENDING" if r.is_suspended() else "NONE"),
        })

    return {
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "items": enriched,
    }


@router.get("/suspended")
def list_suspended_customers():
    repo, db, _ = get_dependencies()
    suspended = repo.get_suspended()

    enriched = []
    for r in suspended:
        latest_notif = db.get_latest_notification_for_customer(r.land_number)
        lifecycle = db.get_lifecycle_state(r.land_number)
        is_notified = bool(
            lifecycle
            and lifecycle.get("last_notified_event_id")
            and latest_notif
            and lifecycle.get("last_notified_event_id") == latest_notif.suspension_event_id
        )
        enriched.append({
            **r.model_dump(),
            "latest_notification": latest_notif.model_dump() if (is_notified and latest_notif) else None,
            "last_notified_at": latest_notif.created_at if (is_notified and latest_notif) else None,
            "notification_status": latest_notif.delivery_status.value if (is_notified and latest_notif) else "PENDING",
            "current_event_id": lifecycle.get("current_event_id") if lifecycle else None,
        })
    return {"total": len(enriched), "items": enriched}


@router.get("/{land_number}")
def get_customer(land_number: str):
    repo, db, _ = get_dependencies()
    customer = repo.get_by_land_number(land_number)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with land number {land_number} not found.")

    latest_notif = db.get_latest_notification_for_customer(customer.land_number)
    lifecycle = db.get_lifecycle_state(customer.land_number)

    return {
        **customer.model_dump(),
        "latest_notification": latest_notif.model_dump() if latest_notif else None,
        "lifecycle_state": lifecycle,
    }


@router.put("/{land_number}")
def update_customer_status(land_number: str, update: CustomerUpdate):
    """
    Update customer status and remark.
    Essential for live demonstrations (e.g., changing Active -> Suspended, editing remarks).
    """
    repo, db, _ = get_dependencies()
    updated = repo.update_customer(land_number, update)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Customer with land number {land_number} not found.")

    return {
        "message": f"Customer {land_number} updated successfully.",
        "customer": updated.model_dump(),
    }


@router.post("/{land_number}/test-notification")
def test_customer_notification(land_number: str):
    """
    Evaluate and preview notification for a single customer without running full batch.
    """
    _, _, runner = get_dependencies()
    result = runner.test_single_customer_notification(land_number)
    return result
