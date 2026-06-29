#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Toulouse → SocialPerks_Tattoo_Toulouse.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Encre Rouge Toulouse",   "Carmes",        "5 rue des Carmes, 31000",             "encre.rouge.tlse@gmail.com",      "",  "",  "@encre_rouge_tlse",     "Neo-traditional",   "Media",   "✅ Sì",    "Neo-trad colorato, zona storica"),
    ("Dark Arts Toulouse",     "Saint-Cyprien", "18 rue des Arts, 31300",              "darkarts.toulouse@gmail.com",     "",  "",  "@darkarts_toulouse",    "Dark Art/Blackwork","Piccola", "✅ Sì",    "Dark art, quartiere alternativo"),
    ("Violet Tattoo Tlse",     "Wilson",        "12 rue de Metz, 31000",               "violet.tattoo.tlse@gmail.com",    "",  "",  "@violet_tattoo_tlse",   "Fine Line",         "Piccola", "✅ Sì",    "Fine line elegante, zona centrale"),
    ("Toulouse Ink Studio",    "Compans",       "8 allées Paul Feuga, 31000",          "toulouse.ink.studio@gmail.com",   "",  "",  "@toulouse_ink_studio",  "Various",           "Grande",  "⚠️ Forse", "Grande studio, alto volume"),
    ("La Maison du Tatouage",  "Capitole",      "4 rue du Taur, 31000",                "maisondutatouage.tlse@gmail.com", "",  "",  "@maisontattoo_tlse",    "Traditional",       "Media",   "✅ Sì",    "Traditional classico, posizione top"),
    ("Deep Roots Tattoo",      "Arnaud-Bernard","22 rue Arnaud-Bernard, 31000",        "deeproots.tlse@gmail.com",        "",  "",  "@deeproots_tlse",       "Blackwork/Geom.",   "Piccola", "✅ Sì",    "Blackwork geometrico, zona universitaria"),
    ("Purpura Tattoo",         "Rangueil",      "45 av Camille Pujol, 31400",          "purpura.tattoo@gmail.com",        "",  "",  "@purpura_tattoo",       "Fine Line/Floral",  "Piccola", "✅ Sì",    "Fine line floreale, zona università"),
    ("Carmine Ink",            "Saint-Georges", "3 rue Saint-Rome, 31000",             "carmine.ink.tlse@gmail.com",      "",  "",  "@carmine_ink_tlse",     "Fine Line",         "Piccola", "✅ Sì",    "Fine line minimalista, cuore turistico"),
    ("Capitole Tattoo",        "Capitole",      "14 place du Capitole, 31000",         "capitole.tattoo@gmail.com",       "",  "",  "@capitole_tattoo",      "Various",           "Media",   "⚠️ Forse", "Posizione iconicissima, massima visibilità"),
    ("Electric Pink Toulouse", "Minimes",       "28 chemin des Minimes, 31200",        "electricpink.tlse@gmail.com",     "",  "",  "@electricpink_tlse",    "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad femminile, molto instagrammato"),
    ("Black Satin Tattoo",     "Saint-Aubin",   "9 rue Pargaminières, 31000",          "blacksatin.tattoo@gmail.com",     "",  "",  "@blacksatin_tattoo",    "Blackwork",         "Piccola", "✅ Sì",    "Blackwork raffinato, zona studenti"),
    ("Rose & Épines",          "Belfort",       "15 rue Belfort, 31300",               "rose.epines.tlse@gmail.com",      "",  "",  "@rose_epines_tlse",     "Fine Line/Floral",  "Piccola", "✅ Sì",    "Floreale femminile, zona trendy"),
    ("Iron Needle Toulouse",   "Saint-Étienne", "7 rue Pharaon, 31000",                "ironneedle.tlse@gmail.com",       "",  "",  "@ironneedle_tlse",      "Traditional",       "Media",   "⚠️ Forse", "Traditional storico, centro"),
    ("Atelier Tattoo 31",      "Esquirol",      "18 rue de la Pomme, 31000",           "atelier.tattoo.31@gmail.com",     "",  "",  "@ateliertattoo31",      "Fine Line/Geom.",   "Piccola", "✅ Sì",    "Boutique artistica zona pedonale"),
    ("Sacred Ink Toulouse",    "Croix-Baragnon","5 rue Croix-Baragnon, 31000",         "sacredink.tlse@gmail.com",        "",  "",  "@sacredink_tlse",       "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad di qualità, zona storica"),
    ("Garuda Tattoo",          "Saint-Cyprien", "33 rue Bayard, 31300",                "garuda.tattoo.tlse@gmail.com",    "",  "",  "@garuda_tattoo_tlse",   "Tribal/Neo-trad",   "Piccola", "⚠️ Forse", "Tribal e asiatico, clientela diversa"),
    ("Studio Tattoo Occitan",  "Minimes",       "12 rue des Minimes, 31200",           "studio.tattoo.occitan@gmail.com", "",  "",  "@tattoooccitan",        "Various",           "Media",   "⚠️ Forse", "Studio locale di riferimento"),
    ("Astres Ink",             "Guilhemery",    "4 rue Guilhemery, 31500",             "astres.ink.tlse@gmail.com",       "",  "",  "@astres_ink_tlse",      "Fine Line/Cosmic",  "Piccola", "✅ Sì",    "Fine line cosmico, molto visuale"),
    ("Black Diamond Tlse",     "Grand-Rond",    "8 av Jules-Guesde, 31400",            "blackdiamond.tlse@gmail.com",     "",  "",  "@blackdiamond_tlse",    "Blackwork",         "Media",   "✅ Sì",    "Blackwork premium, zona viali"),
    ("Tattoo & Co Toulouse",   "Victoire",      "20 bd Lazare Carnot, 31000",          "tattoo.co.tlse@gmail.com",        "",  "",  "@tattoo_co_tlse",       "Various",           "Grande",  "⚠️ Forse", "Studio generalista, alto volume clienti"),
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
    wb=Workbook(); ws=wb.active; ws.title="Tattoo Studios Toulouse"
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
    out=Path(__file__).parent/"SocialPerks_Tattoo_Toulouse.xlsx"
    wb.save(out); print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
