import type { Meeting } from '../types'

interface Props {
  meetings: Meeting[]
  value: number | null
  onChange: (meetingKey: number) => void
}

export default function MeetingSelector({ meetings, value, onChange }: Props) {
  return (
    <select
      className="field__control"
      value={value ?? ''}
      onChange={(event) => onChange(Number(event.target.value))}
      aria-label="Grand Prix"
    >
      <option value="" disabled>
        Select Grand Prix
      </option>
      {meetings.map((meeting) => (
        <option key={meeting.meeting_key} value={meeting.meeting_key}>
          {meeting.name} · {meeting.circuit_short_name}
        </option>
      ))}
    </select>
  )
}
