import type { DriverLaps, LapsResponse, LapPoint, StandingRow } from '../types'
import { formatLapTime } from '../utils/format'

interface Props {
  data: LapsResponse
  available: StandingRow[]
  selected: number[]
  onToggle: (number: number) => void
}

const WIDTH = 900
const HEIGHT = 300
const LEFT = 68
const RIGHT = 18
const TOP = 18
const BOTTOM = 38

function colour(value: string): string {
  return value.startsWith('#') ? value : `#${value}`
}

/** A small dependency-free SVG chart: lap number on X, lap time on Y. */
export default function LapChart({ data, available, selected, onToggle }: Props) {
  const allLaps: LapPoint[] = data.drivers.flatMap((entry) => entry.laps)
  if (allLaps.length === 0) {
    return <p className="muted">No lap times were recorded for this session.</p>
  }

  const maxLap = Math.max(1, ...allLaps.map((lap) => lap.lap_number))
  const times = allLaps.map((lap) => lap.duration)
  const fastest = Math.min(...times)
  const slowest = Math.max(...times)
  const low = fastest - 1
  const high = slowest + 1
  const plotWidth = WIDTH - LEFT - RIGHT
  const plotHeight = HEIGHT - TOP - BOTTOM

  // Faster lap times are drawn higher up, so the axis is intentionally inverted.
  const x = (lap: number) => LEFT + ((lap - 1) / Math.max(1, maxLap - 1)) * plotWidth
  const y = (duration: number) => TOP + ((duration - low) / Math.max(0.001, high - low)) * plotHeight

  const gridValues = Array.from({ length: 5 }, (_, index) => low + ((high - low) * index) / 4)
  const xTicks = Array.from({ length: 5 }, (_, index) =>
    Math.round(1 + ((maxLap - 1) * index) / 4),
  )

  const addable = available.filter((row) => !selected.includes(row.driver.number))

  return (
    <div className="lap-chart">
      <div className="lap-chart__controls">
        {data.drivers.map((entry: DriverLaps) => (
          <button
            type="button"
            key={entry.driver.number}
            className="lap-chip"
            style={{ borderColor: colour(entry.driver.team_colour) }}
            disabled={selected.length === 1 && selected.includes(entry.driver.number)}
            onClick={() => onToggle(entry.driver.number)}
            title="Click to remove from chart"
          >
            <span style={{ background: colour(entry.driver.team_colour) }} />
            {entry.driver.code}
            <small>{formatLapTime(entry.fastest_lap?.duration)}</small>
          </button>
        ))}
        <label className="lap-chart__add">
          <span>ADD DRIVER</span>
          <select
            aria-label="Add driver to lap chart"
            value=""
            onChange={(event) => {
              const number = Number(event.target.value)
              if (number) onToggle(number)
            }}
          >
            <option value="">Select…</option>
            {addable.map((row) => (
              <option key={row.driver.number} value={row.driver.number}>
                {row.driver.code} · {row.points.toFixed(0)} pts
              </option>
            ))}
          </select>
        </label>
      </div>

      <svg
        className="lap-chart__svg"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label="Lap time chart. Faster laps are higher."
      >
        {gridValues.map((value) => (
          <g key={value}>
            <line
              x1={LEFT}
              x2={WIDTH - RIGHT}
              y1={y(value)}
              y2={y(value)}
              className="lap-chart__grid"
            />
            <text x={LEFT - 10} y={y(value) + 4} textAnchor="end" className="lap-chart__label">
              {formatLapTime(value)}
            </text>
          </g>
        ))}

        {xTicks.map((lap) => (
          <text
            key={lap}
            x={x(lap)}
            y={HEIGHT - 12}
            textAnchor="middle"
            className="lap-chart__label"
          >
            L{lap}
          </text>
        ))}

        {data.drivers.map((entry) => {
          const stroke = colour(entry.driver.team_colour)
          return (
            <g key={entry.driver.number}>
              <polyline
                points={entry.laps
                  .map((lap) => `${x(lap.lap_number)},${y(lap.duration)}`)
                  .join(' ')}
                fill="none"
                stroke={stroke}
                strokeWidth="2.4"
                strokeLinejoin="round"
              />
              {entry.laps
                .filter((lap) => lap.is_pit_out_lap)
                .map((lap) => (
                  <circle
                    key={`pit-${lap.lap_number}`}
                    cx={x(lap.lap_number)}
                    cy={y(lap.duration)}
                    r="3.6"
                    fill="var(--panel)"
                    stroke={stroke}
                    strokeWidth="1.6"
                  >
                    <title>{`L${lap.lap_number} · ${formatLapTime(lap.duration)} · pit out`}</title>
                  </circle>
                ))}
              {entry.fastest_lap && (
                <circle
                  cx={x(entry.fastest_lap.lap_number)}
                  cy={y(entry.fastest_lap.duration)}
                  r="5"
                  fill={stroke}
                >
                  <title>{`${entry.driver.code} fastest · ${formatLapTime(entry.fastest_lap.duration)}`}</title>
                </circle>
              )}
            </g>
          )
        })}
      </svg>

      <p className="muted lap-chart__note">{data.note}</p>
    </div>
  )
}
