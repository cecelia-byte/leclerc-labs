import type { Session } from '../types'

interface Props {
  sessions: Session[]
  value: number | null
  onChange: (sessionKey: number) => void
}

export default function SessionTabs({ sessions, value, onChange }: Props) {
  return (
    <div className="tabs" role="tablist" aria-label="Sessions">
      {sessions.map((session) => (
        <button
          key={session.session_key}
          type="button"
          role="tab"
          aria-selected={session.session_key === value}
          className={`tab ${session.session_key === value ? 'tab--active' : ''}`}
          onClick={() => onChange(session.session_key)}
        >
          {session.session_name}
        </button>
      ))}
    </div>
  )
}
