"""Telegram delivery: send the top deals as a chat message via a bot."""

from __future__ import annotations

import os

import requests

from .valuation import ValuedListing

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
REQUEST_TIMEOUT = 10
MAX_DEALS_IN_MESSAGE = 10


def send_deals(
    deals: list[ValuedListing],
    bot_token: str | None = None,
    chat_id: str | None = None,
) -> None:
    bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (in .env or passed in)"
        )

    if not deals:
        _send(bot_token, chat_id, "Sowld: no underpriced deals found today.")
        return

    lines = ["*Sowld — today's deals*"]
    for d in deals[:MAX_DEALS_IN_MESSAGE]:
        listing = d.parsed.listing
        lines.append(
            f"• [{listing.title}]({listing.url}) — {listing.price:.0f}€ "
            f"(fair ~{d.fair_value:.0f}€, {d.deal_score:.0%} under)"
        )
    _send(bot_token, chat_id, "\n".join(lines))


def _send(bot_token: str, chat_id: str, text: str) -> None:
    url = TELEGRAM_API.format(token=bot_token)
    resp = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
