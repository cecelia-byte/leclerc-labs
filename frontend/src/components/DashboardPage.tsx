import { useEffect, useState } from 'react'

import { api } from '../services/api'
import { useApi } from '../hooks/useApi'
import type { StatCardData } from '../types'
import SeasonSelector from './SeasonSelector'
import MeetingSelector from './MeetingSelector'
import SessionTabs from './SessionTabs'
import StatCard from './StatCard'
import LeaderboardRow from './LeaderboardRow'
import ResultsTable from './ResultsTable'
import StandingsTable from './StandingsTable'
import DriverProfile from './DriverProfile'
import HeadToHead from './HeadToHead'
import LapChart from './LapChart'
import StrategyTimeline from './StrategyTimeline'
import TelemetryPanel from './TelemetryPanel'
import { EmptyState, ErrorState, LoadingState } from './AsyncState'

/** Main dashboard: filters first, then real data panels. */
export default function DashboardPage() {
  const seasonsQuery = useApi(api.seasons, [])

  const [year, setYear] = useState<number | null>(null)
  const [meetingKey, setMeetingKey] = useState<number | null>(null)
  const [sessionKey, setSessionKey] = useState<number | null>(null)
  const [selectedDriver, setSelectedDriver] = useState<number | null>(null)
  const [driverA, setDriverA] = useState<number | null>(null)
  const [driverB, setDriverB] = useState<number | null>(null)
  const [lapDrivers, setLapDrivers] = useState<number[]>([])
  const [telemetryDriver, setTelemetryDriver] = useState<number | null>(null)
  const [telemetryLap, setTelemetryLap] = useState<number | null>(null)

  const meetingsQuery = useApi(
    (signal) => api.meetings(year ?? 0, signal),
    [year],
    year !== null,
  )

  const sessionsQuery = useApi(
    (signal) => api.sessions(meetingKey ?? 0, signal),
    [meetingKey],
    meetingKey !== null,
  )

  const preliminarySession = (sessionsQuery.data?.sessions ?? []).find(
    (item) => item.session_key === sessionKey,
  )
  const isRaceSession = preliminarySession?.session_type === 'Race'

  const resultsQuery = useApi(
    (signal) =>
      api.results(sessionKey ?? 0, preliminarySession?.session_type ?? '', signal),
    [sessionKey, preliminarySession?.session_type],
    sessionKey !== null && isRaceSession,
  )

  const qualifyingQuery = useApi(
    (signal) => api.qualifying(sessionKey ?? 0, signal),
    [sessionKey],
    sessionKey !== null && !isRaceSession,
  )

  const standingsQuery = useApi(
    (signal) => api.standings(year ?? 0, signal),
    [year],
    year !== null,
  )

  const profileQuery = useApi(
    (signal) => api.driverSeason(selectedDriver ?? 0, year ?? 0, signal),
    [selectedDriver, year],
    selectedDriver !== null && year !== null,
  )

  const compareQuery = useApi(
    (signal) => api.compare(driverA ?? 0, driverB ?? 0, year ?? 0, signal),
    [driverA, driverB, year],
    driverA !== null &&
      driverB !== null &&
      driverA !== driverB &&
      year !== null,
  )

  const lapsQuery = useApi(
    (signal) => api.laps(sessionKey ?? 0, lapDrivers, signal),
    [sessionKey, lapDrivers.join(',')],
    sessionKey !== null && lapDrivers.length > 0,
  )

  const stintsQuery = useApi(
    (signal) => api.stints(sessionKey ?? 0, lapDrivers, signal),
    [sessionKey, lapDrivers.join(',')],
    sessionKey !== null && lapDrivers.length > 0,
  )

  const telemetryQuery = useApi(
    (signal) =>
      api.telemetry(
        sessionKey ?? 0,
        telemetryDriver ?? 0,
        telemetryLap ?? 0,
        signal,
      ),
    [sessionKey, telemetryDriver, telemetryLap],
    sessionKey !== null && telemetryDriver !== null && telemetryLap !== null,
  )

  // Pick sensible defaults so the page is useful immediately.
  useEffect(() => {
    if (year || !seasonsQuery.data?.seasons.length) return
    const preferred = seasonsQuery.data.seasons.find((item) => item.year === 2025)
    setYear(preferred?.year ?? seasonsQuery.data.seasons[0].year)
  }, [seasonsQuery.data, year])

  useEffect(() => {
    if (
      !year ||
      meetingKey ||
      !meetingsQuery.data?.meetings.length ||
      meetingsQuery.data.year !== year
    ) {
      return
    }
    const grandPrix = meetingsQuery.data.meetings.find((item) =>
      item.name.includes('Grand Prix'),
    )
    setMeetingKey(grandPrix?.meeting_key ?? meetingsQuery.data.meetings[0].meeting_key)
  }, [meetingsQuery.data, meetingKey, year])

  useEffect(() => {
    if (
      !meetingKey ||
      sessionKey ||
      !sessionsQuery.data?.sessions.length ||
      sessionsQuery.data.meeting_key !== meetingKey
    ) {
      return
    }
    const qualifying = sessionsQuery.data.sessions.find(
      (item) => item.session_type === 'Qualifying',
    )
    setSessionKey(qualifying?.session_key ?? sessionsQuery.data.sessions[0].session_key)
  }, [sessionsQuery.data, sessionKey, meetingKey])

  useEffect(() => {
    const rows = standingsQuery.data?.rows ?? []
    if (!rows.length) return
    if (selectedDriver && rows.some((row) => row.driver.number === selectedDriver)) return
    setSelectedDriver(rows[0].driver.number)
  }, [standingsQuery.data, selectedDriver])

  useEffect(() => {
    const rows = standingsQuery.data?.rows ?? []
    if (rows.length < 2) return

    if (!driverA || !rows.some((row) => row.driver.number === driverA)) {
      setDriverA(rows[0].driver.number)
    }
    if (
      !driverB ||
      !rows.some((row) => row.driver.number === driverB) ||
      driverB === driverA
    ) {
      const alternative = rows.find((row) => row.driver.number !== driverA)
      setDriverB(alternative?.driver.number ?? rows[1].driver.number)
    }
  }, [standingsQuery.data, driverA, driverB])

  useEffect(() => {
    const rows = standingsQuery.data?.rows ?? []
    if (!rows.length) return
    setLapDrivers((current) => {
      const stillValid =
        current.length > 0 &&
        current.every((number) => rows.some((row) => row.driver.number === number))
      return stillValid ? current : rows.slice(0, 3).map((row) => row.driver.number)
    })
  }, [standingsQuery.data])

  useEffect(() => {
    const drivers = lapsQuery.data?.drivers ?? []
    if (!drivers.length) return
    if (
      telemetryDriver !== null &&
      drivers.some((entry) => entry.driver.number === telemetryDriver)
    ) {
      return
    }
    const preferred =
      drivers.find((entry) => entry.driver.number === lapDrivers[0]) ?? drivers[0]
    setTelemetryDriver(preferred.driver.number)
  }, [lapsQuery.data, lapDrivers, telemetryDriver])

  useEffect(() => {
    if (telemetryDriver === null) return
    const entry = lapsQuery.data?.drivers.find(
      (item) => item.driver.number === telemetryDriver,
    )
    if (!entry || !entry.laps.length) return
    if (
      telemetryLap !== null &&
      entry.laps.some((lap) => lap.lap_number === telemetryLap)
    ) {
      return
    }
    setTelemetryLap(
      entry.fastest_lap?.lap_number ?? entry.laps[0].lap_number,
    )
  }, [lapsQuery.data, telemetryDriver, telemetryLap])

  const meetings = meetingsQuery.data?.meetings ?? []
  const sessions = sessionsQuery.data?.sessions ?? []
  const selectedMeeting = meetings.find((item) => item.meeting_key === meetingKey)
  const selectedSession = sessions.find((item) => item.session_key === sessionKey)
  const raceCount = meetings.filter((item) => item.name.includes('Grand Prix')).length
  const telemetryEntry = lapsQuery.data?.drivers.find(
    (entry) => entry.driver.number === telemetryDriver,
  )
  const telemetryLaps = telemetryEntry?.laps ?? []

  const standingsRows = standingsQuery.data?.rows ?? []
  const totalPoles = standingsRows.reduce((sum, row) => sum + row.poles, 0)
  const totalPodiums = standingsRows.reduce((sum, row) => sum + row.podiums, 0)

  const stats: StatCardData[] = [
    {
      label: 'POLES',
      value: standingsRows.length ? String(totalPoles).padStart(2, '0') : '--',
      hint: `Poles awarded in ${year ?? 'the selected season'} from verified qualifying.`,
    },
    {
      label: 'PODIUMS',
      value: standingsRows.length ? String(totalPodiums).padStart(2, '0') : '--',
      hint: `Top-three finishes in ${year ?? 'the selected season'} from verified results.`,
    },
    {
      label: 'RACES',
      value: year ? String(raceCount).padStart(2, '0') : '--',
      hint: `Grand Prix weekends in ${year ?? 'the selected season'} from OpenF1.`,
    },
  ]

  const handleYearChange = (next: number) => {
    setYear(next)
    setMeetingKey(null)
    setSessionKey(null)
    setSelectedDriver(null)
    setDriverA(null)
    setDriverB(null)
    setLapDrivers([])
    setTelemetryDriver(null)
    setTelemetryLap(null)
  }

  const handleMeetingChange = (next: number) => {
    setMeetingKey(next)
    setSessionKey(null)
    setTelemetryDriver(null)
    setTelemetryLap(null)
  }

  const handleSessionChange = (next: number) => {
    setSessionKey(next)
    setTelemetryDriver(null)
    setTelemetryLap(null)
  }

  const handleTelemetryDriverChange = (next: number) => {
    setTelemetryDriver(next)
    setTelemetryLap(null)
  }

  const handleDriverAChange = (next: number) => {
    setDriverA(next)
    if (next === driverB) {
      const alternative = standingsRows.find((row) => row.driver.number !== next)
      setDriverB(alternative?.driver.number ?? null)
    }
  }

  const handleDriverBChange = (next: number) => {
    setDriverB(next)
    if (next === driverA) {
      const alternative = standingsRows.find((row) => row.driver.number !== next)
      setDriverA(alternative?.driver.number ?? null)
    }
  }

  const handleLapToggle = (number: number) => {
    setLapDrivers((current) => {
      if (current.includes(number)) {
        return current.length > 1 ? current.filter((item) => item !== number) : current
      }
      // Three lines is the readable maximum, so replace the oldest selection.
      return current.length >= 3 ? [...current.slice(1), number] : [...current, number]
    })
  }

  return (
    <main className="dashboard">
      <section className="hero">
        <div className="hero__content">
          <p className="eyebrow">LECLERC LABS · REAL DATA</p>
          <h2>EVERY LAP TELLS A STORY.</h2>
          <p>Explore the pace. Decode the strategy. Understand the driver.</p>
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>SESSION SELECTOR</h3>
          <span>SOURCE · OPENF1 VIA OUR API</span>
        </div>

        <div className="panel filter-bar">
          <label className="field">
            <span>SEASON</span>
            {seasonsQuery.loading && <LoadingState label="Loading seasons" />}
            {seasonsQuery.error && (
              <ErrorState message={seasonsQuery.error} onRetry={seasonsQuery.refetch} />
            )}
            {seasonsQuery.data && (
              <SeasonSelector
                seasons={seasonsQuery.data.seasons}
                value={year}
                onChange={handleYearChange}
              />
            )}
          </label>

          <label className="field">
            <span>GRAND PRIX</span>
            {!year && <span className="field__hint">Choose a season first</span>}
            {year && meetingsQuery.loading && <LoadingState label="Loading meetings" />}
            {year && meetingsQuery.error && (
              <ErrorState message={meetingsQuery.error} onRetry={meetingsQuery.refetch} />
            )}
            {year && meetingsQuery.data && (
              <MeetingSelector
                meetings={meetings}
                value={meetingKey}
                onChange={handleMeetingChange}
              />
            )}
          </label>

          <div className="field">
            <span>SESSION</span>
            {!meetingKey && <span className="field__hint">Choose a Grand Prix first</span>}
            {meetingKey && sessionsQuery.loading && <LoadingState label="Loading sessions" />}
            {meetingKey && sessionsQuery.error && (
              <ErrorState message={sessionsQuery.error} onRetry={sessionsQuery.refetch} />
            )}
            {meetingKey && sessionsQuery.data && (
              <SessionTabs
                sessions={sessions}
                value={sessionKey}
                onChange={handleSessionChange}
              />
            )}
          </div>
        </div>

        {selectedMeeting && (
          <div className="panel meeting-summary">
            <div>
              <p className="eyebrow">SELECTED EVENT</p>
              <h4>{selectedMeeting.official_name || selectedMeeting.name}</h4>
              <p className="muted">
                {selectedMeeting.circuit_short_name} · {selectedMeeting.location} ·{' '}
                {selectedMeeting.country_name}
              </p>
            </div>
            <div className="meeting-summary__meta">
              <span>SESSION</span>
              <strong>{selectedSession?.session_name ?? '—'}</strong>
            </div>
          </div>
        )}
      </section>

      <section className="section">
        <div className="section__head">
          <h3>LAP PACE</h3>
          <span>ONE OPENF1 CALL · {selectedSession?.session_name ?? 'NO SESSION'}</span>
        </div>

        <div className="panel">
          {!sessionKey ? (
            <EmptyState
              title="Choose a session"
              message="Select a Grand Prix and session to see lap-by-lap pace."
            />
          ) : lapsQuery.loading ? (
            <LoadingState label="Loading lap telemetry" />
          ) : lapsQuery.error ? (
            <ErrorState message={lapsQuery.error} onRetry={lapsQuery.refetch} />
          ) : lapsQuery.data ? (
            <LapChart
              data={lapsQuery.data}
              available={standingsRows}
              selected={lapDrivers}
              onToggle={handleLapToggle}
            />
          ) : (
            <EmptyState title="No laps" message="This session has no recorded lap times." />
          )}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>CAR TELEMETRY</h3>
          <span>RECORDED BY OPENF1 · DOWNSAMPLED</span>
        </div>

        <div className="panel">
          {!sessionKey ? (
            <EmptyState
              title="Choose a session"
              message="Select a Grand Prix and session to see car telemetry."
            />
          ) : !lapsQuery.data ? (
            lapsQuery.loading ? (
              <LoadingState label="Loading telemetry" />
            ) : lapsQuery.error ? (
              <ErrorState message={lapsQuery.error} onRetry={lapsQuery.refetch} />
            ) : (
              <EmptyState title="No laps" message="This session has no recorded laps." />
            )
          ) : !telemetryEntry ? (
            <EmptyState
              title="Choose a driver"
              message="Pick a driver with recorded laps in this session."
            />
          ) : (
            <div className="telemetry-panel">
              <div className="telemetry-controls">
                <label className="field">
                  <span>DRIVER</span>
                  <select
                    className="field__control"
                    value={telemetryDriver ?? ''}
                    onChange={(event) => {
                      const number = Number(event.target.value)
                      if (number) handleTelemetryDriverChange(number)
                    }}
                  >
                    {lapsQuery.data.drivers.map((entry) => (
                      <option key={entry.driver.number} value={entry.driver.number}>
                        {entry.driver.code} · {entry.driver.team}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>LAP</span>
                  <select
                    className="field__control"
                    value={telemetryLap ?? ''}
                    onChange={(event) => {
                      const number = Number(event.target.value)
                      if (number) setTelemetryLap(number)
                    }}
                  >
                    {telemetryLaps.map((lap) => (
                      <option key={lap.lap_number} value={lap.lap_number}>
                        Lap {lap.lap_number}
                        {lap.is_pit_out_lap ? ' · pit out' : ''}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {telemetryQuery.loading ? (
                <LoadingState label="Loading car telemetry" />
              ) : telemetryQuery.error ? (
                <ErrorState
                  message={telemetryQuery.error}
                  onRetry={telemetryQuery.refetch}
                />
              ) : telemetryQuery.data ? (
                <TelemetryPanel data={telemetryQuery.data} />
              ) : (
                <EmptyState
                  title="No telemetry"
                  message="No car data was recorded for this lap."
                />
              )}
            </div>
          )}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>TYRE STINTS</h3>
          <span>RECORDED BY OPENF1 · NOT ESTIMATED</span>
        </div>

        <div className="panel">
          {!sessionKey ? (
            <EmptyState
              title="Choose a session"
              message="Select a Grand Prix and session to see tyre stints."
            />
          ) : stintsQuery.loading ? (
            <LoadingState label="Loading tyre stints" />
          ) : stintsQuery.error ? (
            <ErrorState message={stintsQuery.error} onRetry={stintsQuery.refetch} />
          ) : stintsQuery.data ? (
            <StrategyTimeline data={stintsQuery.data} />
          ) : (
            <EmptyState title="No stints" message="This session has no tyre stint records." />
          )}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>CHAMPIONSHIP OVERVIEW</h3>
          <span>VERIFIED DATA ONLY</span>
        </div>
        <div className="stat-grid">
          {stats.map((stat) => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>{isRaceSession ? 'RACE CLASSIFICATION' : 'QUALIFYING LEADERBOARD'}</h3>
          <span>VERIFIED OPENF1 DATA</span>
        </div>

        <div className="panel">
          {!selectedSession ? (
            <EmptyState
              title="No session selected"
              message="Choose a season, Grand Prix and session above."
            />
          ) : isRaceSession ? (
            resultsQuery.loading ? (
              <LoadingState label="Loading race results" />
            ) : resultsQuery.error ? (
              <ErrorState message={resultsQuery.error} onRetry={resultsQuery.refetch} />
            ) : resultsQuery.data?.rows.length ? (
              <ResultsTable rows={resultsQuery.data.rows} />
            ) : (
              <EmptyState
                title="No race results available"
                message="This event may not have been run yet."
              />
            )
          ) : qualifyingQuery.loading ? (
            <LoadingState label="Loading qualifying leaderboard" />
          ) : qualifyingQuery.error ? (
            <ErrorState message={qualifyingQuery.error} onRetry={qualifyingQuery.refetch} />
          ) : qualifyingQuery.data?.rows.length ? (
            <div className="leaderboard">
              <div className="lb-row lb-row--header">
                <span>POS</span>
                <span />
                <span>DRIVER</span>
                <span>TEAM</span>
                <span>BEST LAP</span>
                <span>GAP</span>
              </div>
              {qualifyingQuery.data.rows.map((row) => (
                <LeaderboardRow key={row.driver.number} row={row} />
              ))}
            </div>
          ) : (
            <EmptyState
              title="No qualifying data available"
              message="This session may not have been run yet."
            />
          )}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>SEASON STANDINGS</h3>
          <span>VERIFIED RESULTS · {year ?? '—'}</span>
        </div>

        <div className="panel">
          {standingsQuery.loading ? (
            <LoadingState label="Aggregating season results — first load can take a minute" />
          ) : standingsQuery.error ? (
            <ErrorState message={standingsQuery.error} onRetry={standingsQuery.refetch} />
          ) : standingsQuery.data?.rows.length ? (
            <StandingsTable
              rows={standingsQuery.data.rows}
              selectedNumber={selectedDriver}
              onSelect={setSelectedDriver}
            />
          ) : (
            <EmptyState
              title="No standings available"
              message="No completed rounds were found for this season."
            />
          )}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>DRIVER PROFILE</h3>
          <span>VERIFIED OPENF1 DATA</span>
        </div>

        {standingsQuery.data?.rows.length ? (
          <div className="driver-roster">
            {standingsQuery.data.rows.map((row) => (
              <button
                type="button"
                key={row.driver.number}
                className={`driver-chip ${selectedDriver === row.driver.number ? 'driver-chip--active' : ''}`}
                onClick={() => setSelectedDriver(row.driver.number)}
                style={{ borderTopColor: row.driver.team_colour }}
              >
                <span>{row.driver.code}</span>
                <small>{row.points.toFixed(0)} pts</small>
              </button>
            ))}
          </div>
        ) : null}

        <div className="panel">
          {profileQuery.loading ? (
            <LoadingState label="Loading driver profile" />
          ) : profileQuery.error ? (
            <ErrorState message={profileQuery.error} onRetry={profileQuery.refetch} />
          ) : profileQuery.data ? (
            <DriverProfile profile={profileQuery.data} />
          ) : (
            <EmptyState title="No driver selected" message="Choose a driver above." />
          )}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h3>HEAD TO HEAD</h3>
          <span>ROUND-BY-ROUND · VERIFIED DATA</span>
        </div>

        <div className="panel">
          {compareQuery.loading ? (
            <LoadingState label="Building comparison" />
          ) : compareQuery.error ? (
            <ErrorState message={compareQuery.error} onRetry={compareQuery.refetch} />
          ) : compareQuery.data && driverA !== null && driverB !== null ? (
            <HeadToHead
              data={compareQuery.data}
              roster={standingsRows}
              driverA={driverA}
              driverB={driverB}
              onDriverA={handleDriverAChange}
              onDriverB={handleDriverBChange}
            />
          ) : (
            <EmptyState
              title="Choose two drivers"
              message="Head-to-head needs two different drivers from the standings."
            />
          )}
        </div>
      </section>
    </main>
  )
}
