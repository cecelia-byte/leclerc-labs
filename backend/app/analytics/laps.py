"""Pure helpers for turning raw OpenF1 lap rows into chart-friendly points."""

from collections import defaultdict
from typing import Any


def _number(value: Any) -> float | None:
    """OpenF1 sometimes sends null or a string instead of a number."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        result = float(value)
    except ValueError:
        return None
    return result if result > 0 else None


def normalise_lap(row: dict[str, Any]) -> dict[str, Any] | None:
    """Keep only laps we can actually put on a chart."""
    lap_number = row.get("lap_number")
    duration = _number(row.get("lap_duration"))
    if not isinstance(lap_number, int) or lap_number < 1 or duration is None:
        return None

    speed = row.get("st_speed")
    return {
        "lap_number": lap_number,
        "duration": duration,
        "sector_1": _number(row.get("duration_sector_1")),
        "sector_2": _number(row.get("duration_sector_2")),
        "sector_3": _number(row.get("duration_sector_3")),
        "speed_trap": int(speed) if isinstance(speed, (int, float)) else None,
        "is_pit_out_lap": bool(row.get("is_pit_out_lap")),
    }


def group_by_driver(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    """Group raw rows by driver number, ignoring unusable entries."""
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        number = row.get("driver_number")
        lap = normalise_lap(row)
        if isinstance(number, int) and lap is not None:
            grouped[number].append(lap)

    for laps in grouped.values():
        laps.sort(key=lambda item: item["lap_number"])
    return dict(grouped)


def fastest_lap(laps: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Fastest non-pit-out lap. Pit-out laps are not representative pace."""
    candidates = [
        lap for lap in laps if not lap["is_pit_out_lap"] and lap["duration"] is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item["duration"])
