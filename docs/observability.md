# Observability with LangSmith (free tier)

SafeBasket traces its agent pipeline to [LangSmith](https://smith.langchain.com).
Because every step is instrumented with the `@traceable` decorator (not just LLM
calls), the **free, no-LLM tier is fully observable** too — you see the matcher,
FAISS retrieval, recommender, and conditional web-research spans for each request.

## Enable it (free LangSmith account)

1. Create a free LangSmith account at <https://smith.langchain.com> and generate an
   API key (Settings → API Keys). The free Developer plan is enough.
2. Set the key for the backend. Either export it before running, or add it to your
   process manager / host:

   ```bash
   export LANGSMITH_API_KEY=ls-...           # or LANGCHAIN_API_KEY=ls-...
   export LANGCHAIN_PROJECT=safebasket        # optional, defaults to "safebasket"
   ```

   That's all — the app enables tracing automatically on startup
   (`Settings.configure_langsmith()` sets `LANGCHAIN_TRACING_V2` / `LANGSMITH_TRACING`).
3. Restart the API and confirm: `GET /health` reports `"langsmith_enabled": true`.
4. Make any request (e.g. analyse `Maggi Masala`) and open your LangSmith project —
   you'll see a `safebasket_agent` trace with nested spans.

## What you'll see

```
safebasket_agent (chain)
└─ analyze (chain)
   ├─ match_harmful_ingredients (tool)
   ├─ faiss_rag_retrieve (retriever)
   ├─ recommend_alternatives (tool)
   └─ web_research (tool)        # only when a flagged item is carcinogenic/high-risk
```

With `OPENAI_API_KEY` also set, the `ChatOpenAI` narrative call is auto-traced by
LangChain and appears under the same root run.

## Notes

- **No key → no-op.** Without a LangSmith key, `@traceable` runs the functions
  normally and sends nothing, with negligible overhead. Nothing else changes.
- On Render/containers, set `LANGSMITH_API_KEY` (and optionally `LANGCHAIN_PROJECT`)
  as service env vars — see `render.yaml` and `backend/.env.example`.
- This is verified offline in `backend/tests/test_observability.py`, which injects a
  recording client and asserts the spans above are emitted in the free tier.
