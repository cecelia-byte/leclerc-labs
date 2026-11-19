"""Counting rules for season statistics. Pure functions — no HTTP here."""

from typing import Any

from app.analytics.metrics import status_from_flags


def status_of(row: dict[str, Any]) -> str:
    return status_from_flags(
        dnf=row.get("dnf"),
        dns=row.get("dns"),
        dsq=row.get("dsq"),
    )


def position_of(row: dict[str, Any]) -> int | None:
    value = row.get("position")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return int(value)


def points_of(row: dict[str, Any]) -> float:
    """OpenF1 supplies points for races; missing values count as zero."""
    value = row.get("points")
    if isinstance(value, bool) or value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def summarise_driver(
    race_rows: list[dict[str, Any]],
    qualifying_rows: list[dict[str, Any]],
) -> dict[str, int | float | None]:
    """Aggregate one driver's season from already-filtered OpenF1 rows."""
    race_positions: list[int] = []
    qualifying_positions: list[int] = []

    wins = 0
    podiums = 0
    dnf = 0
    dns = 0
    dsq = 0

    for row in race_rows:
        status = status_of(row)
        position = position_of(row)

        if status == "DNF":
            dnf += 1
        elif status == "DNS":
            dns += 1
        elif status == "DSQ":
            dsq += 1

        # Retirements are counted separately, never as an ordinary finish.
        if status != "FINISHED" or position is None:
            continue

        race_positions.append(position)
        if position == 1:
            wins += 1
        if position <= 3:
            podiums += 1

    for row in qualifying_rows:
        status = status_of(row)
        position = position_of(row)
        if status == "FINISHED" and position is not None:
            qualifying_positions.append(position)

    return {
        "races": len(race_rows),
        "wins": wins,
        "podiums": podiums,
        "poles": sum(1 for position in qualifying_positions if position == 1),
        "dnf": dnf,
        "dns": dns,
        "dsq": dsq,
        "points": round(sum(points_of(row) for row in race_rows), 1),
        "best_finish": min(race_positions) if race_positions else None,
        "average_finish": (
            round(sum(race_positions) / len(race_positions), 1) if race_positions else None
        ),
        "best_qualifying": min(qualifying_positions) if qualifying_positions else None,
    }


def rank_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add championship positions using points, then race results, then code."""
    ordered = sorted(
        rows,
        key=lambda row: (
            -float(row["points"]),
            -int(row["wins"]),
            -int(row["podiums"]),
            -int(row["poles"]),
            str(row.get("code", "")),
        ),
    )
    for index, row in enumerate(ordered, start=1):
        row["position"] = index
    return ordered
