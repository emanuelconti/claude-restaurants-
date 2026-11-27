# videokit3d: 3D story videos in code, free, nothing to install by hand

Owner, 26 November 2026: the Reels and videos of SocialPerks, Good Message Studio and Sincronia must be exceptional, better than YC launch videos: a hook in the first second, a real story told in 3D, almost no text on screen, music that sounds like music. Use this kit for every Reel and every video from now on, and make each one better than the last.

## Setup (once per session, automatic)
    bash social-cloud-backup/videokit3d/setup.sh /tmp/vk3
It installs three.js into the cache, links or installs Playwright, checks ffmpeg and numpy. Nothing else is needed.

## Make a video
1. Copy an example scene into /tmp/vk3 and change it: `city-story-16x9.html` (a 3D night city: empty places, a customer sends a link as a beam of light, new customers walk in, every venue lights up, the city's lights become the logo), `product-tour-16x9.html` (real product screens on 3D phones, camera moves, words in sequence).
2. Put photos, logos and real screenshots in /tmp/vk3/assets (Playwright can capture the real site or app).
3. Write the music: copy `music-48s.py`, set the length and the moments (bells on events, a chord on the logo). Only tones, never noise or third-party music.
4. `bash make.sh my-scene.html 30 music.wav out.mp4 1080 1920` (vertical for Reels; 1920 1080 for LinkedIn and YouTube).
5. Look at frames before publishing: extract 8-12 stills with ffmpeg and check them one by one.

## How a scene works
The page defines `window.render(t)` that draws the instant t (seconds) and sets `window.ready = true`. Everything is a function of t, so any frame can be rendered by any process. Three.js for 3D (with UnrealBloomPass for glow), HTML on top for words and real screenshots, a seeded random so every process builds the same world.

## Daily Reels in one command (27 November 2026)
`reel3d.py` turns any reviewed queue item into a 3D Reel: the topic's own reviewed photos float as framed panels over a golden, moonlit or pastel sea, the camera flies from one to the next on the beat, one short line at a time (the title as the hook from frame one, then the five points), bloom, and a brand end card (SocialPerks, Sincronia, Good Message Studio). Palette, panel layout, camera orbit and music (`music3d.py`, tones only) change with every item, so no two Reels look the same.

    bash social-cloud-backup/videokit3d/setup.sh /tmp/vk3
    python social-cloud-backup/videokit3d/reel3d.py sp-2026-11-28-1 sin-2026-11-28-3 gms-2026-11-28-5

Then inspect each contact sheet in /tmp/vk3/sheets and run reelkit/approve.py as before. About 3 minutes per Reel on 4 cores. Never change the photos away from the reviewed slides; GMS uses only real message-hoodie photos.
