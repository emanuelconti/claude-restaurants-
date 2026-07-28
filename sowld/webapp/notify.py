"""Best-effort email notification when someone joins the waitlist.

Uses Gmail SMTP with an App Password (the Google account needs 2-Step
Verification on, then an App Password generated for it) — no separate
transactional-email account to sign up for. A failed or unconfigured send
never blocks the signup itself: the record is already in the database by
the time this runs.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("GMAIL_USER", "")
SMTP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "sowld.team@gmail.com")


def is_configured() -> bool:
    return bool(SMTP_USER and SMTP_PASSWORD)


def notify_new_signup(email: str, country: str, category: str) -> None:
    if not is_configured():
        return

    msg = EmailMessage()
    msg["Subject"] = "Nuova iscrizione alla waitlist Sowld"
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_EMAIL
    msg.set_content(f"Email: {email}\nPaese: {country}\nCategoria: {category}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)
    except (smtplib.SMTPException, OSError):
        logger.warning("Failed to send waitlist notification email", exc_info=True)
