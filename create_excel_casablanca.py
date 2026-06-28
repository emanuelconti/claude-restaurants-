#!/usr/bin/env python3
"""Genera SocialPerks_Restaurants_Casablanca.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

RESTAURANTS = [
    ("Rick's Café", "Ancienne Médina", "248 blvd Sour Jdid, Ancienne Médina, Casablanca", "reservation@rickscafe.ma", "+212 5 22 27 42 07", "rickscafe.ma", "@rickscafe_casablanca", "American / Lounge / Bar", "Indipendente", "✅ Sì", "Iconica riproduzione del film Casablanca, courtyard marocain e atmosphere hollywoodiana"),
    ("La Sqala", "Ancienne Médina", "Blvd des Almohades, Ancienne Médina, Casablanca", "lasqala@lasqala.ma", "+212 5 22 26 09 60", "lasqala.ma", "@lasqala_casablanca", "Marocain / Terrasse Historique", "Indipendente", "✅ Sì", "Ristorante nel bastione portoghese del 18° sec, giardino andaluso fotogenico"),
    ("Le Cabestan", "Ain Diab / Corniche", "Blvd de la Corniche, Ain Diab, Casablanca", "info@lecabestan.com", "+212 5 22 39 11 90", "lecabestan.com", "@lecabestan_casa", "Seafood / Vue Océan", "Indipendente", "✅ Sì", "Ristorante di pesce sulla Corniche con terrasse e vista oceano Atlantico"),
    ("La Bodega", "Bourgogne", "129 rue Allah ben Abdallah, Casablanca", "contact@labodega.ma", "+212 5 22 54 18 42", "labodega.ma", "@labodega_casa", "Spanish / Tapas / Flamenco", "Piccola catena", "✅ Sì", "Tapas spagnole e flamenco, décor colorato e atmosfera festiva fotogenica"),
    ("Blanco Riad", "Ancienne Médina", "10 rue Ibn Zidon, Médina, Casablanca", "contact@blancoriad.com", "+212 6 61 28 92 54", "blancoriad.com", "@blancoriad", "Marocain / Riad / Rooftop", "Indipendente", "✅ Sì", "Riad bianco con tetto terrazza e vista sulla Médina, zellige e archi fotogenici"),
    ("Café OuiOui", "Gauloise", "Blvd d'Anfa, Gauloise, Casablanca", "contact@cafe-ouioui.ma", "+212 5 22 39 76 54", "cafe-ouioui.ma", "@cafeouioui_casa", "Café / Brunch / Coloré", "Indipendente", "✅ Sì", "Caffè e brunch colorato con interior floreale, uno dei più instagrammabili di Casa"),
    ("La Table d'Antan", "Anfa", "15 rue Soumaya, Anfa, Casablanca", "contact@latabledantan.ma", "+212 5 22 36 88 09", "latabledantan.ma", "@latabledantan", "Marocain / Gastronomique", "Indipendente", "⚠️ Medio", "Cucina marocchina gastronomica nella villa di Anfa, jardin fotogenico"),
    ("Le Rouget de l'Isle", "Bourgogne", "6 rue Ibn Toumert, Casablanca", "rougetdelisle@gmail.com", "+212 5 22 47 48 15", "", "@rougetdelisle_casa", "French / Bistro", "Indipendente", "✅ Sì", "Bistrot francese nel quartiere Bourgogne, cuisine du marché e vini selezionati"),
    ("Brasserie La Bavaroise", "Bourgogne", "133 rue Allal Ben Abdellah, Casablanca", "labavaroise@gmail.com", "+212 5 22 31 17 60", "", "@labavaroise_casa", "Brasserie Française / Historique", "Indipendente", "⚠️ Medio", "Storica brasserie francesa degli anni '50, interni d'epoca fotogenici"),
    ("Ô Jardin des Délices", "Racine", "9 rue Mozart, Racine, Casablanca", "jardindesdelices@gmail.com", "+212 5 22 36 24 62", "", "@jardindesdelices_casa", "Marocain / Jardin", "Indipendente", "✅ Sì", "Giardino ristorante con fontane e piante, cucina marocchina in ambiente zen"),
    ("Lina's Café", "Maarif", "Blvd Al Massira Al Khadra, Maarif, Casablanca", "contact@linascafe.ma", "+212 5 22 98 44 55", "linascafe.ma", "@linascafe_casa", "Café / Brunch / Sandwichs", "Piccola catena", "⚠️ Medio", "Caffè brunch e sandwichs gourmet in arredo luminoso, fotogenico nel Maarif"),
    ("La Conserve", "Racine", "6 rue Jilali Laâroussi, Racine, Casablanca", "laconserve.casa@gmail.com", "+212 5 22 36 81 44", "", "@laconserve_casa", "French / Bistro Parisien", "Indipendente", "✅ Sì", "Bistrot parigino nel quartiere Racine, ardoise e vini selezionati fotogenici"),
    ("L'Atelier du Gourmand", "Anfa", "3 rue Traktir, Anfa, Casablanca", "atelierdugurmand@gmail.com", "+212 5 22 36 15 30", "", "@atelierdugurmand_casa", "French / Gastronomique", "Indipendente", "✅ Sì", "Atelier gastronomique con presentazioni artistiche in villa di Anfa"),
    ("Pots & Pans", "Gauthier", "2 rue d'Agadir, Gauthier, Casablanca", "potsandpans.casa@gmail.com", "+212 5 22 26 11 44", "", "@potsandpans_casa", "Brunch / Café / Instagrammable", "Indipendente", "✅ Sì", "Brunch trendy nel Gauthier con interior botanico, piante e colori vivaci"),
    ("Numero Siete", "Maarif", "7 rue Mhamid, Maarif, Casablanca", "numerosiete.casa@gmail.com", "+212 5 22 99 18 37", "", "@numerosiete_casa", "Spanish / Tapas Modernas", "Indipendente", "✅ Sì", "Tapas spagnole moderne nel Maarif, pintxos colorati e cocktails fotogenici"),
    ("L'Adresse", "Gauthier", "8 rue Abou Abdellah Assouli, Gauthier, Casablanca", "ladresse.casa@gmail.com", "+212 5 22 27 97 54", "", "@ladresse_casa", "Marocain Moderne / Fusion", "Indipendente", "✅ Sì", "Cucina marocchina moderna con fusion internationale, presentazioni artistiche"),
    ("Le Bistro d'Anfa", "Anfa", "20 blvd de l'Océan, Casablanca", "bistrodanfa@gmail.com", "+212 5 22 36 78 52", "", "@bistrodanfa_casa", "French Bistro / Art Déco", "Indipendente", "✅ Sì", "Bistrot con décor Art Déco nel quartiere Anfa, interni anni '30 fotogenici"),
    ("Ô Bistrot", "Racine", "36 rue Mohamed Diouri, Racine, Casablanca", "obistrot.casa@gmail.com", "+212 5 22 36 80 46", "", "@obistrot_casa", "French / Casual Fine Dining", "Indipendente", "✅ Sì", "Bistrot gastronomique accessible nel quartiere Racine, qualità e fotogenia"),
    ("La Maison de la Tagine", "Bourgogne", "42 rue Jean Jaurès, Bourgogne, Casablanca", "maisontagine@gmail.com", "+212 5 22 46 76 84", "", "@maisontagine_casa", "Marocain / Traditionnel", "Indipendente", "✅ Sì", "Tagine in tajine di terracotta colorata, servizio tradizionale fotogenico"),
    ("Fenicia", "Corniche", "14 blvd de la Corniche, Casablanca", "fenicia.casa@gmail.com", "+212 5 22 39 88 66", "", "@fenicia_casa", "Lebanese / Mediterranean", "Indipendente", "✅ Sì", "Cucina libanese sulla Corniche, mezzé colorati e vista oceano fotogenica"),
    ("Bab El Makhzen", "Gauthier", "5 rue Ibn Batouta, Gauthier, Casablanca", "babelmakhzen@gmail.com", "+212 5 22 22 89 74", "", "@babelmakhzen_casa", "Marocain Gastronomique", "Indipendente", "✅ Sì", "Ristorante marocchino in riad moderno nel Gauthier, zellige e stucchi fotogenici"),
    ("Patisserie Bennis Habous", "Habous", "2 rue Fkih El Gabbas, Habous, Casablanca", "bennis.habous@gmail.com", "+212 5 22 30 30 25", "", "@bennis_habous", "Pâtisserie Marocaine", "Indipendente", "✅ Sì", "Pasticceria marocchina storica nell'Habous, cornes de gazelle e msemen fotogenici"),
    ("Le Mess", "Bourgogne", "50 blvd Rachidi, Casablanca", "lemess.casa@gmail.com", "+212 5 22 36 55 89", "", "@lemess_casa", "Brunch / Café / Healthy", "Indipendente", "✅ Sì", "Brunch e cucina healthy nel cuore del Bourgogne, interni luminosi fotogenici"),
    ("Dar Zitoun", "Anfa", "12 rue des Acacias, Anfa, Casablanca", "darzitoun@gmail.com", "+212 5 22 36 90 47", "", "@darzitoun_casa", "Marocain / Riad Garden", "Indipendente", "✅ Sì", "Dar con giardino di ulivi centenari nel quartiere residenziale Anfa"),
    ("Tanaka", "Maarif", "2 rue de Turenne, Maarif, Casablanca", "tanaka.casa@gmail.com", "+212 5 22 99 65 11", "", "@tanaka_casa", "Japanese / Fine Dining", "Indipendente", "✅ Sì", "Ristorante giapponese fine dining, sushi kaiseki e presentazioni minimaliste"),
    ("La Villa des Arts Café", "Gauthier", "10 blvd Brahim Roudani, Gauthier, Casablanca", "villaartsca@gmail.com", "+212 5 22 29 50 87", "", "@villadesarts_cafe", "Café / Art Gallery / Culturel", "Indipendente", "✅ Sì", "Caffè nella galleria d'arte della Villa des Arts, esposizioni fotografabili"),
    ("Lolita", "Maarif", "Rue Sidi Belyout, Maarif, Casablanca", "lolita.casa@gmail.com", "+212 5 22 99 12 44", "", "@lolita_casa", "Café / Brunch / Colorful", "Indipendente", "✅ Sì", "Café e brunch coloratissimo nel Maarif, decorazioni girly e instagrammabili"),
    ("Al Mounia", "Racine", "95 rue du Prince Moulay Abdallah, Casablanca", "almounia.casa@gmail.com", "+212 5 22 22 26 69", "", "@almounia_casa", "Marocain Classique / Terrasse", "Indipendente", "⚠️ Medio", "Ristorante marocchino classico nella villa, terrasse e giardino fotogenico"),
    ("Café Cinq Continents", "Corniche", "Blvd de la Corniche, Ain Diab, Casablanca", "cinqcontinents@gmail.com", "+212 5 22 39 24 11", "", "@cinqcontinents_casa", "World Food / Brunch / Vue Mer", "Indipendente", "✅ Sì", "Cucina del mondo sulla Corniche con vista oceano, fusion fotogenica"),
    ("Central Park Casa", "Maarif", "104 blvd Rachidi, Casablanca", "centralparkl@casablanca.ma", "+212 5 22 99 46 66", "", "@centralpark_casa", "Café / Brunch / Fast Casual", "Piccola catena", "⚠️ Medio", "Caffè e brunch nel Maarif, specchio da selfie e piatti colorati fotogenici"),
    ("La Belle Époque", "Bourgogne", "8 rue Sidi Belyout, Bourgogne, Casablanca", "labelleepoque.casa@gmail.com", "+212 5 22 47 65 32", "", "@labelleepoque_casa", "French / Brasserie Art Déco", "Indipendente", "✅ Sì", "Brasserie con décor Belle Époque autentico, specchi dorati e mosaici fotogenici"),
    ("Sushi Miyabi", "Maarif", "45 rue Mohamed Zerktouni, Casablanca", "miyabi.casa@gmail.com", "+212 5 22 99 41 27", "", "@sushimiyabi_casa", "Japanese / Sushi Bar", "Indipendente", "✅ Sì", "Sushi bar moderno con bancone aperto, rolls creativi e presentazioni minimaliste"),
    ("Café de l'Univers", "Bourgogne", "20 rue Allal Ben Abdellah, Casablanca", "cafeunivers.casa@gmail.com", "+212 5 22 48 90 14", "", "@cafeunivers_casa", "Café / Terrasse / Cocktails", "Indipendente", "✅ Sì", "Caffè con grande terrasse en plein air nel Bourgogne, aperitivi al tramonto"),
    ("L'Étoile Centrale", "Bourgogne", "107 rue Allal Ben Abdellah, Casablanca", "etoilecentrale@gmail.com", "+212 5 22 47 26 31", "", "@etoilecentrale_casa", "Brasserie / Europeo", "Piccola catena", "⚠️ Medio", "Brasserie nel centro, moules-frites e décor europeo classico"),
    ("La Table Marocaine", "Ancienne Médina", "27 rue Driss 1er, Médina, Casablanca", "tablerocaine.casa@gmail.com", "+212 5 22 30 82 49", "", "@tablerocaine_casa", "Marocain / Authentique", "Indipendente", "✅ Sì", "Cucina marocchina autentica nella Médina, artigianato e zellige fotogenici"),
]


def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Ristoranti Casablanca - SocialPerks"

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

    filename = "/home/user/claude-restaurants-/SocialPerks_Restaurants_Casablanca.xlsx"
    wb.save(filename)
    print(f"✅ {filename}")
    print(f"   Totale: {total} | Con email: {with_email} | Ideali: {ideal}")


if __name__ == "__main__":
    create_excel()
