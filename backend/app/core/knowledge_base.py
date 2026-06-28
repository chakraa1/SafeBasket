"""Loads the curated regulatory knowledge base and Indian product catalogue."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..config import get_settings


@dataclass
class Ingredient:
    name: str
    code: str | None
    aliases: list[str]
    category: str
    severity: str
    carcinogen: bool
    concern: str
    regulatory: dict[str, str]
    found_in: list[str]
    advice: str
    sources: list[str]

    def as_document(self) -> str:
        reg = "; ".join(f"{k}: {v}" for k, v in self.regulatory.items())
        return (
            f"{self.name} ({self.code or 'n/a'}) is a {self.category}. "
            f"Concern: {self.concern} Regulatory status: {reg} "
            f"Commonly found in: {', '.join(self.found_in)}. Advice: {self.advice}"
        )


@dataclass
class Product:
    id: str
    name: str
    brand: str
    category: str
    ingredients: list[str]
    aliases: list[str] = field(default_factory=list)


class KnowledgeBase:
    def __init__(self, data_dir: Path) -> None:
        ingredients_raw = json.loads((data_dir / "ingredients.json").read_text())
        products_raw = json.loads((data_dir / "products.json").read_text())

        self.ingredients: list[Ingredient] = [Ingredient(**item) for item in ingredients_raw]
        self.products: list[Product] = [Product(**p) for p in products_raw["products"]]
        self.alternatives: dict[str, list[str]] = products_raw["alternatives"]
        self.alternative_advice: dict[str, str] = products_raw["alternative_advice"]
        self.product_disclaimer: str = products_raw["disclaimer"]

        self._product_by_id = {p.id: p for p in self.products}

    def product_by_id(self, pid: str) -> Product | None:
        return self._product_by_id.get(pid)

    def find_product(self, query: str) -> Product | None:
        """Best-effort product lookup by name/alias substring matching."""
        q = query.lower().strip()
        if not q:
            return None
        best: tuple[int, Product] | None = None
        for product in self.products:
            candidates = [product.name.lower(), product.brand.lower(), *[a.lower() for a in product.aliases]]
            for cand in candidates:
                if cand and (cand in q or q in cand):
                    score = len(cand)
                    if best is None or score > best[0]:
                        best = (score, product)
        return best[1] if best else None


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    settings = get_settings()
    return KnowledgeBase(settings.data_dir)
