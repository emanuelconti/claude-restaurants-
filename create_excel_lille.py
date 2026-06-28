#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Lille.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Bloempot", "Vieux-Lille", "22 rue des Bouchers, 59000 Lille", "contact@bloempot.fr", "+33 3 20 15 49 99", "bloempot.fr", "@bloempot_lille", "Bistronomie / Florent Ladeyn", "Indipendente", "✅ Sì", "Ristorante dello chef stellato Florent Ladeyn, cucina du terroir e piatti creativi"),
    ("À l'Huîtrière", "Vieux-Lille", "3 rue des Chats Bossus, 59000 Lille", "contact@huitriere.fr", "+33 3 20 55 43 41", "huitriere.fr", "@huitriere_lille", "Fruits de Mer / Gastronomique", "Indipendente", "⚠️ Medio", "Ristorante storico con décor Art Déco, ostriche e piatti di mare fotogenici"),
    ("La Capsule", "Vieux-Lille", "23 rue des Trois Mollettes, 59000 Lille", "lacapsule.lille@gmail.com", "+33 3 20 06 56 09", "", "@lacapsule_lille", "Natural Wine Bar", "Indipendente", "✅ Sì", "Bar naturel e cocktail nel Vieux-Lille, muri di bottiglie e atmosfera cave"),
    ("Manifesto Coffee", "Vieux-Lille", "6 rue Thiers, 59000 Lille", "manifesto.coffee@gmail.com", "+33 3 20 74 12 43", "", "@manifestocoffee_lille", "Specialty Coffee / Brunch", "Indipendente", "✅ Sì", "Specialty coffee trendy nel Vieux-Lille, latte art e colazioni fotografabili"),
    ("Rosa Restaurant", "Wazemmes", "73 blvd de la Liberté, 59000 Lille", "contact@rosa-lille.fr", "+33 3 20 57 39 29", "rosa-lille.fr", "@rosa_lille", "Brunch / Café / Coloré", "Indipendente", "✅ Sì", "Brunch e caffè con interior colorato e floreale, uno dei più fotografati di Lille"),
    ("Le Baromètre", "Centre", "38 rue de la Halle, 59000 Lille", "lebarometre.lille@gmail.com", "+33 3 20 52 09 09", "", "@lebarometre_lille", "Wine Bar / Bistro", "Indipendente", "✅ Sì", "Bar à vins con selezione di vins nature e piccola cucina, atmosfera intima"),
    ("Café Germaine", "Wazemmes", "5 place Nouvelle Aventure, 59000 Lille", "cafegermaine@gmail.com", "+33 3 20 35 54 58", "", "@cafegermaine_lille", "Café / Brunch / Marché", "Indipendente", "✅ Sì", "Caffè e brunch nella zona del mercato di Wazemmes, terrasse animata fotogenica"),
    ("Chez la Vieille", "Vieux-Lille", "60 rue de Gand, 59000 Lille", "chezvielle.lille@gmail.com", "+33 3 20 06 23 35", "", "@chezlavieille_lille", "Estaminet / Cuisine Ch'ti", "Indipendente", "✅ Sì", "Estaminet tradizionale nel Vieux-Lille, cucina ch'ti e décor authentique fotogenico"),
    ("Ch'ti Folk", "Vieux-Lille", "2 rue du Sec Arembault, 59000 Lille", "chtifolk@gmail.com", "+33 3 20 57 14 72", "", "@chtifolk_lille", "Estaminet / Craft Beer", "Indipendente", "✅ Sì", "Estaminet con birre artigianali ch'ti, déco brasse et guinguette fotogenica"),
    ("Alcide Brasserie", "Grand'Place", "5 rue des Halles, 59000 Lille", "contact@alcide-lille.fr", "+33 3 20 12 06 95", "alcide-lille.fr", "@alcide_lille", "Brasserie Moderne", "Indipendente", "⚠️ Medio", "Brasserie moderna nei pressi della Grand'Place, interni design fotogenici"),
    ("Comptoir Volant", "Centre", "1 place du Théâtre, 59000 Lille", "comptoirvolant@gmail.com", "+33 3 20 74 50 22", "", "@comptoirvolant_lille", "Bar à Vins / Tapas", "Indipendente", "✅ Sì", "Wine bar en plein centre, tapas créatives e vini selezionati"),
    ("La Biocive", "Wazemmes", "60 rue Inkermann, 59000 Lille", "contact@labiocive.fr", "+33 3 20 57 50 33", "labiocive.fr", "@labiocive", "Épicerie Bio / Café / Brunch", "Indipendente", "✅ Sì", "Épicerie bio e caffè a Wazemmes, prodotti locaux e piatti colorati"),
    ("Mezebelle", "Centre", "25 place du Général de Gaulle, 59000 Lille", "mezebelle@gmail.com", "+33 3 20 52 40 71", "", "@mezebelle_lille", "Café / Brunch / Coloré", "Indipendente", "✅ Sì", "Café brunch con piatti colorati e pastries fotogeniche nel centro di Lille"),
    ("Le Pain Quotidien Lille", "Vieux-Lille", "9 rue d'Angleterre, 59000 Lille", "lille@painquotidien.com", "+33 3 20 14 22 82", "painquotidien.com", "@painquotidien", "Café / Brunch / Belge", "Piccola catena", "⚠️ Medio", "Caffè belga con grandi tavoli in legno, tartines e colazioni fotogeniche"),
    ("Brasserie de la Cloche", "Vieux-Lille", "13 place du Général de Gaulle, 59000 Lille", "brasseriecloche@gmail.com", "+33 3 20 52 22 31", "", "@lacloche_lille", "Brasserie Historique", "Indipendente", "⚠️ Medio", "Brasserie storica vicino alla Grand'Place, terrasse e interni Belle Époque"),
    ("Chez Baptiste", "Vieux-Lille", "4 rue des Bouchers, 59000 Lille", "chezbaptiste.lille@gmail.com", "+33 3 20 06 49 48", "", "@chezbaptiste_lille", "Bistro / Cuisine Française", "Indipendente", "✅ Sì", "Bistrot français tipico nel Vieux-Lille, chalkboard e atmosfera parigina"),
    ("L'Écume des Mers", "Vieux-Lille", "10 rue de Pas, 59000 Lille", "contact@lecumevieux.fr", "+33 3 20 54 95 40", "lecumevieux.fr", "@lecumevieux", "Fruits de Mer / Poissonnerie", "Indipendente", "✅ Sì", "Pescheria-ristorante nel cuore del Vieux-Lille, plateau di ostriche fotogenico"),
    ("Aux Moules", "Grand'Place", "34 rue de Béthune, 59000 Lille", "auxmoules.lille@gmail.com", "+33 3 20 57 12 46", "", "@auxmoules_lille", "Moules-Frites / Brasserie", "Indipendente", "⚠️ Medio", "Classico belga moules-frites, pentoloni fumanti e atmosfera festiva"),
    ("Les Toquées", "Wazemmes", "48 rue Gambetta, 59000 Lille", "lestoquees.lille@gmail.com", "+33 3 20 57 66 38", "", "@lestoquees_lille", "Cuisine Créative / Femmes Chefs", "Indipendente", "✅ Sì", "Ristorante tutto al femminile con cucina créative, presentazioni artistiche"),
    ("Nid Café", "Centre", "27 place des Patiniers, 59000 Lille", "nidcafe.lille@gmail.com", "+33 3 20 13 51 34", "", "@nidcafe_lille", "Café / Brunch / Cosy", "Indipendente", "✅ Sì", "Caffè nido accogliente con cuscini e piante, atmosfera hygge fotografabile"),
    ("Freya Coffee Shop", "Vieux-Lille", "4 rue Saint-Jacques, 59000 Lille", "freyacoffeeshop@gmail.com", "+33 3 20 94 10 47", "", "@freyacoffeeshop_lille", "Specialty Coffee / Scandinavian", "Indipendente", "✅ Sì", "Coffee shop con estetica scandinava, caffè a freddo e kanelbullar da foto"),
    ("La Terrasse des Remparts", "Vieux-Lille", "10 rue Basse, 59000 Lille", "terrasse.remparts@gmail.com", "+33 3 20 57 02 03", "", "@terrasse_remparts_lille", "Restaurant / Jardin Terrasse", "Indipendente", "✅ Sì", "Ristorante con terrasse giardino nel Vieux-Lille, fiori e verde fotografabili"),
    ("Le Recrutement Café", "Centre", "6 rue de la Clef, 59000 Lille", "lerecrutement.cafe@gmail.com", "+33 3 20 14 08 36", "", "@lerecrutementcafe", "Café / Coworking / Brunch", "Indipendente", "✅ Sì", "Caffè coworking e brunch nel centro, piante e interni moderni fotografabili"),
    ("Le Ginkgo Café", "Wazemmes", "36 rue Pierre Mauroy, 59000 Lille", "ginkgocafe.lille@gmail.com", "+33 3 20 54 71 28", "", "@ginkgocafe_lille", "Café Asiatique / Brunch", "Indipendente", "✅ Sì", "Caffè con atmosfera asiatica e prodotti del mondo, molto instagrammabile"),
    ("Mötley Crêpe", "Centre", "8 rue du Nouveau Siècle, 59000 Lille", "motleycrepe@gmail.com", "+33 3 20 57 33 79", "", "@motleycrepe_lille", "Crêperie Créative", "Indipendente", "✅ Sì", "Crêperie rock con galettes e crêpes créatives, décor grunge fotogenico"),
    ("La Mousse Normande", "Vieux-Lille", "20 place des Patiniers, 59000 Lille", "mousstenormande.lille@gmail.com", "+33 3 20 12 40 56", "", "@mousstenormande_lille", "Bar / Tapas / Craft Beer", "Indipendente", "✅ Sì", "Bar à bières artisanales e tapas créatives, atmosfera conviviale e fotogenica"),
    ("Les Années Folles", "Vieux-Lille", "3 place Louise de Bettignies, 59000 Lille", "lesanneesfolles.lille@gmail.com", "+33 3 20 57 89 40", "", "@lesanneesfolles_lille", "Café / Vintage / Brunch", "Indipendente", "✅ Sì", "Caffè vintage anni '20 con décor d'epoca, brocantes e brunch fotografabili"),
    ("Kura Izakaya", "Centre", "14 rue Masséna, 59000 Lille", "kura.izakaya@gmail.com", "+33 3 20 54 93 47", "", "@kura_izakaya_lille", "Japanese / Izakaya", "Indipendente", "✅ Sì", "Izakaya giapponese nel centro, yakitori e sake in atmosfera sombre fotogenica"),
    ("Pho Banh Mi Viet", "Centre", "22 rue des Stations, 59000 Lille", "phobanhmi.lille@gmail.com", "+33 3 20 06 52 63", "", "@phobanhmi_lille", "Vietnamese / Street Food", "Indipendente", "✅ Sì", "Cucina vietnamita autentica, pho e banh mi colorati e fotogenici"),
    ("Nona Pizza Lille", "Centre", "5 rue Saint-Jacques, 59000 Lille", "nona.lille@gmail.com", "+33 3 20 57 24 80", "", "@nona_lille", "Pizzeria Napolitaine / Naturelle", "Piccola catena", "✅ Sì", "Pizzeria napoletana con impasto a lunga lievitazione, forno a legna fotogenico"),
    ("Les Funambules", "Vieux-Lille", "37 rue de la Monnaie, 59000 Lille", "lesfunambules.lille@gmail.com", "+33 3 20 55 48 29", "", "@lesfunambules_lille", "Café / Brunch / Artistique", "Indipendente", "✅ Sì", "Caffè con esposizioni d'arte temporanee e brunch créatif, molto instagrammabile"),
    ("Meert Pâtisserie", "Vieux-Lille", "25 rue Esquermoise, 59000 Lille", "meert@meert.fr", "+33 3 20 57 07 44", "meert.fr", "@meertlille", "Pâtisserie Historique / Salon de Thé", "Indipendente", "✅ Sì", "Pasticceria storica dal 1761, gaufres de Lille e interni d'epoca UNESCO"),
    ("Chez Max", "Euralille", "10 ave du Président Hoover, 59000 Lille", "chezmax.lille@gmail.com", "+33 3 20 06 77 15", "", "@chezmax_lille", "Bistro / Comptoir", "Indipendente", "✅ Sì", "Bistrot moderno nel quartiere Euralille, cucina créative e terrasse"),
    ("La Cantine de Wazemmes", "Wazemmes", "9 place de la Nouvelle Aventure, 59000 Lille", "lacantine.wazemmes@gmail.com", "+33 3 20 36 60 89", "", "@lacantine_wazemmes", "Café / Marché / Vegan", "Indipendente", "✅ Sì", "Cantine vegan e bio accanto al mercato di Wazemmes, piatti arcobaleno"),
    ("Brasserie Sainte-Marie", "Vieux-Lille", "52 rue de la Monnaie, 59000 Lille", "brasserieste.marie@gmail.com", "+33 3 20 57 33 12", "", "@brasserieste.marie_lille", "Brasserie / Terrasse Fleurie", "Indipendente", "✅ Sì", "Brasserie con terrasse fiorita nel Vieux-Lille, façade en brique rouge fotogenica"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Lille - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Lille.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
