#!/usr/bin/env python3
"""
SocialPerks — Multi-City Outreach Automatico
Sequenza 3 email per tutte le città (Gmail SMTP + SQLite tracking)

Usage:
  python3 outreach_multi.py --city lyon run
  python3 outreach_multi.py --city lyon status
  python3 outreach_multi.py --city lyon import
  python3 outreach_multi.py --city lyon replied contact@restaurant.com
  python3 outreach_multi.py --city lyon optout contact@restaurant.com
  python3 outreach_multi.py run --all       # tutte le città in sequenza
  python3 outreach_multi.py status --all    # stato di tutte le città
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

DELAY_EMAIL_2_DAYS = 3    # giorni tra email 1 → email 2
DELAY_EMAIL_3_DAYS = 7    # giorni tra email 1 → email 3
MAX_PER_DAY        = 15   # email max/giorno per città (evita spam flag)
PAUSE_BETWEEN      = 12   # secondi di pausa tra email
CHECK_HOUR         = 9    # ora del controllo giornaliero automatico

BASE_DIR = Path(__file__).parent

# Città → (excel_file, db_file)
CITY_MAP = {
    "paris":       ("SocialPerks_Restaurants_Paris.xlsx",       "outreach_tracking.db"),
    "paris_new":   ("SocialPerks_Restaurants_Paris_New.xlsx",   "outreach_paris_new.db"),
    "vienna":      ("SocialPerks_Restaurants_Vienna.xlsx",      "outreach_vienna.db"),
    "casablanca":  ("SocialPerks_Restaurants_Casablanca.xlsx",  "outreach_casablanca.db"),
    "lyon":        ("SocialPerks_Restaurants_Lyon.xlsx",        "outreach_lyon.db"),
    "marseille":   ("SocialPerks_Restaurants_Marseille.xlsx",   "outreach_marseille.db"),
    "bordeaux":    ("SocialPerks_Restaurants_Bordeaux.xlsx",    "outreach_bordeaux.db"),
    "toulouse":    ("SocialPerks_Restaurants_Toulouse.xlsx",    "outreach_toulouse.db"),
    "nice":        ("SocialPerks_Restaurants_Nice.xlsx",        "outreach_nice.db"),
    "nantes":      ("SocialPerks_Restaurants_Nantes.xlsx",      "outreach_nantes.db"),
    "lille":       ("SocialPerks_Restaurants_Lille.xlsx",       "outreach_lille.db"),
    "strasbourg":  ("SocialPerks_Restaurants_Strasbourg.xlsx",  "outreach_strasbourg.db"),
}

# Stato corrente della città (impostato da set_city)
DB_FILE    = BASE_DIR / "outreach_paris.db"
EXCEL_FILE = BASE_DIR / "SocialPerks_Restaurants_Paris.xlsx"
CURRENT_CITY = "paris"

LOG_FILE = BASE_DIR / "outreach_multi.log"

# ── LOGGING ───────────────────────────────────────────────────────────────────
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
    """Imposta DB_FILE e EXCEL_FILE per la città specificata."""
    global DB_FILE, EXCEL_FILE, CURRENT_CITY
    if city not in CITY_MAP:
        print(f"Città sconosciuta: '{city}'. Disponibili: {', '.join(CITY_MAP)}")
        sys.exit(1)
    excel_name, db_name = CITY_MAP[city]
    EXCEL_FILE   = BASE_DIR / excel_name
    DB_FILE      = BASE_DIR / db_name
    CURRENT_CITY = city


# ── EMAIL TEMPLATES ───────────────────────────────────────────────────────────
def get_template(step: int, restaurant_name: str) -> tuple[str, str]:
    """Ritorna (subject, body) per il dato step (1, 2 o 3)."""

    if step == 1:
        subject = f"Partenariat {BRAND} × {restaurant_name}"
        body = """\
Bonjour,

Je me permets de vous contacter au nom de SocialPerks, une plateforme actuellement développée par des étudiants issus d'ESADE et du réseau international CEMS.

Notre ambition est de créer une plateforme qui aide les restaurants à gagner en visibilité auprès des étudiants, qu'ils soient locaux ou internationaux, tout en leur permettant de découvrir de nouveaux établissements partenaires.

Le projet est actuellement en phase de lancement dans plusieurs villes européennes, avec l'objectif de constituer un réseau de partenaires de qualité dès aujourd'hui.

