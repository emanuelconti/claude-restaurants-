#!/usr/bin/env python3
"""
Lead scoring & dedup — consolida tutte le liste SocialPerks_*.xlsx già raccolte
(reali, non generate) in un'unica pipeline CRM prioritizzata.

Uso:
    python3 automation/lead_scoring.py

Output:
    automation/output/prioritized_leads.csv

Nessun invio, nessuna scrittura verso l'esterno: legge solo i file .xlsx già nel repo
e scrive un CSV locale. Sicuro da rieseguire quante volte serve (idempotente — non
modifica i file sorgente).
"""
import csv
import glob
import logging
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    print("Manca openpyxl. Installa con: pip install openpyxl", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("lead_scoring")

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "automation" / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIT_SCORE = {
    "✅ Sì": 3,
    "⚠️ Medio": 1,
    "⚠️ Forse": 1,
    "❌ No": -99,  # esclude
}


def find_col(headers, *keywords):
    for i, h in enumerate(headers):
        if not h:
            continue
        low = str(h).lower()
        if any(k in low for k in keywords):
            return i
    return None


def load_file(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = rows[0]

    idx_name = find_col(headers, "nome ristorante", "nome studio")
    idx_city = find_col(headers, "arr.", "quartiere")
    idx_addr = find_col(headers, "indirizzo")
    idx_email = find_col(headers, "email")
    idx_phone = find_col(headers, "tel")
    idx_web = find_col(headers, "sito web")
    idx_insta = find_col(headers, "instagram")
    idx_type = find_col(headers, "tipo cucina", "stile")
    idx_size = find_col(headers, "dimensione")
    idx_fit = find_col(headers, "adatto")
    idx_notes = find_col(headers, "note")

    sector = "Tattoo studio" if "Tattoo" in path.name else "Ristorante"
    city = path.stem.split("_")[-1]

    out = []
    for r in rows[1:]:
        if idx_name is None or not r[idx_name]:
            continue
        email = (r[idx_email] if idx_email is not None else None) or ""
        email = str(email).strip()
        if not email:
            continue  # senza email non è azionabile per outreach email

        fit_raw = r[idx_fit] if idx_fit is not None else None
        fit_score = FIT_SCORE.get(fit_raw, 0)

        notes = (r[idx_notes] if idx_notes is not None else "") or ""
        insta = (r[idx_insta] if idx_insta is not None else "") or ""
        phone = (r[idx_phone] if idx_phone is not None else "") or ""

        score = fit_score
        score += 1 if insta else 0
        score += 1 if phone else 0
        score += 1 if len(str(notes)) > 25 else 0  # nota ricca = personalizzazione più facile

        out.append({
            "sector": sector,
            "city": city,
            "business_name": r[idx_name],
            "location_detail": r[idx_city] if idx_city is not None else "",
            "address": r[idx_addr] if idx_addr is not None else "",
            "email": email,
            "phone": phone,
            "website": r[idx_web] if idx_web is not None else "",
            "instagram": insta,
            "type_style": r[idx_type] if idx_type is not None else "",
            "size": r[idx_size] if idx_size is not None else "",
            "fit_flag": fit_raw or "",
            "notes": notes,
            "score": score,
            "source_file": path.name,
        })
    return out


def main():
    files = sorted((ROOT).glob("SocialPerks_*.xlsx"))
    if not files:
        log.error("Nessun file SocialPerks_*.xlsx trovato in %s", ROOT)
        sys.exit(1)

    all_leads = []
    for f in files:
        leads = load_file(f)
        log.info("%s -> %d lead con email", f.name, len(leads))
        all_leads.extend(leads)

    # Dedup per email (case-insensitive), tiene il punteggio più alto in caso di doppioni
    by_email = {}
    dupes = 0
    for lead in all_leads:
        key = lead["email"].lower()
        if key in by_email:
            dupes += 1
            if lead["score"] > by_email[key]["score"]:
                by_email[key] = lead
        else:
            by_email[key] = lead

    # Escludi i "❌ No" (score molto negativo)
    qualified = [l for l in by_email.values() if l["score"] > -50]
    excluded = len(by_email) - len(qualified)

    qualified.sort(key=lambda l: l["score"], reverse=True)

    for i, lead in enumerate(qualified, start=1):
        lead["rank"] = i
        lead["pipeline_stage"] = "Da contattare"
        lead["next_action"] = "Invio email 1 (variante A/B, vedi sales/MESSAGE_TEMPLATES.md)"

    out_path = OUT_DIR / "prioritized_leads.csv"
    fieldnames = [
        "rank", "score", "sector", "business_name", "city", "location_detail", "address",
        "email", "phone", "website", "instagram", "type_style", "size", "fit_flag", "notes",
        "pipeline_stage", "next_action", "source_file",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(qualified)

    log.info("Totale righe lette: %d", len(all_leads))
    log.info("Doppioni rimossi (stessa email): %d", dupes)
    log.info("Esclusi (fit ❌ No): %d", excluded)
    log.info("Lead qualificati unici: %d", len(qualified))
    log.info("Output scritto in: %s", out_path)


if __name__ == "__main__":
    main()
