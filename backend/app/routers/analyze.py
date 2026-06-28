"""Analysis endpoints: text/brand, ingredient-label image, and cart screenshots."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..core.agent import run_agent
from ..core.knowledge_base import get_knowledge_base
from ..core.ocr import image_to_text, ocr_available, split_cart_lines
from ..dependencies import resolve_tier
from ..schemas import (
    AnalysisResult,
    AnalyzeTextRequest,
    CartAnalysisResult,
    CartItemResult,
)

router = APIRouter(prefix="/api/v1", tags=["analyze"])


@router.post("/analyze", response_model=AnalysisResult)
def analyze(req: AnalyzeTextRequest, tier: dict = Depends(resolve_tier)) -> AnalysisResult:
    if not req.brand and not req.ingredients_text:
        raise HTTPException(status_code=422, detail="Provide a brand or ingredients_text.")
    result = run_agent(
        brand=req.brand,
        ingredients_text=req.ingredients_text,
        deep_research=req.deep_research,
    )
    return AnalysisResult(**result)


@router.post("/analyze-image", response_model=AnalysisResult)
async def analyze_image(
    file: UploadFile = File(...),
    deep_research: bool = Form(default=False),
    tier: dict = Depends(resolve_tier),
) -> AnalysisResult:
    """Analyse a photo of an ingredients label via OCR."""
    if not ocr_available():
        raise HTTPException(
            status_code=503,
            detail="OCR engine (Tesseract) is not available in this environment.",
        )
    text = image_to_text(await file.read())
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from the image.")
    result = run_agent(ingredients_text=text, deep_research=deep_research)
    return AnalysisResult(**result)


@router.post("/analyze-cart", response_model=CartAnalysisResult)
async def analyze_cart(
    file: UploadFile = File(...),
    deep_research: bool = Form(default=False),
    tier: dict = Depends(resolve_tier),
) -> CartAnalysisResult:
    """Analyse a shopping-cart screenshot (Blinkit/Zepto/BigBasket/Amazon/etc.).

    OCRs the screenshot, matches each detected line to known products and flags
    items containing harmful/carcinogenic additives, with safer recommendations.
    """
    if not ocr_available():
        raise HTTPException(
            status_code=503,
            detail="OCR engine (Tesseract) is not available in this environment.",
        )
    kb = get_knowledge_base()
    text = image_to_text(await file.read())
    lines = split_cart_lines(text)
    if not lines:
        raise HTTPException(status_code=422, detail="Could not read any items from the screenshot.")

    items: list[CartItemResult] = []
    total_flagged = 0
    seen_products: set[str] = set()

    for line in lines:
        product = kb.find_product(line)
        if not product or product.id in seen_products:
            continue
        seen_products.add(product.id)
        result = run_agent(brand=product.name, deep_research=deep_research)
        total_flagged += len(result["flagged"])
        items.append(
            CartItemResult(
                detected_text=line,
                matched_product=product.name,
                analysis=AnalysisResult(**result),
            )
        )

    if not items:
        overall = (
            "Read the screenshot but could not confidently match any line to a known "
            "product in the catalogue. Try the brand search or an ingredient-label photo."
        )
    else:
        risky = [i.matched_product for i in items if i.analysis.rating != "clean"]
        overall = (
            f"Analysed {len(items)} recognised item(s); {len(risky)} need attention"
            + (": " + ", ".join(filter(None, risky)) if risky else ".")
        )

    return CartAnalysisResult(
        items=items,
        overall_summary=overall,
        total_flagged=total_flagged,
        disclaimer=kb.product_disclaimer,
    )
