"""HTTP endpoints. No data logic lives here — that is in services/ and analytics/."""

from collections import Counter
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.analytics.formatting import format_gap, format_time
from app.analytics.metrics import position_change, qualifying_times, status_from_flags
from app.schemas.meetings import (
    Meeting,
    MeetingsResponse,
    Session,
    SessionsResponse,
)
from app.schemas.results import (
    DriverInfo,
    QualifyingResponse,
    QualifyingRow,
    ResultsResponse,
    ResultRow,
)
from app.schemas.season import ComparisonResponse, DriverSeasonProfile, StandingsResponse
from app.schemas.seasons import Season, SeasonsResponse
from app.schemas.telemetry import LapsResponse, StintsResponse, TelemetryResponse
from app.services import lap_data, season_stats, telemetry_data
from app.services.driver_rows import to_driver_info as _to_driver
from app.services.openf1 import client

router = APIRouter()


def _to_meeting(item: dict[str, Any]) -> Meeting | None:
    """OpenF1 rows can be incomplete; skip anything we cannot display."""
    meeting_key = item.get("meeting_key")
    year = item.get("year")
    if meeting_key is None or year is None:
        return None

    return Meeting(
        meeting_key=meeting_key,
        year=year,
        name=item.get("meeting_name") or "",
        official_name=item.get("meeting_official_name") or "",
        location=item.get("location") or "",
        country_name=item.get("country_name") or "",
        country_code=item.get("country_code") or "",
        country_flag=item.get("country_flag"),
        circuit_short_name=item.get("circuit_short_name") or "",
        circuit_image=item.get("circuit_image"),
        date_start=item.get("date_start") or "",
        date_end=item.get("date_end") or "",
    )


def _to_session(item: dict[str, Any]) -> Session | None:
    session_key = item.get("session_key")
    meeting_key = item.get("meeting_key")
    if session_key is None or meeting_key is None:
        return None

    return Session(
        session_key=session_key,
        meeting_key=meeting_key,
        session_name=item.get("session_name") or "",
        session_type=item.get("session_type") or "",
        date_start=item.get("date_start") or "",
        date_end=item.get("date_end") or "",
    )


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "leclerc-labs-api"}


@router.get("/api/seasons", response_model=SeasonsResponse)
def get_seasons() -> SeasonsResponse:
    meetings = client.get_meetings()
    counts = Counter(
        meeting["year"]
        for meeting in meetings
        if isinstance(meeting.get("year"), int)
    )
    seasons = [
        Season(year=year, meeting_count=count)
        for year, count in sorted(counts.items(), reverse=True)
    ]
    return SeasonsResponse(seasons=seasons)


@router.get("/api/meetings", response_model=MeetingsResponse)
def get_meetings(year: int = Query(..., ge=2023, le=2100)) -> MeetingsResponse:
    payload = client.get_meetings(year)
    meetings = [
        meeting
        for item in payload
        if not item.get("is_cancelled")
        if (meeting := _to_meeting(item)) is not None
    ]
    return MeetingsResponse(meetings=meetings, year=year)


@router.get("/api/sessions", response_model=SessionsResponse)
def get_sessions(meeting_key: int = Query(..., ge=1)) -> SessionsResponse:
    payload = client.get_sessions(meeting_key)
    sessions = [
        session
        for item in payload
        if not item.get("is_cancelled")
        if (session := _to_session(item)) is not None
    ]
    return SessionsResponse(sessions=sessions, meeting_key=meeting_key)


@router.get("/api/sessions/{session_key}/stints", response_model=StintsResponse)
def get_stints(
    session_key: int,
    drivers: list[int] = Query(default_factory=list),
) -> StintsResponse:
    return lap_data.get_stint_data(session_key, drivers)


@router.get("/api/sessions/{session_key}/laps", response_model=LapsResponse)
def get_laps(
    session_key: int,
    drivers: list[int] = Query(default_factory=list),
) -> LapsResponse:
    return lap_data.get_lap_telemetry(session_key, drivers)


@router.get(
    "/api/sessions/{session_key}/telemetry", response_model=TelemetryResponse
)
def get_telemetry(
    session_key: int,
    driver: int = Query(..., ge=1),
    lap: int = Query(..., ge=1),
) -> TelemetryResponse:
    return telemetry_data.get_telemetry(session_key, driver, lap)


