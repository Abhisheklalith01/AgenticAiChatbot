import json
import csv
from datetime import datetime
from pathlib import Path
from .config import ORDERS_LOG_PATH, DATA_DIR

ORDERS_CSV_PATH = DATA_DIR / "orders_log.csv"

def log_transaction(record: dict) -> dict:
    """Logs a booking or purchase record with timestamp and unique ID."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tx_id = f"NT-{int(datetime.now().timestamp() * 1000) % 1000000:06d}"
    
    entry = {
        "transaction_id": tx_id,
        "timestamp": timestamp,
        **record
    }
    
    # 1. Append to JSON log
    all_logs = []
    if ORDERS_LOG_PATH.exists():
        try:
            with open(ORDERS_LOG_PATH, "r", encoding="utf-8") as f:
                all_logs = json.load(f)
        except Exception:
            all_logs = []
            
    all_logs.append(entry)
    with open(ORDERS_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(all_logs, f, indent=2)
        
    # 2. Append to CSV (Google Sheets mirror format)
    file_exists = ORDERS_CSV_PATH.exists()
    keys = ["transaction_id", "timestamp", "type", "customer_name", "item_or_service", "total_price", "details"]
    with open(ORDERS_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)
        
    return entry
