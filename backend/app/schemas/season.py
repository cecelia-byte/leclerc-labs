"""Response shapes for verified season standings and driver profiles."""

from pydantic import BaseModel

from app.schemas.results import DriverInfo


class StandingRow(BaseModel):
    position: int
    driver: DriverInfo
    races: int
    wins: int
    podiums: int
    poles: int
    dnf: int
    dns: int
    dsq: int
    points: float
    best_finish: int | None = None
    average_finish: float | None = None
    best_qualifying: int | None = None


class StandingsResponse(BaseModel):
    year: int
    rows: list[StandingRow]
    source: str = "OpenF1"
    note: str = "Race and qualifying results from completed rounds only."


class RaceHistoryItem(BaseModel):
    round: int
    meeting_name: str
    date: str
    finish: int
    status: str
    points: float
    qualifying_position: int | None = None


class DriverSeasonProfile(BaseModel):
    year: int
    driver: DriverInfo
    stats: StandingRow
    history: list[RaceHistoryItem]


class ComparisonMetric(BaseModel):
    label: str
    a: float
    b: float
    # 'A', 'B' or 'TIE'
    winner: str
    higher_is_better: bool = True


class ComparisonRound(BaseModel):
    round: int
    meeting_name: str
    date: str
    a_finish: int | None
    a_status: str
    a_points: float
    a_qualifying: int | None
    b_finish: int | None
    b_status: str
    b_points: float
    b_qualifying: int | None
    finish_winner: str
    qualifying_winner: str


class ComparisonResponse(BaseModel):
    year: int
    driver_a: DriverInfo
    driver_b: DriverInfo
    metrics: list[ComparisonMetric]
    rounds: list[ComparisonRound]
    source: str = "OpenF1"
    note: str = "Grand Prix results only. A DNF counts as lost to a finisher."
