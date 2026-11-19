"""Pure telemetry rules — no network calls."""

from datetime import datetime, timedelta, timezone

from app.analytics.telemetry import (
    downsample,
    group_samples,
    normalise_sample,
    summarise,
    to_points,
)


def test_normalise_sample_keeps_only_usable_rows() -> None:
    good = normalise_sample(
        {
            "date": "2025-03-16T03:20:00.123000+00:00",
            "speed": 312.7,
            "throttle": 100,
            "brake": 0,
            "n_gear": 8,
            "rpm": 11800,
            "drs": 12,
        }
    )
    assert good is not None
    assert good["speed"] == 312
    assert good["throttle"] == 100
    assert good["drs"] == 12
    assert good["date"].tzinfo is not None

    assert normalise_sample({"date": "bad", "speed": 100}) is None
    assert normalise_sample({"date": "2025-03-16T03:20:00Z", "speed": "fast"}) is None


def test_group_samples_sorts_by_time_and_drops_bad_rows() -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    rows = [
        {
            "date": (start + timedelta(seconds=2)).isoformat(),
            "speed": 200,
        },
        {"date": "not-a-date", "speed": 210},
        {
            "date": (start + timedelta(seconds=1)).isoformat(),
            "speed": 190,
        },
    ]

    samples = group_samples(rows)
    assert [sample["speed"] for sample in samples] == [190, 200]


def test_downsample_caps_points_and_keeps_last_sample() -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    samples = [
        {"date": start + timedelta(seconds=index), "speed": index}
        for index in range(10)
    ]

    selected = downsample(samples, max_points=3)
    assert len(selected) <= 3
    assert selected[-1] is samples[-1]


def test_summarise_uses_only_recorded_values() -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    samples = [
        {
            "date": start + timedelta(seconds=index),
            "speed": speed,
            "throttle": throttle,
            "brake": brake,
            "gear": 8,
            "rpm": 11000,
            "drs": drs,
        }
        for index, (speed, throttle, brake, drs) in enumerate(
            [(300, 100, 0, 1), (320, 100, 0, 12), (180, 20, 100, 0)]
        )
    ]

    summary = summarise(samples)
    assert summary["top_speed"] == 320
    assert summary["average_speed"] == 266.7
    assert summary["full_throttle_pct"] == 66.7
    assert summary["brake_events"] == 1
    assert summary["max_rpm"] == 11000
    assert summary["drs_pct"] == 66.7


def test_to_points_starts_at_zero_milliseconds() -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    samples = [
        {"date": start, "speed": 100},
        {
            "date": start + timedelta(milliseconds=270),
            "speed": 120,
            "throttle": 50,
            "brake": 0,
            "gear": 5,
            "rpm": 9000,
            "drs": 0,
        },
    ]

    points = to_points(samples)
    assert points[0]["t_ms"] == 0
    assert points[1]["t_ms"] == 270
    assert points[1]["speed"] == 120
