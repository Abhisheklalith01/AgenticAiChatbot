import os
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

INVENTORY_PATH = DATA_DIR / "inventory.json"
FAQS_PATH = DATA_DIR / "faqs.json"
ORDERS_LOG_PATH = DATA_DIR / "orders_log.json"

def load_inventory():
    if INVENTORY_PATH.exists():
        with open(INVENTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "store_name": "NovaTech Gadgets & Repair Studio",
        "hours": {},
        "products": {},
        "repair_services": {}
    }

def load_faqs():
    if FAQS_PATH.exists():
        with open(FAQS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"policies": {}}

# Cache loaded data
INVENTORY_DATA = load_inventory()
FAQS_DATA = load_faqs()

STORE_NAME = INVENTORY_DATA.get("store_name", "NovaTech Gadgets & Repair Studio")
STORE_HOURS = INVENTORY_DATA.get("hours", {})
PRODUCTS = INVENTORY_DATA.get("products", {})
REPAIR_SERVICES = INVENTORY_DATA.get("repair_services", {})
POLICIES = FAQS_DATA.get("policies", {})
