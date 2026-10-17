#!/usr/bin/env python3
"""The Founding Partner video: about three minutes, in Catalan and Spanish.

    python3 founding_video.py --out /tmp/founding            # both
    python3 founding_video.py --out /tmp/founding --lang ca  # one

For the Barcelona venues that signed a letter of intent before SocialPerks
joined EWorks (the owner, 17 October): explained so that anybody follows it,
with music and nothing rough. Six parts: the empty hour, the idea, how it
works in four steps, what the owner sees, what a Founding Partner gets
(0 € for good, where every other venue pays 49 € a month), and how to start:
with the QR on the venue's own sheet. Each venue has its own single-use
sign-up link (socialperks docs/sales/founding-partner), so the video shows
none: this repository is public.

Drawn with daily.py's and lead_kit.py's tools over the product's own screens,
captured in each language (assets/founding/<lang>).
"""

from __future__ import annotations

import argparse
import os

from PIL import Image, ImageDraw

import daily as D
import lead_kit as K
from daily import W, H, LEFT, TEXT_W, WHITE, INK, SIGNAL, YELLOW, PALETTES

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets", "founding")
DARK, BLUE, PAPER, ROSE, NIGHT = PALETTES

COPY = {
    "ca": {
        "file": "SocialPerks_Founding_Partner_CAT",
        "step": "Pas",
        "scenes": [
            ("photo", "Dimarts, 17:00", "Les taules parades. I no entra *ningú*."),
            ("say", "Cada setmana tens hores així. I el lloguer el pagues *igualment*.", DARK),
            ("week", "SocialPerks *veu* les hores que no s'omplen."),
            ("say", "La solució no és més publicitat. Són els *teus clients*.", BLUE),
            ("stories", "Avui tothom es passa enllaços. *Stories*, WhatsApp, grups."),
            ("chapter", "Com funciona", "Quatre passos. *Res de complicat.*", DARK),
            ("step", 1, "Marques les hores *fluixes*. Per exemple, el dimarts a la tarda.", "week-a"),
            ("gifts", 2, "Tries un *detall petit*.", ["Un cafè", "Un vermut", "Unes postres"]),
            ("step", 3, "El client escaneja el teu QR i *comparteix* el seu enllaç.", "qr-scan"),
            ("story", "En una Story o per WhatsApp, marcat com a *publicitat*."),
            ("step", 4, "El seu amic *reserva* i ve a aquella hora.", "qr-gift"),
            ("counter", "Al local escaneges el seu codi i li dones el *detall*. Sense escriure res."),
            ("say", "Un regal, *una vegada*. Ni més ni menys.", BLUE),
            ("chapter", "Què veus tu", "Tot, des del *mòbil*.", NIGHT),
            ("card", "Qui ha vingut i *de part de qui*.", "results"),
            ("card", "Et preparem les *Stories* i les publicacions.", "content"),
            ("say", "Ho calculem tot perquè et surti *a compte*. El detall costa poc. Aquella hora, si no, estaria buida.", DARK),
            ("grid", "Per a *qualsevol* local.", ["Restaurants", "Bars", "Cafeteries", "Pizzeries", "Perruqueries", "Gimnasos"]),
            ("chapter", "Founding Partner", "Vas creure en nosaltres *abans que ningú*.", BLUE),
            ("compare", ("Els altres locals", "49 €", "al mes"), ("Tu", "0 €", "Per sempre.")),
            ("facts", "A més a més:", ["Sense targeta", "Sense contracte", "Ho deixes quan vulguis"]),
            ("say", "Ets un dels primers locals de SocialPerks a Barcelona. I el teu local sortirà al nostre *web*.", NIGHT),
            ("start", "Comences en *5 minuts*.", ["Escaneja el QR del teu document", "Omple les teves dades", "Posa el teu QR al local"]),
            ("end", "Registra't *gratis*.", "Amb el QR del teu document.", "Només per al teu local · Sense targeta"),
        ],
    },
    "es": {
        "file": "SocialPerks_Founding_Partner",
        "step": "Paso",
        "scenes": [
            ("photo", "Martes, 17:00", "Las mesas puestas. Y no entra *nadie*."),
            ("say", "Cada semana tienes horas así. Y el alquiler lo pagas *igual*.", DARK),
            ("week", "SocialPerks *ve* las horas que no se llenan."),
            ("say", "La solución no es más publicidad. Son *tus clientes*.", BLUE),
            ("stories", "Hoy todo el mundo se pasa enlaces. *Stories*, WhatsApp, grupos."),
            ("chapter", "Cómo funciona", "Cuatro pasos. *Nada complicado.*", DARK),
            ("step", 1, "Marcas tus horas *flojas*. Por ejemplo, el martes por la tarde.", "week-a"),
            ("gifts", 2, "Eliges un *detalle pequeño*.", ["Un café", "Un vermut", "Un postre"]),
            ("step", 3, "El cliente escanea tu QR y *comparte* su enlace.", "qr-scan"),
            ("story", "En una Story o por WhatsApp, marcado como *publicidad*."),
            ("step", 4, "Su amigo *reserva* y viene a esa hora.", "qr-gift"),
            ("counter", "En el local escaneas su código y le das el *detalle*. Sin escribir nada."),
            ("say", "Un regalo, *una vez*. Ni más ni menos.", BLUE),
            ("chapter", "Qué ves tú", "Todo, desde el *móvil*.", NIGHT),
            ("card", "Quién ha venido y *de parte de quién*.", "results"),
            ("card", "Te preparamos las *Stories* y los posts.", "content"),
            ("say", "Lo calculamos todo para que te salga *a cuenta*. El detalle cuesta poco. Esa hora, si no, estaría vacía.", DARK),
            ("grid", "Para *cualquier* local.", ["Restaurantes", "Bares", "Cafeterías", "Pizzerías", "Peluquerías", "Gimnasios"]),
            ("chapter", "Founding Partner", "Creíste en nosotros *antes que nadie*.", BLUE),
            ("compare", ("Los demás locales", "49 €", "al mes"), ("Tú", "0 €", "Para siempre.")),
            ("facts", "Y además:", ["Sin tarjeta", "Sin contrato", "Lo dejas cuando quieras"]),
            ("say", "Eres uno de los primeros locales de SocialPerks en Barcelona. Y tu local saldrá en nuestra *web*.", NIGHT),
            ("start", "Empiezas en *5 minutos*.", ["Escanea el QR de tu documento", "Rellena tus datos", "Pon tu QR en el local"]),
            ("end", "Regístrate *gratis*.", "Con el QR de tu documento.", "Solo para tu local · Sin tarjeta"),
        ],
    },
}

