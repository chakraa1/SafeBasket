"""Deterministic analysis engine.

This is the rule-based core that always works (no external API keys needed). It
combines:
  * harmful-ingredient matching against the curated regulatory knowledge base,
  * FAISS RAG retrieval for supporting regulatory context,
  * a transparent safety score, and
  * safer-product recommendations.

The LangChain agent (agent.py) uses this engine as its grounded tool/fallback.
"""

from __future__ import annotations

from .knowledge_base import Product, get_knowledge_base
from .matcher import Match, match_harmful
from .rag import get_rag_index
from .recommender import recommend
from .websearch import research, should_research

SEVERITY_PENALTY = {"high": 35, "medium": 18, "low": 7}
DISCLAIMER = (
    "SafeBasket provides educational information aggregated from public regulatory "
    "databases (FSSAI, FDA CFSAN, EFSA, IARC/WHO, RASFF, Singapore SFA, Hong Kong CFS). "
    "Listed additives may be permitted within FSSAI limits. This is not medical or legal "
    "advice and does not assert any product is unsafe; always read the official label."
)


def _score(matches: list[Match]) -> tuple[int, str]:
    score = 100
    for m in matches:
        score -= SEVERITY_PENALTY.get(m.ingredient.severity, 10)
        if m.ingredient.carcinogen:
            score -= 8
    score = max(0, min(100, score))

    # A high-severity carcinogen (e.g. a banned additive like potassium bromate)
    # always escalates to high-risk regardless of the numeric score.
    force_high_risk = any(
        m.ingredient.carcinogen and m.ingredient.severity == "high" for m in matches
    )

    if force_high_risk or score < 50:
        rating = "high_risk"
    elif score >= 80:
        rating = "clean"
    else:
        rating = "caution"
    return score, rating


def _flagged_payload(matches: list[Match]) -> list[dict]:
    payload = []
    for m in matches:
        ing = m.ingredient
        payload.append(
            {
                "name": ing.name,
                "code": ing.code,
                "category": ing.category,
                "severity": ing.severity,
                "carcinogen": ing.carcinogen,
                "concern": ing.concern,
                "regulatory": [
                    {"authority": k, "note": v} for k, v in ing.regulatory.items()
                ],
                "advice": ing.advice,
                "sources": ing.sources,
                "matched_text": m.matched_text,
            }
        )
    return payload


def _summary(matches: list[Match], rating: str, carcinogen_count: int) -> str:
    if not matches:
        return "No additives of concern were detected from the provided information. Looks clean."
    high = [m.ingredient.name for m in matches if m.ingredient.severity == "high"]
    parts = [f"Found {len(matches)} ingredient(s) of interest."]
    if carcinogen_count:
        parts.append(
            f"{carcinogen_count} carry a carcinogenicity flag from global regulators."
        )
    if high:
        parts.append("Higher-concern items: " + ", ".join(high) + ".")
    if rating == "high_risk":
        parts.append("Overall this product is high-risk; consider a safer alternative.")
    elif rating == "caution":
        parts.append("Consume in moderation and consider cleaner options.")
    return " ".join(parts)


def analyze_text(
    *,
    brand: str | None,
    ingredients_text: str | None,
    deep_research: bool = False,
) -> dict:
    """Core analysis used by both the API and the LangChain agent."""
    kb = get_knowledge_base()
    rag = get_rag_index()

    product: Product | None = None
    text_parts: list[str] = []
    input_summary_parts: list[str] = []

    if brand:
        product = kb.find_product(brand)
        input_summary_parts.append(f"brand/product='{brand}'")
        if product:
            text_parts.extend(product.ingredients)
            input_summary_parts.append(f"matched catalogue product '{product.name}'")
    if ingredients_text:
        text_parts.append(ingredients_text)
        input_summary_parts.append("provided ingredient text")

    combined = " , ".join(text_parts)
    matches = match_harmful(combined) if combined else []

    score, rating = _score(matches)
    carcinogen_count = sum(1 for m in matches if m.ingredient.carcinogen)

    category = product.category if product else None
    recommendations = recommend(category, matches) if rating != "clean" else []

    # FAISS RAG: pull supporting regulatory context for the flagged items.
    rag_context = rag.context_for([m.ingredient.name for m in matches])

    web_research: list[str] = []
    if matches and (deep_research or should_research(matches)):
        web_research = research([m.ingredient.name for m in matches if m.ingredient.carcinogen])

    return {
        "input_summary": "; ".join(input_summary_parts) or "no input provided",
        "safety_score": score,
        "rating": rating,
        "flagged": _flagged_payload(matches),
        "carcinogen_count": carcinogen_count,
        "recommendations": recommendations,
        "summary": _summary(matches, rating, carcinogen_count),
        "web_research": web_research,
        "engine": "rule-based",
        "disclaimer": DISCLAIMER,
        "_rag_context": rag_context,
        "_matches": matches,
        "_category": category,
    }
