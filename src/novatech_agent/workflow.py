"""
StateGraph Multi-Agent Workflow (Day 6 Architecture)
===================================================
Defines a state machine router and specialist agent nodes:
  START -> classify_intent -> {support_agent, booking_agent} -> END
"""

from typing import TypedDict, Literal
from .schemas import IntentClassification
from .agent import agent

class AgenticWorkflowState(TypedDict):
    """Shared state container for the LangGraph workflow."""
    customer_message: str
    thread_id: str
    intent: str
    response: str
    step_count: int

def router_node(state: AgenticWorkflowState) -> dict:
    """Classifies user intent and routes state to appropriate specialist."""
    intent_obj = agent.classify_intent(state["customer_message"])
    return {
        "intent": intent_obj.intent,
        "step_count": state.get("step_count", 0) + 1
    }

def support_faq_node(state: AgenticWorkflowState) -> dict:
    """Specialist node answering store hours, pricing, and RAG policy questions."""
    reply = agent.respond(state["customer_message"], thread_id=state.get("thread_id", "default_thread"))
    return {"response": reply}

def booking_order_node(state: AgenticWorkflowState) -> dict:
    """Specialist node taking repair appointments and logging bookings with validation."""
    reply = agent.respond(state["customer_message"], thread_id=state.get("thread_id", "default_thread"))
    return {"response": reply}

def route_next(state: AgenticWorkflowState) -> str:
    """Conditional edge router function."""
    if state["intent"] == "order_booking":
        return "booking_agent"
    return "support_agent"

# LangGraph builder initialization if installed
def build_langgraph_workflow():
    try:
        from langgraph.graph import StateGraph, START, END
        builder = StateGraph(AgenticWorkflowState)
        builder.add_node("router", router_node)
        builder.add_node("support_agent", support_faq_node)
        builder.add_node("booking_agent", booking_order_node)

        builder.add_edge(START, "router")
        builder.add_conditional_edges(
            "router",
            route_next,
            {
                "support_agent": "support_agent",
                "booking_agent": "booking_agent"
            }
        )
        builder.add_edge("support_agent", END)
        builder.add_edge("booking_agent", END)
        return builder.compile()
    except ImportError:
        return None

# Singleton graph instance
compiled_graph = build_langgraph_workflow()

def execute_workflow(message: str, thread_id: str = "default_user") -> dict:
    """Executes the complete multi-agent workflow for a given query."""
    initial_state: AgenticWorkflowState = {
        "customer_message": message,
        "thread_id": thread_id,
        "intent": "",
        "response": "",
        "step_count": 0
    }
    
    if compiled_graph is not None:
        try:
            return compiled_graph.invoke(initial_state)
        except Exception:
            pass

    # Deterministic workflow simulation
    router_res = router_node(initial_state)
    initial_state.update(router_res)
    if initial_state["intent"] == "order_booking":
        result = booking_order_node(initial_state)
    else:
        result = support_faq_node(initial_state)
    initial_state.update(result)
    return initial_state
