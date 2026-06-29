// Thin API client. The website always reaches the agent through the API,
// matching the product's two-mode design (website + commercial API).
// In production (e.g. Lovable), point this at the deployed backend URL via the
// VITE_API_BASE_URL secret. Empty string falls back to same-origin / dev proxy.
const BASE =
  import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE || ''

async function handle(res) {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch (e) {
      // ignore non-JSON error bodies
    }
    throw new Error(detail)
  }
  return res.json()
}

export function analyzeText(payload) {
  return fetch(`${BASE}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(handle)
}

export function analyzeImage(file, endpoint = 'analyze-image') {
  const form = new FormData()
  form.append('file', file)
  return fetch(`${BASE}/api/v1/${endpoint}`, { method: 'POST', body: form }).then(handle)
}

export function getHealth() {
  return fetch(`${BASE}/health`).then(handle)
}
