# Writing a Good Message Studio carousel

## Strategy: organic that works like paid targeting (the owner, 1 November 2026)

**This section overrides anything below that says otherwise.** We have no ad budget, so every post has to do what a Meta campaign would: reach the right people, stop the scroll, and send them to goodmessagestudio.com. The levers we have are the audience-specific content, the search keywords in the caption, the hashtags, the timing and the shares and saves that push a post to non-followers. Use all of them, every time.

**Who we target:** women in Singapore, 18 to 38. Students, young professionals in the CBD and the heartlands, young mums. English-speaking, on Instagram every day, on Facebook more as they get older. They buy for themselves (a cosy hoodie for the aircon) and as gifts (a birthday, a best friend, Christmas, a colleague's farewell).

**What makes the algorithm show it to new people:** sends (DMs) and saves first, then time spent swiping, then likes. So every carousel is built to be sent ("this is so you") or saved (a list, a guide, a gift idea). The cover must stop the thumb: a big specific promise, a product photo with the message clearly readable.

**The six daily slots** (Singapore time). The routine runs at 08:17, 10:17, 12:17, 15:17, 18:17 and 21:17; match the slot:
1. 08:17, commute: a message to start the day (5 or 6 affirmations, each tied to a product message). Scenes: the MRT, kopi, the walk to the office.
2. 10:17, friendship: "Send this to the friend who…", "Signs she is your soul sister", the bestie who always checks in. Built to be sent.
3. 12:17, lunch: everyday Singapore life with a kind twist: the freezing office aircon (the reason to own a hoodie in a hot country), the 4pm rain, the hawker queue, the group chat. Funny first, warm at the end.
4. 15:17, product spotlight: one product, presented like a brand campaign. Cover: the product with its message readable. Then: what the message means and who it is for; the details exactly as the shop lists them (fabric, fit, colours, sizes: copy them from products.json, never add any); two or three ways to wear it in Singapore (office aircon, cinema, brunch, travel); who it makes a good gift for; the last point names the product and its real price in SGD from products.json. Alternate with "how to style it" carousels ("3 ways to style an oversized hoodie in Singapore"). Built to be saved.
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



**Covers rotate (the owner, 1 November 2026): no carousel may open with the same photo as any of the previous 12.** The renderer picks the cover itself from a fixed rotation by post number, so do not try to choose it; choose the photos of the points. Keep the points' photos different from the day's other posts too. For Good Message Studio the cover rotates through 14 chosen product photos (`GMS_COVERS` in carousels.py); `photo_urls` are for the points (if you also list a cover first, it is dropped). **Never use** the store's supplier advertising images (with text such as "NEW", "380G fleece" or "CHINA"), the balaclava photo ("Police or Bandit?"), or the hoodies with a "19" print: they would make the brand attackable. Never use `gm-city.jpg` or `gm-studio.jpg` either (the model looks AI-generated; the owner, 1 November 2026): prefer real product shots, backs with the printed message, flat lays and hangers.


## Premium, always (the owner, 2 November 2026)

Every post must look like a premium fashion label, never like a supplier listing.
- **Openers:** a carousel opens either on a hero shot (the back with the printed message, or a real lifestyle photo) or on a typographic cover (serif title on a soft colour); the renderer alternates them in a fixed sequence (`GMS_COVERS`), so no photo repeats within 12 posts. Never the plain front of a hoodie, a flat lay of a blank garment or a supplier image as an opener.
- **Reels** always open on the typographic hook (serif, appearing line by line on a colour that changes every day), then the products. Plain blank garments may appear only inside a product card, never as the first frame.
- **Type:** headlines and messages in DM Serif Display, sentence case (never all caps); the small spaced label "G O O D  M E S S A G E  S T U D I O"; body in Inter. Keep lines short and the hook under 60 characters.
- Text never sits on top of the printed message of a garment.

## Layouts that change, like a page that grows (the owner, 1 November 2026)

No more text boxes on top of photos. Slides and reel scenes take turns between three looks, and a good carousel uses all three:
- **product**: the product photo framed like a shop card on cream, the message underneath. Use it when the point names or matches a product.
- **text**: words alone, big, on a soft pastel from the hoodies' own colours. Use it for the line people will screenshot.
- **classic** (carousels) / **photo** (reels): the photo with clean text, no plate.
Carousels: set `"layouts"` (one per point: `product`, `classic` or `text`); by default they take turns product, classic, text. Reels: set `"scenes"` (one per line: `product`, `text` or `photo`); by default product, text, photo. Never two text-only slides in a row, and never a product card whose photo does not match its message.

## Reels: one a day (the owner, 1 November 2026)

Reels reach people who do not follow us far more than carousels do, so the 12:17 Singapore slot publishes a **reel** instead of a carousel, every day. `reel.py` renders it from the shop's real product photos (1080x1920, 30 fps, a slow push on each photo, quick crossfades, an original soft beat with no third-party music, the shop and the handle on the last card) and `reel_publish.py` publishes it with the same daily cap, minimum gap and stop rules as the carousels. It counts as one of the six posts.

What makes a reel travel, and what every reel must do:
- **The first second is the hook.** The opening text must make a woman in Singapore stop and think "this is for me" or "this is for her": "Send this to the friend who needs it today", "POV: your office aircon is set to 16 degrees", "Gifts for her that are not another candle", "5 reminders for the girl who is tired".
- **12 to 15 seconds, 3 to 5 messages.** One short line per scene (at most 60 characters), each on the photo of the product whose print says the same thing or fits it. The printed message on the hoodie must stay visible: the renderer puts the text in the top third for that reason.
- **Built to be sent and watched twice:** a payoff on the last message, and a caption that ends with "Send this to…".
- **Real and honest:** only the shop's own product photos (never AI people, never other brands, never the images listed below as never to use), only real products and prices.
- **The caption is search,** exactly as for carousels: `caption` with Singapore and gift keywords, then the hashtags.

The reel topic file (see `reel.py`): `title`, `hook`, `lines` (3 to 5), `photo_urls` (one for the hook, then one per line, matching the messages), `caption`, `hashtags`. Render with `python3 reel.py --date <date> --topic <file>`, look at frames from every scene (`ffmpeg -ss <seconds> -i out/<date>/reel/reel.mp4 -frames:v 1 frame.jpg`), then `python3 reel_publish.py --token-env INSTAGRAM_TOKEN_SOWLD --date <date>`.

## Professional and unattackable (the owner, 1 November 2026)

Every post must look and read like the work of a serious brand, and nobody must be able to fault it: not a customer, not a competitor, not Meta's review, not an advertising regulator. Before publishing, check each point. If one fails, fix it; if it cannot be fixed, do not publish.

- **True, and provable.** Only facts the account can stand behind. No invented figures, studies, quotes, reviews, testimonials, awards, "best-selling", "No. 1", "limited stock" or deadlines. No "free shipping", discount or promotion unless it is live on the site right now.
- **Products exactly as sold** (where products appear): the name, price, currency, colours, sizes, fabric and fit copied from the shop's own data; never "organic", "sustainable", "handmade", "premium" or any quality claim the product page does not make.
- **No health, medical or financial promises.** Kind words about wellbeing are fine; claims that something heals, treats, cures, guarantees money, funding or results are not.
- **Respect.** Nothing about bodies, weight, age, race, religion, politics or gender roles; no stereotypes of any group or country; inclusive and gender-neutral wherever the audience allows it. Tease situations, never people.
- **Rights.** Only the shop's own product photos and free-licence stock photos the repository already uses or the API returns. No song lyrics, film quotes, celebrities, other brands' logos or trademarks, or anyone's words presented as theirs.
- **No manipulation.** No fake urgency, no engagement bait ("tag 3 friends", "comment YES"), no hashtag stuffing, no misleading cover that the slides do not deliver.
- **Polished.** Perfect spelling and grammar in the post's language; one idea per slide; nothing cut off or wrapped badly; photos sharp, well cropped and on topic; the brand name and handle written exactly; consistent tone from the cover to the last slide.
- **Calm with the platform.** Respect the publishing limits in the scripts, and stop at the first sign of pushback from Meta.

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
- Never post more than the script allows (10 a day, 60 minutes apart) and never spam hashtags.

## The file

```json
{
  "title": "5 messages worth repeating to yourself this week",
  "hook": "Number 5 is the one most of us forget.",
  "photos": "human",
  "photo_urls": ["https://cdn.shopify.com/s/files/.../gm-back.jpg", "..."],
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

## Every post is the brand (the owner, 2 November 2026)

Ads, yes, but a real brand first. Every post must carry one clear concept: a positive message, or a small everyday problem solved (what to say to a friend who is struggling, a gift that means something, a calmer evening, a kinder Monday). The product appears as the natural answer, never as a list of hoodies. Some posts do not sell at all: a thought, a ritual, a line worth saving. Before publishing ask: would a woman in Singapore save or send this even if she never buys? If not, rewrite it. More style: serif headlines, generous space, one idea per slide, calm palette.

## Promote only the message hoodies (the owner, 2 November 2026)

Never feature neutral products (plain caps, plain tees, blank basics) in posts, cards or reels: they say nothing and waste the ad. Show only the hoodies with a message. For mood, life and city scenes use other real photos (no faces, no AI look), not neutral products.
