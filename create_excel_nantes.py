#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Nantes.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("La Cigale", "Graslin", "4 place Graslin, 44000 Nantes", "contact@lacigale.com", "+33 2 51 84 94 94", "lacigale.com", "@lacigale_nantes", "Brasserie Belle Époque", "Indipendente", "✅ Sì", "Brasserie UNESCO con mosaici e décor Belle Époque 1895, una delle più fotografate di Nantes"),
    ("Lulu Rouget", "Hauts-Pavés", "3 rue Moriceau, 44000 Nantes", "contact@lulurouget.com", "+33 2 51 82 72 72", "lulurouget.com", "@lulurouget", "Gastronomique / Bistronomie", "Indipendente", "✅ Sì", "Top ristorante gastronomico di Nantes, piatti artistici e sala design"),
    ("Pickles Restaurant", "Bouffay", "2 rue du Marais, 44000 Nantes", "contact@pickles-nantes.fr", "+33 2 40 89 33 04", "pickles-nantes.fr", "@pickles_nantes", "Natural Wine / Bistro Créatif", "Indipendente", "✅ Sì", "Bistrot naturel e creativo nel Bouffay, uno dei locali più trendy di Nantes"),
    ("Paréidolie", "Talensac", "3 rue des Olivettes, 44000 Nantes", "pareidolie.nantes@gmail.com", "+33 2 40 47 38 71", "", "@pareidolie_nantes", "Natural Wine / Cave à Manger", "Indipendente", "✅ Sì", "Cave à manger con vini naturali e piatti creativi, muri di bottgigie fotogenici"),
    ("Félix Restaurant", "Centre", "1 rue Léon Jost, 44000 Nantes", "contact@felix-restaurant.fr", "+33 2 51 82 52 52", "felix-restaurant.fr", "@felixrestaurant_nantes", "Bistronomie Moderne", "Indipendente", "✅ Sì", "Bistrot gastronomique moderno, presentazioni curate e fotogeniche"),
    ("Cantine 29", "Île de Nantes", "29 blvd des Martyrs Nantais, 44200 Nantes", "cantine29@gmail.com", "+33 2 40 89 41 23", "", "@cantine29_nantes", "Café / Brunch / Healthy", "Indipendente", "✅ Sì", "Caffè e brunch sull'Île de Nantes con terrasse, atmosfera creativa fotogenica"),
    ("Café Mélo", "Centre", "19 rue des Olivettes, 44000 Nantes", "cafemelo.nantes@gmail.com", "+33 2 40 48 37 48", "", "@cafemelo_nantes", "Café / Brunch", "Indipendente", "✅ Sì", "Caffè e brunch nel centro con decorazioni vintage, atmosfera accogliente"),
    ("L'Absinthe Nantes", "Bouffay", "6 rue des Petites Écuries, 44000 Nantes", "labsinthe.nantes@gmail.com", "+33 2 40 89 22 10", "", "@labsinthe_nantes", "Wine Bar / Bistro", "Indipendente", "✅ Sì", "Bar à vins nel Bouffay con décor bohémien, planches fotografabili"),
    ("La Raffinerie Nantes", "Île de Nantes", "10 blvd de la Prairie de Mauves, 44000 Nantes", "contact@laraffinerie-nantes.fr", "+33 2 40 49 71 31", "laraffinerie-nantes.fr", "@laraffinerie_nantes", "Restaurant / Lieu Culturel", "Indipendente", "✅ Sì", "Ristorante in ex-raffineria industriale sull'Île de Nantes, décor unico"),
    ("L'Amour en Cage", "Centre", "12 rue Léon Jost, 44000 Nantes", "lamoureencage@gmail.com", "+33 2 51 84 65 12", "", "@lamoureencage_nantes", "Natural Wine / Tapas", "Indipendente", "✅ Sì", "Wine bar dei vini naturali con tapas créatives, atmosfera intima fotogenica"),
    ("Le Tupina Nantes", "Barbin", "16 rue de Gorges, 44100 Nantes", "letupina.nantes@gmail.com", "+33 2 40 35 47 28", "", "@letupina_nantes", "Bistro / Cuisine du Terroir", "Indipendente", "✅ Sì", "Bistrot di cucina del territorio, camino e arredi rustici fotografabili"),
    ("La Boucherie Moderne", "Hauts-Pavés", "8 rue Émile Péhant, 44000 Nantes", "boucheriemoderne@gmail.com", "+33 2 40 76 22 46", "", "@boucheriemoderne_nantes", "Bistro / Viandes", "Indipendente", "✅ Sì", "Boucherie trasformata in bistrot, esposizione di carni e taglieri fotogenici"),
    ("Umami Nantes", "Centre", "3 rue Colbert, 44000 Nantes", "umami.nantes@gmail.com", "+33 2 40 89 44 12", "", "@umami_nantes", "Japanese / Asian Fusion", "Indipendente", "✅ Sì", "Cucina giapponese-asiatica nel centro, ramen e bento coloratissimi"),
    ("Maison Baron Lefèvre", "Centre", "33 rue de Rieux, 44000 Nantes", "contact@maisondel.fr", "+33 2 40 89 20 20", "maisondel.fr", "@maisonbaronlefevre", "Gastronomique / Maison de Maître", "Indipendente", "⚠️ Medio", "Ristorante gastronomico in maison di charme, sala con luce naturale fotografabile"),
    ("Le Manoir de la Régate", "Centre", "155 route de Gachet, 44300 Nantes", "contact@manoir-regate.fr", "+33 2 40 18 02 97", "manoir-regate.fr", "@manoirdelaregate", "Gastronomique / Vue Loire", "Indipendente", "⚠️ Medio", "Ristorante gastronomico con vista sulla Loira, giardino fotogenico"),
    ("SoCal Kitchen Nantes", "Île de Nantes", "5 quai Ernest Renaud, 44100 Nantes", "socal.nantes@gmail.com", "+33 2 40 12 55 44", "", "@socal_nantes", "California / Brunch / Bowls", "Indipendente", "✅ Sì", "Cucina californiana e brunch colorato sull'Île de Nantes, bowls fotogenici"),
    ("Au Beurre Blanc", "Centre", "3 rue Santeuil, 44000 Nantes", "contact@le-beurreblanc.com", "+33 2 51 82 70 70", "le-beurreblanc.com", "@restaurant_beurrelblanc", "Cuisine Loire-Atlantique", "Indipendente", "⚠️ Medio", "Cucina classica ligérienne, piatto iconico beurre blanc di Nantes"),
    ("Bloom Restaurant", "Île de Nantes", "7 rue de Pirmil, 44200 Nantes", "bloom.nantes@gmail.com", "+33 2 40 09 67 34", "", "@bloom_nantes", "Végétal / Bistronomie", "Indipendente", "✅ Sì", "Cucina vegetale e bistronomique sull'Île de Nantes, piatti floreali fotogenici"),
    ("Le Grappin", "Centre", "10 rue Tournefort, 44000 Nantes", "legrappin.nantes@gmail.com", "+33 2 51 84 22 31", "", "@legrappin_nantes", "Wine Bar / Tapas", "Indipendente", "✅ Sì", "Wine bar conviviale con selezione vini naturali e tapas fotografabili"),
    ("Café Atlantique", "Centre", "16 allée Duguay-Trouin, 44000 Nantes", "cafeatlantique.nantes@gmail.com", "+33 2 40 69 43 51", "", "@cafeatlantique_nantes", "Café / Brasserie / Art", "Indipendente", "✅ Sì", "Caffè brasserie con esposizioni d'arte temporanee, atmosfera culturale"),
    ("Le Gressin Nantes", "Bouffay", "4 rue Bossuet, 44000 Nantes", "legressin.nantes@gmail.com", "+33 2 40 89 23 42", "", "@legressin_nantes", "Bistro / Cave à Manger", "Indipendente", "✅ Sì", "Cave à manger e bistrot nel Bouffay, assortimento di vins nature"),
    ("Pimento", "Centre", "14 rue Jean-Jacques Rousseau, 44000 Nantes", "pimento.nantes@gmail.com", "+33 2 40 89 60 07", "", "@pimento_nantes", "Spanish / Tapas", "Indipendente", "✅ Sì", "Tapas spagnole e pintxos nel centro, atmosfera festiva e colorata fotogenica"),
    ("Les Rosiers Nantes", "Hauts-Pavés", "22 rue Bellevue, 44100 Nantes", "lesrosiers.nantes@gmail.com", "+33 2 40 52 30 38", "", "@lesrosiers_nantes", "Bistro / Jardin", "Indipendente", "✅ Sì", "Bistrot con giardino e rose, uno dei più fotogenici di Nantes in estate"),
    ("La Barge Nantes", "Île de Nantes / Loire", "Quai des Antilles, 44200 Nantes", "contact@labarge-nantes.fr", "+33 2 40 69 76 21", "labarge-nantes.fr", "@labarge_nantes", "Restaurant / Péniche", "Indipendente", "✅ Sì", "Ristorante su chiatta sulla Loira, vista unica fotografabile"),
    ("Mamie Bigoude", "Centre", "7 rue des Carmes, 44000 Nantes", "mamiebigoude@gmail.com", "+33 2 40 48 67 34", "", "@mamiebigoude_nantes", "Crêperie Bretonne", "Indipendente", "⚠️ Medio", "Crêperie con atmosphère bretonne, galettes colorate e fotogeniche"),
    ("Mojo Nantes", "Centre", "23 rue du Calvaire, 44000 Nantes", "mojo.nantes@gmail.com", "+33 2 40 89 51 67", "", "@mojo_nantes", "Cocktail Bar / Food", "Indipendente", "✅ Sì", "Cocktail bar e cucina créative, drinks colorati e décor instagrammabile"),
    ("Gusto!", "Centre", "6 rue de l'Arche Sèche, 44000 Nantes", "gusto.nantes@gmail.com", "+33 2 40 48 20 02", "", "@gusto_nantes", "Italian / Comptoir", "Indipendente", "✅ Sì", "Comptoir italiano con pasta fresca e antipasti colorati nel centro"),
    ("Oh! Poivrier Nantes", "Centre", "12 rue Crébillon, 44000 Nantes", "ohpoivrier.nantes@gmail.com", "+33 2 40 47 15 40", "", "@ohpoivrier_nantes", "Brunch / Café / Épices", "Indipendente", "✅ Sì", "Caffè e brunch con spezie colorate e piatti créatifs nel centro"),
    ("Terre & Mer", "Centre", "8 rue de la Bâclerie, 44000 Nantes", "terremer.nantes@gmail.com", "+33 2 40 89 39 37", "", "@terreetmer_nantes", "Bistro / Seasonal", "Indipendente", "✅ Sì", "Bistrot stagionale con prodotti locaux e presentazioni pulite e fotogeniche"),
    ("L'Instinct Nantes", "Centre", "15 rue des Vieilles Douves, 44000 Nantes", "linstinct.nantes@gmail.com", "+33 2 40 89 48 21", "", "@linstinct_nantes", "Bistronomie / Natural Wine", "Indipendente", "✅ Sì", "Bistrot con vini naturali e cucina di istinto, atmosfera intima fotogenica"),
    ("Nantaise Coffee", "Île de Nantes", "1 rue des Olivettes, 44200 Nantes", "nantaisecoffee@gmail.com", "+33 2 40 69 11 34", "", "@nantaisecoffee", "Specialty Coffee / Brunch", "Indipendente", "✅ Sì", "Specialty coffee sull'Île de Nantes, latte art e bricchetti grafici fotogenici"),
    ("La Comédie", "Graslin", "2 place Graslin, 44000 Nantes", "lacomedienantes@gmail.com", "+33 2 40 69 30 45", "", "@lacomediefr_nantes", "Café / Terrasse / Vue Théâtre", "Indipendente", "✅ Sì", "Caffè con terrasse di fronte al Théâtre Graslin, vista neoclassica fotografabile"),
    ("La Cantine du Troquet", "Centre", "4 rue du Chapeau Rouge, 44000 Nantes", "lacantinedutroquet@gmail.com", "+33 2 40 35 27 60", "", "@lacantinedutroquet", "Cuisine du Marché / Ardoise", "Indipendente", "✅ Sì", "Cantine con lavagna giornaliera e vini al calice, atmosfera bobo-chic"),
    ("Soléa Nantes", "Hauts-Pavés", "11 rue de Coulmiers, 44000 Nantes", "solea.nantes@gmail.com", "+33 2 40 76 38 09", "", "@solea_nantes", "Méditerranéen / Soleil", "Indipendente", "✅ Sì", "Cucina méditéranéenne con colori del Sud, sala luminosa e piatti vivaci"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Nantes - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Nantes.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
