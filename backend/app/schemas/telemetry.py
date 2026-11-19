"""Response shapes for lap-by-lap telemetry."""

from pydantic import BaseModel

from app.schemas.results import DriverInfo


class LapPoint(BaseModel):
    lap_number: int
    duration: float
    sector_1: float | None = None
    sector_2: float | None = None
    sector_3: float | None = None
    speed_trap: int | None = None
    is_pit_out_lap: bool = False


class DriverLaps(BaseModel):
    driver: DriverInfo
    laps: list[LapPoint]
    fastest_lap: LapPoint | None = None


class LapsResponse(BaseModel):
    session_key: int
    drivers: list[DriverLaps]
    source: str = "OpenF1"
    note: str = "Open circles mark pit-out laps; fastest lap excludes them."


class Stint(BaseModel):
    stint_number: int
    compound: str
    lap_start: int
    lap_end: int
    tyre_age_at_start: int | None = None


class DriverStints(BaseModel):
    driver: DriverInfo
    stints: list[Stint]


class StintsResponse(BaseModel):
    session_key: int
    drivers: list[DriverStints]
    max_lap: int
    source: str = "OpenF1"
    note: str = "Compounds and lap ranges are recorded by OpenF1, not estimated."


class TelemetryPoint(BaseModel):
    t_ms: int
    speed: int
    throttle: int | None = None
    brake: int | None = None
    gear: int | None = None
    rpm: int | None = None
    drs: int | None = None


class TelemetrySummary(BaseModel):
    top_speed: int
    average_speed: float
    full_throttle_pct: float
    brake_events: int
    max_rpm: int | None = None
    drs_pct: float


class TelemetryResponse(BaseModel):
    session_key: int
    driver: DriverInfo
    lap_number: int
    points: list[TelemetryPoint]
    summary: TelemetrySummary
    raw_samples: int
    source: str = "OpenF1"
    note: str = "Recorded by OpenF1 at ~3.7 Hz; downsampled for display."
