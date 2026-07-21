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

Six sources are wired up, selected with `--source`. **Verified live**
(2026-07-20) — five of the six are blocked or unreliable, all due to
anti-bot protection that isn't fixable by tweaking headers:

| `--source`      | Country / reach       | Live status |
| :--------------- | :--------------------- | :--------- |
| `ebay`           | US/UK/DE/FR/IT/ES/AT/CH/NL/BE/PL/IE | **Working, official — the default.** Real OAuth2 app credentials, eBay's Browse API — no scraping, no anti-bot risk, ever. Needs `EBAY_CLIENT_ID`/`EBAY_CLIENT_SECRET` (see below). |
| `vinted`         | Pan-European (ES/FR/DE/IT/NL/PL/UK/...) | **Blocked as of 2026-07-20.** Was the reliable one through 2026-07-19; now returns a Cloudflare "challenge" response (`cf-mitigated: challenge`) on the homepage itself, before the search call even runs. Same protection tier as Wallapop/Leboncoin/Subito, not a config regression — see below. |
| `kleinanzeigen`  | Germany                | **Unreliable.** Sometimes returns real listings, sometimes an empty JS shell requiring a browser to render — looks like rate-limiting/bot mitigation that kicks in after a few requests, not a hard block. Retries a few times before giving up (see `sources/common.py`). |
| `wallapop`       | Spain                  | **Blocked.** Returns HTTP 403 even with full browser headers (Accept, Accept-Language, Referer, a real Safari user-agent) — an anti-bot system, not a missing header. |
| `leboncoin`      | France                 | **Blocked.** Same 403 regardless of headers. |
| `subito`         | Italy                  | **Blocked.** Same 403 regardless of headers. |

Vinted going from "reliable" to "Cloudflare-blocked" in the space of a
day is the clearest evidence yet that scraping these sites isn't a stable
foundation — it's not that our code got worse, the site's own protection
got stricter. `ebay` is the only source that can't have this happen to it.

### Retry behavior (added 2026-07-20)

`sources/common.py` has two retry helpers, used by `vinted.py` and
`kleinanzeigen.py`:

- `request_with_backoff` — retries on an actual request exception (2s,
  4s, ... backoff). For failures that raise.
- `retry_until_non_empty` — retries when the request *succeeds* (200 OK)
  but comes back with zero listings, which is Kleinanzeigen's actual
  failure mode (an unrendered JS shell, not an error).

Neither is applied to Wallapop/Leboncoin/Subito — retrying a hard 403
faster doesn't help and just hammers a server that's already refusing
you, so those still fail on the first attempt as before.

Each source lives in its own file under `sowld/sources/` and just needs
to return the shared `Listing` type — everything downstream (parsing,
valuation, scoring, alerts) is source-agnostic and doesn't change per
marketplace.

### Why Wallapop/Leboncoin/Subito/Vinted are blocked, and what would "fixing" them actually mean

These four return 403 (or, for Vinted, a Cloudflare challenge) on every
request, including ones with a real browser's exact header set — that
rules out a simple config fix. What's left is either they're blocking
known cloud/datacenter IP ranges
wholesale, or (more likely for consumer marketplaces this size) a bot
detection layer like Cloudflare or DataDome that fingerprints the TLS
handshake and JS environment, which no header can satisfy from a plain
HTTP client.

Getting past that for real would mean running a full headless browser
with stealth patches and likely rotating residential proxies — at that
point it stops being "a low-volume personal script with a realistic
user-agent" (what the SOW's grey-zone framing in §B3 allows) and starts
being purpose-built evasion of security systems those companies
deliberately run. That's a different, much riskier project, and it's not
one this codebase takes on. If a future need justifies it, that's a
conscious call to make with eyes open — not a silent scope creep.

### About the eBay Browse API

The cleanest source here: an **official, free, legal** API, so none of
the blocking/rate-limiting problems above apply, ever. Setup:

1. Go to **developer.ebay.com** → sign up → **My Account → Application
   Keys**
2. Create a **Production** keyset (not Sandbox — Sandbox only returns
   fake test listings)
3. Copy the **Client ID** and **Client Secret** into `EBAY_CLIENT_ID` /
   `EBAY_CLIENT_SECRET`

No callback URL or app review needed for this — the Browse API's
client-credentials flow is available immediately on a new developer
account. `sources/ebay.py` caches the OAuth token in memory and only
re-authenticates when it's about to expire.

One tradeoff: eBay's search results don't include a long description in
the summary view, only the title and a plain-text `condition` field
(e.g. "Used") — that's folded into what gets sent to the parsing step, so
condition detection is a little thinner here than on sources with a full
listing description.

### About kleinanzeigen.py

`kleinanzeigen.py`'s CSS selectors are the *verified* real markup (an
`<li class="j-adlistitem" data-href="...">` per listing) — not a guess.
The unreliability is about how often the server serves that markup vs. an
empty JS shell, not about the parser being wrong. If a run comes back
empty, that's this rate-limiting behavior, not a bug to chase.

### About subito.py

`subito.py` was written without any way to test it against a live
response before this environment had network access; now that it does,
it's confirmed **blocked** the same way Wallapop and Leboncoin are (see
above) — this isn't a parsing bug to fix, the requests themselves never
get a real response. It still tries the page's embedded JSON-LD
structured data first, and falls back to CSS-selector scraping, but
neither path matters until the 403 itself is no longer happening.

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
    wallapop.py         Wallapop fetch implementation (blocked, see below)
    leboncoin.py        Leboncoin fetch implementation (blocked, see below)
    vinted.py            Vinted fetch implementation (working)
    kleinanzeigen.py      Kleinanzeigen fetch implementation (unreliable)
    subito.py             Subito.it fetch implementation (blocked, see below)
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
  these are undocumented and can change without notice — and, as of this
  writing, three of the five (Wallapop, Leboncoin, Subito) are outright
  blocked by anti-bot protection. See "Why Wallapop/Leboncoin/Subito are
  blocked" above.
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