@router.get("/api/sessions/{session_key}/results", response_model=ResultsResponse)
def get_results(session_key: int, session_type: str | None = None) -> ResultsResponse:
    result_rows = client.get_session_result(session_key)
    driver_rows = client.get_drivers(session_key)

    drivers: dict[int, DriverInfo] = {}
    for item in driver_rows:
        driver = _to_driver(item)
        if driver is not None:
            drivers[driver.number] = driver

    # OpenF1 keys the grid by the qualifying session, so find that session
    # from the meeting instead of assuming the race key works.
    grid: dict[int, int] = {}
    if (session_type or "").lower() == "race":
        meeting_key = next(
            (item.get("meeting_key") for item in result_rows if item.get("meeting_key")),
            None,
        )
        qualifying_key = None
        if meeting_key is not None:
            sessions = client.get_sessions(meeting_key)
            for wanted in ("Qualifying", "Sprint Qualifying"):
                qualifying_key = next(
                    (
                        item.get("session_key")
                        for item in sessions
                        if item.get("session_type") == wanted
                    ),
                    None,
                )
                if qualifying_key is not None:
                    break

        if qualifying_key is not None:
            try:
                grid_rows = client.get_starting_grid(qualifying_key)
            except HTTPException:
                # Grid positions are an enrichment, not essential results data.
                grid_rows = []
            for item in grid_rows:
                number = item.get("driver_number")
                position = item.get("position")
                if number is not None and position is not None:
                    grid[number] = position

    rows: list[ResultRow] = []
    for item in result_rows:
        number = item.get("driver_number")
        position = item.get("position")
        driver = drivers.get(number)
        if driver is None or position is None:
            continue

        status = status_from_flags(
            dnf=item.get("dnf"),
            dns=item.get("dns"),
            dsq=item.get("dsq"),
        )
        grid_position = grid.get(number)

        rows.append(
            ResultRow(
                position=position,
                driver=driver,
                status=status,
                time=format_time(item.get("duration")),
                gap=format_gap(item.get("gap_to_leader")),
                laps=item.get("number_of_laps"),
                grid_position=grid_position,
                # Retirements are not given an ordinary position change.
                position_change=position_change(grid_position, position)
                if status == "FINISHED"
                else None,
            )
        )

    rows.sort(key=lambda row: row.position)
    return ResultsResponse(session_key=session_key, rows=rows)


@router.get("/api/sessions/{session_key}/qualifying", response_model=QualifyingResponse)
def get_qualifying(session_key: int) -> QualifyingResponse:
    result_rows = client.get_session_result(session_key)
    driver_rows = client.get_drivers(session_key)

    drivers: dict[int, DriverInfo] = {}
    for item in driver_rows:
        driver = _to_driver(item)
        if driver is not None:
            drivers[driver.number] = driver

    rows: list[QualifyingRow] = []
    for item in result_rows:
        number = item.get("driver_number")
        position = item.get("position")
        driver = drivers.get(number)
        if driver is None or position is None:
            continue

        times = qualifying_times(item.get("duration"))
        gaps = qualifying_times(item.get("gap_to_leader"))
        # 0.0 is a valid gap (pole position), so check for None, not truthiness.
        gap_value = next(
            (
                value
                for value in (gaps["q3"], gaps["q2"], gaps["q1"], gaps["best"])
                if value is not None
            ),
            None,
        )
        status = status_from_flags(
            dnf=item.get("dnf"),
            dns=item.get("dns"),
            dsq=item.get("dsq"),
        )
        if status != "FINISHED":
            continue

        rows.append(
            QualifyingRow(
                position=position,
                driver=driver,
                best_lap=format_time(times["best"]),
                gap=format_gap(gap_value),
                q1=format_time(times["q1"]),
                q2=format_time(times["q2"]),
                q3=format_time(times["q3"]),
            )
        )

    rows.sort(key=lambda row: row.position)
    return QualifyingResponse(session_key=session_key, rows=rows)


@router.get("/api/standings", response_model=StandingsResponse)
def get_standings(year: int = Query(..., ge=2023, le=2100)) -> StandingsResponse:
    return season_stats.get_standings(year)


@router.get(
    "/api/drivers/{driver_number}/season", response_model=DriverSeasonProfile
)
def get_driver_season(
    driver_number: int,
    year: int = Query(..., ge=2023, le=2100),
) -> DriverSeasonProfile:
    return season_stats.get_profile(driver_number, year)


@router.get("/api/compare", response_model=ComparisonResponse)
def compare_drivers(
    year: int = Query(..., ge=2023, le=2100),
    a: int = Query(..., ge=1),
    b: int = Query(..., ge=1),
) -> ComparisonResponse:
    return season_stats.build_comparison(year, a, b)
