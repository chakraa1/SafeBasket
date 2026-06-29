// Circular safety-score gauge (0-100). Colour shifts with the rating.
export default function ScoreRing({ score, rating }) {
  const radius = 52
  const circ = 2 * Math.PI * radius
  const offset = circ - (score / 100) * circ
  const color =
    rating === 'clean' ? '#1faa59' : rating === 'caution' ? '#e0a800' : '#e23b3b'

  return (
    <div className="score-ring">
      <svg width="130" height="130" viewBox="0 0 130 130">
        <circle cx="65" cy="65" r={radius} className="ring-bg" />
        <circle
          cx="65"
          cy="65"
          r={radius}
          className="ring-fg"
          style={{
            stroke: color,
            strokeDasharray: circ,
            strokeDashoffset: offset,
          }}
        />
      </svg>
      <div className="score-ring__label">
        <span className="score-ring__num" style={{ color }}>
          {score}
        </span>
        <span className="score-ring__max">/100</span>
      </div>
    </div>
  )
}
