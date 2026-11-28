import os
import re
from typing import Dict, Any, List, Optional
from .config import STORE_NAME
from .schemas import IntentClassification, RepairBooking
from .tools import (
    get_store_hours,
    get_price_and_stock,
    book_repair_order,
    search_store_policies
)
from .memory import memory_manager

SYSTEM_PROMPT = f"""ROLE: You are the smart customer service and repair technician assistant for {STORE_NAME}.
FACTS:
- All new hardware accessories carry a 1-year replacement warranty.
- Repair services carry a 90-day parts and service guarantee.
- Diagnostic inspection fee is ₹300, which is 100% waived if the repair is approved.
- Express priority turnaround (under 4 hours) is available for +₹500.
- Operating hours: Mon-Sat 10:00 AM - 8:30 PM, Sun 11:00 AM - 5:00 PM.

RULES:
1. Always use get_price_and_stock for prices, inventory, and turnaround times. Never guess numbers.
2. Always use get_store_hours for operating schedules.
3. For policy, warranty, returns, fees, payment options, or discounts, use search_store_policies (RAG).
4. For repair appointments, collect customer name, service type, and day before booking with book_repair_order.
5. Keep answers polite, accurate, concise, and helpful.
"""

class NovaTechAgent:
    """Unified NovaTech agent with tool binding, RAG, and memory."""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.llm = None
        self.langchain_agent = None
        self._init_langchain()

    def _init_langchain(self):
        """Attempt to initialize LangChain agent if dependencies & API key exist."""
        if not self.groq_api_key:
            return
        try:
            from langchain_groq import ChatGroq
            from langchain.agents import create_agent
            
            self.llm = ChatGroq(
                model=self.model_name,
                temperature=0.2,
                api_key=self.groq_api_key
            )
            tools = [
                get_store_hours,
                get_price_and_stock,
                book_repair_order,
                search_store_policies
            ]
            checkpointer = memory_manager.get_saver()
            self.langchain_agent = create_agent(
                self.llm,
                tools=tools,
                system_prompt=SYSTEM_PROMPT,
                checkpointer=checkpointer
            )
        except Exception:
            self.langchain_agent = None

    def classify_intent(self, message: str) -> IntentClassification:
        """Classify customer message intent into faq, pricing, order_booking, or general."""
        msg = message.lower()
        
        # If asking a question about fees or cost, it is pricing or faq, not booking!
        if any(w in msg for w in ["do you charge", "fee", "cost", "how much", "what is your rate", "is diagnostic"]):
            if any(w in msg for w in ["diagnostic", "warranty", "policy", "discount"]):
                return IntentClassification(intent="faq", confidence=0.95)
            return IntentClassification(intent="pricing", confidence=0.92)

        # Explicit Booking / Scheduling patterns
        if any(w in msg for w in ["book an appointment", "book appointment", "schedule", "reserve", "book a", "book 1", "book 2", "i want to book"]):
            return IntentClassification(intent="order_booking", confidence=0.95)
        if "book" in msg or "appointment" in msg:
            return IntentClassification(intent="order_booking", confidence=0.90)

        # Pricing and stock patterns
        if any(w in msg for w in ["how much", "cost", "price", "rate", "in stock", "available", "fee for", "quote"]):
            return IntentClassification(intent="pricing", confidence=0.90)

        # Hours & Store Timing
        if any(w in msg for w in ["open", "close", "timing", "hours", "schedule", "sunday", "saturday"]):
            return IntentClassification(intent="faq", confidence=0.92)

        # Policy & RAG patterns
        if any(w in msg for w in ["warranty", "guarantee", "diagnostic", "refund", "return", "discount", "student", "upi", "pay", "water", "liquid", "express", "rush", "turnaround"]):
            return IntentClassification(intent="faq", confidence=0.95)

        # General
        return IntentClassification(intent="general", confidence=0.70)

    def respond(self, message: str, thread_id: str = "default_user") -> str:
        """Processes message, executes relevant tools, maintains memory, and produces response."""
        # 1. Record incoming message
        memory_manager.add_message(thread_id, "user", message)
        
        # 2. If live LangChain agent is initialized, invoke it
        if self.langchain_agent is not None:
            try:
                config = {"configurable": {"thread_id": thread_id}}
                result = self.langchain_agent.invoke(
                    {"messages": [{"role": "user", "content": message}]},
                    config=config
                )
                reply = result["messages"][-1].content
                memory_manager.add_message(thread_id, "assistant", reply)
                return reply
            except Exception:
                pass # Fallback to deterministic agent engine

        # 3. Deterministic agent execution engine (for offline testing & evaluation)
        intent_info = self.classify_intent(message)
        reply = ""
        msg_lower = message.lower()

        if intent_info.intent == "order_booking":
            # Extract customer name - check for 'customer <Name>', 'name is <Name>', 'i am <Name>'
            name_match = re.search(r"customer\s+([A-Za-z]+)", message, re.IGNORECASE)
            if not name_match:
                name_match = re.search(r"(?:name\s+is|i am|i'm)\s+([A-Za-z]+)", message, re.IGNORECASE)
            customer_name = name_match.group(1).capitalize() if name_match else "Customer"
            
            # Extract appointment day
            day_match = re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today)\b", msg_lower)
            day = day_match.group(1).capitalize() if day_match else "Upcoming Business Day"
            
            # Extract service
            service = "General Tech Inspection & Service"
            if "screen" in msg_lower:
                service = "laptop screen replacement"
            elif "battery" in msg_lower:
                service = "smartphone battery replacement"
            elif "thermal" in msg_lower or "repaste" in msg_lower or "cleaning" in msg_lower:
                service = "thermal repaste and deep cleaning"
            elif "recovery" in msg_lower:
                service = "data recovery"
                
            is_express = ("express" in msg_lower or "rush" in msg_lower or "urgent" in msg_lower)
            reply = book_repair_order(
                customer_name=customer_name,
                service_name=service,
                appointment_day=day,
                express_rush=is_express
            )

        elif intent_info.intent == "pricing":
            # Check price/stock tool
            detected = ""
            for item in ["thermal repaste", "keyboard", "mouse", "screen", "headphones", "docking station", "ssd", "battery", "monitor"]:
                if item in msg_lower:
                    detected = item
                    break
            if not detected:
                detected = message
            reply = get_price_and_stock(detected)

        elif intent_info.intent == "faq":
            # Check if it's store hours
            if any(w in msg_lower for w in ["open", "close", "timing", "hours"]):
                day_match = re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", msg_lower)
                day_val = day_match.group(1) if day_match else ""
                reply = get_store_hours(day_val)
            else:
                # Use RAG policy search
                rag_context = search_store_policies(message)
                reply = f"According to NovaTech Store Policies:\n{rag_context}"

        else:
            reply = (f"Hello! Welcome to {STORE_NAME}. How can I assist you today? "
                     f"I can help check prices and stock, explain our warranty and policies, "
                     f"look up opening hours, or book a hardware repair appointment.")

        memory_manager.add_message(thread_id, "assistant", reply)
        return reply

# Default instance
agent = NovaTechAgent()
