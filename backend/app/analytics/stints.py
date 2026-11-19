"""Pure helpers for raw OpenF1 tyre-stint rows."""

from collections import defaultdict
from typing import Any


def normalise_stint(row: dict[str, Any]) -> dict[str, Any] | None:
    """Keep only stints with a usable compound and lap range."""
    number = row.get("stint_number")
    start = row.get("lap_start")
    end = row.get("lap_end")
    compound = row.get("compound")
    if not all(isinstance(value, int) for value in (number, start, end)):
        return None
    if number < 1 or start < 1 or end < start or not isinstance(compound, str):
        return None

    return {
        "stint_number": number,
        "compound": compound.upper(),
        "lap_start": start,
        "lap_end": end,
        "tyre_age_at_start": row.get("tyre_age_at_start")
        if isinstance(row.get("tyre_age_at_start"), int)
        else None,
    }


def group_stints_by_driver(
    rows: list[dict[str, Any]],
) -> dict[int, list[dict[str, Any]]]:
    """Group and order stints by driver."""
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        number = row.get("driver_number")
        stint = normalise_stint(row)
        if isinstance(number, int) and stint is not None:
            grouped[number].append(stint)

    for stints in grouped.values():
        stints.sort(key=lambda item: item["stint_number"])
    return dict(grouped)
