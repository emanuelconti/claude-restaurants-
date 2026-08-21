# STATUS — SocialPerks Pilot

Ultimo aggiornamento: Ciclo 1 (audit + fondamenta)

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

## 🔴 Trovato e parzialmente risolto: credenziale esposta
App Password Gmail reale era hardcoded in `outreach_tattoo.py` e
`.github/workflows/outreach_all.yml` — rimossa dal codice ora. **Resta nella cronologia git**
e **richiede revoca manuale da parte tua** su Google. Vedi `docs/AUDIT.md`.

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
| Prospect qualificati (lista pronta) | 821 (626 ristoranti + 195 tattoo studio) + 21 LOI |
| Contatti preparati (bozze pronte) | template pronti, batch non ancora generato per persona |
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
Nessuno ancora — in attesa di autorizzazione per il primo batch (i 21 LOI).

## Rischi
- Credenziale Gmail esposta in git history (vedi sopra) — priorità massima
- Lista lead mai verificata a campione (email/attività ancora valide?)
- Capacità di delivery reale del fondatore (4-6h/settimana/cliente) non ancora testata

## Approvazioni richieste (vedi messaggio principale per il dettaglio unico e minimo)
1. Revocare la App Password Gmail esposta
2. Autorizzare il primo batch di contatto verso i 21 LOI (bozze pronte in `sales/`)
3. Decidere se/quando collegare account Vercel/Netlify (deploy) e Stripe (pagamenti test)

## Prossime tre priorità
1. Ricevere conferma che la credenziale è stata revocata
2. Generare le 21 bozze personalizzate per i LOI (pronte per tua revisione, non invio)
3. Deploy della landing page (appena hai un account collegato) o feedback per rifinirla prima
