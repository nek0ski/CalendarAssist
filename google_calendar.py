import os
from datetime import datetime, timedelta
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from models import CalendarEvent

SCOPES = ["https://www.googleapis.com/auth/calendar"]

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

def get_calendar_service():
    # FORCE WRITE BULLETPROOF CHECK: Recreate files on every execution loop if variables exist
    if os.getenv("GOOGLE_CREDENTIALS_JSON"):
        with open(CREDENTIALS_FILE, "w") as f:
            f.write(os.getenv("GOOGLE_CREDENTIALS_JSON"))
            
    if os.getenv("GOOGLE_TOKEN_JSON"):
        with open(TOKEN_FILE, "w") as f:
            f.write(os.getenv("GOOGLE_TOKEN_JSON"))

    creds = None
    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    except FileNotFoundError:
        pass

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES,
            )

            # FIX: Remove host="localhost" or change it to host="127.0.0.1"
            # Letting the library default without the host string is safest.
            creds = flow.run_local_server(
                port=8080,
                authorization_prompt_message="Opening browser for Google login...",
                success_message="Authentication successful. You can close this window.",
                open_browser=True,
            )

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build(
        "calendar",
        "v3",
        credentials=creds,
    )


def create_calendar_event(event: CalendarEvent):

    service = get_calendar_service()

    start = datetime.fromisoformat(
        f"{event.date}T{event.start_time}"
    )

    if event.end_time:
        end = datetime.fromisoformat(
            f"{event.date}T{event.end_time}"
        )
    else:
        end = start + timedelta(hours=1)

    body = {
        "summary": event.title,
        "location": event.location,
        "description": event.description,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "Asia/Karachi",
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "Asia/Karachi",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {
                    "method": "popup",
                    "minutes": 60,
                }
            ],
        },
    }

    created_event = (
        service.events()
        .insert(
            calendarId="primary",
            body=body,
        )
        .execute()
    )

    return created_event["htmlLink"]