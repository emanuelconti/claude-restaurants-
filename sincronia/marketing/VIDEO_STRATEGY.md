# Video content strategy — Sincronia

Consolidated record of everything worked out on video/social content for Sincronia,
so none of it depends on chat history or on the hosted call-sheet artifact staying
reachable. Covers: the viral-hooks research, the frame-assembly prompt, and the
full 30-day call sheet (22 scripts).

---

## 0. Honesty notes (read before using any of this)

- **No access to the real IG/TikTok accounts.** `socialperksapp` / `sincronia.live` /
  `sowld.ai` on Instagram and `sincronia.live` / `sowld_ai` / `socialperks_app` on
  TikTok could not be analyzed — Instagram rate-limited the request (HTTP 429),
  TikTok's feed is a JS-rendered SPA that returns no data without a real browser
  session. Anything below about "what works" is **general 2026 research for the
  B2B/finance niche**, not a study of your actual channels' past performance.
- **The uploaded promo video (`Sincronia_CORRETTO_2.MP4`) has no usable voice
  track.** Checked with ffmpeg: mean volume -55dB, effectively silent (likely just
  a music bed). Not a source for a "write in my voice" skill.
- **The 22 scripts below are written in a researched "direct founder, no-fluff"
  voice**, not literally the founder's own voice — that requires real writing/speech
  samples from the founder, which haven't been provided yet (see open item below).
- Every fact used in the scripts (grant amounts, coverage %, official links) comes
  from `sincronia/data/programs.json` / `sincronia/marketing/esempio_report.md`,
  last verified 2026-08-22. Nothing here is invented, and none of it references
  fake clients, fake reviews, or fake scarcity.

---

## 1. Viral hooks & formats — what the research says, and why

Source data pulled August 2026. Full citations at the bottom of this section.

### Hook types that outperform for B2B/finance content
1. **Niche callout** — "If you run a B2B company under 10 people in Italy or Spain
   — this is for you." Filters the viewer instantly; for B2B specifically this
   reads as credibility, not just an audience filter.
2. **Contrarian statement** — "Getting a grant isn't hard. Finding the right one
   is." Forces attention because the brain can't leave a stated contradiction
   unresolved — and it happens to be literally true for this niche.
3. **Expert-explainer** — "I read the EIC Accelerator's 40-page guidelines so you
   don't have to." Signals competence in sentence one; trust is the entire product
   in a funding/finance niche.
4. **List-reveal** — "3 EU funding programs almost nobody applies to." Creates a
   completion commitment once the viewer processes "3 things."

**Avoid:** "let me tell you a story" openers (need trust not yet earned) and
face-on "Hi everyone, today we'll talk about..." — that's YouTube grammar, not
short-form grammar.

### Formats that are winning right now
| Format | Why it works | Where it already exists in this project |
|---|---|---|
| Screen-recorded process content | "content from real work" beats scripted talking-head | `sincronia/marketing/report-preview.html` |
| Visual contrast / before-after | communicates a comparison in <30s, no narration needed | `#compare` section of `index.html` |
| Edutainment (educational + genuinely engaging) | best-performing content *type* on LinkedIn specifically right now | the "3 grants nobody talks about" format below |
| No-face, voice-only | doesn't disqualify from the top hook types | matches the founder's existing no-face constraint |

### Technical rules (2026)
- Vertical video: 4:5 (1080×1350) is currently favored in-feed on LinkedIn over
  square/horizontal; 9:16 for TikTok/Reels/Shorts.
- Videos under 90s for completion rate; ideally under 30s for cold reach.
- **Native video only** — a link in the caption/post cuts organic reach up to ~30%.
  Put the link in the first comment or bio.
- **Always burn in captions** — sound-off is the default watching mode.
- The hook must deliver the actual payoff, not tease it. In this niche the
  information itself *is* the value — teasing it reads as clickbait to a founder
  audience with zero patience for it.

