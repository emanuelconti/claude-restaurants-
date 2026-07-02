# LeadForge — Quickstart

## 1. Install

```bash
pip install -r requirements.txt
```

## 2. Get a Gmail App Password

1. Turn on 2-Step Verification: https://myaccount.google.com/security
2. Create an App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character password

## 3. Configure

```bash
cp config.example.py config.py
```

Open `config.py` and edit:
- `GMAIL_USER` — your Gmail address
- `GMAIL_APP_PASSWORD` — the app password from step 2 (or set it as an
  environment variable `GMAIL_APP_PASSWORD` instead of hardcoding it)
- `SENDER_NAME`, `YOUR_COMPANY`, `YOUR_OFFER_LINK`
- The 3 email templates inside `get_template()` — replace the bracketed
  placeholders with your actual pitch

## 4. Add your leads

```bash
cp leads_template.csv leads.csv
```

Fill in `leads.csv` with `name,email,company` rows — one per lead.

## 5. Import and run

```bash
python3 leadforge.py import
python3 leadforge.py run
```

Check progress any time with `python3 leadforge.py status`.

## 6. Automate it (optional)

Run daily with cron:

```
0 9 * * * cd /path/to/leadforge && python3 leadforge.py run >> cron.log 2>&1
```

Or use a free GitHub Actions scheduled workflow (`.github/workflows/leadforge.yml`
in your own repo) with `GMAIL_APP_PASSWORD` stored as a repository secret —
this is exactly how the original system this tool is based on runs in
production, at zero hosting cost.
