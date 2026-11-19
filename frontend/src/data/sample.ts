import type { DemoDriver, DemoQualifyingRow, StatCardData } from '../types'

/**
 * ============================================================
 * ⚠️  DEMO DATA — INVENTED VALUES FOR UI DEVELOPMENT ONLY
 * ============================================================
 * Nothing in this file is real Formula 1 data.
 * Every screen that renders these values MUST show a DEMO DATA badge.
 * Stage 4 replaced this file with responses from our FastAPI backend.
 */
export const DEMO_SEASON = 2025

export const demoDrivers: DemoDriver[] = [
  {
    number: 1,
    code: 'VER',
    firstName: 'Max',
    lastName: 'Verstappen',
    team: 'Red Bull Racing',
    teamColour: '#3671C6',
  },
  {
    number: 63,
    code: 'RUS',
    firstName: 'George',
    lastName: 'Russell',
    team: 'Mercedes',
    teamColour: '#27F4D2',
  },
  {
    number: 4,
    code: 'NOR',
    firstName: 'Lando',
    lastName: 'Norris',
    team: 'McLaren',
    teamColour: '#FF8000',
  },
  {
    number: 16,
    code: 'LEC',
    firstName: 'Charles',
    lastName: 'Leclerc',
    team: 'Ferrari',
    teamColour: '#E80020',
  },
]

export const demoQualifying: DemoQualifyingRow[] = [
  { position: 1, driver: demoDrivers[0], bestLap: '1:29.431', gap: '—' },
  { position: 2, driver: demoDrivers[2], bestLap: '1:29.512', gap: '+0.081' },
  { position: 3, driver: demoDrivers[1], bestLap: '1:29.688', gap: '+0.257' },
  { position: 4, driver: demoDrivers[3], bestLap: '1:29.934', gap: '+0.503' },
]

export const demoStats: StatCardData[] = [
  {
    label: 'POLES',
    value: '--',
    hint: 'Connect verified session data to populate this metric.',
  },
  {
    label: 'PODIUMS',
    value: '--',
    hint: 'Connect verified session data to populate this metric.',
  },
  {
    label: 'RACES',
    value: '--',
    hint: 'Connect verified session data to populate this metric.',
  },
]
