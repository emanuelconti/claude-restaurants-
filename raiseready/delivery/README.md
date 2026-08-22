# RaiseReady — delivery & pagamenti (modalità TEST)

Stesso approccio già validato in `payments/` (SocialPerks): Stripe Payment Links in
modalità test, zero backend obbligatorio per partire. Nessuna chiave configurata, nessun
account collegato, nessun addebito reale.

## Setup pagamento (quando pronto)
1. Account Stripe in modalità TEST
2. 2 Payment Link: "Deck Check" €149, "Deck + Model Check" €349
3. Raccogli email + nome progetto/startup come campi del checkout
4. Redirect a una success page che spiega i prossimi passi (upload dei file)

## Come arrivano i file del cliente (deck/modello)
Opzione più semplice col tuo stack esistente: un form che carica su **Supabase Storage**
(free tier) subito dopo il pagamento confermato — nessun servizio nuovo da creare, solo
attivare lo storage su un progetto Supabase già tuo.

## Come si produce il report
Vedi `raiseready/delivery/REPORT_TEMPLATE.md` — struttura fissa, così ogni report è coerente
e verificabile, che venga scritto a mano o con assistenza AI (richiede una chiave API se si
vuole automatizzare la prima bozza — vedi `docs/STRATEGY_V2.md`).

## Codice riutilizzato
`payments/api/create-checkout-session.js` e `payments/api/webhook.js` sono generici — bastano
un nuovo `PRICE_CATALOG` con questi due prodotti per riusarli identici, invece di duplicare
codice Stripe.
