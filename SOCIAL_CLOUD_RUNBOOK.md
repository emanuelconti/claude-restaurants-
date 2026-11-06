# Social cloud operations: primary editor, backup editor, one publisher

Owner-authorized standing arrangement, 3 November 2026. Read SOCIAL_MARKET_RULES.md first. No paid calls, purchases or new social permissions. Enabled channels remain SP Instagram, Sincronia Instagram and GMS Instagram/Facebook/Threads/YouTube. Pinterest, TikTok and Stories are off.

## Sources and roles

Repository: emanuelconti/claude-restaurants-. Workflow `.github/workflows/social-cloud-backup.yml` lives on default `claude/coao-8jloui` and checks out `codex/social-cloud-backup`. All reviewed inventory and receipts live on that execution branch. Publishing is deterministic on GitHub-hosted runners, not on a Mac or a Claude conversation. The normal Chrome Claude account prepares/optimises content; Safari's Claude account is backup editor only. Routine quotas may stop editors; they do not stop a runner from consuming inventory already prepared.

GMS primary: trig_01JyRzzAfbsqvYfv1TBWZP6R, one daily 07:13 Asia/Singapore. European primary: trig_018CzvbW5QE7qNpfvmjE7WMs, one daily 07:13 Europe/Madrid, with separate SP/Sin briefs. Backup: trig_01SGVvDtrZHjbECD8UZexYQz, one routine at 07:43 and 15:43 Singapore; first check GMS, second check European inventory. Do not create additional publication routines or use run_daily.py --catch-up.

## Replenishing inventory

1. Fetch the latest execution branch and the relevant source branch. Read root SOCIAL_MARKET_RULES.md, current STYLE.md, concise PERFORMANCE.md and cloud `social-cloud-backup/performance/<brand>.json`/`.md`. Source branches: GMS claude/ricerche-automatiche-performance-x5pstt (sowld-social), SP claude/socialperks-continuous-build-lgdgd6 (social-video), Sin claude/graduate-deadlines-consulting-k8obxv (sincronia/social).
2. Read queue.json, state.json and health.json. Target seven future MARKET days, eight UNIQUE topics/day/brand. Never copy another brand's date or clock. Stop cheaply if healthy. Backup acts only on actual gaps or failed primary work; never overwrite a recent primary preparation. Use a fresh branch and fast-forward/merge preserving newer work; a conflicting queue edit means re-read, never force-push.
3. Render real JPGs/JSON and GMS videos into `social-cloud-backup/queue/<brand>/<local-date>/carousel-<slot>/`. GMS has one reviewed reel per day in `reel/` and seven prebuilt 1080x1920 Shorts in carousel folders. Every source slide, cover and reel scene requires visual review. No fabricated QA flag or regenerated hashes on unreviewed images. The GMS cloud copy's carousels.py is a publishing dependency, not a full current renderer: use the SOURCE branch renderers and current real shop photos.
4. Extend queue.json in the existing schema: stable unique id, brand, date, slot, folder, exact title, sha256 for JPG/JSON/MP4. Reel entries have kind=reel and reel_sha256. GMS publish_order places the reel at lunch; assign the rest by Singapore context. Never reuse an id/title already in queue or receipts. No secrets or private telemetry in public commits.
5. Run `python -m unittest discover -s social-cloud-backup -p 'test_*.py'` and `python social-cloud-backup/controller.py --validate` with genuine ffprobe available. The validator checks all exact media hashes, eight topics per brand/date, no duplicate IDs/titles and one actual valid MP4 per GMS topic. Commit approved files and manifest; fetch/merge remote state before pushing. Never overwrite state.json.
6. Manual workflow mode `check` verifies identities/histories/media and does NOT publish; `validate` uses no social credentials. Normal publication is scheduled. `recover-gms` is a dated 3 November exception and must not be used later. Durable receipts and platform history jointly enforce caps despite eventual consistency.

## Health and optimisation

