"""SafeBasket FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import get_settings
from .core.agent import warmup
from .routers import analyze, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.configure_langsmith()
    # Build the FAISS index up-front so the first request is fast.
    warmup()
    yield


app = FastAPI(
    title="SafeBasket API",
    description=(
        "Food-safety intelligence for Indian consumers. Detects harmful/carcinogenic "
        "additives in packaged foods (by brand, ingredient text, label photo, or "
        "shopping-cart screenshot) using a RAG system grounded in global regulatory "
        "databases, and recommends safer alternatives."
    ),
    version=__version__,
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "name": "SafeBasket API",
        "version": __version__,
        "docs": "/docs",
        "modes": ["free (no key)", "commercial (X-API-Key)"],
    }
