"""Matches harmful ingredients/additives within free-form label text."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .knowledge_base import Ingredient, get_knowledge_base


@dataclass
class Match:
    ingredient: Ingredient
    matched_text: str


def _normalise(text: str) -> str:
    text = text.lower()
    # Normalise additive code spellings: "e 102", "ins102", "e-102" -> "e102"
    text = re.sub(r"\b(e|ins)[\s\-]?(\d{3}[a-z]?)\b", r"\1\2", text)
    return text


def match_harmful(text: str) -> list[Match]:
    """Return harmful-ingredient matches found in the supplied text."""
    kb = get_knowledge_base()
    norm = _normalise(text)
    matches: list[Match] = []
    seen: set[str] = set()

    for ing in kb.ingredients:
        candidates = [ing.name, *(ing.aliases or [])]
        if ing.code:
            candidates.append(ing.code)
        for cand in candidates:
            cand_norm = _normalise(cand)
            if not cand_norm:
                continue
            # Word-boundary search for short codes, substring for longer names.
            if len(cand_norm) <= 5:
                pattern = r"(?<![a-z0-9])" + re.escape(cand_norm) + r"(?![a-z0-9])"
                found = re.search(pattern, norm)
            else:
                found = cand_norm in norm
            if found:
                if ing.name not in seen:
                    seen.add(ing.name)
                    matches.append(Match(ingredient=ing, matched_text=cand))
                break

    # Sort by severity (high -> low) then carcinogen flag first.
    order = {"high": 0, "medium": 1, "low": 2}
    matches.sort(key=lambda m: (order.get(m.ingredient.severity, 3), not m.ingredient.carcinogen))
    return matches
