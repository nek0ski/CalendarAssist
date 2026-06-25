from typing import Optional
from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description="Title of the event"
    )

    date: Optional[str] = Field(
        default=None,
        description="Event date in YYYY-MM-DD format"
    )

    start_time: Optional[str] = Field(
        default=None,
        description="Start time in HH:MM (24-hour) format"
    )

    end_time: Optional[str] = Field(
        default=None,
        description="End time in HH:MM (24-hour) format"
    )

    location: Optional[str] = Field(
        default=None,
        description="Event location"
    )

    description: Optional[str] = Field(
        default=None,
        description="Additional event details"
    )

    confidence: float = Field(
        default=0.0,
        description="Confidence score between 0 and 1"
    )