from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN not found.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")