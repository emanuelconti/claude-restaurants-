# Good Message Studio: channels, what is ready and what each one still needs

Last checked on 1 November 2026 (Europe/Madrid), in the Default cloud environment and on every branch of this repository.

## Status

| Channel | Script | Automatic today? | What is still missing |
|---|---|---|---|
| Instagram @goodmessage_studio | `ig_publish.py`, `reel_publish.py` | **Yes**, verified: posts and a reel published on 1 November | nothing |
| Facebook Page "Good Message Studio" | `fb_publish.py` | **Yes for the token** (Page token derived from the user token; first post verified on 1 November). The swipeable link-carousel format is new and **not yet verified on the live Page** | first live run of the carousel format |
| Threads | `threads_publish.py` | **No.** Ready, dry run added, OFF | `THREADS_TOKEN_GMS`, then `GMS_THREADS_ENABLED=1` |
| Pinterest | `pinterest_publish.py` | **No.** Ready, dry run tested offline, OFF | Pinterest Standard access for app 1632981 (now "Trial access pending"), then `PINTEREST_TOKEN_GMS`, `PINTEREST_BOARD_GMS`, `GMS_PINTEREST_ENABLED=1` |
| YouTube Shorts | `youtube_publish.py` | **No.** Ready, dry run tested offline, OFF | Google Cloud project + OAuth consent, then `YOUTUBE_CLIENT_ID_GMS`, `YOUTUBE_CLIENT_SECRET_GMS`, `YOUTUBE_REFRESH_TOKEN_GMS`, `GMS_YOUTUBE_ENABLED=1`; public uploads only after Google's API audit (`GMS_YOUTUBE_PRIVACY=public`) |
| TikTok | `tiktok_publish.py` | **No.** Ready, dry run tested offline, OFF | TikTok developer app with Content Posting API, then `TIKTOK_CLIENT_KEY_GMS`, `TIKTOK_CLIENT_SECRET_GMS`, `TIKTOK_REFRESH_TOKEN_GMS`, `GMS_TIKTOK_ENABLED=1`; public posts only after TikTok's app audit (`GMS_TIKTOK_PRIVACY=PUBLIC_TO_EVERYONE`) |
| Carousell | none | No | the owner decides on 16 November; the account is probably not registered yet |

No channel is called automatic here until a real post has gone out on it.

## The rules every script keeps (channel_guard.py)

- One item per run; the scheduled routine decides which run publishes what.
- At most 6 posts a day per channel, at least 60 minutes since that channel's last post.
- At least 20 minutes since the last Good Message Studio post on Instagram or Facebook (read-only check).
- Any answer with blocked, limit, spam, restricted, temporarily or "too soon" stops the run; nothing is retried.
- **OFF by default:** without `--publish` every script is a dry run, and `--publish` still does nothing unless `GMS_<CHANNEL>_ENABLED=1`.
- Tokens are read from the environment only, sent in headers, never printed or written to files.
- TikTok refuses to post when it cannot read the account's recent videos (`video.list`), because the limits could not be checked.

## What the owner has to do, channel by channel

Only the owner can create accounts, give OAuth consent, accept platform terms or install apps. Claude prepares the code and checks the result.

**Threads**
1. Make sure @goodmessage_studio has a Threads profile (Threads app, same Instagram login).
2. In the Meta app dashboard add the use case "Access the Threads API", with permissions `threads_basic` and `threads_content_publish`, and add the Threads profile as a tester while the app is in development.
3. Generate a long-lived Threads token (60 days, refreshable) and save it in the Default environment as `THREADS_TOKEN_GMS`.
4. Ask Claude to run `python3 threads_publish.py --check-token`; once it answers "token ok", set `GMS_THREADS_ENABLED=1`.

**Pinterest**
1. Wait for the approval email for app "Good Message Studio Publisher" (ID 1632981) at the account's address; then request **Standard access** (Trial access cannot make public Pins).
2. Generate a token with `boards:read`, `pins:read`, `pins:write` and save it as `PINTEREST_TOKEN_GMS`; save the board name ("Good Message Studio") or id as `PINTEREST_BOARD_GMS`.
3. After a dry run that reads the account and the board, set `GMS_PINTEREST_ENABLED=1`.

**YouTube Shorts**
1. Create (or pick) the Good Message Studio YouTube channel.
2. In Google Cloud: a project, enable "YouTube Data API v3", an OAuth consent screen, and an OAuth client.
3. One consent with the channel's Google account for `youtube.upload` and `youtube.readonly`, to get a refresh token.
4. Save `YOUTUBE_CLIENT_ID_GMS`, `YOUTUBE_CLIENT_SECRET_GMS`, `YOUTUBE_REFRESH_TOKEN_GMS`; after a dry run that reads the channel, set `GMS_YOUTUBE_ENABLED=1`. Uploads stay private until the project passes Google's audit; then `GMS_YOUTUBE_PRIVACY=public`.

**TikTok**
1. Create the Good Message Studio TikTok account (decision due 16 November).
2. On developers.tiktok.com: an app with Login Kit and the Content Posting API (Direct Post), scopes `user.info.basic`, `video.list`, `video.publish`.
3. One consent with the TikTok account to get a refresh token; save `TIKTOK_CLIENT_KEY_GMS`, `TIKTOK_CLIENT_SECRET_GMS`, `TIKTOK_REFRESH_TOKEN_GMS`.
4. After a dry run, `GMS_TIKTOK_ENABLED=1`. Posts stay private (SELF_ONLY) until TikTok audits the app; then `GMS_TIKTOK_PRIVACY=PUBLIC_TO_EVERYONE`.

## Tests

`python3 tests/test_channels.py`: offline (no network, no tokens). It proves that missing variables touch nothing, a dry run only reads, `--publish` does nothing without the enable flag, "too soon" and the daily cap stop before any write, every pushback word stops without retry, and an enabled run makes exactly one post.

## Not wired into the routines yet

The scheduled routine for Good Message Studio still publishes Instagram, the reel and Facebook only (Threads is in it but stays OFF without its flag). Pinterest, YouTube and TikTok are added to the routine only after their first verified dry run with real credentials, each 20 minutes after the previous channel.
