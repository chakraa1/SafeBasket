"""Conditional web-research tool.

Only runs when explicitly enabled AND a flagged ingredient warrants deeper
research (e.g. a carcinogen or a recent recall). Uses Tavily when a key is
present; otherwise returns a clear, honest note that live research is disabled.
"""

from __future__ import annotations

from ..config import get_settings
from .observability import traceable


def should_research(matches) -> bool:
    """Decide whether conditional web research is warranted."""
    return any(m.ingredient.carcinogen or m.ingredient.severity == "high" for m in matches)


@traceable(run_type="tool", name="web_research")
def research(names: list[str]) -> list[str]:
    settings = get_settings()
    if not names:
        return []
    if not settings.enable_web_search:
        return [
            "Live web research is disabled in this environment. Enable it by setting "
            "SAFEBASKET_ENABLE_WEB_SEARCH=true and providing TAVILY_API_KEY to fetch "
            "recent recalls/news from global food authorities."
        ]
    if not settings.tavily_api_key:
        return ["Web search enabled but TAVILY_API_KEY is missing; skipping live research."]

    try:
        from langchain_community.tools.tavily_search import TavilySearchResults  # type: ignore

        tool = TavilySearchResults(max_results=3, api_key=settings.tavily_api_key)
        findings: list[str] = []
        for name in names[:3]:
            query = f"{name} food safety recall warning carcinogen news"
            results = tool.invoke({"query": query})
            for r in results if isinstance(results, list) else []:
                content = r.get("content") or r.get("snippet") or ""
                url = r.get("url", "")
                if content:
                    findings.append(f"{name}: {content[:240]} ({url})")
        return findings or ["No notable recent web findings for the flagged ingredients."]
    except Exception as exc:  # pragma: no cover - network dependent
        return [f"Web research failed: {exc}"]
