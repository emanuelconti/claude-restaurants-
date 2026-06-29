#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Bordeaux → SocialPerks_Tattoo_Bordeaux.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Black Market Tattoo",    "Saint-Pierre",  "12 rue des Remparts, 33000",          "blackmarket.bordeaux@gmail.com",  "",  "",  "@blackmarket_bdx",      "Blackwork",         "Media",   "✅ Sì",    "Blackwork di punta a Bordeaux"),
    ("La Fonderie Tattoo",     "Bacalan",       "3 quai de Bacalan, 33300",            "lafonderie.tattoo@gmail.com",     "",  "",  "@lafonderie_tattoo",    "Neo-traditional",   "Media",   "✅ Sì",    "Spazio industriale iconico, molto fotogenico"),
    ("Wild Roots Tattoo",      "Chartrons",     "22 rue Notre-Dame, 33000",            "wildroots.bordeaux@gmail.com",    "",  "",  "@wildroots_bordeaux",   "Botanical/Fine Ln", "Piccola", "✅ Sì",    "Fine line botanico, zona Chartrons trendy"),
    ("Ink Bordeaux",           "Chartrons",     "8 rue du Palais-Gallien, 33000",      "ink.bordeaux@gmail.com",          "",  "",  "@ink_bordeaux",         "Fine Line",         "Media",   "✅ Sì",    "Fine line moderno, clientela giovane"),
    ("Dark Ink Bordeaux",      "Saint-Michel",  "15 rue des Faures, 33800",            "darkink.bordeaux@gmail.com",      "",  "",  "@darkink_bordeaux",     "Dark Art",          "Piccola", "✅ Sì",    "Dark art/blackwork, zona alternativa"),
    ("Sacred Temple Bordeaux", "Caudéran",      "45 av de Caudéran, 33200",            "sacredtemple.bdx@gmail.com",      "",  "",  "@sacredtemple_bdx",     "Neo-traditional",   "Media",   "⚠️ Forse", "Neo-trad colorato, zona residenziale"),
    ("Original Ink",           "Mériadeck",     "20 rue du Château d'Eau, 33000",      "originalink.bordeaux@gmail.com",  "",  "",  "@originalink_bdx",      "Various",           "Media",   "⚠️ Forse", "Studio polivalente zona centro"),
    ("The Black Rose BDX",     "Victoire",      "5 place de la Victoire, 33000",       "theblackrose.bdx@gmail.com",      "",  "",  "@blackrose_bdx",        "Blackwork/Neo-trad","Piccola", "✅ Sì",    "Zona universitaria, clientela giovane"),
    ("Electric Bordeaux",      "Saint-Pierre",  "8 rue Saint-James, 33000",            "electric.bordeaux@gmail.com",     "",  "",  "@electric_bordeaux",    "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad, cuore storico di Bordeaux"),
    ("Atelier Tattoo BDX",     "Chartrons",     "35 cours Portal, 33300",              "atelier.tattoo.bdx@gmail.com",    "",  "",  "@atelier_tattoo_bdx",   "Fine Line",         "Piccola", "✅ Sì",    "Boutique studio zona Chartrons"),
    ("Garonne Ink",            "Bacalan",       "12 quai des Chartrons, 33300",        "garonne.ink@gmail.com",           "",  "",  "@garonne_ink",          "Various",           "Media",   "⚠️ Forse", "Vista fiume, spazio fotogenico"),
    ("Cosmic Body Bordeaux",   "Capucins",      "18 place des Capucins, 33800",        "cosmicbody.bdx@gmail.com",        "",  "",  "@cosmicbody_bdx",       "Watercolor",        "Piccola", "✅ Sì",    "Watercolor colorato, zona mercato"),
    ("Iron & Ink BDX",         "Bastide",       "5 rue Lucien Faure, 33100",           "ironink.bdx@gmail.com",           "",  "",  "@ironink_bdx",          "Traditional",       "Piccola", "⚠️ Forse", "Traditional, riva destra Garonne"),
    ("Brut Tattoo Bordeaux",   "Saint-Michel",  "3 rue Camille Sauvageau, 33800",      "brut.tattoo.bdx@gmail.com",       "",  "",  "@brut_tattoo_bdx",      "Blackwork/Illustr.","Piccola", "✅ Sì",    "Illustrativo dark, quartiere alternativo"),
    ("Studio Victoire Tattoo", "Victoire",      "10 rue Ravez, 33000",                 "studiovictoire.tattoo@gmail.com", "",  "",  "@studiovictoire_ttoo",  "Fine Line/Geom.",   "Piccola", "✅ Sì",    "Fine line geometrico, zona studenti"),
    ("Bordeaux Tattoo Studio", "Centre",        "25 rue Sainte-Catherine, 33000",      "bordeaux.tattoo.studio@gmail.com","",  "",  "@bdx_tattoo_studio",    "Various",           "Grande",  "⚠️ Forse", "Rue piétonne, massima visibilità"),
    ("Maison de l'Encre",      "Chartrons",     "7 rue Borie, 33300",                  "maisondelencre.bdx@gmail.com",    "",  "",  "@maisondelencre_bdx",   "Fine Line",         "Piccola", "✅ Sì",    "Boutique chic zona Chartrons"),
    ("Périgord Ink",           "Mériadeck",     "14 rue du Château Trompette, 33000",  "perigordink.bdx@gmail.com",       "",  "",  "@perigordink_bdx",      "Neo-traditional",   "Piccola", "⚠️ Forse", "Neo-trad zona affari"),
    ("Black Forest BDX",       "Saint-Genès",   "22 rue de Pessac, 33000",             "blackforest.bdx@gmail.com",       "",  "",  "@blackforest_bdx",      "Blackwork",         "Piccola", "✅ Sì",    "Blackwork botanico, zona università"),
    ("Tattoo Collectif BDX",   "Bacalan",       "6 rue Achard, 33300",                 "tattoo.collectif.bdx@gmail.com",  "",  "",  "@tattoocollectif_bdx",  "Various",           "Grande",  "✅ Sì",    "Collettivo 4 artisti, spazio eventi"),
]

