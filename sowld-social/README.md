# Sowld's Instagram carousels

Five carousels a day on [@sowld.ai](https://instagram.com/sowld.ai), written fresh each time and published automatically. Nobody has to open anything.

Same build as SocialPerks' (`social-video/` on `claude/socialperks-continuous-build-lgdgd6`), with Sowld's own colours, mark, audience and topics, and its own `STYLE.md`.

## What a post looks like

A cover photo with a big white title on a dark fade, then one numbered point per slide: heading, one or two lines, and a closing line in Sowld's pink. The mark sits on every slide. 7 to 8 slides, 1080x1350 (the 4:5 feed size), no faces in any photo. The last slide is Sowld, and only when the topic earns it: about one in four.

English: @sowld.ai posts in English, unlike SocialPerks which is Spanish.

## What it says

`STYLE.md` is the brief each run follows. The short version: everyday life people recognise themselves in, about the stuff we own, buy, keep and finally let go of, **and it has to lift**. Recognition alone gets a smile and a scroll; someone follows because of how a post makes them feel about themselves. So every carousel names the stuck thing honestly, turns around point 4 or 5, and ends on something small and doable.

Never a seller's post. No invented figures, no promised earnings, no empty motivational voice.

`carousels.py` holds the bank of 21 written topics. That bank is only the safety net: each run writes a new one and falls back to it only if writing fails, so a slot always goes out.

## Running it by hand

```bash
python3 carousel.py                                # today in Rome, slot 1
python3 carousel.py --date 2026-10-30 --slot 3     # any day and slot, always the same result
python3 carousel.py --slot 2 --topic topic.json    # a topic written for this run
```

Writes `out/<date>/carousel-<slot>/slide-01.jpg` and on, plus `carousel.json` with the title, the slides and the caption.

## Publishing

```bash
python3 ig_publish.py --token-env INSTAGRAM_TOKEN_SOWLD --check-token          # which account the token reaches
python3 ig_publish.py --token-env INSTAGRAM_TOKEN_SOWLD --recent 60            # titles already posted
python3 ig_publish.py --token-env INSTAGRAM_TOKEN_SOWLD --date <date> --slot <n> --upload
```

Instagram only takes images from a public URL, so `--upload` puts the slides on a temporary host (litterbox, then uguu if the first is down) and posts them as one carousel. It checks the last posts first and stops if today's caption is already up, so running it twice never posts twice.

`INSTAGRAM_TOKEN_SOWLD` lives in the cloud environment's settings, never in the repository. An Instagram Login token (starts with `IG`) names its own account and needs nothing else; a Facebook Login token (starts with `EAA`) also needs `--ig-id`, because it could reach several accounts and there would be no telling which.

## The schedule

Five scheduled runs a day, Rome time, each starting a fresh session: **08:40, 12:20, 15:50, 19:10, 21:30**. Every run writes a new topic following `STYLE.md`, checks `--recent 60` so it never repeats a title, renders it, publishes it, and stops.

At **23:10** a last run counts the day's posts on the account and publishes whatever is missing, so a day never ends with fewer than three.

Nothing here commits to the repository, and nothing waits for a human.

## Requirements

Python 3 with Pillow and numpy, and reachable `images.unsplash.com`. A photo that cannot be fetched falls back to a gradient in Sowld's colours, so a slide always renders. Photos are cached in `.cache`.

The fonts are Inter and Inter Tight (SIL Open Font License). `assets/mark.png` is Sowld's mark, the same shape as the site's favicon.
