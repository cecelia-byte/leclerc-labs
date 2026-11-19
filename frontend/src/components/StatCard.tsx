import type { StatCardData } from '../types'

/** One headline metric. Props let us reuse the same design for any stat. */
export default function StatCard({ label, value, hint }: StatCardData) {
  return (
    <article className="stat-card">
      <div className="stat-card__top">
        <span>{label}</span>
        <span
          className={`badge badge--mini ${value === '--' ? '' : 'badge--source'}`}
        >
          {value === '--' ? 'PENDING' : 'OPENF1'}
        </span>
      </div>
      <p className="stat-card__value">{value}</p>
      <p className="stat-card__hint">{hint}</p>
    </article>
  )
}
