"""Health and metadata endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from .. import __version__
from ..config import get_settings
from ..core.knowledge_base import get_knowledge_base
from ..core.ocr import ocr_available
from ..core.rag import get_rag_index
from ..schemas import HealthResponse

router = APIRouter(tags=["meta"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    rag = get_rag_index()
    return HealthResponse(
        status="ok",
        version=__version__,
        llm_enabled=settings.llm_enabled,
        web_search_enabled=settings.enable_web_search,
        langsmith_enabled=settings.langsmith_enabled,
        embeddings=rag.label,
        ingredients_indexed=rag.size,
        ocr_available=ocr_available(),
    )


@router.get("/api/v1/catalogue", tags=["catalogue"])
def catalogue() -> dict:
    """Public catalogue of Indian products SafeBasket can recognise by name."""
    kb = get_knowledge_base()
    return {
        "count": len(kb.products),
        "products": [
            {"id": p.id, "name": p.name, "brand": p.brand, "category": p.category}
            for p in kb.products
        ],
        "disclaimer": kb.product_disclaimer,
    }
