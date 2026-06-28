"""FAISS-backed retrieval over the regulatory knowledge base.

Each harmful-ingredient entry becomes a document. The index supports semantic
retrieval of regulatory context which the agent uses to explain *why* a flagged
ingredient is concerning.
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from ..config import get_settings
from .embeddings import build_embeddings
from .knowledge_base import get_knowledge_base


class RagIndex:
    def __init__(self) -> None:
        settings = get_settings()
        kb = get_knowledge_base()
        self.embeddings, self.label = build_embeddings(settings.embedding_model)

        documents: List[Document] = []
        for ing in kb.ingredients:
            documents.append(
                Document(
                    page_content=ing.as_document(),
                    metadata={"name": ing.name, "code": ing.code or "", "severity": ing.severity},
                )
            )
        self.size = len(documents)
        self.store = FAISS.from_documents(documents, self.embeddings)

    def search(self, query: str, k: int = 4) -> List[Tuple[str, float]]:
        results = self.store.similarity_search_with_score(query, k=k)
        return [(doc.page_content, float(score)) for doc, score in results]

    def context_for(self, names: List[str], k: int = 3) -> List[str]:
        """Retrieve supporting regulatory context for a set of ingredient names."""
        if not names:
            return []
        query = "regulatory safety concerns for " + ", ".join(names)
        return [content for content, _ in self.search(query, k=k)]


@lru_cache(maxsize=1)
def get_rag_index() -> RagIndex:
    return RagIndex()
