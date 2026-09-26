"""
Customer Data Access Layer (Repository Pattern).

This layer abstracts data storage. The agent only interacts with the
CustomerRepository interface. Later, CsvCustomerRepository can be swapped
for a future authorized SltDatabaseRepository or SltApiRepository without
changing the agent's logic.
"""

import os
import csv
import time
import threading
from abc import ABC, abstractmethod
from typing import List, Optional
from backend.models.customer import CustomerRecord, CustomerUpdate


class CustomerRepository(ABC):
    """Abstract Base Class for Customer Data Access."""

    @abstractmethod
    def get_all(self) -> List[CustomerRecord]:
        """Retrieve all customer records."""
        pass

    @abstractmethod
    def get_by_land_number(self, land_number: str) -> Optional[CustomerRecord]:
        """Retrieve a specific customer by land number."""
        pass

    @abstractmethod
    def get_suspended(self) -> List[CustomerRecord]:
        """Retrieve all currently suspended customers."""
        pass

    @abstractmethod
    def update_customer(self, land_number: str, update_data: CustomerUpdate) -> Optional[CustomerRecord]:
        """Update customer details (e.g. status or remark)."""
        pass

    @abstractmethod
    def save_all(self, records: List[CustomerRecord]) -> None:
        """Replace the entire dataset with a new collection of records."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all customer records and reset dataset."""
        pass


class CsvCustomerRepository(CustomerRepository):
    """
    CSV-backed Customer Repository implementation.
    Reads and writes to data/customers.csv with thread safety.
    Operates gracefully when no CSV dataset has been uploaded yet.
    """

    def __init__(self, csv_filepath: str):
        self.csv_filepath = os.path.abspath(csv_filepath)
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.csv_filepath), exist_ok=True)

    def _read_records(self) -> List[CustomerRecord]:
        if not os.path.exists(self.csv_filepath):
            return []
        records: List[CustomerRecord] = []
        try:
            with open(self.csv_filepath, mode="r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    return []
                for row in reader:
                    land_val = (row.get("land_number") or "").strip()
                    if not land_val:
                        continue
                    records.append(CustomerRecord(
                        land_number=land_val,
                        customer_name=(row.get("customer_name") or f"Subscriber {land_val}").strip(),
                        whatsapp_number=(row.get("whatsapp_number") or "").strip(),
                        email=(row.get("email") or "").strip(),
                        status=(row.get("status") or "Active").strip(),
                        remark=(row.get("remark") or "").strip(),
                    ))
        except (OSError, UnicodeDecodeError):
            return []
        return records

    def _write_records(self, records: List[CustomerRecord]) -> None:
        fieldnames = ["land_number", "customer_name", "whatsapp_number", "email", "status", "remark"]
        temp_filepath = f"{self.csv_filepath}.tmp"
        
        # Write to temp file first
        with open(temp_filepath, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow(r.model_dump())
        
        # Windows-resilient atomic or direct replacement with retry
        replaced = False
        for attempt in range(8):
            try:
                os.replace(temp_filepath, self.csv_filepath)
                replaced = True
                break
            except (PermissionError, OSError):
                time.sleep(0.05 * (attempt + 1))
        
        if not replaced:
            # Fallback for Windows file locks/watchers: write directly to target file with retries
            for attempt in range(5):
                try:
                    with open(self.csv_filepath, mode="w", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for r in records:
                            writer.writerow(r.model_dump())
                    break
                except (PermissionError, OSError):
                    time.sleep(0.1)
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError:
                    pass

    def get_all(self) -> List[CustomerRecord]:
        with self._lock:
            return self._read_records()

    def get_by_land_number(self, land_number: str) -> Optional[CustomerRecord]:
        with self._lock:
            records = self._read_records()
            clean_num = land_number.strip()
            for r in records:
                if r.land_number == clean_num:
                    return r
            return None

    def get_suspended(self) -> List[CustomerRecord]:
        with self._lock:
            records = self._read_records()
            return [r for r in records if r.is_suspended()]

    def update_customer(self, land_number: str, update_data: CustomerUpdate) -> Optional[CustomerRecord]:
        with self._lock:
            records = self._read_records()
            clean_num = land_number.strip()
            updated_record = None
            new_records = []

            for r in records:
                if r.land_number == clean_num:
                    dump = r.model_dump()
                    if update_data.status is not None:
                        dump["status"] = update_data.status.strip()
                    if update_data.remark is not None:
                        dump["remark"] = update_data.remark.strip()
                    if update_data.email is not None:
                        dump["email"] = update_data.email.strip()
                    if update_data.whatsapp_number is not None:
                        dump["whatsapp_number"] = update_data.whatsapp_number.strip()
                    updated_record = CustomerRecord(**dump)
                    new_records.append(updated_record)
                else:
                    new_records.append(r)

            if updated_record:
                self._write_records(new_records)
            return updated_record

    def save_all(self, records: List[CustomerRecord]) -> None:
        """Atomically persist a whole new set of customer records."""
        with self._lock:
            self._write_records(records)

    def clear(self) -> None:
        """Clear all customer records and remove CSV file if present."""
        with self._lock:
            if os.path.exists(self.csv_filepath):
                try:
                    os.remove(self.csv_filepath)
                except OSError:
                    self._write_records([])

