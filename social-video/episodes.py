"""What the daily SocialPerks video says, and which day says what.

Every day gets its own video: a kind of place, a format, an opening line, a
closing line and a colour scheme, chosen from the date so the same day always
renders the same video and no two days in a row look alike. The lines are
written to provoke and to sound like a person, never like a brochure. Spanish
is the profile's language (the venues we sell to are in Barcelona); English
is rendered too.

`*words*` mark the highlighted part of a line.
"""

from __future__ import annotations

import datetime as _dt

# The photo a customer of each kind of place really posts, and the place
# itself, as Unsplash ids. The same photographs as the product
# (socialperks: src/assets/stories/CREDITS.json and src/lib/category-images.ts);
# fetched from Unsplash's CDN at render time, so they are not copied here.
STORY_PHOTO = {
    # No faces to camera (the owner, 16 October): the cut from behind, the
    # chair, the massage, the plates, the tape; the same photos as the product.
    "barber": "1648221122323-572c13a31663",
    "salon": "1788985375145-81da8cc731a2",
    "nails": "1772322586702-73125782bd99",
    "gym": "1620188467120-5042ed1eb5da",
    "wellness": "1741522509438-a120c0bb5e88",
    "tattoo_studio": "1564426622559-5af68da63b96",
    "physio": "1706795034887-be9a24d1ac19",
    "hotel": "1641924675896-b6a5aaf64861",
    "restaurant": "1659690402718-ea07d943fd42",
    "bar": "1666282020483-6ebeb210b1c3",
    "cocktail_bar": "1671053805269-48c6c589a269",
    "pizzeria": "1600028068383-ea11a7a101f3",
    "cafe": "1565252556328-92ee4a9a0983",
    "brunch": "1621523133136-cea844f32bdf",
    "ice_cream": "1689001896226-4bacda02550d",
}
PLACE_PHOTO = {
    "barber": "1503951914875-452162b0f3f1",
    "salon": "1633681926022-84c23e8cb2d6",  # the chairs and mirrors, no face (as the product)
    "nails": "1772322586702-73125782bd99",  # the nails themselves: the salon photo is a hairdresser
    "gym": "1534438327276-14e5300c3a48",
    "wellness": "1544161515-4ab6ce6db874",
    "tattoo_studio": "1598371839696-5c5bb00bdc28",
    "physio": "1772122028843-9139d23af4fb",
    "hotel": "1551882547-ff40c63fe5fa",
    "restaurant": "1517248135467-4c7edcad34c4",
    "bar": "1514933651103-005eec06c04b",
    "cocktail_bar": "1514362545857-3bc16c4c7d1b",
    "pizzeria": "1513104890138-7c749659a591",
    "cafe": "1495474472287-4d71bcdd2085",
    "brunch": "1466978913421-dad2ebd01d17",
    "ice_cream": "1497034825429-c343d7c6a68f",
}

