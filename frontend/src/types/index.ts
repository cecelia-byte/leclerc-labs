/** Stage 1 demo-only shape. Kept for sample.ts; no longer used by the UI. */
export interface DemoDriver {
  /** OpenF1 identifies drivers by their race number, e.g. 1, 44, 63. */
  number: number
  /** Three-letter display code, e.g. VER. */
  code: string
  firstName: string
  lastName: string
  team: string
  /** Hex colour without the leading #, as supplied by OpenF1. */
  teamColour: string
}

/** Stage 1 demo-only shape. Kept for sample.ts; no longer used by the UI. */
export interface DemoQualifyingRow {
  position: number
  driver: DemoDriver
  bestLap: string
  gap: string
}

/** A headline statistic on the dashboard. */
export interface StatCardData {
  label: string
  value: string
  hint: string
}

/* ---------- API responses (mirrors backend/schemas) ---------- */

export interface Season {
  year: number
  meeting_count: number
}

export interface SeasonsResponse {
  seasons: Season[]
  source: string
}

export interface Meeting {
  meeting_key: number
  year: number
  name: string
  official_name: string
  location: string
  country_name: string
  country_code: string
  country_flag: string | null
  circuit_short_name: string
  circuit_image: string | null
  date_start: string
  date_end: string
}

export interface MeetingsResponse {
  meetings: Meeting[]
  year: number
  source: string
}

export interface Session {
  session_key: number
  meeting_key: number
  session_name: string
  session_type: string
  date_start: string
  date_end: string
}

export interface SessionsResponse {
  sessions: Session[]
  meeting_key: number
  source: string
}

/* ---------- Results and qualifying ---------- */

export interface DriverInfo {
  number: number
  code: string
  first_name: string
  last_name: string
  team: string
  /** Already includes the leading # so it can be used directly in CSS. */
  team_colour: string
  headshot_url: string | null
}

export interface ResultRow {
  position: number
  driver: DriverInfo
  status: string
  time: string | null
  gap: string | null
  laps: number | null
  grid_position: number | null
  position_change: number | null
}

export interface ResultsResponse {
  session_key: number
  rows: ResultRow[]
  source: string
}

export interface QualifyingRow {
  position: number
  driver: DriverInfo
  best_lap: string | null
  gap: string | null
  q1: string | null
  q2: string | null
  q3: string | null
}

export interface QualifyingResponse {
  session_key: number
  rows: QualifyingRow[]
  source: string
}

/* ---------- Season standings and driver profiles ---------- */

export interface StandingRow {
  position: number
  driver: DriverInfo
  races: number
  wins: number
  podiums: number
  poles: number
  dnf: number
  dns: number
  dsq: number
  points: number
  best_finish: number | null
  average_finish: number | null
  best_qualifying: number | null
}

export interface StandingsResponse {
  year: number
  rows: StandingRow[]
  source: string
  note: string
}

export interface RaceHistoryItem {
  round: number
  meeting_name: string
  date: string
  finish: number
  status: string
  points: number
  qualifying_position: number | null
}

export interface DriverSeasonProfile {
  year: number
  driver: DriverInfo
  stats: StandingRow
  history: RaceHistoryItem[]
}

/* ---------- Head-to-head comparison ---------- */

export interface ComparisonMetric {
  label: string
  a: number
  b: number
  winner: string
  higher_is_better: boolean
}

export interface ComparisonRound {
  round: number
  meeting_name: string
  date: string
  a_finish: number | null
  a_status: string
  a_points: number
  a_qualifying: number | null
  b_finish: number | null
  b_status: string
  b_points: number
  b_qualifying: number | null
  finish_winner: string
  qualifying_winner: string
}

export interface ComparisonResponse {
  year: number
  driver_a: DriverInfo
  driver_b: DriverInfo
  metrics: ComparisonMetric[]
  rounds: ComparisonRound[]
  source: string
  note: string
}

/* ---------- Lap telemetry ---------- */

export interface LapPoint {
  lap_number: number
  duration: number
  sector_1: number | null
  sector_2: number | null
  sector_3: number | null
  speed_trap: number | null
  is_pit_out_lap: boolean
}

export interface DriverLaps {
  driver: DriverInfo
  laps: LapPoint[]
  fastest_lap: LapPoint | null
}

export interface LapsResponse {
  session_key: number
  drivers: DriverLaps[]
  source: string
  note: string
}

export interface Stint {
  stint_number: number
  compound: string
  lap_start: number
  lap_end: number
  tyre_age_at_start: number | null
}

export interface DriverStints {
  driver: DriverInfo
  stints: Stint[]
}

export interface StintsResponse {
  session_key: number
  drivers: DriverStints[]
  max_lap: number
  source: string
  note: string
}

/* ---------- Car telemetry ---------- */

export interface TelemetryPoint {
  t_ms: number
  speed: number
  throttle: number | null
  brake: number | null
  gear: number | null
  rpm: number | null
  drs: number | null
}

export interface TelemetrySummary {
  top_speed: number
  average_speed: number
  full_throttle_pct: number
  brake_events: number
  max_rpm: number | null
  drs_pct: number
}

export interface TelemetryResponse {
  session_key: number
  driver: DriverInfo
  lap_number: number
  points: TelemetryPoint[]
  summary: TelemetrySummary
  raw_samples: number
  source: string
  note: string
}
