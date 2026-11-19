import type { QualifyingRow } from '../types'

/** One driver's row in the qualifying / best-lap leaderboard. */
export default function LeaderboardRow({ row }: { row: QualifyingRow }) {
  const { position, driver, best_lap, gap, q1, q2, q3 } = row
  const phases = [q1, q2, q3].filter(Boolean).join('  ·  ')

  return (
    <div className="lb-row">
      <span className={`lb-row__pos ${position === 1 ? 'lb-row__pos--pole' : ''}`}>
        {String(position).padStart(2, '0')}
      </span>

      <span className="lb-row__stripe" style={{ backgroundColor: driver.team_colour }} />

      <div className="lb-row__driver">
        <strong>{driver.code}</strong>
        <span>
          {driver.first_name} {driver.last_name}
        </span>
      </div>

      <span className="lb-row__team">{driver.team}</span>
      <span className="lb-row__time">{best_lap ?? '—'}</span>
      <span className="lb-row__gap" title={phases || undefined}>
        {gap ?? '—'}
      </span>
    </div>
  )
}
