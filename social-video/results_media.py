#!/usr/bin/env python3
"""The videos for result pricing (SocialPerks policy results-2026-10-19).

    python3 results_media.py --out /tmp/media              # everything
    python3 results_media.py --out /tmp/media --only F1-es # one

Four kinds, one commercial definition (socialperks
docs/coordination/2026-10-21-claude-gtm-video-handoff.md):

  V1  the venue, the whole idea, about two and a half minutes (EN), for a Lead
      to play to an owner;
  V2  the venue, 35 to 40 seconds (EN, ES, IT), to forward;
  L1  a Lead, what they earn, about a minute (EN, ES, IT);
  F1  a Founding Partner, about three minutes (EN, ES, CA): their terms stay
      free for good, while other venues pay a capped fee on results.

The price, everywhere it is said: no monthly fee; up to 5% of a confirmed new
referred guest's first eligible paid visit, net of VAT and refunds, at most
EUR 3; never more than 20% of what the visit documents nor the venue's
budget; no evidence, no fee. The venue funds its gifts. A Lead gets 20% of
the fees SocialPerks actually collects, not of the bill. Nothing here shows
a real charge, a till integration, a notification or a customer count.

Text on screen and music, no voice: every line is burned in and also written
to an .srt beside the video. Drawn with daily.py's, lead_kit.py's and
founding_video.py's tools over the product's own screens (assets/results,
captured on 23 October 2026 from the live demo; assets/founding and
assets/lead-kit for the homepage's pictures).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess

from PIL import Image, ImageDraw

import daily as D
import founding_video as F
import lead_kit as K
from daily import W, H, LEFT, TEXT_W, WHITE, INK, SIGNAL, YELLOW, PALETTES

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
DARK, BLUE, PAPER, ROSE, NIGHT = PALETTES
GREEN = (28, 160, 104)

# ----------------------------------------------------------------- pictures

ALIASES = {
    "week-a": ["week-a", "week-bar"],
    "week-b": ["week-b", "week-gym"],
    "story-a": ["story-a", "story-cocktail"],
    "story-b": ["story-b", "story-barber"],
}


def load(lang, name):
    """The product's screen in this language, wherever it was captured."""
    dirs = [f"results/{lang}", f"founding/{lang}", f"lead-kit/{lang}", "results/en", "lead-kit/en", "founding", "lead-kit"]
    for n in ALIASES.get(name, [name]):
        for d in dirs:
            for ext in ("", ".png", ".jpg"):
                path = os.path.join(ASSETS, d, n + ext)
                if os.path.exists(path):
                    return Image.open(path).convert("RGBA")
    raise FileNotFoundError(f"{lang}/{name}")


def card(lang, name, w, radius=0.05, crop_h=None):
    im = load(lang, name)
    if crop_h:
        im = im.crop((0, 0, im.width, min(im.height, crop_h)))
    im = K.round_corners(K.fit_w(im, w), int(w * radius))
    return D.shadowed(im, blur=30, offset=18, opacity=115)


def phone(lang, name, w):
    return D.shadowed(K.fit_w(load(lang, name), w), blur=34, offset=22, opacity=120)


def money(lang, amount):
    """EUR 40.00 as the language writes it: €40.00, 40,00 €."""
    whole = amount == int(amount)
    if lang == "en":
        return f"€{amount:.0f}" if whole and amount >= 10 else f"€{amount:.2f}"
    text = f"{amount:.0f}" if whole and amount >= 10 else f"{amount:.2f}".replace(".", ",")
    # A no-break space: the amount and its sign never land on two lines.
    return f"{text}\u00a0€"


def panel(rows, w=900, title=None, note=None, total=None):
    """A white card of label / value rows, as the console draws its own."""
    pad, row_h = 56, 128
    f_label, f_value = D.font(44, 600, D.BODY), D.font(58, 900)
    f_title, f_note = D.font(40, 800, D.BODY), D.font(36, 600, D.BODY)
    h = pad * 2 + len(rows) * row_h + (90 if title else 0) + (110 if total else 0) + (80 if note else 0)
    im = D.rounded((w, h), 52, (255, 255, 255, 250))
    d = ImageDraw.Draw(im)
    y = pad
    if title:
        tag = D.pill(title, 34, SIGNAL, (236, 235, 253, 255), weight=800)
        im.alpha_composite(tag, (pad - 6, y - 6))
        y += 90
    for i, (label, value, tone) in enumerate(rows):
        if i:
            d.line((pad, y, w - pad, y), fill=(232, 232, 238), width=3)
        lines = D.wrap_lines(label, f_label, w - 2 * pad - 260)
        ly = y + (row_h - len(lines) * 52) / 2
        for line in lines:
            d.text((pad, ly), line, font=f_label, fill=(80, 82, 96))
            ly += 52
        colour = {"good": GREEN, "accent": SIGNAL}.get(tone, INK)
        vw = f_value.getlength(value)
        d.text((w - pad - vw, y + (row_h - 70) / 2), value, font=f_value, fill=colour)
        y += row_h
    if total:
        label, value = total
        d.rounded_rectangle((pad - 20, y + 14, w - pad + 20, y + 110), 28, fill=(236, 235, 253))
        d.text((pad + 6, y + 36), label, font=D.font(42, 800, D.BODY), fill=SIGNAL)
        vw = D.font(60, 900).getlength(value)
        d.text((w - pad - vw, y + 28), value, font=D.font(60, 900), fill=SIGNAL)
        y += 110
    if note:
        d.text((pad, y + 24), note, font=f_note, fill=(120, 120, 134))
    return D.shadowed(im, blur=30, offset=18, opacity=110)


