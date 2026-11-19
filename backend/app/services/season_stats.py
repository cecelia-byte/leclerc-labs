"""Build verified season statistics from one cached call per race weekend."""

import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import HTTPException

from app import config
from app.analytics.comparison import (
    count_wins,
    finish_winner,
    metric_result,
    qualifying_winner,
)
from app.analytics.season import (
    points_of,
    position_of,
    rank_rows,
    status_of,
    summarise_driver,
)
from app.schemas.results import DriverInfo
from app.schemas.season import (
    ComparisonMetric,
    ComparisonResponse,
    ComparisonRound,
    DriverSeasonProfile,
    RaceHistoryItem,
    StandingsResponse,
    StandingRow,
)
from app.services.cache import TTLCache
from app.services.driver_rows import to_driver_info
from app.services.openf1 import client

_season_cache = TTLCache()
_last_request_at = 0.0


def _paced(fn: Callable[..., list[dict]], *args: Any) -> list[dict]:
    """Space out the per-meeting calls so the free-tier limit is respected."""
    global _last_request_at

    pause = config.OPENF1_BATCH_PAUSE_SECONDS
    if pause > 0 and _last_request_at:
        remaining = pause - (time.monotonic() - _last_request_at)
        if remaining > 0:
            time.sleep(remaining)

    result = fn(*args)
    _last_request_at = time.monotonic()
    return result


def _completed(value: str) -> bool:
    """A session with no usable date is treated as not yet completed."""
    if not value:
        return False
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment <= datetime.now(timezone.utc)


def build_season(
    year: int,
) -> tuple[StandingsResponse, dict[int, DriverSeasonProfile]]:
    cached = _season_cache.get(f"season:{year}")
    if cached is not None:
        return cached

    meetings = client.get_meetings(year)
    sessions = _paced(client.get_sessions_by_year, year)

    meeting_by_key = {
        item["meeting_key"]: item
        for item in meetings
        if item.get("meeting_key") is not None
    }

    race_keys: dict[int, set[int]] = defaultdict(set)
    qualifying_keys: dict[int, set[int]] = defaultdict(set)
    race_session_dates: dict[int, str] = {}

    for item in sessions:
        if item.get("is_cancelled"):
            continue
        meeting_key = item.get("meeting_key")
        session_key = item.get("session_key")
        if meeting_key is None or session_key is None:
            continue

        session_type = item.get("session_type")
        session_name = item.get("session_name")

        # Sprint sessions share the Race/Qualifying session_type, so filter by
        # name to keep championship statistics Grand Prix-only.
        if session_type == "Race" and session_name != "Sprint":
            race_keys[meeting_key].add(session_key)
            race_session_dates[meeting_key] = item.get("date_start") or ""
        elif session_type == "Qualifying" and session_name != "Sprint Qualifying":
            qualifying_keys[meeting_key].add(session_key)

    drivers: dict[int, DriverInfo] = {}
    race_rows: dict[int, list[dict]] = defaultdict(list)
    qualifying_rows: dict[int, list[dict]] = defaultdict(list)
    history: dict[int, list[dict]] = defaultdict(list)

    ordered = sorted(
        (m for m in meetings if m.get("meeting_key") in race_keys),
        key=lambda m: m.get("date_start") or "",
    )

    round_number = 0

    for meeting in ordered:
        meeting_key = meeting["meeting_key"]
        date = race_session_dates.get(meeting_key, "")
        if not _completed(date):
            continue

        round_number += 1
        rows = _paced(client.get_session_results_by_meeting, meeting_key)

        # Only fetch driver metadata when this weekend introduces new numbers.
        numbers = {
            row.get("driver_number")
            for row in rows
            if row.get("driver_number") is not None
        }
        if numbers - drivers.keys():
            for item in _paced(client.get_drivers_for_meeting, meeting_key):
                driver = to_driver_info(item)
                if driver is not None:
                    drivers[driver.number] = driver

        meeting_name = (
            meeting.get("meeting_name")
            or meeting.get("meeting_official_name")
            or "Grand Prix"
        )

        qualifying_positions: dict[int, int] = {}
        for row in rows:
            number = row.get("driver_number")
            session_key = row.get("session_key")
            if (
                number is not None
                and session_key in qualifying_keys[meeting_key]
                and status_of(row) == "FINISHED"
            ):
                position = position_of(row)
                if position is not None:
                    qualifying_positions[number] = position

        for row in rows:
            number = row.get("driver_number")
            session_key = row.get("session_key")
            if number is None or session_key is None:
                continue

            if session_key in race_keys[meeting_key]:
                race_rows[number].append(row)
                position = position_of(row)
                if position is not None:
                    history[number].append(
                        {
                            "round": round_number,
                            "meeting_name": meeting_name,
                            "date": date,
                            "finish": position,
                            "status": status_of(row),
                            "points": points_of(row),
                            "qualifying_position": qualifying_positions.get(number),
                        }
                    )
            elif session_key in qualifying_keys[meeting_key]:
                qualifying_rows[number].append(row)

    ranked: list[dict[str, Any]] = []
    for number in sorted(set(race_rows) | set(qualifying_rows)):
        driver = drivers.get(number)
        if driver is None:
            continue
        ranked.append(
            {
                "driver": driver,
                "code": driver.code,
                **summarise_driver(race_rows[number], qualifying_rows[number]),
            }
        )

    ranked = rank_rows(ranked)
    standings = StandingsResponse(
        year=year,
        rows=[StandingRow(**row) for row in ranked],
    )

    profiles: dict[int, DriverSeasonProfile] = {}
    for row in ranked:
        number = row["driver"].number
        full_history = sorted(history[number], key=lambda item: item["round"])
        profiles[number] = DriverSeasonProfile(
            year=year,
            driver=row["driver"],
            stats=StandingRow(**row),
            history=[RaceHistoryItem(**item) for item in full_history],
        )

    result = (standings, profiles)
    _season_cache.set(f"season:{year}", result, config.CACHE_TTL_STANDINGS_SECONDS)
    return result


