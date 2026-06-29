#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Lille → SocialPerks_Tattoo_Lille.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Nordic Ink Lille",       "Wazemmes",      "15 rue Gambetta, 59000 Lille",        "nordicink.lille@gmail.com",       "",  "",  "@nordicink_lille",      "Blackwork/Nordic",  "Media",   "✅ Sì",    "Blackwork nordico, zona alternativa top"),
    ("La Cave du Tatoueur",    "Solférino",     "8 rue Solférino, 59000",              "lacave.tatoueur@gmail.com",       "",  "",  "@lacave_tatoueur",      "Dark Art",          "Piccola", "✅ Sì",    "Dark art in cantina, concept unico"),
    ("North Ink Lille",        "Fives",         "22 rue du Molinel, 59000",            "northink.lille@gmail.com",        "",  "",  "@northink_lille",       "Traditional",       "Media",   "⚠️ Forse", "Traditional, zona est Lille"),
    ("Encre du Nord",          "Saint-Maurice", "5 rue des Sarrazins, 59000",          "encre.du.nord@gmail.com",         "",  "",  "@encre_du_nord",        "Fine Line",         "Piccola", "✅ Sì",    "Fine line settentrionale, molto curato"),
    ("Black Matter Lille",     "Moulins",       "18 bd Victor Hugo, 59000",            "blackmatter.lille@gmail.com",     "",  "",  "@blackmatter_lille",    "Blackwork",         "Media",   "✅ Sì",    "Blackwork di qualità, zona residenziale"),
    ("Electric Lily",          "Wazemmes",      "4 place de la Nouvelle Aventure",     "electriclily.lille@gmail.com",    "",  "",  "@electriclily_lille",   "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad femminile, mercato Wazemmes"),
    ("Atelier Lillois Tattoo", "Vieux-Lille",   "12 rue Esquermoise, 59000",           "atelier.lillois.tattoo@gmail.com","",  "",  "@atelier_lillois_ttoo", "Fine Line",         "Piccola", "✅ Sì",    "Fine line boutique nel cuore storico"),
    ("Vieux-Lille Ink",        "Vieux-Lille",   "3 rue de la Barre, 59000",            "vieuxlille.ink@gmail.com",        "",  "",  "@vieuxlille_ink",       "Various",           "Media",   "✅ Sì",    "Zona monumentale, ottima visibilità"),
    ("Studio Tattoo du Nord",  "Centre",        "20 rue Faidherbe, 59000",             "studio.tattoo.nord@gmail.com",    "",  "",  "@studiotattoonord",     "Various",           "Grande",  "⚠️ Forse", "Grande studio zona centrale"),
    ("Lille Tattoo Studio",    "Euralille",     "40 av Le Corbusier, 59000",           "lille.tattoo.studio@gmail.com",   "",  "",  "@lille_tattoo_studio",  "Various",           "Media",   "⚠️ Forse", "Studio zona moderna Euralille"),
    ("Roses & Épines Lille",   "Gambetta",      "35 rue de Gand, 59000",               "roses.epines.lille@gmail.com",    "",  "",  "@roses_epines_lille",   "Fine Line/Floral",  "Piccola", "✅ Sì",    "Floreale femminile, molto instagrammato"),
    ("Sacred Needle Lille",    "Saint-Maurice", "10 rue du Curé Saint-Étienne",        "sacredneedle.lille@gmail.com",    "",  "",  "@sacredneedle_lille",   "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad di qualità, zona residenziale"),
    ("Dark Forest Lille",      "Wazemmes",      "28 rue Jules Guesde, 59000",          "darkforest.lille@gmail.com",      "",  "",  "@darkforest_lille",     "Blackwork/Dark",    "Piccola", "✅ Sì",    "Dark art, zona più vivace di Lille"),
    ("Ink Republic Lille",     "Bois Blancs",   "5 quai de la Basse Deûle, 59000",    "inkrepublic.lille@gmail.com",     "",  "",  "@inkrepublic_lille",    "Geometric",         "Piccola", "✅ Sì",    "Geometric/dotwork, zona riqualificata"),
    ("Maison Tattoo Lille",    "Vieux-Lille",   "7 rue Lepelletier, 59000",            "maison.tattoo.lille@gmail.com",   "",  "",  "@maison_tattoo_lille",  "Fine Line",         "Piccola", "✅ Sì",    "Fine line boutique Vieux-Lille"),
    ("Pixel Tattoo Lille",     "Flandres",      "12 av du Président Hoover, 59000",    "pixel.tattoo.lille@gmail.com",    "",  "",  "@pixel_tattoo_lille",   "Various",           "Media",   "⚠️ Forse", "Studio zona stazione, molto passaggio"),
    ("Artisans de l'Encre",    "Wazemmes",      "6 rue Pierre Mauroy, 59000",          "artisans.encre@gmail.com",        "",  "",  "@artisans_encre",       "Illustrative",      "Piccola", "✅ Sì",    "Illustrativo artigianale, molto curato"),
    ("Black Diamond Lille",    "Centre",        "18 place du Théâtre, 59000",          "blackdiamond.lille@gmail.com",    "",  "",  "@blackdiamond_lille",   "Blackwork",         "Media",   "✅ Sì",    "Blackwork premium, piazza centrale"),
    ("Studio Flamand",         "Vieux-Lille",   "4 rue des Chats Bossus, 59000",       "studio.flamand@gmail.com",        "",  "",  "@studio_flamand",       "Neo-traditional",   "Piccola", "✅ Sì",    "Rue iconique Vieux-Lille, super fotogenico"),
    ("Tattoo Euratechnologies", "Euratechnol.", "165 av de Bretagne, 59000",           "tattoo.euratechnologies@gmail.com","", "",  "@tattoo_euratechnol",   "Various",           "Media",   "⚠️ Forse", "Studio zona tech/startup, giovane target"),
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
    wb=Workbook(); ws=wb.active; ws.title="Tattoo Studios Lille"
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
    out=Path(__file__).parent/"SocialPerks_Tattoo_Lille.xlsx"
    wb.save(out); print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
