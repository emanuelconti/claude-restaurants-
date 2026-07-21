# Deploy della piattaforma web (webapp/)

Questo è il percorso per avere Sowld come **prodotto online vero**: un
link che dai in pasto al sito Framer, dove chi arriva si registra, paga un
abbonamento (Stripe) e usa la ricerca da browser — senza terminale, senza
script da lanciare.

Diverso da `avvia.sh`/CLI: quello resta lo script che *tu* lanci per te
stesso. Questo è il servizio che i *tuoi clienti* useranno.

## Costi reali (nessuno è "gratis" per sempre, ma si parte vicino a zero)

| Cosa | Costo per iniziare | Quando si paga davvero |
| :--- | :--- | :--- |
| **Hosting (Render)** | **€0** — piano free per un web service | Solo se serve più potenza/uptime costante (piano a pagamento da ~7$/mese) |
| **Stripe** | **€0** per aprire l'account | Solo una % + fissa (~1.5-2.9% + €0.25) su ogni pagamento *reale* che incassi — se non hai clienti paganti, non paghi nulla |
| **Anthropic API** | Pochi centesimi per ricerca | A consumo, cresce con l'uso reale |
| **Dominio** (sowld.com o simile) | ~10-15€/anno | Se non l'hai già comprato (vedi SOW, Phase 0) |

Quindi: puoi mettere online una versione funzionante e testabile **senza
spendere nulla di fisso**, e i costi veri arrivano solo quando qualcuno
inizia davvero a usarla e a pagare.

## Passo 1 — Crea l'account Render e collega il repo

1. Vai su **render.com** → crea un account (puoi usare GitHub per accedere)
2. "New" → "Blueprint" → collega il repository `emanuelconti/claude-restaurants-`
3. Render trova automaticamente `sowld/render.yaml` e propone il servizio
   `sowld` — importante: imposta la **root directory** su `sowld/` quando
   te lo chiede (il progetto vive in una sottocartella del repo)
4. Prima di confermare, ti chiederà di compilare le variabili segnate
   `sync: false` nel blueprint — per ora lascia vuoto `STRIPE_*`, li
   aggiungiamo dopo. Metti solo:
   ```
   ANTHROPIC_API_KEY = sk-ant-api03-... (quella che hai già creato)
   ```
5. Conferma. Il primo deploy impiega qualche minuto — a fine build avrai
   un URL tipo `https://sowld.onrender.com`

A questo punto il sito è online: landing page, registrazione, login
funzionano già. Manca solo Stripe per sbloccare la ricerca.

## Passo 2 — Crea l'account Stripe (modalità test, zero rischi)

1. Vai su **dashboard.stripe.com/register** → crea un account
2. Resta in **modalità Test** (interruttore in alto) — puoi costruire e
   provare tutto il flusso di pagamento senza che nessuno spenda un euro
   vero, prima di attivare i pagamenti reali
