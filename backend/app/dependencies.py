"""Shared API dependencies: tier/mode resolution for free vs commercial use."""

from __future__ import annotations

from fastapi import Header

from .config import get_settings


def resolve_tier(x_api_key: str | None = Header(default=None)) -> dict:
    """Resolve the caller's tier.

    SafeBasket runs in two modes:
      * "free"       - no key required (used to onboard consumers for free), and
      * "commercial" - a recognised API key unlocks the metered/commercial tier.

    The free tier is always available; this never blocks a request, matching the
    product goal of free onboarding while leaving room for monetisation.
    """
    settings = get_settings()
    if x_api_key and x_api_key in settings.commercial_api_keys:
        return {"tier": "commercial", "authenticated": True}
    return {"tier": "free", "authenticated": False}
