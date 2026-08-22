# Dominio — shortlist pronta, nessun acquisto effettuato

Nessuna registrazione è stata fatta (richiede carta di pagamento reale, checkpoint). Quando
qualcuno con accesso a un metodo di pagamento è pronto, verificare disponibilità su un
registrar (es. Cloudflare Registrar — già nel tuo stack, prezzi at-cost, nessun markup) e
registrare in 2 minuti.

## Shortlist (in ordine di preferenza)
1. `raiseready.io`
2. `getraiseready.com`
3. `raiseready.co`
4. `deckcheck.io`
5. `raiseready.app`

## Perché questo ordine
`.io`/`.com` restano i più credibili per un prodotto B2B rivolto a founder internazionali;
`getX.com` è il fallback standard quando il dominio nudo `.com` non è disponibile.

## Passaggi esatti per registrare (quando pronto)
1. Vai su Cloudflare Registrar (o Namecheap/Porkbun come alternative economiche)
2. Cerca il primo disponibile della lista sopra
3. Registra (costo indicativo €10-15/anno per `.io`, meno per `.com`)
4. Punta il DNS al deploy della landing (`raiseready/landing/`) su Vercel/Netlify/Cloudflare Pages