L = {
    "example": dict(en="Example", es="Ejemplo", ca="Exemple", it="Esempio"),
    "code": dict(en="Guest's code", es="Código del cliente", ca="Codi del client", it="Codice del cliente"),
    "new": dict(en="New guest, first paid visit", es="Cliente nuevo, primera visita pagada", ca="Client nou, primera visita pagada", it="Cliente nuovo, prima visita pagata"),
    "yes": dict(en="Yes", es="Sí", ca="Sí", it="Sì"),
    "paid": dict(en="Paid, net of VAT", es="Pagado, sin IVA", ca="Pagat, sense IVA", it="Pagato, senza IVA"),
    "receipt": dict(en="Receipt no.", es="N.º de ticket", ca="Núm. de tiquet", it="N. scontrino"),
    "fee": dict(en="SocialPerks fee", es="Comisión SocialPerks", ca="Comissió SocialPerks", it="Commissione SocialPerks"),
    "bill": dict(en="New guest pays", es="El cliente nuevo paga", ca="El client nou paga", it="Il cliente nuovo paga"),
    "you_pay": dict(en="You pay", es="Tú pagas", ca="Tu pagues", it="Tu paghi"),
    "max": dict(en="max", es="máx.", ca="màx.", it="max"),
    "monthly": dict(en="Monthly fee", es="Cuota mensual", ca="Quota mensual", it="Canone mensile"),
    "fees": dict(en="Fees SocialPerks collects", es="Comisiones que cobra SocialPerks", ca="Comissions que cobra SocialPerks", it="Commissioni incassate da SocialPerks"),
    "for_you": dict(en="Your 20%", es="Tu 20 %", ca="El teu 20 %", it="Il tuo 20%"),
    "five": dict(en="Five venues like that", es="Cinco locales así", ca="Cinc locals així", it="Cinque locali così"),
    "a_month": dict(en="a month", es="al mes", ca="al mes", it="al mese"),
    "not_forecast": dict(en="Examples, not forecasts.", es="Ejemplos, no previsiones.", ca="Exemples, no previsions.", it="Esempi, non previsioni."),
    "step": dict(en="Step", es="Paso", ca="Pas", it="Passo"),
    "cap": dict(en="5% of the visit, never more than €3.", es="El 5 % de la visita, nunca más de 3 €.",
                ca="El 5 % de la visita, mai més de 3 €.", it="Il 5% della visita, mai più di 3 €."),
}


def receipt(lang):
    t = lambda k: L[k][lang]
    return panel(
        [(t("code"), "482 917", "good"), (t("new"), t("yes"), None), (t("paid"), money(lang, 40), None), (t("receipt"), "A-1023", None)],
        title=t("example"),
        total=(f"{t('fee')} · 5 %", money(lang, 2)),
    )


def fees(lang):
    t = lambda k: L[k][lang]
    rows = [(t("monthly"), money(lang, 0), "good")]
    for bill, fee in ((20, 1), (60, 3), (100, 3)):
        rows.append((f"{t('bill')} {money(lang, bill)}", money(lang, fee), "accent"))
    return panel(rows, title=t("example"), note=t("cap"))


def lead_money(lang):
    t = lambda k: L[k][lang]
    return panel(
        [(t("fees"), money(lang, 100), None), (t("for_you"), money(lang, 20), "good"), (t("five"), f"{money(lang, 100)}", "accent")],
        title=t("example"),
        note=t("not_forecast"),
    )


# ----------------------------------------------------------------- scenes


