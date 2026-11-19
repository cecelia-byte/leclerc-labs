"""Telemetry endpoint with a fake OpenF1 client — no network calls."""

from fastapi.testclient import TestClient

from app.main import app
from app.services import telemetry_data

client = TestClient(app)

RAW_LAPS = [
    {
        "driver_number": 4,
        "lap_number": 10,
        "date_start": "2025-03-16T03:20:00.000000+00:00",
        "lap_duration": 90.0,
    },
    {
        "driver_number": 4,
        "lap_number": 11,
        "date_start": "2025-03-16T03:21:30.000000+00:00",
    },
]

RAW_CAR_DATA = [
    {
        "date": f"2025-03-16T03:20:{second:02d}.000000+00:00",
        "driver_number": 4,
        "speed": 280 + second,
        "throttle": 100,
        "brake": 0,
        "n_gear": 8,
        "rpm": 11500,
        "drs": 0,
    }
    for second in range(10)
]
RAW_CAR_DATA.append(
    {
        "date": "2025-03-16T03:20:11.000000+00:00",
        "driver_number": 4,
        "speed": 180,
        "throttle": 0,
        "brake": 100,
        "n_gear": 4,
        "rpm": 9000,
        "drs": 0,
    }
)

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


def test_telemetry_endpoint_returns_one_lap(monkeypatch) -> None:
    calls: list[tuple[int, int, str, str]] = []

    def fake_car_data(session_key, driver_number, date_start, date_end):
        calls.append((session_key, driver_number, date_start, date_end))
        return RAW_CAR_DATA

    monkeypatch.setattr(telemetry_data.client, "get_laps", lambda session_key: RAW_LAPS)
    monkeypatch.setattr(telemetry_data.client, "get_car_data", fake_car_data)
    monkeypatch.setattr(
        telemetry_data.client, "get_drivers", lambda session_key: RAW_DRIVERS
    )

    response = client.get("/api/sessions/9693/telemetry?driver=4&lap=10")
    assert response.status_code == 200

    data = response.json()
    assert data["driver"]["code"] == "NOR"
    assert data["lap_number"] == 10
    assert data["raw_samples"] == 11
    assert len(data["points"]) <= 120
    assert data["points"][0]["t_ms"] == 0
    assert data["summary"]["top_speed"] == 289
    assert data["summary"]["brake_events"] == 1
    assert data["note"] == "Recorded by OpenF1 at ~3.7 Hz; downsampled for display."

    assert len(calls) == 1
    assert calls[0][0] == 9693
    assert calls[0][1] == 4
    assert calls[0][2] == "2025-03-16T03:20:00.000"
    assert calls[0][3] == "2025-03-16T03:21:30.000"


def test_telemetry_endpoint_returns_404_for_missing_lap(monkeypatch) -> None:
    monkeypatch.setattr(telemetry_data.client, "get_laps", lambda session_key: RAW_LAPS)
    monkeypatch.setattr(
        telemetry_data.client,
        "get_car_data",
        lambda session_key, driver_number, date_start, date_end: [],
    )
    monkeypatch.setattr(
        telemetry_data.client, "get_drivers", lambda session_key: RAW_DRIVERS
    )

    response = client.get("/api/sessions/9693/telemetry?driver=4&lap=99")
    assert response.status_code == 404
