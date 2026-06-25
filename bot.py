from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TOKEN
from handlers import (
    start,
    echo,
    add_calendar_callback,
    cancel_callback,
)

def main():
    # Initialize the application and enable the job queue for background reminders
    app = Application.builder().token(TOKEN).build()

    # /start command
    app.add_handler(CommandHandler("start", start))

    # Button: Add to Calendar
    app.add_handler(
        CallbackQueryHandler(
            add_calendar_callback,
            pattern="^add_calendar$",
        )
    )

    # Button: Cancel
    app.add_handler(
        CallbackQueryHandler(
            cancel_callback,
            pattern="^cancel$",
        )
    )

    # Receive all messages (Text, Captions, etc.)
    app.add_handler(
        MessageHandler(
            filters.ALL,
            echo,
        )
    )

    print("🤖 Calendar Assist with Reminders is running...")
    app.run_polling()

if __name__ == "__main__":
    main()