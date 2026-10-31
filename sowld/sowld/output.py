"""Output step: print a clean table and save the results to CSV."""

from __future__ import annotations

import csv

from .valuation import ValuedListing


def print_table(deals: list[ValuedListing]) -> None:
    if not deals:
        print("No underpriced deals found.")
        return

    headers = ["Score", "Title", "Price", "Fair value", "Brand", "Model", "Cond", "URL"]
    rows = [
        [
            f"{d.deal_score:.0%}",
            d.parsed.listing.title[:40],
            f"{d.parsed.listing.price:.0f}",
            f"{d.fair_value:.0f}",
            d.parsed.brand or "",
            d.parsed.model or "",
            d.parsed.condition_score if d.parsed.condition_score is not None else "",
            d.parsed.listing.url,
        ]
        for d in deals
    ]

    widths = [
        max(len(str(row[i])) for row in ([headers] + rows)) for i in range(len(headers))
    ]

    def fmt_row(row: list) -> str:
        return "  ".join(str(cell).ljust(width) for cell, width in zip(row, widths))

    print(fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt_row(row))


def save_csv(deals: list[ValuedListing], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "deal_score",
                "title",
                "price",
                "fair_value",
                "brand",
                "model",
                "variant",
                "year",
                "size",
                "condition_score",
                "location",
                "url",
            ]
        )
        for d in deals:
            listing = d.parsed.listing
            parsed = d.parsed
            writer.writerow(
                [
                    f"{d.deal_score:.3f}",
                    listing.title,
                    listing.price,
                    f"{d.fair_value:.2f}",
                    parsed.brand,
                    parsed.model,
                    parsed.variant,
                    parsed.year,
                    parsed.size,
                    parsed.condition_score,
                    listing.location,
                    listing.url,
                ]
            )
