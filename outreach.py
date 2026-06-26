#!/usr/bin/env python3
"""
SocialPerks — Triple Outreach Automatico
Sequenza 3 email per ristoranti Parigi (Gmail SMTP + SQLite tracking)

Setup:
  1. Crea App Password Gmail: myaccount.google.com/apppasswords
  2. export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
  3. python3 outreach.py          # avvia scheduler automatico
     python3 outreach.py status   # mostra stato
     python3 outreach.py run      # forza esecuzione immediata
     python3 outreach.py replied  contact@restaurant.com
     python3 outreach.py optout   contact@restaurant.com
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

DELAY_EMAIL_2_DAYS = 4    # giorni tra email 1 → email 2
DELAY_EMAIL_3_DAYS = 8    # giorni tra email 1 → email 3
MAX_PER_DAY        = 15   # email max/giorno (evita spam flag)
PAUSE_BETWEEN      = 12   # secondi di pausa tra email
CHECK_HOUR         = 9    # ora del controllo giornaliero automatico

BASE_DIR   = Path(__file__).parent
DB_FILE    = BASE_DIR / "outreach_tracking.db"
EXCEL_FILE = BASE_DIR / "SocialPerks_Restaurants_Paris.xlsx"
LOG_FILE   = BASE_DIR / "outreach.log"

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
    """Ritorna (subject, body) per il dato step (1, 2 o 3)."""

    if step == 1:
        subject = f"Collaboration contenu créatif – étudiants × {restaurant_name}"
        body = f"""\
Bonjour,

Je me permets de vous contacter au nom de {BRAND}, une plateforme qui connecte \
des étudiants créatifs (photographie, vidéo, Reels) avec des restaurants instagrammables \
comme {restaurant_name}.

Le principe est simple : nos étudiants viennent dîner chez vous et créent du contenu \
professionnel pour vos réseaux sociaux, en échange d'un repas offert. Zéro frais pour vous.

Ce que vous recevez gratuitement :
• 8 à 15 photos haute qualité de vos plats et de votre salle
• 1 à 3 Reels / vidéos courtes pour votre Instagram
• Un regard frais et créatif sur votre établissement

Seriez-vous ouvert(e) à en discuter quelques minutes ?

Je reste disponible pour un appel ou un café à votre convenance.

Cordialement,
{SENDER_NAME}
{BRAND} — www.socialperks.fr"""

    elif step == 2:
        subject = f"Re: Collaboration contenu – {BRAND} × {restaurant_name}"
        body = f"""\
Bonjour,

Je me permets de revenir vers vous suite à mon message de la semaine dernière.

{BRAND} propose à {restaurant_name} une collaboration sans frais : nos étudiants créent \
du contenu photo/vidéo professionnel pour votre Instagram, en échange d'un repas offert.

Avez-vous eu l'occasion d'y réfléchir ? Je suis disponible pour répondre à toutes \
vos questions ou vous montrer des exemples de collaborations précédentes.

Cordialement,
{SENDER_NAME}
{BRAND} — www.socialperks.fr"""

    elif step == 3:
        subject = f"Dernière prise de contact – {BRAND} × {restaurant_name}"
        body = f"""\
Bonjour,

C'est mon dernier message au sujet d'une possible collaboration entre {BRAND} \
et {restaurant_name}.

Si le moment n'est pas opportun, ou si vous préférez être recontacté(e) plus tard, \
faites-le moi savoir — je comprendrai tout à fait.

Dans le cas contraire, je serais ravi(e) d'échanger avec vous : nos étudiants créent \
gratuitement du contenu photo/vidéo professionnel pour votre Instagram.

Merci pour votre temps et bonne continuation.

Cordialement,
{SENDER_NAME}
{BRAND} — www.socialperks.fr"""

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
    """Legge l'Excel e importa i ristoranti con email nel DB."""
    if not EXCEL_FILE.exists():
        log.error("Excel non trovato: %s", EXCEL_FILE)
        return 0

    wb  = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    ws  = wb.active
    conn = get_conn()
    new  = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not isinstance(row[0], int):
            continue
        # Colonne: #, Nome, Arr, Indirizzo, EMAIL, Tel, Sito, IG, Tipo, Dim, SocialPerks, Note
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
        log.error("GMAIL_APP_PASSWORD non impostata. Esegui: export GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
        return False

    msg = MIMEMultipart("alternative")
    msg["From"]    = f"{SENDER_NAME} <{GMAIL_USER}>"
    msg["To"]      = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        # Force IPv4 — patch getaddrinfo to filter out IPv6 results
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
def _send_step(conn: sqlite3.Connection, rid: int, name: str, email: str,
               step: int, sent_today: list[int]) -> bool:
    """Invia un'email e aggiorna il DB. Ritorna True se inviata."""
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
    log.info("=== Controllo giornaliero outreach ===")
    conn      = get_conn()
    now       = datetime.now()
    sent_today = [0]  # lista per passaggio per riferimento

    # Email 1 — ristoranti mai contattati
    new_rests = conn.execute("""
        SELECT r.id, r.name, r.email FROM restaurants r
        WHERE r.id NOT IN (SELECT restaurant_id FROM outreach WHERE step = 1)
          AND r.id NOT IN (SELECT restaurant_id FROM outreach WHERE status IN ('opted_out','replied'))
        LIMIT ?
    """, (MAX_PER_DAY,)).fetchall()

    for r in new_rests:
        _send_step(conn, r["id"], r["name"], r["email"], 1, sent_today)

    # Email 2 — dopo DELAY_EMAIL_2_DAYS giorni dall'email 1
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

    # Email 3 — dopo DELAY_EMAIL_3_DAYS giorni dall'email 1
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
    print("  📊  STATO OUTREACH — SOCIALPERKS PARIGI")
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
    conn.execute(
        "UPDATE outreach SET status = ? WHERE restaurant_id = ?", (status, row["id"])
    )
    conn.commit()
    conn.close()
    log.info("Marcato '%s' come %s", email, status.upper())


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if args and args[0] == "status":
        cmd_status()
        return

    if args and args[0] == "import":
        init_db(); import_from_excel()
        return

    if args and args[0] == "run":
        init_db(); import_from_excel()
        run_daily_outreach()
        cmd_status()
        return

    if args and args[0] in ("replied", "optout") and len(args) > 1:
        status_map = {"replied": "replied", "optout": "opted_out"}
        cmd_mark(args[1], status_map[args[0]])
        return

    # ── Modalità scheduler automatico ────────────────────────────────────────
    log.info("🚀 SocialPerks Outreach System — avvio")

    init_db()
    import_from_excel()

    if not GMAIL_APP_PASSWORD:
        print()
        print("⚠️  GMAIL_APP_PASSWORD non impostata!")
        print()
        print("  1. Vai su: https://myaccount.google.com/apppasswords")
        print("  2. Crea App Password per 'Mail'")
        print("  3. Esegui (Linux/Mac):")
        print("       export GMAIL_APP_PASSWORD='xxxx xxxx xxxx xxxx'")
        print("       python3 outreach.py")
        print()
        print("  Oppure aggiungi al file .env:")
        print("       GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx")
        print()
        sys.exit(1)

    # Prima esecuzione immediata
    run_daily_outreach()
    cmd_status()

    # Scheduler giornaliero
    schedule.every().day.at(f"{CHECK_HOUR:02d}:00").do(run_daily_outreach)
    log.info("Scheduler attivo — prossima esecuzione alle %02d:00. Ctrl+C per fermare.", CHECK_HOUR)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Sistema fermato.")


if __name__ == "__main__":
    main()
