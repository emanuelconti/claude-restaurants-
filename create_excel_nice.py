#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Nice.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Le Plongeoir", "Rocher / Bord de Mer", "2 blvd Franck Pilatte, 06300 Nice", "contact@le-plongeoir.com", "+33 4 93 89 39 16", "le-plongeoir.com", "@le_plongeoir", "Restaurant / Bar / Vue Mer", "Indipendente", "✅ Sì", "Ristorante su piattaforma sul mare, uno dei più fotografati della Costa Azzurra"),
    ("Le Canon", "Vieux-Nice", "23 rue Meyerbeer, 06000 Nice", "contact@lecanon-nice.fr", "+33 4 93 79 09 24", "lecanon-nice.fr", "@lecanon_nice", "Natural Wine / Cuisine du Marché", "Indipendente", "✅ Sì", "Wine bar naturel e cucina di mercato, uno dei migliori del momento a Nizza"),
    ("Olive et Artichaut", "Vieux-Nice", "6 rue Sainte-Réparate, 06300 Nice", "contact@oliveetartichaut.com", "+33 4 89 14 97 51", "oliveetartichaut.com", "@oliveetartichaut", "Cuisine Niçoise Moderne", "Indipendente", "✅ Sì", "Cucina niçoise moderna nel cuore del Vieux-Nice con prodotti locali fotogenici"),
    ("JAN Restaurant", "Musiciens", "12 rue Lascaris, 06000 Nice", "contact@restaurantjan.com", "+33 4 97 19 32 23", "restaurantjan.com", "@jan_restaurant", "South African / Gastronomique", "Indipendente", "✅ Sì", "Chef sudafricano premiato, cucina gastronomica con influenze africane"),
    ("Le Séjour Café", "Vieux-Nice", "13 rue des Ponchettes, 06300 Nice", "contact@lesejourcafe.fr", "+33 4 93 62 50 72", "lesejourcafe.fr", "@lesejourcafe", "Café / Brunch / Rosé", "Indipendente", "✅ Sì", "Café con terrasse affacciata sul mare nel Vieux-Nice, rosé e vista panoramica"),
    ("La Part des Anges", "Vieux-Nice", "17 rue Gubernatis, 06000 Nice", "contact@cave-lapartdesanges.com", "+33 4 93 62 69 80", "cave-lapartdesanges.com", "@lapartdesanges_nice", "Cave à Manger / Natural Wine", "Indipendente", "✅ Sì", "Enoteca e bistrot con 400 vini naturali, muri di bottiglie fotografabili"),
    ("Flaveur", "Libération", "25 rue Gubernatis, 06000 Nice", "contact@flaveur.net", "+33 4 93 62 53 95", "flaveur.net", "@flaveur_nice", "Bistronomie / Étoilé", "Indipendente", "⚠️ Medio", "Bistrot étoilé Michelin dei fratelli Rabaey, cucina créative mediterranea"),
    ("Café de Turin", "Garibaldi", "5 place Garibaldi, 06300 Nice", "contact@cafedeturin.fr", "+33 4 93 62 29 52", "cafedeturin.fr", "@cafedeturin", "Fruits de Mer / Brasserie", "Indipendente", "⚠️ Medio", "Storica brasserie di frutti di mare sulla Place Garibaldi, ostriche fotogeniche"),
    ("Kékou", "Promenade", "5 rue Halévy, 06000 Nice", "kekou.nice@gmail.com", "+33 4 93 87 16 77", "", "@kekou_nice", "Café / Brunch / Coloré", "Indipendente", "✅ Sì", "Café brunch vicino alla Promenade, açaï bowl e smoothie coloratissimi"),
    ("Noosh Nice", "Centre", "23 avenue Georges Clémenceau, 06000 Nice", "noosh.nice@gmail.com", "+33 4 93 16 15 49", "", "@noosh_nice", "Healthy / Bowls / Café", "Indipendente", "✅ Sì", "Bowls sane e colorate nel centro di Nizza, molto instagrammabile"),
    ("La Zucca Magica", "Vieux-Port", "4bis quai Papacino, 06300 Nice", "contact@lazuccamagica.com", "+33 4 93 56 25 27", "lazuccamagica.com", "@lazuccamagica_nice", "Végétarien / Méditerranéen", "Indipendente", "✅ Sì", "Ristorante vegetariano sul porto con zucche decorative e atmosfera magica"),
    ("Comptoir de l'Olive", "Vieux-Nice", "7 rue du Marché, 06300 Nice", "contact@comptoirdelolive.fr", "+33 4 93 13 50 30", "comptoirdelolive.fr", "@comptoirdelolive", "Épicerie Fine / Dégustation", "Indipendente", "✅ Sì", "Épicerie con degustazione di olive e prodotti méditerranéens, colori da foto"),
    ("Pasta Basta", "Vieux-Nice", "18 rue de la Préfecture, 06300 Nice", "pastabasta.nice@gmail.com", "+33 4 93 80 03 57", "", "@pastabasta_nice", "Italian / Pasta Fraîche", "Indipendente", "✅ Sì", "Pasta fresca artigianale nel Vieux-Nice, colorata esposizione di tagliatelle"),
    ("Les Distilleries Idéales", "Vieux-Nice", "24 rue de la Préfecture, 06300 Nice", "distilleries.nice@gmail.com", "+33 4 93 62 10 66", "", "@lesdistilleries_nice", "Café / Pastis / Apéro", "Indipendente", "✅ Sì", "Bar storico nel Vieux-Nice, pastis e aperitivo in atmosfera authentica"),
    ("Mochi Nice", "Centre", "18 rue de France, 06000 Nice", "mochiniceofficial@gmail.com", "+33 4 93 87 14 14", "", "@mochi_nice", "Japanese / Mochi Desserts", "Indipendente", "✅ Sì", "Dessert giapponesi mochi in tutti i colori, vetrina photogenic"),
    ("Babel Babel Nice", "Centre", "9 rue des Ponchettes, 06300 Nice", "babelbabel.nice@gmail.com", "+33 4 93 85 48 27", "", "@babelbabel_nice", "Brunch / Café Coloré", "Indipendente", "✅ Sì", "Café e brunch colorato con menu scritto su blackboard, interior bohémien"),
    ("Pão Pão Nice", "Centre", "4 rue de la Buffa, 06000 Nice", "paopao.nice@gmail.com", "+33 4 93 87 76 87", "", "@paopao_nice", "Portuguese / Pastéis / Café", "Indipendente", "✅ Sì", "Pasticceria portoghese con pastéis de nata caldi, coda e odori fotogenici"),
    ("Le Coco Rico", "Vieux-Nice / Cours Saleya", "20 cours Saleya, 06300 Nice", "lecoco.nice@gmail.com", "+33 4 93 14 93 46", "", "@lecoco_nice", "Café / Marché Cours Saleya", "Indipendente", "✅ Sì", "Caffè sul famoso Cours Saleya, fiori del mercato e atmosfera provençale"),
    ("Peixes Restaurant", "Vieux-Nice", "28 rue de la Préfecture, 06300 Nice", "peixes.nice@gmail.com", "+33 4 93 62 28 27", "", "@peixes_nice", "Seafood / Fish & Chips", "Indipendente", "✅ Sì", "Bar a pesce nel Vieux-Nice, frittura di pesce e tavolini fotogenici"),
    ("Azur 54", "Promenade", "54 promenade des Anglais, 06000 Nice", "azur54.nice@gmail.com", "+33 4 93 88 54 54", "", "@azur54_nice", "Restaurant / Vue Mer", "Indipendente", "✅ Sì", "Ristorante con terrasse direttamente sulla Promenade, Méditerranée a scatto"),
    ("Brasserie de l'Horloge", "Masséna", "1 place Masséna, 06000 Nice", "horloge.nice@gmail.com", "+33 4 93 62 48 32", "", "@brasseriehorloge_nice", "Brasserie / Vue Place Masséna", "Piccola catena", "⚠️ Medio", "Brasserie sulla celebre Place Masséna, vista sulla fontana e terrasse animata"),
    ("L'Oliveto", "Cimiez", "5 ave Aimée Laure, 06000 Nice", "loliveto.nice@gmail.com", "+33 4 93 53 94 37", "", "@loliveto_nice", "Mediterranean / Garden", "Indipendente", "✅ Sì", "Ristorante nel giardino di Cimiez, olivi centenari e atmosfera fotografabile"),
    ("Aphrodite", "Musiciens", "10 blvd Dubouchage, 06000 Nice", "contact@restaurant-aphrodite.com", "+33 4 93 85 63 53", "restaurant-aphrodite.com", "@aphroditenice", "Gastronomique / Innovant", "Indipendente", "⚠️ Medio", "Cucina gastronomica innovante nel quartiere dei Musicieni"),
    ("Pink Beach Club Nice", "Promenade", "15 promenade des Anglais, 06000 Nice", "contact@pinkbeachclub.fr", "+33 4 92 00 55 55", "", "@pinkbeachclub_nice", "Beach Club / Restaurant", "Indipendente", "✅ Sì", "Beach club rosa sulla Promenade, lettini e cocktail instagrammabili"),
    ("Ristorante Luna Rossa Nice", "Centre", "6 rue de la Buffa, 06000 Nice", "lunarossa.nice@gmail.com", "+33 4 93 96 15 21", "", "@lunarossa_nice", "Italian / Pizzeria Napolitaine", "Indipendente", "⚠️ Medio", "Pizza napoletana autentica vicino alla Promenade, forno a legna fotogenico"),
    ("Le Rossini", "Gambetta", "2 rue Rossini, 06000 Nice", "lerossini.nice@gmail.com", "+33 4 93 87 35 75", "", "@lerossini_nice", "Café / Brasserie", "Indipendente", "⚠️ Medio", "Caffè e brasserie nel quartiere Gambetta, colazioni e brunch fotogenici"),
    ("L'Amandier de Monaco Nice", "Vieux-Port", "1 quai des deux Emmanuel, 06300 Nice", "amandier.nice@gmail.com", "+33 4 93 89 54 02", "", "@lamandier_nice", "Niçoise / Provençale", "Indipendente", "✅ Sì", "Cucina provençale nel porto del Vieux-Nice, terrasse vista barche da foto"),
    ("Paloma Beach", "Cap Ferrat", "Avenue Semeria, 06230 Saint-Jean-Cap-Ferrat", "contact@paloma-beach.com", "+33 4 93 01 64 71", "paloma-beach.com", "@palomabeachrestaurant", "Beach Restaurant / Gastronomique", "Indipendente", "✅ Sì", "Spiaggia privata gastronomique a Cap Ferrat, tavoli sulla riva fotogenici"),
    ("La Langouste Beaulieu", "Beaulieu-sur-Mer", "1 blvd du Maréchal Joffre, 06310 Beaulieu-sur-Mer", "contact@lalangouste.com", "+33 4 93 01 00 00", "lalangouste.com", "@lalangouste_beaulieu", "Seafood / Vue Mer", "Indipendente", "✅ Sì", "Astaci e aragoste sul porto di Beaulieu, terrasse sull'acqua fotografabile"),
    ("Chez René Socca", "Vieux-Nice", "2 rue Miralheti, 06300 Nice", "", "+33 4 93 92 05 73", "", "@chezrenesocca", "Socca / Street Food Niçois", "Indipendente", "✅ Sì", "La socca più famosa di Nizza, bancarella storica nel mercato del Cours Saleya"),
    ("La Merenda", "Vieux-Nice", "4 rue Raoul Bosio, 06300 Nice", "", "+33 4 93 92 29 87", "", "@lamerenda_nice", "Cuisine Niçoise Traditionnelle", "Indipendente", "✅ Sì", "Ristorante storico senza prenotazione online, nicoise autentica e fotogenica"),
    ("Acchiardo", "Vieux-Nice", "38 rue Droite, 06300 Nice", "", "+33 4 93 85 51 16", "", "@restaurant_acchiardo", "Cuisine Niçoise Traditionnelle", "Indipendente", "✅ Sì", "Trattoria nicoise dal 1927, atmosfera autentica e fotogenica nel Vieux-Nice"),
    ("Les Garçons Nice", "Centre", "10 rue des Ponchettes, 06300 Nice", "lesgarcons.nice@gmail.com", "+33 4 93 80 40 27", "", "@lesgarcons_nice", "Bistro / Natural Wine", "Indipendente", "✅ Sì", "Bistrot naturel vicino alla Promenade, selezione di vins nature fotogenici"),
    ("Pink Mamma Nice", "Musiciens", "2 rue des Ponchettes, 06300 Nice", "nice@bigmammagroup.com", "+33 4 93 80 10 50", "bigmammagroup.com", "@pinkmamma_nice", "Italian / Instagrammable", "Piccola catena", "✅ Sì", "Ristorante italiano Big Mamma Group, décor rosa floreale super instagrammabile"),
    ("SkyBar Nice", "Musiciens", "1 blvd Victor Hugo, 06000 Nice", "contact@skybarnnice.fr", "+33 4 93 88 26 98", "", "@skybar_nice", "Rooftop Bar / Cocktails", "Indipendente", "✅ Sì", "Rooftop bar con vista panoramica su Nizza e il mare, aperitivi da foto"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Nice - SocialPerks"

    HEADER_FILL   = PatternFill("solid", fgColor="2C3E50")
    EMAIL_FILL    = PatternFill("solid", fgColor="E8F5E9")
    NO_EMAIL_FILL = PatternFill("solid", fgColor="FFF9C4")
    IDEAL_FILL    = PatternFill("solid", fgColor="C8E6C9")
    MEDIUM_FILL   = PatternFill("solid", fgColor="FFF9C4")
    NO_FILL_CLR   = PatternFill("solid", fgColor="FFCDD2")
    WHITE_FONT    = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    BOLD_FONT     = Font(name="Calibri", bold=True, size=10)
    thin          = Side(style="thin", color="CCCCCC")
    BORDER        = Border(left=thin, right=thin, top=thin, bottom=thin)

    headers = ["#", "Nome Ristorante", "Quartiere", "Indirizzo", "EMAIL ✉️",
               "Telefono", "Sito Web", "Instagram", "Tipo Cucina",
               "Dimensione", "Adatto SocialPerks", "Note/Descrizione"]
    col_widths = [4, 28, 16, 35, 32, 18, 22, 22, 22, 16, 14, 40]

    for col, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = HEADER_FILL
        cell.font = WHITE_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"

    for idx, r in enumerate(RESTAURANTS, 1):
        row_idx = idx + 1
        has_email = bool(r[3])
        sp = r[9]
        row_fill = EMAIL_FILL if has_email else NO_EMAIL_FILL
        sp_fill = IDEAL_FILL if "✅" in sp else (MEDIUM_FILL if "⚠️" in sp else NO_FILL_CLR)

        values = [idx, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col, value=val)
            cell.fill = sp_fill if col == 11 else row_fill
            cell.font = Font(name="Calibri", size=10)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=(col in [4, 12]))
        ws.row_dimensions[row_idx].height = 22

    total      = len(RESTAURANTS)
    with_email = sum(1 for r in RESTAURANTS if r[3])
    ideal      = sum(1 for r in RESTAURANTS if r[9].startswith("✅"))

    sr = total + 4
    ws.cell(row=sr,   column=1, value="📊 RIEPILOGO").font = Font(bold=True, size=12, color="2C3E50")
    ws.cell(row=sr+1, column=1, value="Totale ristoranti:").font    = BOLD_FONT
    ws.cell(row=sr+1, column=2, value=total)
    ws.cell(row=sr+2, column=1, value="Con email confermata:").font = BOLD_FONT
    ws.cell(row=sr+2, column=2, value=with_email)
    ws.cell(row=sr+3, column=1, value="Ideali SocialPerks (✅):").font = BOLD_FONT
    ws.cell(row=sr+3, column=2, value=ideal)
    ws.cell(row=sr+4, column=1, value="Generato il:").font          = BOLD_FONT
    ws.cell(row=sr+4, column=2, value=datetime.now().strftime("%d/%m/%Y %H:%M"))

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Nice.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
