# Writing a Good Message Studio carousel

Since 1 November 2026 this account (formerly @sowld.ai) is **Good Message Studio**, the owner's shop at goodmessagestudio.com: hoodies, tees, caps and totes that carry one kind line ("Be Kind", "Peace Starts With Us", "Do What Makes You Happy", "Enjoy The Little Things"). The shop sells in Singapore dollars to people in **Singapore**. There is no ad budget: these posts are the ads, so they must work like good ads while reading like posts people want to save and send.

Each scheduled run writes one carousel, in **English**, and publishes it.

## What every carousel does

1. **Opens with a hook about life, not about clothes.** A feeling, a moment, a message people need: being kind when tired, small joys, rest, peace with yourself and others, doing what makes you happy, mental health handled gently.
2. **Shows the products as the pictures.** The photos are the shop's own product photos (the message printed on the hoodie or tee is part of the picture). Each point should match the message in its photo when it can.
3. **Lands on the shop.** The renderer adds "Wear the message." with goodmessagestudio.com, then the follow slide. Set `"cta": true` on every topic.

The tone: warm, kind, a little playful, never preachy, never pushy. Sell the message first; the hoodie is how you carry it. No "BUY NOW", no fake urgency, no discounts or prices that are not on the shop.

## Who reads it

People in Singapore, mostly 18 to 40, scrolling on the MRT, at lunch, in bed. Use local, everyday scenes when they fit (the MRT, kopi, hawker centres, HDB corridors, the heat, the rain at 4pm, office life in the CBD, weekends at East Coast Park), lightly and never as a caricature. Gifts work well: birthdays, friends, partners, "send this to someone who needs it".

## Mix across the day

- Morning: a gentle push for the day (a message to start with).
- Midday: everyday life people laugh at or feel warm about, with a message in it.
- Evening: reflection, rest, kindness to yourself; or a gift idea ("5 people who need this message").

Formats that work: "5 messages worth repeating this week", "Signs you need a reminder to be kind to yourself", "Things that are small but make the whole day", "Send this to the friend who…", "The 6 stages of a Monday in the CBD (and the message for each)".

## Photos

- Use the shop's product photos: read `https://goodmessagestudio.com/products.json?limit=250` (public) and pick image URLs (`images[].src`, without the query string) of the message products that fit each slide. Put them in the topic as `"photo_urls"`, cover first, then one per point. Prefer the biggest images (1600 px), and the products with a printed message.
- Vary them: not the same cover as the previous posts, and not the same photo twice in one carousel.
- Product photos may show a model wearing the piece: that is fine. Never add other people's photos with faces.
- Render, then look at the cover and every slide. If a photo is blurry, cropped badly or does not fit, swap it and render again.

## Never

- Never invent figures, studies, quotes, reviews, prices, shipping times or promotions.
- Never make medical or mental health claims; be kind, not clinical.
- Nothing mean, political, religious or about bodies.
- No em dashes or en dashes (use a colon or a full stop), no hashtags or emojis on the slides, always "you".
- Never repeat a title or angle already posted: `ig_publish.py --token-env INSTAGRAM_TOKEN_SOWLD --recent 60` prints the first line of the last posts' captions.
- Never post more than the script allows (3 a day, 60 minutes apart) and never spam hashtags.

## The file

```json
{
  "title": "5 messages worth repeating to yourself this week",
  "hook": "Number 5 is the one most of us forget.",
  "photos": "human",
  "photo_urls": ["https://cdn.shopify.com/s/files/.../gm-city.jpg", "..."],
  "points": [
    ["Enjoy the little things", ["The first sip of kopi.", "A message from someone who thought of you."], "Big days are made of small ones."]
  ],
  "cta": true,
  "hashtags": "#goodmessagestudio #singapore #sgfashion #bekind #positivevibes #sgstyle"
}
```

- `title` at most 90 characters; `hook` at most 120.
- 5 to 8 `points`; each heading at most 52 characters, 1 to 6 lines of at most 95, a closing line of at most 75.
- `photo_urls`: the shop's product image URLs (https://cdn.shopify.com/... or https://goodmessagestudio.com/cdn/...), cover first.
- `photos`: a fallback set for any slide without a product photo (`human` or `life`).
- `cta`: `true` on every topic.
- `hashtags`: 6 to 10, always `#goodmessagestudio` and `#singapore`, then ones that fit the topic and Singapore (#sgfashion, #sgstyle, #sggifts, #sgootd, #bekind, #kindness, #positivevibes, #selfcare, #mentalhealthawareness, #giftideas).

`carousel.py --topic <file>` refuses a topic that breaks these limits and says what to fix.
