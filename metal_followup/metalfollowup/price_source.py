"""
Where the metal price comes from.

For this prototype the price is a manual input: a CLI argument, or a
fallback in config/prices.json. There is deliberately no network call here --
the task's hedging/pre-hedging decision stays with a human, and this tool
does not scrape or trust a live feed for that decision.

fetch_price_from_lme() is a placeholder with the signature a real source
would need, so that plugging one in later (LME API, a Bloomberg/Refinitiv
feed, whatever the desk actually licenses) doesn't require touching any
other module -- callers only ever ask resolve_price() for a number.
"""

import json
import os
from typing import Optional


def fetch_price_from_lme(metal_key: str) -> float:
    """Placeholder for a real live-price source. NOT implemented on purpose.

    Wire a real feed in here later. Keep the signature (metal_key -> float)
    so nothing else in the pipeline has to change.
    """
    raise NotImplementedError(
        "Live price fetching is not implemented in this prototype. "
        "Pass --price explicitly or set a value in config/prices.json."
    )


def load_price_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_price(
    metal_key: str,
    cli_price: Optional[float],
    config_path: str,
    use_live_source: bool,
) -> float:
    """Decide what price to write to Synthèse!U3, in priority order:

    1. --price on the CLI (explicit human input, always wins)
    2. --price-source lme (stub -- will raise until a real feed is wired in)
    3. config/prices.json fallback
    4. the metal's hardcoded default (from config.py)
    """
    if cli_price is not None:
        return cli_price

    if use_live_source:
        return fetch_price_from_lme(metal_key)

    prices = load_price_config(config_path)
    if metal_key in prices and "price" in prices[metal_key]:
        return float(prices[metal_key]["price"])

    from .config import get_config
    return get_config(metal_key).default_price
