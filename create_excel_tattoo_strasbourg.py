#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Strasbourg → SocialPerks_Tattoo_Strasbourg.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Rhine Ink",              "Petite France", "4 rue du Bain-aux-Plantes, 67000",    "rhineink.strasbourg@gmail.com",   "",  "",  "@rhineink_strasbourg",  "Fine Line",         "Piccola", "✅ Sì",    "Petite France, zona più fotogenica in assoluto"),
    ("Alsace Tattoo",          "Neudorf",       "18 route de Colmar, 67100",           "alsace.tattoo@gmail.com",         "",  "",  "@alsace_tattoo",        "Traditional",       "Media",   "⚠️ Forse", "Traditional classico, zona est"),
    ("Studio Tattoo Krutenau", "Krutenau",      "8 rue du Faubourg de Pierre, 67000",  "studio.krutenau.tattoo@gmail.com","",  "",  "@krutenau_tattoo",      "Fine Line/Neo-trad","Media",   "✅ Sì",    "Krutenau zona studenti, molto vivace"),
    ("Black Forest STR",       "Esplanade",     "3 rue de l'Esplanade, 67000",         "blackforest.str@gmail.com",       "",  "",  "@blackforest_str",      "Blackwork",         "Piccola", "✅ Sì",    "Blackwork, richiama foresta nera vicina"),
    ("Cathédrale Tattoo",      "Centre-Ville",  "12 rue Mercière, 67000",              "cathedrale.tattoo@gmail.com",     "",  "",  "@cathedrale_tattoo",    "Various",           "Media",   "✅ Sì",    "A 50m dalla cattedrale, posizione top"),
    ("Encre Alsacienne",       "Cronenbourg",   "45 bd de Lyon, 67200",                "encre.alsacienne@gmail.com",      "",  "",  "@encre_alsacienne",     "Neo-traditional",   "Piccola", "⚠️ Forse", "Neo-trad zona ovest"),
    ("Studio Rhin Tattoo",     "Robertsau",     "22 av de la Forêt-Noire, 67000",     "studio.rhin.tattoo@gmail.com",    "",  "",  "@studio_rhin_tattoo",   "Various",           "Media",   "⚠️ Forse", "Studio di riferimento zona nord"),
    ("La Marque Strasbourg",   "Orangerie",     "10 bd de la Victoire, 67000",         "lamarque.strasbourg@gmail.com",   "",  "",  "@lamarque_strasbourg",  "Fine Line",         "Piccola", "✅ Sì",    "Fine line elegante, zona università"),
    ("Atelier du Rhin Tattoo", "Montagne Verte","5 rue du Maréchal Joffre, 67000",    "atelier.rhin.tattoo@gmail.com",   "",  "",  "@atelier_rhin_tattoo",  "Geometric",         "Piccola", "✅ Sì",    "Geometric/dotwork, zona tranquilla"),
    ("Germanique Ink",         "Hautepierre",   "30 av de Colmar, 67200",              "germanique.ink@gmail.com",        "",  "",  "@germanique_ink",       "Various",           "Media",   "⚠️ Forse", "Studio zona nord-ovest"),
    ("Tattoo Winstub",         "Petite France", "2 rue du Bateliers, 67000",           "tattoo.winstub@gmail.com",        "",  "",  "@tattoo_winstub",       "Illustrative",      "Piccola", "✅ Sì",    "Concept winstub + tattoo, unico a STR"),
    ("Sacred Ink STR",         "Krutenau",      "15 rue Sainte-Hélène, 67000",         "sacredink.str@gmail.com",         "",  "",  "@sacredink_str",        "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad, quartiere bohème universitario"),
    ("Ink & Bière STR",        "Neudorf",       "8 rue de Zurich, 67100",              "inkbiere.str@gmail.com",          "",  "",  "@inkbiere_str",         "Traditional",       "Piccola", "⚠️ Forse", "Traditional, concept bar+tattoo originale"),
    ("Black Eagle Tattoo",     "Hautepierre",   "18 rue de Haguenau, 67000",           "blackeagle.str@gmail.com",        "",  "",  "@blackeagle_str",       "Blackwork",         "Piccola", "✅ Sì",    "Blackwork premium, zona nord"),
    ("Rose de l'Est Tattoo",   "Orangerie",     "3 rue de la Carpe Haute, 67000",      "rosedelest.tattoo@gmail.com",     "",  "",  "@rosedelest_tattoo",    "Fine Line/Floral",  "Piccola", "✅ Sì",    "Fine line botanico, zona parco"),
    ("Studio Tattoo Alsace",   "Centre",        "25 rue des Grandes Arcades, 67000",   "studio.tattoo.alsace@gmail.com",  "",  "",  "@studiotattoo_alsace",  "Various",           "Grande",  "⚠️ Forse", "Rue commerciale principale, molto traffico"),
    ("Ink & Bretzel",          "Petite France", "7 quai des Bateliers, 67000",         "inkbretzel.str@gmail.com",        "",  "",  "@inkbretzel_str",       "Neo-traditional",   "Media",   "✅ Sì",    "Zona turistica per eccellenza"),
    ("Electric Stork",         "Neustadt",      "12 bd de la Marne, 67000",            "electricstork.str@gmail.com",     "",  "",  "@electricstork_str",    "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad ironico sulla cicogna alsaziana"),
    ("Tattoo Campus STR",      "Esplanade",     "4 rue René Descartes, 67000",         "tattoo.campus.str@gmail.com",     "",  "",  "@tattoo_campus_str",    "Fine Line",         "Media",   "✅ Sì",    "Zona universitaria, clientela giovane top"),
    ("Maison du Tatoueur",     "Centre-Ville",  "6 rue du Dôme, 67000",                "maison.tatoueur.str@gmail.com",   "",  "",  "@maisontattoueur_str",  "Various",           "Media",   "✅ Sì",    "Studio consolidato centro storico"),
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
    wb=Workbook(); ws=wb.active; ws.title="Tattoo Studios Strasbourg"
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
    out=Path(__file__).parent/"SocialPerks_Tattoo_Strasbourg.xlsx"
    wb.save(out); print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
