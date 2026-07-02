#!/usr/bin/env python3
"""
LeadForge — Automated Cold Email Outreach Engine
Send a 3-step follow-up sequence to any list of leads, with SQLite tracking,
daily send limits, opt-out handling and Gmail SMTP delivery.

This is a generic, niche-agnostic version of a cold-outreach system battle
tested on real campaigns (thousands of emails sent to local businesses).

Setup:
  1. pip install -r requirements.txt
  2. Create a Gmail App Password: myaccount.google.com/apppasswords
  3. Copy config.example.py to config.py and fill in your details
  4. Put your leads in leads.csv (see leads_template.csv for the format)

Usage:
  python3 leadforge.py import          # load leads.csv into the tracking DB
  python3 leadforge.py run             # send whatever is due today
  python3 leadforge.py status          # see pipeline status
  python3 leadforge.py replied contact@example.com   # mark as replied (stops sequence)
  python3 leadforge.py optout contact@example.com     # mark as opted out (stops sequence)
"""

import csv
import sqlite3
import smtplib
import socket
import time
import logging
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path

try:
    import config
except ImportError:
    print("Missing config.py — copy config.example.py to config.py and fill it in.")
    sys.exit(1)

BASE_DIR   = Path(__file__).parent
DB_FILE    = BASE_DIR / "leadforge_tracking.db"
LEADS_FILE = BASE_DIR / "leads.csv"
LOG_FILE   = BASE_DIR / "leadforge.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


# ── DATABASE ─────────────────────────────────────────────────────────────────
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS leads (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    NOT NULL UNIQUE,
            company    TEXT,
            added_at   TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS outreach (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id      INTEGER NOT NULL,
            step         INTEGER NOT NULL,
            sent_at      TEXT,
            status       TEXT DEFAULT 'pending',   -- pending, sent, replied, optout, error
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        );
    """)
    conn.commit()
    conn.close()


def import_leads():
    if not LEADS_FILE.exists():
        log.error(f"{LEADS_FILE} not found. Copy leads_template.csv to leads.csv and fill it in.")
        return
    conn = get_conn()
    added = 0
    with open(LEADS_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name, email, company = row.get("name", "").strip(), row.get("email", "").strip().lower(), row.get("company", "").strip()
            if not email:
                continue
            try:
                cur = conn.execute("INSERT INTO leads (name, email, company) VALUES (?, ?, ?)", (name, email, company))
                lead_id = cur.lastrowid
                for step in (1, 2, 3):
                    conn.execute("INSERT INTO outreach (lead_id, step, status) VALUES (?, ?, 'pending')", (lead_id, step))
                added += 1
            except sqlite3.IntegrityError:
                continue  # already imported
    conn.commit()
    conn.close()
    log.info(f"Imported {added} new leads from {LEADS_FILE.name}")


# ── EMAIL SENDING ────────────────────────────────────────────────────────────
def send_email(to_email: str, subject: str, body: str) -> bool:
    msg = MIMEMultipart()
    msg["From"] = f"{config.SENDER_NAME} <{config.GMAIL_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
            server.sendmail(config.GMAIL_USER, to_email, msg.as_string())
        return True
    except (smtplib.SMTPException, socket.error) as e:
        log.error(f"Send failed to {to_email}: {e}")
        return False


def due_outreach():
    """Return outreach rows due to be sent today, respecting per-step delays."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT o.id AS outreach_id, o.step, l.id AS lead_id, l.name, l.email, l.company,
               (SELECT sent_at FROM outreach WHERE lead_id = l.id AND step = 1) AS step1_sent
        FROM outreach o
        JOIN leads l ON l.id = o.lead_id
        WHERE o.status = 'pending'
        ORDER BY o.step, l.id
    """).fetchall()
    conn.close()

    due = []
    now = datetime.now()
    for r in rows:
        if r["step"] == 1:
            due.append(r)
        else:
            if not r["step1_sent"]:
                continue
            sent_at = datetime.fromisoformat(r["step1_sent"])
            delay_days = config.DELAY_STEP_2_DAYS if r["step"] == 2 else config.DELAY_STEP_3_DAYS
            if now >= sent_at + timedelta(days=delay_days):
                due.append(r)
    return due


def run():
    init_db()
    conn = get_conn()
    sent_today = 0
    for row in due_outreach():
        if sent_today >= config.MAX_PER_DAY:
            log.info(f"Daily limit ({config.MAX_PER_DAY}) reached, stopping.")
            break

        subject, body = config.get_template(row["step"], row["name"], row["company"])
        ok = send_email(row["email"], subject, body)
        status = "sent" if ok else "error"
        conn.execute(
            "UPDATE outreach SET status = ?, sent_at = ? WHERE id = ?",
            (status, datetime.now().isoformat() if ok else None, row["outreach_id"]),
        )
        conn.commit()
        log.info(f"Step {row['step']} -> {row['email']}: {status}")
        if ok:
            sent_today += 1
            time.sleep(config.PAUSE_BETWEEN_SECONDS)
    conn.close()
    log.info(f"Run complete. {sent_today} emails sent.")


def status():
    init_db()
    conn = get_conn()
    total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    counts = conn.execute("SELECT status, COUNT(*) AS n FROM outreach GROUP BY status").fetchall()
    conn.close()
    print(f"Leads: {total_leads}")
    for row in counts:
        print(f"  {row['status']}: {row['n']}")


def mark(email: str, new_status: str):
    conn = get_conn()
    lead = conn.execute("SELECT id FROM leads WHERE email = ?", (email.lower(),)).fetchone()
    if not lead:
        print(f"No lead found for {email}")
        return
    conn.execute("UPDATE outreach SET status = ? WHERE lead_id = ? AND status = 'pending'", (new_status, lead["id"]))
    conn.commit()
    conn.close()
    print(f"{email} -> {new_status}")


if __name__ == "__main__":
    init_db()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "import":
        import_leads()
    elif cmd == "run":
        run()
    elif cmd == "status":
        status()
    elif cmd == "replied" and len(sys.argv) > 2:
        mark(sys.argv[2], "replied")
    elif cmd == "optout" and len(sys.argv) > 2:
        mark(sys.argv[2], "optout")
    else:
        print(__doc__)
