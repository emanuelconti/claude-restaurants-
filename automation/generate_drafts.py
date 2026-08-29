#!/usr/bin/env python3
"""
Genera bozze email personalizzate per i lead con punteggio più alto in
automation/output/prioritized_leads.csv.

IMPORTANTE: questo script scrive solo un file locale di bozze. Non invia nulla,
non ha accesso a nessuna credenziale SMTP. L'invio resta un'azione separata,
manuale, verso terzi reali fuori da questo repo.

Uso:
    python3 automation/generate_drafts.py [--limit 30]
"""
import argparse
import csv
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("generate_drafts")

ROOT = Path(__file__).resolve().parent.parent
IN_PATH = ROOT / "automation" / "output" / "prioritized_leads.csv"
OUT_PATH = ROOT / "automation" / "output" / "draft_batch_1.md"


def french_observation(lead: dict) -> str:
    """Costruisce l'osservazione in francese SOLO da campi strutturati reali
    (stile/quartiere/instagram) — mai traducendo automaticamente la nota italiana
    dentro la frase, per evitare frasi ibride IT/FR poco professionali."""
    style = (lead["type_style"] or "").strip()
    area = (lead["location_detail"] or "").strip()
    insta = (lead["instagram"] or "").strip()
    if style and area:
        return f"votre adresse {area} ({style.lower()}) a l'air d'avoir un vrai cachet"
    if style:
        return f"votre univers ({style.lower()}) se distingue bien, même juste en ligne"
    if insta:
        return "votre profil se démarque dans le quartier"
    return "votre établissement a l'air d'avoir un vrai cachet"


def build_email(lead: dict):
    is_tattoo = lead["sector"] == "Tattoo studio"
    kind_fr = "studio" if is_tattoo else "établissement"
    obs = french_observation(lead)
    subject = f"Vos heures creuses chez {lead['business_name']}"
    body = f"""Bonjour,

J'ai vu que {obs}. Beaucoup d'{kind_fr}s comme le vôtre perdent du chiffre d'affaires sur
1-2 créneaux calmes par semaine, sans vraiment le mesurer.

On propose un pilote de 4 semaines pour remplir spécifiquement ces créneaux avec des clients
locaux — sans app à installer de votre côté. Ça vous intéresserait d'en discuter 10 minutes
cette semaine ?

Emanuel — SocialPerks
"""
    internal_note = (lead["notes"] or "").strip()
    return subject, body, internal_note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    if not IN_PATH.exists():
        log.error("Manca %s — esegui prima automation/lead_scoring.py", IN_PATH)
        return

    with open(IN_PATH, encoding="utf-8") as fh:
        leads = list(csv.DictReader(fh))

    top = leads[: args.limit]

    lines = [
        "# Bozze email — batch 1 (NON INVIATE)",
        "",
        f"Generato da `automation/generate_drafts.py` sui {len(top)} lead con punteggio più "
        "alto in `automation/output/prioritized_leads.csv`. Ogni osservazione personalizzata "
        "viene dalla nota già raccolta per quel lead specifico (dato reale, non inventato).",
        "",
        "**Questo file non invia nulla.** Serve solo come bozza pronta da rivedere e "
        "inviare manualmente (o autorizzare per invio) quando deciderai.",
        "",
        "---",
        "",
    ]
    for i, lead in enumerate(top, start=1):
        subject, body, internal_note = build_email(lead)
        lines.append(f"## {i}. {lead['business_name']} — {lead['city']} ({lead['sector']})")
        lines.append(f"- Email: {lead['email']}")
        lines.append(f"- Instagram: {lead['instagram'] or '—'} · Sito: {lead['website'] or '—'}")
        lines.append(f"- Punteggio: {lead['score']} · Fit: {lead['fit_flag']}")
        if internal_note:
            lines.append(f"- *Nota interna (IT, per personalizzare ulteriormente a mano se vuoi):* {internal_note}")
        lines.append("")
        lines.append(f"**Oggetto:** {subject}")
        lines.append("")
        lines.append("```")
        lines.append(body.strip())
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    log.info("Scritte %d bozze in %s", len(top), OUT_PATH)


if __name__ == "__main__":
    main()
