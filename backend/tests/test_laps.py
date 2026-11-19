"""Pure lap filtering — no HTTP, no OpenF1."""

from app.analytics.laps import fastest_lap, group_by_driver, normalise_lap


def test_normalise_lap_keeps_usable_values() -> None:
    lap = normalise_lap(
        {
            "lap_number": 4,
            "lap_duration": 95.2,
            "duration_sector_1": 30.1,
            "st_speed": 240,
            "is_pit_out_lap": True,
        }
    )
    assert lap is not None
    assert lap["duration"] == 95.2
    assert lap["sector_1"] == 30.1
    assert lap["speed_trap"] == 240
    assert lap["is_pit_out_lap"] is True


def test_normalise_lap_rejects_missing_or_bad_durations() -> None:
    assert normalise_lap({"lap_number": 1, "lap_duration": None}) is None
    assert normalise_lap({"lap_number": 0, "lap_duration": 90.0}) is None
    assert normalise_lap({"lap_number": 2, "lap_duration": -1}) is None


def test_group_by_driver_sorts_laps() -> None:
    grouped = group_by_driver(
        [
            {"driver_number": 4, "lap_number": 3, "lap_duration": 92.0},
            {"driver_number": 4, "lap_number": 1, "lap_duration": 95.0},
            {"driver_number": 1, "lap_number": 1, "lap_duration": 94.0},
        ]
    )
    assert [lap["lap_number"] for lap in grouped[4]] == [1, 3]
    assert set(grouped) == {4, 1}


def test_fastest_lap_ignores_pit_out_laps() -> None:
    laps = [
        {"lap_number": 1, "duration": 120.0, "is_pit_out_lap": True},
        {"lap_number": 2, "duration": 95.0, "is_pit_out_lap": False},
        {"lap_number": 3, "duration": 94.5, "is_pit_out_lap": False},
    ]
    best = fastest_lap(laps)
    assert best is not None
    assert best["lap_number"] == 3


def test_fastest_lap_handles_only_pit_out_laps() -> None:
    laps = [{"lap_number": 1, "duration": 120.0, "is_pit_out_lap": True}]
    assert fastest_lap(laps) is None
