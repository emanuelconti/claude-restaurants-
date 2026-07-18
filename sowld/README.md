# Sowld — Part B: the one function

V0 of the AI buying agent for second-hand goods. One command answers:
"find undervalued road bikes in Barcelona." Nothing else — this is the
proof that the core idea works (see the SOW, Part B).

This is a **backend script, not a web widget** — there's nothing to embed
in the Framer site (Part A). The Framer site just collects waitlist
emails; this tool is what you (or a scheduled job) run to get deal
alerts. The two are independent deliverables.

## Quick start

```bash
cd sowld
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# open .env and set ANTHROPIC_API_KEY at minimum
# (get one at https://console.anthropic.com/)

python -m sowld "road bike" "Barcelona"
```

That's it — it prints a table of underpriced listings and saves them to
`deals.csv` in the current folder. Run it again anytime, or from
`--source leboncoin` for the other supported marketplace.

## How it values items — no dataset needed

There's no sold-price dataset yet, so this doesn't fake one. It uses the
listings themselves as the reference:

1. Fetch current listings for a query + city (Wallapop or Leboncoin).
2. Use Claude to turn each messy listing into structure:
   `{brand, model, variant, year, size, condition_score}`.
3. Group comparables by brand + model.
4. Fair value = the median asking price of its comparables, adjusted for
   condition (±10% per point away from "average").
5. Deal score = `(fair_value - price) / fair_value`. Anything ≥ 25% under
   is flagged by default.
6. Rank and output the underpriced ones as a table + CSV.

Pure comparables-based pricing: it finds items priced below their own
market, and it's hard to argue with. (Later, real sold prices can replace
the median and it gets stronger — see B1 in the SOW.)

## Usage

```bash
python -m sowld "road bike" "Barcelona"
python -m sowld "road bike" "Barcelona" --source leboncoin
python -m sowld "road bike" "Barcelona" --threshold 0.3 --max-results 60
python -m sowld "road bike" "Barcelona" --telegram   # needs TELEGRAM_BOT_TOKEN/CHAT_ID
python -m sowld "road bike" "Barcelona" --email       # needs GMAIL_USER/GMAIL_APP_PASSWORD
```

## Multiple marketplaces

Currently supported: **Wallapop** (default) and **Leboncoin**, selected
with `--source`. Each lives in its own file under `sowld/sources/` and
just needs to return the shared `Listing` type — everything downstream
(parsing, valuation, scoring, alerts) is source-agnostic and doesn't
change per marketplace.

Adding another one (eBay, Vinted, ...) means writing a new
`sources/<name>.py` with a `fetch_listings(query, location, max_results,
delay)` function and registering it in `fetch.py`'s `SOURCES` dict.
Reality check per platform:

- **Wallapop / Leboncoin**: no public API — both use a reverse-engineered
  internal endpoint (see "Data-access reality" below).
- **eBay**: has an official, free, legal **Browse API** — the cleanest
  option, and the SOW suggests it later as a way to sanity-check the
  median with real reference prices.
- **Facebook Marketplace / Groups**: not realistically scrapeable without
  violating their ToS in a way this project won't do — skip it.
- **Vinted**: similar situation to Wallapop/Leboncoin, unofficial
  endpoint, same caveats would apply if added.

## Alert channels: Telegram vs. email

Both are supported, pick whichever fits:

- **`--telegram`** (what the SOW proposes first): create a bot with
  [@BotFather](https://t.me/BotFather) in about 30 seconds, message it
  once, grab your chat ID from
  `https://api.telegram.org/bot<TOKEN>/getUpdates`. One HTTP call per
  alert, arrives instantly on your phone, no app-specific password needed.
- **`--email`** (`mailer.py`): reuses the same Gmail app-password pattern
  already used elsewhere in this repo (`outreach.py`). No bot to set up,
  but slightly less immediate than a push notification.

Other channels (WhatsApp Business API, SMS via Twilio, push
notifications) were skipped for V0: WhatsApp needs business approval and
cost, SMS is paid per message, and push notifications need an actual app
to push into. Telegram/email cover "get pinged" with zero friction.

## Project layout

```
sowld/
  fetch.py           dispatches to the right source module (step 1)
  sources/
    common.py        shared Listing type + geocoding helper
    wallapop.py       Wallapop fetch implementation
    leboncoin.py      Leboncoin fetch implementation
  parse.py            step 2 — Claude structures each listing
  valuation.py         step 3 — condition-adjusted median fair value per group
  scoring.py           step 4 — deal_score, filter, rank
  output.py            step 5 — table + CSV
  telegram.py           step 6a — send the top deals to a Telegram chat
  mailer.py              step 6b — send the top deals by email
  cli.py                wires it all into one command
tests/
  test_valuation.py     pure-logic tests, no network/API needed
  test_scoring.py
```

Run the offline tests any time with:

```bash
pip install pytest
pytest tests/
```

## Data-access reality — read before relying on this in production

*(from the SOW, section B3)*

- **Wallapop and Leboncoin have no public API.** Both fetchers use a
  community-known internal JSON endpoint. These are undocumented and can
  change or break without notice — if `fetch_listings` starts returning
  nothing, make a manual request in a browser's Network tab and check
  whether the request/response shape (or Leboncoin's `api_key` header)
  has drifted.
- This is the grey-zone, personal/low-volume use discussed in the
  strategy doc: keep request volume low, use a realistic user-agent (set
  already), respect rate limits, and store **no seller personal data** —
  only title, price, description, url, location, photo URLs, which is all
  `Listing` keeps.
- A cleaner, fully legal option for a *reference* price is eBay's
  official Browse API — useful later to sanity-check the median, not
  required for V0.
- This is fine for V0/personal use. Before turning this into a public
  product with many users, revisit the strategy doc and talk to a lawyer.

## Notes

- Groups with fewer than 2 comparable listings are skipped — there's
  nothing to compare them against, so no fair value is computed.
- Listings Claude can't assign a brand/model to are skipped for the same
  reason.
- `ANTHROPIC_API_KEY` is always required; `TELEGRAM_BOT_TOKEN`/
  `TELEGRAM_CHAT_ID` only for `--telegram`, `GMAIL_USER`/
  `GMAIL_APP_PASSWORD` only for `--email`.
