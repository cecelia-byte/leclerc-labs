import type { TelemetryResponse } from '../types'

interface Props {
  data: TelemetryResponse
}

const WIDTH = 900
const HEIGHT = 280
const LEFT = 58
const RIGHT = 20
const TOP = 20
const BOTTOM = 36

function colour(value: string): string {
  return value.startsWith('#') ? value : `#${value}`
}

function seconds(ms: number): string {
  return `${(ms / 1000).toFixed(1)}s`
}

/** Recorded OpenF1 car data for one lap; the backend downsamples the points. */
export default function TelemetryPanel({ data }: Props) {
  const points = data.points
  if (points.length === 0) {
    return <p className="muted">No car data was recorded for this lap.</p>
  }

  const maxSpeed = Math.max(100, ...points.map((point) => point.speed))
  const maxTime = Math.max(1, points[points.length - 1].t_ms)
  const plotWidth = WIDTH - LEFT - RIGHT
  const plotHeight = HEIGHT - TOP - BOTTOM

  const x = (time: number) => LEFT + (time / maxTime) * plotWidth
  const ySpeed = (speed: number) => TOP + (1 - speed / maxSpeed) * plotHeight
  const yThrottle = (throttle: number) =>
    TOP + (1 - throttle / 100) * plotHeight

  const speedTicks = Array.from({ length: 4 }, (_, index) =>
    Math.round((maxSpeed * index) / 3),
  )
  const timeTicks = Array.from({ length: 5 }, (_, index) => (maxTime * index) / 4)
  const throttlePoints = points.filter((point) => point.throttle !== null)
  const brakePoints = points.filter((point) => (point.brake ?? 0) > 50)

  return (
    <div className="telemetry">
      <div className="telemetry__head">
        <div className="telemetry__driver">
          <i style={{ background: colour(data.driver.team_colour) }} />
          <div>
            <strong>{data.driver.code}</strong>
            <span>
              {data.driver.first_name} {data.driver.last_name} · {data.driver.team}
            </span>
          </div>
        </div>
        <div className="telemetry__lap">
          <span>LAP</span>
          <strong>{data.lap_number}</strong>
          <small>{data.raw_samples} recorded samples</small>
        </div>
      </div>

      <div className="telemetry__legend">
        <span><i className="telemetry__key telemetry__key--speed" />SPEED</span>
        <span><i className="telemetry__key telemetry__key--throttle" />THROTTLE %</span>
        <span><i className="telemetry__key telemetry__key--brake" />BRAKE</span>
      </div>

      <svg
        className="telemetry__svg"
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label={`Recorded telemetry for ${data.driver.code} on lap ${data.lap_number}`}
      >
        {speedTicks.map((value) => (
          <g key={`speed-${value}`}>
            <line
              x1={LEFT}
              x2={WIDTH - RIGHT}
              y1={ySpeed(value)}
              y2={ySpeed(value)}
              className="telemetry__grid"
            />
            <text
              x={LEFT - 10}
              y={ySpeed(value) + 4}
              textAnchor="end"
              className="telemetry__label"
            >
              {value}
            </text>
          </g>
        ))}

        {timeTicks.map((value) => (
          <text
            key={`time-${value}`}
            x={x(value)}
            y={HEIGHT - 12}
            textAnchor="middle"
            className="telemetry__label"
          >
            {seconds(value)}
          </text>
        ))}

        <text x={LEFT} y={TOP - 6} className="telemetry__label">
          KM/H
        </text>

        {throttlePoints.length > 1 && (
          <polyline
            points={throttlePoints
              .map((point) => `${x(point.t_ms)},${yThrottle(point.throttle ?? 0)}`)
              .join(' ')}
            fill="none"
            stroke="rgba(242, 239, 233, 0.38)"
            strokeWidth="1.4"
          />
        )}

        <polyline
          points={points.map((point) => `${x(point.t_ms)},${ySpeed(point.speed)}`).join(' ')}
          fill="none"
          stroke="var(--accent)"
          strokeWidth="2.6"
          strokeLinejoin="round"
        />

        {brakePoints.map((point) => (
          <line
            key={`brake-${point.t_ms}`}
            x1={x(point.t_ms)}
            x2={x(point.t_ms)}
            y1={HEIGHT - BOTTOM}
            y2={HEIGHT - BOTTOM - 12}
            stroke="#e2483d"
            strokeWidth="2"
          />
        ))}
      </svg>

      <div className="telemetry__summary">
        <div><span>TOP SPEED</span><strong>{data.summary.top_speed} km/h</strong></div>
        <div><span>AVERAGE SPEED</span><strong>{data.summary.average_speed} km/h</strong></div>
        <div><span>FULL THROTTLE</span><strong>{data.summary.full_throttle_pct}%</strong></div>
        <div><span>BRAKE EVENTS</span><strong>{data.summary.brake_events}</strong></div>
        <div><span>MAX RPM</span><strong>{data.summary.max_rpm ?? '—'}</strong></div>
        <div><span>DRS ACTIVE</span><strong>{data.summary.drs_pct}%</strong></div>
      </div>

      <p className="muted telemetry__note">{data.note}</p>
    </div>
  )
}
