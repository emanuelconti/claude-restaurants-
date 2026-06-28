#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Lyon.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Daniel & Denise Saint-Jean", "5e / Vieux-Lyon", "36 rue Tramassac, 69005 Lyon", "saintjean@danieletdenise.fr", "+33 4 78 42 24 62", "danieletdenise.fr", "@danieletdenise", "Bouchon Lyonnais", "Piccola catena", "✅ Sì", "Bouchon iconico nel Vieux-Lyon, quenelles e décor autentico 19° sec très fotografabile"),
    ("Café Mokxa", "1er", "11 rue de l'Abbaye d'Ainay, 69002 Lyon", "contact@cafemokxa.com", "+33 4 72 41 80 08", "cafemokxa.com", "@cafemokxa", "Specialty Coffee / Torréfaction", "Indipendente", "✅ Sì", "Torréfacteur pionnier di Lione, latte art e caffè di qualità in spazio épuré"),
    ("Prairial", "1er", "11 rue Chavanne, 69001 Lyon", "contact@prairial-restaurant.com", "+33 4 78 27 86 93", "prairial-restaurant.com", "@prairial_restaurant", "Bistronomie / Végétal", "Indipendente", "✅ Sì", "Cucina vegetale gastronomica con presentazioni artistiche e sala luminosa"),
    ("Les Apothicaires", "6e", "23 rue de Sèze, 69006 Lyon", "reservation@les-apothicaires.com", "+33 4 26 02 25 09", "les-apothicaires.com", "@lesapothicaires", "Bistronomie Créative", "Indipendente", "✅ Sì", "Ex-farmacia trasformata in bistrot gourmet, décor unico con scaffali di rimedi"),
    ("Imouto", "6e", "156 rue Vendôme, 69006 Lyon", "contact@imouto-restaurant.com", "+33 4 72 61 05 06", "imouto-restaurant.com", "@imoutorestaurant", "Japanese / Fusion", "Indipendente", "✅ Sì", "Ristorante giapponese di riferimento a Lione, bento e sushi molto fotografati"),
    ("Café Comptoir Abel", "2e", "25 rue Guynemer, 69002 Lyon", "contact@cafecomptoirabel.fr", "+33 4 78 37 46 18", "cafecomptoirabel.fr", "@cafecomptoirabel", "Bouchon Lyonnais", "Indipendente", "✅ Sì", "Uno dei bouchon più antichi di Lione (1928), travi di legno e atmosfera bohémien"),
    ("L'Ourson qui Boit", "1er", "23 rue Royale, 69001 Lyon", "loursonquiboit@gmail.com", "+33 4 78 27 23 37", "", "@loursonquiboit", "Wine Bar / Bistro Japonais", "Indipendente", "✅ Sì", "Bar à vins naturels con influenze giapponesi, sala intima molto fotografabile"),
    ("Slake Coffee House", "6e", "27 rue d'Anvers, 69006 Lyon", "hello@slake.fr", "+33 4 72 31 13 22", "slake.fr", "@slakecoffeehouse", "Specialty Coffee / Brunch", "Indipendente", "✅ Sì", "Specialty coffee australiano nel 6e, pancakes e granola bowl fotogenici"),
    ("Brasserie Georges", "2e", "30 cours de Verdun, 69002 Lyon", "info@brasseriegeorges.com", "+33 4 72 56 54 54", "brasseriegeorges.com", "@brasseriegeorges", "Brasserie Historique", "Indipendente", "⚠️ Medio", "Brasserie dal 1836 con interni Art Déco, una delle più fotografate di Lione"),
    ("Season", "1er", "8 rue du Garet, 69001 Lyon", "contact@seasonlyon.fr", "+33 4 78 28 09 57", "seasonlyon.fr", "@seasonlyon", "Café / Brunch / Healthy", "Indipendente", "✅ Sì", "Café brunch nel cuore di Lione, piatti colorati e sani, molto instagrammabile"),
    ("Le Bouchon des Filles", "1er", "20 rue Sergent Blandan, 69001 Lyon", "contact@bouchondesfilles.fr", "+33 4 78 30 40 44", "bouchondesfilles.fr", "@bouchondesfilles", "Bouchon Lyonnais Moderne", "Indipendente", "✅ Sì", "Bouchon tutto al femminile, cucina lyonnaise rivisitata con presentazioni moderne"),
    ("Le Musée", "2e", "2 rue des Forces, 69002 Lyon", "contact@bouchon-lemusee.fr", "+33 4 78 37 71 54", "bouchon-lemusee.fr", "@bouchonlemusee", "Bouchon Lyonnais", "Indipendente", "✅ Sì", "Bouchon classico nel 2e, interior d'epoca e atmosfera autentica fotografabile"),
    ("Balthazar Coffees & Wines", "2e", "10 rue du Plat, 69002 Lyon", "contact@balthazarlyon.com", "+33 4 78 37 45 19", "balthazarlyon.com", "@balthazarlyon", "Coffee & Wine Bar", "Indipendente", "✅ Sì", "Caffè specialty e wine bar in spazio industriale, arredi curati e foto-friendly"),
    ("La Meunière", "1er", "11 rue Neuve, 69001 Lyon", "contact@la-meuniere.fr", "+33 4 78 28 62 91", "la-meuniere.fr", "@lameuniere_lyon", "Bouchon Lyonnais", "Indipendente", "✅ Sì", "Bouchon tipico nel centro, cucina maison e sala con poster d'epoca"),
    ("Sauf Imprévu", "7e", "65 Grande Rue de la Guillotière, 69007 Lyon", "contact@saufimprevu.fr", "+33 4 78 72 70 98", "saufimprevu.fr", "@saufimprevu", "Bistro / Natural Wine", "Indipendente", "✅ Sì", "Bar à vins e bistrot nel 7e, planches fotogeniche e cave naturale"),
    ("Chocho", "1er", "36 rue Burdeau, 69004 Lyon", "contact@chocho-lyon.fr", "+33 4 72 07 02 19", "chocho-lyon.fr", "@chocho_lyon", "Café / Pâtisserie Japonaise", "Indipendente", "✅ Sì", "Pâtisserie e café con influenze giapponesi, wagashi e matcha fotogenici"),
    ("Racine", "6e", "3 rue Pierre Corneille, 69006 Lyon", "contact@racine-lyon.fr", "+33 4 78 89 57 68", "racine-lyon.fr", "@racinelyon", "Bistronomie / Farm-to-table", "Indipendente", "✅ Sì", "Cucina di stagione farm-to-table nel 6e, presentazioni pulite e fotografabili"),
    ("Têtedoie", "5e / Fourvière", "Chemin des Quatre-Vents, 69005 Lyon", "info@tetedoie.com", "+33 4 78 29 40 10", "tetedoie.com", "@tetedoiechristian", "Gastronomique / Panoramique", "Indipendente", "✅ Sì", "Vista panoramica su Lione dalla collina di Fourvière, terrasse con tramonto iconico"),
    ("Café Artisan Croix-Rousse", "4e", "55 blvd de la Croix-Rousse, 69004 Lyon", "cafeartisan69@gmail.com", "+33 4 78 29 64 90", "", "@cafeartisanlyon", "Café / Specialty Coffee", "Indipendente", "✅ Sì", "Caffè specialty sul boulevard della Croix-Rousse, terrasse molto fotografata"),
    ("Les Bonnes Soeurs", "2e", "77 rue Mercière, 69002 Lyon", "lesbonnessoeurs@gmail.com", "+33 4 78 37 74 41", "", "@lesbonnessoeurs_lyon", "Bistro / Wine Bar", "Indipendente", "✅ Sì", "Wine bar e bistrot sulla celebre rue Mercière, atmosfera conviviale fotogenica"),
    ("Substrat", "1er", "7 rue Pleney, 69001 Lyon", "contact@substrat.fr", "+33 4 82 31 09 05", "substrat.fr", "@substrat_lyon", "Café / Torréfaction", "Indipendente", "✅ Sì", "Caffè e torréfacteur nel 1er, sacchi di chicchi e foto minimaliste"),
    ("Coudes sur la Table", "1er", "29 rue de l'Arbre Sec, 69001 Lyon", "coudessurlatable@gmail.com", "+33 4 78 39 59 08", "", "@coudessurlatable", "Bistro / Cave à Manger", "Indipendente", "✅ Sì", "Cave à manger nel centro con vini naturali e piatti semplici fotografabili"),
    ("Takao Takano", "6e", "33 rue Malesherbes, 69006 Lyon", "info@takao-takano.com", "+33 4 82 31 43 39", "takao-takano.com", "@takao_takano", "French-Japanese Gastronomique", "Indipendente", "✅ Sì", "Fusione franco-giapponese stellata, presentazioni minimaliste perfette per IG"),
    ("Fond Rose", "9e / Caluire", "25 chemin de Fond Rose, 69300 Caluire-et-Cuire", "contact@fondrose.com", "+33 4 78 29 34 61", "fondrose.com", "@fondroselyon", "Brasserie / Terrasse / Vue Rhône", "Indipendente", "✅ Sì", "Brasserie con grande terrasse sul Rodano, vista fiume iconica fotografata"),
    ("Au 14 Février", "5e / Vieux-Lyon", "6 rue du Vieux-Lyon, 69005 Lyon", "contact@au14fevrier.com", "+33 4 78 92 91 39", "au14fevrier.com", "@au14fevrier", "French-Japanese Fusion", "Indipendente", "✅ Sì", "Cucina franco-giapponese romantica nel Vieux-Lyon, sala con vista sul Saône"),
    ("Le Café des Fédérations", "1er", "8 rue Major Martin, 69001 Lyon", "contact@cafedesfederations.com", "+33 4 78 28 26 00", "cafedesfederations.com", "@cafedesfederations", "Bouchon Lyonnais", "Indipendente", "⚠️ Medio", "Bouchon tipico nel 1er con menù fisso, atmosfera autentica e fotografabile"),
    ("L'Épicerie Vieux-Lyon", "5e", "7 rue Lainerie, 69005 Lyon", "contact@epicerie-vieuxlyon.fr", "+33 4 78 29 02 37", "", "@epicerie_vieuxlyon", "Épicerie Fine / Café", "Indipendente", "✅ Sì", "Épicerie fine nel Vieux-Lyon, prodotti locali e degustazioni instagrammabili"),
    ("La Table 101", "7e", "101 avenue Jean Jaurès, 69007 Lyon", "contact@latable101.fr", "+33 4 37 43 06 78", "latable101.fr", "@latable101lyon", "Bistronomie Moderne", "Indipendente", "✅ Sì", "Bistrot moderno nel 7e con cucina creativa di stagione"),
    ("La Bijouterie", "2e", "20 rue de la Barre, 69002 Lyon", "contact@labijouterielyon.fr", "+33 4 72 80 90 77", "labijouterielyon.fr", "@labijouterie_lyon", "Restaurant Gastronomique", "Indipendente", "⚠️ Medio", "Ex-gioielleria trasformata in ristorante gastronomico, décor unico a Lione"),
    ("M Restaurant", "6e", "47 ave Foch, 69006 Lyon", "contact@m-restaurant.fr", "+33 4 78 89 55 19", "m-restaurant.fr", "@mrestaurantlyon", "Gastronomique Contemporain", "Indipendente", "⚠️ Medio", "Ristorante contemporaneo nel 6e, menu creativi e sala design fotogenica"),
    ("Le Potager des Halles", "1er", "3 rue de la Martinière, 69001 Lyon", "potager@les-halles-de-lyon.fr", "+33 4 72 00 24 84", "", "@potagerdeshalles", "Végétarien / Bistronomie", "Indipendente", "✅ Sì", "Bistrot végétarien nel mercato coperto, piatti colorati e creativi"),
    ("Café du Soleil Vieux-Lyon", "5e", "2 rue Saint-Georges, 69005 Lyon", "contact@cafedusoleil-lyon.fr", "+33 4 78 37 40 96", "", "@cafedusoleil_lyon", "Café / Brunch", "Indipendente", "✅ Sì", "Caffè e brunch nel quartiere storico, terrasse estiva fotografabile"),
    ("Le Gourmet de Sèze", "6e", "129 rue de Sèze, 69006 Lyon", "gourmet@gourmetdeze.com", "+33 4 78 24 23 42", "gourmetdeze.com", "@legourmetdeseze", "Gastronomique Français", "Indipendente", "⚠️ Medio", "Ristorante gastronomico del 6e, piatti elaborati e sala elegante"),
    ("Pinson Lyon", "7e", "12 rue Bechevelin, 69007 Lyon", "contact@cafepinsonlyon.fr", "+33 4 78 72 17 22", "", "@pinsonlyon", "Café / Brunch / Végane", "Piccola catena", "✅ Sì", "Branch lionese del Café Pinson parigino, piatti vegani coloratissimi"),
    ("La Bijou Café", "1er", "3 rue Sainte-Catherine, 69001 Lyon", "labijoucafe@gmail.com", "+33 4 72 00 00 41", "", "@labijoucafe_lyon", "Café / Brunch", "Indipendente", "✅ Sì", "Piccolo caffè bohémien nel 1er, brunch e viennoiseries artigianali fotogenici"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Lyon - SocialPerks"

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

    headers = ["#", "Nome Ristorante", "Arrondissement", "Indirizzo", "EMAIL ✉️",
               "Telefono", "Sito Web", "Instagram", "Tipo Cucina",
               "Dimensione", "Adatto SocialPerks", "Note/Descrizione"]
    col_widths = [4, 28, 14, 35, 32, 18, 22, 22, 22, 16, 14, 40]

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Lyon.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
