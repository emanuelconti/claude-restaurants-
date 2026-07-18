"""One command: given a query + city, print and save the underpriced deals.

Usage:
    python -m sowld "road bike" "Barcelona"
    python -m sowld "road bike" "Barcelona" --threshold 0.3 --telegram
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from .fetch import fetch_listings
from .output import print_table, save_csv
from .parse import parse_listings
from .scoring import DEFAULT_THRESHOLD, filter_and_rank
from .telegram import send_deals
from .valuation import compute_fair_values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find second-hand listings priced well below their own market."
    )
    parser.add_argument("query", help='What to search for, e.g. "road bike"')
    parser.add_argument("location", help='City to search near, e.g. "Barcelona"')
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Minimum deal score to flag, as a fraction (default {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=40,
        help="Max listings to fetch (default 40)",
    )
    parser.add_argument(
        "--csv",
        default="deals.csv",
        help="CSV output path (default deals.csv)",
    )
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Also send the results to Telegram (needs TELEGRAM_BOT_TOKEN/CHAT_ID)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = build_parser().parse_args(argv)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

    print(f"Fetching listings for '{args.query}' near {args.location}...")
    listings = fetch_listings(args.query, args.location, max_results=args.max_results)
    print(f"Found {len(listings)} listings. Parsing with Claude...")

    parsed = parse_listings(listings, api_key=api_key)
    valued = compute_fair_values(parsed)
    deals = filter_and_rank(valued, threshold=args.threshold)

    print_table(deals)
    save_csv(deals, args.csv)
    print(f"\nSaved {len(deals)} deal(s) to {args.csv}")

    if args.telegram:
        send_deals(deals)
        print("Sent to Telegram.")


if __name__ == "__main__":
    main()
