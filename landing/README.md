# SocialPerks Pilot — Landing page

Sito statico puro (HTML/CSS/JS, zero dipendenze, zero build step). Apri direttamente
`index.html` in un browser per vederlo in locale.

## Cosa manca prima che sia "live" per davvero (checkpoint — serve tua approvazione)

1. **Deploy**: pronto per Vercel / Netlify / Cloudflare Pages (free tier). Basta collegare
   un account e puntarlo a questa cartella `landing/` — non l'ho fatto perché richiede
   connettere un tuo account esterno.
   - Vercel: `vercel --cwd landing` (dopo `vercel login`)
   - Netlify: trascina la cartella `landing/` su app.netlify.com/drop
   - Cloudflare Pages: collega il repo, build command vuoto, output directory `landing`
2. **Dominio**: il footer usa `hello@socialperks.example` come placeholder — va sostituito
   con la tua email reale (o un dominio, se ne acquisti uno — acquisto = checkpoint).
3. **Form reale**: il form attualmente apre un `mailto:` precompilato come fallback (nessun
   dato viene inviato a terzi). Per una raccolta più solida, collega un free tier tipo
   Formspree o Getform (richiede creare un account — checkpoint), oppure una funzione
   Supabase/Vercel già nel tuo stack.
4. **Analytics**: consigliato Cloudflare Web Analytics (gratuito, senza cookie, rispettoso
   della privacy) — richiede connettere l'account Cloudflare. Placeholder lasciato nell'head
   di `index.html`.

## Verifiche già fatte
- Nessuna dipendenza esterna a pagamento
- Nessun testimonial/logo/numero inventato — la sezione social proof dichiara onestamente
  che il programma è agli inizi ("gruppo ristretto di partner")
- Honeypot anti-spam nel form + validazione client-side dei campi obbligatori
- Responsive: layout single-column sotto 760px, grid a 2-3 colonne sopra
- Privacy policy e termini chiaramente marcati come BROUILLON/bozza da validare
