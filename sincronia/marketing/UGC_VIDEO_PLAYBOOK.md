# UGC video, budget zero, senza volto

## Cosa puoi mostrare (e cosa no)

| Puoi mostrare | Perché va bene |
|---|---|
| Il sito, il form, il flusso di pagamento | È reale, è tuo |
| Un report di esempio con un'azienda **inventata e segnata come tale** ("Esempio: PMI innovativa, Milano") | Dimostra il prodotto senza fingere un cliente vero — come fanno tutti i software con gli screenshot demo |
| Contenuto informativo sui bandi reali (quelli nel database: EIC Accelerator, Smart&Start, ecc.) | Sono dati veri, pubblici, verificabili — zero rischio |
| La tua voce che spiega/narra | Hai escluso solo il volto, non la voce |

| NON mostrare | Perché |
|---|---|
| Un report presentato come "di un cliente vero" | Non esiste ancora, sarebbe un caso studio falso |
| Numeri di conversione/vendite finti ("già 50 aziende ci usano") | Falso, vietato dalle tue stesse regole |
| Il tuo volto | Hai chiesto esplicitamente di escluderlo |

## Come si registra (zero budget, zero volto)

- **Schermo**: QuickTime (Mac, integrato, gratis) → File → Nuova registrazione schermo. O OBS Studio (gratis, multipiattaforma) se vuoi più controllo.
- **Voce**: registri col microfono del telefono o del laptop mentre parli sopra la registrazione schermo, oppure aggiungi la voce dopo in fase di montaggio.
- **Montaggio/sottotitoli**: CapCut (gratis, ha anche sottotitoli automatici — utile perché la maggior parte guarda senza audio).
- **Durata**: 20-45 secondi. Il gancio (prima frase) entro i primi 2 secondi o si perde lo scroll.

## 4 script pronti

### 1. "3 bandi che (quasi) nessuno conosce" — educativo, alta condivisibilità
Schermo: il sito, sezione "Bandi tracciati", zoom sulle righe della tabella.
> "Tre finanziamenti pubblici che la maggior parte delle PMI italiane non sa che esistono.
> Uno: Smart&Start Italia, fino a 1.5 milioni a tasso zero, gestito da Invitalia.
> Due: Eurostars, fino a 3 milioni per chi fa R&D con un partner europeo.
> Tre: EIC Accelerator, grant più equity, fino a 2.5 milioni.
> Li trovi tutti, con link ufficiale, su sincronia.live."

### 2. "Come funziona Sincronia in 30 secondi" — demo di prodotto
Schermo: registrazione reale del sito, dal form ai risultati.
> "Ti dico settore, paese e fase della tua azienda. [mostra form]
> In 48 ore ricevi l'elenco dei bandi compatibili, con link ufficiali. [mostra sezione report]
> Se vuoi, revisioniamo anche la candidatura prima che la invii."

### 3. "Cosa controlliamo prima che invii una candidatura" — dimostra competenza
Schermo: il template di report (da `sincronia/delivery/REPORT_TEMPLATE.md`), o un report di esempio chiaramente etichettato "ESEMPIO".
> "Prima di inviare una candidatura a un bando, controlliamo sempre tre cose:
> se il budget torna con quello che chiedi,
> se ci sono red flag tipo un TAM senza fonte,
> e se manca qualcosa che i valutatori si aspettano di vedere.
> Questo è un esempio di come lo segnaliamo. [mostra report demo]"

### 4. "Perché ho costruito Sincronia" — storytelling, zero volto
Schermo: slide di testo semplici (puoi usare `promo-animation.html` come base visiva) o semplicemente schermo nero con testo.
> "Ho passato mesi a vedere PMI perdere finanziamenti a cui avevano diritto,
> solo perché non sapevano dove cercarli o come scriverli bene.
> Ho background di finanza, parlo italiano, spagnolo, inglese, e ho messo insieme
> un database verificato di bandi reali in tutta Europa. Si chiama Sincronia."

## Dove pubblicare
- **LinkedIn** (probabilmente il canale migliore per questo pubblico B2B: video nativo, non link esterno nel primo post)
- Instagram Reels / TikTok se vuoi provare reach più ampio, stesso contenuto riadattato
- YouTube Shorts

## Report demo da usare come materiale visivo
Genera un report di esempio reale (con dati fittizi ma chiaramente segnati) così:
```
cd sincronia/delivery
python3 match_grants.py --country IT --keywords "innovazione,digitalizzazione" \
  --stage startup --business-desc "Esempio: startup italiana, software B2B" \
  --lang it --out esempio_report.md --personalize
```
Aggiungi in cima al file, ben visibile: **"ESEMPIO ILLUSTRATIVO — non un cliente reale"** prima di usarlo in un video.
