# Social cloud publishing by market

Runs on GitHub-hosted Ubuntu, independently of the owner's Mac and Claude subscription quota. Standing service authorised by the owner on 3 November 2026, including after the Thursday Claude quota reset. Only approved inventory can be published; current coverage is recorded in health.json. No payments or paid AI calls.

## Coverage

72 reviewed topics: eight per brand per day for three days. SocialPerks and Sincronia each have 24 Instagram carousels. Good Message Studio has one reel and seven carousels per day; the same daily eight topics cover Instagram, Facebook, Threads and YouTube, using the channel's format. Its 24 YouTube files are prebuilt, including three reels. The accompanying carousel for each reel supplies Facebook and Threads.

Maximum 144 channel publications across the three days, reduced by posts already published by Claude. These are queued publications, not claims of completed posts. Platform rejection, expired credentials or unavailable APIs can still stop a channel; the job fails visibly instead of claiming success or bypassing limits.

Each source slide and cover was visually inspected. Each reel hook, five scenes and closing frame was inspected. Short slideshow scene frames are compared with the reviewed source pixels. The manifest binds approved JPGs, metadata and MP4s with SHA256. No fresh content generation on a runner.

## Schedule and duplicate prevention

Each brand has its own calendar and trigger. SocialPerks: Europe/Madrid, primary slots 09:47,11:47,14:47,16:47,17:47,18:47,20:47,22:47; hourly :47 recovery through 23:47. Sincronia: Europe/Paris, primary slots 08:23,10:23,12:23,14:23,16:23,18:23,20:23,21:23; hourly :23 recovery through 23:23. Good Message Studio: Asia/Singapore, primary slots 08:17,10:17,12:17,14:17,15:17,18:17,20:17,21:17; hourly :17 recovery through 23:17, including the owner's night. Each primary slot increases the cumulative local-day target by one up to eight. Recovery checks do not raise the daily cap. The three cron events route to their own brand only. All GMS inner publisher guards also use Asia/Singapore. At most one new item per channel in a run. See ../SOCIAL_MARKET_RULES.md for distinct audience briefs and the common handoff.

Every channel uses its own verified identity, current remote history, count and exact-title deduplication. Claude's posts count towards the same eight/day target. A second read occurs immediately before publishing. Workflow concurrency serializes cloud runs. No cross-account API transaction exists, so simultaneous external publication by Claude cannot be locked by this workflow; its scheduled times are offset from Claude's main runs.

Receipts persist in state.json on codex/social-cloud-backup. A failed or uncertain attempt is held and reconciled against actual remote history before anything further is sent on that channel. No blind retry after a publishing request starts. Platform pushback stops the channel. Facebook retains its 60-minute gap. YouTube verifies actual public visibility; an accepted private upload is not reported as public success.

## Security and boundaries

The owner explicitly authorized the minimal credential set in encrypted GitHub Actions Secret SOCIAL_BACKUP_ENV. Values are masked and never committed. Runtime private/ is ignored; only state.json is persisted. GitHub raw URLs pinned to the checked-out commit serve the reviewed media; no temporary image host is required for Instagram or Threads.

Enabled: SP and Sin Instagram; GMS Instagram, Facebook, Threads, YouTube. Pinterest, TikTok and Stories remain off. There are no App Store, product, pricing, Stripe, outreach or other project changes.

Scheduler: .github/workflows/social-cloud-backup.yml on default branch claude/coao-8jloui, checking out codex/social-cloud-backup. Check and validate modes never publish. The Codex heartbeat monitors cloud status only; it is not a second publisher. Read ../SOCIAL_CLOUD_RUNBOOK.md for primary/backup editor roles, seven-day inventory target, daily public-result snapshots and deduplicated low-inventory alerts.
