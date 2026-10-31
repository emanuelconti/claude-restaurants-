#!/usr/bin/env python3
"""The two videos of the Merchant Lead kit, in Spanish, Italian and English.

    python3 lead_kit.py --out /tmp/kit            # all six
    python3 lead_kit.py --lang es --only venue    # one

- venue: what a Lead shows a venue owner, on their own phone. What SocialPerks
  does for the venue, what it costs, the guarantee. About 37 seconds.
- lead: for the Lead. What SocialPerks is, their three steps, what they earn,
  how to start. About 36 seconds.

The owner, 16 October: the kits must be understood by anybody, convince
people to join, be exceptional to look at, few words, human, nothing
repeated. Every number here is the standard Lead agreement's (socialperks
src/lib/sp/lead-agreement.ts, version 2026-10-08): 100% of each venue's first
paid month (EUR 49), then 20% (EUR 9.80) of every month it keeps paying, paid
monthly in euros; no territory, no minimums.

Drawn with daily.py's tools (the same look as the daily videos) over the
product's own screens, captured in each language (assets/lead-kit/<lang>).
"""

from __future__ import annotations

import argparse
import os
import subprocess

from PIL import Image, ImageDraw

import daily as D
from daily import W, H, FPS, LEFT, TEXT_W, WHITE, INK, SIGNAL, PINK, YELLOW, PALETTES

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets", "lead-kit")
DARK, BLUE, PAPER, ROSE, NIGHT = PALETTES

COPY = {
    "es": {
        "venue": [
            ("hook", "Si tienes un local:", "¿Cuántas horas de tu semana se quedan *vacías*?"),
            ("week", "SocialPerks *ve* las horas que no se van a llenar."),
            ("gifts", "Pones un *pequeño regalo* en esas horas.", ["Una mascarilla", "Una copa de cava", "Una toalla caliente"]),
            ("stories", "Tus clientes lo *comparten*, cada uno con su propio enlace."),
            ("friend", "Sus amigos *vienen* justo en esas horas."),
            ("counter", "En el mostrador: *un escaneo*. Sin escribir nada."),
            ("price", "*49 €* al mes.", "¿Menos de 3 clientes nuevos en un mes? *Te lo devolvemos.*"),
            ("grid", "Para *cualquier* local.", ["Peluquerías", "Barberías", "Uñas", "Tatuajes", "Gimnasios", "Bares"]),
            ("end", "Primera semana *gratis*.", "Se activa en un minuto.", "socialperkses.com"),
        ],
        "lead": [
            ("hook", "Para ti, Lead:", "¿Conoces a dueños de locales? Cada uno puede *pagarte cada mes*."),
            ("trio", "Esto es SocialPerks:", ["Un cliente comparte", "Un amigo viene", "Escaneo en el mostrador"], "El local llena sus horas *flojas*."),
            ("step", 1, "Te *registras*. Dos minutos.", "join"),
            ("step", 2, "Enseñas *tu QR* al dueño.", "lead"),
            ("step", 3, "Lo escanea y activa su local. *Le ayudamos nosotros.*", "qr-scan"),
            ("money", "*49 €* por cada local que empieza a pagar.", "Y *9,80 €* cada mes, mientras siga pagando.", ["10 locales", "490 €", "+ 98 € al mes"]),
            ("free", "Sin jefe. Sin zonas. Sin mínimos. *Cobras en euros, cada mes.*"),
            ("end", "Empieza *hoy*.", "Te registras en dos minutos.", "socialperkses.com/leads/join"),
        ],
    },
    "it": {
        "venue": [
            ("hook", "Se hai un locale:", "Quante ore della tua settimana restano *vuote*?"),
            ("week", "SocialPerks *vede* le ore che non si riempiranno."),
            ("gifts", "Ci metti un *piccolo regalo*.", ["Una maschera", "Un calice di bollicine", "Un panno caldo"]),
            ("stories", "I tuoi clienti lo *condividono*, ognuno con il suo link."),
            ("friend", "I loro amici *arrivano* proprio in quelle ore."),
            ("counter", "Alla cassa: *una scansione*. Niente da scrivere."),
            ("price", "*49 €* al mese.", "Meno di 3 clienti nuovi in un mese? *Ti rimborsiamo.*"),
            ("grid", "Per *ogni* tipo di locale.", ["Parrucchieri", "Barbieri", "Unghie", "Tatuaggi", "Palestre", "Bar"]),
            ("end", "Prima settimana *gratis*.", "Si attiva in un minuto.", "socialperkses.com"),
        ],
        "lead": [
            ("hook", "Per te, Lead:", "Conosci titolari di locali? Ognuno può *pagarti ogni mese*."),
            ("trio", "Ecco SocialPerks:", ["Un cliente condivide", "Un amico arriva", "Scansione alla cassa"], "Il locale riempie le ore *vuote*."),
            ("step", 1, "Ti *registri*. Due minuti.", "join"),
            ("step", 2, "Mostri *il tuo QR* al titolare.", "lead"),
            ("step", 3, "Lo scansiona e attiva il locale. *Lo aiutiamo noi.*", "qr-scan"),
            ("money", "*49 €* per ogni locale che inizia a pagare.", "E *9,80 €* ogni mese, finché continua a pagare.", ["10 locali", "490 €", "+ 98 € al mese"]),
            ("free", "Niente capo. Niente zone. Niente minimi. *Pagato in euro, ogni mese.*"),
            ("end", "Inizia *oggi*.", "Ti registri in due minuti.", "socialperkses.com/leads/join"),
        ],
    },
    "en": {
        "venue": [
            ("hook", "If you run a venue:", "How many hours of your week stay *empty*?"),
            ("week", "SocialPerks *spots* the hours that won't fill."),
            ("gifts", "You put *one small gift* on them.", ["A hair mask", "A glass of cava", "A hot towel"]),
            ("stories", "Your clients *share* it, each with their own link."),
            ("friend", "Their friends *come in* at exactly those hours."),
            ("counter", "At the counter: *one scan*. Nothing to type."),
            ("price", "*€49* a month.", "Fewer than 3 new clients in a month? *You get it back.*"),
            ("grid", "For *any* kind of venue.", ["Salons", "Barbers", "Nails", "Tattoo", "Gyms", "Bars"]),
            ("end", "First week *free*.", "Ready in one minute.", "socialperkses.com"),
        ],
        "lead": [
            ("hook", "For you, Lead:", "Know venue owners? Each one can *pay you every month*."),
            ("trio", "This is SocialPerks:", ["A client shares", "A friend comes in", "Scanned at the counter"], "The venue fills its *quiet* hours."),
            ("step", 1, "You *sign up*. Two minutes.", "join"),
            ("step", 2, "You show the owner *your QR*.", "lead"),
            ("step", 3, "They scan it and switch the venue on. *We help them set up.*", "qr-scan"),
            ("money", "*€49* for each venue that starts paying.", "Then *€9.80* every month, while it keeps paying.", ["10 venues", "€490", "+ €98 a month"]),
            ("free", "No boss. No territory. No minimums. *Paid in euros, every month.*"),
            ("end", "Start *today*.", "Sign up in two minutes.", "socialperkses.com/leads/join"),
        ],
    },
}