Nous invitons les restaurants intéressés à manifester leur intérêt en signant notre lettre d'intérêt, accessible ici :

https://socialperks-fr.vercel.app/

Cette lettre ne constitue pas un engagement commercial. Elle nous permet simplement d'identifier les établissements souhaitant être informés et participer au lancement de la plateforme.

Nous serions ravis de compter votre établissement parmi nos premiers partenaires.

Bien cordialement,

L'équipe SocialPerks"""

    elif step == 2:
        subject = f"Re: Partenariat {BRAND} × {restaurant_name}"
        body = """\
Bonjour,

Je me permets de revenir vers vous concernant SocialPerks.

Nous constituons actuellement notre premier réseau de restaurants partenaires avant le lancement de la plateforme.

Si le projet vous intéresse, vous pouvez simplement signer notre lettre d'intérêt afin d'être informé des prochaines étapes :

https://socialperks-fr.vercel.app/

Je reste à votre disposition si vous avez la moindre question.

Bien cordialement,

L'équipe SocialPerks"""

    elif step == 3:
        subject = f"Dernier message – {BRAND} × {restaurant_name}"
        body = """\
Bonjour,

Il s'agit de mon dernier message concernant SocialPerks.

Si vous souhaitez faire partie des premiers restaurants partenaires et suivre l'évolution du projet, vous pouvez manifester votre intérêt en remplissant notre lettre d'intérêt :

https://socialperks-fr.vercel.app/

Merci pour votre temps et au plaisir d'échanger avec vous.

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
        CREATE TABLE IF NOT EXISTS restaurants (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT    NOT NULL,
            email          TEXT    NOT NULL UNIQUE,
            arrondissement TEXT,
            instagram      TEXT,
            added_at       TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS outreach (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id   INTEGER NOT NULL,
            step            INTEGER NOT NULL,
            sent_at         TEXT,
            status          TEXT    DEFAULT 'pending',
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
            UNIQUE (restaurant_id, step)
        );
    """)
    conn.commit()
    conn.close()
    log.info("[%s] DB inizializzato: %s", CURRENT_CITY.upper(), DB_FILE)


def import_from_excel() -> int:
    """Legge l'Excel e importa i ristoranti con email nel DB."""
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
        # Colonne: #, Nome, Quartiere, Indirizzo, EMAIL, Tel, Sito, IG, Tipo, Dim, SocialPerks, Note
        name  = row[1]
        arr   = row[2]
        email = row[4]
        ig    = row[7]

        if not email or "@" not in str(email):
            continue

        cur = conn.execute(
            "INSERT OR IGNORE INTO restaurants (name, email, arrondissement, instagram) VALUES (?,?,?,?)",
            (name, str(email).strip(), arr, ig),
        )
        if cur.lastrowid and cur.rowcount:
            new += 1

    conn.commit()
    conn.close()
    log.info("[%s] Importati %d nuovi ristoranti dall'Excel", CURRENT_CITY.upper(), new)
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
        log.error("[%s] ❌ Auth Gmail fallita — controlla GMAIL_APP_PASSWORD", CURRENT_CITY.upper())
        return False
    except Exception as exc:
        log.error("[%s] ❌ Errore invio a %s: %s", CURRENT_CITY.upper(), to, exc)
        return False


# ── OUTREACH ENGINE ───────────────────────────────────────────────────────────
def _send_step(conn: sqlite3.Connection, rid: int, name: str, email: str,
               step: int, sent_today: list[int]) -> bool:
    if sent_today[0] >= MAX_PER_DAY:
        return False

    subject, body = get_template(step, name)
    status = "sent" if send_email(email, subject, body) else "error"

    conn.execute(
        "INSERT OR REPLACE INTO outreach (restaurant_id, step, sent_at, status) VALUES (?,?,?,?)",
        (rid, step, datetime.now().isoformat(), status),
    )
    conn.commit()

    if status == "sent":
        sent_today[0] += 1
        time.sleep(PAUSE_BETWEEN)
        return True
    return False


