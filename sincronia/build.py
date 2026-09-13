#!/usr/bin/env python3
"""Build the Sincronia site.

Generates one indexable page per funding programme (plus native-language
versions for the country schemes people actually search for in their own
language), a directory hub, sitemap.xml and robots.txt.

The landing page is a single page and cannot rank for anything. These
programme pages are the organic-search surface: people search
"Smart&Start Italia requisiti", "NEOTEC convocatoria", "ZIM Antragstopp",
not "Sincronia".

Run:  python3 build.py
"""
import json, os, re, shutil
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "programs.json"
OUT = ROOT / "landing"
PROGRAMS_DIR = OUT / "programs"
SITE = "https://sincronia.live"
TODAY = date.today()

programs = json.loads(DATA.read_text(encoding="utf-8"))

# --------------------------------------------------------------- native copy
# Country schemes get a page in the language they are searched in.
NATIVE = {
"smart-start-italia": {"lang":"it",
 "title":"Smart&Start Italia: requisiti, importi e come funziona",
 "who":"Startup innovative già costituite o in via di costituzione, con progetti tra 100.000 € e 1,5 milioni di euro.",
 "amount":"Finanziamento a tasso zero fino all'80% delle spese ammissibili, con quota maggiorata e una parte a fondo perduto per le startup del Mezzogiorno.",
 "status":"Sportello aperto senza scadenza fissa: le domande sono valutate in ordine di arrivo fino a esaurimento fondi.",
 "catch":"Serve l'iscrizione alla sezione speciale del registro delle startup innovative, che ha requisiti propri."},
"nuova-sabatini": {"lang":"it",
 "title":"Nuova Sabatini 2026: importi, requisiti e come accedere",
 "who":"Micro, piccole e medie imprese italiane iscritte al Registro Imprese.",
 "amount":"Contributo ministeriale sugli interessi di un finanziamento bancario o leasing per l'acquisto di beni strumentali nuovi. Il finanziamento deve essere compreso tra 20.000 € e 4 milioni di euro.",
 "status":"Sportello aperto fino a esaurimento fondi. La Legge di Bilancio 2026 ha stanziato 650 milioni di euro per il biennio 2026-2027.",
 "catch":"Agevola gli interessi, non il bene. Serve comunque una banca o una società di leasing che approvi il finanziamento."},
"on-nuove-imprese-tasso-zero": {"lang":"it",
 "title":"ON — Nuove Imprese a Tasso Zero: cosa è cambiato dal 2026",
 "who":"Micro e piccole imprese di nuova o recente costituzione, con attenzione a giovani e donne.",
 "amount":"Dal 1° luglio 2026 l'agevolazione è concessa solo come finanziamento a tasso zero, rimborsabile in 10 anni.",
 "status":"Sportello aperto. La quota a fondo perduto non è più prevista dal 1° luglio 2026.",
 "catch":"Molte guide online descrivono ancora la quota a fondo perduto: sono aggiornate a prima di luglio 2026."},
"neotec": {"lang":"es",
 "title":"NEOTEC 2026: requisitos, cuantía y estado de la convocatoria",
 "who":"Pequeñas empresas innovadoras de base tecnológica con un máximo de tres años de antigüedad, capital social mínimo de 20.000 € y sin haber repartido beneficios.",
 "amount":"Cubre hasta el 70% del presupuesto elegible, hasta el 85% si el equipo incorpora al menos un doctor. Límites de 250.000 € y 325.000 € respectivamente. Dotación de la convocatoria 2026: 20,38 millones de euros, con un mínimo de 5 millones reservado a empresas lideradas por mujeres.",
 "status":"La convocatoria 2026 se cerró el 14 de mayo de 2026. No hay una nueva convocatoria publicada: no planifiques sobre ella hasta que salga.",
 "catch":"El límite de tres años desde la constitución es estricto. Si no se cumple, lo demás da igual."},
"kit-digital": {"lang":"es",
 "title":"Kit Digital: importes, segmentos y qué se puede financiar",
 "who":"Pymes y autónomos españoles ya constituidos que quieren digitalizarse.",
 "amount":"Bono digital de hasta 29.000 € según el tamaño de la empresa, para soluciones de un catálogo definido: web, comercio electrónico, ciberseguridad, factura electrónica y otras.",
 "status":"Los segmentos y sus plazos han cambiado varias veces. Confirma qué segmento está abierto para tu tamaño de empresa antes de empezar.",
 "catch":"No se puede gastar libremente: solo con agentes digitalizadores acreditados y sobre un catálogo cerrado."},
"enisa-startups-pymes": {"lang":"es",
 "title":"Préstamos ENISA: importes, condiciones y sin aval personal",
 "who":"Pymes y startups innovadoras de cualquier sector con un proyecto realmente diferencial.",
 "amount":"Préstamo participativo de 25.000 € a 1,5 millones de euros, evaluado sobre el proyecto y no sobre el patrimonio personal de los socios, por lo que no exige garantías personales.",
 "status":"Convocatoria abierta durante todo el año.",
 "catch":"Es un préstamo, no una subvención: hay que devolverlo, y parte del interés va ligado a tus resultados."},
"zim": {"lang":"de",
 "title":"ZIM 2026: Antragstopp seit 7. Juli — aktueller Stand",
 "who":"KMU mit bis zu 1.000 Beschäftigten, alle Branchen, für FuE-Projekte allein oder in Kooperation.",
 "amount":"Nicht rückzahlbare Zuschüsse zu FuE-Projektkosten. Bei Einzelprojekten liegt die maximale Bemessungsgrundlage bei 690.000 €. Kooperationsprojekte laufen mit höheren Sätzen und Volumina.",
 "status":"Seit 7. Juli 2026, 12:00 Uhr werden vorübergehend keine Anträge angenommen. Der Antragstopp gilt für alle Projektformen und auch für Projektskizzen.",
 "catch":"Aktuell ausgesetzt. Die meisten Förderübersichten für 2026 führen ZIM weiterhin als offen — sie sind nicht aktualisiert."},
"exist-gruendungsstipendium": {"lang":"de",
 "title":"EXIST-Gründungsstipendium: Voraussetzungen und Ablauf",
 "who":"Studierende, Absolventinnen und Absolventen sowie Forschende, die eine technologie- oder wissensbasierte Gründung aus der Hochschule vorbereiten.",
 "amount":"Monatliches Stipendium für den Lebensunterhalt in der Vorgründungsphase, dazu Mittel für Sachausgaben und Coaching.",
 "status":"Laufend. Die Antragstellung erfolgt über das Gründungsnetzwerk einer Partnerhochschule, nicht direkt.",
 "catch":"Ohne eine Hochschule, die den Antrag trägt, ist eine Bewerbung nicht möglich."},
"bourse-french-tech": {"lang":"fr",
 "title":"Bourse French Tech : conditions et dépenses couvertes",
 "who":"Entreprises de moins de 5 ans et de moins de 50 salariés, au tout début d'un projet d'innovation.",
 "amount":"Subvention couvrant les premières dépenses de validation d'un projet innovant : faisabilité, prototypage, premiers tests de marché.",
 "status":"Instruction en continu par les directions régionales de Bpifrance.",
 "catch":"Calibrée pour les premiers pas, pas pour l'industrialisation. Les montants restent modestes face aux dispositifs ultérieurs."},
"startup-voucher-pt": {"lang":"pt",
 "title":"StartUP Voucher: bolsa, condições e estado das candidaturas",
 "who":"Jovens licenciados até aos 29 anos que criam o próprio emprego em áreas de base tecnológica.",
 "amount":"Bolsa mensal de 900 €, mentoria especializada, incubação em entidades acreditadas, formação e networking, mais prémios intercalares e de conclusão.",
 "status":"A 4.ª edição fechou candidaturas a 30 de janeiro de 2026. Não há uma nova edição anunciada.",
 "catch":"O limite de idade de 29 anos é rígido, e a janela está fechada. Confirme se existe uma 5.ª edição antes de contar com ela."},
}

