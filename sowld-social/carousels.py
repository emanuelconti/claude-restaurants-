"""What Sowld's Instagram carousels say, and which day says what.

The profile posts carousels only: a cover with a big title over a photo, then
one numbered point per slide, text on white with a photo fading in under it,
the mark on every slide, no faces. The last slide is Sowld, and only when the
topic earns it.

Italian, because getsowld.com is Italian first and the account is Italian.

The topics are everyday life around the stuff we own, buy, keep and finally
let go of: the wardrobe, the drawer of cables, moving house, a market find,
the thing you regret selling. People like them because they recognise
themselves, and save them because they are about something they keep putting
off. Nothing here is a sales pitch; see STYLE.md for why that is the rule and
not a preference.

Every topic is a title for the cover, a line for the caption, and points: a
heading, the lines under it, and the closing line set in bold. `photos` names
the set its slides draw from (PHOTO_SETS); `countdown` numbers the points from
the highest down, for a ranking; `cta` adds the Sowld slide at the end.
"""

from __future__ import annotations

import datetime as _dt
import random as _random

# The first day of the bank's rotation.
EPOCH = _dt.date(2026, 10, 30)

PHOTO_SETS = {
    # Wardrobes, shelves, boxes: the stuff a topic about owning things sits on.
    "stuff": [
        "1489274495757-95c7c837b101",  # a rail of clothes
        "1558769132-cb1aea458c5e",  # folded clothes on a shelf
        "1445205170230-053b83016050",  # a wardrobe from above
        "1591047139829-d91aecb6caea",  # a bag on a chair
        "1595341888016-a392ef81b7de",  # shoes lined up
        "1586528116311-ad8dd3c8310d",  # cardboard boxes, moving day
        "1600585154340-be6161a56a0c",  # an empty room, moving day
        "1484101403633-562f891dc89a",  # a desk with cables and a lamp
    ],
    # Markets, second-hand shops, flea stalls: the hunt.
    "market": [
        "1441986300917-64674bd600d8",  # a shopfront
        "1556742049-0cfed4f6a45d",  # a market stall
        "1472851294608-062f824d29cc",  # a shop interior
        "1513519245088-0e12902e5a38",  # vintage furniture
        "1555041469-a586c61ea9bc",  # a vintage table
        "1538688525198-9b88f6f53126",  # an armchair
        "1493663284031-b7e3aefcae8e",  # a lamp and a chair
        "1550009158-9ebf69173e03",  # old electronics on a table
    ],
    # Mornings, coffee, notebooks: for the topics that are just life.
    "life": [
        "1470252649378-9c29740c9fa8",  # sunrise over a valley
        "1484480974693-6ca0a78fb36b",  # an open notebook
        "1506784983877-45594efa4cbe",  # a planner and a coffee
        "1488190211105-8b0e65b80b4e",  # a desk, a coffee, a journal
        "1495364141860-b0d03eccd065",  # a hand holding an alarm clock
        "1511920170033-f8396924c348",  # latte art from above
        "1442975631115-c4f7b05b8a2c",  # a café inside, morning light
        "1434030216411-0b793f4b4173",  # a hand writing
    ],
    # Receipts, cards, laptops: money topics without a single figure invented.
    "money": [
        "1554224155-6726b3ff858f",  # hands with receipts
        "1563013544-824ae1b704d3",  # a card in a hand
        "1520607162513-77705c0f0d4a",  # a card terminal from above
        "1486312338219-ce68d2c6f44d",  # hands typing
        "1516321318423-f06f85e504b3",  # a hand at a laptop
        "1554224154-26032ffc0d07",  # a calculator and papers
    ],
}

