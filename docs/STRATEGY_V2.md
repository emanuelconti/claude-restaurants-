# STRATEGY V2 — pivot: RaiseReady

Sostituisce l'indirizzo di `docs/STRATEGY.md` (SocialPerks Pilot), su richiesta esplicita:
"non c'entra né con SocialPerks né con Sowld né con quell'ecommerce". Gli asset SocialPerks
restano nel repo (non cancellati), semplicemente non più usati come base di questo business.

## Perché un business diverso e non più asset-based
Il modello precedente vinceva perché riusava relazioni/liste già calde (21 LOI, contatti
SocialPerks) — ma richiedeva vendita founder-led (chiamate dirette). Qui la richiesta è
esplicita: **zero coinvolgimento del fondatore in vendita/outreach personale**. Questo cambia
la formula: serve un prodotto **self-serve** (si vende e si eroga senza una call), non più un
servizio relazionale.

## Business scelto: RaiseReady
**Offerta in una frase:** "Carichi il tuo pitch deck (e modello finanziario), ricevi in 24-48h
un report che ti mostra dove un investitore troverebbe buchi — prima che lo faccia lui."

- **Cliente ideale:** founder pre-seed/seed in fundraising attivo — problema urgente
  (raccogliere capitale), spesa già preventivata (c'è un motivo per pagare €150-350 se aiuta
  a chiudere un round più velocemente), community pubbliche raggiungibili senza outreach
  1:1 (Indie Hackers, Product Hunt, r/startups, newsletter EU-Startups)
- **Perché è compatibile con "zero coinvolgimento del fondatore":** acquisto e consegna sono
  entrambi async — nessuna call richiesta né per vendere né per erogare, a differenza del
  modello SocialPerks
- **Cosa NON è:** non è consulenza di investimento, non è una garanzia di raccogliere fondi —
  va dichiarato esplicitamente ovunque (vedi `raiseready/landing/index.html`) per non entrare
  in territorio di consulenza finanziaria regolamentata

## Prezzo
- **Deck Check** — €149 — analisi del solo pitch deck (narrativa, struttura, red flag comuni)
- **Deck + Model Check** — €349 — analisi deck + modello finanziario (coerenza assunzioni,
  unit economics, red flag numerici)

## Il vincolo reale non aggirabile
La consegna richiede che *qualcuno* (umano o AI con una chiave API vera) produca l'analisi.
Due strade, entrambe richiedono un input reale da qualcuno:
1. **Automatica**: serve una `ANTHROPIC_API_KEY` (o altro provider) configurata come
   environment variable — nessuna chiave è disponibile in questo ambiente, va aggiunta da chi
   ha accesso a un account reale
2. **Semi-automatica**: il fondatore (o chiunque altro) rivede/approva ogni report prima
   dell'invio — 10-15 minuti a ordine, non è "vendita", è controllo qualità

Fino a quando una delle due non è attiva, il prodotto è **completo e vendibile** ma la
consegna reale resta un passaggio manuale finale. Non è possibile eliminarlo senza una
credenziale che io non ho.

## Canale di acquisizione (compatibile con zero outreach 1:1)
Content/community marketing invece di cold email: post pronti (vedi
`raiseready/marketing/COMMUNITY_POSTS.md`) per Indie Hackers, Product Hunt, r/startups —
richiedono solo di essere incollati da un account reale (nessun account community esiste già
per questo brand, va creato — azione da 2 minuti, non richiede pagamento).

## Unit economics
Costo diretto per report: ~€0-2 (storage Supabase free tier + eventuale costo API AI se
attivata). Margine lordo stimato >90% se automatizzato, >70% se il tempo di revisione umana
viene valorizzato.

## Target realistici (30 giorni)
- **Base:** 3-8 vendite (€450-€2.800)
- **Stretch:** 15-25 vendite (€2.500-€8.500)
- **Aspirazionale (€1M dichiarato):** non raggiungibile con un prodotto a €150-350 senza
  migliaia di vendite — stessa conclusione economica già in `docs/30_DAY_EXECUTION_PLAN.md`,
  qui anche più marcata perché il prezzo medio è più basso
