from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from pydantic import BaseModel
from backend.config import settings
from backend.models.customer import CustomerRecord
from backend.models.notification import DeliveryStatus
import io
import csv
import re
import os
from typing import List, Dict, Optional

router = APIRouter(tags=["Settings & Stats"])


def get_dependencies():
    from backend.main import customer_repo, db_manager, agent_runner, email_sender
    return customer_repo, db_manager, agent_runner, email_sender


def get_whatsapp_sender():
    from backend.main import whatsapp_sender
    return whatsapp_sender


# Common column synonyms for smart auto-mapping SLT exports
COLUMN_SYNONYMS = {
    "land_number": [
        "landnumber", "landline", "landlinenumber", "telephone", "telephoneno", 
        "telephonenumber", "teleno", "phone", "phonenumber", "accountno", 
        "account", "accountnumber", "accno", "serviceno", "tpno", "msisdn", "number",
        "tp", "tel", "land", "landno", "tele", "telephone_number", "phoneno", "phone_number",
        "account_id", "accountid", "acc_no", "acc", "subscriberno", "subscriber_no",
        "service_number", "subno", "id"
    ],
    "customer_name": [
        "customername", "name", "fullname", "clientname", "accountname", 
        "subscribername", "custname", "customer", "subscriber", "client", "cust",
        "username", "user", "cust_name", "customer_full_name"
    ],
    "email": [
        "email", "mail", "emailaddress", "customeremail", "custemail", "e_mail",
        "email_address", "user_email"
    ],
    "whatsapp_number": [
        "whatsappnumber", "whatsapp", "mobile", "mobileno", "mobilenumber", 
        "contactno", "contactnumber", "contact", "whatsapp_no", "mobile_no", "phone2"
    ],
    "status": [
        "status", "accountstatus", "servicestatus", "state", "substatus", 
        "currentstatus", "servicestate", "service_status", "active_status", "condition"
    ],
    "remark": [
        "remark", "remarks", "reason", "suspensionreason", "comments", 
        "comment", "description", "reasonforsuspension", "note", "notes",
        "reasons", "suspension_reason", "details", "explanation"
    ],
}


def _clean_header_key(key: str) -> str:
    """Normalize a column header to lowercase alphanumeric."""
    return re.sub(r"[^a-z0-9]", "", str(key).lower().strip())


def _detect_column_mapping(headers: List[str]) -> Dict[str, Optional[str]]:
    """Map detected CSV headers to standard CustomerRecord fields."""
    normalized_headers = {_clean_header_key(h): h for h in headers if h}
    mapping: Dict[str, Optional[str]] = {}

    for target_field, synonyms in COLUMN_SYNONYMS.items():
        found = None
        for syn in synonyms:
            if syn in normalized_headers:
                found = normalized_headers[syn]
                break
        mapping[target_field] = found

    return mapping


