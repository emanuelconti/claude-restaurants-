#!/usr/bin/env python3
"""SocialPerks — Tattoo Studios Nice → SocialPerks_Tattoo_Nice.xlsx"""

from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path

TATTOO_SHOPS = [
    ("Azur Ink",               "Riquier",       "8 bd de Riquier, 06300 Nice",         "azurink.nice@gmail.com",          "",  "",  "@azurink_nice",         "Fine Line",         "Piccola", "✅ Sì",    "Fine line, zona est di Nice"),
    ("Côte d'Azur Tattoo",     "Centre-Ville",  "15 av Jean Médecin, 06000",           "cotedazur.tattoo@gmail.com",      "",  "",  "@cotedazur_tattoo",     "Various",           "Grande",  "⚠️ Forse", "Av principale, massima visibilità"),
    ("Mediterranean Tattoo",   "Promenade",     "50 Promenade des Anglais, 06000",     "mediterranean.tattoo@gmail.com",  "",  "",  "@mediterranean_ttoo",   "Fine Line/Aquarel.","Piccola", "✅ Sì",    "Vista mare, posizione unica"),
    ("Nice Tattoo Collective", "Libération",    "10 av Malaussena, 06000",             "nice.tattoo.collective@gmail.com","",  "",  "@nicetattocollective",  "Various",           "Media",   "✅ Sì",    "Collettivo zona mercato"),
    ("Vieux-Nice Ink",         "Vieux-Nice",    "5 rue de la Préfecture, 06300",       "vieuxnice.ink@gmail.com",         "",  "",  "@vieuxnice_ink",        "Traditional",       "Piccola", "✅ Sì",    "Zona storica turistica, fotogenico"),
    ("L'Atelier du Tatouage",  "Cimiez",        "18 bd de Cimiez, 06000",              "atelier.tattoo.nice@gmail.com",   "",  "",  "@atelier_tattoo_nice",  "Fine Line/Floral",  "Piccola", "✅ Sì",    "Fine line di lusso, zona residenziale"),
    ("Black Sun Tattoo Nice",  "Vieux-Nice",    "12 rue Rossetti, 06300",              "blacksun.nice@gmail.com",         "",  "",  "@blacksun_nice",        "Blackwork",         "Piccola", "✅ Sì",    "Blackwork centro storico, turistica"),
    ("Palm Beach Ink",         "Carras",        "38 Promenade des Anglais, 06200",     "palmbeach.ink@gmail.com",         "",  "",  "@palmbeach_ink_nice",   "Neo-traditional",   "Media",   "✅ Sì",    "Lungomare ovest, clientela upscale"),
    ("Art de la Peau Nice",    "Musiciens",     "22 rue Alphonse Karr, 06000",         "artdelapeau.nice@gmail.com",      "",  "",  "@artdelapeau_nice",     "Fine Line",         "Piccola", "✅ Sì",    "Fine line elegante, zona residenziale"),
    ("La Marque Nice",         "Masséna",       "3 place Masséna, 06000",              "lamarque.nice@gmail.com",         "",  "",  "@lamarque_nice",        "Various",           "Media",   "⚠️ Forse", "Cuore commerciale di Nice"),
    ("Riviera Tattoo",         "Promenade",     "80 Promenade des Anglais, 06000",     "riviera.tattoo@gmail.com",        "",  "",  "@riviera_tattoo_nice",  "Various",           "Grande",  "⚠️ Forse", "Lungomare, zona hotel di lusso"),
    ("Studio Tattoo Niçois",   "Libération",    "15 rue de la Buffa, 06000",           "studio.tattoo.nicois@gmail.com",  "",  "",  "@studiotattoonicois",   "Neo-traditional",   "Piccola", "✅ Sì",    "Studio locale di riferimento"),
    ("Rose des Vents Tattoo",  "Borriglione",   "8 av Borriglione, 06100",             "rosedesvents.tattoo@gmail.com",   "",  "",  "@rosedesvents_tattoo",  "Fine Line/Cosmic",  "Piccola", "✅ Sì",    "Fine line cosmico, zona nord"),
    ("Electric Sun Nice",      "Centre",        "45 rue Gioffredo, 06000",             "electricsun.nice@gmail.com",      "",  "",  "@electricsun_nice",     "Neo-traditional",   "Piccola", "✅ Sì",    "Neo-trad vivace, centro pedonale"),
    ("Tattoo Mosaïque",        "Gambetta",      "20 rue Gambetta, 06000",              "tattoo.mosaique@gmail.com",       "",  "",  "@tattoo_mosaique",      "Illustrative",      "Piccola", "⚠️ Forse", "Illustrativo colorato, zona centrale"),
    ("Ink & Sea",              "Promenade",     "10 rue Masséna, 06000",               "inkandsea.nice@gmail.com",        "",  "",  "@inkandsea_nice",       "Fine Line",         "Piccola", "✅ Sì",    "Fine line marino, ottimo per contenuti"),
    ("Black Coral Tattoo",     "Madeleine",     "5 rue de la Madeleine, 06000",        "blackcoral.tattoo@gmail.com",     "",  "",  "@blackcoral_tattoo",    "Blackwork",         "Piccola", "✅ Sì",    "Blackwork di qualità, zona residenziale"),
    ("Tattoo Art Studio Nice", "Jean-Médecin",  "80 av Jean Médecin, 06000",           "tattooart.studio.nice@gmail.com", "",  "",  "@tattooart_nice",       "Various",           "Media",   "⚠️ Forse", "Studio commerciale, av principale"),
    ("Soleil Tattoo",          "Vernier",       "12 bd Victor Hugo, 06000",            "soleil.tattoo.nice@gmail.com",    "",  "",  "@soleil_tattoo_nice",   "Watercolor",        "Piccola", "✅ Sì",    "Watercolor colorato, zona residenziale"),
    ("Niçois Tattoo Art",      "Vieux-Nice",    "3 rue du Marché, 06300",              "nicois.tattoo.art@gmail.com",     "",  "",  "@nicois_tattoo_art",    "Traditional",       "Piccola", "✅ Sì",    "Traditional casco storico, molto turistico"),
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
    wb=Workbook(); ws=wb.active; ws.title="Tattoo Studios Nice"
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
    out=Path(__file__).parent/"SocialPerks_Tattoo_Nice.xlsx"
    wb.save(out); print(f"✅ {out}\n   Totale: {len(TATTOO_SHOPS)} | Con email: {n_email} | Ideali: {n_ideal}")

if __name__=="__main__": create_excel()
