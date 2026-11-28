import json
from typing import Dict, Any, Optional
from .config import STORE_HOURS, PRODUCTS, REPAIR_SERVICES, STORE_NAME
from .schemas import RepairBooking, ProductPurchase
from .logger import log_transaction
from .rag import search_policies

# Check if langchain.tools is available
try:
    from langchain.tools import tool as lc_tool
except ImportError:
    # Minimal decorator shim for standalone execution
    def lc_tool(func):
        func.is_tool = True
        return func

@lc_tool
def get_store_hours(day: str = "") -> str:
    """Look up operating hours for NovaTech Gadgets & Repair Studio for any day of the week.
    
    Args:
        day: Day of week (e.g. 'Monday', 'Sunday', or empty for full schedule).
    """
    day_clean = day.strip().lower()
    if day_clean in STORE_HOURS:
        return f"{STORE_NAME} hours for {day_clean.capitalize()}: {STORE_HOURS[day_clean]}."
    
    lines = [f"{d.capitalize()}: {h}" for d, h in STORE_HOURS.items()]
    return f"Store Operating Hours:\n" + "\n".join(lines)

@lc_tool
def get_price_and_stock(item_name: str, quantity: int = 1) -> str:
    """Check unit price, available stock, or repair turnaround time for any product or repair service.
    
    Args:
        item_name: Name of the product or repair service.
        quantity: Quantity requested (default 1).
    """
    query = item_name.strip().lower()
    
    # 1. Check products
    for name, p in PRODUCTS.items():
        if query in name or name in query:
            total = p["price"] * quantity
            return (f"Product: {name.title()} | Unit Price: ₹{p['price']:,} | "
                    f"Quantity: {quantity} | Total: ₹{total:,} | In Stock: {p['stock']} units.")
            
    # 2. Check repair services
    for name, s in REPAIR_SERVICES.items():
        if query in name or name in query:
            total = s["price"] * quantity
            return (f"Repair Service: {name.title()} | Base Cost: ₹{s['price']:,} | "
                    f"Typical Turnaround: {s['turnaround']} | Notes: {s['notes']}.")
            
    return (f"'{item_name}' was not found in our catalog. "
            f"Available products: {', '.join(PRODUCTS.keys())}. "
            f"Available repair services: {', '.join(REPAIR_SERVICES.keys())}.")

@lc_tool
def book_repair_order(
    customer_name: str,
    service_name: str,
    appointment_day: str,
    contact_info: str = "In-store Walk-in",
    express_rush: bool = False
) -> str:
    """Book and confirm a repair appointment or service order in the system with validation.
    
    Args:
        customer_name: Full name of the customer.
        service_name: Name of the repair service needed.
        appointment_day: Day or date for drop-off / appointment.
        contact_info: Customer contact number or email.
        express_rush: Set to True if express 4-hour rush service (+₹500) is requested.
    """
    # Validate via Pydantic model
    booking = RepairBooking(
        customer_name=customer_name,
        service_name=service_name,
        appointment_day=appointment_day,
        contact_info=contact_info,
        express_rush=express_rush
    )
    
    # Price calculation
    base_price = 0
    clean_service = booking.service_name.lower()
    for name, s in REPAIR_SERVICES.items():
        if clean_service in name or name in clean_service:
            base_price = s["price"]
            clean_service = name
            break
            
    total = base_price + (500 if booking.express_rush else 0)
    
    # Log transaction
    record = log_transaction({
        "type": "repair_booking",
        "customer_name": booking.customer_name,
        "item_or_service": clean_service.title(),
        "appointment_day": booking.appointment_day,
        "contact_info": booking.contact_info,
        "express_rush": booking.express_rush,
        "total_price": f"₹{total:,}" if base_price > 0 else "Pending Inspection",
        "details": f"Appointment booked for {booking.appointment_day}. Express: {booking.express_rush}"
    })
    
    return (f"Booking Confirmed! Appointment ID: {record['transaction_id']}. "
            f"Customer: {booking.customer_name} | Service: {clean_service.title()} | "
            f"Scheduled: {booking.appointment_day} | Estimated Total: {record['total_price']} | "
            f"Status: Logged successfully in repair queue.")

@lc_tool
def search_store_policies(question: str) -> str:
    """Search NovaTech policies, warranty terms, diagnostic fee rules, returns, and payment options using RAG.
    
    Args:
        question: Customer question regarding store rules, warranty, discounts, fees, or turnaround.
    """
    return search_policies(question)
