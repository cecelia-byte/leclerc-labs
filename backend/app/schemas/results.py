"""Response shapes for results and qualifying leaderboards."""

from pydantic import BaseModel


class DriverInfo(BaseModel):
    number: int
    code: str
    first_name: str
    last_name: str
    team: str
    team_colour: str
    headshot_url: str | None = None


class ResultRow(BaseModel):
    position: int
    driver: DriverInfo
    status: str
    time: str | None = None
    gap: str | None = None
    laps: int | None = None
    grid_position: int | None = None
    position_change: int | None = None


class ResultsResponse(BaseModel):
    session_key: int
    rows: list[ResultRow]
    source: str = "OpenF1"


class QualifyingRow(BaseModel):
    position: int
    driver: DriverInfo
    best_lap: str | None = None
    gap: str | None = None
    q1: str | None = None
    q2: str | None = None
    q3: str | None = None


class QualifyingResponse(BaseModel):
    session_key: int
    rows: list[QualifyingRow]
    source: str = "OpenF1"
