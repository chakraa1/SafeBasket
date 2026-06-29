# Deploying SafeBasket's frontend to Lovable

This branch (`cursor/lovable-deploy-ac6e`) is the **Lovable-compatible** layout: the Vite
React app is at the **repository root** (Lovable requires a root-level, non-monorepo Vite
app). The Python agent stays in `backend/` and is deployed separately — the frontend calls
it through `VITE_API_BASE_URL`, so **the agent workflow is identical** to `main`.

## Why a workaround is needed

Lovable **cannot import an existing GitHub repo** (it only *exports* to a repo it creates),
it is **not monorepo-compatible**, and it expects a **Vite React** app at the repo root.
So we make Lovable create a repo, then push this branch's root-level app into it.

## Steps

### 1. Deploy the Python API (once)

Lovable does not run Python. Deploy `backend/` to any container host (Render/Railway/Fly)
using `backend/Dockerfile` (a `render.yaml` blueprint is included). Copy the public URL,
e.g. `https://safebasket-api.onrender.com`. See `DEPLOYMENT.md` for details.

### 2. Create a Lovable project and let it make a GitHub repo

1. In Lovable, create a new project (any starter prompt; it must be a Vite React app).
2. Project → Settings → Git → connect GitHub. Lovable **creates a new repo** and starts
   two-way sync. Note that repo URL.

### 3. Push this app into Lovable's repo (the export workaround)

```bash
# Clone the repo Lovable just created
git clone https://github.com/<you>/<lovable-repo>.git lovable-clone
cd lovable-clone

# Replace its contents with THIS branch's root-level app, keeping Lovable's .git
git checkout -b safebasket
rsync -a --delete --exclude='.git' \
  /path/to/SafeBasket-on-lovable-deploy-branch/ ./
git add -A && git commit -m "Import SafeBasket frontend" && git push -u origin safebasket
```

Lovable picks up the pushed code via two-way sync. (Keeping `backend/` in the repo is
harmless — Lovable only builds the root Vite app.)

### 4. Configure and publish

1. In Lovable, add a secret **`VITE_API_BASE_URL`** = your Step 1 API URL.
2. **Publish** the project → you get a `xxx.lovable.app` URL. Confirm the top-right badge
   reads "API live · N additives indexed".

### 5. Custom domains

On a paid Lovable plan, map `safebasket.co.in` and `safebaskets.com` (Project → Settings →
Domains; add the `A` + `TXT` records Lovable shows; remove any `AAAA`). Full DNS guidance is
in `DEPLOYMENT.md`.

## Notes

- Keep the backend's `SAFEBASKET_CORS_ORIGINS` set to your live domains (and the
  `*.lovable.app` preview URL) so the browser can call the API.
- The agent, RAG, and LangSmith observability are unchanged from `main` — only the frontend
  folder location changed for Lovable compatibility.
