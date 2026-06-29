#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Lyon → SocialPerks_Tattoo_Lyon.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Art Corpus Tattoo",     "Presqu'île",    "8 rue Mercière, 69002 Lyon",          "contact@artcorpus-tattoo.fr",     "+33 4 78 37 02 20", "artcorpus-tattoo.fr",    "@artcorpus_tattoo",    "Various/Neo-trad",  "Grande",  "✅ Sì",    "Studio storico di Lyon, molto conosciuto"),
    ("Sacred Skin Lyon",      "6e",            "42 rue de Sèze, 69006 Lyon",          "sacredskin.lyon@gmail.com",       "",                  "",                       "@sacredskin_lyon",     "Fine Line/Neo-trad","Media",   "✅ Sì",    "Fine line delicato, clientela upscale"),
    ("Black & Blue Tattoo",   "Croix-Rousse",  "15 bd de la Croix-Rousse, 69004",    "blackblue.lyon@gmail.com",        "",                  "",                       "@blackblue_tattoo",    "Blackwork",         "Media",   "✅ Sì",    "Blackwork con forte presenza IG"),
    ("Cabinet de Curiosités", "6e",            "9 rue Auguste Comte, 69002",          "cabinet.curiosites.lyon@gmail.com","",                 "",                       "@cabinetcuriosites_ly","Illustrative",      "Piccola", "✅ Sì",    "Illustrativo/dark art, molto visuale"),
    ("Heavy Duty Tattoo",     "1er",           "22 rue de la République, 69001",      "heavyduty.lyon@gmail.com",        "",                  "",                       "@heavyduty_lyon",      "Traditional",       "Media",   "⚠️ Forse", "Traditional old school zona centrale"),
    ("Skin Factory Lyon",     "Guillotière",   "67 rue Guillotière, 69007",           "skinfactory.lyon@gmail.com",      "",                  "",                       "@skinfactory_lyon",    "Various",           "Grande",  "⚠️ Forse", "Studio grande, alto volume clienti"),
    ("Les Précieux Tattoo",   "3e",            "12 rue du Commandant Rolland, 69003", "lesprecieux.tattoo@gmail.com",    "",                  "",                       "@lesprecieux_tattoo",  "Fine Line/Floral",  "Piccola", "✅ Sì",    "Fine line floreale, molto Pinterest"),
    ("Wild Panther Tattoo",   "Vieux-Lyon",    "8 rue Saint-Jean, 69005",             "wildpanther.lyon@gmail.com",      "",                  "",                       "@wildpanther_lyon",    "Neo-traditional",   "Piccola", "✅ Sì",    "Zona storica turistica, ottima visibilità"),
    ("Electric Chair Lyon",   "7e",            "34 cours Gambetta, 69007",            "electricchair.lyon@gmail.com",    "",                  "",                       "@electricchair_lyon",  "Neo-traditional",   "Media",   "✅ Sì",    "Neo-trad vivace, giovane clientela"),
    ("Encre & Peau",          "3e",            "5 rue Montesquieu, 69003",            "encre.peau.lyon@gmail.com",       "",                  "",                       "@encre_et_peau_lyon",  "Various",           "Piccola", "⚠️ Forse", "Studio a conduzione familiare"),
    ("La Forge Tattoo",       "Presqu'île",    "3 rue de la Monnaie, 69002",          "laforge.tattoo.lyon@gmail.com",   "",                  "",                       "@laforge_tattoo_lyon", "Blackwork/Metal",   "Piccola", "✅ Sì",    "Stile dark/metal, nicchia molto fedele"),
    ("Studio 69 Tattoo",      "6e",            "69 rue de la Part-Dieu, 69003",       "studio69.tattoo@gmail.com",       "",                  "",                       "@studio69_tattoo",     "Various",           "Media",   "⚠️ Forse", "Studio centrale, buon volume"),
    ("Lyon Tattoo Club",      "Part-Dieu",     "10 cours Lafayette, 69003",           "lyontattooclub@gmail.com",        "",                  "",                       "@lyontattooclub",      "Traditional",       "Grande",  "⚠️ Forse", "Grande spazio, attrattivo per eventi"),
    ("Croix-Rousse Ink",      "Croix-Rousse",  "4 Grande Rue de la Croix-Rousse",    "crr.ink.lyon@gmail.com",          "",                  "",                       "@crr_ink_lyon",        "Fine Line",         "Piccola", "✅ Sì",    "Zona bobo, clientela giovane e creativa"),
    ("Madeleine Tattoo",      "6e",            "18 place Bellecour, 69002",           "madeleine.tattoo@gmail.com",      "",                  "",                       "@madeleine_tattoo",    "Fine Line/Minima.", "Piccola", "✅ Sì",    "Zona Bellecour, molto frequentata"),
    ("Dark Matter Lyon",      "Guillotière",   "45 rue de la Guillotière, 69007",     "darkmatter.lyon@gmail.com",       "",                  "",                       "@darkmatter_lyon",     "Blackwork/Dark",    "Piccola", "✅ Sì",    "Dark blackwork, forte identità visiva"),
    ("Ink Sorcery",           "4e",            "12 rue de la Platière, 69001",        "inksorcery.lyon@gmail.com",       "",                  "",                       "@inksorcery_lyon",     "Illustrative",      "Piccola", "✅ Sì",    "Illustrativo fantasy, nicchia appassionata"),
    ("Atelier du Tatouage",   "2e",            "22 rue Victor Hugo, 69002",           "ateliertatouage.lyon@gmail.com",  "",                  "",                       "@atelier_tattoo_lyon", "Fine Line",         "Piccola", "⚠️ Forse", "Studio boutique zona centrale"),
    ("Rose Noire Tattoo",     "1er",           "8 rue Grenette, 69001",               "rosenoire.tattoo@gmail.com",      "",                  "",                       "@rosenoire_tattoo",    "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad femminile, molto Instagrammato"),
    ("Tattoo Paradise Lyon",  "Bron",          "15 rue du Midi, 69500 Bron",          "tattooparadise.lyon@gmail.com",   "",                  "",                       "@tattooparadise_lyon", "Various",           "Grande",  "⚠️ Forse", "Grande studio periferia est"),
]