STATUS_META = {
 "open":    ("Open", "#1a7f4b", "Accepting applications"),
 "rolling": ("Rolling", "#1a7f4b", "Open window, no fixed deadline"),
 "closing": ("Closing", "#b3541e", "Deadline approaching"),
 "paused":  ("Paused", "#8a5c2b", "Temporarily suspended"),
 "closed":  ("Closed", "#8c8c8c", "Window has passed"),
 "check":   ("Check", "#8a5c2b", "Varies by call"),
}
UI = {
 "en": dict(back="All programmes", who="Who it is for", amount="What you get",
            status="Status today", catch="The catch", source="Official source",
            verified="Verified", cta="See if you qualify", authority="Managed by",
            type="Type", other="Other programmes", deadline="Deadline"),
 "it": dict(back="Tutti i bandi", who="A chi si rivolge", amount="Cosa ottieni",
            status="Stato oggi", catch="L'insidia", source="Fonte ufficiale",
            verified="Verificato", cta="Vedi se sei idoneo", authority="Gestito da",
            type="Tipo", other="Altri bandi", deadline="Scadenza"),
 "es": dict(back="Todos los programas", who="A quién se dirige", amount="Qué obtienes",
            status="Estado hoy", catch="La letra pequeña", source="Fuente oficial",
            verified="Verificado", cta="Comprueba si encajas", authority="Gestionado por",
            type="Tipo", other="Otros programas", deadline="Plazo"),
 "de": dict(back="Alle Programme", who="Für wen", amount="Was Sie bekommen",
            status="Stand heute", catch="Der Haken", source="Offizielle Quelle",
            verified="Geprüft", cta="Passt es zu Ihnen?", authority="Verwaltet von",
            type="Art", other="Weitere Programme", deadline="Frist"),
 "fr": dict(back="Tous les dispositifs", who="Pour qui", amount="Ce que vous obtenez",
            status="État aujourd'hui", catch="Le piège", source="Source officielle",
            verified="Vérifié", cta="Voir si vous êtes éligible", authority="Géré par",
            type="Type", other="Autres dispositifs", deadline="Échéance"),
 "pt": dict(back="Todos os programas", who="Para quem", amount="O que recebe",
            status="Estado hoje", catch="O senão", source="Fonte oficial",
            verified="Verificado", cta="Veja se é elegível", authority="Gerido por",
            type="Tipo", other="Outros programas", deadline="Prazo"),
}

