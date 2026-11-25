# AI Agents Workshop — Tasks & Practice Exercises

This document compiles all practical tasks, build exercises, and prep assignments from **Day 1** and **Day 2** of the **AI Agents Workshop (Level 1 Fundamentals)**.

---

## 📅 Day 1 Tasks: How LLMs Work & Your First API Call

### 🎯 Day 1 Build: Sweet Crumbs' First Answer
Implement your first API call with Groq / OpenAI-compatible API to answer a customer question using facts and rules:

```python
import os
from openai import OpenAI

# Step 0: Set up client (e.g. using Groq API)
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
    temperature=0.2,  # Facts and prices: keep it low/focused
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "Can I get an eggless cake today evening?"}
    ],
)

print("Bot reply:", response.choices[0].message.content)
print("Token usage:", response.usage)
```

**Expected Behavior:**
The bot should state that eggless cakes are available, but orders require 24 hours' notice, so this evening is not possible.

---

### 🧪 Day 1 "Your 10%" Hands-on Tasks
1. **Temperature Experiment**:
   - Ask `"Write a tagline for Sweet Crumbs"` 3 times at `temperature=0.2`.
   - Ask 3 times at `temperature=1.2`.
   - Compare consistency vs creativity.
2. **Hallucination Test**:
   - Delete the `FACTS` line from the system prompt.
   - Ask: `"Do you deliver to Kakinada?"`. Observe how it invents a plausible but fictitious policy.
   - Restore `FACTS` with explicit rules and re-test.
3. **Stateless / No-Memory Test**:
   - Make two separate API calls:
     1. `"My name is Ravi"`
     2. `"What is my name?"`
   - Notice the bot doesn't know your name in call 2.
   - Combine both into one `messages` conversation history list and re-run.
4. **Token Cost Comparison**:
   - Send the same message in English and in Telugu.
   - Compare `response.usage.prompt_tokens` to observe tokenizer differences across scripts.
5. **Custom Business Prompt**:
   - Rewrite the `SYSTEM` prompt for your own business or idea (5 facts, 3 rules).
   - Test it against 3 real customer questions.

### 📝 Preparation for Day 2
- [ ] Write down the **10 most common customer questions** for your business or project.

---

## 📅 Day 2 Tasks: Prompts, Memory & Essential Python for Agents

### 🎯 Day 2 Build: Sweet Crumbs Chatbot That Remembers
Complete Colab cell featuring menu dict, system prompt, `@log_call` decorator, typed pricing function, chat loop with trimming, and robust error handling:

```python
import json, functools
from openai import OpenAI, RateLimitError, APIConnectionError

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"
MENU = {"plum cake": 500, "chocolate cake": 650, "cupcake": 80}

SYSTEM = f"""ROLE:   You are the friendly assistant for Sweet Crumbs Home Bakery.
FACTS:  Menu with prices in rupees: {json.dumps(MENU)}
        Orders need 24 hours' notice. All cakes have eggless versions.
RULES:  Never promise a delivery time. If it isn't in FACTS, say "I'll check with the owner."
        Remember the customer's name and order during the chat.
FORMAT: Under 50 words, friendly, English or Telugu matching the customer."""

def log_call(func):
    """Decorator to log function inputs and results without altering code."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"   [log] {func.__name__}{args} -> {result!r}")
        return result
    return wrapper

@log_call
def get_price(item: str, qty: int = 1) -> int:
    """Return the total price in rupees for qty of an item on the menu."""
    return MENU[item.lower().strip()] * qty

history = [{"role": "system", "content": SYSTEM}]
MAX_TURNS = 8

def chat(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})
    recent = [history[0]] + history[1:][-MAX_TURNS:]
    try:
        response = client.chat.completions.create(model=MODEL, messages=recent, temperature=0.3)
        reply = response.choices[0].message.content
    except RateLimitError:
        reply = "We're a little busy. Please try again in a minute."
    except APIConnectionError:
        reply = "I can't reach the server right now. Please try again shortly."
    history.append({"role": "assistant", "content": reply})
    return reply

print("Total for 6 cupcakes:", get_price("cupcake", 6))
while True:
    text = input("You: ")
    if text.lower().strip() in ("bye", "exit", "quit"):
        print("Bot: Thank you for visiting Sweet Crumbs!")
        break
    print("Bot:", chat(text))
```

**Customer Simulation Test**:
1. State your name (`"Hi, I'm Ravi"`).
2. Order an eggless chocolate cake for tomorrow.
3. Ask the price for two (`"How much for 2?"`).
4. Ask `"What did I order?"`.
5. Verify it remembers your name and order, quotes Rs 1,300, and never promises unvetted delivery times.

---

### 🧪 Day 2 "Your 10%" Hands-on Tasks
1. **Prompt Parts Test**:
   - Delete the `RULES` lines from the system prompt and ask: `"Can you deliver in 1 hour?"`.
   - Restore the `RULES` lines and ask again. Compare the safety and behavior.
2. **Few-Shot Intent Classifier**:
   - Build a classifier for your business using 3 few-shot worked examples (`order`, `question`, `complaint`).
   - Test it against 5 unseen customer messages to verify format consistency.
3. **Structured JSON Extraction**:
   - Instruct the bot to extract customer orders as pure JSON:
     `{"name": str, "item": str, "qty": int, "date": str, "eggless": bool}`.
   - Parse the response with `json.loads` inside a `try/except` block.
4. **Memory Trimming & Context Window**:
   - Set `MAX_TURNS = 2`.
   - Introduce yourself with your name in turn 1.
   - Chat for 3 turns on unrelated questions.
   - Ask `"What is my name?"` to observe how trimming drops older conversational context.
5. **Business Customization**:
   - Adapt the full Day 2 script for your own business:
     - Catalogue/menu as a Python dictionary.
     - Price/lookup function with type hints and docstring.
     - Tailored `SYSTEM` prompt with specific role, facts, rules, and format.

### 📝 Preparation for Day 3 (Level 2: AI Agents)
- [ ] Bring your **10 customer questions** and your business's catalogue formatted as a Python dictionary.
- [ ] Next session starts building autonomous agent loops with LangChain and tool execution.
