# Deploying SafeBasket (Lovable + custom domains)

This guide deploys SafeBasket to production with the domains **safebasket.co.in** and
**safebaskets.com**.

## Important architecture note

Lovable Cloud hosts the **React frontend** (with custom-domain support) and a **Supabase**
backend. It does **not** run a Python/FastAPI/LangChain/FAISS service. So SafeBasket deploys
as two pieces:

```
                 custom domains                          VITE_API_BASE_URL
  safebasket.co.in / safebaskets.com ──► Lovable (React) ───────────────► Python API
                                                                          (Render/Railway/Fly)
```

1. **Frontend** → Lovable Cloud, mapped to your two custom domains.
2. **Python agent (`backend/`)** → any container host (Render/Railway/Fly/Cloud Run). The
   frontend calls it via the `VITE_API_BASE_URL` secret.

You must perform the Lovable publish, the paid-plan upgrade, the custom-domain steps, and the
DNS edits yourself — they require your Lovable account and access to your domain registrar.

---

## Step 1 — Deploy the Python API to a public URL

A `backend/Dockerfile` and a root `render.yaml` blueprint are included.

**Render (one option):**
1. Push this repo to GitHub (already done if you merged the PR).
2. Render → **New + → Blueprint** → select this repo. It reads `render.yaml` and builds
   `backend/Dockerfile`.
3. Wait for **Live**, then copy the service URL, e.g. `https://safebasket-api.onrender.com`.
   (Optionally map it to `api.safebasket.co.in` via a `CNAME` in your DNS.)
4. The health check is `GET /health`; docs are at `/docs`.

CORS is already locked to the production domains via the `SAFEBASKET_CORS_ORIGINS` env var in
`render.yaml`. Optional keys (`OPENAI_API_KEY`, `TAVILY_API_KEY`, …) can be added in the host
dashboard — the API runs fine without them.

## Step 2 — Put the frontend on Lovable

Lovable can't import an existing repo and isn't monorepo-compatible, so use the
**`cursor/lovable-deploy-ac6e`** branch (root-level Vite app) and follow the export
workaround in [`LOVABLE.md`](LOVABLE.md). In short:

1. Let Lovable create a repo (Project → Settings → Git), then push this branch's root-level
   app into it.
2. Add a secret **`VITE_API_BASE_URL`** = your Step 1 API URL (e.g.
   `https://safebasket-api.onrender.com` or `https://api.safebasket.co.in`).
   The frontend reads this (see `src/api.js`).
3. **Publish** the project (you get a `xxx.lovable.app` URL first).

## Step 3 — Connect the custom domains

Custom domains require a **paid Lovable plan** and a **published** project.

For **each** domain (`safebasket.co.in` and `safebaskets.com`):

1. Lovable → **Project → Settings → Domains** (or the Publish modal → Custom domain).
2. Enter the domain. Use **Entri** automatic setup if your registrar is listed, otherwise pick
   **manual setup** and Lovable shows you an **`A` record** and a **`TXT`** verification record.
3. Add those exact records at your registrar (see the table below). The `www` subdomain is set
   up by Lovable automatically.
4. **Remove any `AAAA` (IPv6) records** for the domain — they break Lovable routing.
5. Click **Done / Check status**; Lovable verifies and issues SSL. Set one domain as **primary**.

### DNS records to add (use the exact values Lovable shows you)

| Host / Name | Type | Value | Notes |
|-------------|------|-------|-------|
| `@` (apex)  | `A`  | *(IP from Lovable)* | Points the root domain to Lovable |
| `@` (apex)  | `TXT`| *(token from Lovable)* | Ownership verification |
| `www`       | `CNAME` | *(target from Lovable, if shown)* | Usually configured automatically |

> Do this for both `safebasket.co.in` and `safebaskets.com`. Propagation is usually minutes,
> occasionally up to 72h. Don't leave stale `AAAA` records.

## Step 4 — Verify

- Visit `https://safebasket.co.in` and `https://safebaskets.com` → the SafeBasket site loads.
- Top-right shows **"API live · N additives indexed"** (confirms the frontend reached the API).
- Run a brand search (e.g. `Maggi Masala`) and a cart-screenshot scan end-to-end.

If the API badge shows offline: check `VITE_API_BASE_URL` in Lovable and that the API's
`SAFEBASKET_CORS_ORIGINS` includes your live domains.