# One customer per kind of place, the same people as the product's examples
# (story-examples.ts). `f` is she, `m` is he.
PLACES = {
    "barber": dict(name="Jordi", g="m", handle="jordi.b", tag="@barberborn", venue="Barber Born",
                   es=dict(place="una barbería", gift="un arreglo de barba", unit=("corte", "m"), empty="Sillas vacías", ask="Ese fade, ¿dónde?", wd="martes", hour="16:00", tags="#barberia #barber #fade #barcelona"),
                   en=dict(place="barbershop", gift="a beard trim", unit="haircut", empty="Empty chairs", ask="That fade, where?", wd="Tuesday", hour="4pm", tags="#barber #barbershop #fade #smallbusiness")),
    "salon": dict(name="Irene", g="f", handle="irene.bcn", tag="@studionou", venue="Studio Nou",
                  es=dict(place="una peluquería", gift="una mascarilla capilar", unit=("cita", "f"), empty="Sillas vacías", ask="Pero qué pelazo. ¿Dónde?", wd="miércoles", hour="15:00", tags="#peluqueria #balayage #salon #barcelona"),
                  en=dict(place="hair salon", gift="a hair mask", unit="appointment", empty="Empty chairs", ask="That hair! Where?", wd="Wednesday", hour="3pm", tags="#hairsalon #balayage #salonowner #smallbusiness")),
    "nails": dict(name="Clara", g="f", handle="clara.mp", tag="@nailsbyvera", venue="Nails by Vera",
                  es=dict(place="un centro de uñas", gift="nail art en dos uñas", unit=("manicura", "f"), empty="Mesas vacías", ask="¡Qué uñas! ¿Dónde?", wd="jueves", hour="11:00", tags="#unas #nailart #manicura #barcelona"),
                  en=dict(place="nail studio", gift="nail art on two nails", unit="manicure", empty="Empty tables", ask="Those nails! Where?", wd="Thursday", hour="11am", tags="#nails #nailart #nailtech #smallbusiness")),
    "gym": dict(name="Laia", g="f", handle="laia.fit", tag="@gymgracia", venue="Gym Gràcia",
                es=dict(place="un gimnasio", gift="una clase gratis", unit=("clase", "f"), empty="Clase medio vacía", ask="¿A qué gimnasio vas tú?", wd="lunes", hour="15:00", tags="#gimnasio #fitness #gym #barcelona"),
                en=dict(place="gym", gift="a free class", unit="class", empty="Half-empty class", ask="Which gym is that?", wd="Monday", hour="3pm", tags="#gym #fitness #gymowner #smallbusiness")),
    "wellness": dict(name="Sara", g="f", handle="sara.slow", tag="@spabarna", venue="Spa Barna",
                     es=dict(place="un spa", gift="un masaje craneal", unit=("masaje", "m"), empty="Cabinas vacías", ask="Qué envidia. ¿Qué spa es?", wd="martes", hour="17:00", tags="#spa #bienestar #masaje #barcelona"),
                     en=dict(place="spa", gift="a head massage", unit="massage", empty="Empty treatment rooms", ask="So jealous. Which spa?", wd="Tuesday", hour="5pm", tags="#spa #wellness #selfcare #smallbusiness")),
    "tattoo_studio": dict(name="Marc", g="m", handle="marc.ink", tag="@tintaraval", venue="Tinta Raval",
                          es=dict(place="un estudio de tatuaje", gift="un retoque gratis", unit=("tatuaje", "m"), empty="Camilla vacía", ask="¿Quién te ha hecho eso?", wd="miércoles", hour="12:00", tags="#tatuaje #tattoo #ink #barcelona"),
                          en=dict(place="tattoo studio", gift="a free touch-up", unit="tattoo", empty="Empty chair", ask="Who did that?", wd="Wednesday", hour="noon", tags="#tattoo #tattooartist #ink #smallbusiness")),
    "physio": dict(name="Elena", g="f", handle="elena.runs", tag="@fisiogracia", venue="Fisio Gràcia",
                   es=dict(place="una clínica de fisio", gift="10 minutos extra", unit=("sesión", "f"), empty="Camillas vacías", ask="¿Ya corres otra vez? ¿Quién te trató?", wd="jueves", hour="14:00", tags="#fisioterapia #running #salud #barcelona"),
                   en=dict(place="physio clinic", gift="10 extra minutes", unit="session", empty="Empty tables", ask="Running again? Who fixed you?", wd="Thursday", hour="2pm", tags="#physio #physiotherapy #running #smallbusiness")),
    "hotel": dict(name="Tom", g="m", handle="tom.away", tag="@hotelmarbcn", venue="Hotel Mar",
                  es=dict(place="un hotel", gift="late check-out", unit=("huésped", "m"), empty="Habitaciones vacías", ask="¿Dónde estás? Qué desayuno", wd="domingo", hour="18:00", tags="#hotel #escapada #viajes #barcelona"),
                  en=dict(place="hotel", gift="a late checkout", unit="guest", empty="Empty rooms", ask="Where are you? That breakfast", wd="Sunday", hour="6pm", tags="#hotel #boutiquehotel #travel #smallbusiness")),
    "restaurant": dict(name="Pol", g="m", handle="pol.menja", tag="@taulanova", venue="Taula Nova",
                       es=dict(place="un restaurante", gift="un postre para compartir", unit=("cena", "f"), empty="Mesas vacías", ask="¿Dónde es esa cena?", wd="martes", hour="20:00", tags="#restaurante #foodie #barcelona #hosteleria"),
                       en=dict(place="restaurant", gift="a dessert to share", unit="dinner", empty="Empty tables", ask="Where's that dinner?", wd="Tuesday", hour="8pm", tags="#restaurant #foodie #restaurantowner #smallbusiness")),
    "bar": dict(name="Dani", g="m", handle="dani.bcn", tag="@bodegapepa", venue="Bodega Pepa",
                es=dict(place="un bar", gift="un vermut", unit=("ronda", "f"), empty="Barra vacía", ask="¿Qué bar es ese?", wd="lunes", hour="19:00", tags="#bar #tapas #vermut #barcelona"),
                en=dict(place="bar", gift="a vermouth", unit="round", empty="Empty bar", ask="Which bar is that?", wd="Monday", hour="7pm", tags="#bar #tapas #barowner #smallbusiness")),
    "cocktail_bar": dict(name="Marta", g="f", handle="marta.bcn", tag="@casanou", venue="Casa Nou",
                         es=dict(place="una coctelería", gift="una copa de cava", unit=("copa", "f"), empty="Barra vacía", ask="Ese cóctel, ¿dónde?", wd="miércoles", hour="21:00", tags="#cocteleria #cocktails #barcelona #nightlife"),
                         en=dict(place="cocktail bar", gift="a glass of cava", unit="cocktail", empty="Empty bar", ask="That cocktail, where?", wd="Wednesday", hour="9pm", tags="#cocktailbar #cocktails #mixology #smallbusiness")),
    "pizzeria": dict(name="Giulia", g="f", handle="giulia.eats", tag="@pizzeriaduomo", venue="Pizzeria Duomo",
                     es=dict(place="una pizzería", gift="un tiramisú", unit=("pizza", "f"), empty="Mesas vacías", ask="Esa pizza... ¿dónde?", wd="martes", hour="21:00", tags="#pizza #pizzeria #foodie #barcelona"),
                     en=dict(place="pizzeria", gift="a tiramisù", unit="pizza", empty="Empty tables", ask="That pizza... where?", wd="Tuesday", hour="9pm", tags="#pizza #pizzeria #foodie #smallbusiness")),
    "cafe": dict(name="Pau", g="m", handle="pau.morning", tag="@cafecolomer", venue="Café Colomer",
                 es=dict(place="una cafetería", gift="un café con algo dulce", unit=("café", "m"), empty="Mesas vacías", ask="¿Qué cafetería es?", wd="jueves", hour="16:00", tags="#cafeteria #specialtycoffee #latteart #barcelona"),
                 en=dict(place="café", gift="a coffee and something sweet", unit="coffee", empty="Empty tables", ask="Which café is that?", wd="Thursday", hour="4pm", tags="#coffeeshop #specialtycoffee #latteart #smallbusiness")),
    "brunch": dict(name="Lena", g="f", handle="lena.bcn", tag="@brunchclubbcn", venue="Brunch Club",
                   es=dict(place="un brunch", gift="un zumo natural", unit=("brunch", "m"), empty="Mesas vacías", ask="Ese brunch, ¿dónde?", wd="viernes", hour="11:00", tags="#brunch #foodie #brunchtime #barcelona"),
                   en=dict(place="brunch spot", gift="a fresh juice", unit="brunch", empty="Empty tables", ask="That brunch, where?", wd="Friday", hour="11am", tags="#brunch #brunchtime #foodie #smallbusiness")),
    "ice_cream": dict(name="Ana", g="f", handle="ana.bcn", tag="@gelatimar", venue="Gelati Mar",
                      es=dict(place="una heladería", gift="una bola extra", unit=("helado", "m"), empty="Nadie en la cola", ask="¿De dónde es ese helado?", wd="lunes", hour="17:00", tags="#helado #gelato #heladeria #barcelona"),
                      en=dict(place="ice cream shop", gift="an extra scoop", unit="scoop", empty="No queue", ask="Where's that gelato from?", wd="Monday", hour="5pm", tags="#gelato #icecream #icecreamshop #smallbusiness")),
}

