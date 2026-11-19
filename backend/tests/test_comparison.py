"""Pure head-to-head rules — no network, no database."""

from app.analytics.comparison import (
    count_wins,
    finish_winner,
    metric_result,
    qualifying_winner,
)


def test_finisher_beats_retirement() -> None:
    a = {"status": "FINISHED", "finish": 9}
    b = {"status": "DNF", "finish": 4}
    assert finish_winner(a, b) == "A"
    assert finish_winner(b, a) == "B"


def test_better_finishing_position_wins() -> None:
    assert finish_winner({"status": "FINISHED", "finish": 2},
                         {"status": "FINISHED", "finish": 5}) == "A"
    assert finish_winner({"status": "FINISHED", "finish": 8},
                         {"status": "FINISHED", "finish": 3}) == "B"
    assert finish_winner({"status": "FINISHED", "finish": 3},
                         {"status": "FINISHED", "finish": 3}) == "TIE"


def test_qualifying_needs_both_positions() -> None:
    assert qualifying_winner({"qualifying_position": 3}, {"qualifying_position": 6}) == "A"
    assert qualifying_winner({"qualifying_position": None}, {"qualifying_position": 1}) == "TIE"


def test_metric_result_respects_direction() -> None:
    assert metric_result("POINTS", 100, 80)["winner"] == "A"
    assert metric_result("DNF", 2, 1, higher_is_better=False)["winner"] == "B"
    assert metric_result("DNF", 2, 2, higher_is_better=False)["winner"] == "TIE"


def test_count_wins() -> None:
    rows = [{"finish_winner": "A"}, {"finish_winner": "B"}, {"finish_winner": "A"}]
    assert count_wins(rows, "finish_winner", "A") == 2
