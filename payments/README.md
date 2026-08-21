# Stripe — integrazione modalità TEST (Fase 8)

**Stato: pronto ma non collegato.** Nessuna chiave Stripe è configurata in questo repo,
nessun account è stato collegato, nessun addebito reale è mai stato o sarà effettuato senza
tua approvazione esplicita (vedi regole non negoziabili in `docs/STATUS.md`).

## Opzione consigliata per partire subito: Stripe Payment Links (zero codice)

Per il pilota, la via più veloce e a rischio più basso è **non** costruire un checkout
custom, ma usare i **Payment Links** di Stripe (gratuiti, nativi, in modalità test finché non
li attivi live):

1. Accedi al tuo account Stripe (o creane uno — checkpoint, serve tua azione)
2. Metti l'account in **modalità TEST** (toggle in alto a destra nella dashboard)
3. Vai su Payment Links → crea 2 link:
   - "Pilota Essenziale" — €490 — one-time payment
   - "Pilota Standard" — €1.200 — one-time payment
4. Nelle impostazioni del link, imposta come redirect: `success.html` (di questa cartella) e
   raccogli email + nome azienda come campi custom del checkout
5. Incolla i 2 link generati nei CTA "Demander ce pilote" della landing page
   (`landing/index.html`) quando li avrai — al momento puntano al form di contatto

**Perché questa via**: zero codice da mantenere, zero rischio di bug nel gestire dati di
carta (Stripe li gestisce interamente), attivabile in pochi minuti quando deciderai di
collegare l'account.

## Opzione B (più controllo, richiede un piccolo backend)
Scaffold pronto in `payments/api/` per una funzione serverless (Vercel) che crea una
Checkout Session dinamica e gestisce il webhook di conferma pagamento. Usala solo se
serve prezzo dinamico o metadata più ricchi di quanto un Payment Link permetta.

- `payments/api/create-checkout-session.js` — crea la sessione di checkout
- `payments/api/webhook.js` — riceve la conferma di pagamento, registra lo stato,
  triggera l'email di onboarding (vedi `payments/emails/welcome.md`)
- Richiede `STRIPE_SECRET_KEY` e `STRIPE_WEBHOOK_SECRET` come environment variable su Vercel
  (mai nel codice — vedi `payments/.env.example`)

## Catalogo prodotti/prezzi suggerito
| Prodotto | Prezzo | Tipo |
|---|---|---|
| SocialPerks Pilota Essenziale | €490 | one-time |
| SocialPerks Pilota Standard | €1.200 | one-time |
| SocialPerks Retainer Base | €300/mese | subscription (solo dopo pilota riuscito) |
| SocialPerks Retainer Standard | €500/mese | subscription |
| SocialPerks Retainer Premium | €800/mese | subscription |

## Passaggi ESATTI per passare da test a live (da fare tu, quando sei pronto)
1. Verifica identità/business su Stripe (richiesto per accettare pagamenti reali)
2. Sostituisci le chiavi `sk_test_/pk_test_` con quelle `sk_live_/pk_live_` nelle
   environment variable (mai nel codice)
3. Ricrea gli stessi Payment Links in modalità live (i link test non diventano live
   automaticamente)
4. Aggiorna i link nella landing page
5. Testa un pagamento reale di importo minimo prima di condividere il link ai clienti

**Non farò nessuno di questi 5 passaggi autonomamente — richiedono le tue credenziali e la
tua decisione di accettare denaro reale.**
