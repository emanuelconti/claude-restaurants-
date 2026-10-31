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
- **The subject is life, not second hand.** Starting things, stopping things, habits, time, work, money, rest, self-trust, the gap between who you are and who you meant to be. These are what people follow an account for.
- **The stuff topics are one strand among several**, not the theme: the things we own and never use, a wardrobe, moving house, a market find, what you regret selling. Use them when they are the best way into a feeling, not because the brand sells something adjacent.
- **Mix the strands across a week.** If the last three posts were about objects, write about time, or starting, or a bad day. The account should read as a person with a life, not a shop with a blog.
- **One moment per slide:** a heading of a few words, one or two short lines that paint a real scene, and a closing line that lands, funny or true.
- **Mix the moods across the five:** some funny, some warm, one or two useful. Every one of them lifts at the end, whatever its mood.
- **Concrete beats clever.** "You bought it in 2017" beats "purchases age".
- **The closing line of each slide does the work.** It is the line in pink, the one that gets screenshotted. Write the slide, then spend most of the effort on that line.

## The Sowld slide is off right now

`CTA_ENABLED = False` in `carousels.py`. The site is not in the profile's link in bio while it is not ready, so a last slide pointing at a URL nobody can tap wastes the slide and makes the post read as an ad for nothing.

Write topics as if Sowld did not exist. Never mention it, never mention a product, never write a closing line that is secretly a pitch. The job right now is one thing only: **make the post good enough that someone follows the account.**

You can still set `"cta": true` on a topic that genuinely walks into what Sowld does. It will simply be ignored until the flag goes back on, and then those posts already have their last slide written.

## Photos: new ones every time

The owner (31 October): the carousels kept showing the same photos, because each set holds only 8 to 12 and a carousel uses almost all of them. **Every carousel picks its own photos**, chosen for that topic and for each slide, and different from the ones in the last days' posts.

1. Search Unsplash for each slide's scene (`https://unsplash.com/napi/search/photos?query=<words>&per_page=30`, with a browser User-Agent). Take free photos only: the id is the part after `images.unsplash.com/photo-` in `urls.raw`; skip anything on `plus.unsplash.com`.
2. No faces, no logos or brands, nothing that fights the text. Prefer hands, objects, places and light.
3. Put them in the topic as `"photo_ids"`, cover first, then one per point, in order. Never two the same in one carousel, and avoid any you used in the day's other carousels.
4. Render, then **look at the cover and every slide**. If a photo shows a face, repeats an earlier post or does not fit, swap it and render again.

If the search host is refused, leave `photo_ids` out: the slot still goes out with the set's photos, and say so in the run's report. The renderer stops when a photo cannot be fetched, so a carousel never goes out in plain colours.

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
- 5 to 8 `points`; each heading at most 52 characters, 1 to 6 lines of at most 95, a closing line of at most 75. Four to six short lines read better than two long ones: one thought per line, like a list inside the point.
- `photos`: `human` (a desk by a window, a path, a room, someone walking away: for topics about a life), `life` (mornings, coffee, notebooks), `stuff` (wardrobes, shelves, boxes), `market` (shops, stalls, vintage furniture) or `money` (receipts, cards, a laptop). Every photo is face-free. Most topics want `human` or `life`.
- `photo_ids`: the Unsplash ids picked for this topic, cover first, then one per point (see "Photos: new ones every time"). Expected on every topic.
- `countdown: true` numbers the points from the highest down, for a ranking.
- `cta: true` is currently ignored (see above). Leave it out.
- `hashtags`: optional, 5 to 8 that fit the topic, one string.

`carousel.py --topic <file>` refuses a topic that breaks these limits and says what to fix. Look at the cover and two slides once rendered: if a line wraps badly or a photo fights the text, shorten and render again.
