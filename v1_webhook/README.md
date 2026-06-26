# Calendar Assist

An asynchronous Python application that extracts event information from unstructured text or images using the Gemini 2.5 Flash model, validates the structured schema via Pydantic, and creates corresponding events in Google Calendar via the Google Calendar API v3.

## System Architecture

The application handles text input and media attachments, passing them through a validation pipeline before mutation operations are executed against the Google API ecosystem:

Unstructured Source (Text/Image) -> Telegram Bot Framework -> Gemini 2.5 Flash -> Pydantic Structural Validation -> State Confirmation (User Action) -> Google Calendar API Mutation -> Scheduled Foreground Reminder Task

## Core Features

* **Multimodal OCR Processing:** Accepts graphical attachments (flyers, screenshots, banners). Leverages the Gemini Vision capability to parse graphical layouts natively without local layout pre-processing or external binary engines (e.g., Tesseract).
* **Deterministic Structural Extraction:** Generates strict JSON schemas modeling event attributes (title, date, start_time, end_time, location, description, confidence score).
* **Relative Temporal Resolution:** System prompts force the LLM to parse and resolve relative expressions such as "tomorrow", "next Friday", or "this weekend" using a dynamic system execution date reference.
* **Confidence Guardrails:** Enforces a hard structural threshold (confidence >= 80%) and baseline required parameters (title, date, start_time) before presenting a verification layer to the client.
* **State Preservation Interface:** Employs an interactive Telegram inline keyboard UI to manage state machine transitions (Confirmation/Cancellation) without data-store overhead by tracking session contexts dynamically within the native python-telegram-bot user_data dictionary memory space.
* **Asynchronous Automation Scheduler:** Leverages python-telegram-bot's underlying JobQueue architecture to schedule push notifications precisely 1 hour prior to event execution times.

## Directory Layout

```text
CalendarAssist/
│
├── .env                  # Environment configuration secrets (Git ignored)
├── bot.py                # Main application initialization and polling runtime loop
├── config.py             # System configuration module enforcing core variable constraints
├── gemini.py             # Interfaces Google GenAI SDK and manages vision payloads
├── google_calendar.py    # Manages Google OAuth authorization routines and API service builds
├── handlers.py           # Core message handling, operational routines, and callbacks
├── models.py             # Declares strict Pydantic models for data payload contracts
├── requirements.txt      # Production locked system package manifest
├── credentials.json      # Desktop Client configuration file (Git ignored)
└── token.json            # Persisted valid application credential token (Git ignored)

```

## Runtime Dependencies

* Python 3.10+
* `google-genai`: Framework interface for Gemini LLM orchestration.
* `python-telegram-bot[job-queue]`: Implements the asynchronous runtime loop and task automation queues.
* `pydantic`: Implements system-wide data parsing, runtime data enforcement, and validation.
* `apscheduler`: Background scheduling processor supporting the automated reminder pipeline.
* `google-api-python-client` & `google-auth-oauthlib`: Manages service generation and client authentication mechanics for Google API endpoints.

## Configuration Matrix

System initialization relies on variables extracted either from a root `.env` file or cloud-injected container declarations:

```ini
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key

```

### Stateless Cloud Deployments Fallback

To bypass manual web-browser loops inside stateless or serverless architectures (e.g., Railway), the application is instrumented to reconstruct active file buffers from string variables if they are dropped during deployment builds:

* `GOOGLE_CREDENTIALS_JSON`: Raw JSON literal payload derived from `credentials.json`.
* `GOOGLE_TOKEN_JSON`: Raw serialized dictionary string matching the active authorization block inside `token.json`.

## License

This project is licensed under the terms of the MIT License.

```

### Git Update Instructions

To apply these clean changes directly to your public repository, run the following sequence in your VS Code terminal:

```powershell
git add README.md
git commit -m "Docs: Refactor README for technical clarity and format standard standardization"
git push origin main

```