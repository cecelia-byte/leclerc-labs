"""Response shapes for the seasons endpoint."""

from pydantic import BaseModel


class Season(BaseModel):
    year: int
    meeting_count: int


class SeasonsResponse(BaseModel):
    seasons: list[Season]
    # Makes the data source visible in the API itself.
    source: str = "OpenF1"
