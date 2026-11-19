"""Build lap telemetry from the shared OpenF1 client and cached session data."""

from fastapi import HTTPException

from app.analytics.laps import fastest_lap, group_by_driver
from app.analytics.stints import group_stints_by_driver
from app.schemas.results import DriverInfo
from app.schemas.telemetry import (
    DriverLaps,
    DriverStints,
    LapPoint,
    LapsResponse,
    Stint,
    StintsResponse,
)
from app.services.driver_rows import to_driver_info
from app.services.openf1 import client

DEFAULT_DRIVER_COUNT = 5


def _fallback_driver(number: int) -> DriverInfo:
    """Keep a driver on the chart even if OpenF1 omits their metadata."""
    return DriverInfo(
        number=number,
        code=str(number),
        first_name="",
        last_name=f"Driver {number}",
        team="",
        team_colour="#9A948A",
        headshot_url=None,
    )


def get_lap_telemetry(
    session_key: int,
    driver_numbers: list[int] | None = None,
) -> LapsResponse:
    raw_laps = client.get_laps(session_key)
    grouped = group_by_driver(raw_laps)
    if not grouped:
        raise HTTPException(status_code=404, detail="No lap data for this session")

    distinct = list(dict.fromkeys(driver_numbers or []))
    if distinct:
        selected = [number for number in distinct if number in grouped]
    else:
        # Most laps is a fair default when the caller has not chosen drivers.
        selected = sorted(
            grouped,
            key=lambda number: len(grouped[number]),
            reverse=True,
        )[:DEFAULT_DRIVER_COUNT]

    if not selected:
        raise HTTPException(status_code=404, detail="No lap data for these drivers")

    driver_rows = client.get_drivers(session_key)
    drivers: dict[int, DriverInfo] = {}
    for item in driver_rows:
        driver = to_driver_info(item)
        if driver is not None:
            drivers[driver.number] = driver

    entries: list[DriverLaps] = []
    for number in selected:
        laps = grouped[number]
        points = [LapPoint(**lap) for lap in laps]
        best = fastest_lap(laps)
        entries.append(
            DriverLaps(
                driver=drivers.get(number) or _fallback_driver(number),
                laps=points,
                fastest_lap=LapPoint(**best) if best is not None else None,
            )
        )

    return LapsResponse(session_key=session_key, drivers=entries)


def get_stint_data(
    session_key: int,
    driver_numbers: list[int] | None = None,
) -> StintsResponse:
    raw_stints = client.get_stints(session_key)
    grouped = group_stints_by_driver(raw_stints)
    if not grouped:
        raise HTTPException(status_code=404, detail="No tyre stints for this session")

    distinct = list(dict.fromkeys(driver_numbers or []))
    selected = [number for number in distinct if number in grouped] if distinct else list(grouped)
    if not selected:
        raise HTTPException(status_code=404, detail="No tyre stints for these drivers")

    driver_rows = client.get_drivers(session_key)
    drivers: dict[int, DriverInfo] = {}
    for item in driver_rows:
        driver = to_driver_info(item)
        if driver is not None:
            drivers[driver.number] = driver

    entries = [
        DriverStints(
            driver=drivers.get(number) or _fallback_driver(number),
            stints=[Stint(**stint) for stint in grouped[number]],
        )
        for number in selected
    ]
    max_lap = max(
        (stint["lap_end"] for stints in grouped.values() for stint in stints),
        default=0,
    )
    return StintsResponse(session_key=session_key, drivers=entries, max_lap=max_lap)
