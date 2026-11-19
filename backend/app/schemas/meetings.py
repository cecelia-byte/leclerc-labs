"""Response shapes for meetings and sessions."""

from pydantic import BaseModel


class Meeting(BaseModel):
    meeting_key: int
    year: int
    name: str
    official_name: str
    location: str
    country_name: str
    country_code: str
    country_flag: str | None = None
    circuit_short_name: str
    circuit_image: str | None = None
    date_start: str
    date_end: str


class MeetingsResponse(BaseModel):
    meetings: list[Meeting]
    year: int
    source: str = "OpenF1"


class Session(BaseModel):
    session_key: int
    meeting_key: int
    session_name: str
    session_type: str
    date_start: str
    date_end: str


class SessionsResponse(BaseModel):
    sessions: list[Session]
    meeting_key: int
    source: str = "OpenF1"
