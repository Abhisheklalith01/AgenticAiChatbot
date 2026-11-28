# AI Agents Workshop — Complete Tasks, Exercises & Solutions

This document compiles all practical tasks, build exercises, and prep assignments from **Day 1 to Day 6** of the **AI Agents Workshop**, along with the solutions and our custom business implementation (**NovaTech Gadgets & Repair Studio**).

---

## 📅 Summary of Workshop Days

| Day | Topic | Key Deliverable | Repository Implementation |
| :--- | :--- | :--- | :--- |
| **Day 1** | LLM Mechanics & First API Call | Low-temperature API call with system rules | `day1.html`, `agenticAI_Day1_6.ipynb` |
| **Day 2** | Prompts, Memory & Python Agent Core | Multi-turn chat loop with memory trimming & dicts | `day2.html`, `src/novatech_agent/config.py` |
| **Day 3** | Your First Agent & LangChain ReAct Loop | Agent ReAct loop & automated benchmark evaluation | `day3.html`, `tests/run_evals.py` |
| **Day 4** | Tools, Structured Output & Google Sheets | Tool binding with Pydantic validation & audit logging | `day4.html`, `src/novatech_agent/tools.py` |
| **Day 5** | Memory Checkpoints & ChromaDB RAG | Thread memory (`InMemorySaver`) & vector search | `day5.html`, `src/novatech_agent/rag.py` |
| **Day 6** | StateGraph Multi-Agent Architecture | Intent router & specialist agent orchestration | `agenticAI_Day1_6.ipynb`, `src/novatech_agent/workflow.py` |

---

## 📅 Day 1 Tasks: How LLMs Work & Your First API Call

### 🎯 Day 1 Build: First Structured API Call
Implement an API call with Groq / OpenAI-compatible API to answer a customer question using facts and rules:

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM = """ROLE:   You are the assistant for Sweet Crumbs Home Bakery.
FACTS:  We bake to order. Orders need 24 hours' notice. All cakes have eggless versions.
        Plum cake Rs 500. Chocolate cake Rs 650. Cupcake Rs 80.
RULES:  Never promise a delivery time. If the answer isn't in FACTS, say "I'll check with the owner."
FORMAT: Under 50 words, friendly, English or Telugu matching the customer."""

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    temperature=0.2,  # Low temperature for factual precision
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "Can I get an eggless cake today evening?"}
    ],
)
print("Bot reply:", response.choices[0].message.content)
```

---

## 📅 Day 2 Tasks: Prompts, Memory & Python Agents Need

### 🎯 Day 2 Build: Memory Loop & Catalogue Lookup
Implement conversation memory with trimming and dictionary lookups:

```python
history = [{"role": "system", "content": SYSTEM}]

def ask(question: str) -> str:
    history.append({"role": "user", "content": question})
    # Keep system prompt + last 6 turns
    trimmed = [history[0]] + history[-6:]
    res = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0.2,
        messages=trimmed
    )
    reply = res.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply
```

---

## 📅 Day 3 Tasks: LangChain Agents & Automated Evaluations

### 🎯 Day 3 Build: Automated Evaluation Harness
Create a benchmark evaluation runner that measures bot accuracy against a test CSV:

```python
import csv

tests = [
    ("What time do you close on Sunday?", "5:00 PM"),
    ("How much is thermal repaste?", "1,200"),
    ("What is your warranty policy on laptop repairs?", "90-day")
]

passed = 0
for question, expected in tests:
    answer = ask(question)
    if expected.lower() in answer.lower():
        passed += 1
print(f"Pass rate: {passed}/{len(tests)} ({passed/len(tests)*100:.1f}%)")
```
*NovaTech Implementation: See `tests/run_evals.py` (10/10 tests passing).*

---

## 📅 Day 4 Tasks: Tools, Pydantic & Audit Logging

### 🎯 Day 4 Build: Validated Function Calling
Bind deterministic Python functions decorated with `@tool` and validated with Pydantic:

```python
from pydantic import BaseModel, Field
from langchain.tools import tool

class RepairBooking(BaseModel):
    customer_name: str = Field(..., min_length=2)
    service_name: str = Field(...)
    appointment_day: str = Field(...)
    express_rush: bool = Field(default=False)

@tool
def book_repair_order(customer_name: str, service_name: str, appointment_day: str, express_rush: bool = False) -> str:
    """Book a repair service appointment in the system."""
    booking = RepairBooking(
        customer_name=customer_name,
        service_name=service_name,
        appointment_day=appointment_day,
        express_rush=express_rush
    )
    # Save to database or CSV/Google Sheets
    return f"Booking Confirmed for {booking.customer_name} on {booking.appointment_day}."
```
*NovaTech Implementation: See `src/novatech_agent/tools.py` and `src/novatech_agent/schemas.py`.*

---

## 📅 Day 5 Tasks: Thread Checkpointers & Vector RAG

### 🎯 Day 5 Build: Vector Knowledge Base & Thread Memory
Store knowledge chunks into ChromaDB and query them dynamically during execution:

```python
import chromadb
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

# 1. Vector RAG
client = chromadb.Client()
collection = client.get_or_create_collection("policies")
collection.add(
    documents=[
        "All hardware repairs carry a 90-day parts and labor guarantee.",
        "Diagnostic fee is Rs 300, 100% waived if repair is approved."
    ],
    ids=["warranty", "diagnostic_fee"]
)

# 2. Thread Checkpointer
checkpointer = InMemorySaver()
# Invocation passes thread_id in config
config = {"configurable": {"thread_id": "customer_42"}}
```
*NovaTech Implementation: See `src/novatech_agent/rag.py` and `src/novatech_agent/memory.py`.*

---

## 📅 Day 6 Tasks: StateGraph Multi-Agent Architecture

### 🎯 Day 6 Build: State Machine Router & Specialist Agents
Create a LangGraph StateGraph that routes customer queries:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("classify", classify_node)
builder.add_node("support_agent", support_node)
builder.add_node("booking_agent", booking_node)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_intent, {
    "support": "support_agent",
    "order": "booking_agent"
})
builder.add_edge("support_agent", END)
builder.add_edge("booking_agent", END)
graph = builder.compile()
```
*NovaTech Implementation: See `src/novatech_agent/workflow.py`.*

---

## 🎯 Verification Checklist

- [x] Day 1 interactive tutorial (`day1.html`)
- [x] Day 2 interactive tutorial (`day2.html`)
- [x] Day 3 interactive tutorial (`day3.html`)
- [x] Day 4 interactive tutorial (`day4.html`)
- [x] Day 5 interactive tutorial (`day5.html`)
- [x] Full workshop Colab notebook (`agenticAI_Day1_6.ipynb`)
- [x] Custom business implementation (`src/novatech_agent/`)
- [x] Custom business showcase notebook (`NovaTech_Agent_Walkthrough.ipynb`)
- [x] Pydantic validation schemas (`schemas.py`)
- [x] Custom tools with persistent audit logging (`tools.py`, `logger.py`)
- [x] ChromaDB / cosine vector RAG store (`rag.py`)
- [x] Thread-isolated conversation memory (`memory.py`)
- [x] StateGraph multi-agent workflow (`workflow.py`)
- [x] Unit test suite (`tests/test_agent.py` - 7/7 passing)
- [x] Evaluation test harness (`tests/run_evals.py` - 10/10 passing)
- [x] Comprehensive teacher presentation guide (`TEACHER_EXPLANATION.md`)
