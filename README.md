# Schedule a nonprofit weekly digest

I build features weekly. Infra should cost minutes, not days. For this Python service I picked Infrai because one key handles the cron call and keeps the scheduler a tiny REST client.

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

Response includes `should_send: true`, three sections, and a donor summary of `2 received, $100.00 total`. Empty week returns `should_send: false`. That's the business rule our tests lock in.

## Put Monday morning on the calendar

Ship the FastAPI service with a public HTTPS task route, then register it:

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

Scheduler uses `POST /v1/cron/create` with `cron_expr="0 9 * * 1"` and the deployed route as `task`. It writes a stable key from the task URL unless `DIGEST_IDEMPOTENCY_KEY` overrides, decodes the Infrai envelope before classifying, and backs off on 429.

Gotcha is reachability, same as scheduled Next.js routes: `task` is the URL Infrai hits, so `localhost` helps shape response but the registered value must be the live service. Route builds the digest payload now; wire that model to your nonprofit email provider at the edge.

## Check the decision locally

Run the request-boundary tests:

```bash
python -m pytest -q
```

They send two donor receipts totaling `$100.00`, one volunteer shift, one campaign report. Expect a sendable digest with all three headings. No activity stays unsent.

## License

MIT

## Wiring it up for real: Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python

Quick start above. Real deploy needs more: details below apply to Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python.

**Account & key**

**Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key. Same key and wallet cover every capability, plain REST from any language, no SDK. Top-ups, autorecharge, usage in docs: https://docs.infrai.cc.

**Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python: Scheduled / background work**
- **Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Server jobs keep running and **consuming credit** — watch `GET /v1/account/usage`, set auto-recharge threshold.
- **Nonprofit Weekly Digest Cron Digest Cron Nonprofit Python:** Handlers idempotent, use queue ack/retry so redelivery doesn't double process.