# Appointment businesses come up more often: they are who we sell to first.
CATEGORY_ROTATION = [
    "barber", "salon", "gym", "cafe", "nails", "tattoo_studio", "wellness", "barber",
    "restaurant", "salon", "physio", "bar", "nails", "gym", "cocktail_bar", "tattoo_studio",
    "pizzeria", "salon", "hotel", "brunch", "barber", "ice_cream",
]
APPOINTMENTS = {"barber", "salon", "nails", "gym", "wellness", "tattoo_studio", "physio"}
CHAIRS = {"barber", "salon", "nails", "tattoo_studio"}

FORMATS = ["story", "chat", "numbers", "myth", "pov"]

# (es, en, only these kinds of place or None). {gift}, {wd}, {unit} and
# {empty} are filled from the day's place.
HOOKS = [
    ("Tu mejor anuncio acaba de *salir por la puerta*.", "Your best ad just *walked out the door*.", None),
    ("Nadie se fía de tu anuncio. Todos se fían de *su amiga*.", "Nobody trusts your ad. Everybody trusts *their friend*.", None),
    ("{Wd}, {hour}. {empty}. *¿Te suena?*", "{Wd}, {hour}. {empty}. *Sound familiar?*", None),
    ("Pagas por seguidores que *nunca vienen*.", "You pay for followers who *never show up*.", None),
    ("Tus clientes ya hablan de ti. *Tú no lo ves.*", "Your clients already talk about you. *You just can't see it.*", None),
    ("Un descuento trae gente que se va. Un amigo trae *gente que se queda*.", "A discount brings people who leave. A friend brings *people who stay*.", None),
    ("Deja de *suplicar reseñas*.", "Stop *begging for reviews*.", None),
    ("El boca a boca existe. Solo que *nunca lo medías*.", "Word of mouth is real. You just *never measured it*.", None),
    ("300 € en anuncios o *{gift}*. Tú eliges.", "€300 on ads or *{gift}*. Your call.", None),
    ("Tu cliente tiene 600 amigos. Tú, *un {wd} vacío*.", "Your client has 600 friends. You have *an empty {Wd}*.", None),
    ("La Story de tu cliente vale más que *tu flyer*.", "Your client's Story beats *your flyer*.", None),
    ("No necesitas más seguidores. Necesitas *más {wds} llenos*.", "You don't need more followers. You need *fuller {Wds}*.", None),
    ("¿Y si cada {unit} trajera *{otro} {unit}*?", "What if every {unit} brought *another one*?", None),
    ("Lo más publicado de Instagram sale de *tu silla*.", "The most posted thing on Instagram comes out of *your chair*.", CHAIRS),
    ("Tu cliente ya hizo la foto. Solo faltaba *el enlace*.", "Your client already took the photo. It just needed *a link*.", None),
    ("Los influencers cobran. Tus clientes, *{gift}*.", "Influencers charge fees. Your clients take *{gift}*.", None),
    ("Si no llegan clientes nuevos, *te devolvemos el mes*.", "No new clients? *We refund the month.*", None),
    ("Esto no es una tarjeta de puntos. *Nadie quiere más puntos.*", "This isn't a points card. *Nobody wants more points.*", None),
    ("Tu agenda tiene huecos. Los amigos de tus clientes, *tiempo libre*.", "Your diary has gaps. Your clients' friends have *free time*.", APPOINTMENTS),
    ("El algoritmo no te quiere. *La amiga de tu clienta, sí.*", "The algorithm doesn't love you. *Your client's best friend does.*", None),
    ("Tu mejor comercial *no cobra sueldo*.", "Your best salesperson *isn't on payroll*.", None),
    ("¿Cuánto vale una recomendación? *Menos que un café.*", "What's a recommendation worth? *Less than a coffee.*", None),
    ("Ya tienes clientes que te adoran. *Úsalo.*", "You already have clients who love you. *Use it.*", None),
    ("Un flyer acaba en la basura. *Una Story, en 600 móviles.*", "A flyer ends up in the bin. *A Story lands on 600 phones.*", None),
]

