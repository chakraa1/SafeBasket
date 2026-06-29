import { useEffect, useState } from 'react'
import { analyzeImage, analyzeText, getHealth } from './api.js'
import ResultCard from './components/ResultCard.jsx'

const TABS = [
  { id: 'brand', label: 'Brand / Ingredients' },
  { id: 'label', label: 'Label Photo' },
  { id: 'cart', label: 'Cart Screenshot' },
]

const EXAMPLES = ['Maggi Masala', 'Kurkure', 'Thums Up', 'White bread', 'Amul Taaza']

export default function App() {
  const [tab, setTab] = useState('brand')
  const [brand, setBrand] = useState('')
  const [ingredients, setIngredients] = useState('')
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [health, setHealth] = useState(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null))
  }, [])

  function reset() {
    setError('')
    setResult(null)
    setCart(null)
  }

  async function runText() {
    if (!brand && !ingredients) {
      setError('Enter a brand name or paste an ingredients list.')
      return
    }
    reset()
    setLoading(true)
    try {
      const data = await analyzeText({ brand: brand || null, ingredients_text: ingredients || null })
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function runImage(endpoint, isCart) {
    if (!file) {
      setError('Choose an image first.')
      return
    }
    reset()
    setLoading(true)
    try {
      const data = await analyzeImage(file, endpoint)
      if (isCart) setCart(data)
      else setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <nav className="nav">
          <div className="brand">
            <span className="logo">SB</span>
            <span>SafeBasket</span>
          </div>
          <div className="nav__status">
            {health ? (
              <span className="dot dot--ok" title={`embeddings: ${health.embeddings}`}>
                API live · {health.ingredients_indexed} additives indexed
              </span>
            ) : (
              <span className="dot dot--off">API offline</span>
            )}
          </div>
        </nav>
        <div className="hero__inner">
          <span className="kicker">Food-safety intelligence for India</span>
          <h1>
            Know what&apos;s really in <span className="grad">your basket</span>
          </h1>
          <p className="lede">
            SafeBasket scans Indian packaged foods and your online shopping cart, highlights
            harmful and carcinogenic additives using global regulatory databases, and recommends
            cleaner swaps. Free for shoppers, API for businesses.
          </p>
          <div className="hero__tags">
            <span>RASFF</span>
            <span>FDA CFSAN</span>
            <span>FSSAI</span>
            <span>Singapore SFA</span>
            <span>Hong Kong CFS</span>
            <span>IARC / WHO</span>
          </div>
        </div>
      </header>

      <main className="container">
        <div className="card panel">
          <div className="tabs">
            {TABS.map((t) => (
              <button
                key={t.id}
                className={`tab ${tab === t.id ? 'tab--active' : ''}`}
                onClick={() => {
                  setTab(t.id)
                  reset()
                }}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === 'brand' && (
            <div className="form">
              <label>Brand or product</label>
              <input
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                placeholder="e.g. Maggi Masala, Kurkure, Thums Up"
                onKeyDown={(e) => e.key === 'Enter' && runText()}
              />
              <div className="chips">
                {EXAMPLES.map((ex) => (
                  <button key={ex} className="chip" onClick={() => setBrand(ex)}>
                    {ex}
                  </button>
                ))}
              </div>
              <label>Or paste the ingredients section</label>
              <textarea
                rows={4}
                value={ingredients}
                onChange={(e) => setIngredients(e.target.value)}
                placeholder="Refined wheat flour (maida), palm oil, salt, monosodium glutamate (E621)..."
              />
              <button className="cta" onClick={runText} disabled={loading}>
                {loading ? 'Analysing…' : 'Analyse'}
              </button>
            </div>
          )}

          {tab === 'label' && (
            <div className="form">
              <label>Photo of the ingredients label</label>
              <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
              <p className="muted">We read the label text on the server (OCR) and analyse it.</p>
              <button className="cta" onClick={() => runImage('analyze-image', false)} disabled={loading}>
                {loading ? 'Reading label…' : 'Scan label'}
              </button>
            </div>
          )}

          {tab === 'cart' && (
            <div className="form">
              <label>Shopping-cart screenshot (Blinkit, Zepto, BigBasket, Amazon…)</label>
              <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
              <p className="muted">
                We detect items in the screenshot and flag those with harmful additives.
              </p>
              <button className="cta" onClick={() => runImage('analyze-cart', true)} disabled={loading}>
                {loading ? 'Scanning cart…' : 'Scan cart'}
              </button>
            </div>
          )}

          {error && <div className="error">{error}</div>}
        </div>

        {result && <ResultCard result={result} />}

        {cart && (
          <div className="cart-results">
            <div className="card cart-summary">
              <h3>{cart.overall_summary}</h3>
              <p className="muted">{cart.items.length} item(s) recognised · {cart.total_flagged} flags</p>
            </div>
            {cart.items.map((item, i) => (
              <div key={i} className="cart-item">
                <div className="cart-item__label">
                  <span className="muted">detected:</span> {item.detected_text}
                  {item.matched_product && <> → <strong>{item.matched_product}</strong></>}
                </div>
                <ResultCard result={item.analysis} />
              </div>
            ))}
          </div>
        )}
      </main>

      <section className="container modes">
        <div className="card mode">
          <h3>Free for shoppers</h3>
          <p>Scan any product or cart from the website at no cost. No login required.</p>
        </div>
        <div className="card mode">
          <h3>API for businesses</h3>
          <p>
            The same agent is available as a commercial REST API. Send an <code>X-API-Key</code>{' '}
            header for the metered tier. Explore <a href="/docs">/docs</a>.
          </p>
        </div>
        <div className="card mode">
          <h3>FSSAI-aligned</h3>
          <p>
            Built for Indian markets. We surface public regulatory information and note that
            additives may be permitted within FSSAI limits — never a claim that a product is unsafe.
          </p>
        </div>
      </section>

      <footer className="footer">
        SafeBasket · Educational food-safety information from public regulatory databases · Not medical advice
      </footer>
    </div>
  )
}
