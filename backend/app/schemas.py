"""Pydantic request/response models for the SafeBasket API."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    brand: Optional[str] = Field(
        default=None,
        description="Indian food brand or product name to look up (e.g. 'Maggi Masala').",
    )
    ingredients_text: Optional[str] = Field(
        default=None,
        description="Raw ingredients-section text copied from a label.",
    )
    deep_research: bool = Field(
        default=False,
        description="If true, runs conditional web research for flagged items (when enabled).",
    )


class RegulatorySource(BaseModel):
    authority: str
    note: str


class FlaggedIngredient(BaseModel):
    name: str
    code: Optional[str] = None
    category: str
    severity: Literal["high", "medium", "low"]
    carcinogen: bool
    concern: str
    regulatory: list[RegulatorySource]
    advice: str
    sources: list[str]
    matched_text: str


class RecommendedProduct(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    reason: str


class AnalysisResult(BaseModel):
    input_summary: str
    safety_score: int = Field(description="0 (avoid) to 100 (clean), higher is safer.")
    rating: Literal["clean", "caution", "high_risk"]
    flagged: list[FlaggedIngredient]
    carcinogen_count: int
    recommendations: list[RecommendedProduct]
    summary: str
    web_research: list[str] = Field(default_factory=list)
    engine: Literal["llm-agent", "rule-based"]
    disclaimer: str


class CartItemResult(BaseModel):
    detected_text: str
    matched_product: Optional[str] = None
    analysis: AnalysisResult


class CartAnalysisResult(BaseModel):
    items: list[CartItemResult]
    overall_summary: str
    total_flagged: int
    disclaimer: str


class HealthResponse(BaseModel):
    status: str
    version: str
    llm_enabled: bool
    web_search_enabled: bool
    langsmith_enabled: bool
    embeddings: str
    ingredients_indexed: int
    ocr_available: bool