`health_report.py` runs after workflows, independently of publish success. It takes at most one public-result snapshot per brand's own day: Instagram likes/comments for each brand, plus available Facebook, Threads and YouTube counters for GMS. It writes local-hour medians for mature Instagram posts and keeps missing metrics explicit. The current Facebook grant permits publishing and history but does not expose engagement counters; this is not recorded as zero. It does not claim reach, demographics, orders, ROAS or causal best times from public likes. Editors read real results, adapt audience-specific themes/captions and only change timing when sample sizes justify it. Never mix engagement across brands or markets.

Health reports show seven-day actual reviewed coverage. Below three days including today, one GitHub issue is opened/updated; it closes when coverage recovers. A queue shortage is a real issue, not permission to re-post yesterday or invent an image. A current-day shortage stops only the affected brand. Platform restrictions and ambiguous responses hold only their channel. Report exact required token reauthorization; never buy credits, revoke grants, bypass limits or reveal credentials. Existing schedules resume when Claude quota resets; backup idles once primary work/coverage is healthy.

Current starting inventory was visually verified for 3–5 November only. This is a fact, not seven days of coverage. Replenish promptly when either editor regains quota; cloud health makes the gap visible. A failure-free software schedule cannot guarantee future platform uptime, valid tokens or unlimited fresh content without a functioning editor.

One hourly UTC :41 recovery check shares the same publisher lock and receipts. It does not introduce UTC marketing times: each brand still uses its own local target, date, approved inventory and eight-post cap, and Facebook keeps 60 actual minutes. It only recovers due items after a delayed or missed market-specific trigger.

## Server-timed fallback when cron events are delayed

`social-cloud-watchdog.yml` (workflow ID 405490346, "Social cloud recovery timer") is explicitly dispatched by the final always-run step of the same trusted publisher on the default branch. The timer explicitly dispatches that publisher again; it does not rely on implicit workflow_run chains. Environment `social-publisher-recovery-wait` holds the next recovery for 45 minutes on GitHub's servers, without a runner waiting. Each newer publisher completion replaces the older waiting watchdog. After the timer, it checks that the publisher is still active and dispatches the SAME guarded publisher, not another posting script. A disabled publisher stops the chain. The timer has no social secrets and only read-contents/actions-write for its own repository. No untrusted code or PR payload is executed.

Manual `smoke_test=true` uses the separate one-minute `social-publisher-recovery-smoke` environment ONCE. Automatic successors always return to the normal 45-minute environment. Do not shorten the normal timer or leave a rapid dispatch loop. Ordinary cancelled watchdogs are expected when superseded by a newer successful publisher; check the newest waiter rather than alarming on an older cancellation.

Initial timer-release proof on 3 November: 41608706243 waited, completed successfully and automatically dispatched publisher 41608862247 with GitHub's ephemeral token. The permanent version uses explicit workflow_dispatch in both directions so it does not depend on implicit workflow_run propagation. Native cron events had not yet been observed; do not rewrite that history as cron success. This fallback removes dependence on cron delivery, a Mac or Claude quota for consuming the reviewed queue. Actual future inventory and platform authorization are still required.

Platform restrictions are persistent across runs: state.json records platform_block:<brand>:<channel>. Following recoveries skip that channel BEFORE any API call, and health reporting retains prior metrics without extra probes for that brand. The first restriction is an error; repeated skips do not spam failure alerts. Only clear a lock after verified operator review/reauthorization; ambiguous item holds still require reconciliation. Health.json lists paused_channels. This protection must not be removed by a replenishment or quota-reset routine.

## Facebook image-loss correction, 3 November
Product link-preview cards continued to show blank pictures after scraping. New Facebook posts use unpublished native Page photos, verify stored images for every photo, then attach their IDs in a single photo post. Product names, SGD prices and full product URLs remain in captions. No temporary preview URL is used in the feed. Facebook controls the grid/swipe placement. Existing broken posts have not been rewritten or deleted. Do not restore the child_attachments format without verified evidence. No feed POST is blindly retried.

## Facebook format repair, 3 November evening
The screenshots show missing images in old multi_share_no_end_card link posts. API media URLs alone are not visual proof. Future posts use durable native Page photo IDs, not child_attachments/link-preview cards. Slots 4 and 8 are verified message-hoodie product showcases; other carousel slots use the actual reviewed editorial JPGs and original caption. All contain the full shop URL. No temporary image hosts. Native upload and stored-image acknowledgement precede the single feed creation. Existing old link posts are not repaired by this code change and must not be claimed repaired. Reels are optional only after their own supported publisher and reviewed inventory are verified.

