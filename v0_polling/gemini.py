from datetime import datetime
from google import genai
from google.genai import types  # Import types for image processing wrapping

from config import GEMINI_API_KEY
from models import CalendarEvent

client = genai.Client(api_key=GEMINI_API_KEY)


def extract_event(text: str) -> CalendarEvent:
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
Today's date is {today}.

Extract ONE calendar event.

Resolve relative dates like:
- tomorrow
- next Friday
- this weekend

If information is missing, use null.

Message:

{text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CalendarEvent,
        },
    )

    return CalendarEvent.model_validate_json(response.text)


def extract_event_from_image(image_bytes: bytes, caption: str = "") -> CalendarEvent:
    """Passes raw image components alongside an extraction schema directive to Gemini Vision."""
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
Today's date is {today}.

Analyze the text and layout inside this event flyer/screenshot image. 
Extract ONE calendar event from it.

Optional helper caption details: {caption}

Resolve relative timelines appropriately based on today's target tracking date.
If critical fields are completely illegible or missing, use null.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",  # Covers standard telegram image processing downloads
            ),
            prompt
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": CalendarEvent,
        },
    )

    return CalendarEvent.model_validate_json(response.text)