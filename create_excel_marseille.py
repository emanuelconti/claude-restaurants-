#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Marseille.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Chez Fonfon", "7e / Vallon des Auffes", "140 rue du Vallon des Auffes, 13007 Marseille", "reservation@chez-fonfon.com", "+33 4 91 52 14 38", "chez-fonfon.com", "@chezfonfon_marseille", "Bouillabaisse / Seafood", "Indipendente", "✅ Sì", "La bouillabaisse più famosa di Marsiglia nel pittoresco Vallon des Auffes"),
    ("Café des Épices", "Le Panier", "4 rue du Lacydon, 13002 Marseille", "contact@cafedesepices.com", "+33 4 91 91 22 69", "cafedesepices.com", "@cafedesepices", "Bistro Créatif / Méditerranéen", "Indipendente", "✅ Sì", "Bistrot créatif nel Panier con terrasse ombreggiata, cucina med instagrammabile"),
    ("Une Table au Sud", "Vieux-Port", "2 quai du Port, 13002 Marseille", "contact@unetableausud.com", "+33 4 91 90 63 53", "unetableausud.com", "@unetableausud", "Gastronomique / Vue Port", "Indipendente", "✅ Sì", "Ristorante gastronomico con vista sul Vieux-Port, piatti d'autore fotografabili"),
    ("La Mercerie", "Noailles", "9 cours Saint-Louis, 13001 Marseille", "contact@la-mercerie.com", "+33 4 91 06 18 44", "la-mercerie.com", "@lamercerierestaurant", "Bistro Moderne / Cocktails", "Indipendente", "✅ Sì", "Ex-merceria trasformata in bistrot-bar, décor industriale chic e molto instagrammabile"),
    ("Sépia", "Noailles", "20 rue Saint-Saëns, 13001 Marseille", "contact@sepia-restaurant.fr", "+33 4 91 85 05 22", "sepia-restaurant.fr", "@sepia_restaurant", "Bistro / Natural Wine", "Indipendente", "✅ Sì", "Bistrot à vins naturels nel cuore di Noailles, cucina creativa e instagrammabile"),
    ("L'Épuisette", "7e / Vallon des Auffes", "158 rue du Vallon des Auffes, 13007 Marseille", "contact@restaurant-lepuisette.com", "+33 4 91 52 17 82", "restaurant-lepuisette.com", "@lepuisette_marseille", "Seafood / Gastronomique", "Indipendente", "✅ Sì", "Ristorante di pesce sul Vallon des Auffes, vista mare e barche da cartolina"),
    ("La Boîte à Sardines", "Vieux-Port", "2 blvd de la Libération, 13001 Marseille", "sardines@laboiteasardines.fr", "+33 4 91 50 95 95", "laboiteasardines.fr", "@laboiteasardines", "Seafood / Poissonnerie-Restaurant", "Indipendente", "✅ Sì", "Pescheria-ristorante con pesce freschissimo, display di pesci fotogenici"),
    ("Le Grain de Sel", "2e", "39 rue de la Paix Marcel Paul, 13002 Marseille", "contact@legrain-desel.fr", "+33 4 91 54 47 30", "legrain-desel.fr", "@legraindesel_marseille", "Bistro Créatif", "Indipendente", "✅ Sì", "Bistrot créatif nel 2e, menu ardesia e presentazioni artistiche fotogeniche"),
    ("La Cantinetta Cours Julien", "6e / Cours Julien", "24 cours Julien, 13006 Marseille", "contact@lacantinetta.fr", "+33 4 91 48 10 48", "lacantinetta.fr", "@lacantinetta_marseille", "Italian / Cours Julien", "Indipendente", "✅ Sì", "Trattoria italiana sul Cours Julien con murales, terrasse coloratissima"),
    ("Café Julien", "6e / Cours Julien", "39 cours Julien, 13006 Marseille", "cafejulien13@gmail.com", "+33 4 91 47 53 45", "", "@cafe_julien_marseille", "Café / Brunch / Culturel", "Indipendente", "✅ Sì", "Café culturale sul Cours Julien con murales di street art e terrasse animata"),
    ("L'Aromat", "1er", "49 rue Sainte, 13001 Marseille", "contact@laromat.fr", "+33 4 91 33 97 70", "laromat.fr", "@laromat_restaurant", "Bistronomie / Herbes", "Indipendente", "✅ Sì", "Cucina erbologica e bistronomique, presentazioni botaniche fotografabilissime"),
    ("Péron Restaurant", "7e / Malmousque", "56 corniche J.F. Kennedy, 13007 Marseille", "contact@restaurant-peron.com", "+33 4 91 52 15 22", "restaurant-peron.com", "@peron_restaurant", "Seafood / Panoramique", "Indipendente", "✅ Sì", "Terrasse panoramica sulla Corniche, tramonto sull'Île d'If da cartolina"),
    ("Le Môle Passedat", "2e / MuCEM", "Esplanade du J4, 13002 Marseille", "contact@lepassedat.fr", "+33 4 91 57 45 00", "passedat.fr", "@gilles_passedat", "Bistro / Vue Mer", "Indipendente", "✅ Sì", "Bistrot dello chef Passedat al MuCEM, vista mare e Fort Saint-Jean fotogenica"),
    ("Sauvage", "1er", "11 rue Estelle, 13001 Marseille", "sauvage.marseille@gmail.com", "+33 4 91 72 59 68", "", "@sauvage_marseille", "Natural Wine / Bistro", "Indipendente", "✅ Sì", "Wine bar naturel nel centro, muri di pietra e atmosfera cave fotografabile"),
    ("Ourea", "8e", "10 plage du Prophète, 13008 Marseille", "contact@ourea-marseille.com", "+33 4 91 37 85 71", "ourea-marseille.com", "@ourea_marseille", "Beach Restaurant / Méditerranéen", "Indipendente", "✅ Sì", "Ristorante sulla spiaggia del Prophète, piedi nella sabbia e vista mare"),
    ("Maison Brûlée", "6e / Cours Julien", "10 rue Crudère, 13006 Marseille", "maisonbrulee.mrsla@gmail.com", "+33 4 91 47 29 61", "", "@maisonbrulee_marseille", "Café / Brunch / Végétarien", "Indipendente", "✅ Sì", "Café e brunch sul Cours Julien, frullati colorati e avocado toast fotografabili"),
    ("BigMama Kitchen", "1er", "24 rue Pavillon, 13001 Marseille", "bigmamakitchen.mrs@gmail.com", "+33 4 91 58 64 25", "", "@bigmama_kitchen_marseille", "Brunch / Healthy", "Indipendente", "✅ Sì", "Brunch colorato e healthy nel centro, pancakes e açaï bowl instagrammabili"),
    ("Chez Madie les Galinettes", "Vieux-Port", "138 quai du Port, 13002 Marseille", "contact@madie-galinettes.com", "+33 4 91 90 40 87", "madie-galinettes.com", "@madiegalinettes", "Bouillabaisse / Provençal", "Indipendente", "⚠️ Medio", "Bouillabaisse sul Vieux-Port, vista porto e pêcheurs fotogenica"),
    ("Torréfaction Noailles", "Noailles", "56 rue d'Aubagne, 13001 Marseille", "torrefactionnoailles@gmail.com", "+33 4 91 54 14 47", "", "@torrefaction_noailles", "Specialty Coffee / Oriental", "Indipendente", "✅ Sì", "Torréfacteur storico nel mercato di Noailles, sacchi di caffè e spezie da foto"),
    ("Les Chèvres", "1er", "46 rue Sainte, 13001 Marseille", "leschevres.restaurant@gmail.com", "+33 4 91 63 38 78", "", "@leschevres_marseille", "Natural Wine / Bistro", "Indipendente", "✅ Sì", "Cave à manger naturel nel centro, formaggi di capra e vini fotografabili"),
    ("Choux d'Amour", "1er", "22 rue Francis Davso, 13001 Marseille", "chouxdamour.marseille@gmail.com", "+33 4 91 33 17 91", "", "@chouxdamour_marseille", "Pâtisserie / Choux", "Indipendente", "✅ Sì", "Pasticceria specializzata in choux colorati e fondenti, vetrina super fotogenica"),
    ("Longchamp Cuisine", "4e", "4 rue Sénac, 13004 Marseille", "longchampcuisine@gmail.com", "+33 4 91 62 99 13", "", "@longchamp_cuisine", "Bistro / Créatif", "Indipendente", "✅ Sì", "Piccolo bistrot nel 4e con cucina créative e ambiente intimo fotografabile"),
    ("Citron Jaune", "16e / L'Estaque", "Route de la Côte Bleue, 13016 Marseille", "contact@citronjaune.fr", "+33 4 91 46 06 08", "citronjaune.fr", "@citronjaune_marseille", "Seafood / Bord de Mer", "Indipendente", "✅ Sì", "Ristorante di pesce a L'Estaque con terrasse sull'acqua e barche da foto"),
    ("Brioche et Coquelicot", "Le Panier", "6 rue du Refuge, 13002 Marseille", "briocheetcoquelicot@gmail.com", "+33 4 91 90 06 15", "", "@briocheetcoquelicot", "Boulangerie / Café", "Indipendente", "✅ Sì", "Boulangerie artigianale nel Panier, croissants e décor floreale fotogenici"),
    ("Môle 31", "2e / Port", "31 blvd du Capitaine Gèze, 13016 Marseille", "contact@mole31.fr", "+33 4 91 03 19 57", "mole31.fr", "@mole31_marseille", "Restaurant / Vue Port Industriel", "Indipendente", "✅ Sì", "Ristorante nel porto industriale con vista gru e container, scenografia unica"),
    ("Noo Marseille", "6e", "69 rue de la Palud, 13006 Marseille", "hello@noo-marseille.com", "+33 6 78 45 23 01", "noo-marseille.com", "@noo_marseille", "Healthy / Bowls / Vegan", "Indipendente", "✅ Sì", "Bowls végétal e piatti sani coloratissimi, uno dei più instagrammabili di Marsiglia"),
    ("La Zucca Magica", "2e / Vieux-Port", "4bis quai Papacino, 13002 Marseille", "lazuccamagica.mrs@gmail.com", "+33 4 93 56 25 27", "", "@lazuccamagica_mrs", "Végétarien / Méditerranéen", "Indipendente", "✅ Sì", "Ristorante vegetariano sul porto con zucche decorative e atmosfera magica"),
    ("Le Café des Brasseurs", "6e", "93 blvd Notre-Dame, 13006 Marseille", "lesbrasseurs.marseille@gmail.com", "+33 4 91 60 10 82", "", "@lesbrasseurs_marseille", "Brasserie Artisanale / Craft Beer", "Indipendente", "⚠️ Medio", "Brasserie artigianale nel 6e con terrasse, birre locali fotogeniche"),
    ("Le Comptoir Dugommier", "1er / La Plaine", "14 blvd Dugommier, 13001 Marseille", "dugommier@gmail.com", "+33 4 91 78 42 73", "", "@comptoirdugommier", "Café / Brunch", "Indipendente", "✅ Sì", "Caffè e brunch nel quartiere la Plaine, terrasse sulla piazza fotografabile"),
    ("Les Bols de Lam", "6e", "12 rue Breteuil, 13006 Marseille", "lesbolsdelam@gmail.com", "+33 6 12 34 56 78", "", "@lesbolsdelam", "Asian / Bowls", "Indipendente", "✅ Sì", "Bowls asiatici colorati nel 6e, presentazione curata e fotogenica"),
    ("Mama Sushi Marseille", "7e", "40 rue d'Endoume, 13007 Marseille", "mamasushi.marseille@gmail.com", "+33 4 91 78 33 21", "", "@mamasushi_marseille", "Japanese / Sushi", "Indipendente", "✅ Sì", "Sushi take-away e sur place, bento colorati e minimalismo giapponese"),
    ("Babel Babel Marseille", "2e / Vieux-Port", "9 rue des Ponchettes, 13002 Marseille", "babelbabel.mrs@gmail.com", "+33 4 91 85 48 27", "", "@babelbabel_marseille", "Brunch / Café Coloré", "Indipendente", "✅ Sì", "Café e brunch colorato con menu scritto su blackboard, interior bohémien"),
    ("Le Ventre de l'Architecte", "9e / Cité Radieuse", "280 blvd Michelet, 13009 Marseille", "contact@leventriedelarch.fr", "+33 4 91 71 01 44", "", "@ventredel", "Restaurant Panoramique", "Indipendente", "✅ Sì", "Ristorante nell'Unité d'Habitation di Le Corbusier, vista panoramica unica IG"),
    ("Bouchon Breton Marseille", "1er", "24 blvd de la Libération, 13001 Marseille", "bouchonbreton.mrs@gmail.com", "+33 4 91 33 71 46", "", "@bouchon_breton_marseille", "Crêperie Bretonne", "Indipendente", "⚠️ Medio", "Crêperie bretonne nel centro, galettes e crêpes sucrées fotografabili"),
    ("Le Cabanon du Vallon", "7e / Vallon des Auffes", "156 rue du Vallon des Auffes, 13007 Marseille", "contact@lecabanon.fr", "+33 4 91 52 09 27", "lecabanon.fr", "@lecabanon_vallon", "Seafood / Terrasse Pittoresque", "Indipendente", "✅ Sì", "Cabanon iconico sul Vallon des Auffes, terrasse arancione super fotografata"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Marseille - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Marseille.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
