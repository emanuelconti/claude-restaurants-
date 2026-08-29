# Video script — 30 secondi, per un montaggio reale (o per usare la promo animata così com'è)

**Nota tecnica:** questo ambiente non ha ffmpeg né un motore text-to-speech disponibile, quindi
non posso generare direttamente un file `.mp4`. Ho costruito `promo-animation.html` — una
sequenza animata autoportante (nessuna dipendenza esterna) che cicla 4 scene in 16 secondi,
registrabile con qualsiasi screen recorder (QuickTime, OBS, anche lo strumento cattura schermo
del telefono puntato sullo schermo) per ottenere un video reale in pochi minuti. Sotto trovi lo
script voiceover completo se preferisci un montaggio più curato.

## Shot list / voiceover (30s)

| Tempo | Schermo | Voiceover |
|---|---|---|
| 0-4s | "Your deck gets 3 minutes of investor attention." | "You get about three minutes of an investor's attention." |
| 4-8s | "We find the holes before they do." | "We find the gaps in your deck — before they do." |
| 8-12s | "No call. No subscription." | "No call to book. No subscription. Just a report." |
| 12-16s | "From €149" + logo | "RaiseReady. From one hundred forty-nine euros." |
| 16-30s | Screenshot landing/report esempio | "Upload your deck today, get your report in 24 to 48 hours." |

## Come produrlo velocemente senza editing tools
1. Apri `raiseready/marketing/promo-animation.html` in un browser a schermo intero
2. Registra lo schermo per 16-30 secondi (loop naturale)
3. Se vuoi voiceover, registralo separatamente con il microfono del telefono seguendo la
   tabella sopra e sovrapponilo con qualsiasi app gratuita di editing (CapCut, iMovie)
