#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Strasbourg.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Chez Yvonne", "Petite France", "10 rue du Sanglier, 67000 Strasbourg", "contact@chez-yvonne.net", "+33 3 88 32 84 15", "chez-yvonne.net", "@chezyvonne_strasbourg", "Winstub / Alsacien", "Indipendente", "✅ Sì", "Winstub storico preferito di Jacques Chirac, décor alsacien autenticamente fotogenico"),
    ("Maison Kammerzell", "Grande Île", "16 place de la Cathédrale, 67000 Strasbourg", "contact@maison-kammerzell.com", "+33 3 88 32 42 14", "maison-kammerzell.com", "@maisonkammerzell", "Alsacien / Gastronomique", "Indipendente", "✅ Sì", "Casa gotica rinascimentale del 1427, la più fotografata di Strasburgo"),
    ("Le Tire-Bouchon", "Grande Île", "5 rue des Tailleurs de Pierre, 67000 Strasbourg", "contact@letire-bouchon.fr", "+33 3 88 22 16 32", "letire-bouchon.fr", "@letirebouchon_str", "Winstub / Alsacien Moderne", "Indipendente", "✅ Sì", "Winstub con cucina alsaziana moderna, ambiente caldo e molto fotogenico"),
    ("Au Pont Corbeau", "Grande Île", "21 quai Saint-Nicolas, 67000 Strasbourg", "contact@pontcorbeau.com", "+33 3 88 35 60 68", "pontcorbeau.com", "@pontcorbeau_str", "Winstub / Vue Canal", "Indipendente", "✅ Sì", "Winstub sul canale dell'Ill con vista sulle case alsaziane, terrasse fotogenica"),
    ("1741 Strasbourg", "Neustadt", "22 rue du Fossé des Tanneurs, 67000 Strasbourg", "contact@1741.fr", "+33 3 88 35 50 50", "1741.fr", "@1741strasbourg", "Gastronomique / Cave", "Indipendente", "⚠️ Medio", "Ristorante gastronomico in cantina del 18° sec, votato migliore d'Alsazia"),
    ("Café des Anges", "Krutenau", "5 rue Sainte-Catherine, 67000 Strasbourg", "cafeanges.str@gmail.com", "+33 3 88 37 12 67", "", "@cafedesanges_str", "Café / Bar / Brunch", "Indipendente", "✅ Sì", "Caffè e bar bohémien nel Krutenau, terrasse animata e atmosfera studentesca"),
    ("La Corde à Linge", "Grande Île", "2 place Benjamin Zix, 67000 Strasbourg", "contact@lacordealinge.com", "+33 3 88 21 02 05", "lacordealinge.com", "@lacordealinge", "Winstub / Vue Petite France", "Indipendente", "✅ Sì", "Winstub nella Petite France con vista sui canali, terrasse iconicamente fotogenica"),
    ("Au Bain Marie", "Neustadt", "7 rue des Orfèvres, 67000 Strasbourg", "aubainmarie.str@gmail.com", "+33 3 88 23 55 34", "", "@aubainmarie_str", "Épicerie Fine / Traiteur / Café", "Indipendente", "✅ Sì", "Épicerie fine e caffè con prodotti alsaziani, marmellate e terrines fotografabili"),
    ("Café Bretelles", "Krutenau", "24 rue du Faubourg de Pierre, 67000 Strasbourg", "cafebretelles@gmail.com", "+33 3 88 35 54 71", "", "@cafebretelles_str", "Specialty Coffee / Brunch", "Indipendente", "✅ Sì", "Specialty coffee e brunch nel Krutenau, latte art e colazioni fotogeniche"),
    ("L'Épicerie Strasbourg", "Grande Île", "6 rue du Vieux Marché aux Poissons, 67000 Strasbourg", "epicerie.str@gmail.com", "+33 3 88 32 09 32", "", "@epicerie_str", "Épicerie / Vins / Traiteur", "Indipendente", "✅ Sì", "Épicerie fine in casa alsaziana, prodotti régionaux e décor charme fotogenico"),
    ("La Cambuse", "Petite France", "1 rue des Dentelles, 67000 Strasbourg", "lacambuse.str@gmail.com", "+33 3 88 22 15 22", "", "@lacambuse_str", "Bar / Cave à Vins / Tapas", "Indipendente", "✅ Sì", "Cave à manger nella Petite France, muri di pietra e vini alsaziani fotogenici"),
    ("Le Festin de Babette", "Neustadt", "5 rue des Juifs, 67000 Strasbourg", "festindebabette@gmail.com", "+33 3 88 32 11 39", "", "@festindebabette_str", "Bistro / Cuisine d'Exception", "Indipendente", "✅ Sì", "Bistrot gourmet in vicolo storico, menu ardesia e sala intima fotogenica"),
    ("Au Crocodile", "Grande Île", "10 rue de l'Outre, 67000 Strasbourg", "contact@aucrocodile.com", "+33 3 88 32 13 02", "aucrocodile.com", "@aucrocodile_str", "Gastronomique / Historique", "Indipendente", "⚠️ Medio", "Ristorante storico con coccodrillo imbalsamato appeso, décor iconico"),
    ("L'Atelier du Goût", "Krutenau", "38 rue du Fossé des Treize, 67000 Strasbourg", "ateliergoût.str@gmail.com", "+33 3 88 36 95 10", "", "@atelierdugoût_str", "Bistronomie / Créatif", "Indipendente", "✅ Sì", "Bistrot créatif nel Krutenau, presentazioni artistiche e vini naturali"),
    ("Umami Strasbourg", "Neustadt", "8 rue des Francs-Bourgeois, 67000 Strasbourg", "umami.str@gmail.com", "+33 3 88 24 80 12", "", "@umami_str", "Japanese / Asian Fusion", "Indipendente", "✅ Sì", "Cucina giapponese-asiatica nella Neustadt, ramen e bowls colorati fotogenici"),
    ("Ristorante Marco Polo", "Grande Île", "4 rue du Vieux Seigle, 67000 Strasbourg", "marcopolo.str@gmail.com", "+33 3 88 32 29 27", "", "@marcopolo_str", "Italian / Trattoria", "Indipendente", "✅ Sì", "Trattoria italiana in vicolo medioevale, pizza nel forno a legna e décor rustico"),
    ("Le Table d'Étude", "Krutenau", "15 quai des Bateliers, 67000 Strasbourg", "tabledetude@gmail.com", "+33 3 88 36 22 17", "", "@tabledetude_str", "Bistro / Vue Ill", "Indipendente", "✅ Sì", "Bistrot con vista sull'Ill nel quartiere universitario Krutenau"),
    ("Café Atlantico Strasbourg", "Neustadt", "12 blvd du Président Wilson, 67000 Strasbourg", "atlantico.str@gmail.com", "+33 3 88 22 54 32", "", "@cafeatlantico_str", "Café / Latin / Brunch", "Indipendente", "✅ Sì", "Caffè latinoamericano e brunch colorato nella Neustadt, piante tropicali"),
    ("La Hache à Maman", "Krutenau", "20 rue du Faubourg de Pierres, 67000 Strasbourg", "lhacheamaman@gmail.com", "+33 3 88 35 54 20", "", "@lhacheamaman_str", "Burger Gourmet / Brunch", "Indipendente", "✅ Sì", "Burger gourmet e brunch nel Krutenau, brioche fotogeniche e ingredienti locaux"),
    ("La Winstub de la Petite France", "Petite France", "5 rue du Bain aux Plantes, 67000 Strasbourg", "winstubpetitefrce@gmail.com", "+33 3 88 22 68 10", "", "@winstubpetitefrance", "Winstub / Vue Canaux", "Indipendente", "✅ Sì", "Winstub con vista diretta sui canali e case a graticcio, angolo da cartolina"),
    ("Les Haras Restaurant", "Grande Île", "23 rue des Glacières, 67000 Strasbourg", "contact@les-haras.com", "+33 3 88 24 00 00", "les-haras.com", "@lesharas_str", "Brasserie / Lieu Patrimonial", "Indipendente", "✅ Sì", "Brasserie negli ex-haras imperiaux del 18° sec, archi e briques rouges fotogenici"),
    ("Umami Bio Strasbourg", "Neustadt", "22 rue de la Nuée Bleue, 67000 Strasbourg", "umamibio.str@gmail.com", "+33 3 88 23 67 45", "", "@umamibio_str", "Healthy / Bio / Vegan", "Indipendente", "✅ Sì", "Cucina bio e vegan nel cuore della Neustadt, bowls arcobaleno fotografabili"),
    ("Murano Strasbourg", "Grande Île", "7 rue de la Mésange, 67000 Strasbourg", "murano.str@gmail.com", "+33 3 88 15 62 47", "", "@murano_str", "Italian / Fine Dining", "Indipendente", "⚠️ Medio", "Ristorante italiano fine dining nel centro, pasta fresca e vetri di Murano"),
    ("L'Alsace à Table", "Grande Île", "10 rue des Frères, 67000 Strasbourg", "alsace.atable@gmail.com", "+33 3 88 36 17 81", "", "@alsaceatable_str", "Alsacien Traditionnel", "Indipendente", "⚠️ Medio", "Cucina alsaziana tradizionale in cava medievale, choucroute e cervelas"),
    ("Comptoir de l'Ill", "Grande Île", "3 rue de l'Ill, 67000 Strasbourg", "comptoirdell.str@gmail.com", "+33 3 88 32 19 49", "", "@comptoirdell_str", "Café / Brunch / Vue Canal", "Indipendente", "✅ Sì", "Caffè e brunch con vista sull'Ill, terrasse fiorita molto instagrammabile"),
    ("Winstub Zum Strissel", "Grande Île", "5 place de la Grande Boucherie, 67000 Strasbourg", "strissel@strissel.fr", "+33 3 88 32 14 73", "strissel.fr", "@strissel_str", "Winstub / Cave à Vins", "Indipendente", "⚠️ Medio", "Winstub storico con la più grande cave à vins d'Alsazia, ambiance autentique"),
    ("Au Renard Prêchant", "Grande Île", "38 rue du Vieux Marché aux Vins, 67000 Strasbourg", "renardprechant@gmail.com", "+33 3 88 32 62 49", "", "@renardprechant_str", "Bar à Vins / Cave", "Indipendente", "✅ Sì", "Bar à vins alsaziani in cantina del 17° sec, bottiglie a vista fotogeniche"),
    ("La Petite Venise Alsacienne", "Petite France", "8 rue du Bain aux Plantes, 67000 Strasbourg", "petitevenise.str@gmail.com", "+33 3 88 24 00 23", "", "@petitevenise_str", "Restaurant / Vue Canaux", "Indipendente", "✅ Sì", "Ristorante sulla piccola Venezia alsaziana, riflessi dei canali fotogenici"),
    ("Brasserie Gallia", "Krutenau", "15 quai Turckheim, 67000 Strasbourg", "brasserie.gallia@gmail.com", "+33 3 88 36 44 67", "", "@brasseriegallia_str", "Craft Beer / Brasserie", "Indipendente", "✅ Sì", "Brasserie artigianale alsaziana con tour della fabbrica, pinte fotogeniche"),
    ("Le Renommée", "Neustadt", "6 rue de la Division Leclerc, 67000 Strasbourg", "larenommee.str@gmail.com", "+33 3 88 32 78 91", "", "@larenommee_str", "Café / Brasserie Art Nouveau", "Indipendente", "✅ Sì", "Brasserie stile Art Nouveau nella Neustadt, interni d'epoca fotografabili"),
    ("Kobus & Co", "Neustadt", "6 place de la République, 67000 Strasbourg", "kobusandco@gmail.com", "+33 3 88 32 91 30", "", "@kobusandco_str", "Café / Brunch / Colorfull", "Indipendente", "✅ Sì", "Caffè e brunch sulla Place de la République, colazioni colorate e fotogeniche"),
    ("L'Épicurien", "Krutenau", "27 quai des Pêcheurs, 67000 Strasbourg", "lepicurien.str@gmail.com", "+33 3 88 36 00 96", "", "@lepicurien_str", "Bistro / Terasse Loire", "Indipendente", "✅ Sì", "Bistrot sul lungofiume con terrasse sul Ill, aperitivi al tramonto fotogenici"),
    ("Strasbourg by Night", "Grande Île", "12 place du Marché Gayot, 67000 Strasbourg", "strasbourgbynight@gmail.com", "+33 3 88 32 14 22", "", "@strasbourgbynight_str", "Bar / Cocktails / Vue Cathédrale", "Indipendente", "✅ Sì", "Bar con terrasse con vista diretta sulla Cathédrale illuminata, foto iconica"),
    ("Le Caveau Gurtlerhoft", "Grande Île", "1 place des Tripiers, 67000 Strasbourg", "contact@gurtlerhoft.fr", "+33 3 88 75 00 05", "gurtlerhoft.fr", "@gurtlerhoft", "Winstub / Alsacien Authentique", "Indipendente", "⚠️ Medio", "Winstub in cantina medioevale, choucroute e flammekueche in pietra antica"),
    ("My Little Good", "Neustadt", "10 rue des Bouchers, 67000 Strasbourg", "mylittlegood.str@gmail.com", "+33 3 88 22 15 88", "", "@mylittlegood_str", "Café / Brunch / Healthy", "Indipendente", "✅ Sì", "Caffè e brunch healthy nella Neustadt, composizioni floreali e bowl fotogenici"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Strasbourg - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Strasbourg.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
