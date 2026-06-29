import ScoreRing from './ScoreRing.jsx'

const RATING_LABEL = {
  clean: 'Looks clean',
  caution: 'Consume in moderation',
  high_risk: 'High risk',
}

function IngredientRow({ item }) {
  return (
    <div className={`ingredient sev-${item.severity}`}>
      <div className="ingredient__head">
        <span className="ingredient__name">
          {item.name}
          {item.code ? <span className="ingredient__code">{item.code}</span> : null}
        </span>
        <span className="badges">
          {item.carcinogen && <span className="badge badge--carc">carcinogen flag</span>}
          <span className={`badge badge--${item.severity}`}>{item.severity}</span>
        </span>
      </div>
      <p className="ingredient__concern">{item.concern}</p>
      <div className="ingredient__reg">
        {item.regulatory.map((r) => (
          <span key={r.authority} className="reg-chip" title={r.note}>
            {r.authority}
          </span>
        ))}
      </div>
      <p className="ingredient__advice">{item.advice}</p>
    </div>
  )
}

export default function ResultCard({ result }) {
  return (
    <div className={`result-card rating-${result.rating}`}>
      <div className="result-card__top">
        <ScoreRing score={result.safety_score} rating={result.rating} />
        <div className="result-card__headline">
          <span className={`pill pill--${result.rating}`}>{RATING_LABEL[result.rating]}</span>
          <h3>{result.summary}</h3>
          <p className="muted">{result.input_summary}</p>
          <div className="meta-row">
            <span className="meta">engine: {result.engine}</span>
            {result.carcinogen_count > 0 && (
              <span className="meta meta--warn">
                {result.carcinogen_count} carcinogen flag(s)
              </span>
            )}
          </div>
        </div>
      </div>

      {result.flagged.length > 0 && (
        <div className="section">
          <h4>Flagged ingredients ({result.flagged.length})</h4>
          {result.flagged.map((item) => (
            <IngredientRow key={item.name} item={item} />
          ))}
        </div>
      )}

      {result.recommendations.length > 0 && (
        <div className="section">
          <h4>Safer alternatives</h4>
          <div className="recos">
            {result.recommendations.map((r) => (
              <div key={r.id} className="reco">
                <strong>{r.name}</strong>
                <span className="muted">{r.brand}</span>
                <p>{r.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.web_research.length > 0 && (
        <div className="section">
          <h4>Web research</h4>
          <ul className="research">
            {result.web_research.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      <p className="disclaimer">{result.disclaimer}</p>
    </div>
  )
}
