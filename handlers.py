import os
import json
import requests
from datetime import datetime, timedelta
import io
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from gemini import extract_event, extract_event_from_image
from google_calendar import create_calendar_event
from models import CalendarEvent

# A simple dynamic file-based backup state to prevent session loss on free servers
STATE_DIR = "/tmp/bot_sessions"
os.makedirs(STATE_DIR, exist_ok=True)

def save_session(chat_id, data):
    with open(f"{STATE_DIR}/{chat_id}.json", "w") as f:
        json.dump(data, f)

def load_session(chat_id):
    path = f"{STATE_DIR}/{chat_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

async def extract_message_content_and_type(message):
    if message.text:
        return message.text, "text"
    if message.photo:
        photo_file = await message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        return {"bytes": bytes(photo_bytes), "caption": message.caption or ""}, "image"
    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 👋\n\nI'm Calendar Assist.\nSend me an event text or flyer poster, and I'll add it to your calendar completely free!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    content, content_type = await extract_message_content_and_type(update.message)
    if not content_type:
        await update.message.reply_text("I couldn't find any readable text or images.")
        return

    try:
        if content_type == "text":
            event = extract_event(content)
        elif content_type == "image":
            await update.message.reply_text("🔍 Analyzing flyer layout with Gemini Vision...")
            event = extract_event_from_image(content["bytes"], content["caption"])

        if event.confidence >= 0.80 and event.title and event.date and event.start_time:
            # Persistent cross-request state tracking
            save_session(update.message.chat_id, event.model_dump())

            keyboard = [
                [
                    # Changed to align callback data paths
                    InlineKeyboardButton("✅ Add to Calendar", callback_data="confirm_event"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"📅 Event Found via OCR\n\n📌 Title:\n{event.title}\n\n%s Date:\n{event.date}\n\n🕒 Start:\n{event.start_time}\n\n🕓 End:\n{event.end_time or 'Not specified'}\n\n📍 Location:\n{event.location or 'Not specified'}\n\n🎯 Confidence:\n{event.confidence:.0%}\n\nAdd this to your calendar?" % "📆",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                f"⚠️ I couldn't confidently extract details.\n\nTitle: {event.title}\nDate: {event.date}\nConfidence: {event.confidence:.0%}"
            )
    except Exception as e:
        print(f"Error in echo handler: {e}")
        await update.message.reply_text("❌ Something went wrong while extracting details.")

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Event cancelled.")
        return

    if query.data == "confirm_event":
        event_data = load_session(chat_id)
        if not event_data:
            await query.edit_message_text("❌ Session expired. Please upload your flyer again.")
            return

        try:
            event = CalendarEvent(**event_data)
            await query.edit_message_text("⏳ Syncing with Google Calendar...")
            
            # Generate your remote calendar URL interface
            calendar_link = create_calendar_event(event)
            
            # Fire automation registration to Cron-Job.org
            CRON_API_KEY = os.getenv("CRON_JOB_API_KEY")
            username = os.getenv("PYTHONANYWHERE_USERNAME")
            
            if CRON_API_KEY and username:
                try:
                    event_datetime_str = f"{event.date} {event.start_time}"
                    event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
                    reminder_time = event_datetime - timedelta(hours=1)
                    
                    cron_schedule = {
                        "minutes": [reminder_time.minute],
                        "hours": [reminder_time.hour],
                        "mdays": [reminder_time.day],
                        "months": [reminder_time.month],
                        "wdays": [-1]
                    }
                    
                    cron_payload = {
                        "job": {
                            "url": f"https://{username}.pythonanywhere.com/reminder-trigger",
                            "enabled": True,
                            "title": f"Reminder_{chat_id}_{int(reminder_time.timestamp())}",
                            "schedule": cron_schedule,
                            "requestMethod": 1,
                            "requestBody": json.dumps({
                                "chat_id": chat_id,
                                "title": event.title
                            })
                        }
                    }
                    
                    requests.post(
                        "https://api.cron-job.org/jobs", 
                        json=cron_payload, 
                        headers={
                            "Authorization": f"Bearer {CRON_API_KEY}",
                            "Content-Type": "application/json"
                        }
                    )
                except Exception as cron_err:
                    print(f"Cron-job hook failed: {cron_err}")

            await query.edit_message_text(
                f"📅 **Event Added Successfully!**\n\nYour 1-hour automated push notification is scheduled via the external task engine.\n\n🔗 [View in Google Calendar]({calendar_link})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"Error executing callback sequence: {e}")
            await query.edit_message_text("❌ System synchronization error occurred.")