# ----------------------------------------------------------------- pictures


def load(lang, name):
    for path in (os.path.join(ASSETS, lang, name), os.path.join(ASSETS, name)):
        for ext in ("", ".png", ".jpg"):
            if os.path.exists(path + ext):
                return Image.open(path + ext).convert("RGBA")
    raise FileNotFoundError(name)


def card(lang, name, w, radius=0.05, shadow=True):
    im = K.round_corners(K.fit_w(load(lang, name), w), int(w * radius))
    return D.shadowed(im, blur=30, offset=18, opacity=115) if shadow else im


def phone(lang, name, w):
    """The owner's week on the homepage phone, its lower half fading out."""
    return D.shadowed(K.fit_w(load(lang, name), w), blur=34, offset=22, opacity=120)


def tile(name, w, h, label):
    im = D.cover(load("", name).convert("RGB"), w, h).convert("RGBA")
    im = K.round_corners(im, int(w * 0.08))
    tag = D.pill(label, 36, INK, (255, 255, 255, 240), weight=800)
    im.alpha_composite(tag, (20, h - tag.height - 20))
    return D.shadowed(im, blur=22, offset=12, opacity=100)


# ----------------------------------------------------------------- scenes


def scene_photo(eyebrow, text, dur=8.0):
    """The quiet hour: an empty dining room, drifting closer, the words over it."""
    bg = D.KenBurns(load("", "quiet-hour.jpg").convert("RGB"), zoom=(1.0, 1.1), focus=(0.5, 0.5), dark=0.2)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for y in range(H // 3, H):
        d.line((0, y, W, y), fill=(8, 8, 14, int(235 * ((y - H / 3) / (H * 2 / 3)) ** 1.3)))
    words = D.Words(text, 124, 76, TEXT_W, 640, color=WHITE, hl=SIGNAL, hl_text=WHITE)
    brow = D.pill(eyebrow, 46, INK, (255, 255, 255, 240), weight=800)
    oy = H - 330 - words.height

    def draw(t):
        fr = bg.frame(t / dur)
        fr.alpha_composite(shade)
        p = D.ease_out(D.prog(t, 0.5, 0.5))
        D.paste(fr, brow, LEFT, oy - brow.height - 40 + (1 - p) * 30, p)
        words.draw(fr, LEFT, oy, t, start=1.0, stagger=0.12)
        return fr
    return dur, draw


def scene_say(text, pal, dur=None):
    words = len(text.split())
    return K.scene_free(text, pal, dur or max(5.0, 2.2 + words * 0.36))


def scene_chapter(eyebrow, text, pal, dur=4.6):
    return K.scene_hook(eyebrow, text, pal, dur)


def scene_step(n, label, text, sprite, pal, dur=7.0):
    """A numbered step: the chip, the line, and the product below it."""
    back = D.Backdrop(pal)
    chip = D.step_chip(n, f"{label} {n}")
    words = D.Words(text, 96, 60, TEXT_W, 420, color=pal["fg"], hl=pal["hl"], hl_text=pal["hl_text"])
    top = 200
    area_top = top + chip.height + 30 + words.height + 70
    visible = H - 140 - area_top
    s = min(1.0, visible / sprite.height)

    def draw(t):
        fr = back.frame(t + 4 * n)
        pc = D.ease_out(D.prog(t, 0.0, 0.3))
        D.paste(fr, chip, LEFT - 20, top + (1 - pc) * 20, pc)
        words.draw(fr, LEFT, top + chip.height + 30, t, start=0.15, stagger=0.06, style="rise")
        p, dy = K.rise_in(t, 0.5)
        drift = 1 + 0.03 * D.ease_in_out(t / dur)
        D.paste_scaled(fr, sprite, W / 2, area_top + dy + sprite.height * s / 2, s * (0.92 + 0.08 * p) * drift, p)
        return fr
    return dur, draw


def scene_gifts(n, label, text, labels, dur=7.5):
    back = D.Backdrop(PAPER)
    chip = D.step_chip(n, f"{label} {n}")
    words = D.Words(text, 104, 64, TEXT_W, 300, color=INK, hl=YELLOW, hl_text=INK)
    tiles = [tile(name, 840, 330, lab) for name, lab in zip(["gift-coffee.jpg", "gift-vermut.jpg", "gift-dessert.jpg"], labels)]
    top = 200
    y0 = top + chip.height + 30 + words.height + 60

    def draw(t):
        fr = back.frame(t + 5)
        pc = D.ease_out(D.prog(t, 0.0, 0.3))
        D.paste(fr, chip, LEFT - 20, top + (1 - pc) * 20, pc)
        words.draw(fr, LEFT, top + chip.height + 30, t, start=0.15, stagger=0.06, style="rise")
        for i, sp in enumerate(tiles):
            p = D.ease_back(D.prog(t, 0.9 + 0.45 * i, 0.5))
            if p > 0:
                D.paste_scaled(fr, sp, W / 2 + (-28 if i % 2 else 28), y0 + 190 + i * 380, 0.7 + 0.3 * p, D.clamp(p * 1.6))
        return fr
    return dur, draw


def scene_card(text, sprite, pal, dur=7.4):
    """A line, then a piece of the owner's app floating under it."""
    back = D.Backdrop(pal)
    words, top = K.headline(text, pal, size=100, max_h=380)
    area_top = top + words.height + 80
    visible = H - 160 - area_top
    s = min(1.0, visible / sprite.height)

    def draw(t):
        fr = back.frame(t + 8)
        words.draw(fr, LEFT, top, t, start=0.05, stagger=0.06, style="rise")
        p, dy = K.rise_in(t, 0.45)
        drift = 1 + 0.03 * D.ease_in_out(t / dur)
        D.paste_scaled(fr, sprite, W / 2, area_top + dy + sprite.height * s / 2, s * (0.92 + 0.08 * p) * drift, p)
        return fr
    return dur, draw


def scene_grid(text, labels, dur=6.6):
    back = D.Backdrop(PAPER)
    words, top = K.headline(text, PAPER, size=110, max_h=300, align="center")
    names = ["place-restaurant.jpg", "place-bar.jpg", "place-cafe.jpg", "place-pizzeria.jpg", "place-salon.jpg", "place-gym.jpg"]
    tw, th, gap = 400, 380, 34
    tiles = [tile(n, tw, th, lab) for n, lab in zip(names, labels)]
    y0 = top + words.height + 70

    def draw(t):
        fr = back.frame(t + 11)
        words.draw(fr, LEFT, top, t, start=0.05, stagger=0.06, style="rise")
        for i, sp in enumerate(tiles):
            col, row = i % 2, i // 2
            p = D.ease_back(D.prog(t, 0.5 + 0.18 * i, 0.45))
            if p > 0:
                D.paste_scaled(fr, sp, W / 2 + (col - 0.5) * (tw + gap), y0 + th / 2 + row * (th + gap), 0.75 + 0.25 * p, D.clamp(p * 1.6))
        return fr
    return dur, draw


def scene_compare(others, you, dur=9.0):
    """What every other venue pays, struck out; what a Founding Partner pays, for good."""
    back = D.Backdrop(DARK)
    cw = W - 2 * LEFT

    def price_card(label, price, unit, fill, fg, accent):
        im = D.rounded((cw, 470), 56, fill)
        d = ImageDraw.Draw(im)
        d.text((60, 52), label, font=D.font(54, 700, D.BODY), fill=fg)
        f = D.font(210, 900)
        d.text((56, 130), price, font=f, fill=fg)
        d.text((76 + f.getlength(price), 260), unit, font=D.font(70, 800), fill=accent)
        return im, 56 + f.getlength(price)

    top, top_w = price_card(others[0], others[1], others[2], (255, 255, 255, 235), INK, (96, 96, 108))
    bottom, _ = price_card(you[0], you[1], you[2], SIGNAL + (255,), WHITE, YELLOW)
    top_s, bottom_s = D.shadowed(top, blur=26, offset=14, opacity=90), D.shadowed(bottom, blur=30, offset=18, opacity=130)
    y_top, y_bottom = 560, 1180

    def draw(t):
        fr = back.frame(t + 3)
        p1 = D.ease_back(D.prog(t, 0.2, 0.5))
        if p1 > 0:
            D.paste_scaled(fr, top_s, W / 2, y_top, 0.85 + 0.15 * p1, D.clamp(p1 * 1.6))
        ps = D.ease_in_out(D.prog(t, 1.8, 0.6))
        if ps > 0:
            d = ImageDraw.Draw(fr)
            x0 = (W - cw) / 2 + 50
            y = y_top - 470 / 2 + 250
            d.line((x0, y, x0 + (top_w + 10) * ps, y), fill=(223, 73, 150), width=16)
        p2 = D.ease_back(D.prog(t, 2.8, 0.55))
        if p2 > 0:
            D.paste_scaled(fr, bottom_s, W / 2, y_bottom, 0.8 + 0.2 * p2, D.clamp(p2 * 1.6))
        return fr
    draw.branded = True
    return dur, draw


def scene_facts(title, items, dur=7.0):
    back = D.Backdrop(ROSE)
    head = D.Words(title, 110, 70, TEXT_W, 200, color=WHITE, hl=INK, hl_text=WHITE)
    rows = [D.pill(x, 64, INK, (255, 255, 255, 245), weight=800, icon="check") for x in items]
    top = 380

    def draw(t):
        fr = back.frame(t + 9)
        head.draw(fr, LEFT, top, t, start=0.05, stagger=0.06, style="rise")
        for i, row in enumerate(rows):
            p = D.ease_back(D.prog(t, 0.8 + 0.7 * i, 0.45))
            if p > 0:
                D.paste_scaled(fr, row, LEFT + row.width / 2, top + head.height + 170 + i * 210, 0.8 + 0.2 * p, D.clamp(p * 1.6))
        return fr
    draw.branded = True
    return dur, draw


def scene_start(title, steps, dur=8.6):
    back = D.Backdrop(PAPER)
    head = D.Words(title, 120, 76, TEXT_W, 300, color=INK, hl=YELLOW, hl_text=INK)
    dots = [K.number_dot(i + 1, 130) for i in range(len(steps))]
    labels = [D.Words(s_, 86, 56, TEXT_W - 180, 220, weight=800, color=INK) for s_ in steps]
    top = 360

    def draw(t):
        fr = back.frame(t + 12)
        head.draw(fr, LEFT, top, t, start=0.05, stagger=0.06, style="rise")
        y = top + head.height + 220
        for i, (dot, lab) in enumerate(zip(dots, labels)):
            p = D.ease_out(D.prog(t, 1.0 + 0.9 * i, 0.4))
            if p > 0:
                D.paste(fr, dot, LEFT, y + (1 - p) * 30, p)
                lab.draw(fr, LEFT + 170, y + dot.height / 2 - lab.height / 2, t, start=1.05 + 0.9 * i, stagger=0.04, style="rise")
            y += 340
        return fr
    return dur, draw


def scene_end(line1, line2, note, dur=9.0):
    """The close: sign up free, with the QR on the venue's own sheet."""
    back = D.Backdrop(NIGHT)
    m = D.shadowed(D.mark(220), blur=26, offset=14, opacity=110)
    first = D.Words(line1, 140, 90, TEXT_W, 340, color=WHITE, hl=NIGHT["hl"], hl_text=WHITE, align="center")
    sub = D.Words(line2, 80, 56, TEXT_W, 260, weight=800, color=WHITE, align="center")
    tag = D.pill(note, 46, INK, (255, 255, 255, 240), weight=800)
    site = D.text_sprite("socialperkses.com", 50, 700, D.BODY, NIGHT["sub"])

    def draw(t):
        fr = back.frame(t + 13)
        pm = D.prog(t, 0.0, 0.5)
        D.paste_scaled(fr, m, W / 2, 470, 0.5 + 0.5 * D.ease_back(pm), D.clamp(pm * 2))
        first.draw(fr, LEFT, 680, t, start=0.25, stagger=0.06)
        sub.draw(fr, LEFT, 720 + first.height, t, start=0.9, stagger=0.05, style="rise")
        pt = D.ease_back(D.prog(t, 1.6, 0.45))
        y = 720 + first.height + sub.height + 120
        if pt > 0:
            D.paste_scaled(fr, tag, W / 2, y, 0.7 + 0.3 * pt, D.clamp(pt * 2))
        ps = D.ease_out(D.prog(t, 2.0, 0.4))
        D.paste(fr, site, (W - site.width) / 2, H - 300 + (1 - ps) * 20, ps)
        return fr
    return dur, draw


# ----------------------------------------------------------------- timeline


def timeline(lang):
    c = COPY[lang]
    out = []
    for item in c["scenes"]:
        kind = item[0]
        if kind == "photo":
            out.append(scene_photo(item[1], item[2]))
        elif kind == "say":
            out.append(scene_say(item[1], item[2]))
        elif kind == "chapter":
            out.append(scene_chapter(item[1], item[2], item[3]))
        elif kind == "week":
            out.append(K.scene_picture(item[1], [phone(lang, "week-a", 470), phone(lang, "week-b", 470)], NIGHT, 7.0, "pair"))
        elif kind == "stories":
            out.append(K.scene_picture(item[1], [card(lang, "story-a", 470, 0.075), card(lang, "story-b", 470, 0.075)], ROSE, 7.0, "pair"))
        elif kind == "step":
            sprite = phone(lang, item[3], 560) if item[3].startswith("week") else card(lang, item[3], 900)
            out.append(scene_step(item[1], c["step"], item[2], sprite, [PAPER, PAPER, BLUE, ROSE][item[1] - 1]))
        elif kind == "gifts":
            out.append(scene_gifts(item[1], c["step"], item[2], item[3]))
        elif kind == "story":
            out.append(K.scene_picture(item[1], [card(lang, "story-a", 560, 0.075)], NIGHT, 7.0))
        elif kind == "counter":
            out.append(K.scene_picture(item[1], [card(lang, "qr-counter", 960)], DARK, 7.4))
        elif kind == "card":
            out.append(scene_card(item[1], card(lang, item[2], 880, 0.045), PAPER if item[2] == "results" else ROSE))
        elif kind == "grid":
            out.append(scene_grid(item[1], item[2]))
        elif kind == "compare":
            out.append(scene_compare(item[1], item[2]))
        elif kind == "facts":
            out.append(scene_facts(item[1], item[2]))
        elif kind == "start":
            out.append(scene_start(item[1], item[2]))
        elif kind == "end":
            out.append(scene_end(item[1], item[2], item[3]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/founding")
    ap.add_argument("--lang", choices=list(COPY), action="append")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for lang in a.lang or list(COPY):
        base = os.path.join(a.out, COPY[lang]["file"])
        total = K.render_scenes(timeline(lang), base + ".mp4", base + ".jpg", seed=9)
        print(f"{base}.mp4  {total:.1f}s")


if __name__ == "__main__":
    main()