def scene_compare(others, you, dur=10.0):
    """What other venues pay, then what a Founding Partner pays: nothing, for good."""
    back = D.Backdrop(DARK)
    cw = W - 2 * LEFT

    def price_card(label, price, sub, fill, fg, accent):
        f_price = D.font(170, 900)
        sub_lines = D.wrap_lines(sub, D.font(48, 700, D.BODY), cw - 110)
        h = 70 + 70 + 190 + len(sub_lines) * 60 + 50
        im = D.rounded((cw, h), 56, fill)
        d = ImageDraw.Draw(im)
        d.text((56, 52), label, font=D.font(54, 700, D.BODY), fill=fg)
        d.text((52, 120), price, font=f_price, fill=fg)
        y = 330
        for line in sub_lines:
            d.text((58, y), line, font=D.font(48, 700, D.BODY), fill=accent)
            y += 60
        return D.shadowed(im, blur=28, offset=16, opacity=110), h

    top, h1 = price_card(*others, (255, 255, 255, 235), INK, (96, 96, 108))
    bottom, h2 = price_card(*you, SIGNAL + (255,), WHITE, YELLOW)
    y_top = 300 + h1 / 2
    y_bottom = y_top + h1 / 2 + 90 + h2 / 2

    def draw(t):
        fr = back.frame(t + 3)
        p1 = D.ease_back(D.prog(t, 0.2, 0.5))
        if p1 > 0:
            D.paste_scaled(fr, top, W / 2, y_top, 0.85 + 0.15 * p1, D.clamp(p1 * 1.6))
        p2 = D.ease_back(D.prog(t, 2.6, 0.55))
        if p2 > 0:
            D.paste_scaled(fr, bottom, W / 2, y_bottom, 0.8 + 0.2 * p2, D.clamp(p2 * 1.6))
        return fr
    draw.branded = True
    return dur, draw


def scene_facts(title, items, dur=7.0):
    """A list of ticks, each line wrapping instead of shrinking, so a long
    condition reads as large as a short one."""
    back = D.Backdrop(ROSE)
    head = D.Words(title, 110, 70, TEXT_W, 200, color=WHITE, hl=INK, hl_text=WHITE)
    tick = Image.new("RGBA", (84, 84), (0, 0, 0, 0))
    td = ImageDraw.Draw(tick)
    td.ellipse((0, 0, 83, 83), fill=(255, 255, 255, 250))
    td.line((22, 44, 37, 59, 63, 27), fill=GREEN, width=9)
    lines = [D.Words(x, 64, 48, TEXT_W - 120, 230, weight=800, color=WHITE, max_lines=3) for x in items]
    top = 360

    def draw(t):
        fr = back.frame(t + 9)
        head.draw(fr, LEFT, top, t, start=0.05, stagger=0.06, style="rise")
        y = top + head.height + 120
        for i, words in enumerate(lines):
            p = D.ease_back(D.prog(t, 0.8 + 0.7 * i, 0.45))
            if p > 0:
                D.paste_scaled(fr, tick, LEFT + 42, y + 42, 0.6 + 0.4 * p, D.clamp(p * 1.6))
                words.draw(fr, LEFT + 120, y + 4, t, start=0.85 + 0.7 * i, stagger=0.03, style="rise")
            y += max(words.height, 84) + 70
        return fr
    draw.branded = True
    return dur, draw


def scene_panel(text, sprite, pal, dur=8.0):
    return F.scene_card(text, sprite, pal, dur)


# ----------------------------------------------------------------- scripts
#
# Each line: (kind, ...). "*word*" is highlighted. The caption (.srt) of each
# scene is its text without the stars.

GIFTS = dict(en=["A coffee", "A vermouth", "A dessert"], es=["Un café", "Un vermut", "Un postre"],
             ca=["Un cafè", "Un vermut", "Unes postres"], it=["Un caffè", "Un vermouth", "Un dolce"])
PLACES = dict(en=["Restaurants", "Bars", "Cafés", "Pizzerias", "Salons", "Tattoo studios"],
              es=["Restaurantes", "Bares", "Cafeterías", "Pizzerías", "Peluquerías", "Tatuajes"],
              ca=["Restaurants", "Bars", "Cafeteries", "Pizzeries", "Perruqueries", "Tatuatges"],
              it=["Ristoranti", "Bar", "Caffè", "Pizzerie", "Parrucchieri", "Tatuatori"])