### Sources
- [Opus — 5 TikTok Hook Types 2026](https://www.opus.pro/blog/tiktok-hooks-that-go-viral-2026)
- [Conbersa — Best TikTok Hooks](https://www.conbersa.ai/learn/best-tiktok-hooks)
- [Teleprompter — Short-Form Video Strategy 2026](https://www.teleprompter.com/blog/short-form-video-strategy)
- [Visla — LinkedIn Video 2026: What's Working](https://www.visla.us/blog/guides/linkedin-video-in-2026-whats-working-and-how-to-make-it/)
- [Shootsta — LinkedIn Video Strategy 2026](https://shootsta.com/blog/linkedin-video-strategy-in-2026-the-ultimate-b2b-guide)
- [Parmonic — LinkedIn Video Formats 2026](https://info.parmonic.com/blog/linkedin-video-formats-in-2026-what-works-best-for-b2b-marketing)
- [Eclincher — Best Time to Post on LinkedIn for B2B & Financial Services 2026](https://www.eclincher.com/articles/best-time-to-post-on-linkedin-for-b2b-financial-services-2026)
- [Kanbox — Best Time to Post on LinkedIn 2026](https://www.kanbox.io/blog/best-times-to-post-on-linkedin)

---

## 2. Frame-assembly prompt (for CapCut / Sora / any AI video-from-images tool)

Written to animate the 10 English-language screenshot frames (site scroll + the
sample-report "output" frames) into one 24-30s vertical video. Self-contained —
paste as-is along with the 10 frames.

```
Crea un video verticale 9:16 (per Reels/TikTok/Shorts), durata 24-30 secondi,
a partire da 10 immagini statiche che ti fornisco in ordine (01→10).
Le immagini sono screenshot reali di un sito web e di un report di esempio,
tema grafico chiaro/crema con accento terracotta (#b5622e), font titoli serif.

CONTESTO: il prodotto è "Sincronia" — un servizio che trova bandi e
finanziamenti pubblici europei compatibili con l'azienda dell'utente e
rivede la candidatura prima dell'invio. Target: piccole imprese e startup
in Italia, Francia, Spagna, Portogallo, Germania.

STRUTTURA (rispetta l'ordine e i tempi, il gancio nei primi 2 secondi è
la cosa più importante — se non cattura l'attenzione lì, il video muore):

0:00-0:02 — FRAME 01 (hero). Zoom-in lento (Ken Burns) da 100% a 108%
   partendo centrato sul titolo "Find the grants and funding your
   company is eligible for." Testo overlay grande, bold, bianco con
   contorno scuro, che appare in 0.3s: "Your company qualifies for
   grants you don't know exist" — deve comparire ENTRO il secondo 2.

0:02-0:05 — FRAME 02 (confronto). Pan leggero da sinistra a destra.
   Overlay: "Doing it alone vs. doing it right" (piccolo, in alto).

0:05-0:08 — FRAME 03 (come funziona). Zoom-in leggero sul primo step.
   Overlay: "3 steps. 48 hours."

0:08-0:11 — FRAME 04 (revisione candidatura, foto documenti). Pan
   lento verso il basso, leggero blur-in iniziale che si risolve.
   Overlay: "Every application, checked line by line."

0:11-0:14 — FRAME 05 (tabella bandi reali). Zoom-in sulla tabella,
   abbastanza lento da far leggere 1-2 righe (es. Smart&Start Italia,
   EIC Accelerator). Overlay: "Real programs. Official links. Verified."

0:14-0:17 — FRAME 06 (pricing). Zoom-in sul prezzo "€149".
   Overlay: "From €149 — not a subscription."

0:17-0:19 — FRAME 07 (FAQ). Pan veloce, quasi un flash, 1.5s max
   (questo frame serve solo a dare ritmo, non a essere letto).

0:19-0:22 — FRAME 09 (report esempio, banner "SAMPLE REPORT" in alto).
   IMPORTANTE: il banner giallo "⚠️ SAMPLE REPORT — fictional company,
   illustrative only. Not a real client." deve restare leggibile,
   NON tagliarlo e non velocizzarlo troppo — è un disclaimer reale e
   deve essere visibile per almeno 1.5s intero.
   Overlay: "Here's what you actually get:"

0:22-0:25 — FRAME 10 (card dei bandi compatibili nel report). Zoom-in
   lento sulle card con i link ufficiali.

0:25-0:28 — FRAME 08 (footer/CTA "Ready?"). Zoom-in sul bottone
   "Tell us about your company". Overlay finale, grande:
   "sincronia.live — find your grants" con un piccolo arrow/tap
   animation sul bottone.

TRANSIZIONI: dissolvenza incrociata di 0.2-0.3s tra ogni frame, mai
tagli secchi, mai transizioni "flashy" (niente cubi 3D, niente
glitch) — il tono è professionale/editoriale, non hype da infoprodotto.

MUSICA: strumentale, minimale, leggermente in crescendo (piano/synth
soft, tipo "corporate calm" o "lofi motivational"), volume basso
sotto il testo, nessun drop.

SOTTOTITOLI: aggiungi i testi overlay anche come sottotitoli in basso
per chi guarda senza audio (la maggioranza su TikTok/Reels/Shorts).

REGOLE NON NEGOZIABILI — non violarle per nessun motivo:
- Non aggiungere numeri, statistiche, recensioni, testimonianze o
  loghi di clienti che non siano nelle immagini originali.
- Non rimuovere né rendere illeggibile il banner "SAMPLE REPORT" nel
  frame 09/10 — è un disclaimer legale, deve restare visibile.
- Non aggiungere claim tipo "già usato da centinaia di aziende" o
  simili: sono falsi e non vanno inventati.
- Non alterare i testi reali visibili negli screenshot (prezzi, nomi
  dei bandi, link) — puoi solo animarli/zoomarli, non modificarli.
```

The 10 source frames referenced above (English, site switched to `#lang-switch
button[data-lang="en"]`) were generated via Playwright and delivered directly to
the founder as files — they are not stored in the repo (screenshots, not
production assets). Regenerate with the same script pattern used in this
session if needed again: load `landing/index.html` locally, click the EN
language button, scroll to trigger lazy images, capture 8 site-scroll frames +
2 frames of `marketing/report-preview.html`.

---

## 3. The 30-day call sheet (full scripts)

Live, filterable version: **https://claude.ai/code/artifact/794774aa-76f5-41e3-b186-95df5ddf1887**
("Sincronia Call Sheet"). Full content mirrored below so it survives independent
of that link.

### System
- **5 posting days/week, Mon-Fri. Weekends intentionally off** — B2B engagement
  drops on Sat/Sun per the research above, and a solo founder needs the days back.
- **5 pillars rotate on a fixed weekday**, so content becomes a habit instead of
  22 separate creative decisions:

| Day | Pillar | IG time (CET) | TikTok time (CET) |
|---|---|---|---|
| Mon | Program Spotlight | 09:00 | 19:30 |
| Tue | Myth-Busting | 12:00 | 20:00 |
| Wed | Output Reveal | 19:00 | 12:30 |
| Thu | Reality Check | 09:30 | 20:00 |
| Fri | Listicle | 12:00 | 19:00 |

**Why these slots:** Tue-Thu mid-morning/mid-afternoon is the strongest general
B2B/finance window → myth-busting and reality-check land there. Italy/France show
a real midday scroll spike (12-2pm, lunch-driven) → output-reveal uses that slot
on TikTok since it's a slower watch that benefits from an actual pause in someone's
day. 7-10pm CET is the broadest cross-market TikTok window in Europe → used for
the two most shareable, lowest-effort-to-watch formats (spotlight, listicle).
Weekday mornings/evenings are Instagram Reels' strongest windows; lunch works well
for a list format finishable in one scroll-stop.

**Validate later:** once there's enough follower data, check
`TikTok → Creator Tools → Analytics → Followers → Follower Activity` and
Instagram Insights, and nudge these times toward the real audience.

### Week 1

**Mon — Program Spotlight**
Hook: *"€2.5M grant + equity. Most founders have never heard of this one."*
1. Programs table, zoom on EIC Accelerator row — *"EIC Accelerator. EU-wide. Grant plus equity — up to €2.5 million, covering 70% of your costs, plus €1 to 15 million in equity on top."*
2. Cut to eic.ec.europa.eu on screen — *"Part of Horizon Europe. Yes it's real — link's on screen, verify it yourself."*
3. Text card "Best for: deep-tech, high-risk, high-innovation" — *"It's built for high-risk, high-innovation projects. Not everyone fits — that's exactly why we check before you apply."*
On-screen: EIC ACCELERATOR — up to €2.5M · CTA: Full breakdown at sincronia.live

**Tue — Myth-Busting**
Hook: *"Grants are only for tech startups. That's false — and it's costing non-tech businesses money."*
1. Split screen "tech startup" vs "local SME / logistics / retail" — *"Programs like Kit Digital or the Interreg voucher don't care what industry you're in. They care whether you're actually investing in the business."*
2. Cut to ENISA table row — *"ENISA literally says: any sector, with a differential project. You don't need to be building an app."*
On-screen: MYTH: "tech only" — FALSE · CTA: Check what actually applies to you

**Wed — Output Reveal**
Hook: *"Here's the actual report — not a mockup, this is the real format."*
1. Scroll report-preview.html, SAMPLE REPORT banner visible — *"This is a sample — fictional company, clearly labeled — but it's the exact format every real report follows."*
2. Zoom on analyst note card — *"First, an analyst note: which programs actually fit, and why."*
3. Pan across program cards with links — *"Then every compatible program, with the official link and the date we last verified it."*
On-screen: ⚠️ SAMPLE REPORT — real format, fictional company · CTA: From €149 — sincronia.live

**Thu — Reality Check**
Hook: *"Doing this alone vs. doing it with someone who reads the guidelines for a living."*
1. #compare table, left column "alone" — *"Alone: you search, you guess which programs apply, you hope the budget is right."*
2. Right column "with Sincronia" — *"With us: a matched list, official links, and a review before you submit."*
On-screen: ALONE vs WITH SINCRONIA · CTA: See the comparison — sincronia.live

**Fri — Listicle**
Hook: *"3 EU funding programs almost nobody applies to."*
1. *"One: Bourse French Tech — up to €50,000 for your very first validation expenses."*
2. *"Two: Interreg Italy–France Maritime — a voucher up to €6,900 for digital or ecological transition."*
3. *"Three: EIC Pathfinder — up to €2.5 million for early-stage deep-tech, before you're anywhere near market-ready."*
On-screen: 3 GRANTS NOBODY APPLIES TO · CTA: All tracked, with official links — sincronia.live

### Week 2

**Mon — Program Spotlight**
Hook: *"0% interest. Up to €1.5M. Rolling applications — no deadline to miss."*
1. Programs table row — *"Smart&Start Italia. Zero-percent loan plus a grant portion, up to €1.5 million, covering 90% of eligible costs."*
2. Calendar graphic, "no fixed deadline" — *"No fixed deadline — it's a rolling window, managed by Invitalia, so you apply whenever you're ready."*
3. Link invitalia.it on screen — *"Official source on screen. We only send links we've personally verified."*
On-screen: SMART&START ITALIA — 0% + grant, up to €1.5M · CTA: See if you qualify — link in bio

**Tue — Myth-Busting**
Hook: *"You don't need connections to get a grant. You need someone who actually reads the guidelines."*
1. Stack of PDF/guideline pages — *"Every program we list is public. Anyone can apply. The reason most founders never do is nobody has time to read a 40-page eligibility document."*
2. Cut to report card — *"That's the actual job — not knowing someone. Just doing the reading."*
On-screen: MYTH: "you need connections" — FALSE · CTA: We already did the reading — see the database

**Wed — Output Reveal**
Hook: *"Before you submit anything, we check three things most people skip."*
1. Text list: budget / red flags / missing pieces — *"Does the budget actually add up. Are there red flags — like a market-size number with no source. Is anything missing evaluators expect to see."*
2. Application-review photo band — *"Every application, checked line by line, before it goes anywhere."*
On-screen: 3 CHECKS BEFORE YOU SUBMIT · CTA: Add the review — see pricing

**Thu — Reality Check**
Hook: *"3 reasons an application gets rejected — and none of them are 'bad idea.'"*
1. *"One: the budget doesn't reconcile with what's being asked."*
2. *"Two: a claim with no source — a market number nobody can verify."*
3. *"Three: a required document, simply missing."*
On-screen: 3 REASONS APPLICATIONS GET REJECTED · CTA: We catch these before you submit

**Fri — Listicle**
Hook: *"3 signs you probably qualify for a grant you don't know about."*
1. *"One: you're investing in digitizing something — a process, a website, a system."*
2. *"Two: you work with a partner in another country."*
3. *"Three: you have a specific number in mind — €25K, €150K, doesn't matter. There's likely a program sized for it."*
On-screen: 3 SIGNS YOU QUALIFY · CTA: Find out which one — sincronia.live

### Week 3

**Mon — Program Spotlight**
Hook: *"No personal guarantees. Up to €1.5M. Spain's best-kept secret for founders."*
1. Table row highlight — *"ENISA. A participative loan from Spain's Ministry of Industry — from €25,000 up to €1.5 million."*
2. Text "NO personal guarantees required" — *"The part people don't expect: no personal guarantees. It's underwritten on the project, not your personal assets."*
3. Link enisa.es — *"Open all year. Official link on screen — verify it yourself."*
On-screen: ENISA — €25K–€1.5M, no personal guarantee · CTA: Check eligibility at sincronia.live

**Tue — Myth-Busting**
Hook: *"Not every grant has a once-a-year deadline. Some you can apply to today."*
1. Calendar with most days circled — *"Smart&Start Italia and ENISA are both rolling — no fixed annual deadline."*
2. Contrast with Eurostars fixed window — *"Others do have real windows, like Eurostars — which is exactly why tracking the calendar matters."*
On-screen: MYTH: "grants take years" — FALSE · CTA: See which ones are open right now

**Wed — Output Reveal**
Hook: *"We don't ask you to trust us. Every link in your report is official — check it yourself."*
1. Program card zoom: official link + verified date — *"Every program in your report links straight to the government or EU page — not to us."*
2. Pan across 2-3 cards — *"And every one carries the date we last verified it's still accurate."*
On-screen: REAL LINKS. REAL DATES. · CTA: Real links. Real dates. sincronia.live

**Thu — Reality Check**
Hook: *"Most grant consultants take a cut of what you're awarded. We don't."*
1. Pricing section, €149/€349 tiers — *"Flat fee. €149 for the match report, €349 if you want the application reviewed too."*
2. Text "no success fee, no % of the grant" — *"No percentage of what you receive. What you're awarded is yours."*
On-screen: FLAT FEE. NO SUCCESS FEE. · CTA: See both packages — sincronia.live

**Fri — Listicle**
Hook: *"3 numbers worth knowing before you write a single word of your application."*
1. *"EIC Accelerator covers 70% of costs, up to €2.5 million."*
2. *"Smart&Start Italia covers 90% of eligible costs, up to €1.5 million."*
3. *"The Interreg voucher tops out at €6,900 — small, but nowhere near the competition of the big ones."*
On-screen: 3 NUMBERS TO KNOW · CTA: Full database at sincronia.live

### Week 4

**Mon — Program Spotlight**
Hook: *"€3M for founders who work with a partner outside their own country."*
1. Table row, map graphic — *"Eurostars Call 11. Up to €3 million — but only if your project has an international R&D partner."*
2. Text "requires 1+ partner in another Eurostars country" — *"That's the catch and the opportunity. If you already work with a supplier or client abroad, this might already fit you."*
3. Link eurostars-eureka.eu — *"Application windows open seasonally. Check the live dates on the official site — we link it every time."*
On-screen: EUROSTARS CALL 11 — up to €3M, international R&D · CTA: We track the real windows — sincronia.live

**Tue — Myth-Busting**
Hook: *"Too small for a grant? There's one designed for a company that doesn't exist yet."*
1. Table row + "constituted or to-be-constituted" — *"Smart&Start Italia is open to startups not even incorporated yet."*
2. Bourse French Tech row — *"Bourse French Tech is built for the very first validation expenses — before you have real traction."*
On-screen: MYTH: "too small" — FALSE · CTA: Small isn't the disqualifier you think it is

**Wed — Output Reveal**
Hook: *"Here's the whole process, start to finish — no black box."*
1. start.html form fields — *"You tell us your sector, country, and stage."*
2. Report output — *"You get back the programs that actually match, with an option to have the application reviewed before you send it."*
3. #how 3-step cards — *"Three steps. No jargon, no guesswork."*
On-screen: 3 STEPS. NO BLACK BOX. · CTA: Start here — sincronia.live

**Thu — Reality Check**
Hook: *"No bot decides what you get. A person reads your submission — every time."*
1. start.html form submit — *"You fill in your sector, country, stage."*
2. Cut to footer/contact — *"It goes to a real person, not an automated pipeline. A rushed match is worse than no match."*
3. Report output — *"You get the report back with everything checked."*
On-screen: A HUMAN READS EVERY SUBMISSION · CTA: sincronia.live

**Fri — Listicle**
Hook: *"3 things almost every rejected application has in common."*
1. *"No clear budget breakdown — numbers that don't add up when you check them."*
2. *"A claim with no source — 'huge market opportunity' and nothing backing it."*
3. *"A required annex, just… missing."*
On-screen: 3 THINGS REJECTED APPLICATIONS SHARE · CTA: We check for all three before you submit

### Week 5 (2 days)

**Mon — Program Spotlight**
Hook: *"Up to €29,000 just to go digital. Most Spanish SMEs never claim it."*
1. Table row — *"Kit Digital. A digital voucher from the Spanish government, up to €29,000."*
2. Text "for digitizing an existing SME" — *"Not for a new company — for an existing SME that wants to digitize. Website, e-commerce, cybersecurity, whatever you actually need."*
3. Link acelerapyme.gob.es — *"Official source, on screen, like always."*
On-screen: KIT DIGITAL — up to €29,000 · CTA: Full list at sincronia.live

**Tue — Myth-Busting**
Hook: *"Grants aren't free money. They're a real application that gets rejected for real reasons."*
1. report-preview.html analyst-note card — *"Every program has requirements — a budget that has to add up, criteria you actually have to meet."*
2. "checked line by line" text from #how — *"That's the part that gets applications rejected. Not the idea — the paperwork around it."*
On-screen: MYTH: "free money, no work" — FALSE · CTA: We check the paperwork before you submit

---

## 4. Open items

- **Voice-matching skill**: requested via `/skill-creator`, blocked on real writing/
  speech samples from the founder (captions already published, scripts, voice
  memos transcribed, DMs to leads/clients — anything in his actual voice, not chat
  messages to Claude). Once provided, revise the 22 scripts above onto the real
  voice and build the skill for future content.
- **IG/TikTok channel analysis**: not possible with current tooling (rate-limits,
  JS-gated feeds, no login). If the founder exports TikTok/Instagram analytics
  (CSV) or sends screen recordings of specific posts, a real performance analysis
  becomes possible.
