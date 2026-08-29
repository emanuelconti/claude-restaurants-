#!/usr/bin/env python3
"""
SocialPerks — Multi-City Tattoo Outreach Automatico
Sequenza 3 email per tutti i tattoo studios (Gmail SMTP + SQLite tracking)

Usage:
  python3 outreach_tattoo.py run --all
  python3 outreach_tattoo.py status --all
  python3 outreach_tattoo.py --city paris run
  python3 outreach_tattoo.py --city lyon status
  python3 outreach_tattoo.py --city nice replied contact@studio.fr
  python3 outreach_tattoo.py --city bordeaux optout info@studio.fr
"""

import sqlite3
import smtplib
import socket
import time
import logging
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path

import schedule
import openpyxl

# ── CONFIG ────────────────────────────────────────────────────────────────────
GMAIL_USER         = os.getenv("GMAIL_USER", "emanuelconti.mim@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
SENDER_NAME        = "Emanuel Conti"
BRAND              = "SocialPerks"
LANDING_URL        = "https://socialperk.netlify.app/france/"

DELAY_EMAIL_2_DAYS = 3
DELAY_EMAIL_3_DAYS = 7
MAX_PER_DAY        = 15
PAUSE_BETWEEN      = 12
CHECK_HOUR         = 9

BASE_DIR = Path(__file__).parent

CITY_MAP = {
    "paris":       ("SocialPerks_Tattoo_Paris.xlsx",       "outreach_tattoo_paris.db"),
    "lyon":        ("SocialPerks_Tattoo_Lyon.xlsx",        "outreach_tattoo_lyon.db"),
    "marseille":   ("SocialPerks_Tattoo_Marseille.xlsx",   "outreach_tattoo_marseille.db"),
    "bordeaux":    ("SocialPerks_Tattoo_Bordeaux.xlsx",    "outreach_tattoo_bordeaux.db"),
    "toulouse":    ("SocialPerks_Tattoo_Toulouse.xlsx",    "outreach_tattoo_toulouse.db"),
    "nice":        ("SocialPerks_Tattoo_Nice.xlsx",        "outreach_tattoo_nice.db"),
    "nantes":      ("SocialPerks_Tattoo_Nantes.xlsx",      "outreach_tattoo_nantes.db"),
    "lille":       ("SocialPerks_Tattoo_Lille.xlsx",       "outreach_tattoo_lille.db"),
    "strasbourg":  ("SocialPerks_Tattoo_Strasbourg.xlsx",  "outreach_tattoo_strasbourg.db"),
}

DB_FILE      = BASE_DIR / "outreach_tattoo_paris.db"
EXCEL_FILE   = BASE_DIR / "SocialPerks_Tattoo_Paris.xlsx"
CURRENT_CITY = "paris"

LOG_FILE = BASE_DIR / "outreach_tattoo.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def set_city(city: str):
    global DB_FILE, EXCEL_FILE, CURRENT_CITY
    if city not in CITY_MAP:
        print(f"Città sconosciuta: '{city}'. Disponibili: {', '.join(CITY_MAP)}")
        sys.exit(1)
    excel_name, db_name = CITY_MAP[city]
    EXCEL_FILE   = BASE_DIR / excel_name
    DB_FILE      = BASE_DIR / db_name
    CURRENT_CITY = city


# ── EMAIL TEMPLATES ───────────────────────────────────────────────────────────
def get_template(step: int, studio_name: str) -> tuple[str, str]:
    if step == 1:
        subject = f"Partenariat {BRAND} × {studio_name}"
        body = f"""\
Bonjour,

Je me permets de vous contacter au nom de SocialPerks, une plateforme actuellement développée par des étudiants issus d'ESADE et du réseau international CEMS.

Notre concept est simple : nous mettons en relation des studios de tatouage avec des étudiants créateurs de contenu, passionnés de tatouage, qui souhaitent valoriser votre travail sur leurs réseaux sociaux (Instagram, TikTok).

Ces étudiants réalisent des photos et vidéos professionnelles de votre studio et de vos créations, en échange d'une visibilité partagée — une collaboration gagnant-gagnant pour booster votre présence digitale.

Le projet est en phase de lancement dans plusieurs villes françaises. Nous constituons actuellement notre premier réseau de studios partenaires.

Si le concept vous intéresse, vous pouvez manifester votre intérêt ici :

{LANDING_URL}

Cette démarche ne constitue aucun engagement commercial — elle nous permet simplement d'identifier les studios souhaitant participer au lancement.

Nous serions ravis de compter votre studio parmi nos premiers partenaires.

Bien cordialement,

L'équipe SocialPerks"""

    elif step == 2:
        subject = f"Re: Partenariat {BRAND} × {studio_name}"
        body = f"""\
Bonjour,

Je me permets de revenir vers vous au sujet de SocialPerks.

Nous construisons actuellement notre réseau de studios partenaires avant le lancement officiel de la plateforme. L'idée : des étudiants créateurs de contenu mettent en valeur votre travail sur Instagram et TikTok, en échange d'une expérience et d'une visibilité partagée.

Si vous souhaitez en faire partie, il suffit de signer notre lettre d'intérêt :

{LANDING_URL}

Je reste disponible pour toute question.

Bien cordialement,

L'équipe SocialPerks"""

    elif step == 3:
        subject = f"Dernier message – {BRAND} × {studio_name}"
        body = f"""\
Bonjour,

Il s'agit de mon dernier message concernant SocialPerks.

Si vous souhaitez que votre studio fasse partie des premiers partenaires et bénéficie d'une visibilité accrue auprès des étudiants créateurs de contenu, vous pouvez encore manifester votre intérêt :

{LANDING_URL}

Merci pour votre temps et bonne continuation.

Bien cordialement,

L'équipe SocialPerks"""

    else:
        raise ValueError(f"Step non valido: {step}")

    return subject, body


# ── DATABASE ──────────────────────────────────────────────────────────────────
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS studios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            email     TEXT    NOT NULL UNIQUE,
            quartiere TEXT,
            instagram TEXT,
            added_at  TEXT    DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS outreach (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            studio_id    INTEGER NOT NULL,
            step         INTEGER NOT NULL,
            sent_at      TEXT,
            status       TEXT    DEFAULT 'pending',
            FOREIGN KEY (studio_id) REFERENCES studios(id),
            UNIQUE (studio_id, step)
        );
    """)
    conn.commit()
    conn.close()
    log.info("[%s] DB inizializzato: %s", CURRENT_CITY.upper(), DB_FILE)


def import_from_excel() -> int:
    if not EXCEL_FILE.exists():
        log.error("[%s] Excel non trovato: %s", CURRENT_CITY.upper(), EXCEL_FILE)
        return 0

    wb   = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    ws   = wb.active
    conn = get_conn()
    new  = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not isinstance(row[0], int):
            continue
        # Colonne: #, Nome Studio, Quartiere, Indirizzo, EMAIL, Tel, Sito, IG, Stile, Dim, SP, Note
        name  = row[1]
        qrt   = row[2]
        email = row[4]
        ig    = row[7]

        if not email or "@" not in str(email):
            continue

        cur = conn.execute(
            "INSERT OR IGNORE INTO studios (name, email, quartiere, instagram) VALUES (?,?,?,?)",
            (name, str(email).strip(), qrt, ig),
        )
        if cur.lastrowid and cur.rowcount:
            new += 1

    conn.commit()
    conn.close()
    log.info("[%s] Importati %d nuovi studios dall'Excel", CURRENT_CITY.upper(), new)
    return new


# ── EMAIL SENDER ──────────────────────────────────────────────────────────────
def send_email(to: str, subject: str, body: str) -> bool:
    if not GMAIL_APP_PASSWORD:
        log.error("GMAIL_APP_PASSWORD non impostata.")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"]    = f"{SENDER_NAME} <{GMAIL_USER}>"
    msg["To"]      = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        _orig_gai = socket.getaddrinfo
        socket.getaddrinfo = lambda *a, **kw: [
            r for r in _orig_gai(*a, **kw) if r[0] == socket.AF_INET
        ]
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as srv:
                srv.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                srv.sendmail(GMAIL_USER, to, msg.as_string())
        finally:
            socket.getaddrinfo = _orig_gai
        log.info("[%s] ✅ → %s | %s", CURRENT_CITY.upper(), to, subject[:55])
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("[%s] ❌ Auth Gmail fallita", CURRENT_CITY.upper())
        return False
    except Exception as exc:
        log.error("[%s] ❌ Errore invio a %s: %s", CURRENT_CITY.upper(), to, exc)
        return False


# ── OUTREACH ENGINE ───────────────────────────────────────────────────────────
def _send_step(conn, sid: int, name: str, email: str, step: int, sent_today: list) -> bool:
    if sent_today[0] >= MAX_PER_DAY:
        return False
    subject, body = get_template(step, name)
    status = "sent" if send_email(email, subject, body) else "error"
    conn.execute(
        "INSERT OR REPLACE INTO outreach (studio_id, step, sent_at, status) VALUES (?,?,?,?)",
        (sid, step, datetime.now().isoformat(), status),
    )
    conn.commit()
    if status == "sent":
        sent_today[0] += 1
        time.sleep(PAUSE_BETWEEN)
        return True
    return False


def run_daily_outreach() -> int:
    log.info("[%s] === Controllo giornaliero tattoo outreach ===", CURRENT_CITY.upper())
    conn       = get_conn()
    now        = datetime.now()
    sent_today = [0]

    # Email 1 — studios mai contattati con successo
    new_studios = conn.execute("""
        SELECT s.id, s.name, s.email FROM studios s
        WHERE s.id NOT IN (SELECT studio_id FROM outreach WHERE step = 1 AND status = 'sent')
          AND s.id NOT IN (SELECT studio_id FROM outreach WHERE status IN ('opted_out','replied'))
        LIMIT ?
    """, (MAX_PER_DAY,)).fetchall()
    for s in new_studios:
        _send_step(conn, s["id"], s["name"], s["email"], 1, sent_today)

    # Email 2 — dopo 3 giorni
    cutoff2 = (now - timedelta(days=DELAY_EMAIL_2_DAYS)).isoformat()
    for s in conn.execute("""
        SELECT s.id, s.name, s.email FROM studios s
        JOIN outreach o1 ON o1.studio_id = s.id AND o1.step = 1 AND o1.status = 'sent'
        WHERE o1.sent_at <= ?
          AND s.id NOT IN (SELECT studio_id FROM outreach WHERE step = 2)
          AND s.id NOT IN (SELECT studio_id FROM outreach WHERE status IN ('opted_out','replied'))
        LIMIT ?
    """, (cutoff2, MAX_PER_DAY - sent_today[0])).fetchall():
        _send_step(conn, s["id"], s["name"], s["email"], 2, sent_today)

    # Email 3 — dopo 7 giorni
    cutoff3 = (now - timedelta(days=DELAY_EMAIL_3_DAYS)).isoformat()
    for s in conn.execute("""
        SELECT s.id, s.name, s.email FROM studios s
        JOIN outreach o1 ON o1.studio_id = s.id AND o1.step = 1 AND o1.status = 'sent'
        WHERE o1.sent_at <= ?
          AND s.id NOT IN (SELECT studio_id FROM outreach WHERE step = 3)
          AND s.id NOT IN (SELECT studio_id FROM outreach WHERE status IN ('opted_out','replied'))
        LIMIT ?
    """, (cutoff3, MAX_PER_DAY - sent_today[0])).fetchall():
        _send_step(conn, s["id"], s["name"], s["email"], 3, sent_today)

    conn.close()
    log.info("[%s] Tattoo outreach: %d email inviate", CURRENT_CITY.upper(), sent_today[0])
    return sent_today[0]


# ── STATUS ────────────────────────────────────────────────────────────────────
def cmd_status():
    conn    = get_conn()
    total   = conn.execute("SELECT COUNT(*) FROM studios").fetchone()[0]
    sent1   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=1 AND status='sent'").fetchone()[0]
    sent2   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=2 AND status='sent'").fetchone()[0]
    sent3   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=3 AND status='sent'").fetchone()[0]
    replied = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='replied'").fetchone()[0]
    optout  = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='opted_out'").fetchone()[0]
    conn.close()
    city_label = CURRENT_CITY.upper().replace("_", " ")
    print(f"\n{'='*54}\n  TATTOO OUTREACH — SOCIALPERKS {city_label}\n{'='*54}")
    print(f"  Studios nel DB   : {total}")
    print(f"  Email 1 inviate  : {sent1}")
    print(f"  Email 2 inviate  : {sent2}")
    print(f"  Email 3 inviate  : {sent3}")
    print(f"  Risposte         : {replied}")
    print(f"  Opt-out          : {optout}")
    print(f"  Da contattare    : {total - sent1}")
    print(f"{'='*54}\n")


def cmd_status_all():
    grand_total = grand_sent1 = 0
    print(f"\n{'='*62}\n  STATO TATTOO OUTREACH GLOBALE — SOCIALPERKS\n{'='*62}")
    print(f"  {'Città':<14} {'DB':>6} {'E1':>5} {'E2':>5} {'E3':>5} {'Risp':>5}")
    print("-"*62)
    for city in CITY_MAP:
        set_city(city)
        if not DB_FILE.exists():
            print(f"  {city:<14} {'—':>6}"); continue
        conn  = get_conn()
        total = conn.execute("SELECT COUNT(*) FROM studios").fetchone()[0]
        s1    = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=1 AND status='sent'").fetchone()[0]
        s2    = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=2 AND status='sent'").fetchone()[0]
        s3    = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=3 AND status='sent'").fetchone()[0]
        rep   = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='replied'").fetchone()[0]
        conn.close()
        print(f"  {city:<14} {total:>6} {s1:>5} {s2:>5} {s3:>5} {rep:>5}")
        grand_total += total; grand_sent1 += s1
    print(f"-"*62)
    print(f"  {'TOTALE':<14} {grand_total:>6}  già contattati E1: {grand_sent1}")
    print(f"{'='*62}\n")


def cmd_mark(email: str, status: str):
    conn = get_conn()
    row  = conn.execute("SELECT id FROM studios WHERE email = ?", (email,)).fetchone()
    if not row:
        print(f"Email non trovata: {email}"); conn.close(); return
    conn.execute("UPDATE outreach SET status = ? WHERE studio_id = ?", (status, row["id"]))
    conn.commit(); conn.close()
    log.info("[%s] Marcato '%s' come %s", CURRENT_CITY.upper(), email, status.upper())


def run_all_cities():
    total_sent = 0
    for city in CITY_MAP:
        set_city(city)
        if not EXCEL_FILE.exists():
            log.warning("[%s] Excel non trovato, skip.", city.upper()); continue
        log.info("[%s] ─── Inizio tattoo outreach ───", city.upper())
        init_db(); import_from_excel()
        sent = run_daily_outreach()
        total_sent += sent
        log.info("[%s] ─── Fine: %d email inviate ───", city.upper(), sent)
    log.info("=== TATTOO TOTALE: %d email su %d città ===", total_sent, len(CITY_MAP))
    return total_sent


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    args = list(sys.argv[1:])
    city = None
    if "--city" in args:
        idx = args.index("--city"); city = args[idx + 1]; args = args[:idx] + args[idx + 2:]
    run_all = "--all" in args
    if run_all: args.remove("--all")
    cmd = args[0] if args else None

    if cmd == "status" and run_all: cmd_status_all(); return
    if cmd == "run" and run_all:
        if not GMAIL_APP_PASSWORD:
            print("⚠️  GMAIL_APP_PASSWORD non impostata."); sys.exit(1)
        run_all_cities(); cmd_status_all(); return

    if not city:
        print(f"Uso: python3 outreach_tattoo.py [--city CITTÀ] COMANDO [--all]")
        print(f"Città: {', '.join(CITY_MAP)}")
        print("Es: python3 outreach_tattoo.py run --all")
        sys.exit(1)

    set_city(city)
    if cmd == "status": cmd_status(); return
    if cmd == "import": init_db(); import_from_excel(); return
    if cmd == "run":
        if not GMAIL_APP_PASSWORD: print("⚠️  GMAIL_APP_PASSWORD non impostata."); sys.exit(1)
        init_db(); import_from_excel(); run_daily_outreach(); cmd_status(); return
    if cmd in ("replied", "optout") and len(args) > 1:
        init_db(); cmd_mark(args[1], {"replied": "replied", "optout": "opted_out"}[cmd]); return

    # Scheduler automatico per singola città
    init_db(); import_from_excel()
    if not GMAIL_APP_PASSWORD: print("⚠️  GMAIL_APP_PASSWORD non impostata."); sys.exit(1)
    run_daily_outreach(); cmd_status()
    schedule.every().day.at(f"{CHECK_HOUR:02d}:00").do(run_daily_outreach)
    try:
        while True: schedule.run_pending(); time.sleep(60)
    except KeyboardInterrupt: log.info("Sistema fermato.")


if __name__ == "__main__":
    main()
