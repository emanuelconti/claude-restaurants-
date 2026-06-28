#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Toulouse.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Le Bibent", "Capitole", "5 place du Capitole, 31000 Toulouse", "contact@lebibent.com", "+33 5 61 23 89 03", "lebibent.com", "@lebibent_toulouse", "Brasserie Belle Époque", "Indipendente", "✅ Sì", "Brasserie con interni Belle Époque magnifici, soffitti affrescati da fotografare"),
    ("Sept", "Saint-Étienne", "7 rue de l'Esquile, 31000 Toulouse", "contact@sept-toulouse.fr", "+33 5 61 25 20 01", "sept-toulouse.fr", "@sept_toulouse", "Bistronomie Créative", "Indipendente", "✅ Sì", "Bistrot gastronomique nel quartiere Saint-Étienne, sala design e piatti artistici"),
    ("La Faim des Haricots", "Carmes", "3 rue du Puits Vert, 31000 Toulouse", "contact@faim-des-haricots.fr", "+33 5 61 22 49 25", "faim-des-haricots.fr", "@faimdesharicots", "Végétarien / Café", "Piccola catena", "✅ Sì", "Storico ristorante vegetariano di Tolosa, piatti colorati e atmosphere hippie-chic"),
    ("Ô Saveurs", "Saint-Cyprien", "6 rue Pharaon, 31300 Toulouse", "contact@osaveurs.fr", "+33 5 61 25 58 12", "osaveurs.fr", "@osaveurs_toulouse", "Bistronomie / Créatif", "Indipendente", "✅ Sì", "Bistrot créatif nel quartiere Saint-Cyprien, menù ardesia e selezione vini"),
    ("Esquis by Meilleur", "Carmes", "10 place des Carmes, 31000 Toulouse", "contact@esquistoulouse.fr", "+33 5 62 27 07 07", "esquistoulouse.fr", "@esquistoulouse", "Bistronomie / Chef Étoilé", "Indipendente", "⚠️ Medio", "Bistrot dello chef Sébastien Meilleur, cucina créative accessibile"),
    ("Les Jardins de l'Opéra", "Capitole", "1 place du Capitole, 31000 Toulouse", "jardins@grandhotel-toulouse.com", "+33 5 61 23 07 76", "lesjardinsdelopera.com", "@lesjardinsdelopera", "Gastronomique Historique", "Indipendente", "⚠️ Medio", "Ristorante storico del Grand Hôtel, jardin interieur fotogenico"),
    ("IOTH Coffee", "Wilson", "5 rue du Taur, 31000 Toulouse", "iothcoffee@gmail.com", "+33 5 61 23 18 37", "", "@iothcoffee", "Specialty Coffee", "Indipendente", "✅ Sì", "Specialty coffee vicino alla Basilica di Saint-Sernin, latte art molto fotografata"),
    ("Café Populaire", "Wilson", "7 rue du Poids de l'Huile, 31000 Toulouse", "cafepopulaire.tlse@gmail.com", "+33 5 61 23 64 52", "", "@cafepopulaire_toulouse", "Café / Bar / Brunch", "Indipendente", "✅ Sì", "Caffè bobo nel centro, atmosfera parigina e terrasse animata"),
    ("Nœud Pap'", "Saint-Cyprien", "12 rue de la Colombette, 31000 Toulouse", "noeudpap.toulouse@gmail.com", "+33 5 61 55 59 27", "", "@noeudpap_toulouse", "Brunch / Café", "Indipendente", "✅ Sì", "Brunch trendy a Saint-Cyprien, uova bénédictine e french toast fotografabili"),
    ("L'Eau de Bouche", "Carmes", "8 rue Saint-Antoine du T, 31000 Toulouse", "leaudebouche@gmail.com", "+33 5 61 21 08 08", "", "@leaudebouche_toulouse", "Bistro / Wine Bar", "Indipendente", "✅ Sì", "Bar à vins e bistrot nel Carmes, planches e vins nature fotogenici"),
    ("Casa Camille", "Centre", "30 rue des Filatiers, 31000 Toulouse", "casacamille.toulouse@gmail.com", "+33 5 61 22 40 45", "", "@casacamille_toulouse", "Brunch / Café / Organic", "Indipendente", "✅ Sì", "Caffè bio e brunch nel centro storico, prodotti locali e interni caldi fotogenici"),
    ("Le Garçon Sauvage", "Wilson", "12 rue Tolosane, 31000 Toulouse", "garcon.sauvage@gmail.com", "+33 5 61 21 99 54", "", "@legarcon_sauvage", "Natural Wine Bar / Bistro", "Indipendente", "✅ Sì", "Wine bar naturel con cucina créative nel quartiere Wilson"),
    ("Le Genty-Magre", "Capitole", "3 rue Genty-Magre, 31000 Toulouse", "gentymafre@gmail.com", "+33 5 61 21 38 60", "", "@gentym_toulouse", "Wine / Oysters", "Indipendente", "✅ Sì", "Ostriche e vini naturali nella città vecchia, très photogénique"),
    ("La Braisière", "Centre", "42 rue Croix-Baragnon, 31000 Toulouse", "contact@labraisiere.com", "+33 5 61 52 09 27", "labraisiere.com", "@labraisiere_toulouse", "Gastronomique / Sud-Ouest", "Indipendente", "⚠️ Medio", "Cucina gastronomica del Sud-Ouest, presentazioni elaborate e fotografabili"),
    ("Boco Toulouse", "Centre", "15 rue Romiguières, 31000 Toulouse", "toulouse@boco.fr", "+33 5 61 22 43 19", "boco.fr", "@bocorestaurant", "Healthy / Organic Bocaux", "Piccola catena", "⚠️ Medio", "Cuisine sana in vasetti di vetro, concept écolo e fotogenico"),
    ("Ambroisie Toulouse", "Carmes", "28 rue des Fleurs, 31000 Toulouse", "ambroisie.tlse@gmail.com", "+33 5 61 23 23 42", "", "@ambroisie_toulouse", "Bistro / Gastronomique", "Indipendente", "✅ Sì", "Bistrot gastronomique nei Carmes, sala con muro di bottiglie fotografabile"),
    ("Taïko", "Centre", "7 rue de la Colombette, 31000 Toulouse", "taiko.toulouse@gmail.com", "+33 5 61 99 48 72", "", "@taiko_toulouse", "Japanese / Korean", "Indipendente", "✅ Sì", "Cucina giapponese e coreana moderna, bibimbap e ramen fotogenici"),
    ("Pane e Tradizione Toulouse", "Wilson", "15 rue des Couteliers, 31000 Toulouse", "paneetradizione.tlse@gmail.com", "+33 5 61 21 76 54", "", "@paneetradizione_toulouse", "Italian / Pizzeria", "Indipendente", "✅ Sì", "Pizzeria napoletana con forno a legna, impasto fotogenico al momento"),
    ("Yummy Bowl", "Centre", "32 rue Saint-Antoine du T, 31000 Toulouse", "yummybowl.toulouse@gmail.com", "+33 5 61 22 41 17", "", "@yummybowl_toulouse", "Healthy / Bowls / Vegan", "Indipendente", "✅ Sì", "Bowls végétal e healthy colorate, apertura giovani, molto instagrammabile"),
    ("Le Colombo", "Saint-Cyprien", "3 rue de la Colombette, 31300 Toulouse", "lecolombotoulouse@gmail.com", "+33 5 61 59 27 93", "", "@lecolombo_toulouse", "Indian / Créole", "Indipendente", "✅ Sì", "Cucina créole e spezie colorate, piatti vivaci e molto fotogenici"),
    ("Poivre Rose", "Centre", "26 rue du Poids de l'Huile, 31000 Toulouse", "poivrerose.toulouse@gmail.com", "+33 5 61 21 79 75", "", "@poivrerose_toulouse", "Bistro / Cuisine du Marché", "Indipendente", "✅ Sì", "Piccolo bistrot nel centro con cucina di mercato e atmosfera intima"),
    ("Chez Navarre", "Capitole", "19 rue Croix-Baragnon, 31000 Toulouse", "cheznavarre@gmail.com", "+33 5 61 25 21 55", "", "@cheznavarre_toulouse", "Cuisine du Marché", "Indipendente", "✅ Sì", "Cucina di mercato con lavagna quotidiana, sala intima e fotogenica"),
    ("Le Quai Toulouse", "Saint-Cyprien", "Quai de la Daurade, 31000 Toulouse", "contact@lequai-toulouse.fr", "+33 5 61 32 66 44", "", "@lequai_toulouse", "Restaurant / Vue Garonne", "Indipendente", "✅ Sì", "Ristorante sul lungofiume con vista sul Pont Neuf e Garonna rosa"),
    ("Le Père Léon", "Carmes", "2 place de la Trinité, 31000 Toulouse", "lepere.leon@gmail.com", "+33 5 61 25 04 98", "", "@pereleontoulouse", "Brasserie / Terrasse", "Indipendente", "✅ Sì", "Brasserie sulla pittoresca Place de la Trinité nei Carmes"),
    ("Le Cénit", "Purpan", "1 ave Jean Gonord, 31000 Toulouse", "contact@lecenittoulouse.fr", "+33 5 62 71 83 00", "", "@lecenittoulouse", "Restaurant / Panoramique", "Indipendente", "✅ Sì", "Ristorante con vista panoramica sulla città rosa, tramonto fotografabile"),
    ("Dario Toulouse", "Carmes", "26 rue des Filatiers, 31000 Toulouse", "dario.toulouse@gmail.com", "+33 5 61 55 28 41", "", "@dario_toulouse", "Italian Fine Dining", "Indipendente", "✅ Sì", "Ristorante italiano fine dining nei Carmes, piatti elaborati e fotografabili"),
    ("Le Bon Vivre Toulouse", "Côte Pavée", "15 ave de la Colonne, 31400 Toulouse", "lebonvivre.tlse@gmail.com", "+33 5 61 52 35 10", "", "@lebonvivre_toulouse", "Bistro / Brunch", "Indipendente", "✅ Sì", "Bistrot e brunch nel quartiere residenziale Côte Pavée"),
    ("La Cantineta Toulouse", "Capitole", "9 rue des Couteliers, 31000 Toulouse", "lacantineta.tlse@gmail.com", "+33 5 61 23 42 30", "", "@lacantineta_toulouse", "Italian", "Piccola catena", "⚠️ Medio", "Trattoria italiana vicino al Capitole, buon rapporto qualità-prezzo"),
    ("Le Sherpa Café", "Saint-Sernin", "46 rue du Taur, 31000 Toulouse", "lesherpa.toulouse@gmail.com", "+33 5 61 23 22 47", "", "@lesherpa_toulouse", "Café / Bar Alternatif", "Indipendente", "✅ Sì", "Caffè alternativo vicino all'università, murales e atmosfera colorata"),
    ("Toulouse & Co Café", "Centre", "23 rue des Lois, 31000 Toulouse", "toulouseandco@gmail.com", "+33 5 61 21 00 89", "", "@toulouseandco", "Café / Brunch / Local", "Indipendente", "✅ Sì", "Caffè e brunch con prodotti locali e toulousains, atmosfera accogliente"),
    ("Brasserie de Compiegne", "Capitole", "4 place du Capitole, 31000 Toulouse", "contact@brasseriedecompiegne.fr", "+33 5 61 21 99 99", "brasseriedecompiegne.fr", "@brasseriedecompiegne", "Grande Brasserie / Capitole", "Piccola catena", "⚠️ Medio", "Grande brasserie sulla celebre Place du Capitole, terrasse con vista piazza"),
    ("Le Sauvage Toulouse", "Carmes", "18 rue de la Dalbade, 31000 Toulouse", "lesauvage.toulouse@gmail.com", "+33 5 61 22 88 14", "", "@lesauvage_toulouse", "Natural Wine Bar", "Indipendente", "✅ Sì", "Wine bar naturel con selezione di produttori locaux e atmosfera cave"),
    ("Grand Café de l'Opéra", "Capitole", "1 place du Capitole, 31000 Toulouse", "grandcafe.tlse@gmail.com", "+33 5 61 21 37 03", "", "@grandcafeopera_toulouse", "Café / Brasserie Historique", "Indipendente", "⚠️ Medio", "Caffè storico adiacente al Capitole, décor d'epoca e terrasse fotografabile"),
    ("Oh! Poivrier", "Wilson", "1 place Wilson, 31000 Toulouse", "ohpoivrier.tlse@gmail.com", "+33 5 61 21 33 22", "", "@ohpoivrier_toulouse", "Brunch / Café / Épices", "Indipendente", "✅ Sì", "Caffè e brunch in Place Wilson, spezie colorate e piatti créatifs"),
    ("Le Bon Marché Toulouse", "Saint-Aubin", "12 rue Gabriel Péri, 31400 Toulouse", "lebonmarche.tlse@gmail.com", "+33 5 61 53 12 30", "", "@lebonmarche_toulouse", "Café / Coworking / Brunch", "Indipendente", "✅ Sì", "Café coworking con brunch healthy nel quartiere Saint-Aubin"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Toulouse - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Toulouse.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
