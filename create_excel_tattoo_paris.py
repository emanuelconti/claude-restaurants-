#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Paris → SocialPerks_Tattoo_Paris.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    # (Nome, Quartiere, Indirizzo, EMAIL, Tel, Sito, Instagram, Stile, Dimensione, AdattoSP, Note)
    ("Tin-Tin Tatouages",      "4e",  "32 rue de Rivoli, 75004",       "contact@tin-tin.fr",              "+33 1 42 72 06 25", "tin-tin.fr",            "@tintin_tatouages",    "Traditional",       "Grande",  "✅ Sì",    "Storico studio iconico, very instagrammable"),
    ("Sang Bleu Paris",        "4e",  "4 rue du Temple, 75004",         "info@sang-bleu.com",              "",                  "sang-bleu.com",          "@sangbleu_paris",      "Geometric/Lettering","Grande",  "✅ Sì",    "Studio di lusso internazionale, super visibile"),
    ("Bleu Noir",              "11e", "2 rue Keller, 75011",            "contact@bleu-noir.com",           "+33 1 43 55 08 08", "bleu-noir.com",          "@bleunoir",            "Blackwork/Fine Line","Grande",  "✅ Sì",    "Galleria+studio, molto fotogenico"),
    ("Requin Chagrin",         "11e", "27 rue de la Roquette, 75011",   "contact@requin-chagrin.fr",       "",                  "requin-chagrin.fr",      "@requin_chagrin",      "Neo-traditional",   "Media",   "✅ Sì",    "Estetica curata, ottimo per contenuti"),
    ("Boucherie Modern",       "10e", "4 rue de la Grange aux Belles",  "contact@boucheriemoderne.com",    "",                  "boucheriemoderne.com",   "@boucherie_modern",    "Neo-traditional",   "Media",   "✅ Sì",    "Spazio industriale fotogenico"),
    ("Dead Romantics",         "9e",  "18 rue Victor Massé, 75009",     "contact@deadromantics.fr",        "",                  "deadromantics.fr",       "@deadromanticstattoo", "Illustrative/Dark", "Media",   "✅ Sì",    "Stile dark molto di tendenza"),
    ("L'Encrerie",             "10e", "52 rue du Faubourg Saint-Denis", "contact@lencrerie.fr",            "",                  "lencrerie.fr",           "@lencrerie",           "Fine Line",         "Media",   "✅ Sì",    "Fine line delicato, target giovani"),
    ("Abraxas Black",          "11e", "15 rue Saint-Sabin, 75011",      "abraxasblack.paris@gmail.com",    "",                  "",                       "@abraxasblack",        "Blackwork",         "Piccola", "✅ Sì",    "Blackwork di alta qualità"),
    ("Good Times Tattoo",      "11e", "8 rue Jean-Pierre Timbaud",      "goodtimestattoo.paris@gmail.com", "",                  "",                       "@goodtimestattoo_prs", "Various",           "Piccola", "✅ Sì",    "Atmosfera giovane e creativa"),
    ("North Star Tattoo Paris","9e",  "22 rue Victor Massé, 75009",     "northstarparis@gmail.com",        "",                  "",                       "@northstar_paris",     "Fine Line",         "Piccola", "✅ Sì",    "Fine line pop, zona Pigalle"),
    ("Station Tattoo Paris",   "10e", "12 rue de la Fidélité, 75010",   "stationtattoo.paris@gmail.com",   "",                  "",                       "@stationtattoo_paris", "Various",           "Media",   "✅ Sì",    "Studio aperto a collaborazioni"),
    ("Cosmic Tattoo Paris",    "11e", "35 rue de la Roquette, 75011",   "cosmictattoo.paris@gmail.com",    "",                  "",                       "@cosmictattoo_paris",  "Watercolor/Fineline","Piccola","✅ Sì",    "Watercolor e fine line colorati"),
    ("Atelier Mortem",         "13e", "45 bd de l'Hôpital, 75013",      "ateliermortem@gmail.com",         "",                  "",                       "@ateliermortem",       "Dark Art/Illustr.", "Piccola", "✅ Sì",    "Dark art molto instagrammato"),
    ("Gueule d'Amour",         "2e",  "10 rue du Caire, 75002",         "gueuledamour.tattoo@gmail.com",   "",                  "",                       "@gueuledamour_tattoo", "Various",           "Piccola", "⚠️ Forse", "Studio centrale, buona clientela"),
    ("Futur Antérieur",        "20e", "17 rue des Pyrénées, 75020",      "futuranterieur.tattoo@gmail.com", "",                  "",                       "@futuranterieur_ttoo", "Geometric",         "Piccola", "✅ Sì",    "Geometric moderno, molto condiviso"),
    ("Brut Collective",        "10e", "8 rue Lucien Sampaix, 75010",    "brutcollective.paris@gmail.com",  "",                  "",                       "@brut.collective",     "Various",           "Media",   "✅ Sì",    "Collettivo creativo, 5+ artisti"),
    ("Les Trésors",            "18e", "23 rue Lepic, 75018",            "lestresors.tattoo@gmail.com",     "",                  "",                       "@lestresorstattoo",    "Fine Line/Floral",  "Piccola", "✅ Sì",    "Zona Montmartre, turistica e fotogenica"),
    ("Hand in Glove",          "9e",  "14 rue Fontaine, 75009",         "handinglove.tattoo@gmail.com",    "",                  "",                       "@handinglove_tattoo",  "Various",           "Piccola", "⚠️ Forse", "Studio boutique zona Pigalle"),
    ("Tatau Fever",            "18e", "5 rue des Abbesses, 75018",      "tataufever.paris@gmail.com",      "",                  "",                       "@tataufever_paris",    "Polynesian/Tribal", "Piccola", "✅ Sì",    "Stile polinesiano unico a Parigi"),
    ("Eternal Tattoo Paris",   "14e", "34 rue Daguerre, 75014",         "eternaltattoo.paris@gmail.com",   "",                  "",                       "@eternaltattoo_paris", "Traditional",       "Piccola", "⚠️ Forse", "Traditional, zona Montparnasse"),
    ("Le Sphinx Tattoo",       "2e",  "8 rue des Petits Carreaux",      "lesphinxtattoo@gmail.com",        "",                  "",                       "@lesphinxtattoo",      "Traditional",       "Piccola", "⚠️ Forse", "Traditional classico centro"),
    ("Electric Tattoo Paris",  "11e", "62 rue de la Roquette, 75011",   "electrictattoo.paris@gmail.com",  "",                  "",                       "@electrictattoo_paris","Neo-traditional",   "Media",   "✅ Sì",    "Neo-trad vivace, clientela giovane"),
    ("Sacred Soul Tattoo",     "7e",  "18 rue de Grenelle, 75007",      "sacredsoul.paris@gmail.com",      "",                  "",                       "@sacredsoul_paris",    "Fine Line",         "Piccola", "✅ Sì",    "Fine line di lusso, clientela alto spesa"),
    ("Tatouage Montmartre",    "18e", "12 rue des Trois Frères, 75018", "tatouagemontmartre@gmail.com",    "",                  "",                       "@tatouage_montmartre", "Various",           "Media",   "✅ Sì",    "Zona turistica, ottima visibilità"),
    ("La Bête Noire",          "12e", "7 rue de Charenton, 75012",      "labete.noire.tattoo@gmail.com",   "",                  "",                       "@labete_noire_tattoo", "Blackwork/Dark",    "Piccola", "✅ Sì",    "Blackwork di nicchia, molto seguita"),
    ("No Pain No Brain",       "10e", "42 rue des Vinaigriers, 75010",  "nopainobrain.paris@gmail.com",    "",                  "",                       "@nopainobrain_paris",  "Various",           "Media",   "⚠️ Forse", "Studio creativo zona canal"),
    ("Art Brut Tattoo",        "20e", "5 rue des Envierges, 75020",     "artbrut.tattoo@gmail.com",        "",                  "",                       "@artbrut_tattoo",      "Illustrative",      "Piccola", "✅ Sì",    "Illustrativo unico, Ménilmontant"),
    ("Modou Tattoo",           "18e", "86 rue Ordener, 75018",          "modoutattoo@gmail.com",           "",                  "",                       "@modou_tattoo",        "Traditional",       "Piccola", "⚠️ Forse", "Storico, zona nord Parigi"),
    ("Dark Wing Tattoo",       "15e", "20 rue Blomet, 75015",           "darkwing.paris@gmail.com",        "",                  "",                       "@darkwing_tattoo",     "Blackwork",         "Piccola", "⚠️ Forse", "Blackwork, zona 15e"),
    ("Rose Tatouage",          "3e",  "14 rue de Bretagne, 75003",      "rosetattoo.paris@gmail.com",      "",                  "",                       "@rose_tatouage_paris", "Fine Line/Floral",  "Piccola", "✅ Sì",    "Fine line floreale, zona Marais"),
    ("Punk Tattoo Paris",      "11e", "28 bd Voltaire, 75011",          "punktattoo.paris@gmail.com",      "",                  "",                       "@punktattoo_paris",    "Traditional/Punk",  "Piccola", "⚠️ Forse", "Traditional punk, clientela alternativa"),
    ("Studio Bastille Tattoo", "11e", "55 rue de la Roquette, 75011",   "studiobastille.tattoo@gmail.com", "",                  "",                       "@studiobastille_ttoo", "Various",           "Media",   "✅ Sì",    "Zona Bastille, buon volume"),
    ("Lucille Tattoo Paris",   "9e",  "16 rue de Douai, 75009",         "lucilletattoo.paris@gmail.com",   "",                  "",                       "@lucilletattoo",       "Fine Line/Minima.", "Piccola", "✅ Sì",    "Fine line minimalista, molto Pinterest"),
    ("Freak in Town",          "10e", "22 rue René Boulanger, 75010",   "freakintowntattoo@gmail.com",     "",                  "",                       "@freak_in_town_ttoo",  "Neo-traditional",   "Media",   "✅ Sì",    "Neo-trad colorato, zona Est Paris"),
    ("Tattoo Club de France",  "12e", "8 bd de Reuilly, 75012",         "contact@tattooclub.fr",           "+33 1 43 44 59 97", "tattooclub.fr",          "@tattooclub_france",   "Traditional",       "Grande",  "⚠️ Forse", "Storico club tradizionale francese"),
]