CSS = """
:root{--paper:#fbfaf9;--sub:#f2efe9;--surface:#fff;--ink:#14181a;--muted:#6e6862;
 --brass:#b07a45;--brass-ink:#8a5c2b;--line:rgba(20,24,26,.11);--line-strong:rgba(20,24,26,.2);
 --font:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 --font-h:"Inter Tight","Inter",system-ui,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--font);
 font-size:1.0625rem;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:760px;margin:0 auto;padding:0 24px}
.wrap-wide{max-width:1140px;margin:0 auto;padding:0 24px}
header.site{border-bottom:1px solid var(--line);background:rgba(251,250,249,.9);
 position:sticky;top:0;backdrop-filter:saturate(180%) blur(10px);z-index:10}
.nav{display:flex;align-items:center;justify-content:space-between;padding:15px 0;gap:12px}
.brand{font-family:var(--font-h);font-weight:800;font-size:1.2rem;letter-spacing:-.03em;text-decoration:none}
.brand span{color:var(--brass-ink)}
.btn{display:inline-flex;align-items:center;justify-content:center;font-family:var(--font-h);
 font-weight:600;font-size:.9375rem;border-radius:.625rem;padding:12px 22px;text-decoration:none;
 background:var(--ink);color:#fff;border:1px solid var(--ink)}
.btn-ghost{background:transparent;color:var(--ink);border-color:var(--line-strong)}
main{padding:56px 0 88px}
.back{font-size:.875rem;color:var(--muted);text-decoration:none;display:inline-block;margin-bottom:28px}
.back:hover{color:var(--ink)}
h1{font-family:var(--font-h);font-weight:800;font-size:clamp(2rem,4.6vw,3rem);line-height:1.06;
 letter-spacing:-.035em;margin:0 0 14px;text-wrap:balance}
.sub{color:var(--muted);font-size:1.0625rem;margin:0 0 26px}
.badge{display:inline-flex;align-items:center;gap:7px;font-family:var(--font-h);font-weight:600;
 font-size:.8125rem;padding:6px 13px;border-radius:999px;border:1px solid currentColor}
.badge-dot{width:7px;height:7px;border-radius:50%;background:currentColor}
.meta-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:32px}
.chip{font-size:.8125rem;color:var(--muted);border:1px solid var(--line);padding:6px 12px;border-radius:999px}
.callout{border:1px solid var(--line);border-left:3px solid var(--brass);background:var(--surface);
 border-radius:.75rem;padding:20px 24px;margin:0 0 30px}
.callout strong{font-family:var(--font-h);letter-spacing:-.01em}
.block{margin:0 0 30px}
.block h2{font-family:var(--font-h);font-weight:700;font-size:.8125rem;text-transform:uppercase;
 letter-spacing:.1em;color:var(--muted);margin:0 0 9px}
.block p{margin:0;font-size:1.0625rem}
.src{background:var(--surface);border:1px solid var(--line);border-radius:.75rem;padding:20px 24px;
 display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline;justify-content:space-between;margin-bottom:36px}
.src a{color:var(--brass-ink);font-weight:600;word-break:break-all}
.src small{color:var(--muted);font-size:.8125rem}
.cta-box{background:var(--ink);color:#fff;border-radius:1.25rem;padding:34px 32px;text-align:center}
.cta-box h2{font-family:var(--font-h);font-weight:700;font-size:1.5rem;letter-spacing:-.03em;margin:0 0 10px}
.cta-box p{color:rgba(255,255,255,.72);margin:0 0 22px;font-size:.9375rem}
.cta-box .btn{background:#fff;color:var(--ink);border-color:#fff}
.others{margin-top:52px;padding-top:28px;border-top:1px solid var(--line)}
.others h2{font-family:var(--font-h);font-weight:700;font-size:1rem;letter-spacing:-.02em;margin:0 0 14px}
.others ul{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.others a{color:var(--brass-ink);text-decoration:none;font-size:.9375rem}
.others a:hover{text-decoration:underline}
.grid{display:grid;gap:16px;grid-template-columns:1fr}
@media(min-width:760px){.grid{grid-template-columns:1fr 1fr}}
.pcard{background:var(--surface);border:1px solid var(--line);border-radius:1rem;padding:22px;
 text-decoration:none;display:block;transition:border-color .15s}
.pcard:hover{border-color:var(--line-strong)}
.pcard h3{font-family:var(--font-h);font-weight:600;letter-spacing:-.02em;font-size:1.0625rem;margin:0 0 6px}
.pcard p{margin:8px 0 0;font-size:.875rem;color:var(--muted)}
.group{margin-bottom:44px}
.group > h2{font-family:var(--font-h);font-weight:700;font-size:1.25rem;letter-spacing:-.025em;margin:0 0 16px}
footer{border-top:1px solid var(--line);padding:40px 0;color:var(--muted);font-size:.875rem}
footer a{color:var(--brass-ink)}
.disclaimer{background:var(--sub);border:1px solid var(--line);border-radius:1rem;
 padding:20px 24px;font-size:.875rem;color:var(--muted);margin-top:40px}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Inter+Tight:wght@600;700;800&family=Inter:wght@400;500;600&display=swap">')


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def days_left(iso):
    if not iso:
        return None
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return (d - TODAY).days


def head(title, desc, canonical, lang, alternates=(), jsonld=None):
    alts = "".join(
        '<link rel="alternate" hreflang="%s" href="%s">' % (l, u) for l, u in alternates)
    ld = ('<script type="application/ld+json">%s</script>'
          % json.dumps(jsonld, ensure_ascii=False)) if jsonld else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%2314181a'/%3E%3Ctext x='32' y='44' font-family='Inter,sans-serif' font-size='38' font-weight='800' text-anchor='middle' fill='%23b07a45'%3ES%3C/text%3E%3C/svg%3E">\n<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
{alts}
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Sincronia">
<meta name="twitter:card" content="summary">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
{FONTS}
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="site"><div class="wrap-wide nav">
  <a href="{SITE}/" class="brand">Sin<span>cronia</span></a>
  <a href="{SITE}/#matcher" class="btn btn-ghost">{esc(UI[lang]['cta'])}</a>
</div></header>
"""


