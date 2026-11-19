import type { ComparisonResponse, StandingRow } from '../types'

interface Props {
  data: ComparisonResponse
  roster: StandingRow[]
  driverA: number
  driverB: number
  onDriverA: (number: number) => void
  onDriverB: (number: number) => void
}

function FinishLabel({ position, status }: { position: number | null; status: string }) {
  if (status !== 'FINISHED') {
    return <span className={`status status--${status}`}>{status}</span>
  }
  return <strong>P{position ?? '—'}</strong>
}

/** Side-by-side season comparison with a points trend for every Grand Prix. */
export default function HeadToHead({
  data,
  roster,
  driverA,
  driverB,
  onDriverA,
  onDriverB,
}: Props) {
  const maxPoints = Math.max(
    1,
    ...data.rounds.flatMap((round) => [round.a_points, round.b_points]),
  )

  return (
    <div className="h2h">
      <div className="h2h__selectors">
        <label>
          <span>DRIVER A</span>
          <select value={driverA} onChange={(event) => onDriverA(Number(event.target.value))}>
            {roster.map((row) => (
              <option key={row.driver.number} value={row.driver.number}>
                {row.driver.code} · {row.points.toFixed(0)} pts
              </option>
            ))}
          </select>
        </label>
        <span className="h2h__versus">VS</span>
        <label>
          <span>DRIVER B</span>
          <select value={driverB} onChange={(event) => onDriverB(Number(event.target.value))}>
            {roster.map((row) => (
              <option key={row.driver.number} value={row.driver.number}>
                {row.driver.code} · {row.points.toFixed(0)} pts
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="h2h__banners">
        <div style={{ borderTopColor: data.driver_a.team_colour }}>
          <span>{data.driver_a.code}</span>
          <strong>
            {data.driver_a.first_name} {data.driver_a.last_name}
          </strong>
          <small>{data.driver_a.team}</small>
        </div>
        <div style={{ borderTopColor: data.driver_b.team_colour }}>
          <span>{data.driver_b.code}</span>
          <strong>
            {data.driver_b.first_name} {data.driver_b.last_name}
          </strong>
          <small>{data.driver_b.team}</small>
        </div>
      </div>

      <div className="h2h__metrics">
        {data.metrics.map((metric) => {
          const total = metric.a + metric.b
          const share = total ? (metric.a / total) * 100 : 50
          return (
            <div className="h2h-metric" key={metric.label}>
              <div className="h2h-metric__head">
                <strong className={metric.winner === 'A' ? 'change--up' : ''}>
                  {Number.isInteger(metric.a) ? metric.a : metric.a.toFixed(1)}
                </strong>
                <span>{metric.label}</span>
                <strong className={metric.winner === 'B' ? 'change--up' : ''}>
                  {Number.isInteger(metric.b) ? metric.b : metric.b.toFixed(1)}
                </strong>
              </div>
              <div className="h2h-metric__bar">
                <span
                  className={`h2h-metric__a ${metric.winner === 'A' ? 'h2h-metric__side--win' : ''}`}
                  style={{ width: `${share}%` }}
                />
                <span
                  className={`h2h-metric__b ${metric.winner === 'B' ? 'h2h-metric__side--win' : ''}`}
                  style={{ width: `${100 - share}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="h2h__rounds">
        <p className="eyebrow">ROUND BY ROUND · {data.year}</p>
        <div className="h2h-round h2h-round--header">
          <span>R</span>
          <span>GRAND PRIX</span>
          <span>{data.driver_a.code} QUALI / RACE</span>
          <span>{data.driver_b.code} QUALI / RACE</span>
          <span>POINTS TREND</span>
        </div>

        {data.rounds.map((round) => (
          <div className="h2h-round" key={round.round}>
            <span className="muted">{String(round.round).padStart(2, '0')}</span>
            <span className="h2h-round__name">{round.meeting_name}</span>
            <span>
              {round.a_qualifying ?? '—'} / <FinishLabel position={round.a_finish} status={round.a_status} />
            </span>
            <span>
              {round.b_qualifying ?? '—'} / <FinishLabel position={round.b_finish} status={round.b_status} />
            </span>
            <span className="h2h-round__trend">
              <span className="h2h-round__bar h2h-round__bar--a" style={{ width: `${(round.a_points / maxPoints) * 100}%` }} />
              <span className="muted">{round.a_points.toFixed(0)}</span>
              <span className="h2h-round__bar h2h-round__bar--b" style={{ width: `${(round.b_points / maxPoints) * 100}%` }} />
              <span className="muted">{round.b_points.toFixed(0)}</span>
            </span>
          </div>
        ))}
      </div>

      <p className="muted h2h__note">{data.note}</p>
    </div>
  )
}
