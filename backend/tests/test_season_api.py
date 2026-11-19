"""Season endpoints with a tiny fake season — still no network access."""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.season import StandingsResponse
from app.services import season_stats

client = TestClient(app)

PAST_START = "2023-03-01T12:00:00+00:00"
PAST_END = "2023-03-01T14:00:00+00:00"


def _driver(number: int, code: str) -> dict:
    return {
        "driver_number": number,
        "name_acronym": code,
        "first_name": "Test",
        "last_name": "Driver",
        "team_name": "Test Team",
        "team_colour": "E0B552",
        "headshot_url": None,
    }


def test_standings_and_driver_profile(monkeypatch) -> None:
    season_stats._season_cache.clear()
    monkeypatch.setattr(season_stats.config, "OPENF1_BATCH_PAUSE_SECONDS", 0)

    monkeypatch.setattr(
        season_stats.client,
        "get_meetings",
        lambda year: [
            {
                "meeting_key": 500,
                "meeting_name": "Test Grand Prix",
                "date_start": PAST_START,
            }
        ],
    )
    monkeypatch.setattr(
        season_stats.client,
        "get_sessions_by_year",
        lambda year: [
            {
                "meeting_key": 500,
                "session_key": 501,
                "session_type": "Race",
                "date_start": PAST_START,
                "date_end": PAST_END,
                "is_cancelled": False,
            },
            {
                "meeting_key": 500,
                "session_key": 502,
                "session_type": "Qualifying",
                "session_name": "Qualifying",
                "date_end": PAST_END,
                "is_cancelled": False,
            },
            {
                "meeting_key": 500,
                "session_key": 503,
                "session_type": "Race",
                "session_name": "Sprint",
                "date_end": PAST_END,
                "is_cancelled": False,
            },
            {
                "meeting_key": 500,
                "session_key": 504,
                "session_type": "Qualifying",
                "session_name": "Sprint Qualifying",
                "date_end": PAST_END,
                "is_cancelled": False,
            },
        ],
    )
    monkeypatch.setattr(
        season_stats.client,
        "get_session_results_by_meeting",
        lambda meeting_key: [
            {
                "session_key": 501,
                "driver_number": 1,
                "position": 1,
                "points": 25,
                "dnf": False,
                "dns": False,
                "dsq": False,
            },
            {
                "session_key": 501,
                "driver_number": 2,
                "position": 11,
                "points": 0,
                "dnf": True,
                "dns": False,
                "dsq": False,
            },
            {
                "session_key": 502,
                "driver_number": 1,
                "position": 2,
                "points": 0,
                "dnf": False,
                "dns": False,
                "dsq": False,
            },
            {
                "session_key": 502,
                "driver_number": 2,
                "position": 1,
                "points": 0,
                "dnf": False,
                "dns": False,
                "dsq": False,
            },
            {
                "session_key": 503,
                "driver_number": 2,
                "position": 1,
                "points": 8,
                "dnf": False,
                "dns": False,
                "dsq": False,
            },
            {
                "session_key": 504,
                "driver_number": 2,
                "position": 1,
                "points": 0,
                "dnf": False,
                "dns": False,
                "dsq": False,
            },
        ],
    )
    monkeypatch.setattr(
        season_stats.client,
        "get_drivers_for_meeting",
        lambda meeting_key: [_driver(1, "AAA"), _driver(2, "BBB")],
    )

    standings = client.get("/api/standings?year=2035")
    assert standings.status_code == 200

    rows = standings.json()["rows"]
    assert [row["driver"]["code"] for row in rows] == ["AAA", "BBB"]
    assert rows[0]["wins"] == 1
    assert rows[0]["races"] == 1
    assert rows[0]["points"] == 25.0
    assert rows[0]["poles"] == 0
    assert rows[1]["dnf"] == 1
    assert rows[1]["poles"] == 1
    assert rows[1]["races"] == 1
    # Sprint points and sprint poles must not leak into Grand Prix stats.
    assert rows[1]["points"] == 0.0
    assert rows[1]["best_finish"] is None

    profile = client.get("/api/drivers/2/season?year=2035")
    assert profile.status_code == 200

    data = profile.json()
    assert data["driver"]["code"] == "BBB"
    assert data["stats"]["poles"] == 1
    assert data["history"][0]["status"] == "DNF"
    assert data["history"][0]["meeting_name"] == "Test Grand Prix"


def test_unknown_driver_returns_404(monkeypatch) -> None:
    season_stats._season_cache.clear()
    monkeypatch.setattr(
        season_stats,
        "build_season",
        lambda year: (StandingsResponse(year=year, rows=[]), {}),
    )

    response = client.get("/api/drivers/999/season?year=2036")
    assert response.status_code == 404
