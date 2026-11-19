import type { DriverInfo } from '../types'

/** Reusable driver summary card, ready for real OpenF1 driver records. */
export default function DriverCard({ driver }: { driver: DriverInfo }) {
  return (
    <article className="driver-card" style={{ borderTopColor: driver.team_colour }}>
      <span className="driver-card__number">#{driver.number}</span>
      <span className="driver-card__code">{driver.code}</span>
      <p className="driver-card__name">
        {driver.first_name} {driver.last_name}
      </p>
      <p className="driver-card__team">{driver.team}</p>
    </article>
  )
}
