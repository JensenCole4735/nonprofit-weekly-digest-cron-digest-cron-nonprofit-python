from decimal import Decimal

from fastapi.testclient import TestClient

from digest_service import app


client = TestClient(app)


def test_digest_groups_nonprofit_work_and_decides_to_send() -> None:
    response = client.post(
        "/tasks/weekly-digest",
        json={
            "week_ending": "2026-08-16",
            "receipts": [
                {"donor_name": "Avery", "amount": "75.50", "received_on": "2026-08-14"},
                {"donor_name": "Morgan", "amount": "24.50", "received_on": "2026-08-15"},
            ],
            "reminders": [
                {"volunteer_name": "Sam", "shift_name": "Food pantry", "starts_at": "Tue 09:00"}
            ],
            "campaigns": [
                {"campaign_name": "School kits", "raised": "600", "goal": "1000"}
            ],
        },
    )

    assert response.status_code == 200
    digest = response.json()
    assert digest["should_send"] is True
    assert [section["heading"] for section in digest["sections"]] == [
        "Donor receipts",
        "Volunteer reminders",
        "Campaign reporting",
    ]
    assert digest["sections"][0]["lines"] == ["2 received, $100.00 total"]


def test_empty_week_is_not_sent() -> None:
    response = client.post(
        "/tasks/weekly-digest",
        json={"week_ending": "2026-08-16"},
    )

    assert response.status_code == 200
    assert response.json()["should_send"] is False
    assert response.json()["sections"] == []
