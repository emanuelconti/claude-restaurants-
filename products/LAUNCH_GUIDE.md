# Guida al lancio — 2 prodotti pronti, 200€ a testa

Questa cartella contiene **due prodotti digitali finiti**, pronti da vendere online. Nessun prodotto fisico, nessuna spedizione, nessun magazzino. Prima di partire, una premessa onesta: **nessuno può garantire un "guadagno enorme"** — chi lo promette mente. Quello che trovi qui è un prodotto reale, una pagina di vendita pronta e un piano di spesa da 200€ costruito per massimizzare le probabilità di vendita, non un risultato garantito.

## I due prodotti

| | `leadforge/` | `zenbudget/` |
|---|---|---|
| Cos'è | Software di outreach email automatico (B2B) | Planner finanziario Excel/Google Sheets completo |
| Target | Freelance, agenzie, marketer | Pubblico consumer ampio (budgeting/risparmio) |
| Prezzo consigliato | 49€ | 19€ |
| Break-even sui 200€ | ~5 vendite | ~11 vendite |
| Canale di vendita | Gumroad | Gumroad / Etsy |
| File di vendita reale | `leadforge.py` + template | `ZenBudget_Planner.xlsx` (già generato, pronto) |

Entrambi sono venduti come **download digitale istantaneo**: il cliente paga, riceve il file, fine. Zero costi di produzione ricorrenti.

## Passo 1 — Crea l'account Gumroad (10 minuti, gratis)

1. Vai su gumroad.com → crea un account gratuito
2. Collega un metodo di incasso (Stripe/PayPal integrato — Gumroad gestisce i pagamenti, trattiene ~10% di commissione)
3. Verifica l'identità se richiesto (necessario per ricevere pagamenti reali)

## Passo 2 — Carica LeadForge

1. Comprimi in uno zip: `leadforge.py`, `config.example.py`, `leads_template.csv`, `requirements.txt`, `README.md`, `QUICKSTART.md`
2. Su Gumroad: "New product" → digitale → carica lo zip
3. Titolo: "LeadForge — Automated Cold Email Outreach Engine"
4. Prezzo: 49€ (puoi testare anche 29€ per volume maggiore)
5. Descrizione: copia il contenuto di `leadforge/README.md`
6. Copia il link "checkout" del prodotto e incollalo in `leadforge/landing-page/index.html` al posto di `REPLACE_WITH_YOUR_GUMROAD_LINK` (due punti nel file)

## Passo 3 — Carica ZenBudget

1. Su Gumroad: "New product" → digitale → carica `zenbudget/ZenBudget_Planner.xlsx`
2. Titolo: "ZenBudget — The Finance Planner That Fits On One Screen"
3. Prezzo: 19€
4. Descrizione: copia il contenuto di `zenbudget/README.md`
5. Copia il link checkout e sostituiscilo in `zenbudget/landing-page/index.html`

## Passo 4 — Pubblica le landing page (gratis)

Le due pagine in `*/landing-page/index.html` sono file HTML statici, senza dipendenze. Il modo più veloce e gratuito per pubblicarle:

1. Vai su **vercel.com** o **netlify.com** (hai già familiarità con Vercel, visto `socialperks-fr.vercel.app` in questo repo)
2. "Import" la cartella `leadforge/landing-page` (o `zenbudget/landing-page`) come sito statico
3. In 1 click ottieni un URL pubblico (es. `leadforge-shop.vercel.app`)
4. Ripeti per l'altro prodotto

In alternativa, usa direttamente la pagina prodotto di Gumroad (già pronta, zero setup) e salta questo passo.

## Passo 5 — Esegui il piano marketing da 200€

Ogni prodotto ha il suo piano dettagliato:
- `leadforge/marketing-plan-200eur.md`
- `zenbudget/marketing-plan-200eur.md`

**In sintesi per entrambi:** prima 5-7 giorni di distribuzione gratuita (Reddit, X, TikTok/Pinterest a seconda del prodotto) per generare le prime vendite e riprova sociale, poi spingi con ads (Meta/TikTok/Reddit) SOLO sul contenuto che ha già funzionato organicamente. Non buttare i 200€ tutti insieme il primo giorno.

## Checklist pratica

- [ ] Account Gumroad creato e verificato
- [ ] LeadForge caricato su Gumroad, prezzo impostato
- [ ] ZenBudget caricato su Gumroad, prezzo impostato
- [ ] Link Gumroad inseriti nelle landing page
- [ ] Landing page pubblicate (Vercel/Netlify) o si usa la pagina Gumroad diretta
- [ ] 3-5 post organici pubblicati (settimana 1)
- [ ] Budget ads impostato SOLO dopo aver visto cosa converte organicamente

## Cosa realisticamente aspettarsi

Con 200€ e un prodotto genuinamente utile, un lancio ben eseguito porta tipicamente a un numero di vendite a due cifre nelle prime 2-3 settimane — sufficiente per rientrare della spesa e generare profitto, ma non è un risultato automatico: dipende dall'esecuzione (qualità dei contenuti organici, velocità di risposta ai commenti, iterazione sulle creatività ads). Nessuno strumento, incluso questo, può bypassare la necessità di eseguire il piano.
