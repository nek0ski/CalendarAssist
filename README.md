# Calendar Assist

An intelligent, context-aware Telegram assistant that automatically parses event details from unstructured text or flyer images using the Gemini 2.5 Flash model, validates the structured schema via Pydantic, and synchronizes entries directly into Google Calendar via the Google Calendar API v3.

The project demonstrates a complete software engineering evolution—transitioning from a stateful, resource-heavy long-polling architecture to a decoupled, event-driven, production-ready serverless model engineered to scale to zero.

---

## System Architectural Evolution

### v0_polling: Stateful Monolithic Prototype
The legacy version relies on a continuous background script runtime loop (Long Polling) to query Telegram's master servers for incoming updates. 
* **State Management:** Session configurations (`pending_event`) are kept entirely in local, ephemeral server memory threads.
* **Task Automation:** Reminders are managed natively using an in-memory execution queue (`APScheduler`).
* **Resource Footprint:** Requires an uninterrupted 24/7 compute instance with active CPU polling loops, making continuous hosting on free or low-tier hosting environments resource-inefficient and unsustainable.

```text
Unstructured Source -> Telegram Polling Loop -> Gemini 2.5 Flash -> Pydantic Validation -> Local User Memory -> Google Calendar API -> Native JobQueue (APScheduler)

```

### v1_webhook: Event-Driven Serverless Production Deployment

The production version refactors the application into a stateless Python Flask microservice exposed via a WSGI cloud gateway.

* **State Management:** Implements a dynamic, light, file-based local session caching layer to safely track validation payloads across independent asynchronous HTTP callback updates.
* **Task Automation:** Decoupled entirely from the application container. Foreground alerts are externalized via webhooks to the `api.cron-job.org` execution engine. Exactly 1 hour before event execution, the external engine issues a POST call back to the app's trigger endpoint.
* **Resource Footprint:** 0% CPU/RAM consumption while idling. The system flashes awake instantly only upon receiving webhook updates from Telegram or cron-job execution pings, enabling true scale-to-zero operation ideal for free cloud containers (such as PythonAnywhere).

```text
Unstructured Source -> Telegram Webhook Pushes -> Flask Microservice -> Gemini 2.5 Flash -> Pydantic Validation -> File Cache State -> Google Calendar API -> External Cron Engine API -> Asynchronous Webhook Trigger

```

---

## Combined Project Directory Structure

```text
CalendarAssist/
│
├── v0_polling/                 # Legacy Monolithic Prototype Module
│   ├── bot.py                  # Main application initialization and polling runtime loop
│   ├── handlers.py             # Core polling message processing routines and job callbacks
│   └── README_V0.txt           # Setup and operational constraints for v0
│
├── v1_webhook/                 # Serverless Production Module
│   ├── app.py                  # Flask Web App microservice web server entry point
│   ├── handlers.py             # Refactored asynchronous webhook callbacks and external cron triggers
│   └── README_V1.txt           # Cloud deployment instructions for v1
│
├── config.py                   # Centralized Configuration parser enforcing variable constraints
├── gemini.py                   # Interfaces Google GenAI SDK and manages vision payloads
├── google_calendar.py          # Manages Google OAuth authorization routines and API service builds
├── models.py                   # Declares strict Pydantic models for data payload contracts
├── requirements.txt            # Unified production-locked system package manifest
└── README.md                   # System-level master architecture documentation

```

---

## Configuration Matrix

System initialization extracts variables either from a root `.env` file or cloud-injected environment blocks:

```ini
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
CRON_JOB_API_KEY=your_cron_job_org_api_key
PYTHONANYWHERE_USERNAME=your_hosting_username

# Stateless Cloud Deployment Fallbacks
GOOGLE_CREDENTIALS_JSON={"installed":{"client_id":"...","project_id":"..."}}
GOOGLE_TOKEN_JSON={"token":"ya29...","refresh_token":"..."}

```

---

## Runtime Execution Matrix

### Running v0_polling (Local Workspace / Continuous VPS)

1. Navigate to the polling folder:
```bash
cd v0_polling

```


2. Launch the long-polling listener:
```bash
python bot.py

```



### Running v1_webhook (Production Serverless - PythonAnywhere)

1. Point your public Web Application WSGI routing entry file directly to `/v1_webhook/app.py`.
2. Configure your serverless workspace environment variables.
3. Establish the live webhook path by calling the following endpoint structure within your browser address bar:
```text
[https://api.telegram.org/bot](https://api.telegram.org/bot)<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_USERNAME>[.pythonanywhere.com/webhook](https://.pythonanywhere.com/webhook)

```


4. Verify response signature: `{"ok":true,"result":true,"description":"Webhook was set"}`

## License

This project is licensed under the terms of the MIT License.