# Writing the day's carousel

Each scheduled run writes one new carousel for SocialPerks' Instagram, in Spanish, and publishes it. These are the rules for that topic.

The owner's brief (30 October): everyday life that anybody likes and sees themselves in. A strong hook, ultra interesting, likeable, never boring. Never a seller's scene, never an ad on the topic's own slides. Three a day, all everyday life (see below).

**What the page is (the owner, the same evening):** people must come away pushed, focused and motivated, and understand that following @socialperks.es does that for them every day. The page is a daily push for your head, your routine and your drive, told through everyday life. Every carousel ends with the slide that says so ("Un empujón para tu día, cada día. Síguenos"), which the renderer adds; the caption says it too. So every topic must leave the reader with a little more energy, clarity or will than before: a reframe, a small action for today, a reason to keep going, a laugh that lightens the load.

**Likes and follows first (the owner, 31 October, replacing the earlier B2B rule).** The page grows only if people like it, save it and follow it, so all three carousels of the day are everyday life: human, motivational, routine, the things anybody recognises. No carousel is written for business owners, and none is about filling restaurants, quiet hours or getting customers: that is the problem SocialPerks solves, but nobody likes a post about it. Be clever: the post earns the follow, and the brand rides along on the last slide.

- **All three are everyday life**, each with its mood (morning push, midday life, evening mindset).
- **Find the link to SocialPerks at the end when it is natural**: friends, plans, going out, the usual order, your favourite bar or café, recommending a place. Then `"cta": true`. When the topic does not touch it, leave `cta` out: a good post with only the follow slide beats a forced link.
- The concept is told **only on the last slide**, never pitched on the topic's own slides.

## Who reads it

Everyone, mostly 20 to 40, in Barcelona and the rest of Spain, scrolling on the phone on the metro, in a queue, in bed. They like a post when they think "this is so me", they save it when it is useful, and they send it to a friend when it is about them both.

## What works

- **Motivation that is useful, never cheesy.** No empty quotes ("cree en ti", "el éxito es…"), no hustle shouting, no guilt. Concrete and kind: a habit that takes two minutes, the trick for a Monday with no energy, what to do when you feel behind, why small wins count, how to stop comparing yourself, the 5 things to do before checking your phone. The reader must be able to do something with it today.
- **Mindset and focus:** discipline vs. motivation, starting before you feel ready, doing one thing at a time, rest that recharges, saying no, getting back on track after a bad week, the people who push you up.

- **The cover title is the hook.** Specific, a little provocative, a promise the slides keep. Patterns that work: a ranking ("Ranking de las 8 peores sensaciones de un lunes por la mañana"), stages ("Las 7 fases de un domingo por la tarde"), "cosas que solo entiende quien…", "frases que dices cada vez que…", small pleasures, the truth about a city, a myth everybody believes, "señales de que…".
- **The everyday:** mornings, Mondays, coffee, alarms, the metro, work and emails, the weekend, Sunday evening, friends and plans that never happen, going out, "solo una y me voy", your usual order, your favourite bar, the hairdresser, the gym in January, rent and flatmates, the city, the beach, the seasons, holidays, the group chat, birthdays, food.
- **One moment per slide**: a heading of a few words, one or two short lines that paint a real scene, and a closing line that lands, funny or warm.
- **Mix the moods across the day**: morning, a push to start (focus, habits, energy, small actions); lunch, everyday life you laugh at or feel warm about; evening, mindset and reflection (what went well, letting go, friends, tomorrow).
- **Concrete beats clever.** "Llevas una hora viendo vídeos de perros" beats "el tiempo libre se nos escapa".

## The link to SocialPerks

SocialPerks lets people bring a friend to their favourite places, and the friend gets a small welcome gift; the place fills its quiet hours with new people who came on a friend's word. Two last slides tell it:

