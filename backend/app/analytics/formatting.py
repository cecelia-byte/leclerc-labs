"""Convert raw numbers from OpenF1 into strings humans can read."""


def format_time(seconds: object) -> str | None:
    """90.123 -> '1:30.123'. Strings such as '+1 LAP' pass through unchanged."""
    if seconds is None:
        return None
    if isinstance(seconds, str):
        return seconds
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        return None

    minutes, remainder = divmod(float(seconds), 60)
    return f"{int(minutes)}:{remainder:06.3f}"


def format_gap(gap: object) -> str | None:
    """0 -> '—', 0.184 -> '+0.184'. Lapped strings pass through unchanged."""
    if gap is None:
        return None
    if isinstance(gap, str):
        return gap
    if isinstance(gap, bool) or not isinstance(gap, (int, float)):
        return None
    if float(gap) == 0:
        return '—'
    return f"+{float(gap):.3f}"
