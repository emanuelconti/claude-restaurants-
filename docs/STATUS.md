# STATUS — RaiseReady (pivot da SocialPerks Pilot)

Ultimo aggiornamento: Ciclo 3 (pivot business — vedi `docs/STRATEGY_V2.md`)

## Ciclo 3 — pivot
Su richiesta esplicita del fondatore ("non c'entra né con SocialPerks né con Sowld né con
quell'ecommerce"), il business primario cambia da SocialPerks Pilot a **RaiseReady**: deck
review self-serve per founder in fundraising, zero coinvolgimento del fondatore in
vendita/delivery (era il vincolo esplicito). Dettagli in `docs/STRATEGY_V2.md`.

Costruito in questo ciclo, tutto verificato (HTML valido, screenshot desktop/mobile):
- `raiseready/landing/index.html` — landing self-serve, dark theme, pricing €149/€349,
  disclaimer "non è consulenza di investimento" ben visibile (necessario: territorio
  finanziario regolamentato se non dichiarato chiaramente)
- `raiseready/marketing/AD_COPY.md` — Google/Meta/LinkedIn ads pronti da incollare
  (nessun account ads collegato, nessuna spesa avviata)
- `raiseready/marketing/COMMUNITY_POSTS.md` — post pronti per Indie Hackers/Product
  Hunt/r/startups, canale compatibile con "zero outreach 1:1"
- `raiseready/marketing/DOMAIN_SHORTLIST.md` — 5 nomi dominio verificabili, nessuna
  registrazione fatta (serve carta di pagamento reale)
- `raiseready/marketing/promo-animation.html` + `VIDEO_SCRIPT.md` — promo animata
  autoportante (nessun ffmpeg/TTS disponibile in questo ambiente per generare un .mp4
  direttamente; la pagina è registrabile con qualsiasi screen recorder in 1 minuto)
- `raiseready/delivery/README.md` + `REPORT_TEMPLATE.md` — pagamento (riusa scaffold
  Stripe già in `payments/`) e struttura fissa del report da consegnare

**Vincolo reale non aggirabile, dichiarato una volta sola:** dominio, ads a pagamento e
Stripe live richiedono un metodo di pagamento reale che non ho — non li ho costruiti fingendo
di poterli attivare. Tutto il resto è pronto.

Gli asset SocialPerks (Ciclo 1-2) restano nel repo, non cancellati, semplicemente non più il
focus primario — vedi sotto per lo storico.

## Ciclo 2 — novità (storico SocialPerks, non più il business primario)
- I 21 LOI menzionati non esistono in nessun file del repo (verificato: script, Excel, DB) —
  non fabbricati, semplicemente non lavorabili finché non arriva la fonte reale
- Costruita invece la pipeline su dati **reali già raccolti**: `automation/lead_scoring.py`
  consolida i 21 file Excel, dedup per email, esclude i "❌ No", assegna un punteggio →
  **681 lead reali qualificati e prioritizzati** in `automation/output/prioritized_leads.csv`
- `automation/generate_drafts.py` genera bozze email personalizzate per i primi 30 (per
  punteggio) usando SOLO dati strutturati reali (quartiere, stile) per la frase in francese —
  prima versione mescolava note italiane in frasi francesi producendo testo ibrido di bassa
  qualità, corretto prima di considerarlo completo → `automation/output/draft_batch_1.md`
- **Nessuna email è stata inviata.** Le bozze sono pronte per essere riviste e inviate quando
  deciso, manualmente o tramite un batch autorizzato

## Completato
- Audit completo del repository (`docs/AUDIT.md`)
- Scorecard 10 opportunità + decisione (`docs/OPPORTUNITY_SCORECARD.md`)
- Strategia, prezzo, unit economics, target (`docs/STRATEGY.md`)
- Landing page mobile-first completa: hero, come funziona, tarifs, FAQ, form di
  qualificazione, privacy/termini in bozza (`landing/`)
- 10 documenti sales/ completi: ICP, offerta, script vendita, discovery call, obiezioni,
  proposta, onboarding, delivery SOP, retention/upsell, referral
- Template messaggi: 3 cold email, 3 follow-up, LinkedIn, Instagram, demo script, proposta
  pilot/annuale, checklist qualificazione (`sales/MESSAGE_TEMPLATES.md`)
- Scaffold Stripe modalità test (Payment Links consigliati + funzioni serverless opzionali),
  nessuna chiave configurata, nessun account collegato (`payments/`)
- Piano 30 giorni con economics realistiche del target €1M (`docs/30_DAY_EXECUTION_PLAN.md`)

## ✅ Risolto: credenziale esposta
App Password Gmail (nome "claude" nel tuo account, creata 26 giu — combacia con le date dei
commit dell'automazione outreach) era hardcoded in `outreach_tattoo.py` e
`.github/workflows/outreach_all.yml` — rimossa dal codice **e revocata su Google dal
fondatore**. Resta comunque leggibile nella cronologia git (nessuna riscrittura history
fatta finora, richiederebbe force-push esplicitamente autorizzato). Nessuna nuova credenziale
è stata generata: l'invio email resta bloccato finché non ne crei una nuova come GitHub
Secret, quando deciderai di riattivare l'outreach.

## Cosa funziona
- La landing page apre e naviga correttamente (verificata via lettura/struttura HTML; da
  aprire anche tu in un browser per conferma visiva)
- Form di contatto: fallback via `mailto:` funzionante senza bisogno di alcun account esterno

## Cosa NON funziona / non è ancora collegato
- Nessun hosting reale (landing non è online — serve tuo account Vercel/Netlify/Cloudflare)
- Nessun form backend reale oltre il fallback mailto
- Nessuna chiave Stripe configurata (nessun pagamento è possibile finché non colleghi l'account)
- Nessuna email è mai stata inviata da questo ciclo di lavoro — zero outreach reale eseguito

## KPI disponibili (tutti a zero perché non è ancora partita nessuna attività esterna reale)
| KPI | Valore |
|---|---|
| Prospect qualificati (lista pronta, reale) | 681 (dedup + scoring, `automation/output/prioritized_leads.csv`) |
| Contatti preparati (bozze pronte) | 30 bozze reali personalizzate (`automation/output/draft_batch_1.md`) |
| Contatti autorizzati e inviati | 0 |
| Pilot venduti | 0 |
| Ricavi incassati | €0 |
| Ricavi contrattualizzati | €0 |
| Costo strumenti finora | €0 |

## Decisioni prese
- Business primario: SocialPerks Pilot (servizio B2B productized), non piattaforma/marketplace
- Nessun invio email/messaggio senza autorizzazione esplicita batch-per-batch
- Nessuna promessa di risultato garantito ai clienti finché non concordata col fondatore

## Esperimenti attivi
Nessuno ancora — 30 bozze reali pronte in `automation/output/draft_batch_1.md`, invio non
ancora avvenuto (nessuna credenziale email configurata comunque, vedi sopra).

## Rischi
- Credenziale Gmail vecchia resta leggibile in git history (revocata, quindi innocua, ma
  la history non è stata riscritta — valutare in futuro se serve ripulirla del tutto)
- Lista lead mai verificata a campione (email/attività ancora valide?)
- Capacità di delivery reale del fondatore (4-6h/settimana/cliente) non ancora testata

## Nota su "niente autorizzazioni"
Il fondatore ha chiesto di procedere senza fermarsi a chiedere. Rispettato per tutto ciò che è
costruzione/preparazione (script, bozze, docs). Restano comunque bloccati fino a un input reale
del fondatore, non per formalità ma perché tecnicamente non fattibili altrimenti:
credenziali email da (ri)creare per inviare, account esterni da collegare (hosting/Stripe),
invio reale a terzi. Non sono "richieste di permesso" nel senso classico — sono dipendenze
tecniche vere e proprie (senza credenziale non parte nessuna email, punto).

## Prossime tre priorità
1. Generare batch 2 (lead 31-60) con `automation/generate_drafts.py` quando serve
2. Deploy della landing page appena disponibile un account Vercel/Netlify/Cloudflare
3. Creare una nuova credenziale email (GitHub Secret, mai nel codice) quando si vuole
   davvero far partire il primo invio reale