# The bank: what a run posts when writing a fresh topic fails. Everyday life
# first, Sowld only where the topic walks into it on its own.
EVERYDAY = [
    dict(
        title="Le 7 fasi di quando decidi di svuotare l'armadio",
        hook="La 4 è quella che ci blocca tutti.",
        photos="stuff",
        points=[
            ("L'entusiasmo iniziale", ["Tiri fuori tutto e lo metti sul letto.", "Ti senti una persona nuova."], "Durerà quindici minuti."),
            ("Il primo dubbio", ["«Questo magari torna di moda.»", "Lo hai comprato nel 2017."], "La moda torna. Tu, in quella taglia, forse no."),
            ("La pila del forse", ["Non è né da tenere né da buttare.", "Cresce più in fretta delle altre due."], "Il forse è dove va a morire il decluttering."),
            ("Il senso di colpa", ["«L'ho pagato tanto.»", "È fermo lì da tre anni."], "I soldi li hai già spesi. Lo spazio lo stai spendendo adesso."),
            ("La resa", ["Rimetti tutto dentro.", "Tranne due magliette, per dire che hai fatto qualcosa."], "L'armadio ha vinto un'altra volta."),
            ("Il letto da liberare", ["Sono le undici di sera.", "Devi dormire lì."], "La deadline più efficace della storia."),
            ("La promessa", ["«Domenica prossima lo faccio sul serio.»", "È la quarta domenica."], "Lo sappiamo entrambi."),
        ],
    ),
    dict(
        title="Oggetti che tutti abbiamo in casa e nessuno usa da anni",
        hook="Scommetto che ne hai almeno cinque.",
        photos="stuff",
        countdown=True,
        points=[
            ("La scatola dei cavi", ["Non sai più cosa carica cosa.", "Ma buttarli sembra pericoloso."], "Dentro c'è sicuramente un cavo per qualcosa che non possiedi più."),
            ("L'attrezzo da palestra", ["Comprato a gennaio con grande convinzione.", "Ora regge un maglione."], "Il miglior appendiabiti mai acquistato."),
            ("La macchina per fare il pane", ["Usata due volte.", "Pesa come un bambino."], "Il regalo che si trasforma in mobile."),
            ("I cd e i dvd", ["Non hai più niente che li legga.", "Li tieni lo stesso."], "Non sono oggetti, sono ricordi con la custodia rotta."),
            ("I vestiti della taglia di prima", ["In entrambe le direzioni.", "Per sicurezza."], "L'armadio come piano B del corpo."),
            ("Le pentole doppie", ["Una la usi sempre, le altre mai.", "Però non si butta una pentola."], "Esiste una sola padella preferita, e lo sai."),
        ],
    ),
    dict(
        title="Le cose che ci diciamo prima di comprare qualcosa che non ci serve",
        hook="Le abbiamo dette tutti, almeno una volta.",
        photos="money",
        points=[
            ("«È un investimento»", ["Non lo è.", "Lo è quasi mai."], "Un investimento si rivende. Una scusa, no."),
            ("«Era in offerta»", ["Hai risparmiato il 40 per cento.", "Su una cosa che non avresti comprato."], "Risparmiare su una spesa inutile resta una spesa."),
            ("«Lo userò tantissimo»", ["Lo dici con una convinzione impressionante.", "Ci credi davvero, in quel momento."], "Conta quante volte l'hai usato il mese scorso. Non quante ne immagini."),
            ("«Me lo merito»", ["Spesso è vero.", "Ma il carrello non è il posto dove si premiano le cose fatte bene."], "Meritarselo e averne bisogno sono due cose diverse."),
            ("«Se non lo prendo ora lo finiscono»", ["La paura di perderlo decide al posto tuo.", "Quasi sempre non lo finiscono."], "L'urgenza è una tecnica, non un'informazione."),
            ("«Poi lo rivendo»", ["L'intenzione c'è.", "La foto per l'annuncio, mai."], "Rivendere è un lavoro. Comprare dura dieci secondi."),
        ],
    ),
    dict(
        title="Le 6 fasi del trasloco, raccontate da chi ci è passato",
        hook="La 3 cambia il rapporto con i propri oggetti per sempre.",
        photos="stuff",
        points=[
            ("Ottimismo", ["«In un weekend finiamo.»", "Hai comprato dieci scatoloni."], "Te ne serviranno trentadue."),
            ("Il disincanto", ["Scopri quanta roba hai.", "Non eri preparato a questa informazione."], "Vivevi in un magazzino senza saperlo."),
            ("La selezione brutale", ["A un certo punto smetti di decidere con il cuore.", "Decidi con il braccio che deve sollevarlo."], "Niente ti libera come dover portare le cose su per le scale."),
            ("Lo scatolone misto", ["Pile, un calzino, una chiave, delle candeline.", "Scritto sopra: «varie»."], "Ogni trasloco ha il suo scatolone che non verrà mai aperto."),
            ("La casa vuota", ["Resti lì dentro un minuto.", "Sembra più grande e più piccola insieme."], "Le case vuote fanno un rumore che ti ricordi."),
            ("Il dopo", ["Un mese dopo non ricordi metà di quello che hai portato.", "E stai benissimo lo stesso."], "Forse non servivano trentadue scatoloni."),
        ],
    ),
    dict(
        title="Cose che capisci solo quando compri usato",
        hook="La numero 5 te la ricordi per sempre.",
        photos="market",
        cta=True,
        points=[
            ("Le foto dicono più della descrizione", ["La descrizione la scrivono per vendere.", "Le foto no."], "Una foto sfocata proprio del punto che conta non è mai un caso."),
            ("Il prezzo più basso non è l'affare", ["Quasi sempre è l'annuncio con qualcosa che non va.", "O con qualcosa che non è stato detto."], "L'affare vero si nasconde nel mezzo, non in fondo."),
            ("Impari a fare domande", ["«Funziona tutto? Ci sono difetti che non si vedono?»", "Come risponde conta quanto cosa risponde."], "Il silenzio è una risposta anche lui."),
            ("Il prezzo da nuovo non significa niente", ["«Costava 900 euro» non ti dice quanto vale oggi.", "Te lo dicono solo gli annunci simili in vendita adesso."], "Il valore di una cosa usata lo decide il suo mercato, non lo scontrino."),
            ("Il primo acquisto sbagliato", ["Capita a tutti.", "Costa poco e insegna tanto."], "Nessuno diventa bravo senza prendersi una fregatura."),
            ("La soddisfazione è diversa", ["Non è solo aver risparmiato.", "È aver trovato."], "Comprare è facile. Trovare è un'altra cosa."),
        ],
    ),
    dict(
        title="Le 7 bugie che diciamo alla nostra famiglia sugli acquisti",
        hook="La prima la dici almeno una volta al mese.",
        photos="money",
        points=[
            ("«Ce l'avevo già»", ["Detto con totale naturalezza.", "Mentre stacchi l'etichetta."], "L'etichetta è sempre il dettaglio che ti tradisce."),
            ("«Era scontatissimo»", ["Il numero reale resta un segreto di Stato.", "Arrotondi verso il basso. Molto."], "Nessuno ha mai arrotondato verso l'alto il prezzo di una scarpa."),
            ("«Me l'ha regalato una collega»", ["La collega non esiste.", "Nessuno lo verificherà mai."], "Ogni famiglia ha una collega immaginaria molto generosa."),
            ("«Lo uso per lavoro»", ["Tecnicamente potrebbe servire.", "Tecnicamente."], "La parola «tecnicamente» regge interi bilanci familiari."),
            ("«È usato»", ["Questa a volte è vera.", "E funziona benissimo."], "L'unica che non devi inventarti."),
            ("«Non l'ho comprato io»", ["Detto davanti a un pacco con il tuo nome.", "Con sicurezza."], "L'audacia, a volte, paga."),
            ("«È l'ultima cosa»", ["Non è l'ultima cosa.", "Non lo è mai."], "Ci crediamo tutti, ogni volta."),
        ],
    ),
    dict(
        title="Le cose che rimpiangi di aver venduto",
        hook="C'è sempre quell'oggetto. Anche tu stai pensando a uno.",
        photos="stuff",
        points=[
            ("La console dell'infanzia", ["Venduta per comprare quella nuova.", "La nuova non te la ricordi."], "Hai venduto un pezzo di pomeriggi, non una scatola."),
            ("La bici", ["«Tanto non la uso.»", "Ogni primavera, puntuale, ci ripensi."], "Le biciclette si rimpiangono a stagioni."),
            ("Il libro con le annotazioni", ["Il libro lo ritrovi.", "Le tue note a matita no."], "Alcune cose sono uniche solo perché le hai usate tu."),
            ("La giacca", ["Non ti stava neanche benissimo.", "Ma era quella delle foto di quegli anni."], "I vestiti tengono dentro le serate."),
            ("Lo strumento musicale", ["«Tanto non suono più.»", "Era una promessa, non un oggetto."], "Venderlo è stato dire a voce alta che avevi smesso."),
            ("Quello che hai dato via per fretta", ["Non per soldi, non per spazio.", "Solo perché quel giorno volevi chiudere in fretta."], "Il contrario di comprare d'impulso esiste, e fa lo stesso male."),
        ],
    ),
    dict(
        title="Segnali che sei diventato quello che rivende tutto",
        hook="Se te ne riconosci quattro, è tardi.",
        photos="market",
        points=[
            ("Calcoli il valore di tutto", ["Entri da un amico e pensi «questo lo venderesti bene».", "Non lo dici. Ma lo pensi."], "Il cervello, una volta che impara, non si spegne più."),
            ("Hai un angolo per le spedizioni", ["Scatole, nastro, un metro.", "Si è formato da solo."], "Nessuno decide di avere una zona imballaggi. Appare."),
            ("Fotografi con la luce giusta", ["Hai capito qual è la finestra migliore.", "E a che ora."], "La differenza tra una foto e un annuncio è la luce."),
            ("Controlli i prezzi per sport", ["Anche di cose che non venderesti mai.", "Solo per sapere."], "La curiosità è il primo sintomo."),
            ("Hai una scala di stato tua", ["«Buono» per te significa una cosa precisa.", "Molto più precisa di quella degli altri."], "Chi vende davvero descrive i difetti per primo."),
            ("Ti dà fastidio buttare", ["Non per ecologia.", "Perché vedi un valore che gli altri non vedono."], "Una volta che impari a guardare, non torni indietro."),
        ],
    ),
    dict(
        title="Le 6 fasi di una domenica che doveva essere produttiva",
        hook="La 4 arriva sempre, qualunque siano i piani.",
        photos="life",
        points=[
            ("La sveglia delle 8", ["Messa il sabato sera, con grandi ambizioni.", "Spenta alle 8 e 01."], "Il te del sabato sera non conosce il te della domenica mattina."),
            ("La lista", ["Sei cose.", "Scritte bene, in ordine."], "Scrivere la lista conta già come prima cosa fatta, ovviamente."),
            ("Il caffè lungo", ["Doveva durare dieci minuti.", "Sono le undici e mezza."], "Nessun caffè è mai durato quanto previsto."),
            ("Il buco nero", ["Video, messaggi, un articolo su una cosa che non ti serve.", "Alzi la testa e manca un'ora."], "Il tempo libero non si perde. Evapora."),
            ("La produttività improvvisa delle 19", ["All'improvviso riordini un cassetto che non c'entra niente.", "Con enorme energia."], "Facciamo qualsiasi cosa pur di non fare quella della lista."),
            ("La pace delle 22", ["Hai fatto due cose su sei.", "E va benissimo."], "Non tutte le domeniche devono produrre qualcosa."),
        ],
    ),
    dict(
        title="Quanto vale davvero una cosa usata: 5 cose da sapere",
        hook="La 2 è quella che fa sbagliare quasi tutti.",
        photos="market",
        cta=True,
        points=[
            ("Il prezzo da nuovo non conta", ["Un oggetto di quattro anni a metà prezzo non è un affare.", "È il prezzo normale di un oggetto di quattro anni."], "Lo sconto sul nuovo è il confronto sbagliato."),
            ("Conta quanto chiedono gli altri adesso", ["Stesso modello, stesse condizioni, in vendita oggi.", "Cinque annunci bastano per capire dove sei."], "Il mercato di un oggetto è fatto dagli oggetti simili, non dal listino."),
            ("Le condizioni cambiano tutto", ["«Come nuovo» e «con segni» non sono lo stesso oggetto.", "Confrontali solo a parità di stato."], "Due prezzi non si confrontano se non descrivono la stessa cosa."),
            ("Il prezzo non è il costo", ["Aggiungi spedizione, commissioni, il viaggio se lo ritiri.", "E il pezzo che manca e dovrai comprare."], "Confronta il costo vero, non il numero nell'annuncio."),
            ("Uno sconto enorme è un avviso", ["Il 70 per cento sotto non è fortuna.", "È una domanda a cui non hai ancora risposto."], "Guarda meglio, non più in fretta."),
        ],
    ),
    dict(
        title="Le 7 cose che fanno sembrare vecchia una casa (e non sono i mobili)",
        hook="La 5 la sistemi in un pomeriggio.",
        photos="stuff",
        points=[
            ("Le luci bianche fredde", ["Illuminano tutto come un ufficio.", "Nessuno si rilassa in un ufficio."], "La luce calda cambia una stanza più di un divano nuovo."),
            ("I fili in vista", ["Li smetti di vedere dopo una settimana.", "Chi entra li vede subito."], "L'ordine si nota quando manca, non quando c'è."),
            ("Le pareti nude", ["Non servono quadri costosi.", "Serve qualcosa che sia tuo."], "Una casa senza niente alle pareti sembra sempre in attesa."),
            ("Tutto dello stesso negozio", ["Coordinato ma senza storia.", "Come una foto di catalogo."], "Le case belle hanno sempre almeno un pezzo che stona."),
            ("Le tende troppo corte", ["Il dettaglio che non sai nominare.", "Ma che senti."], "Tende lunghe fino a terra: il trucco più sottovalutato che esista."),
            ("Il disordine orizzontale", ["Tavoli e mensole che raccolgono tutto.", "Si riempiono da soli."], "Ogni superficie libera è un posto in meno dove accumulare."),
            ("Le cose che non usi più", ["Occupano spazio e attenzione.", "Anche quando non le guardi."], "Una casa respira quando esce qualcosa, non quando entra."),
        ],
    ),
    dict(
        title="Frasi che dici ogni volta che apri un mercatino dell'usato",
        hook="La terza la dici ad alta voce. Sempre.",
        photos="market",
        points=[
            ("«Solo un giro veloce»", ["Dichiarato all'ingresso.", "Con totale sincerità."], "Non è mai stato un giro veloce."),
            ("«Ma questo chi lo compra?»", ["Detto davanti a un oggetto incomprensibile.", "Qualcuno lo comprerà. Sempre."], "Esiste un acquirente per tutto. È la cosa più bella dell'usato."),
            ("«Mia nonna ce l'aveva uguale»", ["Obbligatorio.", "Almeno una volta a visita."], "I mercatini sono musei dove puoi toccare."),
            ("«Se lo sistemo un attimo...»", ["La frase più pericolosa del lotto.", "Non lo sistemerai."], "Il «lo sistemo io» ha riempito garage interi."),
            ("«Torno dopo se c'è ancora»", ["Non ci sarà.", "Lo sai mentre lo dici."], "Al mercatino, tornare dopo è un modo gentile di dire di no."),
            ("«Ultimo giro e andiamo»", ["Il secondo ultimo giro.", "Dei quattro previsti."], "Nessuno è mai uscito da un mercatino al primo tentativo."),
        ],
    ),
    dict(
        title="6 abitudini di chi non accumula mai roba in casa",
        hook="Non sono più ordinati. Decidono prima.",
        photos="stuff",
        points=[
            ("Decidono all'ingresso", ["Il momento per dire di no è prima che entri in casa.", "Dopo diventa tuo e pesa di più."], "La porta di casa è il filtro migliore che hai."),
            ("Una cosa entra, una esce", ["Non è una regola rigida.", "È un promemoria."], "Lo spazio è fisso. Le cose no."),
            ("Non comprano per il te del futuro", ["Quello che correrà, cucinerà, leggerà di più.", "Comprano per quello che sei adesso."], "Il te immaginario ha un armadio pieno di cose mai usate."),
            ("Tengono il momento, non l'oggetto", ["Una foto occupa meno di una scatola.", "E la ritrovi più facilmente."], "Non è il ricordo che occupa spazio. È il contenitore."),
            ("Si danno una scadenza", ["«Se tra sei mesi è ancora qui intatto, esce.»", "Senza drammi."], "La data decide al posto tuo quando non riesci a decidere."),
            ("Lasciano andare senza aspettare il momento giusto", ["Il momento giusto non arriva.", "Arriva il trasloco."], "Meglio scegliere tu, con calma, che decidere di corsa."),
        ],
    ),
    dict(
        title="Le 8 peggiori sensazioni di un lunedì mattina",
        hook="La 6 non la racconta mai nessuno.",
        photos="life",
        countdown=True,
        points=[
            ("La sveglia che non sembra la tua", ["Suona come se fosse un errore.", "Non lo è."], "Il lunedì ha un suono tutto suo."),
            ("Il buio alle sette", ["Da ottobre in poi.", "Ti sembra di esserti alzato di notte."], "Mezz'ora di luce in più cambia l'umore più di quanto ammettiamo."),
            ("Le email aperte in fila", ["Sabato e domenica si sono accumulate.", "Nessuna è urgente. Insieme sembrano tantissime."], "La quantità spaventa più del contenuto."),
            ("Il caffè bevuto troppo in fretta", ["Non lo assapori.", "Lo usi."], "Un caffè di corsa non è un caffè, è un carburante."),
            ("La metro piena", ["Tutti con la stessa faccia.", "Una strana solidarietà silenziosa."], "L'unico momento in cui siamo tutti sinceri."),
            ("Il weekend che non ti ricordi", ["È passato e non sai dove.", "Eppure non ti sei riposato."], "Riposarsi e non fare niente non sono la stessa cosa."),
            ("La prima riunione", ["Dieci minuti di cose che potevano essere un messaggio.", "Tutti lo pensano."], "Nessuno lo dice mai."),
            ("Il calcolo di quanto manca", ["Lo fai alle nove del lunedì.", "Mancano quattro giorni e mezzo."], "Sapere quanto manca non ha mai aiutato nessuno."),
        ],
    ),
    dict(
        title="Cose che la gente non sa su quello che tiene in cantina",
        hook="La 3 vale più di quanto immagini.",
        photos="market",
        cta=True,
        points=[
            ("L'elettronica vecchia non è spazzatura", ["Modelli fuori produzione, pezzi di ricambio.", "Qualcuno li cerca sul serio."], "Esiste un compratore anche per la scheda di un modello che non si fa più."),
            ("I mobili impagliati tornano", ["Quello che sembrava vecchio dieci anni fa.", "Oggi si cerca."], "Il brutto e il vecchio sono due cose diverse, e il tempo lo chiarisce."),
            ("Gli strumenti musicali reggono il valore", ["Più di quasi tutto il resto.", "Anche usati, anche da anni."], "Il legno invecchia meglio della plastica, in tutti i sensi."),
            ("I giochi della tua infanzia", ["Non tutti, ma alcuni sì.", "Soprattutto con la scatola."], "La scatola è la metà del valore. Nessuno la tiene."),
            ("I libri no, quasi mai", ["Salvo rarità e prime edizioni.", "Meglio regalarli."], "Il valore di un libro è quasi sempre in chi lo legge dopo."),
            ("Ma il tempo costa", ["Fotografare, scrivere, rispondere, spedire.", "Per quindici euro non conviene."], "Prima di vendere, conta anche i minuti che ti costa."),
        ],
    ),
    dict(
        title="Le 6 fasi di quando un amico ti chiede «quanto l'hai pagato?»",
        hook="La 5 la facciamo tutti e nessuno lo ammette.",
        photos="money",
        points=[
            ("Il calcolo veloce", ["Decidi in mezzo secondo se dire la verità.", "Dipende da chi te lo chiede."], "La stessa cifra cambia a seconda dell'interlocutore."),
            ("L'arrotondamento", ["Verso il basso, naturalmente.", "«Sui cento», da centoquaranta."], "«Sui» è la parola più elastica della lingua italiana."),
            ("La giustificazione non richiesta", ["Nessuno te l'ha chiesta.", "La dai comunque."], "Spiegare troppo è sempre un'ammissione."),
            ("Il «ma era usato»", ["Se è vero, lo dici con orgoglio.", "Ed è giusto così."], "Pagare meno per la stessa cosa non è una scusa, è una competenza."),
            ("Il controllo del prezzo dopo", ["Appena resti solo.", "Per vedere se hai fatto bene."], "Nessuno resiste a verificare dopo. Nessuno."),
            ("La pace", ["Se l'hai usato tanto, andava bene comunque.", "Il prezzo conta meno dell'uso."], "Il vero affare è la cosa che usi ogni giorno."),
        ],
    ),
    dict(
        title="Le 6 cose che cambiano quando smetti di rimandare una cosa sola",
        hook="Non serve cambiare vita. Serve chiudere una cosa aperta.",
        photos="life",
        points=[
            ("La lista invisibile", ["Non sono i compiti scritti a pesare.", "Sono i cinque aperti che ti porti dietro ovunque."], "Quello che rimandi non sta fermo: ti segue."),
            ("Il costo del pensarci", ["Ci hai pensato venti volte in due mesi.", "Farlo richiedeva venti minuti."], "Rimandare costa sempre più del fare."),
            ("La cosa più piccola", ["Non quella importante: quella che ti dà più fastidio.", "Di solito è ridicola."], "Comincia da quella ridicola. Serve lo slancio, non l'eroismo."),
            ("Il primo passo sproporzionato", ["Chiudere una cosa piccola sblocca cose grandi.", "Non è motivazione: è slancio."], "Nessuno riordina un cassetto e poi si ferma lì."),
            ("Quello che ti torna indietro", ["Spazio in casa, spazio in testa.", "Arrivano insieme, sempre."], "Lo spazio in testa lo liberi con le mani."),
            ("Stasera", ["Non domenica, non il mese prossimo.", "Una cosa, venti minuti, stasera."], "La prossima settimana ha già troppe cose dentro."),
        ],
    ),
    dict(
        title="Quello che nessuno ti dice sul lasciare andare le cose",
        hook="Non è disciplina. È capire cosa stai davvero tenendo.",
        photos="stuff",
        points=[
            ("Non tieni l'oggetto", ["Tieni la persona che eri quando lo usavi.", "Oppure quella che pensavi di diventare."], "Gli armadi sono pieni di versioni di noi mai arrivate."),
            ("I soldi sono già spesi", ["«L'ho pagato tanto» non lo riporta indietro.", "Tenerlo ti costa ancora, ogni giorno, in spazio."], "I soldi spesi sono spesi. Lo spazio lo stai pagando adesso."),
            ("Il senso di colpa non è tuo", ["Un regalo non usato non è una mancanza di rispetto.", "Il gesto è già avvenuto, anni fa."], "Puoi tenere il pensiero senza tenere l'oggetto."),
            ("Finisce bene altrove", ["Quello che per te è fermo, per qualcun altro è esattamente quello che cercava.", "Succede ogni giorno."], "Una cosa che non usi non vale niente. In mano a un altro, sì."),
            ("La leggerezza dopo", ["Nessuno ha mai svuotato una stanza e si è pentito.", "Mai."], "Non ti mancherà. È la parte che non riesci a credere prima di farlo."),
            ("Una scatola", ["Non tutta la casa, non tutto l'armadio.", "Una scatola, oggi."], "Chi svuota case intere ha iniziato tutti con una scatola."),
        ],
        cta=True,
    ),
    dict(
        title="7 segnali che sei più avanti di quanto pensi",
        hook="Il 5 lo fai già e non te ne accorgi.",
        photos="life",
        points=[
            ("Confronti te con te di un anno fa", ["Non con le vite degli altri sullo schermo.", "È una competenza rara."], "L'unico paragone che dice qualcosa di vero sei tu, prima."),
            ("Dici di no più in fretta", ["A oggetti, a piani, a cose che non ti vanno.", "Senza spiegare per mezz'ora."], "Dire di no in fretta è una forma di rispetto, anche per te."),
            ("Chiedi il prezzo senza vergogna", ["E quanto costa davvero, non quanto costava.", "Nessuno lo trova maleducato."], "Chiedere non è tirchieria. È sapere cosa stai facendo."),
            ("Rimandi meno di prima", ["Non zero. Meno."], "I progressi veri sono noiosi e non si fotografano."),
            ("Compri meno e scegli meglio", ["Non per risparmio.", "Perché hai capito cosa usi davvero."], "Possedere meno cose, ma le giuste, è un traguardo, non una rinuncia."),
            ("Ti fidi del tuo giudizio", ["Guardi una cosa e sai se ti serve.", "Senza dover chiedere a qualcuno."], "Ci è voluto tempo. Vale più di quanto pensi."),
            ("Hai smesso di aspettare il momento giusto", ["Che non arriva.", "Cominci e basta."], "Il momento giusto è una scusa con un bel nome."),
        ],
    ),
    dict(
        title="Le 6 fasi di quando finalmente vendi quella cosa ferma da anni",
        hook="La 5 non te la aspetti e vale più dei soldi.",
        photos="market",
        cta=True,
        points=[
            ("L'esitazione", ["«Magari un giorno la uso.»", "Sono tre anni che lo dici."], "Tre anni di «magari» sono una risposta."),
            ("La foto", ["La parte che blocca tutti.", "Dieci minuti, luce della finestra, fatto."], "La barriera non è vendere: è cominciare."),
            ("Il prezzo", ["Guardi quanto chiedono gli altri per la stessa cosa oggi.", "Non quanto l'hai pagata tu."], "Il valore di una cosa lo decide il suo mercato, non il tuo ricordo."),
            ("Il primo messaggio", ["Arriva prima di quanto credi.", "Qualcuno la stava proprio cercando."], "Quello che per te era ingombro, per un altro era una ricerca salvata."),
            ("Lo spazio vuoto", ["Guardi il punto dove stava.", "Ti senti stranamente più leggero."], "Non erano i soldi. Era quella cosa che ti guardava ogni giorno."),
            ("La seconda", ["Finita la prima, vedi subito la prossima.", "Non si torna più indietro."], "Si comincia sempre da un oggetto solo."),
        ],
    ),
    dict(
        title="Cose che impari solo quando ti costringi a scegliere",
        hook="La 4 vale per gli armadi e per tutto il resto.",
        photos="stuff",
        points=[
            ("Scegliere stanca più che lavorare", ["Per questo rimandiamo.", "Non è pigrizia: è fatica vera."], "Decidere una volta costa meno che pensarci venti."),
            ("Il forse non è una risposta", ["È solo la decisione spostata più avanti.", "Con gli interessi."], "Ogni «forse» è un appuntamento con te stesso che salterai."),
            ("Meno opzioni, più pace", ["Quattro maglioni che ami battono venti che vanno bene.", "Lo sai già, la mattina."], "La scelta non è libertà quando è troppa."),
            ("Quello che tieni dice cosa sei adesso", ["Non cosa eri, non cosa speravi.", "Adesso."], "Guarda cosa ti circonda: è la versione più sincera di te."),
            ("Si può sbagliare", ["Darai via qualcosa che rimpiangerai.", "Una cosa su cento."], "Sbagliare ogni tanto costa molto meno che non decidere mai."),
            ("Diventa facile", ["Le prime dieci decisioni sono dure.", "Dalla ventesima in poi ci metti due secondi."], "Non serve essere decisi per cominciare. Si diventa decisi cominciando."),
        ],
    ),
]

