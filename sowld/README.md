# Sowld — Part B: the one function

V0 of the AI buying agent for second-hand goods. One command answers:
"find undervalued road bikes in Barcelona." Nothing else — this is the
proof that the core idea works (see the SOW, Part B).

## How it values items — no dataset needed

There's no sold-price dataset yet, so this doesn't fake one. It uses the
listings themselves as the reference:

1. Fetch current listings for a query + city (Wallapop).
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

## Setup

```bash
cd sowld
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
```

## Usage

```bash
python -m sowld "road bike" "Barcelona"
python -m sowld "road bike" "Barcelona" --threshold 0.3 --max-results 60
python -m sowld "road bike" "Barcelona" --telegram   # also needs TELEGRAM_BOT_TOKEN/CHAT_ID
```

Prints a table of the underpriced listings found and saves the same data
to `deals.csv`.

## Project layout

```
sowld/
  fetch.py      step 1 — query + city -> raw listings (Wallapop)
  parse.py      step 2 — Claude structures each listing
  valuation.py  step 3 — condition-adjusted median fair value per group
  scoring.py    step 4 — deal_score, filter, rank
  output.py     step 5 — table + CSV
  telegram.py   step 6 — send the top deals to a Telegram chat
  cli.py        wires it all into one command
tests/
  test_valuation.py   pure-logic tests, no network/API needed
  test_scoring.py
```

Run the offline tests any time with:

```bash
pip install pytest
pytest tests/
```

## Data-access reality — read before relying on this in production

*(from the SOW, section B3)*

- **Wallapop has no public API.** `fetch.py` uses a community-known
  internal JSON endpoint. It is undocumented and can change or break
  without notice — if `fetch_listings` starts returning nothing, make a
  manual request and check whether the response shape has drifted.
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
- `ANTHROPIC_API_KEY` is required; `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`
  are only needed with `--telegram`.
