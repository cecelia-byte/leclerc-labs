import type { ResultRow } from '../types'

function ChangeCell({ value }: { value: number | null }) {
  if (value === null) return <span className="muted">—</span>
  if (value === 0) return <span className="muted">0</span>

  return (
    <span className={value > 0 ? 'change change--up' : 'change change--down'}>
      {value > 0 ? `+${value}` : value}
    </span>
  )
}

/** Race classification with measured grid-to-finish changes. */
export default function ResultsTable({ rows }: { rows: ResultRow[] }) {
  return (
    <div className="results-table">
      <div className="result-row result-row--header">
        <span>POS</span>
        <span>DRIVER</span>
        <span>TEAM</span>
        <span>GRID</span>
        <span>CHANGE</span>
        <span>STATUS</span>
        <span>TIME</span>
        <span>GAP</span>
      </div>

      {rows.map((row) => (
        <div className="result-row" key={row.driver.number}>
          <span
            className={`lb-row__pos ${row.position === 1 ? 'lb-row__pos--pole' : ''}`}
          >
            {String(row.position).padStart(2, '0')}
          </span>

          <div className="lb-row__driver">
            <strong>
              <span
                className="team-dot"
                style={{ backgroundColor: row.driver.team_colour }}
              />
              {row.driver.code}
            </strong>
            <span>
              {row.driver.first_name} {row.driver.last_name}
            </span>
          </div>

          <span className="lb-row__team">{row.driver.team}</span>
          <span>{row.grid_position ?? '—'}</span>
          <ChangeCell value={row.position_change} />
          <span className={`status status--${row.status}`}>{row.status}</span>
          <span className="lb-row__time">{row.time ?? '—'}</span>
          <span className="lb-row__gap">{row.gap ?? '—'}</span>
        </div>
      ))}
    </div>
  )
}
