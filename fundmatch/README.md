# GrantPath (fundmatch)

Business primario attuale (dopo 2 pivot: SocialPerks Pilot → RaiseReady → GrantPath).
Motivo del pivot finale: RaiseReady vendeva "un PDF scritto dall'AI" — mercato debole,
nessuno paga per qualcosa che può ottenere gratis da un chatbot. GrantPath vende accesso a
informazione reale e verificata (bandi/finanziamenti pubblici) + giudizio esperto sulla
candidatura — mercato consolidato, la gente paga consulenti per questo da sempre.

## Struttura
- `data/programs.json` — database di bandi/finanziamenti REALI, ognuno verificato con link
  ufficiale e data di verifica. Nessun programma è inventato.
- `delivery/match_grants.py` — motore di matching (profilo azienda → programmi compatibili),
  con opzione `--personalize` che usa un LLM SOLO per riassumere/spiegare i match reali,
  mai per inventarne di nuovi (vincolo esplicito nel prompt)
- `landing/index.html` — sito, dark theme "istituzionale", con: credenziali del fondatore,
  tabella di programmi con link diretti alle fonti ufficiali, disclaimer chiaro
  ("non garantiamo l'ottenimento di alcun finanziamento")

## Testato
- `match_grants.py` verificato end-to-end, sia senza chiave AI (elenco puro dal database)
  sia con chiave AI reale (nota personalizzata, verificata: non inventa nulla fuori dai dati)
- Landing verificata: HTML valido, screenshot desktop/mobile

## Cosa manca prima di andare live
Stesso schema di RaiseReady: dominio, deploy (Vercel, root directory `fundmatch/landing`),
Stripe (Payment Link €149 e €349), chiave LLM (già fornita e testata per RaiseReady, stessa
può essere riusata qui — stesso meccanismo `LLM_API_KEY`).

## Da ampliare
Il database ha 10 programmi verificati (IT/FR/ES/UE) — va ampliato nel tempo con altre fonti
verificate manualmente prima di ogni aggiunta, mai generato automaticamente senza verifica.
