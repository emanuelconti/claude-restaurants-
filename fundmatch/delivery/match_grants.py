#!/usr/bin/env python3
"""
GrantPath — motore di matching bandi/finanziamenti.

Prende un profilo azienda (paese, settore/parole chiave, fase) e lo confronta con il
database REALE e verificato in fundmatch/data/programs.json (nessun bando è inventato:
ogni riga ha un link ufficiale e una data di ultima verifica).

Uso:
    python3 match_grants.py --country IT --keywords "AI,digitalizzazione" --stage startup \
        --out matches.md [--personalize]

--personalize usa un LLM (stesso meccanismo di raiseready/delivery/analyze_deck.py, provider
gratuito via LLM_API_KEY) per scrivere una breve nota personalizzata SOLO sui match trovati
nel database — il prompt vieta esplicitamente di inventare programmi non presenti nei dati.
Senza --personalize, lo script produce comunque l'elenco completo dei match, utile e reale
anche senza nessuna chiave AI.
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("match_grants")

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "programs.json"


def load_programs():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def match(programs, country: str, keywords: list, stage: str):
    country = (country or "").upper()
    keywords = [k.strip().lower() for k in keywords if k.strip()]
    scored = []
    for p in programs:
        score = 0
        if country and country in p["countries"]:
            score += 3
        if not country:
            score += 1  # nessun filtro paese: mostra comunque, punteggio base
        target_l = p["target"].lower()
        if stage and stage.lower() in target_l:
            score += 2
        for kw in keywords:
            if kw in target_l or kw in p["notes"].lower() or kw in p["name"].lower():
                score += 2
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


def format_matches_md(matches: list) -> str:
    if not matches:
        return (
            "Nessun programma nel nostro database attuale corrisponde a questo profilo. "
            "Il database è verificato ma non esaustivo — non significa che non esistano "
            "opportunità, solo che non le abbiamo ancora catalogate."
        )
    lines = ["## Bandi e finanziamenti compatibili\n"]
    for p in matches:
        lines.append(f"### {p['name']} ({p['scope']})")
        lines.append(f"- **Target:** {p['target']}")
        lines.append(f"- **Tipo:** {p['funding_type']} — {p['amount']}")
        lines.append(f"- **Link ufficiale:** {p['official_url']}")
        lines.append(f"- **Note:** {p['notes']}")
        lines.append(f"- *Verificato il: {p['last_verified']}*")
        lines.append("")
    return "\n".join(lines)


def personalize(matches: list, business_desc: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        log.error("Manca il pacchetto openai per --personalize. pip install openai")
        sys.exit(1)

    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        log.error("LLM_API_KEY non impostata — vedi raiseready/delivery/README.md per Groq gratuito.")
        sys.exit(1)

    base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

    matches_json = json.dumps(matches, ensure_ascii=False, indent=2)
    system_prompt = (
        "Sei un consulente che spiega a un'azienda perché alcuni bandi/finanziamenti "
        "potrebbero fare al caso suo. USA SOLO i programmi nella lista JSON fornita — "
        "non inventare MAI un programma, un importo o una scadenza che non sia nei dati. "
        "Se un dato (es. scadenza esatta) non è nel JSON, scrivi esplicitamente "
        "'verificare la scadenza aggiornata sul sito ufficiale' invece di inventarla."
    )
    user_prompt = (
        f"Descrizione azienda: {business_desc}\n\n"
        f"Programmi trovati (JSON):\n{matches_json}\n\n"
        "Scrivi una breve nota (max 200 parole) su quali di questi programmi sembrano più "
        "rilevanti per questa azienda e perché, restando SOLO sui dati forniti."
    )

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", default="", help="Codice paese: IT, FR, ES")
    ap.add_argument("--keywords", default="", help="Parole chiave separate da virgola")
    ap.add_argument("--stage", default="", help="Es: startup, PMI")
    ap.add_argument("--business-desc", default="", help="Descrizione libera azienda (per --personalize)")
    ap.add_argument("--out", default="matches.md")
    ap.add_argument("--personalize", action="store_true")
    args = ap.parse_args()

    programs = load_programs()
    matches = match(programs, args.country, args.keywords.split(","), args.stage)
    log.info("Trovati %d match su %d programmi nel database.", len(matches), len(programs))

    output = format_matches_md(matches)

    if args.personalize and matches:
        note = personalize(matches, args.business_desc or "non specificata")
        output = (
            "> ⚠️ BOZZA — DA RIVEDERE PRIMA DI INVIARE AL CLIENTE\n\n"
            "## Nota personalizzata\n\n" + note + "\n\n---\n\n" + output
        )

    Path(args.out).write_text(output, encoding="utf-8")
    log.info("Scritto: %s", args.out)


if __name__ == "__main__":
    main()