FOOT = """<footer><div class="wrap">
  <p>Sincronia — %s · <a href="%s/">%s</a></p>
</div></footer>
</body></html>"""


def program_page(p, lang):
    ui = UI[lang]
    nat = NATIVE.get(p["id"]) if lang != "en" else None
    slug = p["id"] if lang == "en" else "%s.%s" % (p["id"], lang)

    if nat:
        title = nat["title"]
        who, amount, status_note, catch = nat["who"], nat["amount"], nat["status"], nat["catch"]
    else:
        title = "%s: eligibility, amounts and current status" % p["name"]
        who, amount = p["who"], p["amount_detail"]
        status_note, catch = p["status_note"], p["catch"]

    label, color, _ = STATUS_META[p["status"]]
    dl = days_left(p.get("deadline"))
    desc = ("%s — %s. %s" % (p["name"], p["amount_short"], status_note))[:300]
    canonical = "%s/programs/%s.html" % (SITE, slug)

    alternates = [("en", "%s/programs/%s.html" % (SITE, p["id"]))]
    if p["id"] in NATIVE:
        nl = NATIVE[p["id"]]["lang"]
        alternates.append((nl, "%s/programs/%s.%s.html" % (SITE, p["id"], nl)))

    jsonld = {
        "@context": "https://schema.org",
        "@type": "GovernmentService",
        "name": p["name"],
        "serviceType": p["funding_type"],
        "provider": {"@type": "GovernmentOrganization", "name": p["authority"]},
        "areaServed": p["scope"],
        "audience": {"@type": "Audience", "audienceType": p["who"]},
        "url": canonical,
        "sameAs": p["official_url"],
    }

    deadline_html = ""
    if p.get("deadline"):
        if dl is not None and dl >= 0:
            deadline_html = ('<span class="chip"><strong>%s:</strong> %s — %d days left</span>'
                             % (esc(ui["deadline"]), p["deadline"], dl))
        else:
            deadline_html = ('<span class="chip"><strong>%s:</strong> %s</span>'
                             % (esc(ui["deadline"]), p["deadline"]))

    others = [q for q in programs if q["id"] != p["id"]
              and set(q["countries"]) & set(p["countries"])][:5]
    others_html = "".join(
        '<li><a href="%s/programs/%s.html">%s — %s</a></li>'
        % (SITE, q["id"], esc(q["name"]), esc(q["amount_short"])) for q in others)

    return head(title, desc, canonical, lang, alternates, jsonld) + f"""
<main><div class="wrap">
  <a class="back" href="{SITE}/programs/">← {esc(ui['back'])}</a>
  <h1>{esc(p['name'])}</h1>
  <p class="sub">{esc(p['authority'])} · {esc(p['scope'])}</p>

  <div class="meta-row">
    <span class="badge" style="color:{color}"><span class="badge-dot"></span>{esc(label)}</span>
    <span class="chip"><strong>{esc(ui['type'])}:</strong> {esc(p['funding_type'])}</span>
    {deadline_html}
  </div>

  <div class="callout">
    <strong>{esc(ui['status'])} — {TODAY.isoformat()}</strong><br>{esc(status_note)}
  </div>

  <div class="block"><h2>{esc(ui['amount'])}</h2><p>{esc(amount)}</p></div>
  <div class="block"><h2>{esc(ui['who'])}</h2><p>{esc(who)}</p></div>
  <div class="block"><h2>{esc(ui['catch'])}</h2><p>{esc(catch)}</p></div>

  <div class="src">
    <span><strong>{esc(ui['source'])}:</strong> <a href="{p['official_url']}" target="_blank" rel="noopener">{esc(p['official_url'])}</a></span>
    <small>{esc(ui['verified'])}: {p['last_verified']}</small>
  </div>

  <div class="cta-box">
    <h2>{esc(ui['cta'])}</h2>
    <p>{esc(UI[lang]['other'])} · {len(programs)} programmes tracked</p>
    <a class="btn" href="{SITE}/#matcher">{esc(ui['cta'])} →</a>
  </div>

  <div class="others"><h2>{esc(ui['other'])}</h2><ul>{others_html}</ul></div>

  <div class="disclaimer">Sincronia tracks public funding programmes and reviews applications. We do not guarantee any funding and we do not give tax or legal advice. Figures and deadlines change — always re-check the official source linked above before acting.</div>
</div></main>
""" + FOOT % (TODAY.isoformat(), SITE, "sincronia.live")