F1 = {
    "es": [
        ("photo", "Martes, 17:00", "Las mesas puestas. Y no entra *nadie*."),
        ("say", "Cada semana tienes horas así. Y el alquiler lo pagas *igual*.", DARK),
        ("shot", "SocialPerks te enseña *qué horas* se quedan flojas.", "results", NIGHT),
        ("say", "La solución no es más publicidad. Son *tus clientes*.", BLUE),
        ("stories", "Hoy todo el mundo se pasa enlaces. *Stories*, WhatsApp, grupos."),
        ("chapter", "Cómo funciona", "Cuatro pasos. *Nada complicado.*", DARK),
        ("step", 1, "Eliges una hora *floja*. Por ejemplo, el martes por la tarde.", "week-a"),
        ("gifts", 2, "Eliges un *detalle pequeño* que te puedas permitir. Y cuántas plazas."),
        ("step", 3, "Tu cliente escanea tu QR y *comparte* su propio enlace.", "qr-scan"),
        ("story", "En una Story o por WhatsApp, marcado como *publicidad*."),
        ("step", 4, "Su amigo ve la oferta y viene *a esa hora*.", "qr-gift"),
        ("checkin", "En el mostrador te enseña un *código*. Lo escribes y le das el detalle."),
        ("say", "Un regalo, *una vez*. Lo pagas tú, así que tú decides cuál.", BLUE),
        ("chapter", "Qué ves tú", "Todo, desde el *móvil*.", NIGHT),
        ("shot", "Tu QR, con *tu nombre*. Para el mostrador o la bio.", "qr-card", PAPER),
        ("shot", "Te preparamos las *Stories* y los posts.", "content", ROSE),
        ("say", "Ves cada visita registrada y de parte de quién. Tú decides si te *compensa*.", DARK),
        ("grid", "Para *cualquier* local."),
        ("chapter", "Founding Partner", "Creíste en nosotros *antes que nadie*.", BLUE),
        ("say", "Por eso, para ti, *gratis para siempre*.", NIGHT),
        ("compare", ("Los demás locales", "5 %", "de la primera visita de cada cliente nuevo, máx. 3 €"),
                    ("Tú", "0 €", "Ni cuota ni comisión. Para siempre.")),
        ("say", "Lo uses o no, es *tuyo*.", BLUE),
        ("facts", "Sin letra pequeña:", ["Sin tarjeta", "Sin contrato", "Tu enlace no caduca"]),
        ("say", "Queremos crecer con gente *como tú*. Y darte a conocer entre nuestra red de estudiantes de *Esade*.", NIGHT),
        ("start", "Lo activas en *5 minutos*.", ["Abre tu enlace personal", "Rellena los datos del local", "Pon tu QR en el mostrador"]),
        ("say", "¿Dudas? Escríbeme por *WhatsApp*.", BLUE),
        ("end", "Empieza *gratis*.", "Con tu enlace personal.", "Solo para tu local · Sin tarjeta"),
    ],
    "ca": [
        ("photo", "Dimarts, 17:00", "Les taules parades. I no entra *ningú*."),
        ("say", "Cada setmana tens hores així. I el lloguer el pagues *igualment*.", DARK),
        ("shot", "SocialPerks t'ensenya *quines hores* es queden fluixes.", "results", NIGHT),
        ("say", "La solució no és més publicitat. Són els *teus clients*.", BLUE),
        ("stories", "Avui tothom es passa enllaços. *Stories*, WhatsApp, grups."),
        ("chapter", "Com funciona", "Quatre passos. *Res de complicat.*", DARK),
        ("step", 1, "Tries una hora *fluixa*. Per exemple, el dimarts a la tarda.", "week-a"),
        ("gifts", 2, "Tries un *detall petit* que et puguis permetre. I quantes places."),
        ("step", 3, "El teu client escaneja el teu QR i *comparteix* el seu enllaç.", "qr-scan"),
        ("story", "En una Story o per WhatsApp, marcat com a *publicitat*."),
        ("step", 4, "El seu amic veu l'oferta i ve *a aquella hora*.", "qr-gift"),
        ("checkin", "Al taulell t'ensenya un *codi*. L'escrius i li dones el detall."),
        ("say", "Un regal, *una vegada*. El pagues tu, així que tu decideixes quin.", BLUE),
        ("chapter", "Què veus tu", "Tot, des del *mòbil*.", NIGHT),
        ("shot", "El teu QR, amb *el teu nom*. Per al taulell o la bio.", "qr-card", PAPER),
        ("shot", "Et preparem les *Stories* i les publicacions.", "content", ROSE),
        ("say", "Veus cada visita registrada i de part de qui. Tu decideixes si et *compensa*.", DARK),
        ("grid", "Per a *qualsevol* local."),
        ("chapter", "Founding Partner", "Vas creure en nosaltres *abans que ningú*.", BLUE),
        ("say", "Per això, per a tu, *gratis per sempre*.", NIGHT),
        ("compare", ("Els altres locals", "5 %", "de la primera visita de cada client nou, màx. 3 €"),
                    ("Tu", "0 €", "Ni quota ni comissió. Per sempre.")),
        ("say", "L'utilitzis o no, és *teu*.", BLUE),
        ("facts", "Sense lletra petita:", ["Sense targeta", "Sense contracte", "El teu enllaç no caduca"]),
        ("say", "Volem créixer amb gent *com tu*. I donar-te a conèixer entre la nostra xarxa *d'estudiants d'Esade*.", NIGHT),
        ("start", "L'actives en *5 minuts*.", ["Obre el teu enllaç personal", "Omple les dades del local", "Posa el teu QR al taulell"]),
        ("say", "Dubtes? Escriu-me per *WhatsApp*.", BLUE),
        ("end", "Comença *gratis*.", "Amb el teu enllaç personal.", "Només per al teu local · Sense targeta"),
    ],
    "en": [
        ("photo", "Tuesday, 5pm", "Tables set. And *nobody* walks in."),
        ("say", "Every week has hours like this. And the rent is the *same*.", DARK),
        ("shot", "SocialPerks shows you *which hours* stay quiet.", "results", NIGHT),
        ("say", "The answer isn't more ads. It's *your customers*.", BLUE),
        ("stories", "Everybody passes links around today. *Stories*, WhatsApp, group chats."),
        ("chapter", "How it works", "Four steps. *Nothing complicated.*", DARK),
        ("step", 1, "Pick a *quiet* hour. Tuesday afternoon, for example.", "week-a"),
        ("gifts", 2, "Choose a *small gift* you can afford. And how many."),
        ("step", 3, "Your customer scans your QR and *shares* their own link.", "qr-scan"),
        ("story", "In a Story or on WhatsApp, marked as an *ad*."),
        ("step", 4, "Their friend sees the offer and comes *at that hour*.", "qr-gift"),
        ("checkin", "At the counter they show a *code*. You type it in and hand over the gift."),
        ("say", "One gift, *once*. You fund it, so you choose it.", BLUE),
        ("chapter", "What you see", "All of it, on your *phone*.", NIGHT),
        ("shot", "Your QR, with *your name*. For the counter or your bio.", "qr-card", PAPER),
        ("shot", "Your *Stories* and posts, ready made.", "content", ROSE),
        ("say", "You see every recorded visit, and who sent it. You decide if it's *worth it*.", DARK),
        ("grid", "For *any* local business."),
        ("chapter", "Founding Partner", "You believed in us *before anyone else*.", BLUE),
        ("say", "So for you, it's *free for good*.", NIGHT),
        ("compare", ("Other venues", "5%", "of each new guest's first visit, max €3"),
                    ("You", "€0", "No fee, no commission. For good.")),
        ("say", "Use it or not, it's *yours*.", BLUE),
        ("facts", "No small print:", ["No card", "No contract", "Your link never expires"]),
        ("say", "We want to grow with people *like you*, and make you known among our *Esade* student network.", NIGHT),
        ("start", "Set up in *5 minutes*.", ["Open your personal link", "Fill in your venue's details", "Put your QR on the counter"]),
        ("say", "Questions? Message me on *WhatsApp*.", BLUE),
        ("end", "Start *free*.", "With your personal link.", "Only for your venue · No card"),
    ],
}

