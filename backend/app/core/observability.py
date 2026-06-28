"""LangSmith observability helpers.

We trace the SafeBasket agent pipeline with LangSmith's ``@traceable`` decorator.
Crucially this works for the **free tier** too: the rule-based engine never calls
an LLM, but ``@traceable`` still records each step (matching, FAISS retrieval,
recommendation, web research) so the whole agent run is observable.

Tracing only sends data when LangSmith is configured (an API key is present);
otherwise ``@traceable`` is a transparent no-op with negligible overhead. The
import is guarded so the service still runs if the langsmith SDK is unavailable.
"""

from __future__ import annotations

try:  # langsmith ships as a dependency of langchain-core
    from langsmith import traceable  # type: ignore
except Exception:  # pragma: no cover - defensive fallback

    def traceable(*dargs, **dkwargs):  # type: ignore
        """No-op stand-in matching the @traceable(...) / @traceable usage."""
        if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
            return dargs[0]

        def decorator(func):
            return func

        return decorator


__all__ = ["traceable"]
