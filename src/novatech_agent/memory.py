from typing import Dict, List, Any
from datetime import datetime

class ConversationMemoryManager:
    """
    Manages multi-turn conversation memory with isolated threads (thread_id).
    Compatible with LangGraph checkpointer / InMemorySaver semantics.
    """
    def __init__(self):
        self._threads: Dict[str, List[Dict[str, str]]] = {}
        self._saver = None
        try:
            from langgraph.checkpoint.memory import InMemorySaver
            self._saver = InMemorySaver()
        except ImportError:
            self._saver = None

    def get_saver(self):
        """Returns LangGraph InMemorySaver instance if installed."""
        return self._saver

    def get_history(self, thread_id: str) -> List[Dict[str, str]]:
        """Retrieve conversation message history for a given thread."""
        return self._threads.get(thread_id, [])

    def add_message(self, thread_id: str, role: str, content: str):
        """Append a user or assistant message to the thread history."""
        if thread_id not in self._threads:
            self._threads[thread_id] = []
        self._threads[thread_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def clear_thread(self, thread_id: str):
        """Clear memory for a thread."""
        if thread_id in self._threads:
            del self._threads[thread_id]

# Singleton instance
memory_manager = ConversationMemoryManager()
