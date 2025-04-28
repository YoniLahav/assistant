# budget_manager.py

import json
import os
import difflib
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict

ALLOWED_CATEGORIES = [
    "food",
    "transport",
    "entertainment",
    "utilities",
    "rent",
    "salary",
    "investment",
    "health",
    "education",
    "shopping",
    "other",
]

class BudgetManager:
    def __init__(self, filename: str = "budget_data.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)

    def _load_data(self) -> List[Dict]:
        with open(self.filename, 'r') as f:
            return json.load(f)

    def _save_data(self, data: List[Dict]):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

    def _normalize_category(self, category: str) -> str:
        category = category.lower()
        matches = difflib.get_close_matches(category, ALLOWED_CATEGORIES, n=1, cutoff=0.7)
        if matches:
            return matches[0]
        raise ValueError(f"Invalid category '{category}'. Must be one of: {', '.join(ALLOWED_CATEGORIES)}")

    def add_record(self, record_type: str, date: str, amount: float, description: str, category: str):
        category = self._normalize_category(category)
        data = self._load_data()
        record = {
            "record_id": str(uuid.uuid4()),
            "type": record_type,
            "date": date,
            "amount": amount,
            "description": description,
            "category": category
        }
        data.append(record)
        self._save_data(data)

    def edit_record(self, record_id: str, record_type: str, date: str, amount: float, description: str, category: str):
        category = self._normalize_category(category)
        data = self._load_data()
        for record in data:
            if record.get("record_id") == record_id:
                record.update({
                    "type": record_type,
                    "date": date,
                    "amount": amount,
                    "description": description,
                    "category": category
                })
                self._save_data(data)
                return
        raise ValueError("Record ID not found.")

    def delete_record(self, record_id: str):
        data = self._load_data()
        new_data = [record for record in data if record.get("record_id") != record_id]
        if len(new_data) == len(data):
            raise ValueError("Record ID not found.")
        self._save_data(new_data)

    def query_records(self, record_type: Optional[str], from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        data = self._load_data()
        results = []
        for record in data:
            record_dt = datetime.fromisoformat(record["date"])
            if record_type is None or record["type"] == record_type:
                if from_date and to_date:
                    from_dt = datetime.fromisoformat(from_date)
                    to_dt = datetime.fromisoformat(to_date)
                    if from_dt <= record_dt <= to_dt:
                        results.append(record)
                else:
                    results.append(record)
        return results

    def find_records(self, record_type: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None,
                     amount: Optional[float] = None, description: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
        data = self._load_data()
        results = []
        for record in data:
            record_dt = datetime.fromisoformat(record["date"])
            if record_type and record["type"] != record_type:
                continue
            if from_date and to_date:
                from_dt = datetime.fromisoformat(from_date)
                to_dt = datetime.fromisoformat(to_date)
                if not (from_dt <= record_dt <= to_dt):
                    continue
            if amount and record["amount"] != amount:
                continue
            if description and description.lower() not in record["description"].lower():
                continue
            if category:
                try:
                    normalized_category = self._normalize_category(category)
                    if record["category"] != normalized_category:
                        continue
                except ValueError:
                    continue
            results.append(record)
        return results

    def get_total(self, record_type: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> float:
        records = self.query_records(record_type, from_date, to_date)
        return sum(record["amount"] for record in records)

    def get_balance(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> float:
        income = self.get_total("income", from_date, to_date)
        expense = self.get_total("expense", from_date, to_date)
        return income - expense

    def get_total_for_category(self, record_type: str, from_date: Optional[str], to_date: Optional[str], category: str) -> float:
        normalized_category = self._normalize_category(category)
        records = self.query_records(record_type, from_date, to_date)
        return sum(record["amount"] for record in records if record["category"] == normalized_category)

    def get_total_breakdown_by_category(self, record_type: str, from_date: Optional[str], to_date: Optional[str]) -> Dict[str, float]:
        records = self.query_records(record_type, from_date, to_date)
        category_totals = defaultdict(float)
        for record in records:
            category_totals[record["category"]] += record["amount"]
        return dict(category_totals)

    def get_allowed_categories(self) -> List[str]:
        return ALLOWED_CATEGORIES