NAMES = {
    "es": {"venue": "3_Video_para_el_local", "lead": "4_Video_para_ti"},
    "it": {"venue": "3_Video_per_il_locale", "lead": "4_Video_per_te"},
    "en": {"venue": "3_Video_for_the_venue", "lead": "4_Video_for_you"},
}

# ----------------------------------------------------------------- pictures


def load(lang, name):
    path = os.path.join(ASSETS, lang, name + ".jpg")
    if not os.path.exists(path):
        path = os.path.join(ASSETS, name + ".jpg") if os.path.exists(os.path.join(ASSETS, name + ".jpg")) else os.path.join(ASSETS, name)
    return Image.open(path).convert("RGBA")


def fit_w(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def round_corners(im, r):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    out = im.copy()
    out.putalpha(mask)
    return out


def story_card(lang, name, w):
    """A customer's Story, whole, as the console shows it."""
    return D.shadowed(round_corners(fit_w(load(lang, name), w), int(w * 0.075)), blur=30, offset=18, opacity=120)


def week_phone(lang, name, w):
    """The owner's week on the homepage's phone, the page around its frame cut away."""
    im = load(lang, name)
    for corner in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)]:
        ImageDraw.floodfill(im, corner, (0, 0, 0, 0), thresh=40)
    return D.shadowed(fit_w(im, w), blur=34, offset=22, opacity=130)


def scene_card(lang, name, w):
    """A frame of the homepage's QR flow: the table card and the guest's phone."""
    return D.shadowed(round_corners(fit_w(load(lang, name), w), int(w * 0.05)), blur=30, offset=18, opacity=110)


