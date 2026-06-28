#!/usr/bin/env python3
"""
SocialPerks — Triple Outreach Automatico — CASABLANCA
Sequenza 3 email per ristoranti Casablanca (Gmail SMTP + SQLite tracking)
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

# ── CONFIG ───────────────────────────────────────────────────────────────────
GMAIL_USER         = os.getenv("GMAIL_USER", "emanuelconti.mim@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
SENDER_NAME        = "Emanuel Conti"
BRAND              = "SocialPerks"

DELAY_EMAIL_2_DAYS = 3
DELAY_EMAIL_3_DAYS = 7
MAX_PER_DAY        = 15
PAUSE_BETWEEN      = 12
CHECK_HOUR         = 9

BASE_DIR   = Path(__file__).parent
DB_FILE    = BASE_DIR / "outreach_tracking_casablanca.db"
EXCEL_FILE = BASE_DIR / "SocialPerks_Restaurants_Casablanca.xlsx"
LOG_FILE   = BASE_DIR / "outreach_casablanca.log"

# ── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── EMAIL TEMPLATES ──────────────────────────────────────────────────────────
def get_template(step: int, restaurant_name: str) -> tuple[str, str]:
    if step == 1:
        subject = f"Partenariat {BRAND} × {restaurant_name}"
        body = """\
Bonjour,

Je me permets de vous contacter au nom de SocialPerks, une plateforme actuellement développée par des étudiants issus d'ESADE et du réseau international CEMS.

Notre ambition est de créer une plateforme qui aide les restaurants à gagner en visibilité auprès des étudiants, qu'ils soient locaux ou internationaux, tout en leur permettant de découvrir de nouveaux établissements partenaires.

Le projet est actuellement en phase de lancement dans plusieurs villes, avec l'objectif de constituer un réseau de partenaires de qualité dès aujourd'hui.

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


# ── DATABASE ─────────────────────────────────────────────────────────────────
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
    log.info("DB inizializzato: %s", DB_FILE)


def import_from_excel() -> int:
    if not EXCEL_FILE.exists():
        log.error("Excel non trovato: %s", EXCEL_FILE)
        return 0

    wb   = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    ws   = wb.active
    conn = get_conn()
    new  = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not isinstance(row[0], int):
            continue
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
    log.info("Importati %d nuovi ristoranti dal Excel", new)
    return new


# ── EMAIL SENDER ─────────────────────────────────────────────────────────────
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
        log.info("✅ [STEP] → %s | %s", to, subject[:55])
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("❌ Auth Gmail fallita — controlla GMAIL_APP_PASSWORD")
        return False
    except Exception as exc:
        log.error("❌ Errore invio a %s: %s", to, exc)
        return False


# ── OUTREACH ENGINE ───────────────────────────────────────────────────────────
def _send_step(conn, rid, name, email, step, sent_today):
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
    log.info("=== Controllo giornaliero outreach CASABLANCA ===")
    conn       = get_conn()
    now        = datetime.now()
    sent_today = [0]

    new_rests = conn.execute("""
        SELECT r.id, r.name, r.email FROM restaurants r
        WHERE r.id NOT IN (SELECT restaurant_id FROM outreach WHERE step = 1)
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
    log.info("Outreach completato: %d email inviate", sent_today[0])
    return sent_today[0]


# ── COMMANDS ─────────────────────────────────────────────────────────────────
def cmd_status():
    conn = get_conn()
    total   = conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0]
    sent1   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=1 AND status='sent'").fetchone()[0]
    sent2   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=2 AND status='sent'").fetchone()[0]
    sent3   = conn.execute("SELECT COUNT(*) FROM outreach WHERE step=3 AND status='sent'").fetchone()[0]
    replied = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='replied'").fetchone()[0]
    optout  = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='opted_out'").fetchone()[0]
    errors  = conn.execute("SELECT COUNT(*) FROM outreach WHERE status='error'").fetchone()[0]
    conn.close()

    print()
    print("=" * 52)
    print("  📊  STATO OUTREACH — CASABLANCA")
    print("=" * 52)
    print(f"  Ristoranti con email nel DB :  {total}")
    print(f"  Email 1 inviate (iniziale)  :  {sent1}")
    print(f"  Email 2 inviate (follow-up) :  {sent2}")
    print(f"  Email 3 inviate (finale)    :  {sent3}")
    print(f"  Risposte ricevute           :  {replied}")
    print(f"  Opt-out                     :  {optout}")
    print(f"  Errori invio                :  {errors}")
    print(f"  Da contattare               :  {total - sent1}")
    print("=" * 52)
    print()


def cmd_mark(email: str, status: str):
    conn = get_conn()
    row  = conn.execute("SELECT id FROM restaurants WHERE email = ?", (email,)).fetchone()
    if not row:
        print(f"Email non trovata nel DB: {email}")
        conn.close()
        return
    conn.execute("UPDATE outreach SET status = ? WHERE restaurant_id = ?", (status, row["id"]))
    conn.commit()
    conn.close()
    log.info("Marcato '%s' come %s", email, status.upper())


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if args and args[0] == "status":
        cmd_status(); return

    if args and args[0] == "import":
        init_db(); import_from_excel(); return

    if args and args[0] == "run":
        init_db(); import_from_excel()
        run_daily_outreach(); cmd_status(); return

    if args and args[0] in ("replied", "optout") and len(args) > 1:
        status_map = {"replied": "replied", "optout": "opted_out"}
        cmd_mark(args[1], status_map[args[0]]); return

    log.info("🚀 SocialPerks Outreach CASABLANCA — avvio")
    init_db()
    import_from_excel()

    if not GMAIL_APP_PASSWORD:
        print("⚠️  GMAIL_APP_PASSWORD non impostata!")
        sys.exit(1)

    run_daily_outreach()
    cmd_status()

    schedule.every().day.at(f"{CHECK_HOUR:02d}:00").do(run_daily_outreach)
    log.info("Scheduler attivo — prossima esecuzione alle %02d:00.", CHECK_HOUR)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Sistema fermato.")


if __name__ == "__main__":
    main()
