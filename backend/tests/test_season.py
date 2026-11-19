"""Counting rules for season statistics — no network needed."""

from app.analytics.season import points_of, rank_rows, summarise_driver


def race(position: int, points: float, dnf: bool = False) -> dict:
    return {
        "position": position,
        "points": points,
        "dnf": dnf,
        "dns": False,
        "dsq": False,
    }


def qualifying(position: int) -> dict:
    return {
        "position": position,
        "points": None,
        "dnf": False,
        "dns": False,
        "dsq": False,
    }


def test_points_of_handles_missing_values() -> None:
    assert points_of({"points": 25.0}) == 25.0
    assert points_of({"points": None}) == 0.0
    assert points_of({}) == 0.0


def test_summary_keeps_retirements_separate() -> None:
    summary = summarise_driver(
        [race(1, 25), race(3, 15), race(11, 0, dnf=True)],
        [qualifying(1), qualifying(4)],
    )

    assert summary["races"] == 3
    assert summary["wins"] == 1
    assert summary["podiums"] == 2
    assert summary["poles"] == 1
    assert summary["dnf"] == 1
    assert summary["points"] == 40.0
    assert summary["best_finish"] == 1
    assert summary["average_finish"] == 2.0
    # The DNF's position must not be folded into the average finish.
    assert summary["average_finish"] == (1 + 3) / 2


def test_rank_rows_uses_points_then_wins() -> None:
    rows = [
        {"code": "AAA", "points": 100, "wins": 2, "podiums": 4, "poles": 1},
        {"code": "BBB", "points": 100, "wins": 3, "podiums": 2, "poles": 0},
    ]

    ranked = rank_rows(rows)
    assert [row["code"] for row in ranked] == ["BBB", "AAA"]
    assert [row["position"] for row in ranked] == [1, 2]
