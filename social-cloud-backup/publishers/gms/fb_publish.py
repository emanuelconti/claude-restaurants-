#!/usr/bin/env python3
"""Publish a rendered carousel on Good Message Studio's Facebook Page, as one post with all its slides.

    python3 fb_publish.py --check-token
    python3 fb_publish.py --date 2026-11-02 --slot 1            # the same slides and caption as the Instagram post

The owner (1 November 2026): no ad budget, so the shop's carousels go out
organically on Facebook too. It reads, from the environment:
- FB_PAGE_TOKEN_GMS: a Page access token for the "Good Message Studio" Page,
  with pages_manage_posts and pages_read_engagement (a long-lived one), or the
  owner's user token with those permissions plus pages_show_list: the script
  then asks Facebook for the Page token itself;
- FB_PAGE_ID_GMS: the Page's id.

Same safety rules as ig_publish.py: at most 8 posts a day (Asia/Singapore),
at least 60 minutes between posts, never the same caption twice, and it stops
for good on any answer from Meta that says blocked, limit, spam, restricted or
temporarily. The token never goes in a URL or in the output.
"""

from __future__ import annotations

import argparse
import io
import uuid
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import carousels as C  # noqa: E402
import ig_publish as IG  # noqa: E402  (public asset validation only)

API = "https://graph.facebook.com/v21.0"
MAX_PER_DAY = 8  # Owner's standing Singapore cap, including posts by any publisher.
MIN_GAP = 60  # minutes
STOP_WORDS = ("blocked", "limit", "spam", "restricted", "temporarily")
SINGAPORE = ZoneInfo("Asia/Singapore")


class Stop(RuntimeError):
    pass