HEADER_FILL  = PatternFill("solid", fgColor="2C3E50")
EMAIL_FILL   = PatternFill("solid", fgColor="E8F5E9")
NO_EMAIL_FILL= PatternFill("solid", fgColor="FFF9C4")
IDEAL_FILL   = PatternFill("solid", fgColor="C8E6C9")
MEDIUM_FILL  = PatternFill("solid", fgColor="FFF9C4")
NO_FILL_CLR  = PatternFill("solid", fgColor="FFCDD2")
HEADER_FONT  = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
NORMAL_FONT  = Font(name="Calibri", size=10)
BOLD_FONT    = Font(name="Calibri", bold=True, size=10)
THIN = Side(style="thin", color="CCCCCC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEADERS = ["#","Nome Studio","Quartiere","Indirizzo","EMAIL","Tel","Sito Web","Instagram","Stile","Dimensione","AdattoSocialPerks","Note"]
COL_WIDTHS = [4,28,14,34,30,16,22,22,18,12,15,28]

def apply_row(ws, row_idx, values, fill):
    for col, val in enumerate(values, 1):
        cell = ws.cell(row=row_idx, column=col, value=val)
        cell.fill = fill; cell.font = NORMAL_FONT; cell.border = BORDER
        cell.alignment = Alignment(wrap_text=False, vertical="center")

def create_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Tattoo Studios Lyon"
    for col,(h,w) in enumerate(zip(HEADERS,COL_WIDTHS),1):
        cell = ws.cell(row=1,column=col,value=h)
        cell.fill=HEADER_FILL; cell.font=HEADER_FONT; cell.border=BORDER
        cell.alignment=Alignment(horizontal="center",vertical="center")
        ws.column_dimensions[get_column_letter(col)].width=w
    ws.row_dimensions[1].height=22; ws.freeze_panes="A2"
    n_email=n_ideal=0
    for i,shop in enumerate(TATTOO_SHOPS,1):
        name,qrt,addr,email,tel,sito,ig,stile,dim,sp,note=shop
        has_email=bool(email and "@" in email); is_ideal=sp=="✅ Sì"
        if has_email: n_email+=1; row_fill=IDEAL_FILL if is_ideal else MEDIUM_FILL
        else: row_fill=NO_EMAIL_FILL
        if is_ideal: n_ideal+=1
        apply_row(ws,i+1,[i,name,qrt,addr,email,tel,sito,ig,stile,dim,sp,note],row_fill)
    ws.auto_filter.ref=f"A1:{get_column_letter(len(HEADERS))}1"
    ws2=wb.create_sheet("Guida Outreach")
    ws2.column_dimensions["A"].width=18; ws2.column_dimensions["B"].width=70
    for row_idx,(k,v) in enumerate([
        ("SOCIALPERKS","Piattaforma per tattoo studios — studenti creano contenuti social"),
        ("Link","https://socialperk.netlify.app/france/"),
        ("TOTALE",f"{len(TATTOO_SHOPS)} studios | {n_email} con email | {n_ideal} ideali"),
    ],1):
        ws2.cell(row=row_idx,column=1,value=k).font=BOLD_FONT
        ws2.cell(row=row_idx,column=2,value=v).font=NORMAL_FONT
    out=Path(__file__).parent/"SocialPerks_Tattoo_Lyon.xlsx"
    wb.save(out)
    print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