def phone_screen(lang, name, w):
    """A page of the product inside a plain phone body."""
    screen = fit_w(load(lang, name), w - 36)
    screen = screen.crop((0, 0, screen.width, min(screen.height, int(screen.width * 2.05))))
    body = D.rounded((w, screen.height + 36), 64, INK + (255,))
    body.alpha_composite(round_corners(screen, 48), (18, 18))
    return D.shadowed(body, blur=34, offset=22, opacity=130)


def photo_tile(name, w, h, label=None):
    im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
    im = D.cover(im.convert("RGB"), w, h).convert("RGBA")
    im = round_corners(im, int(w * 0.09))
    if label:
        tag = D.pill(label, 34, INK, (255, 255, 255, 240), weight=800)
        im.alpha_composite(tag, (18, h - tag.height - 18))
    return D.shadowed(im, blur=22, offset=12, opacity=100)


# ----------------------------------------------------------------- scenes


def headline(text, pal, size=104, top=230, align="left", max_h=520):
    words = D.Words(text, size, 64, TEXT_W, max_h, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"], align=align)
    return words, top


def rise_in(t, start=0.25, dur=0.6):
    p = D.ease_out(D.prog(t, start, dur))
    return p, (1 - p) * 120


def scene_hook(eyebrow, text, pal, dur=3.4):
    back = D.Backdrop(pal)
    words = D.Words(text, 128, 76, TEXT_W, 860, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    oy = 900 - words.height / 2
    brow = D.text_sprite(eyebrow, 50, 700, D.BODY, pal["sub"])

    def draw(t):
        fr = back.frame(t)
        p = D.ease_out(D.prog(t, 0.0, 0.4))
        D.paste(fr, brow, LEFT, oy - 120 + (1 - p) * 30, p)
        words.draw(fr, LEFT, oy, t, start=0.15, stagger=min(0.09, 1.2 / max(1, len(words.items))))
        return fr
    draw.branded = True
    return dur, draw


def scene_picture(text, sprites, pal, dur, arrange="single"):
    """A line at the top, the product below it, rising in and drifting slowly closer."""
    back = D.Backdrop(pal)
    words, top = headline(text, pal, size=96, max_h=420)
    area_top = top + words.height + 70

    def draw(t):
        fr = back.frame(t + 3)
        words.draw(fr, LEFT, top, t, start=0.05, stagger=0.05, style="rise")
        drift = 1 + 0.035 * D.ease_in_out(t / dur)
        if arrange == "single":
            sp = sprites[0]
            p, dy = rise_in(t)
            cy = area_top + (H - 160 - area_top) / 2
            D.paste_scaled(fr, sp, W / 2, cy + dy, (0.9 + 0.1 * p) * drift, p)
        else:  # a pair, the second behind and to the right
            for i, sp in enumerate(sprites):
                p, dy = rise_in(t, 0.2 + 0.25 * i)
                cx = W / 2 + (-170 if i == 0 else 190)
                cy = area_top + (H - 160 - area_top) / 2 + (40 if i else -20)
                D.paste_scaled(fr, sp, cx, cy + dy, (0.9 + 0.1 * p) * drift, p)
        return fr
    return dur, draw


def scene_gifts(text, labels, pal, dur=4.2):
    back = D.Backdrop(pal)
    words, top = headline(text, pal, size=104, max_h=440)
    names = ["gift-salon-treatment.jpg", "gift-cocktail_bar-cava.jpg", "gift-barber-hot-towel.jpg"]
    tiles = [photo_tile(n, 820, 340, label) for n, label in zip(names, labels)]
    y0 = top + words.height + 70

    def draw(t):
        fr = back.frame(t + 5)
        words.draw(fr, LEFT, top, t, start=0.05, stagger=0.05, style="rise")
        for i, tile in enumerate(tiles):
            p = D.ease_back(D.prog(t, 0.35 + 0.28 * i, 0.5))
            if p <= 0:
                continue
            cx = W / 2 + (-30 if i % 2 else 30)
            D.paste_scaled(fr, tile, cx, y0 + 200 + i * 390, 0.7 + 0.3 * p, D.clamp(p * 1.6))
        return fr
    return dur, draw


def scene_price(big, small, pal, dur=5.2):
    back = D.Backdrop(pal)
    first = D.Words(big, 190, 120, TEXT_W, 420, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"], align="center")
    second = D.Words(small, 84, 56, TEXT_W, 520, weight=800, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"], align="center")
    ring = D.ring_gradient(150)
    check = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(check)
    d.ellipse((10, 10, 140, 140), fill=WHITE)
    d.line((45, 78, 68, 102, 108, 54), fill=SIGNAL, width=16, joint="curve")

    def draw(t):
        fr = back.frame(t + 7)
        first.draw(fr, LEFT, 560 - first.height / 2, t, start=0.05, stagger=0.08)
        second.draw(fr, LEFT, 900, t, start=1.4, stagger=0.06, style="rise")
        p = D.ease_back(D.prog(t, 2.6, 0.5))
        if p > 0:
            D.paste_scaled(fr, ring, W / 2, 900 + second.height + 170, 0.6 + 0.4 * p, D.clamp(p * 2))
            D.paste_scaled(fr, check, W / 2, 900 + second.height + 170, (0.6 + 0.4 * p) * 0.8, D.clamp(p * 2))
        return fr
    draw.branded = True
    return dur, draw


def scene_grid(text, labels, pal, dur=3.8):
    back = D.Backdrop(pal)
    words, top = headline(text, pal, size=110, max_h=300, align="center")
    names = ["place-salon.jpg", "place-barber.jpg", "place-nails.jpg", "place-tattoo_studio.jpg", "place-gym.jpg", "place-cocktail_bar.jpg"]
    tw, th, gap = 400, 380, 34
    tiles = [photo_tile(n, tw, th, label) for n, label in zip(names, labels)]
    y0 = top + words.height + 70

    def draw(t):
        fr = back.frame(t + 11)
        words.draw(fr, LEFT, top, t, start=0.05, stagger=0.06, style="rise")
        for i, tile in enumerate(tiles):
            col, row = i % 2, i // 2
            p = D.ease_back(D.prog(t, 0.3 + 0.12 * i, 0.45))
            if p <= 0:
                continue
            cx = W / 2 + (col - 0.5) * (tw + gap)
            cy = y0 + th / 2 + row * (th + gap)
            D.paste_scaled(fr, tile, cx, cy, 0.75 + 0.25 * p, D.clamp(p * 1.6))
        return fr
    return dur, draw


def scene_end(line1, line2, url, pal, dur=4.6, qr=False):
    back = D.Backdrop(pal)
    m = D.shadowed(D.mark(200), blur=26, offset=14, opacity=110)
    first = D.Words(line1, 120, 80, TEXT_W, 300, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"], align="center")
    sub = D.text_sprite(line2, 56, 600, D.BODY, pal["sub"])
    site = D.pill(url, 52 if len(url) < 24 else 44, pal["hl_text"], pal["hl"] + (255,), weight=800)
    code = None
    if qr:
        q = Image.open(os.path.join(ASSETS, "join-qr.png")).convert("RGBA").resize((420, 420), Image.NEAREST)
        card = D.rounded((470, 470), 40, (255, 255, 255, 255))
        card.alpha_composite(q, (25, 25))
        code = D.shadowed(card, blur=26, offset=14, opacity=110)

    def draw(t):
        fr = back.frame(t + 13)
        pm = D.prog(t, 0.0, 0.5)
        D.paste_scaled(fr, m, W / 2, 380, 0.5 + 0.5 * D.ease_back(pm), D.clamp(pm * 2))
        first.draw(fr, LEFT, 560, t, start=0.25, stagger=0.06)
        ps = D.ease_out(D.prog(t, 0.7, 0.4))
        D.paste(fr, sub, (W - sub.width) / 2, 560 + first.height + 30 + (1 - ps) * 30, ps)
        pq = D.ease_back(D.prog(t, 1.0, 0.5))
        y = 560 + first.height + 150
        if code is not None and pq > 0:
            D.paste_scaled(fr, code, W / 2, y + 260, 0.7 + 0.3 * pq, D.clamp(pq * 2))
            y += 560
        pu = D.ease_back(D.prog(t, 1.2, 0.45))
        if pu > 0:
            D.paste_scaled(fr, site, W / 2, y + 60, 0.7 + 0.3 * pu, D.clamp(pu * 2))
        return fr
    return dur, draw


def number_dot(n, size=78):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, size - 1, size - 1), fill=SIGNAL)
    f = D.font(int(size * 0.55), 900)
    d.text(((size - f.getlength(str(n))) / 2, size * 0.14), str(n), font=f, fill=WHITE)
    return im


def scene_trio(title, captions, bottom, lang, pal, dur=6.0):
    """What SocialPerks is, in three rows: the Story, the friend, the counter."""
    back = D.Backdrop(pal)
    brow = D.text_sprite(title, 50, 700, D.BODY, pal["sub"])
    words = D.Words(bottom, 104, 64, TEXT_W, 300, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    shots = [story_card(lang, "story-cocktail", 230), scene_card(lang, "qr-gift", 400), scene_card(lang, "qr-counter", 400)]
    dots = [number_dot(i + 1) for i in range(3)]
    text_x = LEFT + 470
    labels = [D.Words(c, 62, 44, W - LEFT - text_x - 100, 220, weight=800, color=pal["fg"]) for c in captions]
    top = 190
    row0 = top + 80 + words.height + 60

    def draw(t):
        fr = back.frame(t + 2)
        pb = D.ease_out(D.prog(t, 0.0, 0.4))
        D.paste(fr, brow, LEFT, top + (1 - pb) * 20, pb)
        words.draw(fr, LEFT, top + 80, t, start=0.1, stagger=0.05, style="rise")
        y = row0
        for i, (sp, dot, label) in enumerate(zip(shots, dots, labels)):
            h = min(sp.height, 440)
            s_ = h / sp.height
            p = D.ease_back(D.prog(t, 0.7 + 0.8 * i, 0.5))
            if p > 0:
                D.paste_scaled(fr, sp, LEFT + 200, y + h / 2, s_ * (0.8 + 0.2 * p), D.clamp(p * 1.6))
                pc = D.ease_out(D.prog(t, 0.95 + 0.8 * i, 0.35))
                D.paste(fr, dot, text_x, y + h / 2 - dot.height / 2 + (1 - pc) * 20, pc)
                label.draw(fr, text_x + dot.width + 24, y + h / 2 - label.height / 2, t, start=1.0 + 0.8 * i, stagger=0.04, style="rise")
            y += h + 30
        return fr
    return dur, draw


def scene_step(n, text, shot, lang, pal, dur=3.8):
    back = D.Backdrop(pal)
    chip = D.step_chip(n, {"es": "Paso", "it": "Passo", "en": "Step"}[lang] + f" {n}")
    words = D.Words(text, 100, 64, TEXT_W, 420, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    if shot in ("join", "lead"):
        sprite = phone_screen(lang, shot, 640)
    else:
        sprite = scene_card(lang, shot, 900)
    top = 200
    area_top = top + chip.height + 30 + words.height + 70

    def draw(t):
        fr = back.frame(t + 4 * n)
        pc = D.ease_out(D.prog(t, 0.0, 0.3))
        D.paste(fr, chip, LEFT - 20, top + (1 - pc) * 20, pc)
        words.draw(fr, LEFT, top + chip.height + 30, t, start=0.15, stagger=0.05, style="rise")
        p, dy = rise_in(t, 0.35)
        drift = 1 + 0.03 * D.ease_in_out(t / dur)
        top_of_sprite = area_top + dy
        visible = H - 120 - area_top
        s = min(1.0, visible / sprite.height) if shot not in ("join", "lead") else 1.0
        D.paste_scaled(fr, sprite, W / 2, top_of_sprite + sprite.height * s / 2, s * (0.92 + 0.08 * p) * drift, p)
        return fr
    return dur, draw


def scene_money(first, second, example, pal, dur=6.4):
    back = D.Backdrop(pal)
    a = D.Words(first, 104, 64, TEXT_W, 380, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    b = D.Words(second, 84, 56, TEXT_W, 340, weight=700, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    label, total, monthly = example
    card = D.rounded((W - 2 * LEFT, 420), 56, (255, 255, 255, 245))
    d = ImageDraw.Draw(card)
    d.text((56, 44), label, font=D.font(54, 700, D.BODY), fill=(96, 96, 108))
    d.text((56, 120), total, font=D.font(170, 900), fill=INK)
    d.text((56, 320), monthly, font=D.font(60, 800, D.BODY), fill=SIGNAL)
    card = D.shadowed(card, blur=28, offset=16, opacity=90)

    def draw(t):
        fr = back.frame(t + 6)
        a.draw(fr, LEFT, 210, t, start=0.05, stagger=0.06)
        b.draw(fr, LEFT, 230 + a.height + 50, t, start=1.5, stagger=0.05, style="rise")
        p = D.ease_back(D.prog(t, 3.2, 0.55))
        if p > 0:
            D.paste_scaled(fr, card, W / 2, 1420, 0.8 + 0.2 * p, D.clamp(p * 1.8))
        return fr
    draw.branded = True
    return dur, draw


def scene_free(text, pal, dur=4.0):
    back = D.Backdrop(pal)
    words = D.Words(text, 124, 76, TEXT_W, 1000, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"], align="center")
    oy = 920 - words.height / 2

    def draw(t):
        fr = back.frame(t + 9)
        words.draw(fr, LEFT, oy, t, start=0.05, stagger=0.09)
        return fr
    draw.branded = True
    return dur, draw


# ----------------------------------------------------------------- timelines


def timeline(lang, which):
    out = []
    for item in COPY[lang][which]:
        kind = item[0]
        if kind == "hook":
            out.append(scene_hook(item[1], item[2], DARK if which == "venue" else BLUE))
        elif kind == "week":
            out.append(scene_picture(item[1], [week_phone(lang, "week-bar", 470), week_phone(lang, "week-gym", 470)], NIGHT, 4.4, "pair"))
        elif kind == "gifts":
            out.append(scene_gifts(item[1], item[2], PAPER))
        elif kind == "stories":
            out.append(scene_picture(item[1], [story_card(lang, "story-cocktail", 480), story_card(lang, "story-barber", 480)], BLUE, 4.4, "pair"))
        elif kind == "friend":
            out.append(scene_picture(item[1], [scene_card(lang, "qr-gift", 960)], ROSE, 3.8))
        elif kind == "counter":
            out.append(scene_picture(item[1], [scene_card(lang, "qr-counter", 960)], DARK, 4.0))
        elif kind == "price":
            out.append(scene_price(item[1], item[2], BLUE))
        elif kind == "grid":
            out.append(scene_grid(item[1], item[2], PAPER))
        elif kind == "end":
            out.append(scene_end(item[1], item[2], item[3], NIGHT if which == "venue" else DARK, qr=(which == "lead")))
        elif kind == "trio":
            out.append(scene_trio(item[1], item[2], item[3], lang, NIGHT))
        elif kind == "step":
            out.append(scene_step(item[1], item[2], item[3], lang, [PAPER, ROSE, BLUE][item[1] - 1]))
        elif kind == "money":
            out.append(scene_money(item[1], item[2], item[3], DARK))
        elif kind == "free":
            out.append(scene_free(item[1], ROSE))
    return out


def render(lang, which, out_path, cover_path, seed):
    return render_scenes(timeline(lang, which), out_path, cover_path, seed)


def render_scenes(scenes, out_path, cover_path, seed):
    """Scenes to an MP4 with the day's kind of music, cutting with a short push and flash; also used by founding_video.py."""
    total = sum(d for d, _ in scenes)
    frames = int(round(total * FPS))
    wav = out_path[:-4] + ".wav"
    D.music(seed, total, wav)
    mk = D.watermark(None)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    starts, acc = [], 0.0
    for d, _ in scenes:
        starts.append(acc)
        acc += d
    best = None
    for i in range(frames):
        t = i / FPS
        k = max(j for j, s in enumerate(starts) if s <= t + 1e-9)
        local = t - starts[k]
        fr = scenes[k][1](local)
        if k > 0 and local < 0.2:
            z = 1 + 0.05 * (1 - D.ease_out(local / 0.2))
            cw, ch = W / z, H / z
            fr = fr.crop((int((W - cw) / 2), int((H - ch) / 2), int((W + cw) / 2), int((H + ch) / 2))).resize((W, H), Image.BILINEAR)
            flash = int(90 * (1 - local / 0.2))
            if flash > 0:
                fr.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, flash)))
        if getattr(scenes[k][1], "branded", False):
            D.paste(fr, mk, LEFT, H - 250, 0.9)
        rgb = fr.convert("RGB")
        if best is None and k == 0 and local >= min(2.4, scenes[0][0] - 0.3):
            best = rgb.copy()
        proc.stdin.write(rgb.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit(f"ffmpeg failed for {out_path}")
    os.remove(wav)
    (best or rgb).save(cover_path, quality=90)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/lead-kit")
    ap.add_argument("--lang", choices=["es", "it", "en"], action="append")
    ap.add_argument("--only", choices=["venue", "lead"])
    a = ap.parse_args()
    for lang in a.lang or ["es", "it", "en"]:
        os.makedirs(os.path.join(a.out, lang), exist_ok=True)
        for which in ([a.only] if a.only else ["venue", "lead"]):
            base = os.path.join(a.out, lang, NAMES[lang][which])
            total = render(lang, which, base + ".mp4", base + ".jpg", seed=7 if which == "venue" else 11)
            print(f"{base}.mp4  {total:.1f}s")


if __name__ == "__main__":
    main()