V1 = {
    "en": [
        ("photo", "Tuesday, 5pm", "Tables set. And *nobody* walks in."),
        ("say", "Quiet hours cost a local business money. *Every week.*", DARK),
        ("shot", "SocialPerks shows you *which hours* stay quiet.", "results", NIGHT),
        ("say", "The answer isn't more ads. It's what *your customers* already do: recommend you.", BLUE),
        ("chapter", "How it works", "Four steps. *Nothing complicated.*", DARK),
        ("step", 1, "Pick a quiet time. *You* decide when the offer runs.", "week-a"),
        ("gifts", 2, "Choose a *small gift* you can afford, and how many. Keep your normal prices."),
        ("step", 3, "Your customer scans your QR and *shares* their own link.", "qr-scan"),
        ("story", "In a Story or a private message, marked as an *ad*."),
        ("say", "Staff check it was *really* shared. Tapping a share button proves nothing.", ROSE),
        ("step", 4, "A friend opens the link and picks an eligible time.", "qr-gift"),
        ("say", "Not every invitation brings someone. The offer is built for your *quiet* slots.", NIGHT),
        ("checkin", "At the counter the friend shows a *code*. Staff type it in."),
        ("panel", "For a new paying guest, staff also note the *amount paid* and the receipt number.", "receipt", PAPER),
        ("say", "That step is manual today: no till integration, no *automatic* check of what was spent.", DARK),
        ("chapter", "What it costs", "*No* monthly fee.", BLUE),
        ("panel", "Up to *5%* of a new guest's first paid visit, net of VAT and refunds. Never more than *€3*.", "fees", PAPER),
        ("facts", "And it can be *less*:", ["Never over 20% of what the visit brings", "Never over your monthly budget", "No evidence, no fee"]),
        ("say", "The gift is *yours* to fund. It costs money even when nobody comes, so keep it small.", DARK),
        ("shot", "Your QR, with *your name*.", "qr-card", PAPER),
        ("shot", "Ready-made *Stories* and posts.", "content", ROSE),
        ("grid", "For *any* local business."),
        ("say", "Judge it on *real* paid visits, real costs and your team's time.", NIGHT),
        ("end", "See it *live*.", "Open the demo. No account.", "socialperkses.com"),
    ],
    "es": [
        ("photo", "Martes, 17:00", "Mesas listas. Y *no entra nadie*."),
        ("say", "Las horas vacías le cuestan dinero a un negocio. *Cada semana.*", DARK),
        ("shot", "SocialPerks te enseña *qué horas* se quedan vacías.", "results", NIGHT),
        ("say", "La respuesta no es más publicidad. Es lo que *tus clientes* ya hacen: recomendarte.", BLUE),
        ("chapter", "Cómo funciona", "Cuatro pasos. *Nada complicado.*", DARK),
        ("step", 1, "Elige una hora tranquila. *Tú* decides cuándo va la oferta.", "week-a"),
        ("gifts", 2, "Elige un *pequeño regalo* que te puedas permitir, y cuántos. Tus precios no cambian."),
        ("step", 3, "Tu cliente escanea tu QR y *comparte* su propio enlace.", "qr-scan"),
        ("story", "En una Story o un mensaje privado, marcado como *publicidad*."),
        ("say", "Publicar no da nada. El regalo es para el amigo que *viene de verdad*.", ROSE),
        ("step", 4, "Un amigo abre el enlace y elige una hora disponible.", "qr-gift"),
        ("say", "No todas las invitaciones traen a alguien. La oferta está pensada para tus horas *tranquilas*.", NIGHT),
        ("checkin", "En el mostrador el amigo enseña un *código*. Recibe el regalo, y quien lo invitó gana uno para otra visita."),
        ("panel", "Por cada cliente nuevo que paga, tu equipo apunta el *importe* y el número de ticket.", "receipt", PAPER),
        ("say", "Ese paso hoy es manual: sin conexión con la caja, sin comprobación *automática* del gasto.", DARK),
        ("chapter", "Lo que cuesta", "*Sin* cuota mensual.", BLUE),
        ("panel", "Hasta un *5 %* de la primera visita pagada de un cliente nuevo, sin IVA ni devoluciones. Nunca más de *3 €*.", "fees", PAPER),
        ("facts", "Y puede ser *menos*:", ["Nunca más del 20 % de lo que deja la visita", "Nunca más de tu presupuesto mensual", "Sin pruebas, no se cobra"]),
        ("say", "El regalo lo pagas *tú*. Cuesta aunque no venga nadie, así que que sea pequeño.", DARK),
        ("shot", "Tu QR, con *tu nombre*.", "qr-card", PAPER),
        ("shot", "*Stories* y posts ya preparados.", "content", ROSE),
        ("grid", "Para *cualquier* negocio de barrio."),
        ("say", "Júzgalo por visitas pagadas *reales*, costes reales y el tiempo de tu equipo.", NIGHT),
        ("end", "Míralo *en vivo*.", "Abre la demo. Sin cuenta.", "socialperkses.com"),
    ],
    "ca": [
        ("photo", "Dimarts, 17:00", "Taules a punt. I *no entra ningú*."),
        ("say", "Les hores buides costen diners a un negoci. *Cada setmana.*", DARK),
        ("shot", "SocialPerks et mostra *quines hores* queden buides.", "results", NIGHT),
        ("say", "La resposta no és més publicitat. És el que *els teus clients* ja fan: recomanar-te.", BLUE),
        ("chapter", "Com funciona", "Quatre passos. *Res de complicat.*", DARK),
        ("step", 1, "Tria una hora tranquil·la. *Tu* decideixes quan va l'oferta.", "week-a"),
        ("gifts", 2, "Tria un *petit regal* que et puguis permetre, i quants. Els teus preus no canvien."),
        ("step", 3, "El teu client escaneja el teu QR i *comparteix* el seu propi enllaç.", "qr-scan"),
        ("story", "En una Story o un missatge privat, marcat com a *publicitat*."),
        ("say", "Publicar no dona res. El regal és per a l'amic que *ve de debò*.", ROSE),
        ("step", 4, "Un amic obre l'enllaç i tria una hora disponible.", "qr-gift"),
        ("say", "No totes les invitacions porten algú. L'oferta està pensada per a les teves hores *tranquil·les*.", NIGHT),
        ("checkin", "Al taulell l'amic ensenya un *codi*. Rep el regal, i qui el va convidar en guanya un per a una altra visita."),
        ("panel", "Per cada client nou que paga, el teu equip apunta l'*import* i el número de tiquet.", "receipt", PAPER),
        ("say", "Aquest pas avui és manual: sense connexió amb la caixa, sense comprovació *automàtica* de la despesa.", DARK),
        ("chapter", "El que costa", "*Sense* quota mensual.", BLUE),
        ("panel", "Fins a un *5 %* de la primera visita pagada d'un client nou, sense IVA ni devolucions. Mai més de *3 €*.", "fees", PAPER),
        ("facts", "I pot ser *menys*:", ["Mai més del 20 % del que deixa la visita", "Mai més del teu pressupost mensual", "Sense proves, no es cobra"]),
        ("say", "El regal el pagues *tu*. Costa encara que no vingui ningú, així que fes-lo petit.", DARK),
        ("shot", "El teu QR, amb *el teu nom*.", "qr-card", PAPER),
        ("shot", "*Stories* i posts ja preparats.", "content", ROSE),
        ("grid", "Per a *qualsevol* negoci de barri."),
        ("say", "Jutja-ho per visites pagades *reals*, costos reals i el temps del teu equip.", NIGHT),
        ("end", "Mira-ho *en directe*.", "Obre la demo. Sense compte.", "socialperkses.com"),
    ],
}

