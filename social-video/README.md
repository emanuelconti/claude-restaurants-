# The daily SocialPerks video

Every morning a new short video for SocialPerks' own social profile (Instagram Reels, TikTok, Shorts). Each day is different: a different kind of place, a different format, a different opening line and colours. The lines provoke and sound like a person. The photos are what customers really post from each kind of place, the same as on socialperkses.com.

Every video also explains the whole idea in about 15 seconds, so someone who has never heard of SocialPerks gets it: the hour that does not fill, the small gift put on it (1), the customer who shares a Story or sends a message (2), the friend who comes in and shows a code at the counter (3), and why a Story and a message are different with the same link.

```bash
python3 social-video/daily.py                    # today (Madrid time), Spanish and English
python3 social-video/daily.py --date 2026-10-20  # any day; the same day always gives the same video
python3 social-video/daily.py --lang es          # one language
```

Under `social-video/out/<date>/` it writes:

- `socialperks-<date>-es.mp4` and `-en.mp4`: 1080x1920, 30 fps, H.264 + AAC, 14 to 17 seconds, cut fast: every scene at about twice its written speed, cuts on a 120 BPM grid alternating a whip pan and a punch-in, a slow push on every frame. No music in the file, only a whoosh into each cut: the trending sound goes on top from the app's own library (the page says how). `--music` puts the original reggaeton or Latin trap beat back in.
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

## Requirements

You need Python 3 with Pillow and numpy, ffmpeg with libx264, and internet access to `images.unsplash.com` for the photos. If a photo cannot be fetched, the video uses the day's colours instead, so a video always comes out. Downloaded photos are cached in `social-video/.cache`.

The fonts in `fonts/` are Inter and Inter Tight (SIL Open Font License), converted to TTF from the site's own files. `assets/mark.png` is the SocialPerks mark.

## Every morning, automatically

A scheduled task starts a fresh session at 07:51 Madrid time. The session renders the day's video and updates the owner's page, **SocialPerks video del giorno** (https://claude.ai/artifact/YNUEr5KqP3zZYDwBmXD6sM, private to the owner).

The page is the delivery because a session in the cloud cannot hand the owner a file. Its steps:

1. Read the page as it is published.
2. Upload the two MP4s and the Spanish cover to the page's asset store.
3. Run `page.py` with the new asset ids. It rebuilds the page from `page.html`, with today on top, the English version under it and the last seven days.
4. Publish the page to the same address.
5. Delete the assets of days that fell off the week.

A push notification says the run finished. On the phone, "Condividi su Instagram o TikTok" copies the caption and opens the share sheet with the video, where Instagram and TikTok are; "Copia testo" copies the caption on its own.

The session does not commit or post anything. Posting on the profile stays a tap, because Instagram and TikTok only publish through their apps or a business API connected to the account.
