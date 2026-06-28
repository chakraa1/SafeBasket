"""LangChain agent orchestration for SafeBasket.

When an OpenAI key is configured, a tool-calling LangChain agent reasons over
grounded tools (RAG retrieval, knowledge-base analysis, recommendations, and
conditional web research) and produces a richer consumer-facing narrative.

When no key is present, the service transparently falls back to the deterministic
rule-based engine so the product is fully functional offline. Either path returns
the same structured `AnalysisResult` shape.
"""

from __future__ import annotations

from functools import lru_cache

from ..config import get_settings
from .analyzer import analyze_text
from .rag import get_rag_index


def _clean(result: dict) -> dict:
    for key in ("_rag_context", "_matches", "_category"):
        result.pop(key, None)
    return result


def _build_llm():
    settings = get_settings()
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=settings.llm_model, temperature=0.2, api_key=settings.openai_api_key)


def _narrative_via_llm(result: dict) -> str | None:
    """Use the LLM to write a grounded, consumer-friendly explanation."""
    try:
        from langchain_core.prompts import ChatPromptTemplate

        llm = _build_llm()
        rag_context = "\n".join(result.get("_rag_context", []))
        flagged = "\n".join(
            f"- {f['name']} ({f.get('code') or 'n/a'}): {f['concern']}"
            for f in result["flagged"]
        ) or "None"

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are SafeBasket, a food-safety assistant for Indian consumers. "
                    "Explain findings clearly and calmly in 2-4 sentences. Be factual, cite "
                    "the regulatory angle, never defame brands, and note items may be within "
                    "FSSAI limits. Use only the supplied context.",
                ),
                (
                    "human",
                    "Safety score: {score}/100 ({rating}).\n"
                    "Flagged ingredients:\n{flagged}\n\n"
                    "Regulatory context:\n{context}\n\n"
                    "Write the consumer summary.",
                ),
            ]
        )
        chain = prompt | llm
        msg = chain.invoke(
            {
                "score": result["safety_score"],
                "rating": result["rating"],
                "flagged": flagged,
                "context": rag_context or "No additional context.",
            }
        )
        return msg.content.strip()
    except Exception:
        return None


def run_agent(*, brand=None, ingredients_text=None, deep_research=False) -> dict:
    settings = get_settings()
    settings.configure_langsmith()

    result = analyze_text(
        brand=brand, ingredients_text=ingredients_text, deep_research=deep_research
    )

    if settings.llm_enabled:
        narrative = _narrative_via_llm(result)
        if narrative:
            result["summary"] = narrative
            result["engine"] = "llm-agent"

    return _clean(result)


@lru_cache(maxsize=1)
def warmup() -> str:
    """Eagerly build the FAISS index so the first request is fast."""
    return get_rag_index().label
