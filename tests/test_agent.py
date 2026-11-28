import unittest
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from novatech_agent.agent import agent
from novatech_agent.tools import get_store_hours, get_price_and_stock, book_repair_order, search_store_policies
from novatech_agent.memory import memory_manager
from novatech_agent.schemas import RepairBooking, ProductPurchase
from novatech_agent.workflow import execute_workflow

class TestNovaTechAgent(unittest.TestCase):
    
    def test_store_hours_lookup(self):
        sunday_hours = get_store_hours("Sunday")
        self.assertIn("11:00 AM to 5:00 PM", sunday_hours)
        all_hours = get_store_hours("")
        self.assertIn("Monday:", all_hours)

    def test_pricing_and_stock(self):
        mouse_info = get_price_and_stock("wireless gaming mouse", quantity=2)
        self.assertIn("Wireless Gaming Mouse", mouse_info)
        self.assertIn("₹5,600", mouse_info)
        
        repaste_info = get_price_and_stock("thermal repaste")
        self.assertIn("₹1,200", repaste_info)

    def test_pydantic_booking_validation(self):
        booking = RepairBooking(
            customer_name="Vikram Singh",
            service_name="laptop screen replacement",
            appointment_day="Monday",
            contact_info="vikram@example.com",
            express_rush=True
        )
        self.assertEqual(booking.customer_name, "Vikram Singh")
        self.assertTrue(booking.express_rush)

    def test_repair_booking_tool(self):
        res = book_repair_order(
            customer_name="Rohan Verma",
            service_name="smartphone battery replacement",
            appointment_day="Saturday",
            express_rush=False
        )
        self.assertIn("Booking Confirmed", res)
        self.assertIn("Rohan Verma", res)
        self.assertIn("Smartphone Battery Replacement", res)

    def test_rag_policy_search(self):
        warranty_res = search_store_policies("What is warranty on repair services?")
        self.assertIn("90-day", warranty_res)
        
        fee_res = search_store_policies("What is your diagnostic inspection fee?")
        self.assertIn("300", fee_res)

    def test_conversation_memory(self):
        thread = "user_test_thread_99"
        memory_manager.clear_thread(thread)
        agent.respond("Hi there, are you open today?", thread_id=thread)
        agent.respond("How much is thermal repaste?", thread_id=thread)
        history = memory_manager.get_history(thread)
        self.assertEqual(len(history), 4) # 2 user + 2 assistant messages

    def test_workflow_state_graph(self):
        result = execute_workflow("Can I book a screen repair for customer Pooja on Wednesday?", thread_id="wf_test")
        self.assertEqual(result["intent"], "order_booking")
        self.assertIn("Pooja", result["response"])

if __name__ == "__main__":
    unittest.main()