def call(method: str, path: str, token: str, params: dict | None = None) -> dict:
    params = dict(params or {})
    url = f"{API}/{path}"
    data = None
    headers = {"Authorization": f"Bearer {token}"}
    if method == "GET":
        if params:
            url += "?" + urllib.parse.urlencode(params)
    elif isinstance(params.get("source"), bytes):
        picture = params.pop("source")
        boundary = "gms-" + uuid.uuid4().hex
        fields = [f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode() for key, value in params.items()]
        fields += [f'--{boundary}\r\nContent-Disposition: form-data; name="source"; filename="product-card.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode(), picture, f'\r\n--{boundary}--\r\n'.encode()]
        data = b"".join(fields)
        headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as error:
        try:
            message = json.loads(error.read().decode()).get("error", {}).get("message", "")
        except Exception:
            message = str(error)
        if any(w in message.lower() for w in STOP_WORDS):
            raise Stop(f"Meta says: {message}. Stopped, nothing retried.") from None
        raise RuntimeError(f"{method} {path}: {message}") from None


SHOP = "https://goodmessagestudio.com"


def message_hoodies(products: list) -> list:
    """Only the four message ranges verified in the owner's current brand brief.

    A generic 'Oversized' title does not prove a printed message. New ranges
    require editorial verification before they can enter automatic cards.
    """
    messages = ("enjoy the little things", "peace starts with us", "be kind", "do what makes you happy")
    return [product for product in products
            if product.get("images") and "hoodie" in product.get("title", "").lower()
            and any(message in product["title"].lower() for message in messages)]


def product_card(image_bytes: bytes, title: str, description: str) -> bytes:
    """Bake the product label into a native photo; no external link-preview image.

    Preserve the real product photo without cropping its print. The shop link
    stays in the post/photo caption; this is not an ad-style clickable link card.
    """
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    source = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if min(source.size) < 320:
        raise RuntimeError("Product source is a tiny placeholder; nothing published")
    card = Image.new("RGB", (1080, 1350), "#f9fafb")
    source = ImageOps.contain(source, (1080, 1080), Image.Resampling.LANCZOS)
    card.paste(source, ((1080-source.width)//2, (1080-source.height)//2))
    draw = ImageDraw.Draw(card); draw.line((0,1080,1080,1080), fill="#d5d7dc", width=2)
    def font(size):
        for path in (os.environ.get("GMS_CARD_FONT", ""), "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"):
            if path and os.path.isfile(path):return ImageFont.truetype(path,size)
        raise RuntimeError("Product-card font missing; nothing published")
    for size in range(44,27,-1):
        face=font(size);lines=[];line=""
        for word in title.split():
            candidate=(line+" "+word).strip()
            if draw.textlength(candidate,font=face)>984 and line:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
        if len(lines)<=2:break
    if len(lines)>2:raise RuntimeError("Product label does not fit; nothing published")
    for i,line in enumerate(lines):draw.text((48,1110+i*55),line,font=face,fill="#15161b")
    draw.text((48,1240),description,font=font(30),fill="#5d626b")
    draw.text((48,1287),"goodmessagestudio.com",font=font(28),fill="#244638")
    out=io.BytesIO();card.save(out,"JPEG",quality=93,optimize=True);return out.getvalue()


def page_token(page: str, token: str) -> str:
    """Return a Page token: FB_PAGE_TOKEN_GMS may hold the owner's user token
    instead (1 November 2026), and a user token with pages_show_list can ask for
    the Page's own token. A Page token asking for itself gets no access_token
    back, so it is used as it is."""
    try:
        return call("GET", page, token, {"fields": "access_token"}).get("access_token") or token
    except Stop:
        raise
    except RuntimeError:
        return token


def recent(page: str, token: str) -> list:
    return call("GET", f"{page}/posts", token, {"fields": "message,created_time,permalink_url", "limit": 25}).get("data", [])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--slot", type=int, default=1)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--check-token", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("FB_PAGE_TOKEN_GMS", "").strip()
    page = os.environ.get("FB_PAGE_ID_GMS", "").strip()
    if not token or not page:
        sys.exit("FB_PAGE_TOKEN_GMS or FB_PAGE_ID_GMS is not set: nothing published")
    try:
        token = page_token(page, token)
        if args.check_token:
            name = call("GET", page, token, {"fields": "name"}).get("name", "?")
            print(f"token ok: Page {name!r}, {len(recent(page, token))} recent posts read, publishing not tried")
            return
        if not args.date:
            ap.error("--date is needed to publish")
        folder = os.path.join(args.out, args.date, f"carousel-{args.slot}")
        with open(os.path.join(folder, "carousel.json"), encoding="utf-8") as source:
            meta = json.load(source)
        first = meta["caption"].split("\n", 1)[0].strip()
        posts = recent(page, token)
        done = next((p for p in posts if (p.get("message") or "").strip().startswith(first)), None)
        if done:
            print(f"already published: {done.get('permalink_url')}")
            return
        now = dt.datetime.now(dt.timezone.utc)
        stamps = [dt.datetime.strptime(p["created_time"], "%Y-%m-%dT%H:%M:%S%z") for p in posts if p.get("created_time")]
        today = sum(1 for s in stamps if s.astimezone(SINGAPORE).date() == now.astimezone(SINGAPORE).date())
        if today >= MAX_PER_DAY:
            print(f"daily cap: the Page already has {today} posts today, nothing published")
            return
        if stamps and (now - max(stamps)).total_seconds() < MIN_GAP * 60:
            sys.exit(f"too soon: the last post went out {int((now - max(stamps)).total_seconds() // 60)} min ago (minimum {MIN_GAP}), nothing published")
        # Six editorial carousel slots and two product showcases. Both use
        # native Facebook photos, never fragile product link-preview cards.
        product_showcase = args.slot in (4, 8)
        cards = []
        if product_showcase:
            products = json.load(urllib.request.urlopen(SHOP + "/products.json?limit=250", timeout=60))["products"]
            products = message_hoodies(products)
            if len(products) < 3:
                sys.exit("could not read enough verified products: nothing published")
            picks = [products[((args.slot - 1) * 5 + i) % len(products)] for i in range(min(5, len(products)))]
            for product in picks:
                value = (product.get("variants") or [{}])[0].get("price")
                label = f"Shop now · S${float(value):.0f}" if value else "Shop now"
                cards.append(dict(name=product["title"], description=label,
                                  link=SHOP + "/products/" + product["handle"],
                                  picture=product["images"][0]["src"].split("?")[0]))
        else:
            from PIL import Image
            base = os.environ.get("GMS_PUBLIC_ASSET_BASE", "").rstrip("/")
            if not base.startswith("https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/"):
                sys.exit("immutable reviewed asset base missing: nothing published")
            names = meta.get("slides", [])
            if not 2 <= len(names) <= 10:
                sys.exit("Facebook carousel needs 2 to 10 reviewed slides: nothing published")
            for name in names:
                if os.path.basename(name) != name:
                    sys.exit("invalid reviewed slide path: nothing published")
                with Image.open(os.path.join(folder, name)) as image:
                    image.verify()
                url = base + "/" + name
                IG.check_public(url)
                cards.append(dict(name=first, description="", link=SHOP, picture=url))
        # Native photo IDs are durable. Link-preview cards can lose their images
        # even after a successful scrape (owner evidence, 3 November).
        # Fail closed before feed publication unless every selected photo exists.
        photo_ids = []
        for card in cards:
            params = {"published": "false", "caption": card["name"] + "\n" + card["description"] + "\n" + card["link"]}
            if product_showcase:
                with urllib.request.urlopen(card["picture"], timeout=60) as response:
                    raw = response.read()
                params["source"] = product_card(raw, card["name"], card["description"])
            else:
                params["url"] = card["picture"]
            photo = call("POST", f"{page}/photos", token, params)
            if not photo.get("id"):
                raise RuntimeError("Facebook did not acknowledge the native photo; no feed post published")
            stored = call("GET", photo["id"], token, {"fields": "images"})
            if not any(image.get("width", 0) >= 320 and image.get("height", 0) >= 320 for image in stored.get("images", [])):
                raise RuntimeError("Facebook native photo is missing or a tiny placeholder; no feed post published")
            photo_ids.append(str(photo["id"]))
        message = meta["caption"].replace(C.CAPTION_SHARE, C.CAPTION_SHARE_LINK).replace(C.CAPTION_SAVE, C.CAPTION_SAVE + "\n\n" + C.CAPTION_SHARE_LINK)
        # Keep a clickable shop route in the post itself even if a Facebook placement hides card labels.
        message = message.replace("(link in bio)", "")
        if "https://goodmessagestudio.com" not in message:
            message += "\n\nShop now: https://goodmessagestudio.com"
        if product_showcase:
            message += "\n\n" + "\n\n".join(card["name"] + "\n" + card["description"] + "\n" + card["link"] for card in cards)
        params = {"message": message,
                  "attached_media": json.dumps([{"media_fbid": photo_id} for photo_id in photo_ids])}
        # A feed failure is ambiguous. Never blindly retry a post creation.
        post = call("POST", f"{page}/feed", token, params)
        link = call("GET", post["id"], token, {"fields": "permalink_url"}).get("permalink_url")
    except Stop as stop:
        sys.exit(str(stop))
    except RuntimeError as error:
        sys.exit(f"Facebook: {error}")
    with open(os.path.join(folder, "published-facebook.json"), "w", encoding="utf-8") as fh:
        json.dump({"post_id": post["id"], "permalink": link, "format": "native_products" if product_showcase else "native_editorial_carousel", "photo_ids": photo_ids}, fh, indent=1)
    print(f"published: {link}")


if __name__ == "__main__":
    main()
