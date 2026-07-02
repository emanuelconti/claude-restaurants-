# LeadForge — Launch content that actually moves product

No LinkedIn — wrong audience for a $49 dev tool, and generic "build in
public" LinkedIn posts get ignored. Everything below is either a channel
with actual buyer intent (directories people search when shopping for a
tool) or the one channel that's genuinely unfair for this specific product:
using LeadForge to sell LeadForge.

---

## The unfair advantage: cold-email people who'd actually buy this

You already own a working cold-email sequencer. The people most likely to
buy LeadForge — freelancers and small agencies doing outreach by hand — are
themselves reachable by cold email. Use the product on itself.

1. Build a list of ~150-300 freelance marketers / small agency
   founders / outreach consultants. Fastest sources: search
   "freelance lead generation" or "cold email consultant" on LinkedIn or
   Google, scrape names/emails from agency directories (Clutch, Upwork
   profiles list contact info sometimes), or buy a cheap targeted list on
   Apollo.io's free tier (25 free exports/month).
2. Drop them into `leads.csv` in the same format as everything else.
3. Rewrite the 3 templates in `config.py` to pitch LeadForge itself — draft
   below.
4. Run it exactly like you would for a client campaign. Daily cap 15,
   same pacing.

This is the highest-intent channel you have: everyone on that list has
already proven, by doing outreach for a living, that they'd use a tool like
this. Nothing else on this page targets that precisely.

**Step 1 template:**
```
Subject: the tool I use for my own outreach

Hey {name},

Guessing you send cold email for a living or for clients. I got tired of
paying for Instantly/Lemlist for what's really a scheduler + a database, so
I built my own — then packaged it since a few people asked.

No monthly fee, runs on your own Gmail, does the sequencing/tracking/pacing
part for you. This email came from it, actually.

If that's useful: [link]

- [your name]
```

**Step 2 (day 3):**
```
Subject: Re: the tool I use for my own outreach

Following up — if cold email is part of how you get clients, this replaces
whatever you're paying monthly for it now. $49 once.

[link]
```

**Step 3 (day 7, last one):**
```
Subject: last one

Not going to keep emailing about this. Link's here if it's ever useful:
[link]
```

Keep this list separate from any client work — it's your own funnel, not
outreach you're running on someone else's behalf.

---

## Reddit — r/Entrepreneur, r/freelance, r/smallbusiness, r/SaaS

Text post, not a link post — link posts get auto-removed on most of these.
Don't put the link in the body. Put it in a comment once someone asks, or
in your profile.

**Title:**
> Built my own cold email tool because Instantly wanted $97/mo for a scheduler and a database

**Body:**
```
Been doing outreach for partnerships/clients for a while and got annoyed
paying monthly for tools that are, underneath, a send schedule + a tracking
table + rate limiting so you don't get flagged as spam. That's not $97/mo
of infrastructure.

Wrote my own in Python. Runs off a normal Gmail account with an app
password. Tracks who's been sent what in SQLite so nobody gets double
emailed. Stops the second someone replies or opts out.

Not selling anything here, just sharing because I see this complaint a lot
in this sub specifically. If anyone wants the packaged version instead of
building it themselves, it's in my post history / profile.
```

Reply to every comment. This post lives or dies on the comments, not the
post itself — that's where people ask "does this work with X" and you
close them.

---

## X / Twitter

Skip the "thread with hook" format — it reads as templated now and people
scroll past it. One post, plainly stated, with a real screenshot attached
(use `landing-page/assets/terminal.png`, already in this repo).

> spent 3 years paying for cold email tools that are basically a for-loop
> with a database
>
> built my own, it's just python + sqlite, runs on gmail
>
> packaged it up: [link] — $49 once, no subscription

Follow-up reply a day later, only if the first post got any traction:

> a few people asked what's actually in it — daily send cap, 3-step
> sequence, stops automatically when someone replies. that's it, that's the
> whole product. no dashboard to log into.

---

## Directories — submit once, they keep sending traffic for free

These are places people actively search when comparison-shopping cold
email tools. Higher intent than social, and it's a 5-minute form each.

- **AlternativeTo** — list LeadForge as an alternative to Lemlist,
  Instantly, Apollo, Woodpecker. This is the single highest-intent listing
  available: people land there already comparing tools.
- **SaaSHub** — same idea, submit under "cold email software"
- **BetaList** — for the pre-launch/early-adopter crowd
- **Indie Hackers** — post in "Show IH", their product-showcase thread, not
  as a separate self-promo post
- **SideProjectors / StartupBase** — quick listings, low effort
- **Gumroad Discover** — automatic once the product's listed, no extra work

## Product Hunt (once you have 3–5 sales as proof)

**Name:** LeadForge — Cold email outreach without the subscription

**Tagline:** A self-hosted 3-step cold email sequencer. One-time payment,
runs on your own Gmail.

**Description:**
```
LeadForge automates the part of cold outreach that's actually tedious —
sequencing, tracking, and pacing — without locking you into a monthly SaaS
fee.

- 3-step follow-up sequence with configurable delays
- SQLite tracking: never double-email a lead or miss a follow-up
- Daily send cap + pacing to protect your sender reputation
- One command to mark a lead as replied or opted out
- Runs on your own Gmail account via an app password — no third-party
  server touches your leads

Built from a real system that has sent thousands of outreach emails for
business partnership campaigns. Packaged as a one-time purchase: $49,
source included, yours to keep and modify.
```

**First comment (post as the maker):**
```
Hey PH! Built this after getting fed up with $50-300/mo cold email tools
for something that's fundamentally a scheduler + a database. Happy to
answer any questions about the anti-spam pacing or the setup — takes about
10 minutes from zero to your first sequence running.
```
