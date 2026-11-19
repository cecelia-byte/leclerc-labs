"""Pure calculations. No network, no database, easy to test."""


def status_from_flags(*, dnf: object, dns: object, dsq: object) -> str:
    """Retirements are kept separate from ordinary finishing positions."""
    if dsq:
        return 'DSQ'
    if dns:
        return 'DNS'
    if dnf:
        return 'DNF'
    return 'FINISHED'


def position_change(grid_position: int | None, finish_position: int | None) -> int | None:
    """Positive means the driver gained places. None when either value is missing."""
    if grid_position is None or finish_position is None:
        return None
    return grid_position - finish_position


def qualifying_times(raw: object) -> dict[str, float | None]:
    """OpenF1 may give a scalar or a list of Q1/Q2/Q3 times."""
    values: list[float] = []

    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, (int, float)) and not isinstance(item, bool):
                values.append(float(item))
    elif isinstance(raw, (int, float)) and not isinstance(raw, bool):
        values.append(float(raw))

    return {
        'q1': values[0] if len(values) > 0 else None,
        'q2': values[1] if len(values) > 1 else None,
        'q3': values[2] if len(values) > 2 else None,
        'best': min(values) if values else None,
    }
