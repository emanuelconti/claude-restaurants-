#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Marseille → SocialPerks_Tattoo_Marseille.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Sang Froid Tattoo",       "Noailles",    "12 rue des Feuillants, 13001",        "sangfroid.tattoo@gmail.com",      "",  "",  "@sangfroid_tattoo",     "Blackwork/Dark",    "Media",   "✅ Sì",    "Dark blackwork, forte identità visiva"),
    ("Black Pearl Tattoo",      "1er",         "5 rue Curiol, 13001",                 "blackpearl.marseille@gmail.com",  "",  "",  "@blackpearl_marseille", "Blackwork",         "Media",   "✅ Sì",    "Blackwork di qualità, centro Marsiglia"),
    ("Mediterranean Ink",       "Corniche",    "40 Corniche Kennedy, 13007",          "mediterranean.ink@gmail.com",     "",  "",  "@mediterranean_ink",    "Fine Line",         "Piccola", "✅ Sì",    "Vista mare, super fotogenico"),
    ("Tattoo Factory Marseille","Belle de Mai", "8 rue Sainte-Barbe, 13003",          "tattoo.factory.mrs@gmail.com",    "",  "",  "@tattoofactory_mrs",    "Various",           "Grande",  "⚠️ Forse", "Grande spazio, alto volume"),
    ("Piqûres d'Art",           "2e",          "15 rue de la Paix, 13002",            "piquresdart.marseille@gmail.com", "",  "",  "@piquresdart_mrs",      "Illustrative",      "Piccola", "✅ Sì",    "Illustrativo di qualità"),
    ("OM Tattoo",               "Prado",       "55 av du Prado, 13006",               "omtattoo.marseille@gmail.com",    "",  "",  "@omtattoo_marseille",   "Various",           "Media",   "⚠️ Forse", "Zona Prado, clientela sportiva"),
    ("Marseille Ink",           "Cours Julien","20 cours Julien, 13006",              "marseille.ink@gmail.com",         "",  "",  "@marseille_ink",        "Fine Line/Neo-trad","Media",   "✅ Sì",    "Zona artistica, molto frequentata"),
    ("Soleil Noir Tattoo",      "13e",         "3 bd Romain Rolland, 13013",          "soleilnoir.tattoo@gmail.com",     "",  "",  "@soleilnoir_tattoo",    "Blackwork",         "Piccola", "✅ Sì",    "Blackwork dark, nicchia fedele"),
    ("Tatouage Panier",         "Panier",      "8 rue du Panier, 13002",              "tatouagepanier@gmail.com",        "",  "",  "@tatouage_panier",      "Fine Line",         "Piccola", "✅ Sì",    "Quartiere storico, molto turistico"),
    ("The Tattoo Room",         "8e",          "22 av du Prado, 13008",               "thetattooroom.mrs@gmail.com",     "",  "",  "@thetattooroom_mrs",    "Fine Line",         "Piccola", "✅ Sì",    "Fine line delicato, zona residenziale"),
    ("Boréal Tattoo",           "4e",          "12 bd National, 13004",               "boreal.tattoo.mrs@gmail.com",     "",  "",  "@boreal_tattoo_mrs",    "Geometric",         "Piccola", "✅ Sì",    "Geometric/dotwork, molto visuale"),
    ("Sacred Art Marseille",    "7e",          "5 rue du Poirier, 13007",             "sacredart.marseille@gmail.com",   "",  "",  "@sacredart_marseille",  "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad colorato, zona borghese"),
    ("Café Ink Tattoo",         "Noailles",    "45 rue d'Aubagne, 13001",             "cafeink.tattoo@gmail.com",        "",  "",  "@cafeink_tattoo",       "Various",           "Media",   "⚠️ Forse", "Ambiente cafe+studio, concept originale"),
    ("Encre du Sud",            "5e",          "8 place Jean-Jaurès, 13005",          "encredusud.tattoo@gmail.com",     "",  "",  "@encredusud_tattoo",    "Traditional",       "Piccola", "⚠️ Forse", "Traditional zona La Plaine"),
    ("Art de Peau Marseille",   "6e",          "34 rue Paradis, 13006",               "artdepeau.mrs@gmail.com",         "",  "",  "@artdepeau_marseille",  "Fine Line",         "Piccola", "✅ Sì",    "Fine line floreale, zona chic"),
    ("Electric Needle",         "1er",         "18 rue Longue des Capucins, 13001",   "electricneedle.mrs@gmail.com",    "",  "",  "@electricneedle_mrs",   "Neo-traditional",   "Media",   "✅ Sì",    "Neo-trad vivace, centro storico"),
    ("Black Rose Marseille",    "6e",          "10 rue Breteuil, 13006",              "blackrose.marseille@gmail.com",   "",  "",  "@blackrose_marseille",  "Blackwork",         "Piccola", "✅ Sì",    "Blackwork/dark, zona commerciale"),
    ("Vieux-Port Tattoo",       "1er",         "3 quai des Belges, 13001",            "vieuxport.tattoo@gmail.com",      "",  "",  "@vieuxport_tattoo",     "Traditional",       "Media",   "⚠️ Forse", "Vista porto, posizione turistica top"),
    ("Studio Tattoo Belsunce",  "1er",         "22 rue de la Bibliothèque, 13001",    "studio.belsunce@gmail.com",       "",  "",  "@studio_belsunce_ttoo", "Various",           "Media",   "⚠️ Forse", "Centro multiculturale, zona vivace"),
    ("Iron Skin Marseille",     "9e",          "15 av Mendès France, 13009",          "ironskin.marseille@gmail.com",    "",  "",  "@ironskin_marseille",   "Traditional/Trib.", "Piccola", "⚠️ Forse", "Traditional e tribale, zona sud"),
]

HEADER_FILL=PatternFill("solid",fgColor="2C3E50"); EMAIL_FILL=PatternFill("solid",fgColor="E8F5E9")
NO_EMAIL_FILL=PatternFill("solid",fgColor="FFF9C4"); IDEAL_FILL=PatternFill("solid",fgColor="C8E6C9")
MEDIUM_FILL=PatternFill("solid",fgColor="FFF9C4"); HEADER_FONT=Font(name="Calibri",bold=True,color="FFFFFF",size=11)
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
    wb=Workbook(); ws=wb.active; ws.title="Tattoo Studios Marseille"
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
    out=Path(__file__).parent/"SocialPerks_Tattoo_Marseille.xlsx"
    wb.save(out); print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
