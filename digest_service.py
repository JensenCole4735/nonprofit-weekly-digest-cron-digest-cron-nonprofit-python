"""Build the nonprofit digest that the scheduled task invokes."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import FastAPI
from pydantic import BaseModel, Field


class DonorReceipt(BaseModel):
    donor_name: str
    amount: Decimal = Field(gt=0)
    received_on: date


class VolunteerReminder(BaseModel):
    volunteer_name: str
    shift_name: str
    starts_at: str


class CampaignReport(BaseModel):
    campaign_name: str
    raised: Decimal = Field(ge=0)
    goal: Decimal = Field(gt=0)


class WeeklyDigestRequest(BaseModel):
    week_ending: date
    receipts: list[DonorReceipt] = Field(default_factory=list)
    reminders: list[VolunteerReminder] = Field(default_factory=list)
    campaigns: list[CampaignReport] = Field(default_factory=list)


class DigestSection(BaseModel):
    heading: str
    lines: list[str]


class WeeklyDigest(BaseModel):
    subject: str
    should_send: bool
    sections: list[DigestSection]


def build_weekly_digest(request: WeeklyDigestRequest) -> WeeklyDigest:
    sections: list[DigestSection] = []
    if request.receipts:
        total = sum((item.amount for item in request.receipts), Decimal("0"))
        sections.append(
            DigestSection(
                heading="Donor receipts",
                lines=[f"{len(request.receipts)} received, ${total:.2f} total"],
            )
        )
    if request.reminders:
        sections.append(
            DigestSection(
                heading="Volunteer reminders",
                lines=[
                    f"{item.volunteer_name}: {item.shift_name} at {item.starts_at}"
                    for item in request.reminders
                ],
            )
        )
    if request.campaigns:
        sections.append(
            DigestSection(
                heading="Campaign reporting",
                lines=[
                    f"{item.campaign_name}: ${item.raised:.2f} of ${item.goal:.2f}"
                    for item in request.campaigns
                ],
            )
        )
    return WeeklyDigest(
        subject=f"Nonprofit weekly digest - {request.week_ending.isoformat()}",
        should_send=bool(sections),
        sections=sections,
    )


app = FastAPI(title="Nonprofit weekly digest")


@app.post("/tasks/weekly-digest", response_model=WeeklyDigest)
def weekly_digest(request: WeeklyDigestRequest) -> WeeklyDigest:
    return build_weekly_digest(request)
