import type {
  ComparisonResponse,
  DriverSeasonProfile,
  LapsResponse,
  MeetingsResponse,
  QualifyingResponse,
  ResultsResponse,
  SeasonsResponse,
  SessionsResponse,
  StintsResponse,
  StandingsResponse,
  TelemetryResponse,
} from '../types'

/**
 * All backend calls go through here.
 * In dev, `/api` is proxied to http://localhost:8000 by Vite.
 * In production, set VITE_API_BASE_URL to the deployed backend URL.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    signal,
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const body: unknown = await response.json()
      if (
        typeof body === 'object' &&
        body !== null &&
        'detail' in body &&
        typeof body.detail === 'string'
      ) {
        message = body.detail
      }
    } catch {
      // Keep the generic message if the error body was not JSON.
    }
    throw new Error(message)
  }

  return response.json() as Promise<T>
}

export const api = {
  seasons: (signal?: AbortSignal) => request<SeasonsResponse>('/seasons', signal),

  meetings: (year: number, signal?: AbortSignal) =>
    request<MeetingsResponse>(`/meetings?year=${year}`, signal),

  sessions: (meetingKey: number, signal?: AbortSignal) =>
    request<SessionsResponse>(`/sessions?meeting_key=${meetingKey}`, signal),

  results: (sessionKey: number, sessionType: string, signal?: AbortSignal) =>
    request<ResultsResponse>(
      `/sessions/${sessionKey}/results?session_type=${encodeURIComponent(sessionType)}`,
      signal,
    ),

  qualifying: (sessionKey: number, signal?: AbortSignal) =>
    request<QualifyingResponse>(`/sessions/${sessionKey}/qualifying`, signal),

  standings: (year: number, signal?: AbortSignal) =>
    request<StandingsResponse>(`/standings?year=${year}`, signal),

  driverSeason: (driverNumber: number, year: number, signal?: AbortSignal) =>
    request<DriverSeasonProfile>(
      `/drivers/${driverNumber}/season?year=${year}`,
      signal,
    ),

  compare: (a: number, b: number, year: number, signal?: AbortSignal) =>
    request<ComparisonResponse>(`/compare?year=${year}&a=${a}&b=${b}`, signal),

  laps: (
    sessionKey: number,
    drivers: number[],
    signal?: AbortSignal,
  ) => {
    const query = drivers.map((number) => `drivers=${number}`).join('&')
    const suffix = query ? `?${query}` : ''
    return request<LapsResponse>(`/sessions/${sessionKey}/laps${suffix}`, signal)
  },

  stints: (
    sessionKey: number,
    drivers: number[],
    signal?: AbortSignal,
  ) => {
    const query = drivers.map((number) => `drivers=${number}`).join('&')
    const suffix = query ? `?${query}` : ''
    return request<StintsResponse>(`/sessions/${sessionKey}/stints${suffix}`, signal)
  },

  telemetry: (
    sessionKey: number,
    driver: number,
    lap: number,
    signal?: AbortSignal,
  ) =>
    request<TelemetryResponse>(
      `/sessions/${sessionKey}/telemetry?driver=${driver}&lap=${lap}`,
      signal,
    ),
}
