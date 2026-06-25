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


async def extract_message_content_and_type(message):
    """Extracts text, caption, or downloads an image file from the message."""
    # If it's a plain text message
    if message.text:
        return message.text, "text"

    # If it's a photo/poster
    if message.photo:
        # Get the highest resolution version of the photo
        photo_file = await message.photo[-1].get_file()
        # Download the photo into memory as bytes
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Return the raw bytes, along with any caption attached to the photo
        return {"bytes": bytes(photo_bytes), "caption": message.caption or ""}, "image"

    return None, None


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=f"⏰ **Upcoming Event Reminder!**\n\n{job.data}",
        parse_mode="Markdown"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 👋\n\n"
        "I'm Calendar Assist.\n"
        "Send me an event text, or upload/forward an event flyer/poster, and I'll add it to your calendar!"
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

        # Confidence check
        if (
            event.confidence >= 0.80
            and event.title
            and event.date
            and event.start_time
        ):
            context.user_data["pending_event"] = event.model_dump()

            keyboard = [
                [
                    InlineKeyboardButton("✅ Add to Calendar", callback_data="add_calendar"),
                    InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"""📅 Event Found via OCR\n\n📌 Title:\n{event.title}\n\n📆 Date:\n{event.date}\n\n🕒 Start:\n{event.start_time}\n\n🕓 End:\n{event.end_time or "Not specified"}\n\n📍 Location:\n{event.location or "Not specified"}\n\n🎯 Confidence:\n{event.confidence:.0%}\n\nAdd this to your calendar?""",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                f"⚠️ I couldn't confidently extract the details from this flyer.\n\nTitle: {event.title}\nDate: {event.date}\nStart Time: {event.start_time}\n\nConfidence: {event.confidence:.0%}\n\nPlease provide a clearer text copy or image."
            )

    except Exception as e:
        print(f"Error in echo handler: {e}")
        await update.message.reply_text("❌ Something went wrong while extracting the event details.")


async def add_calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    event_data = context.user_data.get("pending_event")

    if not event_data:
        await query.edit_message_text("❌ Session expired or event info missing. Please send the message again.")
        return

    try:
        event = CalendarEvent(**event_data)
        await query.edit_message_text("⏳ Connecting to Google Calendar...")
        
        calendar_link = create_calendar_event(event)
        
        # Schedule notification (Will operate natively seamlessly on Railway)
        try:
            event_datetime = datetime.fromisoformat(f"{event.date}T{event.start_time}")
            reminder_time = event_datetime - timedelta(hours=1)
            now = datetime.now()

            if reminder_time <= now:
                reminder_time = now + timedelta(seconds=10)
                reminder_msg = f"📌 **{event.title}** is starting very soon at {event.start_time}!"
            else:
                reminder_msg = f"📌 **{event.title}** starts in 1 hour (at {event.start_time})!"

            context.job_queue.run_once(
                send_reminder,
                when=reminder_time,
                chat_id=query.message.chat_id,
                name=f"reminder_{event.title}_{event.date}",
                data=reminder_msg
            )
        except Exception as schedule_err:
            print(f"Notification scheduling failed: {schedule_err}")

        context.user_data.pop("pending_event", None)

        await query.edit_message_text(
            f"📅 **Event Added Successfully!**\n\nReminders are active! I'll ping you here on Telegram 1 hour before it kicks off.\n\n🔗 [View in Google Calendar]({calendar_link})",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    except Exception as e:
        print(f"Error in calendar callback: {e}")
        await query.edit_message_text("❌ Authorization failed or something went wrong creating the event.")


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("pending_event", None)
    await query.edit_message_text("❌ Event cancelled.")