def run_daily_outreach() -> int:
    log.info("[%s] === Controllo giornaliero outreach ===", CURRENT_CITY.upper())
    conn       = get_conn()
    now        = datetime.now()
    sent_today = [0]

    new_rests = conn.execute("""
        SELECT r.id, r.name, r.email FROM restaurants r
        WHERE r.id NOT IN (SELECT restaurant_id FROM outreach WHERE step = 1 AND status = 'sent')
          AND r.id NOT IN (SELECT restaurant_id FROM outreach WHERE status IN ('opted_out','replied'))
        LIMIT ?
    """, (MAX_PER_DAY,)).fetchall()

    for r in new_rests:
        _send_step(conn, r["id"], r["name"], r["email"], 1, sent_today)

    cutoff2 = (now - timedelta(days=DELAY_EMAIL_2_DAYS)).isoformat()
    followup2 = conn.execute("""
        SELECT r.id, r.name, r.email FROM restaurants r
        JOIN outreach o1 ON o1.restaurant_id = r.id AND o1.step = 1 AND o1.status = 'sent'
        WHERE o1.sent_at <= ?
          AND r.id NOT IN (SELECT restaurant_id FROM outreach WHERE step = 2)
          AND r.id NOT IN (SELECT restaurant_id FROM outreach WHERE status IN ('opted_out','replied'))
        LIMIT ?
    """, (cutoff2, MAX_PER_DAY - sent_today[0])).fetchall()

    for r in followup2:
        _send_step(conn, r["id"], r["name"], r["email"], 2, sent_today)

    cutoff3 = (now - timedelta(days=DELAY_EMAIL_3_DAYS)).isoformat()
    followup3 = conn.execute("""
        SELECT r.id, r.name, r.email FROM restaurants r
        JOIN outreach o1 ON o1.restaurant_id = r.id AND o1.step = 1 AND o1.status = 'sent'
        WHERE o1.sent_at <= ?
          AND r.id NOT IN (SELECT restaurant_id FROM outreach WHERE step = 3)
          AND r.id NOT IN (SELECT restaurant_id FROM outreach WHERE status IN ('opted_out','replied'))
        LIMIT ?
    """, (cutoff3, MAX_PER_DAY - sent_today[0])).fetchall()

    for r in followup3:
        _send_step(conn, r["id"], r["name"], r["email"], 3, sent_today)

    conn.close()
    log.info("[%s] Outreach completato: %d email inviate", CURRENT_CITY.upper(), sent_today[0])
    return sent_today[0]


# ── COMMANDS ──────────────────────────────────────────────────────────────────
def cmd_status():
    conn    = get_conn()
    total   = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
    sent1   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=1 AND status='sent'").fetchone()[0]
    sent2   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=2 AND status='sent'").fetchone()[0]
    sent3   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=3 AND status='sent'").fetchone()[0]
    replied = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='replied'").fetchone()[0]
    optout  = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='opted_out'").fetchone()[0]
    errors  = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='error'").fetchone()[0]
    conn.close()

    city_label = CURRENT_CITY.upper().replace("_", " ")
    print()
    print("=" * 54)
    print(f"  STATO OUTREACH — SOCIALPERKS {city_label}")
    print("=" * 54)
    print(f"  Ristoranti nel DB           :  {total}")
    print(f"  Email 1 inviate (iniziale)  :  {sent1}")
    print(f"  Email 2 inviate (follow-up) :  {sent2}")
    print(f"  Email 3 inviate (finale)    :  {sent3}")
    print(f"  Risposte ricevute           :  {replied}")
    print(f"  Opt-out                     :  {optout}")
    print(f"  Errori invio                :  {errors}")
    print(f"  Da contattare               :  {total - sent1}")
    print("=" * 54)
    print()


def cmd_status_all():
    original = CURRENT_CITY
    grand_total = grand_sent1 = grand_not_contacted = 0
    print()
    print("=" * 60)
    print("  STATO OUTREACH GLOBALE — SOCIALPERKS")
    print("=" * 60)
    print(f"  {'Città':<14} {'Nel DB':>7} {'E1':>5} {'E2':>5} {'E3':>5} {'Risp':>5} {'Err':>5}")
    print("-" * 60)
    for city in CITY_MAP:
        set_city(city)
        if not DB_FILE.exists():
            print(f"  {city:<14} {'—':>7}")
            continue
        conn    = get_conn()
        total   = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
        sent1   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=1 AND status='sent'").fetchone()[0]
        sent2   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=2 AND status='sent'").fetchone()[0]
        sent3   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=3 AND status='sent'").fetchone()[0]
        replied = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='replied'").fetchone()[0]
        errors  = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='error'").fetchone()[0]
        conn.close()
        print(f"  {city:<14} {total:>7} {sent1:>5} {sent2:>5} {sent3:>5} {replied:>5} {errors:>5}")
        grand_total      += total
        grand_sent1      += sent1
        grand_not_contacted += (total - sent1)
    print("-" * 60)
    print(f"  {'TOTALE':<14} {grand_total:>7}  email inviate E1: {grand_sent1}  da contattare: {grand_not_contacted}")
    print("=" * 60)
    print()
    set_city(original)


