"""Tests run without network access by replacing the OpenF1 client."""

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api import routes
from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_seasons_are_derived_from_meetings(monkeypatch) -> None:
    monkeypatch.setattr(
        routes.client,
        "get_meetings",
        lambda year=None: [
            {"year": 2025, "meeting_key": 1},
            {"year": 2025, "meeting_key": 2},
            {"year": 2024, "meeting_key": 3},
        ],
    )

    response = client.get("/api/seasons")
    assert response.status_code == 200

    data = response.json()
    assert data["source"] == "OpenF1"
    assert data["seasons"] == [
        {"year": 2025, "meeting_count": 2},
        {"year": 2024, "meeting_count": 1},
    ]


def test_upstream_failure_becomes_a_clean_502(monkeypatch) -> None:
    def explode(year=None):
        raise HTTPException(status_code=502, detail="Could not reach OpenF1")

    monkeypatch.setattr(routes.client, "get_meetings", explode)

    response = client.get("/api/seasons")
    assert response.status_code == 502
    assert response.json()["detail"] == "Could not reach OpenF1"


def _meeting_row(meeting_key: int, name: str, cancelled: bool = False) -> dict:
    return {
        "meeting_key": meeting_key,
        "year": 2025,
        "meeting_name": name,
        "meeting_official_name": name.upper(),
        "location": "Melbourne",
        "country_name": "Australia",
        "country_code": "AUS",
        "country_flag": "flag.png",
        "circuit_short_name": "Melbourne",
        "circuit_image": "circuit.png",
        "date_start": "2025-03-14T01:30:00+00:00",
        "date_end": "2025-03-16T06:00:00+00:00",
        "is_cancelled": cancelled,
    }


def test_meetings_drop_cancelled_events(monkeypatch) -> None:
    monkeypatch.setattr(
        routes.client,
        "get_meetings",
        lambda year=None: [
            _meeting_row(1, "Australian Grand Prix"),
            _meeting_row(2, "Cancelled Grand Prix", cancelled=True),
        ],
    )

    response = client.get("/api/meetings?year=2025")
    assert response.status_code == 200

    data = response.json()
    assert [m["meeting_key"] for m in data["meetings"]] == [1]
    assert data["year"] == 2025


def test_invalid_year_is_rejected() -> None:
    assert client.get("/api/meetings?year=1999").status_code == 422


def test_sessions_are_returned_for_a_meeting(monkeypatch) -> None:
    monkeypatch.setattr(
        routes.client,
        "get_sessions",
        lambda meeting_key: [
            {
                "session_key": 9158,
                "meeting_key": meeting_key,
                "session_name": "Qualifying",
                "session_type": "Qualifying",
                "date_start": "2025-03-15T04:00:00+00:00",
                "date_end": "2025-03-15T05:00:00+00:00",
                "is_cancelled": False,
            }
        ],
    )

    response = client.get("/api/sessions?meeting_key=1254")
    assert response.status_code == 200

    data = response.json()
    assert data["meeting_key"] == 1254
    assert data["sessions"][0]["session_name"] == "Qualifying"


def _driver_row(number: int, code: str) -> dict:
    return {
        "driver_number": number,
        "name_acronym": code,
        "first_name": "Test",
        "last_name": "Driver",
        "team_name": "Test Team",
        "team_colour": "3671C6",
        "headshot_url": None,
    }


def test_results_include_grid_and_exclude_dnf_from_position_change(monkeypatch) -> None:
    monkeypatch.setattr(
        routes.client,
        "get_session_result",
        lambda session_key: [
            {
                "meeting_key": 9999,
                "driver_number": 1,
                "position": 2,
                "dnf": False,
                "dns": False,
                "dsq": False,
                "duration": 5600.1,
                "gap_to_leader": 1.5,
                "number_of_laps": 57,
            },
            {
                "meeting_key": 9999,
                "driver_number": 2,
                "position": 11,
                "dnf": True,
                "dns": False,
                "dsq": False,
                "duration": 5400.0,
                "gap_to_leader": "+1 LAP",
                "number_of_laps": 40,
            },
        ],
    )
    monkeypatch.setattr(
        routes.client,
        "get_drivers",
        lambda session_key: [_driver_row(1, "AAA"), _driver_row(2, "BBB")],
    )
    monkeypatch.setattr(
        routes.client,
        "get_sessions",
        lambda meeting_key: [
            {"session_type": "Qualifying", "session_key": 7777, "is_cancelled": False}
        ],
    )
    monkeypatch.setattr(
        routes.client,
        "get_starting_grid",
        lambda session_key: [
            {"driver_number": 1, "position": 5, "lap_duration": 91.2},
            {"driver_number": 2, "position": 3, "lap_duration": 91.4},
        ],
    )

    response = client.get("/api/sessions/9999/results?session_type=Race")
    assert response.status_code == 200

    rows = response.json()["rows"]
    assert rows[0]["position_change"] == 3
    assert rows[0]["grid_position"] == 5
    assert rows[0]["status"] == "FINISHED"
    assert rows[1]["status"] == "DNF"
    assert rows[1]["position_change"] is None


def test_qualifying_splits_q1_q2_q3(monkeypatch) -> None:
    monkeypatch.setattr(
        routes.client,
        "get_session_result",
        lambda session_key: [
            {
                "driver_number": 1,
                "position": 1,
                "dnf": False,
                "dns": False,
                "dsq": False,
                "duration": [91.5, 90.8, 90.2],
                # Real OpenF1 data: 0.0 in Q3 means pole, not "missing".
                "gap_to_leader": [0.272, 0.022, 0.0],
                "number_of_laps": 12,
            }
        ],
    )
    monkeypatch.setattr(
        routes.client,
        "get_drivers",
        lambda session_key: [_driver_row(1, "AAA")],
    )

    response = client.get("/api/sessions/9998/qualifying")
    assert response.status_code == 200

    row = response.json()["rows"][0]
    assert row["q1"] == "1:31.500"
    assert row["q2"] == "1:30.800"
    assert row["q3"] == "1:30.200"
    assert row["best_lap"] == "1:30.200"
    assert row["gap"] == "—"


def test_results_survive_a_failed_grid_lookup(monkeypatch) -> None:
    monkeypatch.setattr(
        routes.client,
        "get_session_result",
        lambda session_key: [
            {
                "meeting_key": 9999,
                "driver_number": 1,
                "position": 1,
                "dnf": False,
                "dns": False,
                "dsq": False,
                "duration": 5000.0,
                "gap_to_leader": 0,
                "number_of_laps": 57,
            }
        ],
    )
    monkeypatch.setattr(
        routes.client,
        "get_drivers",
        lambda session_key: [_driver_row(1, "AAA")],
    )
    monkeypatch.setattr(
        routes.client,
        "get_sessions",
        lambda meeting_key: [
            {"session_type": "Qualifying", "session_key": 7777, "is_cancelled": False}
        ],
    )

    def fail(session_key):
        raise HTTPException(status_code=503, detail="OpenF1 rate limit reached.")

    monkeypatch.setattr(routes.client, "get_starting_grid", fail)

    response = client.get("/api/sessions/9997/results?session_type=Race")
    assert response.status_code == 200
    assert response.json()["rows"][0]["grid_position"] is None
    assert response.json()["rows"][0]["position_change"] is None