PUNCHES = [
    ("Ellos comparten. *Sus amigos vienen.* Tú lo ves.", "They share. *Their friends come.* You see it."),
    ("Boca a boca que *se puede contar*.", "Word of mouth you can *actually count*."),
    ("Un regalo pequeño. *Amigos de verdad.*", "A small gift. *Real friends.*"),
    ("Llena tus horas flojas con *los amigos de tus clientes*.", "Fill your quiet hours with *your clients' friends*."),
    ("Sin anuncios. Sin descuentos. *Con amigos.*", "No ads. No discounts. *Just friends.*"),
]

CTA = {
    "es": dict(site="socialperkses.com", free="Primera semana gratis", guarantee="Menos de 3 clientes nuevos al mes: te devolvemos el mes."),
    "en": dict(site="socialperkses.com", free="First week free", guarantee="Fewer than 3 new clients a month: we refund the month."),
}

PLURAL_ES = {"lunes": "lunes", "martes": "martes", "miércoles": "miércoles", "jueves": "jueves", "viernes": "viernes", "sábado": "sábados", "domingo": "domingos"}

EPOCH = _dt.date(2026, 10, 17)


def day_number(date: _dt.date) -> int:
    return (date - EPOCH).days


def episode(date: _dt.date) -> dict:
    """Everything the day's video needs, chosen from the date alone."""
    n = day_number(date)
    category = CATEGORY_ROTATION[n % len(CATEGORY_ROTATION)]
    fmt = FORMATS[n % len(FORMATS)]
    # Hooks walk the list with a stride coprime to its length, so every hook
    # comes back only after all the others, and each time with a different
    # kind of place and format.
    stride = 7
    start = (n * stride) % len(HOOKS)
    for step in range(len(HOOKS)):
        es, en, only = HOOKS[(start + step) % len(HOOKS)]
        if only is None or category in only:
            break
    punch = PUNCHES[(n * 3) % len(PUNCHES)]
    return dict(n=n, date=date.isoformat(), category=category, format=fmt, hook=dict(es=es, en=en),
                punch=dict(es=punch[0], en=punch[1]), palette=(n * 2) % 5, guarantee=n % 2 == 0,
                seed=n)


def fill(text: str, category: str, lang: str) -> str:
    p = PLACES[category]
    c = p[lang]
    wd = c["wd"]
    unit = c["unit"]
    if lang == "es":
        word, gender = unit
        values = dict(gift=c["gift"], wd=wd, Wd=wd[:1].upper() + wd[1:], wds=PLURAL_ES[wd], unit=word,
                      otro="otro" if gender == "m" else "otra", empty=c["empty"], hour=c["hour"])
    else:
        values = dict(gift=c["gift"], wd=wd, Wd=wd, Wds=wd + "s", unit=unit, empty=c["empty"], hour=c["hour"])
    out = text
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return out
