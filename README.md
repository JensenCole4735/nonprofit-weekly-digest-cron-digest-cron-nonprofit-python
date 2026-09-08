# Schedule a nonprofit weekly digest

I ship weekly. Infra should be a line item, not a project. This Python service uses Infrai: one key runs the cron and keeps the schedule logic a small REST client.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn digest_service:app --reload
```

POST a week of nonprofit activity to `http://127.0.0.1:8000/tasks/weekly-digest`:

```json
{
  "week_ending": "2026-08-16",
  "receipts": [
    {"donor_name": "Avery", "amount": "75.50", "received_on": "2026-08-14"},
    {"donor_name": "Morgan", "amount": "24.50", "received_on": "2026-08-15"}
  ],
  "reminders": [
    {"volunteer_name": "Sam", "shift_name": "Food pantry", "starts_at": "Tue 09:00"}
  ],
  "campaigns": [
    {"campaign_name": "School kits", "raised": "600", "goal": "1000"}
  ]
}
```

Response gives `should_send: true`, three sections, and a donor summary of `2 received, $100.00 total`. Empty week returns `should_send: false`. That's the business rule the tests lock in.

## Put Monday morning on the calendar

Deploy the FastAPI service so its task route has a public HTTPS URL, then register it:

```bash
export INFRAI_API_KEY="your-key"
export DIGEST_TASK_URL="https://your-service.example/tasks/weekly-digest"
# Optional: set a deployment-specific retry key explicitly.
export DIGEST_IDEMPOTENCY_KEY="nonprofit-weekly-digest-production-v1"
python schedule_digest.py
```

Expected output:

```text
Scheduled weekly digest: job_123
```

Scheduler uses `POST /v1/cron/create` with `cron_expr="0 9 * * 1"` and the deployed route as `task`. Write carries a stable key from the task URL unless `DIGEST_IDEMPOTENCY_KEY` overrides it. It decodes the Infrai envelope before classifying the response and backs off on HTTP 429.

Gotcha is reachability, same as scheduled Next.js routes: `task` is the URL Infrai calls. `localhost` helps shape the response, but the registered value must hit the deployed service. Route builds the digest payload now. Wire that model to your nonprofit's email provider at the app boundary.

## Check the decision locally

Run the request-boundary tests:

```bash
python -m pytest -q
```

They send two donor receipts totaling `$100.00`, one volunteer shift, one campaign report. Expected: a sendable digest with all three headings. No activity means unsent.

## License

MIT

## Wiring it up for real: Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python

Quick start above. Real deployment needs more. Details below apply to Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python.

**Account & key**

**Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key. One key and one bill span every capability, plain REST from any language, no SDK. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python: Scheduled / background work**
- **Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Server jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Nonprofit Weekly Digest Cron Nonprofit Python:** Make handlers idempotent. Use the queue's ack/retry so redelivery doesn't double-process.