def index_page():
    by_scope = {}
    for p in programs:
        by_scope.setdefault(p["scope"], []).append(p)

    groups = ""
    for scope in sorted(by_scope, key=lambda s: (s != "EU", s)):
        cards = ""
        for p in sorted(by_scope[scope], key=lambda x: x["name"]):
            label, color, _ = STATUS_META[p["status"]]
            cards += f"""<a class="pcard" href="{SITE}/programs/{p['id']}.html">
  <span class="badge" style="color:{color};font-size:.6875rem;padding:4px 10px"><span class="badge-dot"></span>{esc(label)}</span>
  <h3 style="margin-top:10px">{esc(p['name'])}</h3>
  <p>{esc(p['amount_short'])}</p>
  <p style="color:var(--brass-ink)">{esc(p['authority'])}</p>
</a>"""
        groups += '<div class="group"><h2>%s</h2><div class="grid">%s</div></div>' % (esc(scope), cards)

    open_n = sum(1 for p in programs if p["status"] in ("open", "rolling", "closing"))
    title = "European funding programmes: what is actually open today"
    desc = ("%d public funding programmes across Italy, France, Spain, Germany, Portugal and the EU, "
            "each with its current status and official source. Checked %s."
            % (len(programs), TODAY.isoformat()))
    canonical = "%s/programs/" % SITE

    jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title,
        "numberOfItems": len(programs),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": p["name"],
             "url": "%s/programs/%s.html" % (SITE, p["id"])}
            for i, p in enumerate(programs)],
    }

    return head(title, desc, canonical, "en", (), jsonld) + f"""
<main><div class="wrap-wide">
  <h1>What is actually open today</h1>
  <p class="sub">{len(programs)} public funding programmes across Italy, France, Spain, Germany, Portugal
  and the EU. Every one carries its status, the official source and the date we last checked it —
  {open_n} are currently accepting applications. Last check: {TODAY.isoformat()}.</p>
  {groups}
  <div class="disclaimer">Public programmes change conditions, budgets and deadlines without notice.
  Every entry links to its official source — check it before you act. Sincronia does not guarantee
  funding and does not give tax or legal advice.</div>
</div></main>
""" + FOOT % (TODAY.isoformat(), SITE, "sincronia.live")


