#!/usr/bin/env python3
"""The owner's daily page: today's video and carousel, their captions, the last week.

The scheduled run renders the day's video (daily.py) and carousel
(carousel.py), uploads the MP4s, the cover and the slides to the page's
asset store, then runs this to rebuild the page with the new day on top and
publishes it to the same address. A run in the cloud cannot hand the owner a
file, so the page is the delivery: the owner opens it on the phone and taps
"Condividi", which copies the caption and opens the phone's share sheet with
the video, or with all the slides at once.

    python3 social-video/page.py --date 2026-10-17 \\
        --ids '{"es": "<asset id>", "en": "<asset id>", "cover": "<asset id>"}' \\
        --carousel-ids '["<slide 1 id>", "<slide 2 id>", ...]' \\
        --previous <the published page, as Artifact read saved it>

It writes out/<date>/page.html and prints {"page": ..., "prune": [...]}: the
asset ids no day on the page uses any more (older than a week, or replaced by
a re-run), for the run to delete.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import episodes as E  # noqa: E402

KEEP_DAYS = 7

PLACE_IT = {
    "barber": "Barbiere", "salon": "Parrucchiere", "nails": "Unghie", "gym": "Palestra",
    "tattoo_studio": "Tatuaggi", "wellness": "Benessere", "physio": "Fisioterapia", "hotel": "Hotel",
    "restaurant": "Ristorante", "bar": "Bar", "cocktail_bar": "Cocktail bar", "pizzeria": "Pizzeria",
    "cafe": "Caffè", "brunch": "Brunch", "ice_cream": "Gelateria",
}
FORMAT_IT = {"story": "La Story di un cliente", "chat": "Chat tra amici", "numbers": "I numeri", "myth": "Falso mito", "pov": "POV"}

DAYS_TAG = re.compile(r'<script type="application/json" id="sp-days">(.*?)</script>', re.S)


def captions(folder: str) -> dict:
    text = open(os.path.join(folder, "caption.txt"), encoding="utf-8").read().strip()
    out = {}
    for part, lang in zip(text.split("\n\n-----\n\n"), ("es", "en")):
        # The first line names the language (ESPAÑOL, ENGLISH); the page says it already.
        out[lang] = part.split("\n\n", 1)[1].strip() if "\n\n" in part else part.strip()
    return out


def previous_days(path: str | None) -> list:
    if not path or not os.path.exists(path):
        return []
    found = DAYS_TAG.search(open(path, encoding="utf-8").read())
    if not found:
        return []
    try:
        return json.loads(found.group(1).replace("<\\/", "</"))
    except json.JSONDecodeError:
        return []


def ids_of(day: dict) -> set:
    ids = {day.get(key) for key in ("es", "en", "cover") if day.get(key)}
    return ids | set((day.get("carousel") or {}).get("slides") or [])


def carousel_of(folder: str, slide_ids: list) -> dict:
    """The day's carousel as the page shows it: the slides' asset ids, in order, its title and caption."""
    meta = json.load(open(os.path.join(folder, "carousel", "carousel.json"), encoding="utf-8"))
    if len(slide_ids) != len(meta["slides"]):
        sys.exit(f"--carousel-ids has {len(slide_ids)} ids for {len(meta['slides'])} slides")
    return {"title": meta["title"], "caption": meta["caption"], "slides": slide_ids}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date", required=True)
    ap.add_argument("--ids", default=None, help='{"es": id, "en": id, "cover": id}; leave out to keep the day\'s video already on the page')
    ap.add_argument("--carousel-ids", default=None, help="the slides' asset ids, in slide order (JSON list)")
    ap.add_argument("--carousel-link", default=None, help="the Instagram post, when ig_publish.py already published it")
    ap.add_argument("--previous", default=None)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    args = ap.parse_args()

    date = dt.date.fromisoformat(args.date)
    ep = E.episode(date)
    folder = os.path.join(args.out, ep["date"])
    before = previous_days(args.previous)
    # A re-run for the same day updates what it was given and keeps the rest.
    today = next((dict(d) for d in before if d.get("date") == ep["date"]), {"date": ep["date"]})
    today.update(place=PLACE_IT.get(ep["category"], ep["category"]), format=FORMAT_IT.get(ep["format"], ep["format"]))
    if args.ids:
        ids = json.loads(args.ids)
        today.update(es=ids["es"], en=ids["en"], cover=ids.get("cover"), caption=captions(folder))
    elif not today.get("es"):
        sys.exit("--ids is needed: the page has no video for this day yet")
    if args.carousel_ids:
        today["carousel"] = carousel_of(folder, json.loads(args.carousel_ids))
    if args.carousel_link and today.get("carousel"):
        today["carousel"]["permalink"] = args.carousel_link
    days = [today] + [d for d in before if d.get("date") != today["date"]]
    days.sort(key=lambda d: d["date"], reverse=True)
    kept = days[:KEEP_DAYS]
    used = set().union(*(ids_of(d) for d in kept))
    prune = sorted(set().union(*(ids_of(d) for d in before)) - used) if before else []

    template = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
    data = json.dumps(kept, ensure_ascii=False).replace("</", "<\\/")
    page = os.path.join(folder, "page.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(template.replace("__DAYS__", data))
    print(json.dumps({"page": page, "prune": prune}))


if __name__ == "__main__":
    main()
