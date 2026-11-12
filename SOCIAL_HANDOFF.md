> Current owner instruction, 3 November 2026: read SOCIAL_MARKET_RULES.md and SOCIAL_CLOUD_RUNBOOK.md FIRST. The cloud is the sole standing publisher, also after Thursday. Chrome Claude is primary editor; Safari Claude is backup editor only. Each brand has its own audience and market calendar; GMS is English/SGD/women in Singapore/Asia-Singapore. Older schedules and channel lists below are historical.

# Social accounts: shared handoff (read this before touching any of them)

For every Claude, Codex or person who works on @socialperks.es, Good Message Studio (@goodmessage_studio, formerly @sowld.ai, and its Facebook Page) or @sincronia.live. Last updated 2 November 2026 (10 a day). The owner is Emanuel; everything below is his decision unless marked otherwise. Keep this file current when something changes.

## Where things live

| Account | Branch | Folder | Token variable (Default environment) |
|---|---|---|---|
| @socialperks.es (Spanish, B2B: owners of cafés, restaurants, bars, gyms, salons, spas, hotels, shops) | `claude/socialperks-continuous-build-lgdgd6` | `social-video/` | `INSTAGRAM_ACCESS_TOKEN` |
| Good Message Studio, Instagram + Facebook Page (English, women 18 to 38 in Singapore, shop goodmessagestudio.com) | `claude/ricerche-automatiche-performance-x5pstt` | `sowld-social/` | `INSTAGRAM_TOKEN_SOWLD`; Facebook `FB_PAGE_TOKEN_GMS` (may be the owner's user token: `fb_publish.py` derives the Page token itself) and `FB_PAGE_ID_GMS` |
| @sincronia.live (English, founders and startups looking for funding) | `claude/graduate-deadlines-consulting-k8obxv` | `sincronia/social/` | `INSTAGRAM_TOKEN_SINCRONIA` (`SINCRONIA_IG_ID` holds a wrong value; the script falls back to the right id 17841404632479565 by itself) |

Each folder's `STYLE.md` is the brief (strategy, "Professional and unattackable" checklist, photos, layouts) and its `README.md` the commands. Good Message Studio also has `CHANNELS.md` (status of Threads, Pinterest, YouTube, TikTok).

## Rules that never change

- Never remove, lower or get around the limits in the scripts: **10 posts a day per account and per channel** (the owner, 2 November: we start from zero followers and must grow); **at least 60 minutes between two posts of the same account**, so never in a burst; at least 20 minutes between publishes on different accounts or channels. A routine run may publish up to 3 posts per account (2 for Good Message Studio), waiting 60 minutes between them. (31 October: a burst of posts got the Meta app blocked.)
- Any answer with blocked, limit, spam, restricted, temporarily or "too soon": stop, do not retry, report.
- Never print, log or commit a token or any part of one.
- Never publish a carousel in plain colours: the renderers stop when a photo is missing.
- Never post the same caption twice; scripts check the account first.
- Before a manual post, count the account's posts today on Instagram (`ig_publish.py --recent 60`).

## Look and content decisions (owner, 31 October to 2 November)

- **Covers:** no photo may open two of any 12 posts in a row (the profile grid shows 12). The renderer picks the cover from one fixed sequence per account; do not choose covers by hand.
- **Good Message Studio is premium:** openers are hero shots (the back with the printed message, real lifestyle) or typographic covers in DM Serif Display on a soft colour; never the plain front of a blank hoodie, never supplier images, never `gm-city.jpg` / `gm-studio.jpg` (the model looks AI-generated), never the balaclava photo or the "19" print. Serif headings in sentence case, no text boxes on photos, text never over the printed message. Slides alternate product card / words only / photo with text.
- **Reels (Good Message Studio, one a day at 12:17 Singapore):** always open on the typographic hook; real product photos only; original beat; `reel.py` + `reel_publish.py`.
- **Every Good Message Studio post leads to the shop:** Instagram captions say "link in bio" (bio link = goodmessagestudio.com); Facebook and Threads get "Shop now: https://goodmessagestudio.com" as a real link.
- **Facebook:** one swipeable link carousel (cards that open the shop), never a grid of small photos. Card images must be uploaded to the Page first (`fb_publish.py` does it): images left on the temporary hosts expire and the cards turn white (seen on 2 November).
- **SocialPerks:** B2B. One of the day's three is about running a place and ends with `"cta": "business"`; the others stay likeable everyday or owner-life topics.
- **Sincronia:** up to 10 posts a day, about funding readiness, grants vs equity, founder life. Never promise money or funding.
- Captions carry a searchable paragraph (`"caption"`) and 8 to 12 mixed hashtags, never the same block twice in a row; no engagement bait ("tag 3 friends").

## Scheduled routines (claude.ai/code/routines, Default environment)

| Routine | When | What |
|---|---|---|
| Good Message Studio | 08:17, 10:17, 12:17 (reel), 15:17, 18:17, 21:17 Singapore | up to 2 posts per run, 60 min apart, to reach 10 a day: Instagram, then Facebook 20 min later (Threads when enabled) |
| Caroselli (principale) | 08:47, 12:47, 16:47, 20:47 Madrid | up to 3 posts per account per run, SocialPerks and Sincronia alternating 20 min apart, each account 60 min apart, to reach 10 a day each |
| Good Message Studio – TikTok | 07:47, 14:47, 17:47, 20:47, 23:47 Singapore | 1 TikTok per run: the 14:47 run posts a reel, the others a new carousel turned into a slideshow (`tiktok_publish.py --carousel-slot`); the script refuses a repeated title, "too soon" or less than 20 min after Instagram/Facebook. Privacy `GMS_TIKTOK_PRIVACY` (SELF_ONLY until the owner sets PUBLIC_TO_EVERYONE) |
| Instagram backup | 23:41 Madrid | fills only what SocialPerks or Sincronia are missing |
| Recupero automatico ogni ora | hourly at :59 | **disabled** since 1 November 23:54 (not by the session that created it); ask the owner before turning it on |
| Controllo mattutino | 10:07 Madrid | token health for all accounts + authorization status of the other channels |
| Reminders | 16 November (15-day review, decide TikTok/Pinterest/Carousell); 15 January 2027 (renew the Facebook token before it loses data access on 30 January 2027) | |

## Other channels (Good Message Studio)

TikTok is connected since 2 November (see the routine above). Threads and Pinterest scripts exist and are **OFF**. YouTube Shorts: connected on 2 November (first Short uploaded private until Google's audit); every Short has `| goodmessagestudio.com` in the title and the shop link on the first description line (the owner: always point to the shop). The other channels: they need the owner's accounts, OAuth/audits and `GMS_<CHANNEL>_ENABLED=1`. Exact steps and variable names in `sowld-social/CHANNELS.md`. No channel counts as automatic until a real post went out on it. Carousell: decision on 16 November (account probably not registered).

## Known open points (2 November)

- Two Facebook posts of 1 November ("6 signs she is your soul sister", "5 gifts for the friend who always checks on you") show white cards; the owner deletes them by hand. Posts made before the fix of 2 November 09:15 may turn white too.
- Instagram API cannot delete posts; the owner deletes from the app.
- Sessions started by another session (not by the owner) may be stopped by the permission check and wait for the owner's "sì"; scheduled routines run on their own.


## 2 November 2026, afternoon: channels go out together (owner)

The owner removed the 20-minute gap between different channels of the same account: Instagram, Facebook, Threads, Pinterest and TikTok now go out one right after the other (CROSS_GAP = 0 in sowld-social/channel_guard.py). Still unchanged: 60 minutes between two posts on the same channel, 10 a day per channel, stop without retry on blocked/limit/spam/restricted/temporarily/too soon.

## Learning from results (owner, 2 November 2026)

Every account has a PERFORMANCE.md in its folder (sowld-social/, social-video/, sincronia/social/), written once a day by the routine "Ottimizzazione giornaliera". Every publishing routine reads it before choosing topics: more of what got likes, comments, saves and shares; less of the topics people ignored; competitor ideas adapted, never copied. Instagram, Facebook and Threads give these numbers through their APIs; Pinterest and TikTok only once their access is approved.

## Stories (owner, 2 November 2026)

Good Message Studio also posts Stories: after each carousel, `python3 story_publish.py --date <today Madrid> --slot <n> --publish` (sowld-social) posts the cover on a 9:16 canvas with "Shop now · link in bio" as an Instagram Story and a Facebook Page Story. Limits: 10 stories a day per channel, 60 minutes apart; stop without retry on blocked/limit/spam/restricted/temporarily/too soon.

Update, same day: Stories OFF (owner: organic Stories reach only followers, not worth it). story_publish.py stays in the folder, unused.


## 2 November 2026, evening: ONE routine, 3 runs a day (owner: usage limit almost gone)

Only the routine "SOCIAL UNICA" publishes now: 07:43, 13:43, 19:43 Madrid, all three accounts in the same run, about 5 posts a day per account (2 + 2 + 1), every channel of an account right after the other (Instagram, Facebook, Threads, Pinterest, TikTok). The 07:43 run also starts with the Good Message Studio reel and writes a short PERFORMANCE.md per account. All the other publishing, backup, optimisation and check routines are OFF. Any other Claude: do not create new routines or extra runs; keep work short and cheap; script limits stay (10/day, 60 min per channel).

Update (owner, 2 Nov evening): no 60-minute wait on Instagram, Threads (MIN_GAP = 0). Only Facebook keeps 60 minutes between Page posts. Daily caps unchanged.


## CONTEXT RULE FOR EVERY IMAGE (owner, 2 November 2026, very important; for every Claude and for Codex)

Every photo must show exactly what its slide talks about, for that account audience. A post about where to eat shows food, a table, a restaurant; never a bicycle, a random street, an object with no link to the text. SocialPerks: cafés, restaurants, bars, gyms, salons, spas, hotels, shops, owners at work. Sincronia: founders at work, desks, meetings, money/pitch scenes. Good Message Studio: only the message hoodies and real life scenes that match the line. Before publishing, look at EVERY slide image (not only the cover) and ask: does this photo obviously belong to this sentence? If not, change the photo or do not publish. A photo that does not fit is worse than no post.


## Lessons of 2 November 2026, evening (owner) — read before every run

- YouTube (Good Message Studio only): Shorts are ALWAYS public. Links in a Short description are not clickable: the description says "Shop now: goodmessagestudio.com (tap the link on our channel page)", the title ends with "| goodmessagestudio.com", and every reel/slideshow end card shows goodmessagestudio.com and "link in bio". Quality must be sharp: slideshows are encoded at 1080x1920, lanczos, crf 16 (YouTube shows low resolution for a few minutes while it processes HD; that is normal).
- Facebook link carousel is now right (verified): 5 cards, each a real message hoodie with photo, name and "Shop now at goodmessagestudio.com · price". Plain hoodies, caps, tees are never used.
- Always keep the target in mind (GMS: women in Singapore; SocialPerks: owners of venues in Spain; Sincronia: founders seeking funding) and optimise from PERFORMANCE.md (more of what gets likes/saves, less of what is ignored).
- Only one routine runs ("SOCIAL UNICA", 07:43/13:43/19:43 Madrid). Any Claude or Codex: you do not need to create routines; just read this file.


## TOP PRIORITY (owner, 2 November 2026): publishing must NEVER stop

If one channel fails, the others go on. Every morning (07:43 run) all tokens are checked; anything broken or expiring within 10 days goes in the FIRST line of the report (push notification) with the exact fix. Known expiries: Pinterest refresh token ~1 Jan 2027 (reminder 27 Dec); Threads token ~1 Jan 2027 (reminder 27 Dec); Facebook user token 30 Jan 2027 (reminder 15 Jan); Instagram long-lived tokens ~60 days; TikTok refresh 365 days; YouTube app in Production (refresh token does not expire unless revoked). New tokens can only be saved in the environment by the owner: any Claude or Codex prepares the exact link/steps immediately, never stops the other channels.

Token alarm: routine "ALLARME TOKEN social" (07:11 Madrid daily, push + EMAIL to the owner) runs sowld-social/token_keepalive.py and every --check-token. Instagram tokens are Facebook-login (EAA) tokens: they cannot be renewed in place. Threads gives a NEW value on refresh, so it must be saved by the owner. Any Claude/Codex that sees a broken token: tell the owner at once with the exact link/steps; never stop the other channels.


## 4 November 2026 (owner): MORE REELS + premium carousels, all three Instagram profiles

- REELS: 3-4 Reels a day on EVERY Instagram profile, besides the 8 carousels. Tool: carousel_reel.py in each account folder: render a carousel made FOR the Reel (new topic, own slot, strong hook on the first slide), then `python3 carousel_reel.py --date <today> --slot <n> --publish --token-env <account token>`. Vertical 1080x1920, slow zoom, cross-fades, original synthesized music (never copyrighted tracks). Max 4 Reels/day per account (script cap); Instagram daily cap is now 13 posts. Look at one frame per slide before publishing. Good Message Studio: its daily reel.py reel counts as one of the 4.
- CAROUSELS must look like the ones the owner liked at the start: a cover that is a full-bleed REAL photo matching the topic, with a short bold title on it; clean inner slides; every photo obviously about its line; no strange objects, no random stock, no ugly or busy graphics. If a slide looks cheap, re-render or do not publish. Targeted always: GMS = women in Singapore, only message hoodies; SocialPerks = venue owners in Spain; Sincronia = founders seeking funding. These posts are our advertising: they must look like great ads.


## CONTENT DIRECTION (owner, 6 November 2026) — overrides older topic lists

People do not care about narrow, niche tips (e.g. "5 details to enjoy the bar without thinking about the photo"). Write about LIFE: everyday moments, motivation, encouragement, small wins, friendship, courage to start, keep going, be kind to yourself, enjoy the people around you. Human, warm, short lines people want to save and send to a friend. Then connect it naturally to us: SocialPerks = share the places you love with your friends and get rewarded / owners: your regulars are your best advertising (invite to join, link in bio); Good Message Studio = wear the message that keeps you going (message hoodies, link in bio). At least 8 posts out of 10 must be life/motivation first, product second. Reels especially: one strong motivating hook in the first second.


## THREADS SPAM WARNING (6 November 2026)

Threads removed a Good Message Studio post for spam ("actions at high volume"). Now: at most 3 Threads posts a day, at least 3 hours apart, NO link in the post text (link only in the profile bio), and only the strongest, most human topics go to Threads. Every Claude and Codex: never raise these, never post the same text on Threads twice, and if Threads or any platform warns about spam, lower the volume on that channel at once and tell the owner.

## Organic growth playbook (owner, 9 November 2026: zero views, zero sales; find a way)

Posting alone does not grow a new account. What the routines must do every run (GMS first, same logic for SocialPerks and Sincronia):
- Reels are the reach engine: 4 a day, first second = a human, motivating hook in big type; 7-15 s; loopable; on-screen text that people want to send to a friend ("send this to her"). Carousels are for saves.
- Shareable life lines (motivation, friendship, small wins), product only as the natural answer; 1 post in 5 may sell.
- Captions end with one question that invites a comment, and a "send this to..." line. Local hashtags (Singapore for GMS, Spanish cities for SocialPerks), 5-8, mixed sizes.
- Read PERFORMANCE.md every run and copy the format of the best post of the week (hook, length, cover type).
Growth the owner must do by hand (platform rules forbid automating likes, follows, comments, DMs): 15 minutes a day replying to comments, commenting on 10 local accounts, and sending the best Reel to friends and groups; gifting 1 hoodie a week to a Singapore micro-creator (2k-20k followers) in exchange for an honest post.


## Comments (owner, 9 November 2026: he cannot do it by hand)

Every run: `python3 comments.py --token-env <account token> --list`, then answer each real comment with `--reply <id> "text"`: warm, human, short, in the comment language, often with a question back; max 20 per run. Ignore and never answer spam/scam comments (e.g. "can we repost it, send me DM", promo pages, crypto). Only our own posts: never like, follow, comment or DM other accounts (forbidden automation).

## Free growth levers for Good Message Studio (owner, 9 November 2026: no budget, no gifts, no time, no site changes)

- Ride what Singapore is talking about: each run, before writing, think of this week in Singapore (weather, MRT, office life, exams/PSLE results, Deepavali, 11.11 and 12.12 sales, Christmas at Orchard Road, year-end, CNY in February) and make at least 1 post in 3 about it, in a warm human way. Singapore English, local references (kopi, hawker, MRT, aircon), never stereotypes.
- Gifting moments sell hoodies: 11.11, 12.12, Christmas, birthdays, "for your best friend". Use them in Reels and carousels in the weeks before.
- Search brings buyers without followers: YouTube Shorts titles and Pinterest pins use what people search ("gift for her Singapore", "oversized hoodie Singapore", "positive quote hoodie").
- Test and copy: every day try one new Reel hook style; PERFORMANCE.md keeps the winner, and the next days use it more.

## THREADS: 9 posts removed as spam on 6-7 November 2026 — new rules (owner, 9 November)

Threads is PAUSED until 16 November 2026 (the script refuses to publish before then) so the young account can recover. From 16 November: at most ONE Threads post a day (20 hours apart), and it must read like a real person, not a template:
- no listicle titles ("5 ways to...", "5 messages for..."), no carousel of the same slides posted on Instagram, no shop link, no repeated closing line ("Save this, or send it to someone..." is banned);
- use `threads_publish.py --date <today> --slot <n> --text "..."` (text only): a short personal thought or a question in 1-3 sentences, different every day (e.g. "Who was the first person you texted this morning?"), sometimes with one real photo of a hoodie worn;
- reply to every comment on Threads like a person.
Any Claude or Codex: never raise these limits; if Threads removes another post, stop Threads again for 2 weeks and tell the owner.


Facebook (12 Nov 2026): the Be Kind Rainbow Hoodie card keeps coming out blank (Facebook fails to load that product page image, the file itself is fine). It is left out of the link-carousel cards until the owner verifies goodmessagestudio.com in Meta Business (then cards can carry our own pictures). Any publisher that builds Facebook cards (also social-cloud-backup on codex/social-cloud-backup) must skip it too.
