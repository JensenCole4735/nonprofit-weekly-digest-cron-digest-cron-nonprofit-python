"""Register the hosted digest route as a weekly cron task."""

from __future__ import annotations

import os
from hashlib import sha256

from infrai_client import InfraiClient


def schedule_weekly_digest() -> str:
    task_url = os.environ["DIGEST_TASK_URL"]
    idempotency_key = os.environ.get("DIGEST_IDEMPOTENCY_KEY") or (
        f"nonprofit-weekly-digest-{sha256(task_url.encode()).hexdigest()[:16]}"
    )
    result = InfraiClient().create_cron(
        cron_expr="0 9 * * 1",
        task=task_url,
        idempotency_key=idempotency_key,
    )
    return str(result["job_id"])


if __name__ == "__main__":
    print(f"Scheduled weekly digest: {schedule_weekly_digest()}")
