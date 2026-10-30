# Writing the day's carousel

Each scheduled run writes one new carousel for SocialPerks' Instagram, in Spanish, and publishes it. These are the rules for that topic. The owner's brief (30 October): ultra interesting and likeable, a strong hook, things people see themselves in, never boring, never a sales pitch. Three a day: morning, lunch, evening.

## Who reads it

People who run a small local business in Spain: a bar, a café, a restaurant, a barbershop, a hair or nail salon, a gym, a physio, a tattoo studio. Tired, proud, busy, a bit fed up with apps and rent. They read on the phone between two customers. They save a post when it is useful and send it to a friend when it is true.

## What works

- **The cover title is the hook.** Specific, a little provocative, a promise the slides keep. Patterns that work: a ranking ("Ranking de los 8 peores momentos de…"), a contrast ("El negocio que se llena y el que no: 7 diferencias"), a confession ("Lo que nadie te cuenta antes de…"), a mirror ("Las 7 sensaciones que solo entiende quien…"), a number with a stake ("6 errores que te cuestan clientes cada martes"), a myth ("Por qué el 30 % de descuento te sale caro").
- **One point per slide**: a heading of a few words, one or two short lines that show a real moment (a Tuesday at 4pm, the supplier's new prices, Sunday night thinking about Monday), and a closing line that lands. People should think "this is me".
- **Mix the moods** across the day: one practical (customers, quiet hours, platforms, prices, reviews, staff, word of mouth), one about the life of running a place (routine, tiredness, pride, small wins, the first customer of the day), one topical or emotional (rent, inflation, AI, tourism, the neighbourhood, motivation for a bad week).
- **Concrete beats clever.** "Pide el de pistacho y siéntate fuera" beats "la experiencia importa".

## Never

- Never invent figures, studies or quotes. The only number with a source in the bank is Nielsen 2015 (83 % trust friends' recommendations); platform fees of 15 to 35 % are the product's own figure. Otherwise no statistics.
- Never name real people, businesses, competitors or brands, and never imply SocialPerks has partners or results it does not have.
- Never sell on the slides: SocialPerks only appears on the last slide, which the renderer adds.
- No em dashes or en dashes (use a colon or a full stop), never the word "perk", no hashtags or emojis on the slides, no "tú/usted" mix (always "tú").
- Gender-neutral where it can be ("quien tiene un negocio", "tu equipo", "tus clientes").
- Never repeat a title or angle already posted: `ig_publish.py --recent 60` prints the first line of the last posts' captions, which is their title.

## The file

A JSON object, in the same shape as the topics in `carousels.py`:

```json
{
  "title": "Ranking de los 8 peores momentos de tener un negocio",
  "hook": "Si tienes un negocio, los has vivido todos.",
  "photos": "life",
  "countdown": true,
  "points": [
    ["Mirar la agenda del martes", ["Huecos a las 16:00, a las 17:00, a las 18:00.", "Y el alquiler no tiene huecos."], "La hora vacía también se paga."]
  ]
}
```

- `title` at most 90 characters; `hook` (the caption's second line) at most 120.
- 5 to 8 `points`; each heading at most 52 characters, 1 or 2 lines of at most 95, a closing line of at most 75.
- `photos`: `life` (mornings, notebooks, coffee, sunrise), `money` (receipts, cards, laptops), `city` (Barcelona, cafés, terraces, toasts) or `venue` (the places' own photos: haircuts, nails, plates, cocktails). Pick the set that fits the mood. Every photo has no face.
- `countdown: true` numbers the points from the highest down, for a ranking.

`carousel.py --topic <file>` refuses a topic that breaks these limits and says what to fix. Look at the cover and two slides once rendered: if a line wraps badly or a photo fights the text, shorten and render again.
