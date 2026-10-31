# Writing a Sincronia carousel

Each scheduled run writes one carousel for @sincronia.live, in **English**, and
publishes it. These are the rules for that topic.

**Why English.** Sincronia's audience is founders and small companies across
Italy, France, Spain, Germany and Portugal. No single national language reaches
them; English is the one they already share, and it is the site's own default.
The other brands' pages keep their own languages: nothing here changes them.

**What the page is.** A daily push for your head, your routine and your drive,
told through everyday life. Someone who follows it should come away with a
little more energy, clarity or will than they arrived with: a reframe, one
small action for today, a reason to keep going, or a laugh that lightens the
load. Every carousel ends with the follow slide, which the renderer adds.

## Who reads it

Mostly 25 to 45, working on something of their own or thinking about it,
scrolling on the phone between things. They like a post when they think "this
is so me", they save it when it is useful, and they send it to a friend when it
is about them both.

## What works

- **Motivation that is useful, never cheesy.** No empty quotes ("believe in
  yourself", "success is…"), no hustle shouting, no guilt. Concrete and kind: a
  habit that takes two minutes, what to do on a Monday with no energy, what to
  do when you feel behind, why small wins count, how to stop comparing
  yourself. The reader must be able to do something with it today.
- **Mindset and focus:** discipline vs. motivation, starting before you feel
  ready, one thing at a time, rest that actually rests, saying no, getting back
  on track after a bad week, the people who push you up.
- **The everyday:** mornings, Mondays, coffee, alarms, commutes, work and
  email, the weekend, Sunday evening, friends and plans that never happen, the
  group chat, seasons, holidays, money, the gym in January.
- **The cover title is the hook.** Specific, a little provocative, a promise the
  slides keep. Patterns that work: a ranking ("8 signs you are further along
  than you think"), stages ("The 7 phases of a Sunday evening"), "things that
  are not laziness", "lies your brain tells you at 11pm", "what X actually
  looks like".
- **One moment per slide:** a heading of a few words, one or two short lines
  that paint a real scene, and a closing line that lands, warm or funny.
- **Mix the moods across the day.** Morning, a push to start. Midday, everyday
  life you laugh at or feel warm about. Evening, mindset and reflection.
- **Concrete beats clever.** "You have been watching dog videos for an hour"
  beats "free time slips away from us".

## The link to Sincronia, almost never

Sincronia helps companies find the public funding they qualify for. That is a
narrow subject and this page is not about it. Do not work it in. If, rarely, a
topic is genuinely about money a business leaves on the table, deadlines nobody
tracks, or paperwork that eats a week, the slides may stand on their own merit
as that topic: still no brand name, no link, no pitch. The follow slide is the
only place the brand appears.

## Never

- Never invent figures, studies or quotes. No statistics at all.
- Never name real people, businesses or brands.
- Nothing mean, political, religious or about bodies; tease situations, never
  people.
- No em dashes or en dashes (use a colon or a full stop), no hashtags or emojis
  on the slides themselves.
- Never promise money, results or funding. This page gives no advice about
  grants.
- Never repeat a title or angle already posted: `ig_publish.py --recent 60`
  prints the first line of the last posts' captions, which is their title. The
  `EVERYDAY` topics in `carousels.py` are taken too.

## The file

A JSON object, in the same shape as the topics in `carousels.py`:

```json
{
  "title": "7 things to do before you check your phone",
  "hook": "The first twenty minutes set the tone for the whole day.",
  "photos": "life",
  "points": [
    ["Stand up before you scroll", ["Feet on the floor, curtains open."], "Your head follows your body."]
  ],
  "hashtags": "#morningroutine #habits #focus #discipline #mindset"
}
```

- `title` at most 90 characters; `hook` (the caption's second line) at most 120.
- 5 to 8 `points`; each heading at most 52 characters, 1 or 2 lines of at most
  95, a closing line of at most 75.
- `photos`: `life` (mornings, notebooks, coffee, sunrise, an hourglass), `work`
  (desks, laptops, hands writing, receipts) or `city` (cafés, streets, tables).
  Every photo has no face.
- `countdown: true` numbers the points from the highest down, for a ranking.
- `hashtags`: optional, 5 to 8 that fit the topic, one string.

`carousel.py --topic <file>` refuses a topic that breaks these limits and says
what to fix. Look at the cover and two slides once rendered: if a line wraps
badly or a photo fights the text, shorten and render again.
