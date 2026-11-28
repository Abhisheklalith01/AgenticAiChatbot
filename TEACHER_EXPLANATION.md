# Teacher Presentation Guide: Agentic AI Chatbot System

Use this document to prepare for explaining your project to your teacher or instructor. It covers the core theoretical concepts, software architecture, technical decisions, and common viva/exam questions.

---

## 1. Quick 60-Second Elevator Pitch

> *"In this project, I progressed from basic LLM prompt engineering to building a production-ready, multi-agent AI system called **NovaTech Gadgets & Repair Hub**. Unlike a simple chatbot that merely answers text questions, an **agentic AI** can reason, choose actions dynamically, use tools (like database lookups and booking appointments), validate structured inputs with Pydantic schemas, maintain persistent conversation memory per customer using LangGraph checkpointers, and look up store policies using Vector RAG (ChromaDB). I also implemented an automated evaluation harness testing 10 benchmark scenarios with 100% accuracy."*

---

## 2. Fundamental Difference: Chatbot vs. Agentic AI

| Feature | Standard LLM / Chatbot | Agentic AI System (Our Implementation) |
| :--- | :--- | :--- |
| **Action Capability** | Read/write text only. Cannot take external actions. | Can invoke real tools (calculators, databases, APIs, appointment books). |
| **Decision Flow** | Linear: Input $\rightarrow$ LLM $\rightarrow$ Output. | Autonomous ReAct Loop: Reason $\rightarrow$ Act $\rightarrow$ Observe $\rightarrow$ Finish. |
| **Output Integrity** | Can hallucinate prices, dates, or non-existent policies. | Bound to deterministic database lookups and Pydantic schemas. |
| **Memory** | Stateless or naive string concatenation. | Thread-isolated checkpointers (`InMemorySaver` / `thread_id`). |
| **Knowledge Base** | Limited to static training cutoff weights. | Dynamic Vector RAG (ChromaDB) retrieving real-time policy documents. |

---

## 3. Curriculum Breakdown: Day 1 to Day 6

### Day 1: LLM Foundations & API Invocations
- **Core Concept**: Understanding tokenization, temperature, system vs. user prompts, and basic API calls via Groq's high-speed inference engine (`ChatGroq`).
- **Code**: Initialized models with low temperature (0.1–0.2) to ensure deterministic, factual answers.

### Day 2: Structured Prompts, Role Definitions & Guardrails
- **Core Concept**: System prompts defining the persona, business facts, and negative constraints ("Never guess numbers; use tools").
- **Code**: Created the persona for NovaTech (`ROLE: You are the smart customer service technician for NovaTech...`).

### Day 3: LangChain & The Agent Execution Loop (ReAct)
- **Core Concept**: Introduction to LangChain prompt templates, message roles (`HumanMessage`, `AIMessage`, `SystemMessage`), and the ReAct reasoning pattern.
- **Code**: Automated evaluation harness comparing model responses against benchmark expectations in `tests.csv`.

### Day 4: Tools, Structured Output & Pydantic Validation
- **Core Concept**: Tool calling (Function calling). Instead of outputting free text, the model emits a structured JSON payload calling a specific Python function.
- **Code**:
  - `get_price_and_stock`: Queries real inventory prices.
  - `get_store_hours`: Looks up operating hours for any day.
  - `book_repair_order`: Validates input types with Pydantic (`RepairBooking`) and logs the booking to persistent JSON/CSV logs.

### Day 5: Memory Checkpointing & Vector RAG (ChromaDB)
- **Core Concept**:
  1. **Thread Memory**: Each customer has a distinct `thread_id`. LangGraph's checkpointer (`InMemorySaver`) tracks conversation state across multiple turns without mixing up users.
  2. **Vector RAG**: Chunks policy documents (warranty terms, return window, diagnostic fees), embeds them, and searches them using cosine vector similarity (`search_store_policies`).

### Day 6: StateGraph Multi-Agent Architecture
- **Core Concept**: Multi-agent routing. A router inspects incoming intent (`IntentClassification`) and directs the workflow between specialist agents:
  - **Support / FAQ Specialist**: Handles hours, pricing, and policy lookups.
  - **Booking / Order Specialist**: Handles appointment scheduling and order validation.

---

## 4. Architecture Diagram

```
                 +-----------------------+
                 | Customer User Message |
                 +-----------+-----------+
                             |
                             v
               +---------------------------+
               | StateGraph Intent Router  |
               +-------------+-------------+
                             |
             +---------------+---------------+
             |                               |
             v                               v
   [Support / FAQ Agent]           [Order & Booking Agent]
             |                               |
    +--------+--------+                      |
    |                 |                      v
    v                 v            +-------------------+
(Store Hours)  (Vector RAG)        | Pydantic Schema   |
    |          (ChromaDB)          | (RepairBooking)   |
    |                 |            +---------+---------+
    +--------+--------+                      |
             |                               v
             v                     +-------------------+
+------------------------+         | Transaction Log   |
| Thread Memory Manager  |         | (JSON & CSV Audit)|
| (LangGraph Checkpoint) |         +---------+---------+
+-----------+------------+                   |
            |                                |
            +----------------+---------------+
                             |
                             v
                 +-----------------------+
                 | Final Verified Answer |
                 +-----------------------+
```

---

## 5. Our Custom Business Showcase: NovaTech Electronics & Repair Hub

Instead of only following the tutorial bakery example, we built an enterprise electronics & repair studio agent with:

1. **Hardware Catalog**: Gaming mice, mechanical keyboards, ANC headphones, NVMe SSDs, monitors.
2. **Repair Services**: Laptop screen replacement, thermal paste & dust cleaning, battery swaps, data recovery.
3. **Store Policies & RAG**:
   - 90-day parts & labor guarantee on repairs; 1-year replacement on new components.
   - ₹300 diagnostic fee, 100% waived if repair is approved.
   - 10% student discount on repair labor with college ID.
   - Express 4-hour rush repair service (+₹500).
   - Ultrasonic cleaning protocol for liquid damage.
4. **Structured Logging**: Every booking generates a unique transaction code (`NT-XXXXXX`) and appends to `data/orders_log.json` and `data/orders_log.csv`.

---

## 6. Likely Teacher Questions & Best Answers

### Q1: "Why use Pydantic schemas instead of just plain dictionary checks?"
> **Answer**: *"Pydantic enforces strict runtime type validation, handles default values, coerces types safely, and produces clear, readable errors if fields are missing. When LLMs generate JSON function arguments, Pydantic guarantees that the parameters match our expected schema before any transaction or database write is performed."*

### Q2: "How does RAG prevent hallucinations in this project?"
> **Answer**: *"Without RAG, an LLM might make up a 2-year warranty or claim that diagnostic tests are free. With RAG, the agent calls the `search_store_policies` tool, which retrieves the exact policy chunk from the vector store. The system prompt instructs the agent to answer strictly from the retrieved text, eliminating hallucinations."*

### Q3: "What is the role of `thread_id` in LangGraph memory?"
> **Answer**: *"LLMs are inherently stateless; each HTTP request knows nothing about prior turns. The `thread_id` acts as a session key. LangGraph's checkpointer retrieves previous messages for that specific thread and passes them in context, allowing the agent to remember what the customer asked earlier in the conversation while keeping different users completely isolated."*

### Q4: "How did you test and evaluate your agent?"
> **Answer**: *"I implemented an automated test harness in `tests/run_evals.py` based on a test dataset (`data/tests.csv`). It sends 10 diverse user messages, verifies that the model accurately routes the intent, invokes the correct tool, and includes the expected factual keyword in the response. All 10 test cases passed with 100% accuracy."*
