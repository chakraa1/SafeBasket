"""End-to-end style tests for the SafeBasket API and analysis engine."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.analyzer import analyze_text
from app.core.matcher import match_harmful
from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["ingredients_indexed"] > 0


def test_matcher_detects_known_additive():
    matches = match_harmful("Ingredients: maida, palm oil, monosodium glutamate (E621), TBHQ")
    names = {m.ingredient.name for m in matches}
    assert "Monosodium glutamate" in names
    assert "Tertiary butylhydroquinone" in names


def test_analyze_brand_maggi():
    res = client.post("/api/v1/analyze", json={"brand": "Maggi Masala"})
    assert res.status_code == 200
    body = res.json()
    assert body["rating"] in {"caution", "high_risk"}
    assert body["safety_score"] < 100
    assert any(f["name"] == "Monosodium glutamate" for f in body["flagged"])
    assert body["recommendations"], "expected safer alternatives"


def test_analyze_carcinogen_bread():
    res = client.post(
        "/api/v1/analyze",
        json={"ingredients_text": "maida, water, yeast, potassium bromate (E924)"},
    )
    body = res.json()
    assert body["carcinogen_count"] >= 1
    assert body["rating"] == "high_risk"


def test_analyze_clean_product():
    res = client.post("/api/v1/analyze", json={"brand": "Amul Taaza"})
    body = res.json()
    assert body["rating"] == "clean"
    assert body["flagged"] == []


def test_analyze_requires_input():
    res = client.post("/api/v1/analyze", json={})
    assert res.status_code == 422


def test_rag_context_present():
    result = analyze_text(brand="Kurkure", ingredients_text=None)
    assert result["_rag_context"], "FAISS RAG should return supporting context"
    assert result["engine"] == "rule-based"


def test_catalogue():
    res = client.get("/api/v1/catalogue")
    assert res.status_code == 200
    assert res.json()["count"] > 0
