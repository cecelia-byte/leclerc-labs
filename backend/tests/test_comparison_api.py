"""Comparison endpoint with cached fake profiles — no OpenF1 calls."""

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.results import DriverInfo
from app.schemas.season import (
    DriverSeasonProfile,
    RaceHistoryItem,
    StandingsResponse,
    StandingRow,
)
from app.services import season_stats

client = TestClient(app)


def _driver(number: int, code: str) -> DriverInfo:
    return DriverInfo(
        number=number,
        code=code,
        first_name="Test",
        last_name="Driver",
        team="Test Team",
        team_colour="#E0B552",
        headshot_url=None,
    )


def _profile(number: int, code: str, position: int, history: list[RaceHistoryItem]) -> DriverSeasonProfile:
    driver = _driver(number, code)
    return DriverSeasonProfile(
        year=2035,
        driver=driver,
        stats=StandingRow(
            position=position,
            driver=driver,
            races=len(history),
            wins=1,
            podiums=1,
            poles=0,
            dnf=0,
            dns=0,
            dsq=0,
            points=sum(item.points for item in history),
            best_finish=1,
            average_finish=3.0,
            best_qualifying=1,
        ),
        history=history,
    )


def test_compare_returns_rounds_and_metrics(monkeypatch) -> None:
    profile_a = _profile(
        1,
        "AAA",
        1,
        [
            RaceHistoryItem(round=1, meeting_name="Round One", date="2023-01-01T00:00:00+00:00",
                            finish=1, status="FINISHED", points=25, qualifying_position=1),
            RaceHistoryItem(round=2, meeting_name="Round Two", date="2023-01-08T00:00:00+00:00",
                            finish=5, status="FINISHED", points=10, qualifying_position=6),
        ],
    )
    profile_b = _profile(
        2,
        "BBB",
        2,
        [
            RaceHistoryItem(round=1, meeting_name="Round One", date="2023-01-01T00:00:00+00:00",
                            finish=3, status="FINISHED", points=15, qualifying_position=2),
            RaceHistoryItem(round=2, meeting_name="Round Two", date="2023-01-08T00:00:00+00:00",
                            finish=2, status="FINISHED", points=18, qualifying_position=3),
        ],
    )

    monkeypatch.setattr(
        season_stats,
        "build_season",
        lambda year: (StandingsResponse(year=year, rows=[]), {1: profile_a, 2: profile_b}),
    )

    response = client.get("/api/compare?year=2035&a=1&b=2")
    assert response.status_code == 200

    data = response.json()
    assert data["driver_a"]["code"] == "AAA"
    assert len(data["rounds"]) == 2
    assert data["rounds"][0]["finish_winner"] == "A"
    assert data["rounds"][1]["finish_winner"] == "B"

    metrics = {item["label"]: item for item in data["metrics"]}
    assert metrics["RACE FINISH WINS"]["a"] == 1
    assert metrics["RACE FINISH WINS"]["b"] == 1
    assert metrics["POINTS"]["winner"] == "A"


def test_compare_rejects_same_driver(monkeypatch) -> None:
    monkeypatch.setattr(
        season_stats,
        "build_season",
        lambda year: (StandingsResponse(year=year, rows=[]), {}),
    )

    response = client.get("/api/compare?year=2035&a=1&b=1")
    assert response.status_code == 400


def test_compare_rejects_unknown_driver(monkeypatch) -> None:
    monkeypatch.setattr(
        season_stats,
        "build_season",
        lambda year: (StandingsResponse(year=year, rows=[]), {}),
    )

    response = client.get("/api/compare?year=2035&a=1&b=2")
    assert response.status_code == 404
