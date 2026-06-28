# SafeBasket

Food-safety agent for Indian consumers. Two products share one Python agent:
a free **React website** (`frontend/`) and a commercial **FastAPI API** (`backend/`).
See `README.md` for architecture and standard commands.

## Cursor Cloud specific instructions

Services (run each in its own terminal; do not background blindly):

| Service  | Dir         | Dev command                                            | Port |
|----------|-------------|--------------------------------------------------------|------|
| API      | `backend/`  | `. .venv/bin/activate && uvicorn app.main:app --reload --port 8000` | 8000 |
| Website  | `frontend/` | `npm run dev`                                          | 5173 |

Non-obvious notes:

- **Backend uses a venv at `backend/.venv`.** Always `. backend/.venv/bin/activate`
  before running `uvicorn`/`pytest`; the update script (re)creates it.
- **Runs fully offline with no secrets.** With no `OPENAI_API_KEY`, the agent uses a
  deterministic rule-based engine; with no sentence-transformers installed, the FAISS
  RAG layer uses a built-in hashing-embedding fallback (see `/health` → `embeddings`).
  Everything still works — this is expected, not a misconfiguration.
- **OCR needs the Tesseract system binary** (`tesseract-ocr`, installed via apt — NOT pip).
  `/health` reports `ocr_available`. Without it, `/api/v1/analyze-image` and
  `/api/v1/analyze-cart` return 503 but brand/ingredient-text analysis still works.
  Generate a sample cart screenshot with `python backend/scripts/make_sample_cart.py <out>`.
- **Optional integrations** (LLM, Tavily web search, LangSmith) activate only when their
  env vars are set; see `backend/.env.example`. Web research is off unless
  `SAFEBASKET_ENABLE_WEB_SEARCH=true` AND `TAVILY_API_KEY` are present.
- **The website talks to the agent only through the API.** Vite proxies `/api` and
  `/health` to `http://localhost:8000`, so start the backend before the frontend.
- **High-quality embeddings are optional** and live in `backend/requirements-ml.txt`
  (pulls in torch — large). The core `requirements.txt` deliberately omits it.
- **Compliance:** keep messaging FSSAI-aligned — surface public regulatory info, note
  additives may be within FSSAI limits, never assert a product is unsafe.