def cmd_mark(email: str, status: str):
    conn = get_conn()
    row  = conn.execute("SELECT id FROM restaurants WHERE email = ?", (email,)).fetchone()
    if not row:
        print(f"Email non trovata nel DB: {email}")
        conn.close()
        return
    conn.execute(
        "UPDATE outreach SET status = ? WHERE restaurant_id = ?", (status, row["id"])
    )
    conn.commit()
    conn.close()
    log.info("[%s] Marcato '%s' come %s", CURRENT_CITY.upper(), email, status.upper())


def run_all_cities():
    """Esegue outreach per tutte le città in sequenza."""
    total_sent = 0
    for city in CITY_MAP:
        set_city(city)
        if not EXCEL_FILE.exists():
            log.warning("[%s] Excel non trovato, skip.", city.upper())
            continue
        log.info("[%s] ─── Inizio outreach ───", city.upper())
        init_db()
        import_from_excel()
        sent = run_daily_outreach()
        total_sent += sent
        log.info("[%s] ─── Fine: %d email inviate ───", city.upper(), sent)
    log.info("=== TOTALE GIORNALIERO: %d email inviate su %d città ===", total_sent, len(CITY_MAP))
    return total_sent


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    args = list(sys.argv[1:])

    # Parsing --city
    city = None
    if "--city" in args:
        idx  = args.index("--city")
        city = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    run_all = "--all" in args
    if run_all:
        args.remove("--all")

    cmd = args[0] if args else None

    # ── status --all ──────────────────────────────────────────────────────────
    if cmd == "status" and run_all:
        cmd_status_all()
        return

    # ── run --all ─────────────────────────────────────────────────────────────
    if cmd == "run" and run_all:
        if not GMAIL_APP_PASSWORD:
            print("⚠️  GMAIL_APP_PASSWORD non impostata — export GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
            sys.exit(1)
        run_all_cities()
        cmd_status_all()
        return

    # ── Comandi per città singola ─────────────────────────────────────────────
    if not city:
        print("Specifica --city CITTÀ oppure usa --all.")
        print(f"Città disponibili: {', '.join(CITY_MAP)}")
        print()
        print("Esempi:")
        print("  python3 outreach_multi.py --city lyon run")
        print("  python3 outreach_multi.py run --all")
        print("  python3 outreach_multi.py status --all")
        sys.exit(1)

    set_city(city)

    if cmd == "status":
        cmd_status()
        return

    if cmd == "import":
        init_db(); import_from_excel()
        return

    if cmd == "run":
        if not GMAIL_APP_PASSWORD:
            print("⚠️  GMAIL_APP_PASSWORD non impostata.")
            sys.exit(1)
        init_db(); import_from_excel()
        run_daily_outreach()
        cmd_status()
        return

    if cmd in ("replied", "optout") and len(args) > 1:
        init_db()
        status_map = {"replied": "replied", "optout": "opted_out"}
        cmd_mark(args[1], status_map[cmd])
        return

    # ── Modalità scheduler automatico ────────────────────────────────────────
    log.info("SocialPerks Outreach — avvio scheduler per %s", city.upper())
    init_db()
    import_from_excel()

    if not GMAIL_APP_PASSWORD:
        print("⚠️  GMAIL_APP_PASSWORD non impostata — export GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
        sys.exit(1)

    run_daily_outreach()
    cmd_status()

    schedule.every().day.at(f"{CHECK_HOUR:02d}:00").do(run_daily_outreach)
    log.info("Scheduler attivo — controllo alle %02d:00. Ctrl+C per fermare.", CHECK_HOUR)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Sistema fermato.")


if __name__ == "__main__":
    main()
