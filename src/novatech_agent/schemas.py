from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    """Structured intent classification model using Pydantic."""
    intent: Literal["faq", "pricing", "order_booking", "general"] = Field(
        description="faq = policy, warranty, delivery, hours questions; "
                    "pricing = checking cost, stock, or turnaround of a product/service; "
                    "order_booking = wants to book a repair appointment or place an order; "
                    "general = greetings, chitchat, or ambiguous queries."
    )
    confidence: float = Field(default=1.0, description="Confidence score from 0.0 to 1.0")
    detected_entity: Optional[str] = Field(default=None, description="Product or service name detected in message")

class RepairBooking(BaseModel):
    """Validated schema for a repair service booking."""
    customer_name: str = Field(..., min_length=2, description="Full name of customer")
    service_name: str = Field(..., description="The repair service (e.g. 'laptop screen replacement', 'smartphone battery replacement')")
    appointment_day: str = Field(..., description="Day or date for the appointment (e.g. 'Friday', 'Tomorrow 3pm')")
    contact_info: Optional[str] = Field(default="In-store Walk-in", description="Customer phone number or email")
    express_rush: bool = Field(default=False, description="Whether customer requested express rush turnaround (+₹500)")

class ProductPurchase(BaseModel):
    """Validated schema for a product order."""
    customer_name: str = Field(..., min_length=2, description="Full name of customer")
    product_name: str = Field(..., description="The catalog item being purchased")
    quantity: int = Field(default=1, ge=1, le=10, description="Quantity to purchase (1-10 units)")
    delivery_required: bool = Field(default=False, description="True for courier delivery (+₹100), False for in-store pickup")
