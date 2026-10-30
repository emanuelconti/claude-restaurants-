# The daily SocialPerks video and carousel

Every morning a new short video for SocialPerks' own social profile (Instagram Reels, TikTok, Shorts). Each day is different: a different kind of place, a different format, a different opening line and colours. The lines provoke and sound like a person. The photos are what customers really post from each kind of place, the same as on socialperkses.com.

Every video also explains the whole idea in under 30 seconds, so someone who has never heard of SocialPerks gets it: the hour that does not fill, the small gift put on it (1), the customer who shares a Story or sends a message (2), the friend who comes in and shows a code at the counter (3), and why a Story and a message are different with the same link.

```bash
python3 social-video/daily.py                    # today (Madrid time), Spanish and English
python3 social-video/daily.py --date 2026-10-20  # any day; the same day always gives the same video
python3 social-video/daily.py --lang es          # one language
```

Under `social-video/out/<date>/` it writes:

- `socialperks-<date>-es.mp4` and `-en.mp4`: 1080x1920, 30 fps, H.264 + AAC, 25 to 29 seconds, cut fast: words and cards land half again as fast as written and each scene holds long enough to read, cuts on a 120 BPM grid alternating a whip pan and a punch-in, a slow push on every frame. No music in the file, only a whoosh into each cut: the trending sound goes on top from the app's own library (the page says how). `--music` puts the original reggaeton or Latin trap beat back in.
- a cover JPEG per language;
- `caption.txt`: the text to paste under the post, in both languages, with hashtags.

**Post the Spanish one.** The venues we sell to are in Barcelona. The English one is there for a second account or for ads.

## What it says

`episodes.py` holds everything the video says:

- **Formats.** There are five, and the date picks one. The format decides how the video opens; the middle is always the same three numbered steps, then "Story or message: the same link".
  - *story*: a customer's Story with the link, then the friend who came in;
  - *chat*: a friend asks "where?", the customer sends the link;
  - *numbers*: 1 Story, 3 new friends, €0 in ads;
  - *myth*: what they sell you, struck out, then what works;
  - *POV*: you run a salon at 11:00, and the phone starts buzzing.
- **Kinds of place.** There are fifteen, appointments first. Each has the customer and venue from the product's examples, the gift, the quiet hour and the hashtags.
- **Lines.** There are 24 opening lines and 5 closing lines. A line comes back only after all the others, and always with a different place and format.

To add a line, append it to `HOOKS` in Spanish and English, with `*...*` around the words to highlight. To add a format, add a scene in `daily.py` and its name to `FORMATS`.

## The carousel

Next to the video, a second post every day: a swipeable carousel for the feed, in the style the owner pointed at on 30 October. The cover is a photo with a big white title on a dark fade; then one numbered point per slide, the text on white at the top and a photo fading in under it, the mark on every slide, no faces; the last slide is SocialPerks. The topics are what owners of small local businesses already worry about (quiet hours, platforms, discounts, why nobody recommends them), so they read it, save it and send it to someone who also runs a business.

```bash
python3 social-video/carousel.py                    # today (Madrid time)
python3 social-video/carousel.py --date 2026-10-31  # any day; the same day always gives the same carousel
```

Under `social-video/out/<date>/carousel/` it writes `slide-01.jpg` and on (1080x1350, the 4:5 feed size, 7 to 10 slides) and `carousel.json` with the title, the slides and the caption. Spanish only, like the post.

`carousels.py` holds what it says: 14 business topics and 7 about life (routine, motivation, what it feels like to run a place, the rent, AI), taking turns, a business one on even days from 30 October and a life one on odd days; each list starts again, with other photos, when it runs out. To add one, append it to `BUSINESS` or `LIFE`: a title for the cover, a line for the caption, and points (a heading, the lines under it, the closing line in bold). Business topics use the video's photos (without the one that shows a face); life topics name a set in `PHOTO_SETS` (sunrise, notebooks, coffee, Barcelona, receipts), each photo fetched and checked to have no face.

### Straight to Instagram

From the Claude app a page can hand the phone only one file at a time, so the page sends the slides as one ZIP there (Files opens it into a folder; select all, share, «Salva immagini»); in Safari they go to the share sheet together. To skip all that, `ig_publish.py` posts the carousel itself, as one post with every slide in order, through the Instagram API:

```bash
INSTAGRAM_ACCESS_TOKEN=... python3 social-video/ig_publish.py --date 2026-10-31 \
    --base-url https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/daily-posts/2026-10-31/
```

Instagram fetches each image from a public URL, so the daily run first force-pushes the day's slides to the `daily-posts` branch (one commit, only that day, so the branch never grows). The token comes from the Meta app's dashboard (Instagram API with Instagram Login, permissions `instagram_business_basic` and `instagram_business_content_publish`), lasts 60 days, and lives in the cloud environment's settings as `INSTAGRAM_ACCESS_TOKEN`, never in the repository. Without it the run skips this step and the page works as before. It never posts the same caption twice, and the page shows the link to the post once it is up.

### Three a day, written fresh

Since 30 October the profile posts carousels only, three a day, about everyday life that anybody likes (the owner: never a seller's scene; SocialPerks only on a last slide, and only when the topic is about friends and favourite places). The scheduled runs publish them themselves at 08:47, 13:13 and 20:41, Madrid time. Each run writes a new topic following `STYLE.md`, checks the last posts so it never repeats one (`ig_publish.py --recent 60`), renders it with `carousel.py --slot <n> --topic <file>`, puts the slides on a temporary public host for an hour so Instagram can fetch them (`ig_publish.py --upload`), publishes it and adds it to the day on the page with the link to the post. If writing fails, the slot falls back to the `EVERYDAY` bank in `carousels.py`. The daily video is paused until the owner asks for it back.

## Requirements

You need Python 3 with Pillow and numpy, ffmpeg with libx264, and internet access to `images.unsplash.com` for the photos. If a photo cannot be fetched, the video uses the day's colours instead, so a video always comes out. Downloaded photos are cached in `social-video/.cache`.

The fonts in `fonts/` are Inter and Inter Tight (SIL Open Font License), converted to TTF from the site's own files. `assets/mark.png` is the SocialPerks mark.

## Every morning, automatically

A scheduled task starts a fresh session at 07:51 Madrid time. The session renders the day's video and carousel and updates the owner's page, **SocialPerks post del giorno** (https://claude.ai/artifact/YNUEr5KqP3zZYDwBmXD6sM, private to the owner).

The page is the delivery because a session in the cloud cannot hand the owner a file. Its steps:

1. Read the page as it is published.
2. Upload the two MP4s, the Spanish cover and the carousel's slides to the page's asset store.
3. Run `page.py` with the new asset ids (`--ids` for the video, `--carousel-ids` for the slides in order). It rebuilds the page from `page.html`, with today's video and carousel on top, the English video under it and the last seven days.
4. Publish the page to the same address.
5. Delete the assets of days that fell off the week.

A push notification says the run finished. On the phone, "Condividi su Instagram o TikTok" copies the caption and opens the share sheet with the video, where Instagram and TikTok are; "Copia testo" copies the caption on its own. For the carousel, "Salva o condividi le immagini" copies its caption and hands all the slides to the share sheet at once, in order: "Salva immagini" puts them in Photos, or Instagram opens with them.

The session does not commit or post anything. Posting on the profile stays a tap, because Instagram and TikTok only publish through their apps or a business API connected to the account.
