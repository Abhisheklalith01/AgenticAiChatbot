# Agentic AI Chatbot — Complete Curriculum & Enterprise Implementation

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.2%2B-green.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![ChromaDB](https://img.shields.io/badge/RAG-ChromaDB-purple.svg)](https://www.trychroma.com/)
[![Pydantic](https://img.shields.io/badge/Validation-Pydantic%20v2-red.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Evaluations-100%25%20Passing-brightgreen.svg)](tests/run_evals.py)

This repository contains the complete interactive coursework, starter notebooks, and production-grade enterprise implementations for the **Agentic AI Chatbot Workshop (Days 1 to 6)**.

It features two parallel tracks:
1. **Curriculum Track**: The Sweet Crumbs Home Bakery tutorial series spanning foundational LLM prompts to multi-agent StateGraphs.
2. **Custom Enterprise Track**: **NovaTech Gadgets & Repair Studio** — a full custom business agent system with Pydantic validation, Vector RAG knowledge base, multi-turn thread memory checkpointers, automated evaluations, and multi-agent routing.

---

## 📁 Repository Structure

```
AgenticAiChatbot/
├── README.md                          # Repository overview & quickstart guide
├── TASKS.md                           # Detailed workshop tasks, solutions & checklist
├── TEACHER_EXPLANATION.md             # In-depth viva / presentation guide for teacher
├── requirements.txt                   # Project Python dependencies
│
├── day1.html                          # Interactive tutorial: LLM mechanics & API calls
├── day2.html                          # Interactive tutorial: Prompts, memory & Python essentials
├── day3.html                          # Interactive tutorial: LangChain agents & ReAct loop
├── day4.html                          # Interactive tutorial: Tools, Pydantic & Google Sheets
├── day5.html                          # Interactive tutorial: Thread memory & ChromaDB RAG
│
├── agenticAI_Day1_6.ipynb             # Full 6-Day workshop Google Colab notebook
├── NovaTech_Agent_Walkthrough.ipynb   # Dedicated custom business showcase notebook
│
├── data/
│   ├── inventory.json                 # Hardware products & repair service catalog
│   ├── faqs.json                      # Policy knowledge base (warranty, returns, fees)
│   ├── tests.csv                      # Benchmark evaluation dataset (10 scenarios)
│   └── orders_log.json                # Live transaction audit log
│
├── src/
│   └── novatech_agent/
│       ├── __init__.py                # Package initialization
│       ├── config.py                  # Catalog loader & store hours
│       ├── schemas.py                 # Pydantic models (Intent, RepairBooking, Purchase)
│       ├── tools.py                   # Custom tools (pricing, stock, hours, booking, RAG)
│       ├── rag.py                     # ChromaDB / TF-IDF vector knowledge base
│       ├── memory.py                  # Thread-based memory checkpointer
│       ├── logger.py                  # JSON & CSV transaction logger
│       ├── agent.py                   # Core unified ReAct agent engine
│       └── workflow.py                # LangGraph StateGraph router & specialist nodes
│
└── tests/
    ├── test_agent.py                  # Unit tests (tools, Pydantic, memory, workflow)
    └── run_evals.py                   # Automated benchmark evaluation runner (100% accuracy)
```

---

## 🌟 Custom Business Showcase: NovaTech Gadgets & Repair Studio

Rather than only running the bakery tutorial, we engineered a custom domain agent for **NovaTech Gadgets & Repair Studio**:

- **Hardware Catalog**: Mechanical keyboards, 26K DPI gaming mice, ANC headphones, NVMe SSDs, 144Hz monitors.
- **Repair Services**: Laptop screen replacement, thermal paste & deep cleaning, battery replacements, data recovery.
- **Strict Pydantic Validation**: `RepairBooking` guarantees customer name, appointment day, contact details, and priority express flags before any transaction is logged.
- **Vector RAG Knowledge Base**: Uses ChromaDB / vector embeddings to index return windows, diagnostic fee waiver rules, 90-day repair warranties, and student discounts.
- **Thread Memory**: Each customer conversation maintains its own context thread via LangGraph's checkpointer (`InMemorySaver`), isolating sessions and remembering multi-turn context.
- **StateGraph Multi-Agent Architecture**: Routes between a **Support/FAQ Specialist** and a **Booking/Order Specialist** based on classified user intent.

---

## 🚀 Quickstart Guide

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Abhisheklalith01/AgenticAiChatbot.git
cd AgenticAiChatbot
pip install -r requirements.txt
```

### 2. Run Automated Unit Tests
```bash
python tests/test_agent.py
```
*Output: 7/7 unit tests passing.*

### 3. Run Benchmark Evaluation Suite
```bash
python tests/run_evals.py
```
*Output: 10/10 test scenarios passing (100.0% accuracy).*

### 4. Interactive Python Usage
```python
import sys
sys.path.insert(0, "src")
from novatech_agent.agent import agent

# 1. Ask store hours
print(agent.respond("What time do you close on Sunday?"))

# 2. Check repair pricing
print(agent.respond("How much is thermal repaste?"))

# 3. Query store policies via RAG
print(agent.respond("What is your warranty policy on laptop repairs?"))

# 4. Book an appointment with validation & logging
print(agent.respond("I want to book an appointment for smartphone battery replacement for customer Aarav on Friday"))
```

---

## 📖 Interactive HTML Tutorials

Open any of the tutorial files in your web browser for interactive simulations, sliders, and quizzes:
- **`day1.html`**: Token prediction, temperature exploration, context windows.
- **`day2.html`**: System prompts, few-shot prompting, conversation history loops.
- **`day3.html`**: LangChain ReAct loops, prompt templates, and evaluation loops.
- **`day4.html`**: Function calling, `@tool`, Pydantic typing, structured outputs.
- **`day5.html`**: Conversation memory checkpointers (`thread_id`), vector embeddings, and RAG.

---

## 🎓 Preparing for Teacher / Viva Questions

Check out **[`TEACHER_EXPLANATION.md`](TEACHER_EXPLANATION.md)** for a 60-second elevator pitch, architecture diagrams, step-by-step concept explanations, and answers to likely viva questions.
