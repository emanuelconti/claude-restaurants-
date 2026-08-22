#!/usr/bin/env python3
"""
RaiseReady — pipeline di analisi deck, end-to-end.

Legge un pitch deck (PDF), estrae il testo, lo manda a un modello LLM seguendo la
struttura fissa in REPORT_TEMPLATE.md, scrive un report Markdown.

Funziona con QUALSIASI provider compatibile con l'API OpenAI — incluso Groq, che ha un
tier gratuito reale (nessuna carta di credito richiesta, solo un signup gratuito su
console.groq.com per ottenere una chiave). Basta impostare le env var:

    LLM_API_KEY=...           (obbligatoria per l'analisi reale)
    LLM_BASE_URL=https://api.groq.com/openai/v1   (default: Groq free tier)
    LLM_MODEL=llama-3.3-70b-versatile              (default: modello gratuito Groq)

Nessuna chiave è configurata in questo repo. Senza LLM_API_KEY lo script funziona
comunque in modalità --dry-run, che produce un report segnaposto chiaramente etichettato
come tale — utile per testare tutta la pipeline (upload, estrazione, formattazione,
scrittura file) senza credenziali, ma MAI da mandare a un cliente reale.

Uso:
    python3 analyze_deck.py --deck path/to/deck.pdf [--model-file path/to/model.xlsx] \
        --out report.md [--dry-run]

Dipendenze (vedi requirements.txt): pypdf (estrazione testo, libero/gratuito),
openai (SDK, compatibile con qualunque endpoint OpenAI-compatible incluso il free tier Groq).
"""
import argparse
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("analyze_deck")

DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"  # provider free-tier di default
DEFAULT_MODEL = "openai/gpt-oss-120b"                 # modello gratuito su Groq (verificato
                                                       # live via /v1/models il 2026-08-22 —
                                                       # Groq cambia il catalogo modelli nel
                                                       # tempo, se dà 404 rilanciare con
                                                       # LLM_MODEL=<altro id da /v1/models>)

REPORT_TEMPLATE_PATH = Path(__file__).resolve().parent / "REPORT_TEMPLATE.md"

SYSTEM_PROMPT = """Sei un analista che rivede pitch deck di startup per individuare buchi \
strutturali e narrativi PRIMA che li veda un investitore. Segui ESATTAMENTE la struttura \
del template fornito. Non dare consigli di investimento, non valutare se conviene investire, \
non promettere risultati di raccolta fondi — solo feedback strutturale/editoriale sul \
documento. Se un'informazione richiesta dal template non è presente nel deck, scrivi \
esplicitamente "non presente nel documento fornito" invece di inventarla."""


def extract_pdf_text(path: Path) -> str:
    try:
        import pypdf
    except ImportError:
        log.error("Manca pypdf. Installa con: pip install -r requirements.txt")
        sys.exit(1)

    reader = pypdf.PdfReader(str(path))
    texts = []
    for i, page in enumerate(reader.pages):
        try:
            texts.append(page.extract_text() or "")
        except Exception as e:
            log.warning("Impossibile estrarre testo dalla pagina %d: %s", i + 1, e)
    text = "\n".join(texts).strip()
    if not text:
        log.warning(
            "Nessun testo estratto dal PDF — potrebbe essere un deck fatto di sole immagini "
            "(serve OCR, non incluso in questa pipeline base)."
        )
    return text


def build_user_prompt(deck_text: str, model_text: str, template: str) -> str:
    parts = [
        "TEMPLATE DA SEGUIRE:\n" + template,
        "\nTESTO DEL DECK:\n" + (deck_text or "[nessun testo estratto]"),
    ]
    if model_text:
        parts.append("\nTESTO DEL MODELLO FINANZIARIO:\n" + model_text)
    else:
        parts.append("\n[Nessun modello finanziario fornito — salta la sezione 4 del template]")
    return "\n".join(parts)


def call_llm(user_prompt: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        log.error("Manca il pacchetto openai. Installa con: pip install -r requirements.txt")
        sys.exit(1)

    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        log.error(
            "LLM_API_KEY non impostata. Nessuna analisi reale è possibile senza una chiave.\n"
            "  Opzione gratuita consigliata: crea un account su console.groq.com (nessuna "
            "carta richiesta), genera una API key, ed esportala come:\n"
            "  export LLM_API_KEY='...'\n"
            "Oppure esegui con --dry-run per testare il resto della pipeline senza chiave."
        )
        sys.exit(1)

    base_url = os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL)
    model = os.getenv("LLM_MODEL", DEFAULT_MODEL)

    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
    except Exception as e:
        log.error(
            "Chiamata al modello fallita: %s\n"
            "  Se l'errore parla di modello non trovato, i provider free-tier cambiano "
            "spesso il catalogo — controlla i modelli disponibili ORA con:\n"
            "  curl https://api.groq.com/openai/v1/models -H \"Authorization: Bearer $LLM_API_KEY\"\n"
            "  e imposta LLM_MODEL=<id valido> prima di rilanciare.",
            e,
        )
        sys.exit(1)

    return resp.choices[0].message.content


def dry_run_report(business_name: str) -> str:
    return f"""# ⚠️ REPORT SEGNAPOSTO (--dry-run) — NON INVIARE A UN CLIENTE REALE

Questo è un output finto generato senza chiamare nessun modello, per verificare che il
resto della pipeline (estrazione PDF, formattazione, scrittura file) funzioni. Non
contiene un'analisi vera del deck di **{business_name}**.

Per un report reale: imposta `LLM_API_KEY` (vedi istruzioni in `raiseready/delivery/README.md`)
ed esegui di nuovo senza `--dry-run`.
"""


def main():
    ap = argparse.ArgumentParser(description="RaiseReady — analizza un pitch deck")
    ap.add_argument("--deck", required=True, help="Path al PDF del pitch deck")
    ap.add_argument("--model-file", help="Path opzionale a un modello finanziario (testo/csv)")
    ap.add_argument("--out", default="report.md", help="Path del report in output")
    ap.add_argument("--business-name", default="", help="Nome della startup (per l'intestazione)")
    ap.add_argument("--dry-run", action="store_true", help="Non chiama nessun LLM, output finto")
    args = ap.parse_args()

    deck_path = Path(args.deck)
    if not deck_path.exists():
        log.error("File non trovato: %s", deck_path)
        sys.exit(1)

    business_name = args.business_name or deck_path.stem

    log.info("Estrazione testo da %s...", deck_path.name)
    deck_text = extract_pdf_text(deck_path)
    log.info("Estratti %d caratteri.", len(deck_text))

    model_text = ""
    if args.model_file:
        model_path = Path(args.model_file)
        if model_path.exists():
            model_text = model_path.read_text(encoding="utf-8", errors="ignore")
        else:
            log.warning("File modello non trovato: %s — proseguo senza.", model_path)

    if args.dry_run:
        report = dry_run_report(business_name)
    else:
        template = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
        prompt = build_user_prompt(deck_text, model_text, template)
        log.info("Chiamata al modello (%s)...", os.getenv("LLM_MODEL", DEFAULT_MODEL))
        report = call_llm(prompt)

    out_path = Path(args.out)
    out_path.write_text(report, encoding="utf-8")
    log.info("Report scritto in %s", out_path)


if __name__ == "__main__":
    main()
