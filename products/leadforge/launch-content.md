# LeadForge — Ready-to-post launch content

Copy-paste these as-is, or tweak the bracketed parts. Post in this order:
Reddit/X/LinkedIn first (days 1–5), Product Hunt once you have a few sales
as social proof (day 5+).

---

## Reddit — r/Entrepreneur, r/freelance, r/smallbusiness, r/SaaS

Post as a **text post**, not a link post — link posts get auto-removed on
most of these subs. Put the landing page link only in a comment or your
profile, not the post body, and only after the post gets traction.

**Title:**
> I got tired of paying $99/mo for cold email software, so I built my own script — here's what's in it

**Body:**
```
For the last few months I've been running cold outreach campaigns (thousands
of emails sent) to land partnerships, and every tool out there wanted
$50-300/month for what is, underneath, a scheduler + a database + an SMTP
call.

So I built my own: a Python script that
- sends a 3-step follow-up sequence (initial, follow-up, last touch)
- tracks every lead in SQLite so nothing gets double-emailed
- respects a daily send cap so it doesn't trip spam filters
- stops the sequence the second someone replies or opts out

It runs on a normal Gmail account with an app password. No monthly fee,
because it's not a service — it's a script you own.

Happy to answer questions about the setup or the anti-spam pacing if
anyone's curious. Turned it into a small packaged version for anyone who
doesn't want to build it from scratch — link in my profile if you want it,
not trying to spam the sub with it here.
```

---

## X / Twitter — build-in-public thread

**Tweet 1 (hook):**
> I sent 3,000+ cold emails without a $99/mo SaaS.
>
> Here's the exact script I use — thread 🧵

**Tweet 2:**
> Every cold email tool does the same 3 things:
> 1. Send a sequence on a schedule
> 2. Track who replied / opted out
> 3. Not get you flagged as spam
>
> That's a database and an SMTP call. Doesn't need to cost $300/mo.

**Tweet 3:**
> So I built LeadForge: Python script, SQLite tracking, runs on your own
> Gmail. Daily send cap + pacing built in so you don't get blacklisted.
>
> [screenshot of `leadforge.py status` output]

**Tweet 4:**
> Stops the sequence the moment someone replies. No more accidentally
> emailing someone who already said no.

**Tweet 5 (CTA):**
> Packaged it up for anyone who wants the setup without writing it from
> scratch: [landing page link]
>
> $49, one-time, yours to keep.

---

## LinkedIn — single post

```
I stopped paying for cold email software.

Every tool in this space (Lemlist, Instantly, Apollo...) charges a monthly
fee for the same core mechanics: a send schedule, a tracking database, and
pacing to avoid spam filters.

I built a script that does exactly that, runs on a normal Gmail account, and
costs $0/month because it's not a service — you own it outright.

If you're a freelancer or small agency doing your own outreach and tired of
subscription pricing for a tool you use for one campaign a quarter, I
packaged it: [landing page link]

#coldemail #freelancing #outreach #smallbusiness
```

---

## Product Hunt listing (use once you have 3-5 sales as proof)

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