- `"cta": true`, the friend side ("¿Tienes un sitio favorito? Llévate a un amigo."): for topics about friends, plans, going out, favourite places, recommending a spot or "lo de siempre".
- `"cta": "business"`, the venue side: not used for now (the owner, 31 October). Topics are never about running a place.

Leave `cta` out when the topic does not touch friends or places. Never mention SocialPerks, venues signing up or marketing on the topic's own slides: only the last slide says it.

## Photos: new ones every time

The owner (31 October): the carousels kept showing the same photos, because each set holds only 8 to 12 and a carousel uses almost all of them. **Every carousel picks its own photos**, chosen for that topic and for each slide, and different from the ones in the last days' posts.

1. Search Unsplash's API for each slide's scene: `GET https://api.unsplash.com/search/photos?query=<words>&per_page=30&content_filter=high`, with the header `Authorization: Client-ID <key>`, the key read from the environment variable `UNSPLASH_ACCESS_KEY` (never print it). The website and its `napi` search refuse scripts (401), so only the API works. The id is the part after `images.unsplash.com/photo-` in `urls.raw`; skip anything on `plus.unsplash.com`.
2. No faces, no logos or brands, nothing that fights the text. Prefer hands, objects, places and light.
3. Put them in the topic as `"photo_ids"`, cover first, then one per point, in order. Never two the same in one carousel, and avoid any you used in the day's other carousels.
4. Render, then **look at the cover and every slide**. If a photo shows a face, repeats an earlier post or does not fit, swap it and render again.

If `UNSPLASH_ACCESS_KEY` is not set or the search is refused, leave `photo_ids` out: the slot still goes out with the set's photos, and say so in the run's report. The renderer stops when a photo cannot be fetched, so a carousel never goes out in plain colours.

## Never

- Never invent figures, studies or quotes. No statistics at all.
- Never name real people, businesses or brands. Places in a city are fine (Gràcia, el Born, la Barceloneta).
- Nothing mean, political, religious or about bodies; tease situations, never people.
- No em dashes or en dashes (use a colon or a full stop), never the word "perk", no hashtags or emojis on the slides, always "tú".
- Gender-neutral where it can be.
- Never repeat a title or angle already posted: `ig_publish.py --recent 60` prints the first line of the last posts' captions, which is their title. The `EVERYDAY` topics in `carousels.py` are taken too.

## The file

A JSON object, in the same shape as the topics in `carousels.py`:

```json
{
  "title": "Las 7 fases de un domingo por la tarde",
  "hook": "La 5 es la que más duele.",
  "photos": "life",
  "points": [
    ["La siesta que no era siesta", ["«Diez minutitos.»", "Te despiertas a las siete sin saber qué año es."], "El tiempo, en domingo, es otro."]
  ],
  "hashtags": "#domingo #vidareal #humor #barcelona #findesemana"
}
```

- `title` at most 90 characters; `hook` (the caption's second line) at most 120.
- 5 to 8 `points`; each heading at most 52 characters, 1 or 2 lines of at most 95, a closing line of at most 75.
- `photos`: `life` (mornings, notebooks, coffee, sunrise, an alarm clock, an hourglass), `money` (receipts, cards, laptops), `city` (Barcelona, cafés, terraces, toasts, cooking) or `venue` (haircuts, nails, plates, cocktails, a gym). Pick what fits. Every photo has no face.
- `photo_ids`: the Unsplash ids picked for this topic, cover first, then one per point (see "Photos: new ones every time"). Expected on every topic.
- `countdown: true` numbers the points from the highest down, for a ranking.
- `cta`: `true` for the friend side when the topic naturally touches friends or places, otherwise left out (`"business"` is not used for now).
- `hashtags`: optional, 5 to 8 that fit the topic, one string.

`carousel.py --topic <file>` refuses a topic that breaks these limits and says what to fix. Look at the cover and two slides once rendered: if a line wraps badly or a photo fights the text, shorten and render again.
