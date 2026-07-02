"""
LeadForge configuration.
Copy this file to config.py and fill in your details. config.py is gitignored
so your credentials never get committed.
"""

import os

# ── SENDER ────────────────────────────────────────────────────────────────
GMAIL_USER         = os.getenv("GMAIL_USER", "you@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")   # myaccount.google.com/apppasswords
SENDER_NAME        = "Your Name"
YOUR_COMPANY        = "Your Company"
YOUR_OFFER_LINK      = "https://your-link.example.com"

# ── SENDING BEHAVIOUR ────────────────────────────────────────────────────────
DELAY_STEP_2_DAYS    = 3    # days between email 1 -> email 2
DELAY_STEP_3_DAYS    = 7    # days between email 1 -> email 3
MAX_PER_DAY          = 15   # cap to avoid spam flags on a normal Gmail inbox
PAUSE_BETWEEN_SECONDS = 12  # pause between individual sends


# ── EMAIL TEMPLATES ───────────────────────────────────────────────────────────
# {name} = lead first/full name, {company} = lead company name
def get_template(step: int, name: str, company: str) -> tuple[str, str]:
    display_name = name or "there"

    if step == 1:
        subject = f"Quick idea for {company}" if company else "Quick idea for you"
        body = f"""\
Hi {display_name},

I help businesses like {company or "yours"} with [YOUR VALUE PROPOSITION HERE].

I put together a short overview of how this could work for you:
{YOUR_OFFER_LINK}

Would you be open to a quick look?

Best,
{SENDER_NAME}
{YOUR_COMPANY}"""

    elif step == 2:
        subject = f"Re: Quick idea for {company}" if company else "Re: Quick idea for you"
        body = f"""\
Hi {display_name},

Just following up on my previous note — did you get a chance to look?

Here's the link again in case it's useful: {YOUR_OFFER_LINK}

Happy to answer any questions.

Best,
{SENDER_NAME}"""

    elif step == 3:
        subject = f"Last note — {company}" if company else "Last note"
        body = f"""\
Hi {display_name},

This will be my last email on this — I don't want to clutter your inbox.

If it's useful down the line, the link is here: {YOUR_OFFER_LINK}

All the best,
{SENDER_NAME}"""

    else:
        raise ValueError(f"Invalid step: {step}")

    return subject, body
