# LECLERC LABS

**Race intelligence from real Formula 1 data.**

Leclerc Labs is a beginner-friendly full-stack analytics project. It combines a
React dashboard with a FastAPI service that reads public race data from
[OpenF1](https://openf1.org/). No invented statistics are shown as real.
This is an independent personal project and is not affiliated with Formula 1 or
any driver.

Current UI version badge: **v0.9**.

## What it does

- Pick a season, Grand Prix and session (Practice, Qualifying or Race).
- View the qualifying leaderboard with Q1/Q2/Q3 times and gaps.
- View race classification with grid position, finish status and position change.
- Browse championship standings and per-driver season profiles.
- Compare any two drivers head to head, round by round.
- Plot lap pace from recorded OpenF1 lap times.
- Inspect recorded car telemetry for a chosen driver and lap: speed, throttle,
  brake, gear, RPM and DRS.
- Show recorded tyre stints on a strategy timeline — nothing is estimated.

## Tech stack

| Layer | Choice | Why |
| --- | --- | --- |
| Frontend | React 18 + TypeScript + Vite | Fast dev server and type safety |
| Styling | Plain CSS with CSS variables | No UI framework to learn |
| Charts | Hand-written SVG | No chart dependency |
| Backend | FastAPI + Pydantic | Clear JSON APIs and validation |
| HTTP client | httpx | Calls OpenF1 from Python |
| Config | python-dotenv | Optional `.env` overrides |
| Tests | pytest | Pure-rule and endpoint tests |
| Data | OpenF1 only | Free, public, no API key |

There is no database, no Redux, no user accounts and no live timing feed.
All data comes from OpenF1 through our backend.

## Project structure

```text
leclerc-labs/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # HTTP endpoints
│   │   ├── analytics/             # Pure rules: metrics, laps, stints, comparison
│   │   ├── schemas/               # Pydantic response shapes
│   │   ├── services/              # OpenF1 client, caching, season aggregation
│   │   ├── config.py              # Environment settings
│   │   └── main.py                # FastAPI app
│   ├── tests/                     # pytest suite
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/            # Dashboard, HeadToHead, LapChart, TelemetryPanel
    │   ├── services/api.ts        # Every /api call lives here
    │   ├── types/                 # Shared TypeScript response types
    │   └── index.css              # Stealth-gold design tokens
    ├── vite.config.ts             # Proxies /api to port 8000
    └── package.json
```

`frontend/src/data/sample.ts` contains clearly labelled demo values used while
building the UI in early stages. It is not imported by the running app; the
dashboard uses real backend responses.

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- Internet access to OpenF1

## Run locally

### 1. Backend (port 8000)

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```

On macOS/Linux, activate with `source .venv/bin/activate` instead.

API docs: <http://localhost:8000/docs>  
Health check: <http://localhost:8000/api/health>

### 2. Frontend (port 5173)

In a second terminal, from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite forwards `/api` requests to FastAPI, so no
CORS or URL configuration is needed in development.

### Stopping the servers

Press `Ctrl+C` in each terminal. Restart the backend after changing Python
route files; otherwise an older process may keep serving stale routes.

## Optional configuration

The backend reads these environment variables (a `backend/.env` file works too):

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENF1_BASE_URL` | `https://api.openf1.org/v1` | OpenF1 endpoint |
| `OPENF1_TIMEOUT_SECONDS` | `10` | Per-request timeout |
| `OPENF1_BATCH_PAUSE_SECONDS` | `2.1` | Pause between season calls |
| `CACHE_TTL_SEASONS_SECONDS` | `3600` | Season list cache |
| `CACHE_TTL_RESULTS_SECONDS` | `86400` | Session result cache |
| `CACHE_TTL_STANDINGS_SECONDS` | `3600` | Standings cache |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Allowed CORS origin |

For a deployed frontend, set `VITE_API_BASE_URL` to the deployed backend URL.
Locally it falls back to `/api`.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/health` | Service status |
| GET | `/api/seasons` | Available years and meeting counts |
| GET | `/api/meetings?year=2025` | Meetings for a season |
| GET | `/api/sessions?meeting_key=1254` | Sessions in a meeting |
| GET | `/api/sessions/{key}/results?session_type=Race` | Race classification |
| GET | `/api/sessions/{key}/qualifying` | Qualifying leaderboard |
| GET | `/api/sessions/{key}/laps?drivers=4&drivers=1` | Recorded lap times |
| GET | `/api/sessions/{key}/stints?drivers=4&drivers=1` | Recorded tyre stints |
| GET | `/api/sessions/{key}/telemetry?driver=4&lap=10` | Recorded car telemetry for one lap |
| GET | `/api/standings?year=2025` | Championship standings |
| GET | `/api/drivers/{number}/season?year=2025` | Driver season profile |
| GET | `/api/compare?year=2025&a=4&b=1` | Driver head-to-head |

OpenF1 rate limits are respected with caching, pacing and HTTP 429 handling.
A 429 from OpenF1 becomes a `503` from our API with a retry message. The first
`/api/standings?year=2025` call can take about 50 seconds because it gathers one
round at a time; later calls are cached. OpenF1 provides historical data from
2023 onward, and future events may have no results yet.

## Data and metric rules

- **Source:** OpenF1 only. Every real-data panel is labelled `OPENF1`.
- **Position change:** `grid position − finish position`. Positive means gained places.
- **Retirements:** `DNF`, `DNS` and `DSQ` are kept separate from finishing positions.
- **Qualifying:** OpenF1 may return Q1/Q2/Q3 times as a list; the best is shown as the headline lap.
- **Season stats:** Sprint and Sprint Qualifying sessions are excluded from Grand Prix standings.
- **Head to head:** a finisher beats a non-finisher; two non-finishers tie; otherwise the lower position wins. Qualifying wins require positions for both drivers.
- **Lap chart:** laps without a valid `lap_duration` are skipped; pit-out laps are excluded from fastest-lap selection.
- **Telemetry:** car data is recorded by OpenF1 at roughly 3.7 Hz. The backend keeps at most 120 evenly spaced points for the chart, but summary values use every recorded sample from the lap.
- **Telemetry summary:** full-throttle percentage counts samples at 95% throttle or more; brake events count transitions from released to pressed; DRS percentage counts OpenF1 DRS codes 1, 10, 12 and 14.
- **Strategy:** compounds and lap ranges are exactly what OpenF1 recorded. No pit stops are guessed.
- **No DPI/talent score:** any such metric would be an estimate, so it is not presented as fact.

## Verify the project

Backend tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

Expected: `48 passed`.

Frontend type-check and production build:

```powershell
cd frontend
npm run build
```

`npm run typecheck` runs only the TypeScript check. With both servers running,
open the app and the API docs to confirm the dashboard and endpoints respond.

## Roadmap ideas (not built yet)

- Database cache so restarts do not clear warm data
- Driver DNA-style analysis; a single talent score would be subjective, so it is not built
- Optional deployment and version control once explicitly requested