V2 = {
    "en": [
        ("photo", "Tuesday, 5pm", "Your customers know your *next* customers."),
        ("stories", "Pick a quiet time and a small gift. Customers share *their own link*."),
        ("checkin", "Friends show a *code*. Staff confirm the visit and what was paid."),
        ("panel", "*No* monthly fee. Up to 5% of a new guest's first paid visit, max €3.", "fees", PAPER),
        ("end", "You fund the *gift*.", "See it in the demo. No account.", "socialperkses.com"),
    ],
    "es": [
        ("photo", "Martes, 17:00", "Tus clientes conocen a tus *próximos* clientes."),
        ("stories", "Eliges una hora floja y un detalle. Tus clientes comparten *su propio enlace*."),
        ("checkin", "Sus amigos enseñan un *código*. Tu equipo confirma la visita y lo pagado."),
        ("panel", "*Sin* cuota mensual. Hasta un 5 % de la primera visita pagada de un cliente nuevo, máx. 3 €.", "fees", PAPER),
        ("end", "El detalle lo *pagas tú*.", "Míralo en la demo. Sin cuenta.", "socialperkses.com"),
    ],
    "it": [
        ("photo", "Martedì, 17:00", "I tuoi clienti conoscono i tuoi *prossimi* clienti."),
        ("stories", "Scegli un'ora vuota e un omaggio. I clienti condividono *il loro link*."),
        ("checkin", "Gli amici mostrano un *codice*. Lo staff conferma la visita e quanto pagato."),
        ("panel", "*Nessun* canone mensile. Fino al 5% della prima visita pagata di un cliente nuovo, max 3 €.", "fees", PAPER),
        ("end", "L'omaggio lo *paghi tu*.", "Guardalo nella demo. Senza account.", "socialperkses.com"),
    ],
}

