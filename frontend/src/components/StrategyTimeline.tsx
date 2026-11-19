import type { StintsResponse } from '../types'

interface Props {
  data: StintsResponse
}

const COMPOUNDS: Record<string, { label: string; colour: string; light?: boolean }> = {
  SOFT: { label: 'S', colour: '#e2483d' },
  MEDIUM: { label: 'M', colour: '#e0b552', light: true },
  HARD: { label: 'H', colour: '#e8e6e1', light: true },
  INTERMEDIATE: { label: 'I', colour: '#43a86b' },
  WET: { label: 'W', colour: '#3b82f6' },
}

function compound(value: string) {
  return COMPOUNDS[value] ?? { label: '?', colour: '#6b7076' }
}

/** Real tyre stints from OpenF1 — no pit strategy is guessed. */
export default function StrategyTimeline({ data }: Props) {
  const maxLap = Math.max(1, data.max_lap)
  const usedCompounds = Array.from(
    new Set(data.drivers.flatMap((entry) => entry.stints.map((stint) => stint.compound))),
  )

  return (
    <div className="strategy">
      <div className="strategy__legend">
        {usedCompounds.map((value) => {
          const info = compound(value)
          return (
            <span key={value}>
              <i style={{ background: info.colour }} />
              {value}
            </span>
          )
        })}
      </div>

      <div className="strategy__axis">
        <span>LAP 1</span>
        <span>LAP {Math.round(maxLap / 2)}</span>
        <span>LAP {maxLap}</span>
      </div>

      {data.drivers.map((entry) => (
        <div className="strategy-row" key={entry.driver.number}>
          <div className="strategy-row__driver">
            <i style={{ background: entry.driver.team_colour }} />
            {entry.driver.code}
          </div>
          <div className="strategy-row__track">
            {entry.stints.map((stint) => {
              const info = compound(stint.compound)
              const left = ((stint.lap_start - 1) / maxLap) * 100
              const width = ((stint.lap_end - stint.lap_start + 1) / maxLap) * 100
              return (
                <div
                  key={stint.stint_number}
                  className={`strategy-stint ${info.light ? 'strategy-stint--light' : ''}`}
                  style={{ left: `${left}%`, width: `${width}%`, background: info.colour }}
                  title={`${stint.compound} · laps ${stint.lap_start}–${stint.lap_end} · age ${stint.tyre_age_at_start ?? '—'}`}
                >
                  {width > 6 ? info.label : ''}
                </div>
              )
            })}
          </div>
          <span className="strategy-row__count">{entry.stints.length} stints</span>
        </div>
      ))}

      <p className="muted strategy__note">{data.note}</p>
    </div>
  )
}
