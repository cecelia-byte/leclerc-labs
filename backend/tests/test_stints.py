"""Pure tyre-stint helpers — no HTTP."""

from app.analytics.stints import group_stints_by_driver, normalise_stint


def test_normalise_stint_keeps_usable_rows() -> None:
    stint = normalise_stint(
        {
            "stint_number": 2,
            "compound": "medium",
            "lap_start": 12,
            "lap_end": 30,
            "tyre_age_at_start": 3,
        }
    )
    assert stint is not None
    assert stint["compound"] == "MEDIUM"
    assert stint["lap_end"] == 30


def test_normalise_stint_rejects_bad_ranges() -> None:
    bad_end = {
        "stint_number": 1,
        "lap_start": 5,
        "lap_end": 2,
        "compound": "HARD",
    }
    bad_compound = {
        "stint_number": 1,
        "lap_start": 1,
        "lap_end": 2,
        "compound": None,
    }
    assert normalise_stint(bad_end) is None
    assert normalise_stint(bad_compound) is None


def test_group_stints_sorts_by_stint_number() -> None:
    grouped = group_stints_by_driver(
        [
            {
                "driver_number": 4,
                "stint_number": 2,
                "lap_start": 20,
                "lap_end": 40,
                "compound": "HARD",
            },
            {
                "driver_number": 4,
                "stint_number": 1,
                "lap_start": 1,
                "lap_end": 19,
                "compound": "MEDIUM",
            },
        ]
    )
    assert [item["stint_number"] for item in grouped[4]] == [1, 2]
