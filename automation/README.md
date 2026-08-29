# Automazione lead — Fase 6/7

Due script Python, senza dipendenze a pagamento, che processano SOLO i dati che hai già
raccolto tu (i file `SocialPerks_*.xlsx`). Nessuno dei due invia nulla o tocca credenziali.

## 1. `lead_scoring.py` — consolidamento e scoring
```
python3 automation/lead_scoring.py
```
- Legge tutti i 21 file `SocialPerks_*.xlsx` in root
- Deduplica per email
- Esclude i lead marcati "❌ No" nella colonna "Adatto SocialPerks"
- Assegna un punteggio (fit + presenza Instagram/telefono + ricchezza della nota)
- Scrive `automation/output/prioritized_leads.csv` ordinato per priorità

Risultato ultima esecuzione: **683 righe con email lette → 681 lead qualificati unici**
(2 esclusi perché marcati non adatti, 0 doppioni per email trovati).

## 2. `generate_drafts.py` — bozze email personalizzate
```
python3 automation/generate_drafts.py --limit 30
```
- Prende i primi N lead da `prioritized_leads.csv`
- Genera un'osservazione in francese SOLO da campi strutturati reali (quartiere, stile
  cucina/tatuaggio) — non traduce automaticamente le note italiane dentro la frase francese,
  per evitare frasi ibride di bassa qualità
- Include comunque la nota italiana originale come riferimento interno, separata dal corpo
  dell'email, per un'ulteriore personalizzazione manuale facoltativa
- Scrive `automation/output/draft_batch_1.md` — **solo bozze, zero invii**

## Prossimi batch
Rilancia `generate_drafts.py` con `--limit` più alto (o modifica per uno slice successivo)
per generare altri batch quando i primi saranno stati rivisti/inviati.