L1 = {
    "en": [
        ("chapter", "For Leads", "Earn from the businesses *you know*.", DARK),
        ("say", "Introduce a venue with your *personal link*.", BLUE),
        ("say", "The venue pays *no* monthly fee. Only a capped fee when a new guest pays.", NIGHT),
        ("panel", "You get *20%* of the fees SocialPerks actually collects.", "lead", PAPER),
        ("facts", "Good to know:", ["20% of our fee, not of the bill", "Founding Partners earn nothing", "30-day review, then monthly", "Under €25 carries over"]),
        ("say", "Rights you already signed stay valid. Any change, only *in writing*.", DARK),
        ("say", "New sign-ups are paused for now. Your private panel shows *your* numbers.", BLUE),
        ("end", "Questions? Ask *Emanuel*.", "Your panel, your numbers.", "socialperkses.com"),
    ],
    "es": [
        ("chapter", "Para Leads", "Gana con los locales *que conoces*.", DARK),
        ("say", "Presentas un local con tu *enlace personal*.", BLUE),
        ("say", "El local *no* paga cuota mensual. Solo una comisión con tope cuando paga un cliente nuevo.", NIGHT),
        ("panel", "Te llevas el *20 %* de las comisiones que SocialPerks cobra de verdad.", "lead", PAPER),
        ("facts", "Ten en cuenta:", ["20 % de la comisión, no del ticket", "Los Founding Partners no generan nada", "30 días de revisión, luego cada mes", "Menos de 25 € se acumula"]),
        ("say", "Los derechos que ya firmaste siguen valiendo. Cualquier cambio, solo *por escrito*.", DARK),
        ("say", "Las nuevas altas están en pausa por ahora. Tu panel privado muestra *tus* números.", BLUE),
        ("end", "¿Dudas? Pregunta a *Emanuel*.", "Tu panel, tus números.", "socialperkses.com"),
    ],
    "it": [
        ("chapter", "Per i Lead", "Guadagna con i locali *che conosci*.", DARK),
        ("say", "Presenti un locale con il tuo *link personale*.", BLUE),
        ("say", "Il locale *non* paga canone mensile. Solo una commissione con tetto quando paga un cliente nuovo.", NIGHT),
        ("panel", "Ricevi il *20%* delle commissioni che SocialPerks incassa davvero.", "lead", PAPER),
        ("facts", "Da sapere:", ["20% della commissione, non dello scontrino", "I Founding Partner non generano nulla", "30 giorni di verifica, poi ogni mese", "Sotto i 25 € si accumula"]),
        ("say", "I diritti che hai già firmato restano validi. Ogni cambio, solo *per iscritto*.", DARK),
        ("say", "Le nuove adesioni sono in pausa per ora. Il tuo pannello privato mostra *i tuoi* numeri.", BLUE),
        ("end", "Domande? Chiedi a *Emanuel*.", "Il tuo pannello, i tuoi numeri.", "socialperkses.com"),
    ],
}

SETS = {"F1": F1, "V1": V1, "V2": V2, "L1": L1}
FILES = {
    "F1": "SocialPerks_Founding_Partner_{L}",
    "V1": "SocialPerks_Venue_Explainer_{L}",
    "V2": "SocialPerks_Venue_Short_{L}",
    "L1": "SocialPerks_Lead_Earnings_{L}",
}
SHORT = {"V2"}  # shorter scenes: 35 to 40 seconds in all


# ----------------------------------------------------------------- timeline


def plain(text):
    return text.replace("*", "")


