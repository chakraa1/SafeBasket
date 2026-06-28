"""Embedding providers for the FAISS RAG layer.

Primary provider is a local sentence-transformers model. If the model cannot be
loaded (e.g. no network to download weights), we fall back to a deterministic
hashing embedding so the FAISS index always builds and the product works fully
offline.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import List

import numpy as np
from langchain_core.embeddings import Embeddings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


class HashingEmbeddings(Embeddings):
    """Deterministic, dependency-light embedding via the hashing trick.

    Produces L2-normalised dense vectors using token unigrams + bigrams hashed
    into a fixed dimensional space. Quality is modest but it is fully offline
    and stable, which is ideal as a fallback for the FAISS index.
    """

    name = "hashing-fallback"

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def _embed_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype="float32")
        tokens = _tokenize(text)
        grams = list(tokens)
        grams += [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        for gram in grams:
            h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            sign = 1.0 if (h >> 1) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(float(np.dot(vec, vec)))
        if norm > 0:
            vec /= norm
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_one(t).tolist() for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_one(text).tolist()


def build_embeddings(model_name: str):
    """Return (embeddings, label). Tries sentence-transformers, else falls back."""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore

        emb = HuggingFaceEmbeddings(model_name=model_name)
        # Force a tiny embed to ensure weights actually load before committing.
        emb.embed_query("safebasket healthcheck")
        return emb, f"sentence-transformers:{model_name}"
    except Exception:  # pragma: no cover - network/model load failure path
        return HashingEmbeddings(), HashingEmbeddings.name
