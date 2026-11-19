"""Pure helpers for recorded OpenF1 car-data samples.

Car data arrives at roughly 3.7 Hz — tens of thousands of rows per race — so
we keep the summary honest and only downsample the points sent to the chart.
"""

from datetime import datetime, timezone
from typing import Any

MAX_CHART_POINTS = 120
DRS_ON = {1, 10, 12, 14}


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _number(value: Any, *, minimum: float = 0, integer: bool = False) -> float | int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if number < minimum:
        return None
    return int(number) if integer else number


def normalise_sample(row: dict[str, Any]) -> dict[str, Any] | None:
    """Keep samples that have a timestamp and a usable speed value."""
    when = _parse_date(row.get("date"))
    speed = _number(row.get("speed"))
    if when is None or speed is None:
        return None

    return {
        "date": when,
        "speed": int(speed),
        "throttle": _number(row.get("throttle"), integer=True),
        "brake": _number(row.get("brake"), integer=True),
        "gear": _number(row.get("n_gear"), integer=True),
        "rpm": _number(row.get("rpm"), integer=True),
        "drs": _number(row.get("drs"), integer=True),
    }


def group_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalise and sort samples in time order."""
    samples = [sample for row in rows if (sample := normalise_sample(row)) is not None]
    samples.sort(key=lambda item: item["date"])
    return samples


def downsample(
    samples: list[dict[str, Any]],
    max_points: int = MAX_CHART_POINTS,
) -> list[dict[str, Any]]:
    """Keep at most `max_points` evenly spaced samples, including the last."""
    if max_points < 1:
        return []
    if len(samples) <= max_points:
        return list(samples)
    if max_points == 1:
        return [samples[0]]

    indexes = {
        round(index * (len(samples) - 1) / (max_points - 1))
        for index in range(max_points)
    }
    return [samples[index] for index in sorted(indexes)]


def summarise(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive summary numbers directly from the recorded samples."""
    speeds = [sample["speed"] for sample in samples]
    throttles = [
        sample["throttle"] for sample in samples if sample["throttle"] is not None
    ]
    rpms = [sample["rpm"] for sample in samples if sample["rpm"] is not None]
    drs_values = [sample["drs"] for sample in samples if sample["drs"] is not None]

    brake_events = 0
    previous_brake: int | None = None
    for sample in samples:
        brake = sample["brake"]
        if brake is None:
            continue
        if previous_brake == 0 and brake > 0:
            brake_events += 1
        previous_brake = brake

    full_throttle = sum(1 for value in throttles if value >= 95)
    drs_on = sum(1 for value in drs_values if value in DRS_ON)

    return {
        "top_speed": max(speeds),
        "average_speed": round(sum(speeds) / len(speeds), 1),
        "full_throttle_pct": round(100 * full_throttle / len(throttles), 1)
        if throttles
        else 0.0,
        "brake_events": brake_events,
        "max_rpm": max(rpms) if rpms else None,
        "drs_pct": round(100 * drs_on / len(drs_values), 1) if drs_values else 0.0,
    }


def to_points(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert timestamps to milliseconds from the first sample for charting."""
    if not samples:
        return []

    start = samples[0]["date"]
    return [
        {
            "t_ms": int((sample["date"] - start).total_seconds() * 1000),
            "speed": sample["speed"],
            "throttle": sample.get("throttle"),
            "brake": sample.get("brake"),
            "gear": sample.get("gear"),
            "rpm": sample.get("rpm"),
            "drs": sample.get("drs"),
        }
        for sample in samples
    ]
