#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Bordeaux.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("La Tupina", "Saint-Pierre", "6 rue Porte de la Monnaie, 33000 Bordeaux", "contact@latupina.com", "+33 5 56 91 56 37", "latupina.com", "@latupina_bordeaux", "Cuisine Gascon / Traditionnel", "Indipendente", "⚠️ Medio", "Ristorante gastronomico tradizionale di Bordeaux, camino e décor autentico"),
    ("Soléna", "Chartrons", "5 rue Chauffour, 33000 Bordeaux", "contact@solena-bordeaux.fr", "+33 5 56 44 27 54", "solena-bordeaux.fr", "@solena_bordeaux", "Bistronomie / Vins", "Indipendente", "✅ Sì", "Bistrot gastronomique nei Chartrons, cucina créative e selezione vini naturali"),
    ("Miles", "Chartrons", "33 rue du Cancera, 33000 Bordeaux", "contact@miles-bordeaux.com", "+33 5 56 81 18 24", "miles-bordeaux.com", "@miles_bordeaux", "Bistronomie Créative", "Indipendente", "✅ Sì", "Bistrot créatif con presentazioni artistiche, tra i migliori del momento a Bordeaux"),
    ("Racines Bordeaux", "Chartrons", "30 rue Saint-Rémi, 33000 Bordeaux", "racines.bordeaux@gmail.com", "+33 5 56 39 49 15", "", "@racines_bordeaux", "Natural Wine / Bistro", "Indipendente", "✅ Sì", "Bar à vins naturels e cucina di stagione, selezione di produttori biologici"),
    ("Hovenia", "Saint-Pierre", "44 rue des Ayres, 33000 Bordeaux", "contact@hovenia-bordeaux.fr", "+33 5 56 44 35 06", "hovenia-bordeaux.fr", "@hhovenia", "Natural Wine Bar", "Indipendente", "✅ Sì", "Cave à manger naturel nella città vecchia, selezione vini biodinamici fotogenici"),
    ("Le Cheverus Café", "Centre", "1 allée de Chartres, 33000 Bordeaux", "contact@cheveruscafe.fr", "+33 5 56 48 29 73", "cheveruscafe.fr", "@cheveruscafe", "Café / Brunch", "Indipendente", "✅ Sì", "Caffè nel cuore di Bordeaux con terrasse sulla piazza, colazioni fotografabili"),
    ("Symbiose", "Centre", "61 cours d'Alsace-Lorraine, 33000 Bordeaux", "contact@symbiose-bordeaux.fr", "+33 5 56 01 83 31", "symbiose-bordeaux.fr", "@symbiose_bordeaux", "Bistronomie / Vegan-Friendly", "Indipendente", "✅ Sì", "Bistrot bistronomique con menù vegan-friendly, piatti colorati e fotografabili"),
    ("Garopapilles", "Centre", "62 rue l'Abbé de l'Épée, 33000 Bordeaux", "contact@garopapilles.com", "+33 5 56 51 31 14", "garopapilles.com", "@garopapilles", "Cave à Manger / Bistronomie", "Indipendente", "✅ Sì", "Gastronomia e vineria di qualità, presentazioni curate e fotografabili"),
    ("Miss Betsy", "Centre", "16 Place du Palais, 33000 Bordeaux", "missbetsy.bordeaux@gmail.com", "+33 5 57 95 35 95", "", "@missbetsy_bordeaux", "Brunch / Café Américain", "Indipendente", "✅ Sì", "Brunch americano sulla piazza del Palazzo, pancakes e waffles fotogenici"),
    ("Brasserie Bordelaise", "Centre", "50 rue Saint-Rémi, 33000 Bordeaux", "contact@brasserie-bordelaise.fr", "+33 5 56 44 48 95", "brasserie-bordelaise.fr", "@brasseriebordelaise", "Brasserie / Fromages", "Piccola catena", "⚠️ Medio", "Brasserie e fromagerie emblematica di Bordeaux, muri di formaggi fotografabili"),
    ("L'Amer", "Chartrons", "58 rue Notre-Dame, 33000 Bordeaux", "lamer.bordeaux@gmail.com", "+33 5 56 51 99 29", "", "@lamer_bordeaux", "Bar à Vin / Bistro", "Indipendente", "✅ Sì", "Wine bar con cocktails creativi nel quartiere Notre-Dame, muri di mattoni fotogenici"),
    ("La Cagette", "Capucins", "8 rue des Piliers de Tutelle, 33000 Bordeaux", "contact@lacagette-bordeaux.fr", "+33 5 56 52 71 81", "lacagette-bordeaux.fr", "@lacagette_bordeaux", "Épicerie Fine / Café", "Indipendente", "✅ Sì", "Epicerie fine e caffè con prodotti locali, décor rurale instagrammabile"),
    ("La Conserverie Bordeaux", "Chartrons", "60 rue Notre-Dame, 33000 Bordeaux", "laconserverie.bdx@gmail.com", "+33 5 56 11 39 68", "", "@laconserverie_bordeaux", "Épicerie Fine / Cantine", "Indipendente", "✅ Sì", "Conserve artigianali e cantine nel cuore dei Chartrons, colori vivaci fotogenici"),
    ("MOGA", "Centre", "2 rue des Remparts, 33000 Bordeaux", "contact@moga-bordeaux.com", "+33 5 56 81 33 00", "moga-bordeaux.com", "@moga_bordeaux", "Café / Concept Store", "Indipendente", "✅ Sì", "Concept store caffè, moda e arte nel centro storico, ambiente curatoriale"),
    ("Le Café Maritime", "Bassins à Flot", "23 quai des Chartrons, 33300 Bordeaux", "contact@cafemaritime.fr", "+33 5 56 39 42 43", "cafemaritime.fr", "@cafemaritime_bordeaux", "Brasserie / Vue Garonne", "Piccola catena", "⚠️ Medio", "Brasserie moderna sui bassins à flot, terrasse con vista sulle chiuse fotogenica"),
    ("Casa Pepa", "Saint-Michel", "10 place Canteloup, 33000 Bordeaux", "casapepa.bordeaux@gmail.com", "+33 5 56 91 32 21", "", "@casapepa_bordeaux", "Spanish / Tapas", "Indipendente", "✅ Sì", "Tapas spagnole in Place Canteloup nel quartiere Saint-Michel, terrasse pittoresca"),
    ("L'Entrecôte", "Centre", "4 cours du 30 Juillet, 33000 Bordeaux", "contact@entrecote.fr", "+33 5 56 81 76 10", "entrecote.fr", "@lentrecote_bordeaux", "Steak / Bistro", "Piccola catena", "⚠️ Medio", "Bistrot iconico con un solo piatto: entrecôte e patatine fritte in salsa verde"),
    ("Le Petit Commerce", "Saint-Pierre", "22 rue du Parlement Saint-Pierre, 33000 Bordeaux", "contact@lepetitcommerce.fr", "+33 5 56 79 76 58", "lepetitcommerce.fr", "@lepetitcommerce_bordeaux", "Seafood / Fruits de Mer", "Indipendente", "✅ Sì", "Fruits de mer en Vieille Ville, plateau d'huîtres e vista su ruelle médiévale"),
    ("Cabane Ganzul", "Estuaire / Blanquefort", "1 quai Léon Blum, 33290 Blanquefort", "contact@cabaneganzul.fr", "+33 5 56 35 30 62", "cabaneganzul.fr", "@cabaneganzul", "Seafood / Ostréiculteur", "Indipendente", "✅ Sì", "Cabane ostréicole sull'estuario della Gironda, ostriche sul pontile da foto"),
    ("Akashi Bordeaux", "Chartrons", "105 rue du Palais Gallien, 33000 Bordeaux", "akashi.bordeaux@gmail.com", "+33 5 56 67 46 51", "", "@akashi_bordeaux", "Japanese / Sushi", "Indipendente", "✅ Sì", "Sushi di qualità nei Chartrons, nigiri e maki presentati con cura"),
    ("Bar du Boucher", "Saint-Pierre", "8 rue Parlement Saint-Pierre, 33000 Bordeaux", "barduboucher.bdx@gmail.com", "+33 5 56 52 41 71", "", "@barduboucher_bordeaux", "Wine Bar / Charcuterie", "Indipendente", "✅ Sì", "Bar à vins et charcuterie en Vieille Ville, planches fotografabili"),
    ("L'Atelier des Quais", "Bastide", "52 quai de la Souys, 33100 Bordeaux", "contact@atelierdesquais.fr", "+33 5 56 86 26 61", "atelierdesquais.fr", "@atelierdesquais", "Restaurant / Vue Garonne", "Indipendente", "✅ Sì", "Ristorante sulla riva opposta con vista panoramica su Bordeaux e Pont de Pierre"),
    ("Les Halles Bacalan", "Bacalan", "152 quai de Bacalan, 33000 Bordeaux", "contact@hallesbacalan.fr", "+33 5 24 61 88 74", "hallesbacalan.fr", "@hallesbacalan", "Marché Couvert / Food Hall", "Indipendente", "✅ Sì", "Mercato food hall vicino alla Cité du Vin, stand artigiani fotografabili"),
    ("Cent33", "Centre", "133 rue Saint-Rémi, 33000 Bordeaux", "contact@cent33.fr", "+33 5 56 44 55 44", "cent33.fr", "@cent33_bordeaux", "Brunch / Café", "Indipendente", "✅ Sì", "Café brunch nel cuore di Bordeaux, interni luminosi e piatti colorati"),
    ("Cé Moi", "Chartrons", "18 quai des Chartrons, 33000 Bordeaux", "cemoi.bordeaux@gmail.com", "+33 5 56 23 80 48", "", "@cemoi_bordeaux", "Café / Pâtisserie", "Indipendente", "✅ Sì", "Caffè e pasticceria sui quais des Chartrons, torte e vista sul fleuve"),
    ("Le Glouton", "Saint-Michel", "34 rue Sainte-Colombe, 33000 Bordeaux", "contact@leglouton-bordeaux.fr", "+33 5 56 30 00 38", "", "@leglouton_bordeaux", "Bistro / Natural Wine", "Indipendente", "✅ Sì", "Bistrot e cave à manger naturel nel quartiere Saint-Michel"),
    ("Café Belga Bordeaux", "Chartrons", "115 quai des Chartrons, 33000 Bordeaux", "cafebelga.bordeaux@gmail.com", "+33 5 56 50 51 90", "", "@cafebelga_bordeaux", "Café / Brunch / Belge", "Piccola catena", "⚠️ Medio", "Caffè e brunch sur les quais des Chartrons, terrasse con vista Garonna"),
    ("Burdigala Wine Bar", "Centre", "115 rue Georges Bonnac, 33000 Bordeaux", "winebarburdigala@gmail.com", "+33 5 56 90 16 16", "", "@burdigala_wines", "Wine Bar", "Indipendente", "✅ Sì", "Enoteca con selezione premium vini di Bordeaux, design contemporaneo"),
    ("Le Boulier", "Chartrons", "47 rue Notre-Dame, 33000 Bordeaux", "leboulier.bordeaux@gmail.com", "+33 5 56 79 12 93", "", "@leboulier_bordeaux", "Brasserie / Terrasse", "Indipendente", "✅ Sì", "Brasserie con grande terrasse nel quartiere Notre-Dame dei Chartrons"),
    ("Cantine & Sens", "Bastide", "23 quai de la Souys, 33100 Bordeaux", "cantineandsens@gmail.com", "+33 5 56 51 84 21", "", "@cantineandsens", "Café / Healthy / Brunch", "Indipendente", "✅ Sì", "Cantine healthy nella Bastide con terrasse sulla Garonna"),
    ("Chefs de la Cité", "Centre / Bassins", "60 quai des Marques, 33300 Bordeaux", "chefsdelacite.bdx@gmail.com", "+33 5 56 00 23 41", "", "@chefsdelacite_bdx", "Brunch / Healthy / Tendance", "Indipendente", "✅ Sì", "Brunch e cucina healthy con ingredienti locali vicino ai Bassins à Flot"),
    ("Papilles & Pupilles Restaurant", "Chartrons", "19 rue Ausone, 33000 Bordeaux", "contact@papillesenpupilles-restaurant.fr", "+33 5 56 81 29 47", "papillesenpupilles-restaurant.fr", "@papillesenpupilles", "Cave à Manger / Gastronomique", "Indipendente", "✅ Sì", "Ristorante di qualità collegato alla famosa blogzine di vini e cucina"),
    ("Bistrot Belharra", "Capucins", "14 rue de la Devise, 33000 Bordeaux", "bistrotbelharra@gmail.com", "+33 5 56 52 28 36", "", "@bistrotbelharra", "Surf / Basque / Brunch", "Indipendente", "✅ Sì", "Spirito surf e cucina basca nel cuore di Bordeaux, décor maritime fotogenico"),
    ("Le Saint-James", "Bouliac", "3 place Camille Hostein, 33270 Bouliac", "contact@saintjames-bouliac.com", "+33 5 57 97 06 00", "saintjames-bouliac.com", "@lesaintjames_bouliac", "Gastronomique / Vue Bordeaux", "Indipendente", "⚠️ Medio", "Vista panoramica su Bordeaux dall'hotel-ristorante stellato sulle colline"),
    ("Nüfish", "Centre", "4 rue de la Vieille Tour, 33000 Bordeaux", "nufish.bordeaux@gmail.com", "+33 5 57 83 23 48", "", "@nufish_bordeaux", "Japanese / Poke / Sushi", "Piccola catena", "✅ Sì", "Poke bowl e sushi moderni nel centro, colorati e instagrammabili"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Bordeaux - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Bordeaux.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
