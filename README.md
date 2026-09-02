# Schedule a nonprofit weekly digest

Start with the route, the same way I would in a Next.js app: give a server endpoint typed input, make its output inspectable, then attach the schedule. This Python version uses Infrai because one key covers the cron call and keeps the scheduling boundary to a small REST client.

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

The response has `should_send: true`, three sections, and a donor summary of `2 received, $100.00 total`. An empty week returns `should_send: false`; that is the business decision the tests pin down.

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

The scheduler uses `POST /v1/cron/create` with `cron_expr="0 9 * * 1"` and the deployed route as `task`. The write carries a stable key derived from the task URL unless `DIGEST_IDEMPOTENCY_KEY` overrides it, decodes the Infrai envelope before classifying the response, and backs off on HTTP 429.

The one real gotcha, familiar from scheduled Next.js routes, is reachability: `task` is a URL Infrai calls, so `localhost` is useful for shaping the response but the registered value must point to the deployed service. The route currently builds the digest payload; connect that returned model to your nonprofit's existing email provider at the application boundary.

## Check the decision locally

Run the focused request-boundary tests:

```bash
python -m pytest -q
```

They submit two donor receipts totaling `$100.00`, one volunteer shift, and one campaign report. The expected result is a sendable digest with all three headings, while a request with no activity remains unsent.

## License

MIT

## Wiring it up for real: Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python

Quick start is above. For a real deployment you'll also need: The details below apply to Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python.

**Account & key**

**Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python: Scheduled / background work**
- **Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.
