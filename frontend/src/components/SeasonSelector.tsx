import type { Season } from '../types'

interface Props {
  seasons: Season[]
  value: number | null
  onChange: (year: number) => void
}

/** Native select: keyboard-friendly and accessible by default. */
export default function SeasonSelector({ seasons, value, onChange }: Props) {
  return (
    <select
      className="field__control"
      value={value ?? ''}
      onChange={(event) => onChange(Number(event.target.value))}
      aria-label="Season"
    >
      <option value="" disabled>
        Select season
      </option>
      {seasons.map((season) => (
        <option key={season.year} value={season.year}>
          {season.year} · {season.meeting_count} meetings
        </option>
      ))}
    </select>
  )
}