3. Vai su **Product catalog** → "Add product" → dai un nome (es. "Sowld
   Pro"), imposta un prezzo ricorrente mensile (es. €9/mese) → salva
4. Apri il prodotto creato e copia il **Price ID** (inizia con `price_...`)
5. Vai su **Developers → API keys** → copia la **Secret key** (in test,
   inizia con `sk_test_...`)

## Passo 3 — Il webhook (Stripe deve poter avvisare il tuo server)

1. Su Stripe: **Developers → Webhooks → Add endpoint**
2. URL endpoint: `https://sowld.onrender.com/webhooks/stripe` (usa il tuo
   URL Render reale)
3. Eventi da ascoltare: `checkout.session.completed`,
   `customer.subscription.updated`, `customer.subscription.deleted`
4. Salva, poi copia il **Signing secret** (inizia con `whsec_...`)

## Passo 4 — Torna su Render e completa le variabili

Nelle Environment variables del servizio `sowld` su Render, aggiungi:
```
STRIPE_SECRET_KEY = sk_test_...
STRIPE_PRICE_ID = price_...
STRIPE_WEBHOOK_SECRET = whsec_...
```
Salva — Render fa un nuovo deploy automatico in ~1 minuto.

## Passo 5 — Prova il flusso intero

1. Apri `https://sowld.onrender.com`
2. Registrati con una tua email
3. Ti porta al checkout Stripe — in modalità test usa la carta finta
   `4242 4242 4242 4242`, qualsiasi data futura, qualsiasi CVC
4. Dopo il pagamento (finto) torni sulla dashboard con la ricerca sbloccata
5. Prova una ricerca vera

Se funziona tutto, **hai un prodotto online funzionante, in modalità
test**. Solo quando vuoi davvero incassare pagamenti reali: torna su
Stripe, disattiva "Test mode", ripeti i passi 2-4 con le chiavi *live*
(`sk_live_...`, nuovo Price ID, nuovo webhook) al posto di quelle test.

## Passo 6 — Database persistente (fallo prima di avere clienti veri)

Di default il sito usa SQLite, un semplice file — su Render questo file
**si azzera a ogni deploy**, cancellando tutti gli account registrati.
Va benissimo mentre stai ancora testando (è normale dover rifare
signup/pagamento ogni volta che aggiorno il codice), ma prima di lanciare
davvero il prodotto serve un database che non si cancella mai.

1. Su Render: **New +** → **Postgres**
2. Dai un nome (es. "sowld-db"), scegli la regione più vicina a quella del
   servizio web, piano **Free** (gratuito 30 giorni, poi ~7$/mese — vedi
   sotto)
3. Crea. Dopo qualche secondo, apri il database e cerca il campo
   **"Internal Database URL"** — copialo (inizia con `postgres://`)
4. Torna sul servizio `sowld` → Environment Variables → modifica
   `DATABASE_URL`, sostituendo il valore con quello appena copiato
5. Salva — Render fa un nuovo deploy. Da questo momento gli account
   restano salvati per sempre, anche quando aggiorno il codice

Nota sul piano gratuito di Postgres su Render: è gratis per un periodo
limitato (in genere 30 giorni), poi Render lo sospende se non passi a un
piano a pagamento (da ~7$/mese) — quando sarai pronto ad avere clienti
veri che pagano, questo costo fisso mensile va messo in conto insieme
agli altri.

## Il link per Framer

Una volta online, l'URL da inserire nel sito Framer (Part A) come pulsante
"Accedi alla piattaforma" / "Request beta access" è semplicemente:
```
https://sowld.onrender.com
```
(o il tuo dominio finale, se colleghi `sowld.com` a Render in un secondo
momento — Render supporta domini personalizzati gratuitamente).

## Limiti onesti di questa versione

- **Ricerca sincrona**: la pagina resta in caricamento per tutta la durata
  della ricerca (10-30 secondi). Va bene per pochi utenti; con più
  traffico servirebbe eseguirla in background.
- **Wallapop, Leboncoin, Subito.it, Vinted e ora anche Kleinanzeigen sono
  bloccati** da protezioni anti-bot (verificato dal vivo il 2026-07-21) —
  **eBay è l'unica fonte affidabile al 100%** oggi, essendo l'unica con
  un'API ufficiale. Configura `EBAY_CLIENT_ID`/`EBAY_CLIENT_SECRET` prima
  di considerare il prodotto pronto per clienti veri. Kleinanzeigen non è
  più solo "incostante": test diretti del 2026-07-21 mostrano che il
  blocco (Akamai) è sistematico per qualsiasi client Python — non basta
  aggiornare i selettori HTML (già fatto), i dati veri restano dietro un
  fingerprint del client che nessuna intestazione realistica riesce a
  superare. Vedi README.md, sezione "Multiple marketplaces", per i
  dettagli.
- **Limite di ricerche mensili per utente**: 50 di default
  (`MONTHLY_SEARCH_LIMIT` nelle Environment Variables), per tenere sotto
  controllo il costo massimo dell'API Anthropic per cliente. Alzalo se il
  prezzo dell'abbonamento lo giustifica.