def timeline(kind, lang):
    """The scenes, and for each its caption."""
    out, captions = [], []
    short = kind in SHORT
    step = L["step"][lang]
    for item in SETS[kind][lang]:
        k = item[0]
        if k == "photo":
            out.append(F.scene_photo(item[1], item[2], dur=7.0 if short else 8.0))
            captions.append(f"{item[1]}. {plain(item[2])}")
        elif k == "say":
            out.append(F.scene_say(item[1], item[2]))
            captions.append(plain(item[1]))
        elif k == "chapter":
            out.append(F.scene_chapter(item[1], item[2], item[3]))
            captions.append(f"{item[1]}. {plain(item[2])}")
        elif k == "shot":
            out.append(F.scene_card(item[1], card(lang, item[2], 760 if item[2] == "qr-card" else 880, 0.045), item[3]))
            captions.append(plain(item[1]))
        elif k == "stories":
            sprites = [card(lang, "story-a", 470, 0.075), card(lang, "story-b", 470, 0.075)]
            out.append(K.scene_picture(item[1], sprites, ROSE, 7.5 if short else 7.0, "pair"))
            captions.append(plain(item[1]))
        elif k == "step":
            sprite = phone(lang, item[3], 560) if item[3].startswith("week") else card(lang, item[3], 900)
            out.append(F.scene_step(item[1], step, item[2], sprite, [PAPER, PAPER, BLUE, ROSE][item[1] - 1]))
            captions.append(f"{step} {item[1]}. {plain(item[2])}")
        elif k == "gifts":
            out.append(_gifts(item[1], step, item[2], GIFTS[lang]))
            captions.append(f"{step} {item[1]}. {plain(item[2])}")
        elif k == "story":
            out.append(K.scene_picture(item[1], [card(lang, "story-a", 560, 0.075)], NIGHT, 7.0))
            captions.append(plain(item[1]))
        elif k == "checkin":
            out.append(F.scene_card(item[1], card(lang, "checkin", 820, 0.05, crop_h=1000), DARK, 7.5 if short else 8.0))
            captions.append(plain(item[1]))
        elif k == "panel":
            sprite = {"receipt": receipt, "fees": fees, "lead": lead_money}[item[2]](lang)
            out.append(scene_panel(item[1], sprite, item[3], 9.0 if short else 10.0))
            captions.append(plain(item[1]))
        elif k == "grid":
            out.append(F.scene_grid(item[1], PLACES[lang]))
            captions.append(plain(item[1]))
        elif k == "compare":
            out.append(scene_compare(item[1], item[2]))
            captions.append(f"{item[1][0]}: {item[1][1]} {item[1][2]}. {item[2][0]}: {item[2][1]}. {item[2][2]}")
        elif k == "facts":
            out.append(scene_facts(item[1], item[2], dur=8.0 if len(item[2]) > 3 else 7.0))
            captions.append(plain(item[1]) + " " + " · ".join(item[2]))
        elif k == "start":
            out.append(F.scene_start(item[1], item[2]))
            captions.append(plain(item[1]) + " " + " · ".join(item[2]))
        elif k == "end":
            out.append(F.scene_end(item[1], item[2], item[3], dur=7.0 if short else 9.0))
            captions.append(f"{plain(item[1])} {item[2]} {item[3]}")
        else:
            raise ValueError(k)
    return out, captions


def _gifts(n, label, text, labels):
    """founding_video's three gift photos, with this language's labels."""
    return F.scene_gifts(n, label, text, labels)


def srt(scenes, captions, path):
    def stamp(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    t, rows = 0.0, []
    for i, ((dur, _), text) in enumerate(zip(scenes, captions), 1):
        rows.append(f"{i}\n{stamp(t + 0.3)} --> {stamp(t + dur - 0.1)}\n{text}\n")
        t += dur
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,width,height",
                          "-of", "json", path], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/results")
    ap.add_argument("--only", action="append", help="e.g. F1-es, V2-it")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    jobs = [(k, l) for k, sets in SETS.items() for l in sets]
    if a.only:
        jobs = [(k, l) for k, l in jobs if f"{k}-{l}" in a.only]
    manifest_path = os.path.join(a.out, "manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    for i, (kind, lang) in enumerate(jobs):
        name = FILES[kind].format(L="CAT" if lang == "ca" else lang.upper())
        base = os.path.join(a.out, name)
        scenes, captions = timeline(kind, lang)
        total = K.render_scenes(scenes, base + ".mp4", base + ".jpg", seed=11 + i)
        srt(scenes, captions, base + ".srt")
        info = probe(base + ".mp4")
        manifest[name] = dict(asset=kind, lang=lang, file=name + ".mp4", seconds=round(total, 1),
                              bytes=os.path.getsize(base + ".mp4"), sha256=sha256(base + ".mp4"),
                              streams=[s["codec_name"] for s in info["streams"]], srt=name + ".srt", cover=name + ".jpg")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"{base}.mp4  {total:.1f}s")


if __name__ == "__main__":
    main()
