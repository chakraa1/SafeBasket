"""Recommends safer alternative products based on flagged categories."""

from __future__ import annotations

from .knowledge_base import get_knowledge_base
from .matcher import Match


def recommend(category: str | None, matches: list[Match]) -> list[dict]:
    """Suggest safer products for the given category (if known)."""
    kb = get_knowledge_base()
    if not category or category not in kb.alternatives:
        return []

    advice = kb.alternative_advice.get(category, "")
    recommendations: list[dict] = []
    for pid in kb.alternatives[category]:
        product = kb.product_by_id(pid)
        if not product:
            continue
        recommendations.append(
            {
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "reason": advice or "A cleaner option in the same category.",
            }
        )
    return recommendations
