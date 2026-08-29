# AUDIT — Stato del workspace (Fase 1)

Data audit: 2026-08-21

## 🔴 Finding critico: credenziale esposta (RISOLTO PARZIALMENTE)

Una App Password Gmail reale (`emanuelconti.mim@gmail.com`) era hardcoded in chiaro in:
- `outreach_tattoo.py` (riga 32)
- `.github/workflows/outreach_all.yml` (righe 30, 35)

**Azione presa ora:** rimosso il fallback hardcoded da entrambi i file (i workflow ora
dipendono solo da `secrets.GMAIL_APP_PASSWORD`, che va impostato su GitHub, non nel codice).

**Azione richiesta al fondatore (non automatizzabile da qui):**
1. Revocare quella App Password su https://myaccount.google.com/apppasswords
2. Se serve invio email, generarne una nuova e salvarla SOLO come GitHub Secret
3. La password resta comunque leggibile nella cronologia git finché non viene riscritta
   la history (operazione distruttiva, richiede force-push su branch remoti — da fare
   solo con autorizzazione esplicita)

## Asset riutilizzabili trovati

### SocialPerks — sistema di outreach già costruito
- 5 script Python di invio email via Gmail SMTP + tracking SQLite
  (`outreach.py`, `outreach_multi.py`, `outreach_tattoo.py`, `outreach_paris_new.py`, `outreach_casablanca.py`)
- Sequenza a 3 step (email 1 → +3gg → +7gg), template in francese, oggetto tipo
  "Partenariat SocialPerks × {ristorante}"
- 4 GitHub Actions workflow, TUTTI con schedule già disabilitato (solo `workflow_dispatch`
  manuale) — nessuna email parte automaticamente allo stato attuale
- **~821 lead pre-raccolti e mai (o quasi mai) contattati**, in 21 file Excel:
  - Ristoranti: ~626 contatti in 12 città (Parigi, Lione, Marsiglia, Bordeaux, Lille,
    Nantes, Nizza, Strasburgo, Tolosa, Vienna, Casablanca + un secondo file "Paris_New")
  - Tattoo studio: ~195 contatti in 9 città francesi
- **Storico reale invii:** solo `outreach_tracking.db` è mai stato committato: 47 ristoranti
  Parigi originali, 15 email risultano inviate (sequenza incompleta). Le altre città/verticali
  (multi-city, tattoo, Casablanca, Paris_New) non hanno mai un DB committato → probabile
  indicazione che quelle campagne non sono mai state eseguite end-to-end, solo preparate.
  **Da verificare col fondatore**, non assumere.
- Le **21 LOI** menzionate dal fondatore risultano quindi ottenute con ogni probabilità da
  conversazioni dirette/manuali più che da questa automazione (il volume di invii tracciati
  è troppo basso per spiegarle da solo).

### Documenti/contesto esterni (da conversazione, non nel repo)
- `Tracker_Candidature_FT2027` (xlsx) e CV — pertinenti alla ricerca lavoro del fondatore,
  non a questo business. Ignorati per questo task.
- Nessun asset SOWLD o e-commerce presente in questo repository.

## Cosa NON esiste ancora in questo repo
- Nessuna landing page, nessun sito, nessun frontend
- Nessuna integrazione Stripe
- Nessun CRM strutturato oltre gli Excel/SQLite grezzi
- Nessun documento di strategia/offerta

## Decisione presa in Fase 1
Non ripartire da zero: gli asset SocialPerks (lead list pulite in 12 città, sequenza email,
relazioni già calde con 21 LOI, know-how di outreach B2B locale) sono il vantaggio
competitivo reale del fondatore e vanno riusati — ma **ripensando il modello da
marketplace/piattaforma a servizio B2B productized**, molto più veloce da vendere in 30
giorni (vedi `docs/OPPORTUNITY_SCORECARD.md` e `docs/STRATEGY.md`).