HEADER_FILL=PatternFill("solid",fgColor="2C3E50"); IDEAL_FILL=PatternFill("solid",fgColor="C8E6C9")
MEDIUM_FILL=PatternFill("solid",fgColor="FFF9C4"); NO_EMAIL_FILL=PatternFill("solid",fgColor="FFF9C4")
HEADER_FONT=Font(name="Calibri",bold=True,color="FFFFFF",size=11)
NORMAL_FONT=Font(name="Calibri",size=10); BOLD_FONT=Font(name="Calibri",bold=True,size=10)
THIN=Side(style="thin",color="CCCCCC"); BORDER=Border(left=THIN,right=THIN,top=THIN,bottom=THIN)
HEADERS=["#","Nome Studio","Quartiere","Indirizzo","EMAIL","Tel","Sito Web","Instagram","Stile","Dimensione","AdattoSocialPerks","Note"]
COL_WIDTHS=[4,28,14,34,30,16,22,22,18,12,15,28]

def apply_row(ws,row_idx,values,fill):
    for col,val in enumerate(values,1):
        cell=ws.cell(row=row_idx,column=col,value=val)
        cell.fill=fill; cell.font=NORMAL_FONT; cell.border=BORDER
        cell.alignment=Alignment(wrap_text=False,vertical="center")

def create_excel():
    wb=Workbook(); ws=wb.active; ws.title="Tattoo Studios Bordeaux"
    for col,(h,w) in enumerate(zip(HEADERS,COL_WIDTHS),1):
        cell=ws.cell(row=1,column=col,value=h)
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
    ws2=wb.create_sheet("Guida Outreach"); ws2.column_dimensions["A"].width=18; ws2.column_dimensions["B"].width=70
    for row_idx,(k,v) in enumerate([("SOCIALPERKS","Tattoo studios — studenti creano contenuti social"),("Link","https://socialperk.netlify.app/france/"),("TOTALE",f"{len(TATTOO_SHOPS)} studios | {n_email} con email | {n_ideal} ideali")],1):
        ws2.cell(row=row_idx,column=1,value=k).font=BOLD_FONT; ws2.cell(row=row_idx,column=2,value=v).font=NORMAL_FONT
    out=Path(__file__).parent/"SocialPerks_Tattoo_Bordeaux.xlsx"
    wb.save(out); print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
