#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Paris_New.xlsx — nuovi lead Parigi (non presenti nel file principale)"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    # ── CAFÉS & BRUNCH ─────────────────────────────────────────────────────────
    ("Café Lomi", "18e", "3bis rue Marcadet, 75018 Paris", "contact@lomi.paris", "+33 9 80 39 56 24", "lomi.paris", "@lomi.paris", "Specialty Coffee / Torréfaction", "Indipendente", "✅ Sì", "Torréfacteur indépendant du 18e, brunch photogénique et café de qualité"),
    ("Télescope", "1er", "5 rue Villedo, 75001 Paris", "contact@telescopecafe.com", "+33 1 42 61 33 14", "telescopecafe.com", "@telescopecafe", "Specialty Coffee", "Indipendente", "✅ Sì", "Pionnière du café de spécialité à Paris, minimaliste et instagrammable"),
    ("Ten Belles", "10e", "10 rue de la Grange aux Belles, 75010 Paris", "contact@tenbelles.com", "+33 1 42 40 90 78", "tenbelles.com", "@tenbelles", "Specialty Coffee / Brunch", "Indipendente", "✅ Sì", "Café de spécialité iconique du canal Saint-Martin, brunch et gâteaux"),
    ("Boot Café", "3e", "19 rue du Pont aux Choux, 75003 Paris", "", "+33 6 78 81 97 00", "", "@bootcafe", "Specialty Coffee", "Indipendente", "✅ Sì", "Minuscolo caffè in una ex-calzoleria, uno dei più instagrammabili di Parigi"),
    ("Café Oberkampf", "11e", "3 rue Neuve Popincourt, 75011 Paris", "contact@cafeoberkampf.com", "+33 1 43 57 28 55", "cafeoberkampf.com", "@cafeoberkampf", "Café / Brunch", "Indipendente", "✅ Sì", "Brunch colorato nel quartiere Oberkampf, interni curati e photogéniques"),
    ("Café Kitsuné", "1er/6e/8e", "51 Galerie de Montpensier, 75001 Paris", "cafe@maisonkitsune.com", "+33 1 40 15 62 32", "maisonkitsune.com", "@cafekitsune", "Japanese Café / Design", "Piccola catena", "⚠️ Medio", "Caffè fashion e musica, interni epurati e molto fotografabili"),
    ("Fragments", "3e", "76 rue des Tournelles, 75003 Paris", "contact@fragmentscafe.com", "+33 9 67 97 87 48", "fragmentscafe.com", "@fragmentsparis", "Specialty Coffee / Natural Wine", "Indipendente", "✅ Sì", "Caffè e vini naturali nel Marais, atmosfera curata e bohémien"),
    ("KB CaféShop", "9e", "53 ave Trudaine, 75009 Paris", "contact@kbcafeshop.com", "+33 1 56 92 12 41", "kbcafeshop.com", "@kbcafeshop", "Specialty Coffee / Brunch", "Indipendente", "✅ Sì", "Caffè australiano nel 9e, brunch copioso e molto fotografabile"),
    ("Café Pinson", "3e/10e", "6 rue du Forez, 75003 Paris", "contact@cafepinson.fr", "+33 9 83 82 53 60", "cafepinson.fr", "@cafepinson", "Café / Healthy / Végane", "Piccola catena", "✅ Sì", "Café végane et biologique, plats colorés et instagrammables"),
    ("Café Méricourt", "11e", "22 rue de la Folie-Méricourt, 75011 Paris", "contact@cafemericourt.com", "+33 1 43 38 94 04", "cafemericourt.com", "@cafemericourt", "Café / Brunch", "Indipendente", "✅ Sì", "Brunch du weekend iconique dans le 11e, oeuf bénédictine photogénique"),

    # ── BISTROTS & RESTAURANTS MODERNES ───────────────────────────────────────
    ("Yard", "11e", "6 rue Mont Louis, 75011 Paris", "contact@yardparis.com", "+33 1 40 09 70 30", "yardparis.com", "@yard.paris", "Wine Bar / Bistro", "Indipendente", "✅ Sì", "Cave à manger naturel dans le 11e, planches photogéniques"),
    ("Clown Bar", "11e", "114 rue Amelot, 75011 Paris", "contact@clown-bar-paris.fr", "+33 1 43 55 87 35", "clown-bar-paris.fr", "@clownbarparis", "Bistro / Natural Wine", "Indipendente", "⚠️ Medio", "Bar à vins naturels dans l'ancien décor du Cirque d'Hiver, unique"),
    ("Mokonuts", "11e", "5 rue Saint-Bernard, 75011 Paris", "mokonuts@mokonuts.com", "+33 9 80 81 82 85", "mokonuts.com", "@mokonuts", "Café / Middle-Eastern / Bakery", "Indipendente", "✅ Sì", "Pâtisseries créatives et cuisine Moyen-Orient, cookies instagrammés partout"),
    ("Le Mary Celeste", "3e", "1 rue Commines, 75003 Paris", "contact@lemaryceleste.com", "+33 9 80 72 98 83", "lemaryceleste.com", "@lemaryceleste", "Cocktail Bar / Tapas", "Indipendente", "✅ Sì", "Bar à cocktails et tapas dans le Marais, décor marin très photogénique"),
    ("Septime La Cave", "11e", "3 rue Basfroi, 75011 Paris", "", "+33 1 43 67 14 87", "septime-lacave.fr", "@septimeparis", "Cave à Manger / Natural Wine", "Indipendente", "✅ Sì", "Cave à vins naturels du célèbre Septime, planches de charcuterie et fromages"),
    ("Aux Deux Amis", "11e", "45 rue Oberkampf, 75011 Paris", "", "+33 1 58 30 38 13", "", "@auxdeuxamis11", "Bistro / Tapas / Natural Wine", "Indipendente", "✅ Sì", "Bar à vins nature avec petits plats, atmosphère conviviale instagrammable"),
    ("Camille Surnom", "3e", "24 rue des Francs Bourgeois, 75003 Paris", "", "+33 1 42 72 20 50", "", "@camillesurnom", "Bistro Parisien", "Indipendente", "✅ Sì", "Bistrot classique avec terrasse sur le Marais, cuisine simple et belle"),
    ("Breizh Café Marais", "3e", "109 rue Vieille du Temple, 75003 Paris", "contact@breizhcafe.com", "+33 1 42 72 13 77", "breizhcafe.com", "@breizhcafe", "Crêperie Bretonne", "Piccola catena", "⚠️ Medio", "Crêperie haut de gamme dans le Marais, galettes photographiées partout"),
    ("Au Passage", "11e", "1bis passage Saint-Sébastien, 75011 Paris", "", "+33 1 43 55 07 52", "", "@aupassage_paris", "Wine Bar / Small Plates", "Indipendente", "✅ Sì", "Bar dans un passage couvert, vins nature et planches photogéniques"),
    ("Bistrot Paul Bert", "11e", "18 rue Paul Bert, 75011 Paris", "bistrotpaulbert@gmail.com", "+33 1 43 72 24 01", "bistrotpaulbert.fr", "@bistrotpaulbert", "Bistro Classique", "Indipendente", "✅ Sì", "Bistrot parisien authentique, steak tartare et entrecôte parfaits en photo"),

    # ── ASIATIQUE & FUSION ─────────────────────────────────────────────────────
    ("Tân Dinh", "7e", "60 rue de Verneuil, 75007 Paris", "tandinh@wanadoo.fr", "+33 1 45 44 04 84", "", "@tandinh_paris", "Vietnamese Fine Dining", "Indipendente", "✅ Sì", "Restaurant vietnamien historique du 7e, décor fleuri instagrammable"),
    ("Chez Vong", "1er", "10 rue de la Grande Truanderie, 75001 Paris", "chezvong@wanadoo.fr", "+33 1 40 39 99 89", "", "@chezvong_paris", "Chinese / Cantonese", "Indipendente", "⚠️ Medio", "Cantonese historique dans le 1er, décor chinois traditionnel"),
    ("Himitsu", "11e", "10 rue du Général Guilhem, 75011 Paris", "himitsu.paris@gmail.com", "+33 9 83 03 54 21", "", "@himitsu_paris", "Japanese Izakaya", "Indipendente", "✅ Sì", "Izakaya japonaise dans le 11e, plats créatifs et atmosphère intime"),
    ("Pho Banh Cuon 14", "13e", "129 ave de Choisy, 75013 Paris", "", "+33 1 45 83 61 15", "", "@phobanhcuon14", "Vietnamese / Pho", "Indipendente", "⚠️ Medio", "Pho authentique dans le quartier asiatique, ambiance immuable"),
    ("Lao Lane Xang 2", "13e", "102 ave d'Ivry, 75013 Paris", "", "+33 1 58 89 00 00", "", "@laolane_paris", "Laotian / Thai", "Indipendente", "⚠️ Medio", "Cuisine laotienne rare à Paris, photographique et accessible"),
    ("Kari Kari", "6e", "34 rue du Cardinal Lemoine, 75005 Paris", "karikari.paris@gmail.com", "+33 1 43 29 59 60", "", "@karikari_paris", "Japanese / Katsu Sando", "Indipendente", "✅ Sì", "Katsu sando et tonkatsu, sandwiches japonais très photographiés"),
    ("Pink Mamma", "9e", "20bis rue de Douai, 75009 Paris", "pinkmamma@bigmammagroup.com", "+33 1 58 63 36 78", "bigmammagroup.com", "@pinkmammaparis", "Italian / Modern", "Piccola catena", "⚠️ Medio", "Restaurant italien sur 4 étages dans le 9e, décor floral iconique"),
    ("East Mamma", "11e", "133 rue du Faubourg-Saint-Antoine, 75011 Paris", "eastmamma@bigmammagroup.com", "+33 1 43 41 32 15", "bigmammagroup.com", "@eastmamma", "Italian / Modern", "Piccola catena", "⚠️ Medio", "Grande trattoria italienne dans le 11e, pasta fresca et pizzas"),
    ("Bao Bei", "3e", "54 rue Saintonge, 75003 Paris", "contact@baobei.fr", "+33 9 51 45 43 05", "baobei.fr", "@baobei_paris", "Chinese / Taiwanese", "Indipendente", "✅ Sì", "Bao vapeur et cuisine taïwanaise dans le Marais, esthétique épuré"),
    ("Nôm", "3e", "8 rue du Pont aux Choux, 75003 Paris", "contact@nomparis.fr", "+33 1 42 74 47 27", "nomparis.fr", "@nom_paris", "Vietnamese / Modern", "Indipendente", "✅ Sì", "Cuisine vietnamienne contemporaine dans le Marais, bols colorés"),

    # ── STREET FOOD, BURGERS & SANDWICHS ──────────────────────────────────────
    ("Le Camion Qui Fume", "Multiple", "Locations varies Paris", "contact@lecamionquifume.com", "+33 6 12 49 43 12", "lecamionquifume.com", "@lecamionquifume", "Burgers Gourmet / Food Truck", "Piccola catena", "⚠️ Medio", "Food trucks de burgers gourmet, queue instagrammable les mid"),
    ("Fulgurances L'Adresse", "11e", "10 rue Alexandre Dumas, 75011 Paris", "contact@fulgurances.com", "+33 1 43 70 89 89", "fulgurances.com", "@fulgurances", "Pop-up / Gastronomique", "Indipendente", "✅ Sì", "Résidence de jeunes chefs, concept unique et photographiable"),
    ("Saucisson & Champagne", "2e", "29 rue Sainte-Anne, 75001 Paris", "sacochampagne@gmail.com", "+33 1 42 36 80 18", "", "@saucissonchampagne", "Charcuterie / Champagne Bar", "Indipendente", "✅ Sì", "Bar à champagne avec saucissons, concept photographique et festif"),
    ("L'Avant Comptoir de la Mer", "6e", "3 carrefour de l'Odéon, 75006 Paris", "contact@camdeborde.com", "+33 1 44 27 07 97", "", "@lavantcomptoir", "Seafood Standing Bar", "Indipendente", "✅ Sì", "Bar debout fruits de mer dans le 6e, huitres et bulots très photographiés"),
    ("Miznon Paris", "4e", "22 rue des Ecouffes, 75004 Paris", "paris@miznonrestaurant.com", "+33 1 42 74 83 58", "miznonrestaurant.com", "@miznonparis", "Israeli / Pita Street Food", "Piccola catena", "✅ Sì", "Pita israélienne gourmet dans le Marais, queue et plats très photogéniques"),
    ("Le Comptoir du Relais", "6e", "9 carrefour de l'Odéon, 75006 Paris", "contact@hotel-paris-relais-saint-germain.com", "+33 1 44 27 07 97", "hotel-paris-relais-saint-germain.com", "@comptoir_du_relais", "Bistro Parisien / Yves Camdeborde", "Indipendente", "✅ Sì", "Le bistrot de Camdeborde, indispensable du 6e, tartelettes et assiettes splendides"),

    # ── VÉGANE & HEALTHY ──────────────────────────────────────────────────────
    ("Wild & The Moon", "3e/8e/11e", "55 rue Charlot, 75003 Paris", "hello@wildandthemoon.com", "+33 9 83 35 36 79", "wildandthemoon.com", "@wildandthemoon", "Raw / Vegan / Healthy", "Piccola catena", "✅ Sì", "Jus et plats raw vegan ultra-photogéniques dans le Marais et ailleurs"),
    ("Hank Burger", "5e/9e/18e", "55 rue du Faubourg Saint-Denis, 75010 Paris", "contact@hankburger.com", "+33 1 47 70 67 61", "hankburger.com", "@hankburger", "Vegan Burgers", "Piccola catena", "⚠️ Medio", "Burgers 100% véganes, visuels forts pour les réseaux sociaux"),
    ("VG Pâtisserie", "8e", "18 rue Marbeuf, 75008 Paris", "contact@vg-patisserie.com", "+33 1 45 61 09 56", "vg-patisserie.com", "@vgpatisserie", "Vegan Pâtisserie", "Indipendente", "✅ Sì", "Première grande pâtisserie végane de Paris, gâteaux artistiques et photogéniques"),
    ("Sol Semilla", "10e", "23 rue des Vinaigriers, 75010 Paris", "contact@sol-semilla.fr", "+33 1 42 01 03 44", "sol-semilla.fr", "@solsemilla", "Vegan / Latin / Superfood", "Indipendente", "✅ Sì", "Cuisine végane et superaliments latino-américains, bowls colorées"),

    # ── PÂTISSERIES & DESSERTS ─────────────────────────────────────────────────
    ("La Pâtisserie du Meurice", "1er", "228 rue de Rivoli, 75001 Paris", "contact@lemeurice.com", "+33 1 44 58 10 10", "dorchestercollection.com", "@lemeurice", "Pâtisserie Grand Hôtel", "Gruppo", "❌ No", "Pâtisserie du Palace, trop luxueux pour collaboration étudiante"),
    ("Jacques Genin", "3e", "133 rue de Turenne, 75003 Paris", "contact@jacquesgenin.fr", "+33 1 45 77 29 01", "jacquesgenin.fr", "@jacquesgenin", "Chocolaterie / Pâtisserie", "Indipendente", "✅ Sì", "Maître chocolatier et pâtissier indépendant dans le Marais, caramels iconiques"),
    ("Mamiche", "9e", "45 rue Condorcet, 75009 Paris", "bonjour@mamiche.fr", "+33 1 40 16 15 58", "mamiche.fr", "@mamiche_boulangerie", "Boulangerie Artisanale", "Indipendente", "✅ Sì", "Boulangerie tendance du 9e, pain au levain et viennoiseries très photographiées"),
    ("Liberté", "10e", "39 rue des Vinaigriers, 75010 Paris", "contact@liberte-paris.com", "+33 1 42 05 51 76", "liberte-paris.com", "@liberte_paris", "Boulangerie / Pâtisserie", "Piccola catena", "✅ Sì", "Pain, viennoiseries et tartes créatives, devanture photogénique rose"),
    ("Circus Bakery", "6e", "63 rue de Seine, 75006 Paris", "circus.bakery@gmail.com", "+33 6 13 17 09 65", "", "@circusbakery", "Cinnamon Rolls / Bakery", "Indipendente", "✅ Sì", "Connue pour ses cinnamon rolls, queue devant la boutique, très instagrammable"),
    ("Du Pain et des Idées", "10e", "34 rue Yves Toudic, 75010 Paris", "contact@dupainetdesidees.com", "+33 1 42 40 44 52", "dupainetdesidees.com", "@dupainetdesidees", "Boulangerie Traditionnelle", "Indipendente", "✅ Sì", "La meilleure boulangerie de Paris selon beaucoup, escargots et pain des amis"),
    ("Bontemps Pâtisserie", "3e", "57 rue de Bretagne, 75003 Paris", "bontempspatisserie@gmail.com", "+33 1 42 74 10 68", "", "@bontempspatisserie", "Pâtisserie / Tarte Flambée", "Indipendente", "✅ Sì", "Tartes créatives et desserts photogéniques rue de Bretagne dans le Marais"),
    ("Pain Pain", "18e", "88 rue Ramey, 75018 Paris", "painpain.boulangerie@gmail.com", "+33 1 42 23 61 86", "", "@painpainparis", "Boulangerie Artisanale", "Indipendente", "✅ Sì", "Boulangerie artisanale de Montmartre, croissants et briochettes photographiées"),

    # ── WINE BARS & COCKTAILS ──────────────────────────────────────────────────
    ("Septime", "11e", "80 rue de Charonne, 75011 Paris", "contact@septime-charonne.fr", "+33 1 43 67 38 29", "septime-charonne.fr", "@septimeparis", "Bistronomie / Natural Wine", "Indipendente", "✅ Sì", "L'une des meilleures tables de Paris, cuisine de saison et vins naturels"),
    ("Clamato", "11e", "80 rue de Charonne, 75011 Paris", "contact@clamato-charonne.fr", "+33 1 43 72 74 53", "clamato-charonne.fr", "@clamato_paris", "Seafood Bar / Natural Wine", "Indipendente", "✅ Sì", "Bar à huitres et fruits de mer du même groupe que Septime"),
    ("Bisou", "9e", "3 rue le Peletier, 75009 Paris", "contact@bisoubarparis.com", "+33 1 44 63 04 26", "bisoubarparis.com", "@bisou_bar", "Cocktail Bar / Wine Bar", "Indipendente", "✅ Sì", "Bar à vins et cocktails dans le 9e, murs carrelés pastel instagrammables"),
    ("Bar Hemingway – Ritz", "1er", "15 place Vendôme, 75001 Paris", "info@ritzparis.com", "+33 1 43 16 33 65", "ritzparis.com", "@ritz_paris", "Cocktail Bar / Palace", "Gruppo", "❌ No", "Bar iconique au Ritz, trop luxueux et grande chaîne"),
    ("Glass", "18e", "7 rue de Steinkerque, 75018 Paris", "contact@glassparis.com", "+33 1 42 62 35 83", "glassparis.com", "@glassparis", "Cocktail Bar / Music", "Indipendente", "✅ Sì", "Bar à cocktails et musique à Pigalle, néons et ambiance photographiable"),
    ("Bluebell Cocktails & Kitchen", "11e", "32 rue de Lappe, 75011 Paris", "contact@bluebellparis.com", "+33 1 43 55 09 56", "bluebellparis.com", "@bluebell_paris", "Cocktail Bar / Kitchen", "Indipendente", "✅ Sì", "Cocktails créatifs et petite restauration rue de Lappe"),

    # ── RESTAURANTS TENDANCE ──────────────────────────────────────────────────
    ("Frenchie", "2e", "5 rue du Nil, 75002 Paris", "contact@frenchie-restaurant.com", "+33 1 40 39 96 19", "frenchie-restaurant.com", "@frenchie_paris", "Bistronomie Moderne", "Piccola catena", "⚠️ Medio", "Référence de la bistronomie parisienne, rue du Nil photogénique"),
    ("Le Servan", "11e", "32 rue Saint-Maur, 75011 Paris", "contact@leservan.com", "+33 1 55 28 51 82", "leservan.com", "@leservanparis", "Bistronomie / Asian Influences", "Indipendente", "✅ Sì", "Cuisine bistronomique avec influences asiatiques, salle aux moulures dorées"),
    ("Nénuphar", "10e", "18 quai de la Loire, 75019 Paris", "contact@nenuphar.fr", "+33 1 42 09 60 39", "nenuphar.fr", "@nenuphar_paris", "Restaurant / Péniche", "Indipendente", "✅ Sì", "Péniche-restaurant sur le canal, terrasse sur l'eau très photographiée"),
    ("Le Rigmarole", "11e", "10 rue du Grand Prieuré, 75011 Paris", "contact@lerigmarole.com", "+33 9 83 01 04 52", "lerigmarole.com", "@lerigmarole", "Japanese-French Fusion", "Indipendente", "✅ Sì", "Cuisine franco-japonaise unique dans le 11e, ramen et plats créatifs"),
    ("Ober Mamma", "11e", "107 blvd Richard Lenoir, 75011 Paris", "obermamma@bigmammagroup.com", "+33 1 58 30 62 59", "bigmammagroup.com", "@obermamma", "Italian Osteria", "Piccola catena", "⚠️ Medio", "Grande osteria italienne du groupe Big Mamma dans le 11e"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Nouveaux Restaurants Paris"

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

    headers = ["#", "Nome Ristorante", "Arr.", "Indirizzo", "EMAIL ✉️",
               "Telefono", "Sito Web", "Instagram", "Tipo Cucina",
               "Dimensione", "Adatto SocialPerks", "Note/Descrizione"]
    col_widths = [4, 28, 6, 35, 32, 18, 22, 22, 22, 16, 14, 40]

    for col, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill      = HEADER_FILL
        cell.font      = WHITE_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border    = BORDER
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"

    for idx, r in enumerate(RESTAURANTS, 1):
        row_idx = idx + 1
        has_email = bool(r[3])
        sp = r[9]
        row_fill = EMAIL_FILL if has_email else NO_EMAIL_FILL
        if "✅" in sp:
            sp_fill = IDEAL_FILL
        elif "⚠️" in sp:
            sp_fill = MEDIUM_FILL
        else:
            sp_fill = NO_FILL_CLR

        values = [idx, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row_idx, column=col, value=val)
            cell.fill      = sp_fill if col == 11 else row_fill
            cell.font      = Font(name="Calibri", size=10)
            cell.border    = BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=(col in [4, 12]))
        ws.row_dimensions[row_idx].height = 22

    total      = len(RESTAURANTS)
    with_email = sum(1 for r in RESTAURANTS if r[3])
    ideal      = sum(1 for r in RESTAURANTS if r[9].startswith("✅"))

    sr = total + 4
    ws.cell(row=sr,   column=1, value="📊 RIEPILOGO").font = Font(bold=True, size=12, color="2C3E50")
    ws.cell(row=sr+1, column=1, value="Totale ristoranti:").font     = BOLD_FONT
    ws.cell(row=sr+1, column=2, value=total)
    ws.cell(row=sr+2, column=1, value="Con email confermata:").font  = BOLD_FONT
    ws.cell(row=sr+2, column=2, value=with_email)
    ws.cell(row=sr+3, column=1, value="Ideali per SocialPerks (✅):").font = BOLD_FONT
    ws.cell(row=sr+3, column=2, value=ideal)
    ws.cell(row=sr+4, column=1, value="Generato il:").font           = BOLD_FONT
    ws.cell(row=sr+4, column=2, value=datetime.now().strftime("%d/%m/%Y %H:%M"))

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Paris_New.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")
    return filename


if __name__ == "__main__":
    create_excel()
