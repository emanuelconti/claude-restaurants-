# LeadForge — Automated Cold Email Outreach Engine

Send a proven 3-step follow-up email sequence to any list of leads, automatically,
without touching your inbox by hand. Built from a real system that has sent
thousands of outreach emails to acquire business partners.

## What you get

- `leadforge.py` — the automation engine (Python, ~250 lines, no external
  services required beyond your Gmail account)
- SQLite tracking so every lead's sequence state is remembered — no duplicate
  or missed emails
- Automatic daily send cap and pacing to stay under spam filters
- One-command opt-out / reply handling so you never annoy someone who already
  responded
- `config.example.py` — plug in your name, offer link and email copy
- `leads_template.csv` — the exact column format to drop your list into

## Who this is for

Freelancers, agencies, and small business owners who want to reach local
businesses, prospects or partners by email without paying $50-200/month for a
cold email SaaS. You already have the leads (or can find them on Google
Maps / LinkedIn) — this handles the sending, sequencing and tracking.

## Setup (10 minutes)

1. `pip install -r requirements.txt`
2. Create a Gmail App Password: https://myaccount.google.com/apppasswords
   (requires 2-Step Verification enabled on your Google account)
3. `cp config.example.py config.py` and fill in your name, company, offer
   link and the 3 email templates
4. `cp leads_template.csv leads.csv` and fill in your leads (name, email,
   company)
5. `python3 leadforge.py import`
6. `python3 leadforge.py run`

Run `leadforge.py run` daily (cron, Task Scheduler, or a GitHub Actions
workflow — see `QUICKSTART.md` for a ready-made one) and the sequence takes
care of itself.

## Commands

```
python3 leadforge.py import                        # load leads.csv into the DB
python3 leadforge.py run                            # send what's due today
python3 leadforge.py status                         # see pipeline counts
python3 leadforge.py replied someone@example.com    # stop sequence, they replied
python3 leadforge.py optout someone@example.com     # stop sequence, they opted out
```

## Why Gmail SMTP and SQLite, not a SaaS

No monthly fee, no per-seat pricing, no vendor lock-in. It runs on your
machine or a free GitHub Actions runner. You own the list and the data.

## Fair use

Cold email is legal in most jurisdictions when it's B2B, relevant, and offers
an easy opt-out — but rules differ by country (e.g. GDPR in the EU, CAN-SPAM
in the US). You are responsible for complying with the laws that apply to
your leads. Keep your daily volume reasonable and always honor opt-outs.
