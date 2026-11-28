import math
import re
from typing import List, Dict, Tuple
from .config import POLICIES

class RAGKnowledgeBase:
    """
    RAG Vector Store for NovaTech policies and FAQ documents.
    Supports ChromaDB if installed, with a high-accuracy TF-IDF cosine vector
    search fallback when running in lightweight environments.
    """
    def __init__(self):
        self.chroma_collection = None
        self.documents = []
        self.doc_ids = []
        self._initialize()

    def _initialize(self):
        # Prepare document chunks
        self.documents = []
        self.doc_ids = []
        for key, text in POLICIES.items():
            self.doc_ids.append(key)
            self.documents.append(f"[{key.upper()}] {text}")

        # Try initializing ChromaDB
        try:
            import chromadb
            client = chromadb.Client()
            self.chroma_collection = client.get_or_create_collection("novatech_policies")
            # Populate collection
            self.chroma_collection.add(
                documents=self.documents,
                ids=self.doc_ids
            )
        except Exception:
            self.chroma_collection = None

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def _cosine_search(self, query: str, top_k: int = 2) -> List[str]:
        """Built-in lightweight vector similarity search."""
        q_lower = query.lower()
        q_tokens = set(self._tokenize(query))
        scored = []
        for doc_id, doc in zip(self.doc_ids, self.documents):
            d_tokens = self._tokenize(doc)
            if not d_tokens:
                continue
            common = q_tokens.intersection(set(d_tokens))
            score = len(common) / (math.sqrt(len(q_tokens) + 1) * math.sqrt(len(set(d_tokens))))
            # Exact topic boost if doc tag matches query
            if doc_id.replace("_", " ") in q_lower or any(part in q_lower for part in doc_id.split("_")):
                score += 0.8
            # Keyword boosts
            for word in ["warranty", "diagnostic", "fee", "student", "discount", "express", "urgent", "return", "refund", "upi", "payment", "liquid", "water", "delivery"]:
                if word in q_lower and word in doc.lower():
                    score += 0.35
            scored.append((score, doc))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k] if score > 0.05]

    def query(self, query_text: str, n_results: int = 2) -> str:
        """Searches policy documents and returns formatted string of matching knowledge."""
        if self.chroma_collection is not None:
            try:
                res = self.chroma_collection.query(query_texts=[query_text], n_results=n_results)
                docs = res.get("documents", [[]])[0]
                if docs:
                    return "\n\n".join(docs)
            except Exception:
                pass
        
        results = self._cosine_search(query_text, top_k=n_results)
        if results:
            return "\n\n".join(results)
        return "No specific policy document matched. Please ask the store manager directly."

# Singleton instance
kb = RAGKnowledgeBase()

def search_policies(query: str) -> str:
    """Tool function: search store policies, warranty, diagnostic fees, returns, and turnaround."""
    return kb.query(query)
