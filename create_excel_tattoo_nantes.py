#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Nantes → SocialPerks_Tattoo_Nantes.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Black Forest Tattoo",    "Bouffay",       "8 rue des Carmes, 44000 Nantes",      "blackforest.nantes@gmail.com",    "",  "",  "@blackforest_nantes",   "Dark Art/Blackwork","Media",   "✅ Sì",    "Dark art, quartiere più vivace di Nantes"),
    ("Atlantic Ink",           "Île de Nantes", "4 quai François Mitterrand, 44200",   "atlantic.ink.nantes@gmail.com",   "",  "",  "@atlantic_ink_nantes",  "Fine Line",         "Piccola", "✅ Sì",    "Île de Nantes, zona creativa top"),
    ("Loire Tattoo",           "Barbin",        "15 rue Barbin, 44000",                "loire.tattoo@gmail.com",          "",  "",  "@loire_tattoo",         "Neo-traditional",   "Media",   "✅ Sì",    "Neo-trad, zona universitaria"),
    ("La Fabrique à Tatouages","Centre-Ville",  "22 rue du Calvaire, 44000",           "lafabrique.tattoo@gmail.com",     "",  "",  "@lafabrique_tattoo",    "Various",           "Grande",  "⚠️ Forse", "Grande studio, alto volume clienti"),
    ("Ink Machine Nantes",     "Chantenay",     "18 bd de Chantenay, 44100",           "inkmachine.nantes@gmail.com",     "",  "",  "@inkmachine_nantes",    "Various",           "Media",   "⚠️ Forse", "Studio consolidato zona ovest"),
    ("Wild Ink Nantes",        "Saint-Félix",   "5 rue Saint-Félix, 44002",            "wildink.nantes@gmail.com",        "",  "",  "@wildink_nantes",       "Traditional",       "Piccola", "✅ Sì",    "Traditional old school, quartiere trendy"),
    ("Nantes Tattoo Studio",   "Graslin",       "12 rue Crébillon, 44000",             "nantes.tattoo.studio@gmail.com",  "",  "",  "@nantes_tattoo_studio", "Fine Line",         "Piccola", "✅ Sì",    "Fine line, zona teatro e boutique"),
    ("Dark Matter Tattoo NTS", "Doulon",        "35 bd des Anglais, 44300",            "darkmatter.nantes@gmail.com",     "",  "",  "@darkmatter_nantes",    "Blackwork",         "Piccola", "✅ Sì",    "Blackwork di nicchia, est Nantes"),
    ("Rose & Épines NTS",      "Zola",          "8 rue Zola, 44000",                   "rose.epines.nantes@gmail.com",    "",  "",  "@rose_epines_nantes",   "Fine Line/Floral",  "Piccola", "✅ Sì",    "Floreale femminile, zona residenziale"),
    ("Electric Cathedral",     "Bouffay",       "3 place du Bouffay, 44000",           "electriccathedral.nts@gmail.com", "",  "",  "@electriccathedral_nts","Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad colorato, cuore storico"),
    ("Sacred Art Nantes",      "Erdre",         "20 bd Robert Schuman, 44000",         "sacredart.nantes@gmail.com",      "",  "",  "@sacredart_nantes",     "Neo-traditional",   "Piccola", "⚠️ Forse", "Neo-trad, zona nord Nantes"),
    ("Studio Tattoo 44",       "Talensac",      "4 rue de Bel-Air, 44000",             "studio.tattoo.44@gmail.com",      "",  "",  "@studiotattoo44",       "Various",           "Media",   "⚠️ Forse", "Studio di riferimento zona Talensac"),
    ("Encre de Loire",         "Madeleine",     "12 rue de la Madeleine, 44000",       "encre.de.loire@gmail.com",        "",  "",  "@encre_de_loire",       "Illustrative",      "Piccola", "✅ Sì",    "Illustrativo poetico, zona chic"),
    ("Black Pearl NTS",        "Île de Nantes", "10 bd Victor Hugo, 44200",            "blackpearl.nantes@gmail.com",     "",  "",  "@blackpearl_nantes",    "Blackwork",         "Media",   "✅ Sì",    "Blackwork moderno, ex-zones industriali"),
    ("Tattoo & Soul NTS",      "Saint-Similien","7 rue de Brest, 44000",               "tattoo.soul.nantes@gmail.com",    "",  "",  "@tattoo_soul_nantes",   "Fine Line",         "Piccola", "✅ Sì",    "Fine line spirituale, zona alternativa"),
    ("Iron Anchor Tattoo",     "Chantenay",     "25 rue du Bois Briand, 44100",        "ironanchor.nantes@gmail.com",     "",  "",  "@ironanchor_nantes",    "Sailor/Traditional","Piccola", "⚠️ Forse", "Sailor tattoo, tema marinaro originale"),
    ("Géométrik Studio",       "Zola",          "18 rue Fouré, 44000",                 "geometrik.studio.nts@gmail.com",  "",  "",  "@geometrik_studio_nts", "Geometric/Dotwork", "Piccola", "✅ Sì",    "Geometric dotwork molto visuale"),
    ("Moon & Stars Tattoo",    "Bouffay",       "6 rue de la Barillerie, 44000",       "moonandstars.tattoo@gmail.com",   "",  "",  "@moonandstars_tattoo",  "Fine Line/Astro.",  "Piccola", "✅ Sì",    "Fine line astrologico, molto di tendenza"),
    ("Nantes Ink Collective",  "Hauts-Pavés",   "30 rue de Chanzy, 44000",             "nantes.ink.collective@gmail.com", "",  "",  "@nantesink_collective", "Various",           "Grande",  "⚠️ Forse", "Collettivo 3 artisti, zona bobo"),
    ("Studio Abalone",         "Centre",        "15 rue des Olivettes, 44000",         "studio.abalone@gmail.com",        "",  "",  "@studio_abalone",       "Watercolor",        "Piccola", "✅ Sì",    "Watercolor marino, stile unico"),
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
    wb=Workbook(); ws=wb.active; ws.title="Tattoo Studios Nantes"
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
    out=Path(__file__).parent/"SocialPerks_Tattoo_Nantes.xlsx"
    wb.save(out); print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
