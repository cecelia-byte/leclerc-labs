"""Turn one raw OpenF1 driver record into our shared DriverInfo shape."""

from typing import Any

from app.schemas.results import DriverInfo


def to_driver_info(item: dict[str, Any]) -> DriverInfo | None:
    number = item.get("driver_number")
    if number is None:
        return None

    colour = item.get("team_colour") or "8A8F98"
    if not str(colour).startswith("#"):
        colour = f"#{colour}"

    return DriverInfo(
        number=number,
        code=item.get("name_acronym") or "???",
        first_name=item.get("first_name") or "",
        last_name=item.get("last_name") or "",
        team=item.get("team_name") or "Unknown",
        team_colour=colour,
        headshot_url=item.get("headshot_url"),
    )
