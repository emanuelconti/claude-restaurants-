# Sowld — Part B: the one function (+ hosted platform)

V0 of the AI buying agent for second-hand goods. One command answers:
"find undervalued road bikes in Barcelona." Nothing else — this is the
proof that the core idea works (see the SOW, Part B).

Two ways to use it, in the same codebase:

- **CLI (`sowld/`, this README)** — a script you run yourself, no hosting,
  no accounts beyond an Anthropic API key. Good for validating the idea
  and for your own personal use.
- **Hosted platform (`webapp/`, see [DEPLOY.md](DEPLOY.md))** — a real
  website with signup, login and a Stripe subscription, that gates the
  same search behind a paywall. This is what you'd link to from the
  Framer site (Part A) as an actual product, not just a waitlist.

They share all the underlying logic (`fetch` → `parse` → `valuation` →
`scoring`) — the webapp is a thin paid front door on top of everything
below.

## Quick start (easiest — guided script)

Requires Python 3 installed (Mac/Linux already have it; on Windows use
[WSL](https://learn.microsoft.com/windows/wsl/install) or Git Bash).

```bash
cd sowld
bash avvia.sh
```

First run: it sets everything up automatically and asks you to paste your
Anthropic API key once (get one free at console.anthropic.com/, click
"API Keys" → "Create Key"). Every run after that just asks what you're
looking for and in which city — nothing else to configure.

## Quick start (manual)

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
`deals.csv` in the current folder. Run it again anytime, or add
`--source vinted` (etc.) for another supported marketplace.

## How it values items — no dataset needed

There's no sold-price dataset yet, so this doesn't fake one. It uses the
listings themselves as the reference:

1. Fetch current listings for a query + city, from whichever marketplace
   you pick with `--source`.
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
python -m sowld "road bike" "Barcelona" --source vinted
python -m sowld "road bike" "Barcelona" --threshold 0.3 --max-results 60
python -m sowld "road bike" "Barcelona" --telegram   # needs TELEGRAM_BOT_TOKEN/CHAT_ID
python -m sowld "road bike" "Barcelona" --email       # needs GMAIL_USER/GMAIL_APP_PASSWORD
```

## Multiple marketplaces

Five of Europe's main second-hand marketplaces are wired up, selected
with `--source`:

| `--source`      | Country / reach       | Confidence |
| :--------------- | :--------------------- | :--------- |
| `wallapop`       | Spain                  | Reverse-engineered internal API — same pattern the SOW itself proposes for V0. |
| `leboncoin`      | France                 | Reverse-engineered internal API, same caveats as Wallapop. |
| `vinted`         | Pan-European (ES/FR/DE/IT/NL/PL/UK/...) | Reverse-engineered but **well-documented by the community** (e.g. the pyVinted project) — the highest-confidence of the non-official sources. |
| `kleinanzeigen`  | Germany                | **Experimental.** HTML scrape (JSON-LD first, CSS fallback) — not yet exercised against a live page, see below. |
| `subito`         | Italy                  | **Experimental.** Same approach and caveat as Kleinanzeigen. |

Each source lives in its own file under `sowld/sources/` and just needs
to return the shared `Listing` type — everything downstream (parsing,
valuation, scoring, alerts) is source-agnostic and doesn't change per
marketplace. Adding another one means writing a new `sources/<name>.py`
with a matching `fetch_listings(query, location, max_results, delay)`
function and registering it in `fetch.py`'s `SOURCES` dict.

Other platforms considered and why they're not in yet:

- **eBay**: has an official, free, legal **Browse API** — the cleanest
  option of all, and the SOW suggests it later as a way to sanity-check
  the median with real reference prices. Worth adding next.
- **Marktplaats (Netherlands), OLX (Poland/Romania/Portugal)**: same
  reverse-engineering approach as Kleinanzeigen/Subito would apply —
  straightforward to add following that pattern once it's been validated.
- **Facebook Marketplace / Groups**: not realistically scrapeable without
  violating their ToS in a way this project won't do — skipped.

### About the two "experimental" sources

`kleinanzeigen.py` and `subito.py` were written without any way to test
them against a live response — this environment currently has no network
access to those sites. They try the page's embedded JSON-LD structured
data first (a relatively stable target many sites use for SEO), and fall
back to CSS-selector scraping with best-guess class names if no JSON-LD
is found. **The first real run against each is the actual test.** If
`fetch_listings` comes back empty, open the search URL in a browser,
inspect a listing card's HTML, and update the selectors in `_scrape_html`
— that's expected, one-time maintenance, not a sign something is
fundamentally broken.

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
  fetch.py             dispatches to the right source module (step 1)
  sources/
    common.py          shared Listing type, geocoding, JSON-LD helper
    wallapop.py         Wallapop fetch implementation
    leboncoin.py        Leboncoin fetch implementation
    vinted.py            Vinted fetch implementation
    kleinanzeigen.py      Kleinanzeigen fetch implementation (experimental)
    subito.py             Subito.it fetch implementation (experimental)
  parse.py             step 2 — Claude structures each listing
  valuation.py          step 3 — condition-adjusted median fair value per group
  scoring.py             step 4 — deal_score, filter, rank
  output.py               step 5 — table + CSV
  telegram.py              step 6a — send the top deals to a Telegram chat
  mailer.py                 step 6b — send the top deals by email
  cli.py                    wires it all into one command
tests/
  test_valuation.py         pure-logic tests, no network/API needed
  test_scoring.py
  test_fetch_dispatch.py    source registry + JSON-LD helper
  test_html_sources.py      Kleinanzeigen/Subito parsing against fake HTML
```

Run the offline tests any time with:

```bash
pip install pytest
pytest tests/
```

## Data-access reality — read before relying on this in production

*(from the SOW, section B3)*

- **None of these marketplaces have a public API.** Wallapop, Leboncoin
  and Vinted use reverse-engineered internal JSON endpoints; Kleinanzeigen
  and Subito.it scrape the search-results HTML page directly. All of
  these are undocumented and can change or break without notice — if
  `fetch_listings` starts returning nothing for a source, make a manual
  request (or open the search URL in a browser) and check whether the
  request/response shape has drifted. See "About the two experimental
  sources" above for Kleinanzeigen/Subito specifically.
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
