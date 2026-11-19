import type { DriverSeasonProfile } from '../types'

/** Verified season profile for one driver, computed from OpenF1 results. */
export default function DriverProfile({ profile }: { profile: DriverSeasonProfile }) {
  const { driver, stats } = profile
  const history = profile.history.slice(-8)

  const cards = [
    { label: 'RACES', value: stats.races },
    { label: 'WINS', value: stats.wins },
    { label: 'PODIUMS', value: stats.podiums },
    { label: 'POLES', value: stats.poles },
    { label: 'DNF', value: stats.dnf },
    { label: 'POINTS', value: stats.points.toFixed(1) },
    { label: 'BEST FINISH', value: stats.best_finish ?? '—' },
    { label: 'AVG FINISH', value: stats.average_finish ?? '—' },
  ]

  return (
    <div className="driver-profile" style={{ borderTopColor: driver.team_colour }}>
      <div className="driver-profile__head">
        {driver.headshot_url && (
          <img className="driver-profile__photo" src={driver.headshot_url} alt="" />
        )}
        <div>
          <p className="eyebrow">CHAMPIONSHIP POSITION {String(stats.position).padStart(2, '0')}</p>
          <h4>
            {driver.first_name} <span>{driver.last_name}</span>
          </h4>
          <p className="muted">
            #{driver.number} · {driver.code} · {driver.team}
          </p>
        </div>
      </div>

      <div className="driver-profile__stats">
        {cards.map((card) => (
          <div key={card.label}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </div>
        ))}
      </div>

      <div className="driver-profile__history">
        <p className="eyebrow">RECENT RACE HISTORY</p>
        {history.length ? (
          history.map((item) => (
            <div className="history-row" key={`${item.meeting_name}-${item.date}`}>
              <span className="history-row__name">{item.meeting_name}</span>
              <span className="muted">
                {new Date(item.date).toLocaleDateString('en-GB', {
                  day: '2-digit',
                  month: 'short',
                })}
              </span>
              <span className={`status status--${item.status}`}>{item.status}</span>
              <strong>P{item.finish}</strong>
              <span className="muted">{item.points.toFixed(0)} pts</span>
            </div>
          ))
        ) : (
          <p className="muted">No completed races yet.</p>
        )}
      </div>
    </div>
  )
}
