"""Email delivery: send the top deals via Gmail SMTP — an alternative to Telegram.

Telegram is the default because it needs no app password and delivers
instantly to a phone via one HTTP call. Email works just as well and
reuses the same Gmail app-password pattern already used elsewhere in this
repo (see outreach.py) — handy if you'd rather not set up a bot.
"""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText

from .valuation import ValuedListing

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
MAX_DEALS_IN_EMAIL = 20


def send_deals_email(
    deals: list[ValuedListing],
    to_address: str | None = None,
    gmail_user: str | None = None,
    gmail_app_password: str | None = None,
) -> None:
    gmail_user = gmail_user or os.environ.get("GMAIL_USER")
    gmail_app_password = gmail_app_password or os.environ.get("GMAIL_APP_PASSWORD")
    to_address = to_address or os.environ.get("DEALS_EMAIL_TO") or gmail_user
    if not gmail_user or not gmail_app_password or not to_address:
        raise RuntimeError(
            "GMAIL_USER, GMAIL_APP_PASSWORD and a recipient (DEALS_EMAIL_TO, "
            "or GMAIL_USER itself) must be set (in .env or passed in)"
        )

    if not deals:
        body = "No underpriced deals found today."
    else:
        blocks = []
        for d in deals[:MAX_DEALS_IN_EMAIL]:
            listing = d.parsed.listing
            blocks.append(
                f"{listing.title} — {listing.price:.0f}€ "
                f"(fair ~{d.fair_value:.0f}€, {d.deal_score:.0%} under)\n{listing.url}"
            )
        body = "\n\n".join(blocks)

    msg = MIMEText(body)
    msg["Subject"] = f"Sowld — {len(deals)} deal(s) found"
    msg["From"] = gmail_user
    msg["To"] = to_address

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, [to_address], msg.as_string())