@router.get("/dataset/template")
def download_dataset_template():
    """
    Download a ready-to-use sample CSV template formatted for the SLT Notification Agent.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["land_number", "customer_name", "whatsapp_number", "email", "status", "remark"])
    writer.writerow(["0112345678", "Nimal Perera", "+94771234567", "nimal.perera@example.com", "Active", "Account active in good standing"])
    writer.writerow(["0112345679", "Kamal Silva", "+94771234568", "kamal.silva@example.com", "Suspended", "Bill overdue"])
    writer.writerow(["0112345680", "Sunil Fernando", "+94771234569", "sunil.fernando@example.com", "Suspended", "Technical issue"])
    writer.writerow(["0112345681", "Anoma Jayasinghe", "+94771234570", "anoma.j@example.com", "Suspended", "Customer requested temporary suspension"])
    writer.writerow(["0112345682", "Ruwan Bandara", "+94771234571", "", "Suspended", "Bill overdue (Missing Email Test)"])
    
    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=slt_customer_dataset_template.csv"},
    )


@router.post("/dataset/upload")
async def upload_customer_dataset(
    file: UploadFile = File(...),
    clear_cache: bool = True,
):
    """
    Upload a new CSV dataset (SLT customer export).
    Intelligently maps columns, validates records, updates storage,
    clears lifecycle cache to prevent skipping emails for new uploads, and returns analytics.
    """
    if not file.filename.lower().endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only CSV text files are supported.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    # Try decoding UTF-8 (with BOM handling) then latin-1
    content_str = ""
    for enc in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            content_str = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if not content_str:
        raise HTTPException(status_code=400, detail="Unable to decode file text encoding.")

    # Determine delimiter
    first_line = content_str.splitlines()[0] if content_str.splitlines() else ""
    delimiter = ","
    if ";" in first_line and first_line.count(";") > first_line.count(","):
        delimiter = ";"
    elif "\t" in first_line:
        delimiter = "\t"

    reader = csv.DictReader(io.StringIO(content_str), delimiter=delimiter)
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="No headers found in uploaded CSV file.")

    mapping = _detect_column_mapping(reader.fieldnames)
    first_row_is_data = False

    # Landline or identifier mapping check
    if not mapping.get("land_number"):
        # Check positional fallback: if column 0 contains digits, the file likely has no header row
        first_col = reader.fieldnames[0] if reader.fieldnames else ""
        if first_col and any(c.isdigit() for c in first_col):
            # Positional fallback (first column is landline)
            mapping["land_number"] = first_col
            first_row_is_data = True
            if len(reader.fieldnames) > 1:
                mapping["customer_name"] = reader.fieldnames[1]
            if len(reader.fieldnames) > 2:
                mapping["whatsapp_number"] = reader.fieldnames[2]
            if len(reader.fieldnames) > 3:
                mapping["email"] = reader.fieldnames[3]
            if len(reader.fieldnames) > 4:
                mapping["status"] = reader.fieldnames[4]
            if len(reader.fieldnames) > 5:
                mapping["remark"] = reader.fieldnames[5]
        else:
            detected_list = ", ".join(reader.fieldnames)
            raise HTTPException(
                status_code=400,
                detail=f"Could not identify a customer account or telephone column. Detected headers: [{detected_list}]. Expected headers like: land_number, telephone, phone, or account_no. You can download the sample template using the link above.",
            )

    records: List[CustomerRecord] = []
    
    # If the first row was data rather than header names, prepend it
    if first_row_is_data and reader.fieldnames:
        first_row_dict = {col: col for col in reader.fieldnames}
        land_val = first_row_dict.get(mapping["land_number"] or "", "").strip()
        if land_val:
            records.append(
                CustomerRecord(
                    land_number=land_val,
                    customer_name=first_row_dict.get(mapping.get("customer_name") or "", f"Subscriber {land_val}").strip() or f"Subscriber {land_val}",
                    whatsapp_number=first_row_dict.get(mapping.get("whatsapp_number") or "", "").strip(),
                    email=first_row_dict.get(mapping.get("email") or "", "").strip(),
                    status="Suspended" if "susp" in first_row_dict.get(mapping.get("status") or "", "").lower() else "Active",
                    remark=first_row_dict.get(mapping.get("remark") or "", "Imported record").strip() or "Imported record",
                )
            )
    line_idx = 1
    for row in reader:
        line_idx += 1
        # Extract fields using mapping
        land_num_raw = (row.get(mapping["land_number"] or "") or "").strip() if mapping["land_number"] else ""
        if not land_num_raw:
            continue  # skip completely blank line

        name_raw = (row.get(mapping["customer_name"] or "") or "").strip() if mapping["customer_name"] else f"Subscriber {land_num_raw}"
        email_raw = (row.get(mapping["email"] or "") or "").strip() if mapping["email"] else ""
        whatsapp_raw = (row.get(mapping["whatsapp_number"] or "") or "").strip() if mapping["whatsapp_number"] else ""
        status_raw = (row.get(mapping["status"] or "") or "Active").strip() if mapping["status"] else "Active"
        remark_raw = (row.get(mapping["remark"] or "") or "").strip() if mapping["remark"] else ""

        # Normalize status to standard values
        status_lower = status_raw.lower()
        if "susp" in status_lower or "inact" in status_lower or "bar" in status_lower or "hold" in status_lower:
            normalized_status = "Suspended"
        else:
            normalized_status = "Active"

        records.append(
            CustomerRecord(
                land_number=land_num_raw,
                customer_name=name_raw or f"Subscriber {land_num_raw}",
                whatsapp_number=whatsapp_raw,
                email=email_raw,
                status=normalized_status,
                remark=remark_raw or ("Suspension pending" if normalized_status == "Suspended" else "Active"),
            )
        )

    if not records:
        raise HTTPException(status_code=400, detail="No valid customer data rows were found in the file.")

    repo, db, _, _ = get_dependencies()
    repo.save_all(records)

    # Automatically clear lifecycle duplicate cache so the new dataset's accounts
    # are evaluated cleanly and notifications are not skipped as duplicates from previous runs.
    cleared_lifecycle_count = 0
    if clear_cache:
        cleared_lifecycle_count = db.clear_lifecycle_states()

    # Compute dataset summary statistics
    total = len(records)
    suspended_count = sum(1 for r in records if r.is_suspended())
    active_count = total - suspended_count
    with_email = sum(1 for r in records if r.email and "@" in r.email)
    missing_email = total - with_email
    suspended_ready = sum(1 for r in records if r.is_suspended() and r.email and "@" in r.email)

    return {
        "success": True,
        "message": f"Successfully imported {total} records from {file.filename}.",
        "filename": file.filename,
        "total_records": total,
        "active_records": active_count,
        "suspended_records": suspended_count,
        "suspended_with_email": suspended_ready,
        "missing_email_records": missing_email,
        "mapped_columns": {k: v for k, v in mapping.items() if v is not None},
        "preview": [r.model_dump() for r in records[:6]],
        "cache_cleared": clear_cache,
        "lifecycle_records_cleared": cleared_lifecycle_count,
    }





@router.get("/stats")
def get_dashboard_stats():
    """Aggregated statistics for the main dashboard view."""
    repo, db, runner, _ = get_dependencies()
    customers = repo.get_all()
    
    total_customers = len(customers)
    active_customers = sum(1 for c in customers if c.is_active())
    suspended_customers = sum(1 for c in customers if c.is_suspended())
    
    db_stats = db.get_stats()
    latest_run = db.get_latest_agent_run()

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "suspended_customers": suspended_customers,
        "notifications_sent": db_stats["sent_or_simulated"],
        "notifications_skipped": db_stats["skipped_notifications"],
        "notifications_failed": db_stats["failed_notifications"],
        "total_notifications": db_stats["total_notifications"],
        "total_agent_runs": db_stats["total_agent_runs"],
        "agent_status": "RUNNING" if runner.is_running else "READY",
        "last_agent_run": latest_run.model_dump() if latest_run else None,
    }


@router.get("/settings")
def get_system_settings():
    """Safe system settings representation with masked credentials."""
    _, _, runner, email_sender = get_dependencies()
    whatsapp_sender = get_whatsapp_sender()
    wa_test = whatsapp_sender.test_mode if whatsapp_sender else True
    wa_configured = bool(whatsapp_sender.is_configured_for_real_delivery()) if whatsapp_sender else False
    strategy = runner.channel_strategy if runner else settings.notification_channel_strategy

    return {
        "email_mode": "SIMULATION" if email_sender.test_mode else "REAL_SMTP",
        "smtp_configured": bool(settings.smtp_host),
        "smtp_host": settings.smtp_host or "(Not configured - using simulation)",
        "smtp_port": settings.smtp_port,
        "sender_email": settings.sender_email,
        "whatsapp_mode": "SIMULATION" if wa_test else "REAL_META",
        "whatsapp_configured": wa_configured,
        "whatsapp_phone_number_id": settings.meta_whatsapp_phone_number_id or "(Not provided yet)",
        "whatsapp_template": settings.meta_whatsapp_template_name,
        "channel_strategy": strategy,
        "llm_status": "ENABLED" if bool(settings.gemini_api_key or settings.llm_api_key) else "TEMPLATE_FALLBACK",
        "llm_provider": "Google Gemini" if bool(settings.gemini_api_key or settings.llm_api_key) else "Built-in Templates",
        "dataset_path": settings.dataset_path,
        "database_path": settings.database_path,
        "is_synthetic_data": True,
        "disclaimer": "100% fictional sample dataset. No connection to real SLT infrastructure.",
    }


@router.post("/settings/toggle-mode")
def toggle_email_mode():
    """Toggle between simulation mode and real SMTP mode."""
    _, _, _, email_sender = get_dependencies()
    email_sender.test_mode = not email_sender.test_mode
    return {
        "message": f"Email mode updated to {'SIMULATION' if email_sender.test_mode else 'REAL_SMTP'}",
        "email_mode": "SIMULATION" if email_sender.test_mode else "REAL_SMTP",
    }


@router.post("/settings/toggle-whatsapp-mode")
def toggle_whatsapp_mode():
    """Toggle between simulation mode and real Meta Cloud API mode for WhatsApp."""
    whatsapp_sender = get_whatsapp_sender()
    if not whatsapp_sender:
        raise HTTPException(status_code=500, detail="WhatsApp service is not initialized")
    whatsapp_sender.test_mode = not whatsapp_sender.test_mode
    return {
        "message": f"WhatsApp mode updated to {'SIMULATION' if whatsapp_sender.test_mode else 'REAL_META'}",
        "whatsapp_mode": "SIMULATION" if whatsapp_sender.test_mode else "REAL_META",
    }


class ChannelStrategyRequest(BaseModel):
    strategy: str


@router.post("/settings/channel-strategy")
def set_channel_strategy(req: ChannelStrategyRequest):
    """Set active notification channel strategy: EMAIL_ONLY, WHATSAPP_ONLY, or BOTH."""
    strategy = req.strategy.upper().strip()
    if strategy not in ("BOTH", "EMAIL_ONLY", "WHATSAPP_ONLY"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy '{strategy}'. Must be BOTH, EMAIL_ONLY, or WHATSAPP_ONLY.",
        )

    _, _, runner, _ = get_dependencies()
    if runner:
        runner.channel_strategy = strategy
    settings.notification_channel_strategy = strategy

    return {
        "success": True,
        "message": f"Active dispatch channel updated to {strategy}",
        "channel_strategy": strategy,
    }


class WhatsAppTestRequest(BaseModel):
    recipient_number: str


@router.post("/settings/test-whatsapp")
def test_whatsapp_notification(req: WhatsAppTestRequest):
    """Test send a single simulated or real WhatsApp message."""
    whatsapp_sender = get_whatsapp_sender()
    if not whatsapp_sender:
        raise HTTPException(status_code=500, detail="WhatsApp sender is not initialized")

    status, err = whatsapp_sender.send_notification(
        recipient_phone=req.recipient_number,
        customer_name="Test Customer",
        land_number="0112345678",
        reason="Account audit suspension test",
    )
    return {
        "success": status in (DeliveryStatus.SENT, DeliveryStatus.SIMULATED),
        "status": status.value,
        "error": err,
    }


@router.post("/dataset/clear")
@router.post("/dataset/reset")
def clear_uploaded_dataset():
    """
    Remove the currently uploaded CSV dataset and clear the duplicate prevention cache.
    The system will wait for a new CSV dataset upload.
    """
    repo, db, _, _ = get_dependencies()
    if hasattr(repo, "clear"):
        repo.clear()
    elif os.path.exists(settings.dataset_path):
        try:
            os.remove(settings.dataset_path)
        except OSError:
            pass
    cleared = db.clear_lifecycle_states()
    return {
        "success": True,
        "message": "Uploaded customer dataset and duplicate cache cleared successfully.",
        "count": 0,
        "total_records": 0,
        "lifecycle_records_cleared": cleared,
    }


@router.post("/cache/clear")
def clear_system_cache(clear_notifications: bool = False, clear_runs: bool = False):
    """
    Clear duplicate prevention cache (customer lifecycle tracking states)
    and optionally dispatch logs/runs.
    """
    _, db, _, _ = get_dependencies()
    result = db.clear_all_cache(clear_logs=clear_notifications)
    if clear_runs:
        result["runs_cleared"] = db.clear_agent_runs()
    return {
        "success": True,
        "message": f"Successfully cleared {result['lifecycle_cleared']} cached customer lifecycle states.",
        "details": result,
    }
