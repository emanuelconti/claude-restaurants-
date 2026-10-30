# Writing the day's carousel

Each scheduled run writes one new carousel for SocialPerks' Instagram, in Spanish, and publishes it. These are the rules for that topic.

The owner's brief (30 October): everyday life that anybody likes and sees themselves in. A strong hook, ultra interesting, likeable, never boring. Not about businesses, not a seller's scene, not about our brand: if a topic links naturally to SocialPerks, the last slide may say so; if it does not, there is no SocialPerks slide at all. Three a day.

**What the page is (the owner, the same evening):** people must come away pushed, focused and motivated, and understand that following @socialperks.es does that for them every day. The page is a daily push for your head, your routine and your drive, told through everyday life. Every carousel ends with the slide that says so ("Un empujón para tu día, cada día. Síguenos"), which the renderer adds; the caption says it too. So every topic must leave the reader with a little more energy, clarity or will than before: a reframe, a small action for today, a reason to keep going, a laugh that lightens the load.

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

## The link to SocialPerks, only when it fits

SocialPerks lets people bring a friend to their favourite places, and the friend gets a small welcome gift. So a topic about friends, plans, going out, favourite places, recommending a spot or "lo de siempre" may end with the SocialPerks slide: set `"cta": true`. Everything else: leave `cta` out, and the post is pure everyday life. Never mention SocialPerks, venues signing up or marketing on the slides themselves.

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
- `countdown: true` numbers the points from the highest down, for a ranking.
- `cta: true` only when the topic links naturally to bringing a friend to a favourite place.
- `hashtags`: optional, 5 to 8 that fit the topic, one string.

`carousel.py --topic <file>` refuses a topic that breaks these limits and says what to fix. Look at the cover and two slides once rendered: if a line wraps badly or a photo fights the text, shorten and render again.
