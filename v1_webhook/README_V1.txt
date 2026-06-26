========================================================================
MODULE SPECIFICATION: v1_webhook (SERVERLESS WEBHOOK PRODUCTION MODULE)
========================================================================

[1. ARCHITECTURE OVERVIEW]
This module houses the production-ready implementation of CalendarAssist, refactored 
into an asynchronous, event-driven Flask microservice. Instead of resource-intensive 
polling loops, this architecture leverages an asynchronous webhook model. 

The application layer consumes 0% system memory and CPU cycles while idling, 
achieving a true scale-to-zero runtime state ideal for serverless cloud containers.

[2. PIPELINE GRAPH]
Unstructured Input -> Instantaneous HTTPS POST Webhook -> Flask Application -> 
Gemini Core -> Pydantic Validation -> Dynamic Disk Cache -> Google API Mutation -> 
External Cron Engine API -> Asynchronous Webhook Reminder Trigger

[3. SYSTEM MANIFEST & RESOURCE DECOUPLING]
- Entry Point: `app.py` (Flask application handling webhook routing logic).
- Routing Layer: `handlers.py` (Refactored to handle serverless state and external triggers).
- Task Automation: Decoupled entirely from the runtime container. Background task scheduling 
  is delegated to `api.cron-job.org` via automated REST commands, neutralizing container-sleep timeout risks.

[4. SPECIFIC ENVIRONMENT PARSING MATRIX]
System initialization within this directory requires an active `.env` file containing 
the following continuous parameter matrix keys:

- `BOT_TOKEN`               -> Active Telegram bot client identifier string.
- `GEMINI_API_KEY`          -> Access token issued via Google AI Studio.
- `CRON_JOB_API_KEY`        -> Authentication token for the api.cron-job.org platform.
- `PYTHONANYWHERE_USERNAME` -> Your live application cloud hostname prefix path.
- `GOOGLE_CREDENTIALS_JSON` -> Serialized dictionary containing desktop application OAuth configurations.
- `GOOGLE_TOKEN_JSON`       -> Serialized persistent OAuth sign-in token refresh block data.

[5. OPERATIONAL DEPENDENCIES & BEHAVIOR CONSTRAINTS]
- State Tracking: To survive standard container sleep cycles without losing mid-transaction state, 
  user confirmation caching (`pending_event`) is decoupled from memory and dynamically committed 
  to a localized folder cache hierarchy (`/tmp/bot_sessions`).
- Webhook Handshake: Long polling functions are strictly disabled. The bot relies entirely on 
  Telegram's servers actively pushing structured JSON payloads to the webserver via the exposed 
  `/webhook` endpoint routing directory.

[6. HOW TO DEPLOY ON PYTHONANYWHERE]
1. Navigate to the PythonAnywhere Web Dashboard and construct a new Web App manually.
2. Select the matching Python runtime engine and define your project paths pointing directly 
   to `/home/YOUR_USERNAME/CalendarAssist/v1_webhook`.
3. Open your automatically generated WSGI configuration script, flush the placeholder content, 
   and paste this optimized loader sequence:

    import sys
    import os
    from dotenv import load_dotenv

    project_home = '/home/YOUR_USERNAME/CalendarAssist/v1_webhook'
    if project_home not in sys.path:
        sys.path.insert(0, project_home)

    load_dotenv(os.path.join(project_home, '.env'))
    from app import app as application

4. Click the green "Reload" button to build the webapp instance container.
5. Bind the master connection between Telegram and your live microservice by pasting the 
   following URL string matrix into your web browser's address bar:

   https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<USERNAME>.pythonanywhere.com/webhook

6. Success confirmation signature: `{"ok":true,"result":true,"description":"Webhook was set"}`
========================================================================