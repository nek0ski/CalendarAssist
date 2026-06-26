import os
import json
from flask import Flask, request, jsonify
from telegram import Update, Bot
from handlers import handle_message, handle_callback  # We will keep your logic!

app = Flask(__name__)

# Initialize the Bot object without running an active polling loop
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
async def telegram_webhook():
    """Receives incoming text/flyer updates directly from Telegram's servers"""
    if request.method == "POST":
        payload = request.get_json(force=True)
        update = Update.de_json(payload, bot)
        
        # Pass the update block into your asynchronous application handlers
        if update.message:
            await handle_message(update, None)
        elif update.callback_query:
            await handle_callback(update, None)
            
        return jsonify({"status": "success"}), 200
    return "Invalid Request", 400

@app.route('/reminder-trigger', methods=['POST'])
async def reminder_trigger():
    """The external wake-up endpoint hit by cron-job.org when an event is 1 hour away"""
    payload = request.get_json(force=True)
    chat_id = payload.get("chat_id")
    event_title = payload.get("title")
    
    # Send your foreground reminder alert back to your Telegram client
    await bot.send_message(
        chat_id=chat_id, 
        text=f"⏰ Reminder: Your event '{event_title}' is starting in exactly 1 hour!"
    )
    return jsonify({"status": "reminder_sent"}), 200