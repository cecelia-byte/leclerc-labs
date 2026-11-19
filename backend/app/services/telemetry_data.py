"""Build one driver's recorded telemetry for one lap."""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException

from app.analytics.telemetry import downsample, group_samples, summarise, to_points
from app.schemas.results import DriverInfo
from app.schemas.telemetry import TelemetryResponse, TelemetrySummary
from app.services.driver_rows import to_driver_info
from app.services.openf1 import client


def _utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _query_date(value: datetime) -> str:
    """OpenF1 date filters expect a UTC timestamp without the +00:00 suffix."""
    return value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


def _lap_window(
    raw_laps: list[dict[str, Any]],
    driver_number: int,
    lap_number: int,
) -> tuple[datetime, datetime] | None:
    lap_rows = [
        row
        for row in raw_laps
        if row.get("driver_number") == driver_number
        and row.get("lap_number") == lap_number
    ]
    if not lap_rows:
        return None

    row = lap_rows[-1]
    start = _utc(row.get("date_start"))
    if start is None:
        return None

    next_rows = [
        item
        for item in raw_laps
        if item.get("driver_number") == driver_number
        and item.get("lap_number") == lap_number + 1
    ]
    end = _utc(next_rows[0].get("date_start")) if next_rows else None
    if end is None or end <= start:
        duration = row.get("lap_duration")
        seconds = float(duration) if isinstance(duration, (int, float)) else 120.0
        end = start + timedelta(seconds=seconds if seconds > 0 else 120.0)

    return start, end


def _fallback_driver(number: int) -> DriverInfo:
    return DriverInfo(
        number=number,
        code=str(number),
        first_name="",
        last_name=f"Driver {number}",
        team="",
        team_colour="#9A948A",
        headshot_url=None,
    )


def get_telemetry(
    session_key: int,
    driver_number: int,
    lap_number: int,
) -> TelemetryResponse:
    raw_laps = client.get_laps(session_key)
    window = _lap_window(raw_laps, driver_number, lap_number)
    if window is None:
        raise HTTPException(
            status_code=404,
            detail="No recorded lap found for this driver",
        )

    start, end = window
    raw_samples = client.get_car_data(
        session_key,
        driver_number,
        _query_date(start),
        _query_date(end),
    )
    samples = group_samples(raw_samples)
    if not samples:
        raise HTTPException(
            status_code=404,
            detail="No car data recorded for this lap",
        )

    driver_rows = client.get_drivers(session_key)
    driver = next(
        (
            found
            for item in driver_rows
            if (found := to_driver_info(item)) is not None
            and found.number == driver_number
        ),
        None,
    ) or _fallback_driver(driver_number)

    return TelemetryResponse(
        session_key=session_key,
        driver=driver,
        lap_number=lap_number,
        points=to_points(downsample(samples)),
        summary=TelemetrySummary(**summarise(samples)),
        raw_samples=len(samples),
    )
