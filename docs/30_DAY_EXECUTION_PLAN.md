# 30-Day Execution Plan — SocialPerks Pilot

## Economics del target (Fase richiesta esplicitamente)

Ipotesi di prezzo medio contratto pilota: **€850** (media tra €490 e €1.200).

| Configurazione | Contratti necessari | Prospect necessari (stima 3-5% conversione) | Realistico in 30gg founder-led? |
|---|---|---|---|
| 10 contratti da €100.000 | 10 | ~250-350 | **No** — nessun cliente in questo segmento paga €100k per un pilota locale di 4 settimane; incompatibile con l'offerta |
| 100 contratti da €10.000 | 100 | ~2.500-3.500 | **No** — richiederebbe upsell immediato a retainer enterprise mai validato, e capacità di delivery per 100 clienti in parallelo (impossibile per 1 persona) |
| 1.000 vendite da €1.000 | ~1.000 | ~25.000-35.000 prospect contattati e qualificati | **No** — il pool di lead pronti oggi è ~821 contatti + 21 LOI, due ordini di grandezza sotto quanto servirebbe |
| Combinazione realistica: pilota (~€850) + retainer (~€500/mese) | — | — | Vedi target base/stretch sotto |

**Conclusione onesta:** con il modello e gli asset attuali (821 lead pre-raccolti, 21 LOI,
capacità di delivery di una persona), **€1.000.000 in 30 giorni non è raggiungibile** — nessuna
configurazione realistica lo permette senza vendite enterprise a 6 cifre che questo prodotto
non giustifica. Il target resta la stella polare dichiarata dal fondatore, non l'obiettivo
operativo del mese 1.

| Target | Definizione | Contratti pilota stimati | Ricavi incassati stimati |
|---|---|---|---|
| **Base** | Vendita ai 21 LOI + prime liste calde | 3-5 | €1.500-€6.000 |
| **Stretch** | Base + 2° giro outreach su ~821 lead | 10-15 | €10.000-€20.000 |
| **Aspirazionale (dichiarato)** | €1.000.000 | ~1.000+ | Non raggiungibile in 30gg con questo modello — richiede mesi/anni e team, non un mese/una persona |

## Giorni 1-2 — Fondamenta (fatto in questo ciclo)
- Audit repo, scorecard, strategia, landing page, sales assets, scaffold Stripe test
- **Claude**: tutto quanto sopra ✅
- **Emanuel**: revocare la App Password Gmail esposta (vedi `docs/AUDIT.md`), leggere e
  correggere `docs/STRATEGY.md` dove non rispecchia la realtà del business
- KPI: 0 → docs/strategia pronti
- Continua se: la strategia ha senso per te. Correggi se: il pricing/target ti sembra sbagliato.

## Giorni 3-4 — Pre-vendita
- **Claude**: rifinire landing in base al tuo feedback, collegare Payment Link quando crei
  l'account Stripe test
- **Emanuel**: creare account Stripe (test mode), decidere dominio/hosting, rivedere i 21 LOI
  e segnare chi richiamare per primo
- Deliverable: landing pubblicata (checkpoint: deploy richiede tuo account Vercel/Netlify)
- KPI: landing live, 2 Payment Link test creati

## Giorni 5-7 — Primi contatti autorizzati
- **Claude**: preparare batch di messaggi personalizzati per i 21 LOI (bozze, non inviati)
- **Emanuel**: autorizzare batch specifico, effettuare le prime chiamate/messaggi ai LOI
  (founder-led — è la parte che nessuna automazione deve sostituire alla fiducia già costruita)
- KPI: 21 LOI ricontattati, N call fissate
- Criterio: se <20% dei LOI risponde in 7 giorni, rivedere messaggio/offerta prima di
  espandere alla lista fredda

## Settimana 2 — Discovery call, pilot, prime delivery
- **Claude**: preparare proposte personalizzate, aggiornare pipeline/dashboard KPI
- **Emanuel**: discovery call, chiusura primi pilot, avvio delivery (`sales/DELIVERY_SOP.md`)
- KPI: proposte inviate, pilot venduti, primo incasso reale
- Criterio: prima vendita entro giorno 14 → procedi. Zero vendite → rivedere prezzo/offerta/ICP

## Settimana 3 — Case study, referral, prezzo
- **Claude**: preparare case study dal primo pilota concluso (dati reali, non inventati)
- **Emanuel**: chiedere referral ai clienti soddisfatti (`sales/REFERRAL_SYSTEM.md`),
  valutare aumento prezzo per nuovi prospect
- KPI: referral generati, case study pubblicato (se dati lo permettono)

## Settimana 4 — Scala il canale che funziona
- **Claude**: analizzare quale canale (LOI diretti / lista fredda / referral) ha convertito
  meglio, preparare batch successivo solo su quello
- **Emanuel**: autorizzare espansione outreach su nuove città della lista (~626+195 contatti),
  decidere se attivare retainer sui primi clienti pilota
- KPI: MRR da retainer, rinnovi, nuovo batch autorizzato

## Nota
Ogni "Emanuel" qui sopra è founder-led per scelta, non per limite tecnico — la vendita dei
primi contratti B2B locali si chiude con relazione umana diretta, non con automazione.
