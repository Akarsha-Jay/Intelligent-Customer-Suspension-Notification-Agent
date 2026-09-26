# Synthetic Customer Dataset Documentation

## Important Business Context & Disclaimer

> [!IMPORTANT]
> **100% Synthetic / Fictional Dataset**  
> Access to the original SLT customer database is currently not available for this proof-of-concept project.  
> As instructed by project supervision, this dataset is **completely fictional and synthetic**.  
> - No real SLT customer information, names, phone numbers, or email addresses are used.  
> - No connection to any real SLT database or customer care system exists.  
> - No real SLT operational policies, payment amounts, restoration periods, or phone numbers are assumed or used.  
> 
> The architecture is decoupled so that this sample dataset can later be replaced with an authorized real SLT database or API without rewriting the agent.

---

## Dataset Overview

- **File Path**: `data/customers.csv`
- **Total Records**: 100 (configurable via `scripts/generate_sample_data.py`)
- **Format**: Comma-Separated Values (CSV), UTF-8 encoding

---

## Column Descriptions

| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `land_number` | String | Fictional Sri Lankan-format landline number | `0116789001` |
| `customer_name` | String | Fictional customer name | `Customer 001` |
| `whatsapp_number` | String | Fictional Sri Lankan mobile format | `+94770000001` |
| `email` | String | Safe placeholder email (`@example.com`) or empty | `customer001@example.com` |
| `status` | String | Service status: `Active` or `Suspended` | `Active`, `Suspended` |
| `remark` | String | Service note explaining account state or suspension | `Bill overdue` |

---

## Service Status & Remarks Distribution

- **Active Customers (~60-70%)**: Accounts in good standing. The agent skips these customers and never sends a suspension notification.
- **Suspended Customers (~30-40%)**: Accounts requiring evaluation by the agent.

### Suspension Categories & Remark Mappings

| Suspension Category | Sample Remarks in Dataset | Expected Notification Tone |
| :--- | :--- | :--- |
| `BILL_OVERDUE` | "Bill overdue", "Unpaid bill", "Outstanding payment" | Payment overdue notice |
| `PAYMENT_NOT_RECEIVED` | "Payment not received", "Non-payment of monthly charges" | Payment reminder |
| `CUSTOMER_REQUESTED` | "Customer requested temporary suspension", "Temporary suspension requested by customer" | Acknowledgment of customer-requested hold |
| `TECHNICAL_ISSUE` | "Technical issue", "Service issue", "Line maintenance" | Technical service notice |
| `ACCOUNT_ISSUE` | "Account issue", "Verification required", "Identity verification pending" | Account verification notice |
| `UNKNOWN` | Unrecognized or empty remark | General suspension notice |

---

## Standard Demonstration Test Cases

The first 8 records in `data/customers.csv` are deterministically seeded for consistent testing:

1. **Customer 001** (`0116789001`): `Active` — Agent skips (No notification).
2. **Customer 002** (`0116789002`): `Suspended` ("Bill overdue") — Category `BILL_OVERDUE`.
3. **Customer 003** (`0116789003`): `Suspended` ("Payment not received") — Category `PAYMENT_NOT_RECEIVED`.
4. **Customer 004** (`0116789004`): `Suspended` ("Customer requested temporary suspension") — Category `CUSTOMER_REQUESTED`.
5. **Customer 005** (`0116789005`): `Suspended` ("Technical issue") — Category `TECHNICAL_ISSUE`.
6. **Customer 006** (`0116789006`): `Suspended` ("Account issue") — Category `ACCOUNT_ISSUE`.
7. **Customer 007** (`0116789007`): `Suspended` ("Bill overdue", Missing email `""`) — Handled safely as `SKIPPED` without crashing.
8. **Customer 008** (`0116789008`): `Suspended` ("Customer requested service suspension", Missing email `""`) — Handled safely as `SKIPPED`.

---

## Regenerating the Dataset

You can regenerate or resize the dataset at any time using:

```bash
# 100 records (default)
python scripts/generate_sample_data.py --count 100

# 500 records
python scripts/generate_sample_data.py --count 500

# 1000 records
python scripts/generate_sample_data.py --count 1000
```
