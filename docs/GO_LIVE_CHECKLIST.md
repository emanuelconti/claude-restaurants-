# GO LIVE — checklist passo-passo (zero gergo, zero saltare passaggi)

Questa è l'unica lista di cose che **solo tu** puoi fare, perché richiedono un tuo account
reale, una tua email, o una tua carta. Tutto il resto (codice, testi, pagine, script) è già
fatto e pushato sul branch. Ogni passaggio dura 2-10 minuti, in ordine.

---

## 1. Chiave AI gratuita (10 minuti, zero carta di credito)
Serve per far scrivere davvero i report a RaiseReady (senza, funziona solo in modalità test/finta).

1. Vai su **console.groq.com**
2. Clicca "Sign up", registrati con la tua email (nessuna carta richiesta)
3. Nel pannello, cerca "API Keys" → "Create API Key"
4. Copia la chiave che inizia con `gsk_...`
5. Tienila da parte — la useremo al passaggio 5

## 2. Dominio (5 minuti se usi sincronia.live che hai già, altrimenti 10)
**Se possiedi già `sincronia.live`:**
1. Vai dove hai comprato il dominio (registrar — es. Namecheap, GoDaccy, ecc.)
2. Cerca la sezione "DNS" o "Gestione DNS"
3. Quando avremo il sito online (passaggio 3), ti darò 2 righe esatte da incollare lì
   (si chiamano "record DNS") — per ora salta al passaggio 3

**Se preferisci un dominio nuovo dedicato a RaiseReady (es. `raiseready.io`):**
1. Vai su **domains.cloudflare.com** (o Namecheap se preferisci)
2. Cerca `raiseready.io` (o vedi altre opzioni in `raiseready/marketing/DOMAIN_SHORTLIST.md`)
3. Compralo (~€10-15/anno, serve una carta)

## 3. Mettere il sito online (5 minuti, gratis)
1. Vai su **vercel.com**, clicca "Sign up", accedi con GitHub (lo stesso account dove sta
   questo repository)
2. Clicca "Add New Project", scegli questo repository (`claude-restaurants-`)
3. In "Root Directory" scrivi: `raiseready/landing`
4. Clicca "Deploy" — in 1 minuto hai un link tipo `raiseready-xyz.vercel.app` che funziona
5. Se vuoi collegare il tuo dominio (sincronia.live o quello nuovo): su Vercel vai in
   Settings → Domains → Add → scrivi il dominio → Vercel ti mostra le 2 righe DNS esatte da
   incollare dal passaggio 2

## 4. Pagamenti (5 minuti)
1. Vai su **dashboard.stripe.com/register**, crea un account con la tua email
2. Resta in modalità **Test** (interruttore in alto a destra — NON attivarlo su "live" ancora)
3. Vai su "Payment Links" → "Create payment link"
4. Crea 2 link: "Deck Check" €149, "Deck + Numbers Check" €349
5. Copia i 2 link — te li faccio incollare io nel sito appena me li dai

## 5. Email per ricevere le richieste (2 minuti)
1. Se hai già un'email che vuoi usare (es. la tua Gmail), va benissimo, dimmela e la metto
   ovunque serve nel sito al posto del placeholder `hello@raiseready.example`
2. In alternativa, crea una nuova email dedicata (es. Gmail gratuito)

## 6. Dammi le 3 cose raccolte
Quando hai fatto 1, 4, 5 (il 2-3 solo se vuoi il sito già online), mandami:
- La chiave Groq (`gsk_...`)
- I 2 link Stripe
- L'email da usare

Io le collego ovunque serve nel codice e ripubblico. **Non condividere mai la chiave Groq o
le chiavi Stripe in chat pubbliche o screenshot che pubblichi altrove** — solo qui con me va bene.

---

## Cosa NON serve fare
- Non serve creare un database a mano — lo aggiungo io via Supabase quando serve, con la tua
  approvazione per collegare l'account (stesso principio: un account, non una carta, se
  resti nel free tier)
- Non serve scrivere codice
- Non serve capire cosa sono i "record DNS" oltre a copiare/incollare quello che ti mostro
