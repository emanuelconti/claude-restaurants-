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

## Il link per Framer

Una volta online, l'URL da inserire nel sito Framer (Part A) come pulsante
"Accedi alla piattaforma" / "Request beta access" è semplicemente:
```
https://sowld.onrender.com
```
(o il tuo dominio finale, se colleghi `sowld.com` a Render in un secondo
momento — Render supporta domini personalizzati gratuitamente).

## Limiti onesti di questa versione

- **Il database è SQLite su disco effimero**: sul piano free di Render il
  filesystem si resetta a ogni riavvio/deploy — utenti e abbonamenti
  registrati vengono persi. Va benissimo per testare il flusso adesso;
  prima di avere clienti veri, serve un database persistente (Render
  offre Postgres gratuito per 90 giorni, poi a pagamento) — è un cambio
  di poche righe in `webapp/db.py` (`DATABASE_URL`).
- **Ricerca sincrona**: la pagina resta in caricamento per tutta la durata
  della ricerca (10-30 secondi). Va bene per pochi utenti; con più
  traffico servirebbe eseguirla in background.
- **Kleinanzeigen/Subito sono ancora sperimentali** (vedi README.md) — il
  primo vero test in produzione potrebbe richiedere un aggiustamento ai
  selettori.