def build_comparison(
    year: int,
    driver_a: int,
    driver_b: int,
) -> ComparisonResponse:
    if driver_a == driver_b:
        raise HTTPException(status_code=400, detail="Choose two different drivers")

    profiles = build_season(year)[1]
    profile_a = profiles.get(driver_a)
    profile_b = profiles.get(driver_b)
    if profile_a is None or profile_b is None:
        raise HTTPException(status_code=404, detail="Driver not found in this season")

    by_round_a = {item.round: item for item in profile_a.history}
    by_round_b = {item.round: item for item in profile_b.history}

    rounds: list[dict[str, Any]] = []
    for round_number in sorted(set(by_round_a) | set(by_round_b)):
        item_a = by_round_a.get(round_number)
        item_b = by_round_b.get(round_number)

        side_a = {
            "finish": item_a.finish if item_a else None,
            "status": item_a.status if item_a else "DNS",
            "points": item_a.points if item_a else 0.0,
            "qualifying_position": item_a.qualifying_position if item_a else None,
        }
        side_b = {
            "finish": item_b.finish if item_b else None,
            "status": item_b.status if item_b else "DNS",
            "points": item_b.points if item_b else 0.0,
            "qualifying_position": item_b.qualifying_position if item_b else None,
        }
        reference = item_a or item_b

        rounds.append(
            {
                "round": round_number,
                "meeting_name": reference.meeting_name,
                "date": reference.date,
                "a_finish": side_a["finish"],
                "a_status": side_a["status"],
                "a_points": side_a["points"],
                "a_qualifying": side_a["qualifying_position"],
                "b_finish": side_b["finish"],
                "b_status": side_b["status"],
                "b_points": side_b["points"],
                "b_qualifying": side_b["qualifying_position"],
                "finish_winner": finish_winner(side_a, side_b),
                "qualifying_winner": qualifying_winner(side_a, side_b),
            }
        )

    def podiums(history: list[RaceHistoryItem]) -> int:
        return sum(
            1
            for item in history
            if item.status == "FINISHED" and item.finish <= 3
        )

    metrics: list[ComparisonMetric] = [
        ComparisonMetric(
            **metric_result(
                "RACE FINISH WINS",
                count_wins(rounds, "finish_winner", "A"),
                count_wins(rounds, "finish_winner", "B"),
            )
        ),
        ComparisonMetric(
            **metric_result(
                "QUALIFYING WINS",
                count_wins(rounds, "qualifying_winner", "A"),
                count_wins(rounds, "qualifying_winner", "B"),
            )
        ),
        ComparisonMetric(
            **metric_result(
                "POINTS",
                round(sum(item["a_points"] for item in rounds), 1),
                round(sum(item["b_points"] for item in rounds), 1),
            )
        ),
        ComparisonMetric(
            **metric_result("WINS", profile_a.stats.wins, profile_b.stats.wins)
        ),
        ComparisonMetric(
            **metric_result("PODIUMS", podiums(profile_a.history), podiums(profile_b.history))
        ),
        ComparisonMetric(
            **metric_result("DNF", profile_a.stats.dnf, profile_b.stats.dnf, higher_is_better=False)
        ),
    ]

    return ComparisonResponse(
        year=year,
        driver_a=profile_a.driver,
        driver_b=profile_b.driver,
        metrics=metrics,
        rounds=[ComparisonRound(**item) for item in rounds],
    )


def get_standings(year: int) -> StandingsResponse:
    return build_season(year)[0]


def get_profile(driver_number: int, year: int) -> DriverSeasonProfile:
    profile = build_season(year)[1].get(driver_number)
    if profile is None:
        raise HTTPException(status_code=404, detail="Driver not found in this season")
    return profile