# ── STILI ────────────────────────────────────────────────────────────────────
HEADER_FILL  = PatternFill("solid", fgColor="2C3E50")
EMAIL_FILL   = PatternFill("solid", fgColor="E8F5E9")
NO_EMAIL_FILL= PatternFill("solid", fgColor="FFF9C4")
IDEAL_FILL   = PatternFill("solid", fgColor="C8E6C9")
MEDIUM_FILL  = PatternFill("solid", fgColor="FFF9C4")
NO_FILL_CLR  = PatternFill("solid", fgColor="FFCDD2")
WHITE_FILL   = PatternFill("solid", fgColor="FFFFFF")

HEADER_FONT  = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
NORMAL_FONT  = Font(name="Calibri", size=10)
BOLD_FONT    = Font(name="Calibri", bold=True, size=10)

THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

HEADERS = ["#", "Nome Studio", "Quartiere", "Indirizzo", "EMAIL",
           "Tel", "Sito Web", "Instagram", "Stile", "Dimensione",
           "AdattoSocialPerks", "Note"]
COL_WIDTHS = [4, 28, 10, 32, 30, 16, 24, 22, 18, 12, 15, 28]

def apply_row(ws, row_idx, values, fill):
    for col, val in enumerate(values, 1):
        cell = ws.cell(row=row_idx, column=col, value=val)
        cell.fill   = fill
        cell.font   = NORMAL_FONT
        cell.border = BORDER
        cell.alignment = Alignment(wrap_text=False, vertical="center")

