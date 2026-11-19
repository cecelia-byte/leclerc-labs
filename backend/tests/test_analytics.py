"""Pure calculation tests — no network and no server needed."""

from app.analytics.formatting import format_gap, format_time
from app.analytics.metrics import position_change, qualifying_times, status_from_flags


def test_format_time() -> None:
    assert format_time(90.123) == "1:30.123"
    assert format_time(None) is None
    assert format_time("+1 LAP") == "+1 LAP"


def test_format_gap() -> None:
    assert format_gap(0) == "—"
    assert format_gap(0.184) == "+0.184"
    assert format_gap("+1 LAP") == "+1 LAP"


def test_position_change_sign_convention() -> None:
    assert position_change(5, 2) == 3   # gained three places
    assert position_change(2, 5) == -3  # lost three places
    assert position_change(None, 5) is None


def test_status_priority() -> None:
    assert status_from_flags(dnf=True, dns=False, dsq=False) == "DNF"
    assert status_from_flags(dnf=False, dns=True, dsq=False) == "DNS"
    assert status_from_flags(dnf=True, dns=True, dsq=True) == "DSQ"
    assert status_from_flags(dnf=False, dns=False, dsq=False) == "FINISHED"


def test_qualifying_times_accept_scalar_and_list() -> None:
    scalar = qualifying_times(91.5)
    assert scalar["best"] == 91.5
    assert scalar["q1"] == 91.5
    assert scalar["q2"] is None

    session = qualifying_times([91.5, 90.8, 90.2])
    assert session["q1"] == 91.5
    assert session["q2"] == 90.8
    assert session["q3"] == 90.2
    assert session["best"] == 90.2