### Native product showcase reliability (3 November evening)

Facebook product slots 4/8 bake verified photo/name/SGD price into a portrait native upload; other slots attach every reviewed editorial slide. Sources and Facebook-native photo dimensions must be at least 320×320. A tiny/missing acknowledgement stops before feed creation, not a partial or link-preview fallback. Product destinations remain in captions. Older broken posts are not implicitly repaired by the new format. YouTube preflight rejects missing or silent audio; preserve original GMS music and test receipts.

### Timely content is editorial, not an autonomous news publisher

The owner permits occasional relevant news explainers within the normal daily slots, subject to the source/date/rights checks in SOCIAL_MARKET_RULES.md. Existing publisher only consumes reviewed assets. Do not create another news posting routine or publish the screenshot’s financial story without fresh verification and brand relevance.

### First baked product showcase visually verified, 4 November

Normal scheduled Facebook post https://www.facebook.com/1429179606036501/posts/1431621302458998 was opened in the authenticated browser. All four native images loaded at 960x1200. The first full photo was opened and showed the complete Enjoy The Little Things garment plus baked product name, S$79 price and shop address. The other three product images, SGD labels and full product URLs were present. This verifies the new native format; it does not repair old link-card posts retroactively. No extra test was published.

## Reels and Facebook formats, 5 November 2026
Read the matching section at the end of SOCIAL_MARKET_RULES.md first.

Editors (primary trig_018CzvbW5QE7qNpfvmjE7WMs for SP/Sin, trig_01JyRzzAfbsqvYfv1TBWZP6R for GMS, backup trig_01SGVvDtrZHjbECD8UZexYQz) produce two Reels per brand per new day:
1. Prepare the eight carousels as before (slides + carousel.json + editorial text in editorial/<brand or europe>-<date>.txt).
2. Render the Reels from the reviewed topics: `python social-cloud-backup/reelkit/render.py --brand sp --ids sp-<date>-1,sp-<date>-3,sp-<date>-5,sp-<date>-7 --cache <scratch> --sheets <scratch>/sheets` (from 7 November four Reels a day: Sin slots 1,3,5,7; GMS publish_order 1,6,7, the lunch reel stays in reel/ via publishers/gms/reel.py or reel-<slot> via render.py). Fonts/marks come from the source branches (publishers/<brand>/fonts, assets; not committed). Output: queue/<brand>/<date>/reel-<slot>/reel.mp4, reel.json, cover.jpg.
3. Inspect every contact sheet; fix and re-render anything unreadable, mismatched or off-brief. Copy the sheets to editorial/qa-reels-<date>/.
4. `python social-cloud-backup/reelkit/approve.py --ids ... --qa "Contact sheet inspected <date>"` writes kind=reel, reel_dir and reel_sha256.
5. Run the unit tests and `controller.py --validate`: every MP4 must be referenced by the queue, 1080x1920, 30 fps, H.264 + AAC with decoded non-silent audio; new Reels 15-30 s with a 1080x1920 cover and a caption opening with the exact title.

Publisher: the controller passes REEL_PUBLIC_VIDEO_URL / REEL_PUBLIC_COVER_URL pinned to the commit for any brand and folder (GMS_PUBLIC_VIDEO_URL kept for compatibility). Instagram: publishers/<brand>/reel_publish.py (SP @socialperks.es Europe/Madrid, Sin @sincronia.live Europe/Paris, GMS Asia/Singapore), shared logic in publishers/reel_common.py. YouTube uses the Reel of reel items. Facebook: reel items go to publishers/gms/fb_reel_publish.py (native Page Reels, local upload to rupload.facebook.com, status read-back); 2/5/8 go to fb_publish.py --format cards. Facebook history now includes Page Reels and a durable last_publish_utc receipt also enforces the 60-minute gap. `--check` runs `fb_publish.py --diagnose-cards` (read-only).

If state.json has fb_cards_paused, cards are off and slots 2/5/8 use the native showcase. Clear it only after reviewing the logged evidence and fixing the cause.