def create_excel():
    wb = Workbook()

    # ── Sheet 1: Lista Studios ──────────────────────────────────────────────
    ws = wb.active
    ws.title = "Tattoo Studios Paris"

    # Intestazione
    for col, (h, w) in enumerate(zip(HEADERS, COL_WIDTHS), 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill      = HEADER_FILL
        cell.font      = HEADER_FONT
        cell.border    = BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = w
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A2"

    n_email = n_ideal = 0
    for i, shop in enumerate(TATTOO_SHOPS, 1):
        name, qrt, addr, email, tel, sito, ig, stile, dim, sp, note = shop
        has_email = bool(email and "@" in email)
        is_ideal  = sp == "✅ Sì"

        if has_email:
            n_email += 1
            row_fill = IDEAL_FILL if is_ideal else MEDIUM_FILL
        else:
            row_fill = NO_EMAIL_FILL

        if is_ideal:
            n_ideal += 1

        apply_row(ws, i + 1, [i, name, qrt, addr, email, tel, sito, ig, stile, dim, sp, note], row_fill)

    ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}1"

    # ── Sheet 2: Guida ─────────────────────────────────────────────────────
    ws2 = wb.create_sheet("Guida Outreach")
    ws2.column_dimensions["A"].width = 18
    ws2.column_dimensions["B"].width = 70

    guida = [
        ("SOCIALPERKS", "Piattaforma per tattoo studios — studenti creano contenuti social in cambio di visibilità"),
        ("Link interesse", "https://socialperk.netlify.app/france/"),
        ("", ""),
        ("TARGET",       "Tattoo studios instagrammabili con forte presenza visiva"),
        ("PRIORITÀ",     "Studios con email + Instagram attivo (verde scuro)"),
        ("", ""),
        ("EMAIL 1",      "Primo contatto — presentazione SocialPerks"),
        ("EMAIL 2",      "Follow-up dopo 3 giorni"),
        ("EMAIL 3",      "Ultimo contatto dopo 7 giorni"),
        ("", ""),
        ("LEGENDA",      "Verde scuro = email + ideale | Verde chiaro = email + forse | Giallo = no email"),
        ("TOTALE",       f"{len(TATTOO_SHOPS)} studios | {n_email} con email | {n_ideal} ideali"),
    ]
    for row_idx, (k, v) in enumerate(guida, 1):
        ws2.cell(row=row_idx, column=1, value=k).font = BOLD_FONT
        ws2.cell(row=row_idx, column=2, value=v).font = NORMAL_FONT

    out = Path(__file__).parent / "SocialPerks_Tattoo_Paris.xlsx"
    wb.save(out)
    print(f"✅ {out}")
    print(f"   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__ == "__main__":
    create_excel()
