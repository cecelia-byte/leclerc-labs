"""Stint endpoint with a fake OpenF1 client — no network calls."""

from fastapi.testclient import TestClient

from app.main import app
from app.services import lap_data

client = TestClient(app)

RAW_STINTS = [
    {
        "driver_number": 4,
        "stint_number": 1,
        "compound": "MEDIUM",
        "lap_start": 1,
        "lap_end": 20,
        "tyre_age_at_start": 0,
    },
    {
        "driver_number": 4,
        "stint_number": 2,
        "compound": "HARD",
        "lap_start": 21,
        "lap_end": 44,
        "tyre_age_at_start": 1,
    },
    {
        "driver_number": 1,
        "stint_number": 1,
        "compound": "SOFT",
        "lap_start": 1,
        "lap_end": 15,
        "tyre_age_at_start": 0,
    },
]

RAW_DRIVERS = [
    {
        "driver_number": 4,
        "name_acronym": "NOR",
        "first_name": "Lando",
        "last_name": "Norris",
        "team_name": "McLaren",
        "team_colour": "F47600",
    }
]


def test_stints_endpoint_returns_ordered_stints(monkeypatch) -> None:
    monkeypatch.setattr(lap_data.client, "get_stints", lambda session_key: RAW_STINTS)
    monkeypatch.setattr(lap_data.client, "get_drivers", lambda session_key: RAW_DRIVERS)

    response = client.get("/api/sessions/999/stints?drivers=4")
    assert response.status_code == 200

    data = response.json()
    assert data["max_lap"] == 44
    assert len(data["drivers"]) == 1
    norris = data["drivers"][0]
    assert [item["compound"] for item in norris["stints"]] == ["MEDIUM", "HARD"]
    assert norris["stints"][1]["tyre_age_at_start"] == 1
    # Missing driver metadata should not remove a driver from the timeline.
    assert norris["driver"]["code"] == "NOR"


def test_stints_endpoint_uses_fallback_driver(monkeypatch) -> None:
    monkeypatch.setattr(lap_data.client, "get_stints", lambda session_key: RAW_STINTS)
    monkeypatch.setattr(lap_data.client, "get_drivers", lambda session_key: [])

    response = client.get("/api/sessions/999/stints?drivers=1")
    assert response.status_code == 200
    assert response.json()["drivers"][0]["driver"]["code"] == "1"


def test_stints_endpoint_returns_404_when_empty(monkeypatch) -> None:
    monkeypatch.setattr(lap_data.client, "get_stints", lambda session_key: [])
    monkeypatch.setattr(lap_data.client, "get_drivers", lambda session_key: [])

    response = client.get("/api/sessions/999/stints")
    assert response.status_code == 404
