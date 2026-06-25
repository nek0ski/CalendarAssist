from models import CalendarEvent
from google_calendar import create_calendar_event

event = CalendarEvent(
    title="Test Event",
    date="2026-06-30",
    start_time="15:00",
    end_time="16:00",
    location="Home",
    description="Testing Calendar API",
    confidence=1.0,
)

link = create_calendar_event(event)

print(link)