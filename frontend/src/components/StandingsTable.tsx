import type { StandingRow } from '../types'

interface Props {
  rows: StandingRow[]
  selectedNumber: number | null
  onSelect: (driverNumber: number) => void
}

/** Championship table. Clicking a driver opens their verified season profile. */
export default function StandingsTable({ rows, selectedNumber, onSelect }: Props) {
  return (
    <div className="standings-table">
      <div className="standings-row standings-row--header">
        <span>POS</span>
        <span>DRIVER</span>
        <span>TEAM</span>
        <span>RACES</span>
        <span>WINS</span>
        <span>PODIUMS</span>
        <span>POLES</span>
        <span>DNF</span>
        <span>PTS</span>
      </div>

      {rows.map((row) => (
        <button
          type="button"
          key={row.driver.number}
          className={`standings-row ${selectedNumber === row.driver.number ? 'standings-row--selected' : ''}`}
          onClick={() => onSelect(row.driver.number)}
          aria-label={`View ${row.driver.code} season profile`}
        >
          <span className="lb-row__pos">{String(row.position).padStart(2, '0')}</span>
          <span className="standings-row__driver">
            <span
              className="team-dot"
              style={{ backgroundColor: row.driver.team_colour }}
            />
            <strong>{row.driver.code}</strong>
          </span>
          <span className="lb-row__team">{row.driver.team}</span>
          <span>{row.races}</span>
          <span className={row.wins ? 'change--up' : 'muted'}>{row.wins}</span>
          <span>{row.podiums}</span>
          <span className={row.poles ? 'change--up' : 'muted'}>{row.poles}</span>
          <span className={row.dnf ? 'change--down' : 'muted'}>{row.dnf}</span>
          <strong className="standings-row__points">{row.points.toFixed(1)}</strong>
        </button>
      ))}
    </div>
  )
}
