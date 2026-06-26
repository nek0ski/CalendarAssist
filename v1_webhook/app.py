import os
import json
from flask import Flask, request, jsonify
from telegram import Update, Bot
from handlers import echo, handle_callback  # Imported echo for clean routing updates

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
async def telegram_webhook():
    if request.method == "POST":
        payload = request.get_json(force=True)
        update = Update.de_json(payload, bot)
        
        # Correctly pass incoming execution loops to their proper handler destinations
        if update.message:
            await echo(update, None)
        elif update.callback_query:
            await handle_callback(update, None)
            
        return jsonify({"status": "success"}), 200
    return "Invalid Request", 400

@app.route('/reminder-trigger', methods=['POST'])
async def reminder_trigger():
    payload = request.get_json(force=True)
    chat_id = payload.get("chat_id")
    event_title = payload.get("title")
    
    await bot.send_message(
        chat_id=chat_id, 
        text=f"⏰ **Reminder:** Your event '{event_title}' starts in exactly 1 hour!"
    )
    return jsonify({"status": "reminder_sent"}), 200