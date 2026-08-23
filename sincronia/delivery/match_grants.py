#!/usr/bin/env python3
"""
Sincronia — motore di matching bandi/finanziamenti.

Prende un profilo azienda (paese, settore/parole chiave, fase) e lo confronta con il
database REALE e verificato in sincronia/data/programs.json (nessun bando è inventato:
ogni riga ha un link ufficiale e una data di ultima verifica).

Uso:
    python3 match_grants.py --country IT --keywords "AI,digitalizzazione" --stage startup \
        --lang it --out matches.md [--personalize]

--lang sceglie la lingua di TUTTO il report consegnato al cliente (etichette del template E
nota AI generata), coerente con la lingua del sito: it, es, pt, fr, de. Default: it.

--personalize usa un LLM (stesso meccanismo di raiseready/delivery/analyze_deck.py, provider
gratuito via LLM_API_KEY) per scrivere una breve nota personalizzata SOLO sui match trovati
nel database — il prompt vieta esplicitamente di inventare programmi non presenti nei dati,
nella lingua scelta. Senza --personalize, lo script produce comunque l'elenco completo dei
match, utile e reale anche senza nessuna chiave AI.
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

LABELS = {
    "it": {
        "heading": "Bandi e finanziamenti compatibili",
        "target": "Target", "type": "Tipo", "link": "Link ufficiale", "notes": "Note",
        "verified": "Verificato il", "no_match": (
            "Nessun programma nel nostro database attuale corrisponde a questo profilo. "
            "Il database è verificato ma non esaustivo: non significa che non esistano "
            "opportunità, solo che non le abbiamo ancora catalogate."
        ),
        "draft_banner": "⚠️ BOZZA — DA RIVEDERE PRIMA DI INVIARE AL CLIENTE",
        "note_heading": "Nota personalizzata",
    },
    "es": {
        "heading": "Ayudas y financiaciones compatibles",
        "target": "Destinatario", "type": "Tipo", "link": "Enlace oficial", "notes": "Notas",
        "verified": "Verificado el", "no_match": (
            "Ningun programa de nuestra base de datos actual coincide con este perfil. "
            "La base de datos esta verificada pero no es exhaustiva: no significa que no "
            "existan oportunidades, solo que aun no las hemos catalogado."
        ),
        "draft_banner": "⚠️ BORRADOR, REVISAR ANTES DE ENVIAR AL CLIENTE",
        "note_heading": "Nota personalizada",
    },
    "pt": {
        "heading": "Apoios e financiamentos compativeis",
        "target": "Destinatario", "type": "Tipo", "link": "Link oficial", "notes": "Notas",
        "verified": "Verificado em", "no_match": (
            "Nenhum programa na nossa base de dados atual corresponde a este perfil. "
            "A base de dados e verificada mas nao e exaustiva: nao significa que nao "
            "existam oportunidades, apenas que ainda nao as catalogamos."
        ),
        "draft_banner": "⚠️ RASCUNHO, REVER ANTES DE ENVIAR AO CLIENTE",
        "note_heading": "Nota personalizada",
    },
    "fr": {
        "heading": "Aides et financements compatibles",
        "target": "Cible", "type": "Type", "link": "Lien officiel", "notes": "Remarques",
        "verified": "Verifie le", "no_match": (
            "Aucun programme de notre base de donnees actuelle ne correspond a ce profil. "
            "La base de donnees est verifiee mais pas exhaustive: cela ne veut pas dire "
            "qu'il n'existe pas d'opportunites, seulement que nous ne les avons pas encore repertoriees."
        ),
        "draft_banner": "⚠️ BROUILLON, A RELIRE AVANT D'ENVOYER AU CLIENT",
        "note_heading": "Note personnalisee",
    },
    "de": {
        "heading": "Passende Foerderungen und Finanzierungen",
        "target": "Zielgruppe", "type": "Art", "link": "Offizieller Link", "notes": "Hinweise",
        "verified": "Geprueft am", "no_match": (
            "Kein Programm in unserer aktuellen Datenbank passt zu diesem Profil. Die "
            "Datenbank ist geprueft, aber nicht vollstaendig: das heisst nicht, dass es "
            "keine Moeglichkeiten gibt, nur dass wir sie noch nicht erfasst haben."
        ),
        "draft_banner": "⚠️ ENTWURF, VOR DEM VERSAND AN DEN KUNDEN PRUEFEN",
        "note_heading": "Persoenliche Anmerkung",
    },
}

SYSTEM_PROMPT_BY_LANG = {
    "it": (
        "Sei un consulente che spiega a un'azienda perché alcuni bandi/finanziamenti "
        "potrebbero fare al caso suo. Scrivi SEMPRE in italiano. USA SOLO i programmi nella "
        "lista JSON fornita: non inventare MAI un programma, un importo o una scadenza che "
        "non sia nei dati. Se un dato (es. scadenza esatta) non è nel JSON, scrivi "
        "esplicitamente 'verificare la scadenza aggiornata sul sito ufficiale' invece di inventarla."
    ),
    "es": (
        "Eres un consultor que explica a una empresa por que algunas ayudas o financiaciones "
        "podrian interesarle. Escribe SIEMPRE en español. USA SOLO los programas de la lista "
        "JSON proporcionada: nunca inventes un programa, importe o plazo que no este en los "
        "datos. Si un dato (por ejemplo un plazo exacto) no esta en el JSON, escribe "
        "explicitamente 'verificar el plazo actualizado en la fuente oficial' en vez de inventarlo."
    ),
    "pt": (
        "Es um consultor que explica a uma empresa porque alguns apoios ou financiamentos "
        "podem interessar. Escreve SEMPRE em portugues. USA APENAS os programas da lista "
        "JSON fornecida: nunca inventes um programa, valor ou prazo que nao esteja nos "
        "dados. Se um dado (por exemplo um prazo exato) nao estiver no JSON, escreve "
        "explicitamente 'verificar o prazo atualizado na fonte oficial' em vez de o inventar."
    ),
    "fr": (
        "Vous etes un consultant qui explique a une entreprise pourquoi certaines aides ou "
        "certains financements pourraient l'interesser. Ecrivez TOUJOURS en francais. "
        "UTILISEZ UNIQUEMENT les programmes de la liste JSON fournie: n'inventez JAMAIS un "
        "programme, un montant ou une echeance absent des donnees. Si une information (par "
        "exemple une echeance exacte) n'est pas dans le JSON, ecrivez explicitement "
        "'verifier l'echeance actualisee sur la source officielle' plutot que de l'inventer."
    ),
    "de": (
        "Sie sind ein Berater, der einem Unternehmen erklaert, warum bestimmte Foerderungen "
        "oder Finanzierungen relevant sein koennten. Schreiben Sie IMMER auf Deutsch. "
        "VERWENDEN SIE NUR die Programme aus der bereitgestellten JSON-Liste: erfinden Sie "
        "NIEMALS ein Programm, einen Betrag oder eine Frist, die nicht in den Daten stehen. "
        "Wenn eine Angabe (z. B. eine genaue Frist) nicht im JSON steht, schreiben Sie "
        "ausdruecklich 'aktuelle Frist auf der offiziellen Quelle pruefen', statt sie zu erfinden."
    ),
}


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


def format_matches_md(matches: list, lang: str) -> str:
    lbl = LABELS.get(lang, LABELS["it"])
    if not matches:
        return lbl["no_match"]
    lines = [f"## {lbl['heading']}\n"]
    for p in matches:
        lines.append(f"### {p['name']} ({p['scope']})")
        lines.append(f"- **{lbl['target']}:** {p['target']}")
        lines.append(f"- **{lbl['type']}:** {p['funding_type']}, {p['amount']}")
        lines.append(f"- **{lbl['link']}:** {p['official_url']}")
        lines.append(f"- **{lbl['notes']}:** {p['notes']}")
        lines.append(f"- *{lbl['verified']}: {p['last_verified']}*")
        lines.append("")
    return "\n".join(lines)


def personalize(matches: list, business_desc: str, lang: str) -> str:
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
    system_prompt = SYSTEM_PROMPT_BY_LANG.get(lang, SYSTEM_PROMPT_BY_LANG["it"])
    user_prompt = (
        f"Descrizione azienda / company description: {business_desc}\n\n"
        f"Programmi trovati / matched programs (JSON):\n{matches_json}\n\n"
        "Scrivi una breve nota (max 200 parole), nella lingua indicata dalle istruzioni di "
        "sistema, su quali di questi programmi sembrano più rilevanti per questa azienda e "
        "perché, restando SOLO sui dati forniti."
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
    ap.add_argument("--lang", default="it", choices=list(LABELS.keys()),
                     help="Lingua dell'intero report consegnato: it, es, pt, fr, de")
    ap.add_argument("--out", default="matches.md")
    ap.add_argument("--personalize", action="store_true")
    args = ap.parse_args()

    lbl = LABELS.get(args.lang, LABELS["it"])

    programs = load_programs()
    matches = match(programs, args.country, args.keywords.split(","), args.stage)
    log.info("Trovati %d match su %d programmi nel database (lingua report: %s).",
              len(matches), len(programs), args.lang)

    output = format_matches_md(matches, args.lang)

    if args.personalize and matches:
        note = personalize(matches, args.business_desc or "non specificata", args.lang)
        output = (
            f"> {lbl['draft_banner']}\n\n"
            f"## {lbl['note_heading']}\n\n" + note + "\n\n---\n\n" + output
        )

    Path(args.out).write_text(output, encoding="utf-8")
    log.info("Scritto: %s", args.out)


if __name__ == "__main__":
    main()
