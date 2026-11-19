"""Lap endpoint with a fake OpenF1 client — no network calls."""

from fastapi.testclient import TestClient

from app.main import app
from app.services import lap_data

client = TestClient(app)

RAW_LAPS = [
    {
        "driver_number": 4,
        "lap_number": 1,
        "lap_duration": 120.0,
        "duration_sector_1": 40.0,
        "is_pit_out_lap": True,
    },
    {
        "driver_number": 4,
        "lap_number": 2,
        "lap_duration": 94.5,
        "duration_sector_1": 30.0,
        "st_speed": 245,
        "is_pit_out_lap": False,
    },
    {
        "driver_number": 1,
        "lap_number": 1,
        "lap_duration": 95.0,
        "is_pit_out_lap": False,
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
    },
    {
        "driver_number": 1,
        "name_acronym": "VER",
        "first_name": "Max",
        "last_name": "Verstappen",
        "team_name": "Red Bull Racing",
        "team_colour": "4781D7",
    },
]


def test_laps_endpoint_returns_selected_drivers(monkeypatch) -> None:
    monkeypatch.setattr(lap_data.client, "get_laps", lambda session_key: RAW_LAPS)
    monkeypatch.setattr(lap_data.client, "get_drivers", lambda session_key: RAW_DRIVERS)

    response = client.get("/api/sessions/999/laps?drivers=4&drivers=1")
    assert response.status_code == 200

    data = response.json()
    assert [item["driver"]["code"] for item in data["drivers"]] == ["NOR", "VER"]
    norris = data["drivers"][0]
    assert [lap["lap_number"] for lap in norris["laps"]] == [1, 2]
    assert norris["laps"][0]["is_pit_out_lap"] is True
    assert norris["fastest_lap"]["lap_number"] == 2
    assert norris["fastest_lap"]["speed_trap"] == 245


def test_laps_endpoint_defaults_to_drivers_with_most_laps(monkeypatch) -> None:
    monkeypatch.setattr(lap_data.client, "get_laps", lambda session_key: RAW_LAPS)
    monkeypatch.setattr(lap_data.client, "get_drivers", lambda session_key: RAW_DRIVERS)

    response = client.get("/api/sessions/999/laps")
    assert response.status_code == 200
    assert len(response.json()["drivers"]) == 2


def test_laps_endpoint_returns_404_when_no_rows(monkeypatch) -> None:
    monkeypatch.setattr(lap_data.client, "get_laps", lambda session_key: [])
    monkeypatch.setattr(lap_data.client, "get_drivers", lambda session_key: [])

    response = client.get("/api/sessions/999/laps")
    assert response.status_code == 404