CAPTION_SAVE = "Salvalo e mandalo a chi deve leggerlo."
CAPTION_SHARE = "Quanto vale davvero quello che hai in casa? getsowld.com"
HASHTAGS = "#usato #secondhand #casa #vitareale #decluttering #italia #risparmio"

# The last slide, only for topics with "cta": what Sowld actually does.
CTA = dict(
    title="Quanto vale davvero quello che stai guardando?",
    lines=["Sowld confronta un annuncio usato con annunci simili in vendita adesso e stima quanto vale."],
    small="Gratis, 15 controlli al mese. Le stime sono indicative.",
    url="getsowld.com",
)

SLOTS = 5  # carousels a day


def check_topic(topic: dict) -> list:
    """What is wrong with a topic written for a run, in words a writer can fix; empty if nothing."""
    errors = []

    def text(value, name, most):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name} is missing")
        elif len(value) > most:
            errors.append(f"{name} has {len(value)} characters, at most {most}: {value!r}")
        elif "—" in value or "–" in value:
            errors.append(f"{name} has a dash; use a colon, a full stop or a comma: {value!r}")

    text(topic.get("title"), "title", 90)
    text(topic.get("hook"), "hook", 120)
    points = topic.get("points")
    if not isinstance(points, list) or not 5 <= len(points) <= 8:
        errors.append("points must be a list of 5 to 8 points")
        points = []
    for i, point in enumerate(points, 1):
        if not (isinstance(point, (list, tuple)) and len(point) == 3 and isinstance(point[1], list)):
            errors.append(f"point {i} must be [heading, [line, line], closing line]")
            continue
        heading, lines, punch = point
        text(heading, f"point {i} heading", 52)
        if not 1 <= len(lines) <= 2:
            errors.append(f"point {i} needs 1 or 2 lines")
        for j, line in enumerate(lines, 1):
            text(line, f"point {i} line {j}", 95)
        text(punch, f"point {i} closing line", 75)
    if "hashtags" in topic and not (isinstance(topic["hashtags"], str) and topic["hashtags"].startswith("#") and len(topic["hashtags"]) <= 200):
        errors.append("hashtags must be one string of up to 200 characters, starting with #")
    if "cta" in topic and not isinstance(topic["cta"], bool):
        errors.append("cta must be true or false")
    if topic.get("photos", "stuff") not in PHOTO_SETS:
        errors.append(f"photos must be one of {sorted(PHOTO_SETS)}")
    return errors


