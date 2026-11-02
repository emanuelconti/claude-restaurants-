# Temporary cloud social backup

Runs on GitHub-hosted Ubuntu, independently of the owner's Mac and Claude subscription quota. Valid 3–5 November 2026, hard expiry 6 November at 02:00 Europe/Paris. No payments or paid AI calls.

## Coverage

72 reviewed topics: eight per brand per day for three days. SocialPerks and Sincronia each have 24 Instagram carousels. Good Message Studio has one reel and seven carousels per day; the same daily eight topics cover Instagram, Facebook, Threads and YouTube, using the channel's format. Its 24 YouTube files are prebuilt, including three reels. The accompanying carousel for each reel supplies Facebook and Threads.

Maximum 144 channel publications across the three days, reduced by posts already published by Claude. These are queued publications, not claims of completed posts. Platform rejection, expired credentials or unavailable APIs can still stop a channel; the job fails visibly instead of claiming success or bypassing limits.

Each source slide and cover was visually inspected. Each reel hook, five scenes and closing frame was inspected. Short slideshow scene frames are compared with the reviewed source pixels. The manifest binds approved JPGs, metadata and MP4s with SHA256. No fresh content generation on a runner.

## Schedule and duplicate prevention

Cumulative targets at 07:58,08:58,09:58,13:58,14:58,15:58,19:58,20:58 Paris: 1,2,3,4,5,6,7,8. A lightweight cloud check runs hourly 07:58–23:58 to allow recovery, particularly when Facebook's 60 actual minutes have not elapsed. Recovery checks do not raise the target or daily cap. At most one new item per account/channel in a run.

Every channel uses its own verified identity, current remote history, count and exact-title deduplication. Claude's posts count towards the same eight/day target. A second read occurs immediately before publishing. Workflow concurrency serializes cloud runs. No cross-account API transaction exists, so simultaneous external publication by Claude cannot be locked by this workflow; its scheduled times are offset from Claude's main runs.

Receipts persist in state.json on codex/social-cloud-backup. A failed or uncertain attempt is held and reconciled against actual remote history before anything further is sent on that channel. No blind retry after a publishing request starts. Platform pushback stops the channel. Facebook retains its 60-minute gap. YouTube verifies actual public visibility; an accepted private upload is not reported as public success.

## Security and boundaries

The owner explicitly authorized the minimal credential set in encrypted GitHub Actions Secret SOCIAL_BACKUP_ENV. Values are masked and never committed. Runtime private/ is ignored; only state.json is persisted. GitHub raw URLs pinned to the checked-out commit serve the reviewed media; no temporary image host is required for Instagram or Threads.

Enabled: SP and Sin Instagram; GMS Instagram, Facebook, Threads, YouTube. Pinterest, TikTok and Stories remain off. There are no App Store, product, pricing, Stripe, outreach or other project changes.

Scheduler: .github/workflows/social-cloud-backup.yml on default branch claude/coao-8jloui, checking out codex/social-cloud-backup. Check and validate modes never publish. The temporary Codex heartbeat monitors cloud status only; it is not a second publisher.
