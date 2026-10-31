# Sincronia on Instagram

Daily carousels for @sincronia.live, in English. Everyday life, motivation and
mindset; the brand appears only on the follow slide.

    python3 carousel.py --slot 1                 # render today's first carousel
    python3 run_daily.py --slot 1                # render it and publish it
    python3 run_daily.py --catch-up              # everything today that is not out yet
    python3 ig_publish.py --recent 60 --ig-id X  # the titles already posted

`STYLE.md` is the brief each run writes from. `carousels.py` holds the written
bank used when a run writes nothing of its own, so a post always goes out.
`brand.py` carries the site's own palette and mark.

The account id is not discoverable from the token (its scopes are
`instagram_basic` and `instagram_content_publish` only), so publishing takes it
from `--ig-id`, `SINCRONIA_IG_ID` or `ig_id.txt`, and caches whatever works.
Without it a run still renders and exits 2, leaving the slides for a later run.