def bank_topic(date: _dt.date, slot: int = 1) -> dict:
    """A written topic for a date and slot, when a run has none of its own."""
    n = (date - EPOCH).days * SLOTS + (slot - 1)
    return EVERYDAY[n % len(EVERYDAY)]


def carousel(date: _dt.date, slot: int = 1, topic: dict | None = None) -> dict:
    """The slides' content for a date and slot, one photo per slide (cover first), the same every time."""
    topic = topic or bank_topic(date, slot)
    rng = _random.Random(date.toordinal() * 10 + slot)
    pool = list(PHOTO_SETS.get(topic.get("photos", "stuff"), PHOTO_SETS["stuff"]))
    rng.shuffle(pool)
    need = 1 + len(topic["points"])
    picks = (pool * (need // len(pool) + 1))[:need]
    # The title opens the caption, so the next runs can see what was already posted.
    cta = bool(topic.get("cta"))
    tail = CAPTION_SHARE if cta else CAPTION_SAVE
    caption = f"{topic['title']}\n\n{topic['hook']}\n\n{tail}\n\n{topic.get('hashtags') or HASHTAGS}"
    count = len(topic["points"])
    numbers = list(range(count, 0, -1)) if topic.get("countdown") else list(range(1, count + 1))
    return dict(date=date.isoformat(), slot=slot, title=topic["title"], points=topic["points"],
                numbers=numbers, photos=picks, caption=caption, cta=cta)