def main():
    PROGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    for f in PROGRAMS_DIR.glob("*.html"):
        f.unlink()

    urls = [("%s/" % SITE, "1.0"), ("%s/programs/" % SITE, "0.9")]

    (PROGRAMS_DIR / "index.html").write_text(index_page(), encoding="utf-8")

    n = 0
    for p in programs:
        (PROGRAMS_DIR / ("%s.html" % p["id"])).write_text(program_page(p, "en"), encoding="utf-8")
        urls.append(("%s/programs/%s.html" % (SITE, p["id"]), "0.8"))
        n += 1
        if p["id"] in NATIVE:
            lang = NATIVE[p["id"]]["lang"]
            fn = "%s.%s.html" % (p["id"], lang)
            (PROGRAMS_DIR / fn).write_text(program_page(p, lang), encoding="utf-8")
            urls.append(("%s/programs/%s" % (SITE, fn), "0.8"))
            n += 1

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr in urls:
        sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>"
                  % (u, TODAY.isoformat(), pr))
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE, encoding="utf-8")

    print("programme pages : %d" % n)
    print("sitemap urls    : %d" % len(urls))
    print("open/rolling    : %d of %d" % (
        sum(1 for p in programs if p["status"] in ("open", "rolling", "closing")), len(programs)))


if __name__ == "__main__":
    main()
