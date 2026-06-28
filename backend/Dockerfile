# SafeBasket API - production image.
# Deploy this to any container host (Render, Railway, Fly.io, Cloud Run, etc.)
# to get the public backend URL that the Lovable-hosted frontend calls.

FROM python:3.12-slim

# Tesseract is required for the label / cart-screenshot OCR endpoints.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

EXPOSE 8000

# Honour the platform-provided $PORT (Render/Railway/Cloud Run set this).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
