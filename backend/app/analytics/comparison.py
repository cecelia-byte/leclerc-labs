"""Pure head-to-head rules. Inputs are plain history rows, not HTTP objects."""

from typing import Any


def finish_winner(a: dict[str, Any], b: dict[str, Any]) -> str:
    """A finisher beats a non-finisher; otherwise the lower position wins."""
    a_finished = a.get("status") == "FINISHED"
    b_finished = b.get("status") == "FINISHED"

    if a_finished and not b_finished:
        return "A"
    if b_finished and not a_finished:
        return "B"
    if not a_finished or not b_finished:
        return "TIE"

    a_position = a.get("finish")
    b_position = b.get("finish")
    if a_position is None or b_position is None:
        return "TIE"
    if a_position < b_position:
        return "A"
    if b_position < a_position:
        return "B"
    return "TIE"


def qualifying_winner(a: dict[str, Any], b: dict[str, Any]) -> str:
    """Lower qualifying position is better. Missing times produce a tie."""
    a_position = a.get("qualifying_position")
    b_position = b.get("qualifying_position")
    if a_position is None or b_position is None:
        return "TIE"
    if a_position < b_position:
        return "A"
    if b_position < a_position:
        return "B"
    return "TIE"


def metric_result(
    label: str,
    a_value: float,
    b_value: float,
    *,
    higher_is_better: bool = True,
) -> dict[str, Any]:
    """Build one comparable summary row."""
    if a_value == b_value:
        winner = "TIE"
    elif higher_is_better:
        winner = "A" if a_value > b_value else "B"
    else:
        winner = "A" if a_value < b_value else "B"

    return {
        "label": label,
        "a": a_value,
        "b": b_value,
        "winner": winner,
        "higher_is_better": higher_is_better,
    }


def count_wins(rows: list[dict[str, Any]], key: str, side: str) -> int:
    """Count how often one side won a per-round comparison."""
    return sum(1 for row in rows if row[key] == side)
