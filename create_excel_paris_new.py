#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Paris_New.xlsx — nuovi lead Parigi"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Septime", "11e", "80 rue de Charonne, 75011 Paris", "reservation@septime-charonne.fr", "+33 1 43 67 38 29", "septime-charonne.fr", "@septime_paris", "Bistronomie / Farm-to-table", "Indipendente", "✅ Sì", "Uno dei bistrot più acclamati di Parigi, presentazioni minimaliste molto fotografate"),
    ("Clown Bar", "11e", "114 rue Amelot, 75011 Paris", "clownbar.paris@gmail.com", "+33 1 43 55 87 35", "", "@clownbarofficial", "Natural Wine / Bistro / Art", "Indipendente", "✅ Sì", "Ex-bar del circo con affreschi Art Nouveau, uno dei più instagrammabili di Parigi"),
    ("Le Mary Celeste", "3e / Marais", "1 rue Commines, 75003 Paris", "contact@lemaryceleste.com", "+33 1 42 77 23 32", "lemaryceleste.com", "@lemaryceleste", "Oyster Bar / Cocktails", "Indipendente", "✅ Sì", "Ostricheria-cocktail bar nel Marais, ostriche e drinks fotogenici"),
    ("Frenchie", "2e", "5 rue du Nil, 75002 Paris", "contact@frenchie-restaurant.com", "+33 1 40 39 96 19", "frenchie-restaurant.com", "@frenchierestaurant", "Bistronomie Moderne", "Indipendente", "✅ Sì", "Bistrot gastronomique iconico del 2e, sala piccola e molto prenotata"),
    ("Café Kitsuné", "1er / Palais-Royal", "51 galerie de Montpensier, 75001 Paris", "contact@cafekitsune.com", "+33 1 42 60 97 53", "cafekitsune.com", "@cafekitsune", "Specialty Coffee / Japonais", "Piccola catena", "✅ Sì", "Caffè fashion-forward nei giardini del Palais-Royal, colazioni iconiche"),
    ("Broken Arm", "3e / Marais", "12 rue Perrée, 75003 Paris", "contact@the-broken-arm.com", "+33 1 44 61 53 60", "the-broken-arm.com", "@thebrokenarm", "Café / Concept Store / Design", "Indipendente", "✅ Sì", "Caffè nel concept store design del Marais, interni minimal très fotografati"),
    ("Ten Belles", "10e / Canal Saint-Martin", "10 rue de la Grange aux Belles, 75010 Paris", "hello@tenbelles.com", "+33 1 42 40 90 78", "tenbelles.com", "@tenbelles", "Specialty Coffee / Brunch", "Piccola catena", "✅ Sì", "Specialty coffee sul Canal Saint-Martin, brunch e latte art fotogenici"),
    ("Le Servan", "11e", "32 rue Saint-Maur, 75011 Paris", "leservan@gmail.com", "+33 1 55 28 51 82", "leservan.com", "@leservan_paris", "Bistronomie Franco-Asiatique", "Indipendente", "✅ Sì", "Bistrot franco-asiatico dell'11e, piatti fusion creativi fotografabili"),
    ("Yard Wine Bar", "11e", "6 rue de Mont-Louis, 75011 Paris", "yard.paris@gmail.com", "+33 1 40 09 70 30", "", "@yardwinebar", "Natural Wine Bar / Courtyard", "Indipendente", "✅ Sì", "Wine bar con courtyard interieur, vini naturali e atmosfera cave fotogenica"),
    ("Le Grand Bain", "20e / Belleville", "14 rue Denoyez, 75020 Paris", "contact@legrandbain.fr", "+33 1 58 30 88 07", "legrandbain.fr", "@legrandbain", "Natural Wine / Bistronomie", "Indipendente", "✅ Sì", "Bistrot e wine bar nel cuore di Belleville, street art e atmosfera fotografabile"),
    ("Café Oberkampf", "11e", "3 rue Neuve Popincourt, 75011 Paris", "cafeoberkampf@gmail.com", "+33 1 43 57 75 47", "", "@cafeoberkampf", "Café / Brunch / Bar", "Indipendente", "✅ Sì", "Caffè e brunch all'Oberkampf, atmosfera hipster e terrasse fotografabile"),
    ("Buvette Gastrothèque", "9e / Pigalle", "28 rue Henry Monnier, 75009 Paris", "contact@ilovebuvette.com", "+33 1 44 63 41 71", "ilovebuvette.com", "@ilovebuvette", "French / Wine / Cosy", "Indipendente", "✅ Sì", "Gastrothèque dal decor vintage nel SoPi, ardoise e bottiglie fotogenici"),
    ("Holybelly 5", "10e / Canal", "5 rue Lucien Sampaix, 75010 Paris", "contact@holybelly.fr", "+33 1 82 28 00 80", "holybelly.fr", "@holybelly5", "Brunch / Coffee / Australian", "Indipendente", "✅ Sì", "Brunch australiano sul Canal Saint-Martin, pancakes e flat white iconici"),
    ("Balagan", "1er", "9 rue d'Alger, 75001 Paris", "contact@balagan-paris.com", "+33 1 40 20 72 14", "balagan-paris.com", "@balaganparis", "Israeli / Middle Eastern", "Indipendente", "✅ Sì", "Cucina israeliana gourmet nel 1er, mezzé colorati e hummus fotografabile"),
    ("Perché", "11e", "7 rue de la Forge Royale, 75011 Paris", "perche.paris@gmail.com", "+33 1 43 70 26 27", "", "@perche_paris", "Café / Brunch / Terrasse", "Indipendente", "✅ Sì", "Caffè con terrasse segreta nell'11e, piatti colorati e giardino segreto"),
    ("Le Petit Keller", "11e", "13 rue Keller, 75011 Paris", "lepetikkeller@gmail.com", "+33 1 47 00 12 97", "", "@lepetikeller", "Bistro / Natural Wine", "Indipendente", "✅ Sì", "Piccolo bistrot a vini naturali a Bastille, atmosfera intima e fotografabile"),
    ("Fulgurances L'Adresse", "11e", "10 rue Alexandre Dumas, 75011 Paris", "contact@fulgurances.com", "+33 1 71 19 37 37", "fulgurances.com", "@fulgurances", "Pop-up / Chef en Résidence", "Indipendente", "✅ Sì", "Ristorante pop-up con chef en résidence, piatti innovativi molto fotografati"),
    ("Mokonuts", "11e", "5 rue Saint-Bernard, 75011 Paris", "contact@mokonuts.com", "+33 1 82 28 00 63", "mokonuts.com", "@mokonuts", "Café / Pâtisserie / Levantine", "Indipendente", "✅ Sì", "Caffè pasticceria con influenze levantine, cookies e piatti del giorno fotogenici"),
    ("Café Verlet", "1er", "256 rue Saint-Honoré, 75001 Paris", "contact@cafeverlet.com", "+33 1 42 60 67 39", "cafeverlet.com", "@cafeverlet", "Torréfaction / Café Historique", "Indipendente", "✅ Sì", "Torréfacteur storico dal 1880 vicino al Louvre, sacchi di caffè fotogenici"),
    ("Au Passage", "11e", "1bis passage Saint-Sébastien, 75011 Paris", "aupassage.paris@gmail.com", "+33 1 43 55 07 52", "", "@aupassage_paris", "Natural Wine / Small Plates", "Indipendente", "✅ Sì", "Wine bar e piccoli piatti in passaggio nel Marais, molto instagrammabile"),
    ("Épicerie Verte", "11e", "48 rue de Cîteaux, 75012 Paris", "epicerieverte@gmail.com", "+33 1 43 40 73 21", "", "@epicerieverte", "Épicerie Bio / Café", "Indipendente", "✅ Sì", "Épicerie bio e caffè nell'12e, colori naturali e atmosfera organic fotogenica"),
    ("Le Syndicat", "10e", "51 rue du Faubourg Saint-Denis, 75010 Paris", "contact@syndicatcocktailclub.com", "+33 1 45 23 24 44", "syndicatcocktailclub.com", "@syndicat_fsd", "Cocktail Bar / French Spirits", "Indipendente", "✅ Sì", "Cocktail bar con soli spirits francesi nel Faubourg Saint-Denis"),
    ("Café Panache", "11e", "1 rue Trousseau, 75011 Paris", "cafepanache.paris@gmail.com", "+33 1 48 07 14 25", "", "@cafepanache_paris", "Café / Brunch Cosy", "Indipendente", "✅ Sì", "Caffè e brunch all'angolo del Marais-Bastille, interni caldi fotografabili"),
    ("Liberté Patisserie Boulangerie", "10e", "39 rue des Vinaigriers, 75010 Paris", "liberte@liberteparis.fr", "+33 1 42 05 51 76", "liberteparis.fr", "@liberte_paris", "Boulangerie / Pâtisserie Tendance", "Indipendente", "✅ Sì", "Boulangerie di design nel 10e, viennoiseries colorate e molto instagrammabili"),
    ("Hoca", "18e / Montmartre", "9 rue de l'Abreuvoir, 75018 Paris", "hoca.paris@gmail.com", "+33 1 46 06 65 87", "", "@hoca_paris", "Café / Brunch / Montmartre", "Indipendente", "✅ Sì", "Caffè e brunch nell'una delle strade più belle di Montmartre, vista iconique"),
    ("Maison Plisson", "3e / Marais", "93 blvd Beaumarchais, 75003 Paris", "contact@lamaisonplisson.com", "+33 1 71 18 19 09", "lamaisonplisson.com", "@maisonplisson", "Épicerie Fine / Café / Traiteur", "Indipendente", "✅ Sì", "Épicerie di design al Marais, prodotti gourmet e café fotogenico"),
    ("Café Chilango", "11e", "35 rue de Lappe, 75011 Paris", "cafechilango@gmail.com", "+33 1 48 07 02 38", "", "@cafechilango_paris", "Mexican / Street Food / Brunch", "Indipendente", "✅ Sì", "Cucina messicana e brunch coloratissimo a Bastille, tacos fotogenici"),
    ("Bones Restaurant", "11e", "43 rue Godefroy Cavaignac, 75011 Paris", "contact@bonesrestaurant.fr", "+33 1 43 70 95 38", "bonesrestaurant.fr", "@bonesrestaurant", "Bistronomie / Cave", "Indipendente", "✅ Sì", "Bistrot moderno nell'11e con ampia selezione di vini naturali fotogenici"),
    ("Brasserie Dubillot", "2e", "18 rue Bachaumont, 75002 Paris", "brasseriedubillot@gmail.com", "+33 1 40 26 02 00", "", "@brasseriedubillot", "Brasserie Parisian / Retro", "Indipendente", "✅ Sì", "Brasserie con décor retro anni '80 nel Sentier, zinc bar molto fotografato"),
    ("Le Barbouquin", "11e", "1 rue Théophile Roussel, 75011 Paris", "lebarbouquin@gmail.com", "+33 1 43 71 42 62", "", "@lebarbouquin", "Café / Librairie / Brunch", "Indipendente", "✅ Sì", "Caffè-libreria nel 11e vicino al mercato d'Aligre, atmosfera culturale fotogenica"),
    ("Jah Jah by Le Tricycle", "10e", "11 rue des Petites Écuries, 75010 Paris", "contact@jahjahparis.com", "+33 1 47 70 03 51", "jahjahparis.com", "@jahjah_paris", "Vegan / Afro-Caribbean", "Indipendente", "✅ Sì", "Cucina vegana afro-caraibica nel 10e, colori vivaci e piatti fotografabili"),
    ("Le Rigmarole", "11e", "10 rue du Grand Prieuré, 75011 Paris", "contact@lerigmarole.com", "+33 1 71 24 58 72", "lerigmarole.com", "@lerigmarole", "Japanese / Italian Fusion", "Indipendente", "✅ Sì", "Cucina italo-giapponese sperimentale nell'11e, pasta fatta a mano fotogenica"),
    ("Septime La Cave", "11e", "3 rue Basfroi, 75011 Paris", "lacave@septime-charonne.fr", "+33 1 43 67 14 87", "septime-charonne.fr", "@septimecave", "Natural Wine Bar / Small Plates", "Indipendente", "✅ Sì", "Cave à vins naturels del gruppo Septime, muri di pietra e bottiglie fotogenici"),
    ("Les Arlots", "10e", "136 rue du Faubourg-Poissonnière, 75010 Paris", "contact@lesarlots.com", "+33 1 42 82 92 01", "lesarlots.com", "@lesarlots_paris", "Bistronomie / Charcuterie", "Indipendente", "✅ Sì", "Bistrot naturel nel 10e, charcuterie maison e cave à manger fotogenica"),
    ("Café Martha", "11e", "93 blvd du Temple, 75003 Paris", "cafemartha.paris@gmail.com", "+33 1 43 38 16 27", "", "@cafemartha_paris", "Café / Brunch / Trendy", "Indipendente", "✅ Sì", "Caffè trendy al confine Marais-Republique, brunches colorati e molto fotografati"),
    ("Virtus", "12e / Nation", "29 rue de Cotte, 75012 Paris", "contact@virtus-paris.com", "+33 1 40 09 70 63", "virtus-paris.com", "@virtus_paris", "French / Japanese Gastronomique", "Indipendente", "✅ Sì", "Bistronomie franco-giapponese in rue de Cotte, presentazioni artistiche fotogeniche"),
    ("Le Barav", "3e / Marais", "6 rue Charles-François Dupuis, 75003 Paris", "lebarav.paris@gmail.com", "+33 1 48 04 57 59", "", "@lebarav_paris", "Wine Bar / Israeli", "Indipendente", "✅ Sì", "Wine bar israeliano nel Marais, mezzé colorati e selezione di vins natures"),
    ("Café de Flore", "6e / Saint-Germain", "172 blvd Saint-Germain, 75006 Paris", "cafedeflore@wanadoo.fr", "+33 1 45 48 55 26", "cafedeflore.fr", "@cafedflore", "Café / Littéraire / Historique", "Indipendente", "⚠️ Medio", "Caffè letterario storico di Saint-Germain, uno dei più fotografati del mondo"),
    ("La Recyclerie", "18e / Montmartre", "83 blvd Ornano, 75018 Paris", "contact@larecyclerie.com", "+33 1 42 57 58 49", "larecyclerie.com", "@larecyclerie", "Café / Concept Éco / Garden", "Indipendente", "✅ Sì", "Ex-stazione ferroviaria trasformata in eco-café, giardino e polli fotogenici"),
    ("Café du Coin", "11e", "9 rue Camille Desmoulins, 75011 Paris", "cafecoin.paris@gmail.com", "+33 1 43 67 30 30", "", "@cafedcoin_paris", "Café / Bistronomie / Natural Wine", "Indipendente", "✅ Sì", "Caffè e bistrot di quartiere nell'11e con vini naturali selezionati"),
    ("Pink Mamma Parigi", "9e / Pigalle", "20bis rue de Douai, 75009 Paris", "pigalle@bigmammagroup.com", "+33 1 83 74 99 11", "bigmammagroup.com", "@pinkmamma_paris", "Italian / Multi-Etage / Pink", "Piccola catena", "✅ Sì", "Ristorante italiano Big Mamma su 5 piani, décor floreale rosa super instagrammabile"),
    ("Yard", "11e", "6 rue de Mont-Louis, 75011 Paris", "yard.winebar@gmail.com", "+33 1 40 09 70 30", "", "@yard_winebar", "Natural Wine / Bar / Courtyard", "Indipendente", "✅ Sì", "Wine bar con cortile interiore e atmosfera cave, très fotogenico"),
    ("Deux Fois Plus de Piment", "20e / Belleville", "33 blvd de Belleville, 75011 Paris", "2foispluspiment@gmail.com", "+33 1 43 55 15 21", "", "@deuxfoisplusdepiment", "Chinese / Sichuan Street Food", "Indipendente", "✅ Sì", "Cucina sichuanese di Belleville, hotpot fumante e colori rosso fotogenici"),
    ("Brutos", "20e / Nation", "32 rue des Orteaux, 75020 Paris", "contact@brutos.fr", "+33 1 43 73 54 28", "brutos.fr", "@brutos_paris", "Modern Brazilian / Grill", "Indipendente", "✅ Sì", "Cucina brasiliana moderna nel 20e, grill fumante e ingredienti colorati"),
    ("Café Compagnon", "1er", "22 rue Croix des Petits Champs, 75001 Paris", "cafecompagnon.paris@gmail.com", "+33 1 40 26 36 39", "", "@cafecompagnon_paris", "Café / Brunch / Boulangerie", "Indipendente", "✅ Sì", "Caffè e boulangerie nel 1er con pane artigianale, colazioni fotografabili"),
    ("Les Enfants du Marché", "3e / Marais", "39 rue de Bretagne, 75003 Paris", "contact@lesenfantsdumarche.com", "+33 1 42 77 86 53", "lesenfantsdumarche.com", "@lesenfantsdumarche", "Marché Couvert / Wine / Tapas", "Indipendente", "✅ Sì", "Bar à vins nel mercato coperto delle Enfants Rouges, banchi fotogenici"),
    ("Flore en l'Île", "4e / Île Saint-Louis", "42 quai d'Orléans, 75004 Paris", "floreenlile@gmail.com", "+33 1 43 29 88 27", "", "@floreenlile", "Café / Vue Notre-Dame / Sorbet", "Indipendente", "✅ Sì", "Caffè con terrasse e vista Notre-Dame sull'Île Saint-Louis, panorama iconico"),
    ("Café Pinson", "3e / Marais", "6 rue du Forez, 75003 Paris", "contact@cafe-pinson.fr", "+33 1 58 00 44 55", "cafe-pinson.fr", "@cafepinson", "Vegan / Brunch / Coloré", "Piccola catena", "✅ Sì", "Caffè vegano nel Marais, açaï bowls e Buddha bowls coloratissimi fotogenici"),
    ("Fragments Paris", "3e", "76 rue des Tournelles, 75003 Paris", "contact@fragmentsparis.com", "+33 9 77 62 36 45", "fragmentsparis.com", "@fragmentsparis", "Specialty Coffee / Cantine", "Indipendente", "✅ Sì", "Specialty coffee in ex-atelier nel Marais, industrial chic e colazioni fotogeniche"),
    ("Elmer", "3e", "30 rue Notre-Dame de Nazareth, 75003 Paris", "elmer.paris@gmail.com", "+33 1 42 74 35 36", "", "@elmerrestaurant", "Bistronomie / Fusion", "Indipendente", "✅ Sì", "Bistrot gastronomique nel 3e, cucina fusion con presentazioni curatissime"),
    ("Café du Marché", "15e", "38 rue Cler, 75007 Paris", "cafedumarcheruecler@gmail.com", "+33 1 47 34 62 61", "", "@cafedumarcheparis", "Café / Marché / Authentique", "Indipendente", "⚠️ Medio", "Caffè sul mercato storico Rue Cler, terrasse e prodotti freschi fotogenici"),
    ("Marcelle Café", "14e", "2 rue Vandamme, 75014 Paris", "marcelleparis@gmail.com", "+33 1 43 20 91 23", "", "@marcelle_cafe", "Café / Brunch / Vegan", "Indipendente", "✅ Sì", "Caffè vegan e brunch colorato nel 14e vicino Montparnasse"),
    ("La Dernière Goutte", "6e", "6 rue de Bourbon le Château, 75006 Paris", "contact@ladernieregoutte.net", "+33 1 43 29 11 62", "ladernieregoutte.net", "@ladernieregoutte", "Cave à Vins / Wine Bar", "Indipendente", "✅ Sì", "Piccola cave à vins a Saint-Germain, selezione boutique e atmosfera intima"),
    ("Chez Omar", "3e / Marais", "47 rue de Bretagne, 75003 Paris", "chezomar.paris@gmail.com", "+33 1 42 72 36 26", "", "@chezomar_paris", "Algerian / Couscous", "Indipendente", "✅ Sì", "Trattoria algerina storica vicino al Marché des Enfants Rouges, semplice e fotogenica"),
    ("Folderol", "11e", "8 rue de la Main d'Or, 75011 Paris", "folderol.paris@gmail.com", "+33 1 48 07 31 04", "", "@folderol_paris", "Natural Wine / Bistro Créatif", "Indipendente", "✅ Sì", "Bistrot créatif e wine bar naturel nell'11e, atmosfera intime e fotogenica"),
    ("Sushi B", "2e", "5 rue Rambuteau, 75004 Paris", "contact@sushi-b.fr", "+33 1 40 27 95 75", "sushi-b.fr", "@sushi_b_paris", "Japanese / Omakase", "Indipendente", "⚠️ Medio", "Omakase giapponese nel cuore di Parigi, presentazioni minimaliste fotogeniche"),
    ("Hébé", "11e", "11 rue Saint-Sabin, 75011 Paris", "hebe.paris@gmail.com", "+33 1 48 05 45 23", "", "@hebe_paris", "Natural Wine / Bistro", "Indipendente", "✅ Sì", "Wine bar e bistrot all'11e, muri di pietra e bottiglie muri fotogenici"),
    ("Ô Château Caveau", "1er", "68 rue Jean-Jacques Rousseau, 75001 Paris", "contact@o-chateau.com", "+33 1 44 73 97 80", "o-chateau.com", "@ochateau_paris", "Wine Bar / Cave / Dégustation", "Indipendente", "✅ Sì", "Wine bar parigino di riferimento con cave voûtée fotogenica"),
    ("Café Lomi", "18e", "3ter rue Marcadet, 75018 Paris", "contact@cafelomi.com", "+33 1 42 08 63 66", "cafelomi.com", "@cafelomi", "Specialty Coffee / Torréfaction", "Indipendente", "✅ Sì", "Torréfacteur e caffè nel 18e, sacchi di caffè verde e atelier molto fotografato"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Paris New Leads - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Paris_New.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
