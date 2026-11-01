# Writing a Good Message Studio carousel

## Strategy: organic that works like paid targeting (the owner, 1 November 2026)

**This section overrides anything below that says otherwise.** We have no ad budget, so every post has to do what a Meta campaign would: reach the right people, stop the scroll, and send them to goodmessagestudio.com. The levers we have are the audience-specific content, the search keywords in the caption, the hashtags, the timing and the shares and saves that push a post to non-followers. Use all of them, every time.

**Who we target:** women in Singapore, 18 to 38. Students, young professionals in the CBD and the heartlands, young mums. English-speaking, on Instagram every day, on Facebook more as they get older. They buy for themselves (a cosy hoodie for the aircon) and as gifts (a birthday, a best friend, Christmas, a colleague's farewell).

**What makes the algorithm show it to new people:** sends (DMs) and saves first, then time spent swiping, then likes. So every carousel is built to be sent ("this is so you") or saved (a list, a guide, a gift idea). The cover must stop the thumb: a big specific promise, a product photo with the message clearly readable.

**The six daily slots** (Singapore time). The routine runs at 08:17, 10:17, 12:17, 15:17, 18:17 and 21:17; match the slot:
1. 08:17, commute: a message to start the day (5 or 6 affirmations, each tied to a product message). Scenes: the MRT, kopi, the walk to the office.
2. 10:17, friendship: "Send this to the friend who…", "Signs she is your soul sister", the bestie who always checks in. Built to be sent.
3. 12:17, lunch: everyday Singapore life with a kind twist: the freezing office aircon (the reason to own a hoodie in a hot country), the 4pm rain, the hawker queue, the group chat. Funny first, warm at the end.
4. 15:17, style: how to wear it. "3 ways to style an oversized hoodie in Singapore", hoodie for cinema and office aircon, tee with jeans for brunch. Built to be saved.
5. 18:17, gifts: gift guides ("Gifts for her under SGD 60", "What to give the friend who has everything", birthday, farewell, Secret Santa). Use only real products and real prices from products.json. Built to be saved and sent.
6. 21:17, night: self-care and kindness to yourself, rest, letting go of the day, gentle mental-health awareness (never clinical, never a claim).

**Seasonal calendar** (lead with it when it is close): 11.11 and Black Friday only if the shop really runs a promotion (never invent one); World Kindness Day, 13 November (our day: post about kindness that week); Christmas and year-end gifting from mid-November to 24 December; New Year intentions in January; Chinese New Year and Galentine's/Valentine's in January and February; Mother's Day in May; World Mental Health Day, 10 October.

**Caption = search.** Instagram and Facebook search read the caption, so set `"caption"` on every topic: two or three natural sentences with what someone in Singapore would type, for example "oversized hoodie Singapore", "gift for her Singapore", "birthday gift for best friend", "cosy hoodie for office aircon", "slogan tee with a kind message". Mention the product type, Singapore, and the use or the occasion. Then end with one soft line that drives sends ("Send this to the friend who needs it today."). Never "tag 3 friends", never "comment YES": that is engagement bait and gets posts pushed down.

**Hashtags: 8 to 12, mixed by size, never the same block twice in a row.** Always `#goodmessagestudio #singapore`. Then pick:
- Singapore fashion and shopping (2 or 3): #sgfashion #sgootd #sgstyle #singaporefashion #sgshopping #shopsg #sgonlineshop #sgdeals (only with a real deal)
- audience and gifts (2 or 3): #sggifts #giftideasforher #giftsforher #birthdaygiftideas #bestfriendgift #christmasgiftideas (in season) #sggirls
- the message (2 or 3): #bekind #kindnessmatters #selflove #positivevibes #enjoythelittlethings #mentalhealthawareness #worldkindnessday (13 November)
- the product (1 or 2): #oversizedhoodie #hoodieseason #graphichoodie #slogantee #cosyvibes
No banned or spammy tags (#like4like, #follow4follow and the like).

**Cover and photos:** the cover is a product photo where the printed message reads at a glance (gm-city, gm-back, the Be Kind back print, Do What Makes You Happy), or a model wearing it. The slides follow the products named in the points. Different cover from the day's other posts.


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
- Never post more than the script allows (6 a day, 60 minutes apart) and never spam hashtags.

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
