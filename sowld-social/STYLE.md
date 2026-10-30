# Writing a Sowld carousel

Each scheduled run writes one new carousel for Sowld's Instagram (@sowld.ai), in English, and publishes it. These are the rules for that topic.

The brief: everyday life that anybody recognises themselves in, and that leaves them **moved to do something**. A strong hook, interesting, never boring, **never a seller's post**. We are not advertising a product: we are writing things people like, save, send to someone, and come back for. If a topic walks naturally into what Sowld does, the last slide may say so; if it does not, there is no Sowld slide at all.

Five a day.

## The one rule above the others: it has to lift

Recognition alone is a dead end. "Ha, that is so me" gets a smile and a scroll. Someone follows an account because of how it makes them feel about **themselves**, not about the account.

So every carousel ends somewhere better than it started. The reader should close it thinking *I want to do that* or *I could do that too*, not just *that is funny*.

How that works in practice:

- **Name the thing honestly first.** The stuck feeling, the pile that never shrinks, the thing postponed for two years. Nobody is inspired by someone who skips the hard part.
- **Then turn.** Somewhere in the second half, the tone shifts from "this is us" to "and it could be different". Usually around point 4 or 5.
- **The last point is the one they remember.** It is never a joke. It is the small, true, doable thing: start with one drawer, decide once instead of thinking about it for a month, let the thing go before the move forces you to.
- **Small and concrete, never grand.** "Start with one drawer" works. "Change your life" does not: it is the voice of every account they have already muted.
- **Earned, not declared.** Never write "be grateful", "believe in yourself", "life is now". Show a scene so true that the reader reaches the thought themselves.

Humour still belongs: it is how the first half earns the second. The best posts are funny for four slides and land somewhere that stays.

## Who reads it

Everyone, mostly 20 to 45, in the UK, Ireland and the rest of the English speaking world, scrolling on the phone on the bus, in a queue, in bed. Some resell things, most do not: they just own too much stuff, buy second-hand sometimes, and keep meaning to clear out a cupboard.

They like a post when they think "this is exactly me". They **save** it when it is useful for something they keep putting off. They **send** it to a friend when it is about the two of them.

## What works

- **The cover title is the hook.** Specific, a little provocative, a promise the slides keep. Patterns: stages ("The 7 stages of finally clearing out your wardrobe"), a ranking ("The 8 worst feelings of a Monday morning"), "things you only learn when…", "things you say every time…", "signs that…", "what nobody tells you about…".
- **Our ground, where we are actually interesting:** the stuff we own and never use, the wardrobe, the drawer of cables, moving house, markets and second-hand finds, what you regret selling, what things are really worth, buying on impulse, clearing out, giving away, the garage, the box in the cellar.
- **And ordinary life around it**, because not every post can be about objects: Mondays, coffee, Sunday evenings, money and small lies about it, the group chat, flats and rent, the city, seasons.
- **One moment per slide:** a heading of a few words, one or two short lines that paint a real scene, and a closing line that lands, funny or true.
- **Mix the moods across the five:** some funny, some warm, one or two useful. Every one of them lifts at the end, whatever its mood.
- **Concrete beats clever.** "You bought it in 2017" beats "purchases age".
- **The closing line of each slide does the work.** It is the line in pink, the one that gets screenshotted. Write the slide, then spend most of the effort on that line.

## The link to Sowld, only when it fits

Sowld compares a second-hand listing against similar items on sale right now and estimates what it is really worth. So a topic about what something is worth, buying used, what is sitting in the cellar, or spotting a bad deal may end with the Sowld slide: set `"cta": true`.

Everything else: leave `cta` out, and the post is pure everyday life. Never mention Sowld, subscriptions or anything to buy on the slides themselves.

Roughly one in four or five gets the CTA. More than that and the profile reads as an ad, which is the one thing it must not read as.

## Never

- **Never invent figures, studies, quotes or prices.** No statistics at all, no "70% of people". If a number is not verifiable, it does not go in.
- Never promise earnings, never imply reselling makes money easily, never a "make money from…" angle. That is the seller's voice the brief rules out, and it would be a claim we cannot stand behind.
- **Never the empty motivational voice.** No "inizia oggi la tua nuova vita", no "il successo è una scelta", no quotes attributed to anyone. Inspiration here comes from a true scene and a doable next step, never from an exclamation mark.
- Never shame the reader. The pile, the clutter, the postponed thing: these are everybody's, and the post is on their side. Tease the situation, never the person in it.
- Never name real people, businesses or brands negatively. Marketplaces can be named plainly when a topic needs it; mentioning a real product you might own is fine.
- Nothing mean, political, religious or about bodies; tease situations, never people.
- No em dashes or en dashes (use a colon or a full stop), no hashtags or emojis on the slides, always "you".
- Gender-neutral throughout.
- **Never repeat a title or an angle already posted.** `ig_publish.py --token-env INSTAGRAM_TOKEN_SOWLD --recent 60` prints the first line of the last posts' captions, which is their title. The `EVERYDAY` topics in `carousels.py` count as taken too.

## The file

A JSON object, the same shape as the topics in `carousels.py`:

```json
{
  "title": "The 7 stages of finally clearing out your wardrobe",
  "hook": "Stage 4 is where everyone gets stuck.",
  "photos": "stuff",
  "points": [
    ["The burst of energy", ["You pull everything out onto the bed.", "You feel like a different person."], "That feeling lasts about fifteen minutes."]
  ],
  "hashtags": "#secondhand #declutter #thrifting #homeorganisation"
}
```

- `title` at most 90 characters; `hook` (the caption's second line) at most 120.
- 5 to 8 `points`; each heading at most 52 characters, 1 or 2 lines of at most 95, a closing line of at most 75.
- `photos`: `stuff` (wardrobes, shelves, boxes, a desk of cables), `market` (shops, stalls, vintage furniture), `life` (mornings, coffee, notebooks) or `money` (receipts, cards, a laptop). Every photo is face-free.
- `countdown: true` numbers the points from the highest down, for a ranking.
- `cta: true` only when the topic links naturally to what something is worth.
- `hashtags`: optional, 5 to 8 that fit the topic, one string.

`carousel.py --topic <file>` refuses a topic that breaks these limits and says what to fix. Look at the cover and two slides once rendered: if a line wraps badly or a photo fights the text, shorten and render again.
