> Versione corrente: 3. Nei punti modificati, `REVISIONE_UI_14_PUNTI_V3.md` prevale sulle specifiche precedenti. Il totale resta di 20 slide.

> Nota di versione: la revisione successiva `REVISIONE_UI_18_PUNTI.md` prevale sui punti modificati. Ha richiesto una nuova slide sulla DSL: la versione corrente contiene 20 slide.

# ISTRUZIONI DEFINITIVE — CORREZIONE DELLA PRESENTAZIONE 5G

**Leggi questo documento PRIMA di modificare il progetto. Questa è una richiesta di implementazione, non un brainstorming grafico.**

## 0. Quello che voglio ottenere (da leggere prima di qualsiasi codice)

Ti fornirò lo ZIP **`Presentazione_5G_definitiva_19_slide.zip`**, che contiene una presentazione web in HTML, SVG, CSS e JavaScript con **19 slide già esistenti**. Devi modificarla, **non rifarla da zero**, **non convertirla in PowerPoint**, **non sostituirla con screenshot statici**.

La presentazione precedente è stata cambiata più volte seguendo specifiche troppo complesse e interpretate male. Il risultato è peggiorato: tante schede, gradienti e frecce, ma non si capisce cosa una slide debba spiegare. **Questa volta segui letteralmente il contenuto e la disposizione descritti sotto**. Non inventare dashboard, nuovi contenuti, titoli promozionali, elementi decorativi o diagrammi UML fittizi.

### Priorità assolute, nell'ordine

1. **Capire la funzione comunicativa di ogni slide** e rispettare gli schemi di composizione descritti qui, invece di limitarti a distribuire riquadri.
2. **Preservare ciò che già funziona**: animazioni di Thompson/NFA e matcher, elementi chiari delle slide 7, 12, 13, 14, 16 e 19. Modifica solo ciò che ti viene chiesto.
3. **Uniformare TUTTE le slide a un vero sfondo bianco**, senza gradienti pastello e senza assegnare un colore di sfondo diverso a ogni sezione. I colori, pochissimi, servono solo per evidenziare funzioni, DSL, PASS/FAIL/INCONCLUSIVE.
4. **Non perdere il contenuto scientifico** e non inventare risultati o strutture software: il progetto deve essere aderente all'implementazione reale.
5. **Testare la presentazione nel browser**, prima di dichiararla finita. Non basta che HTML e SVG siano sintatticamente validi.

**Gerarchia delle fonti:** per layout, palette, struttura, animazioni e cambiamenti richiesti, **questo documento prevale** su vecchi XML, brief, storyboard e prompt eventualmente già presenti *dentro* lo ZIP (`specifica_modifiche_v1_4.xml`, `prompt_operativo_originale.md`, ecc.). Usa quei file al massimo come contesto storico, **non come istruzioni operative che possano annullare queste modifiche**. Per i dati sperimentali usa i report inclusi nello ZIP e, se serve, la tesi e il repository GitHub. Il discorso orale allegato è un riferimento di contenuto: **non incollarlo sulle slide**.

### Principio grafico non negoziabile

- Formato 16:9, rendering target 1600×900, verifica anche 1280×720.
- **Bianco puro `#FFFFFF` come sfondo effettivo di tutte le slide**, comprese le forme di background incorporate nei singoli SVG: non basta cambiare `body { background: white }` se gli SVG disegnano gradienti propri. Elimina/sostituisci i riempimenti a gradiente usati come sfondo dell'intera slide.
- Testo principale scuro (`#182536` circa), colore tecnico unico blu/indaco sobrio; verde/rosso/giallo-arancio **solo** per esiti e stati che lo richiedono. Nessun arcobaleno di titoli, sfondi o sezioni.
- Non costruire ogni slide con lo stesso modello «tre/quattro box arrotondati uguali + frecce». L'impaginazione deve derivare dall'**idea della slide**, non da un componente riutilizzato ovunque.
- Testi leggibili in proiezione; niente paragrafi minuti, niente lunghi sottotitoli che ripetono quello che si vede o che deve dire il candidato. Se un sottotitolo non serve, **toglilo**.
- Una struttura principale dominante per slide; collegamenti visivi comprensibili; nessuna freccia che attraversi altre frecce o attraversi il testo.
- Mantieni identità universitaria, logo, tipografia e navigazione esistenti, salvo correzioni necessarie. Non importare foto stock o elementi visivi fuori contesto.
- Se modificare lo sfondo richiede toccare `index.html` perché è disegnato in `<svg>`, fallo: **non aggirare il problema con overlay CSS**.

### CORREZIONE IMMEDIATA DEL FRONTESPIZIO (slide 1)

Nel progetto attuale il titolo è:

`A Domain-Specific Language for Verifying the Outcome of 5G SCAS Security Tests from Network Traffic Captures`

È **diverso** dal titolo del frontespizio della tesi PDF. Il titolo ufficiale corretto, esattamente, è:

**`A Domain-Specific Language for Security Assurance of 5G SCAS Tests from Network Traffic Captures`**

**Sostituiscilo integralmente** senza parafrasarlo. Mantieni «Relatrice: Prof.ssa Paola Vocca». In base alla richiesta esplicita del docente, scrivi **«Correlatore: Dott. Francesco Mancini»** invece di «Prof. Francesco Mancini». Preserva ogni altro dato corretto.

---

# 1. DESCRIZIONE SLIDE PER SLIDE — 19 SLIDE ESISTENTI

Gli schemi ASCII seguenti mostrano **dove e in che ordine devono comparire gli elementi**, non la decorazione grafica finale. Una freccia `→` indica un rapporto esplicito tra elementi, **non** un obbligo di disegnare una linea lunga o una freccia che attraversa tutto lo schermo. Le slide vanno progettate per essere viste da una commissione a distanza.

## SLIDE 01 — Titolo [CORREGGERE POCO]

**Cosa fare:** sistema SOLO il titolo della tesi e il titolo del correlatore come descritto sopra; rendi lo sfondo bianco e assicurati che il titolo completo entri bene nella slide. **Non fare un redesign radicale del frontespizio**. La grafica esplicativa a destra è secondaria e non deve rubare spazio alla dicitura ufficiale.

**Non fare:** nuovo titolo, sottotitolo inventato, colori di sfondo, testo ridotto illeggibile per far entrare una frase sbagliata.

## SLIDE 02 — Il 5G Core è fatto di Network Functions [RIFARE IL MESSAGGIO, PRESERVARE LA RETE]

**Questa è UNA slide dedicata SOLO al contesto delle NF. NON nominare e NON mostrare le SCAS in questa slide.**

Messaggio per il pubblico: la rete 5G è composta da diverse **Network Functions** che cooperano tra loro. Le loro comunicazioni utilizzano **protocolli e procedure standardizzate** e queste funzioni/interazioni devono soddisfare requisiti di sicurezza.

**Impostazione visiva precisa:**

```text
TITOLO: «5G Core: Network Functions e interazioni»

        [Schema 5G ridotto e BEN GRANDE]

             AMF ───── AUSF ───── UDM
              │                      
             SMF ───── UPF

      linee/comunicazioni etichettate in modo sobrio:
            protocolli e procedure standardizzati

  IN BASSO: «Funzioni e interazioni devono rispettare
                         requisiti di sicurezza»
```

È uno schema **concettuale**, non è necessario inventare collegamenti di protocollo tra qualunque coppia di NF. Puoi riutilizzare la topologia della slide attuale rendendola più comprensibile. L'informazione principale è che le NF comunicano e sono soggette a requisiti di sicurezza. Niente box «SCAS del 3GPP», niente elenchi di precondizioni/azioni/risultati attesi qui: spostali nella slide 3.

**Nota di precisione:** non sostenere che le funzioni di rete siano state storicamente sempre software su hardware general-purpose. Se aggiungi una micro-nota sul passaggio dalle PNF alla realizzazione software, verifica la correttezza; non è indispensabile per il messaggio di questa slide.

## SLIDE 03 — Le SCAS: da testo human-readable a risultato da spiegare [RIPROGETTARE]

Questa slide introduce finalmente le **SCAS**, che descrivono requisiti/procedure di sicurezza in un formato pensato per essere letto e interpretato da persone. Vanno formalizzati i criteri se vogliamo automatizzare la valutazione. In una esecuzione possiamo avere una PCAP con molti messaggi e un verdetto, ma **PCAP + verdetto, da soli, non esplicitano quali evidenze e criteri hanno motivato l'esito**.

**Composizione:** un elemento principale deve sembrare una pagina/documento di specifica, non un generico rettangolo intitolato “Criteri”. Segue il risultato di un'esecuzione e il problema della motivazione.

```text
TITOLO: «Le SCAS descrivono come verificare la sicurezza»

┌──────────────────────┐     ┌─────────────────────────┐
│ SPECIFICA SCAS       │     │ ESECUZIONE DEL TEST     │
│ human-readable       │     │ PCAP: molti messaggi     │
│ • precondizioni      │ ──→ │ [righe di pacchetti]     │
│ • azioni             │     │ [righe di pacchetti]     │
│ • risultato atteso   │     │ [messaggi rilevanti?]    │
└──────────────────────┘     └───────────┬─────────────┘
                                         ↓
                              «PASS / FAIL / INCONCLUSIVE»
                                       +  ?
                          «Quali messaggi e criteri
                            giustificano l'esito?»

   PICCOLO, IN CHIUSURA: «Per automatizzare questa verifica,
                   i criteri SCAS vanno formalizzati in codice»
```

L'interrogativo deve essere visivamente il punto finale della slide, non l'ennesima etichetta in un box. Si deve capire che la cattura contiene **molti** messaggi e che solo alcuni servono al test. Mostra il documento come **testo human-readable** e la PCAP come **sequenza fitta di righe/eventi**, senza trascrivere intere SCAS illeggibili. Se mostri un esempio normativo, distingui una parafrasi da una citazione testuale.

**Non fare:** tre box identici «Criteri / PCAP / Verdetto»; anticipare nella stessa slide tutta la soluzione DSL; affermare che tutti i verdetti SCAS sono immotivati per definizione.

## SLIDE 04 — Da un verificatore per test a regole DSL + un motore comune [REDESIGN OBBLIGATORIO, ANIMAZIONE OBBLIGATORIA]

**È la slide più importante da rifare con precisione. La trasformazione deve essere TEMPORALE, non due sistemi contemporaneamente a video.**

All'apertura della slide deve essere visibile **SOLO IL MODELLO PRIMA**, cioè un programma/verificatore dedicato a ciascun test. L'utente preme «Avanti» o il comando di animazione, e **il primo modello SCOMPARE/VENE SOSTITUITO** dal secondo. Il secondo mostra molte regole DSL per test diversi che vengono interpretate dallo **stesso motore di verifica/pipeline**. Non deve mai restare a sinistra il vecchio modello mentre a destra compare il nuovo. La vecchia soluzione è da sostituire, non da confrontare staticamente.

**Stato A (PRIMA, prima dell'animazione):**

```text
        «Scrivere codice specifico per ogni test»

          TEST A  →  VERIFICATORE A
          TEST B  →  VERIFICATORE B
          TEST C  →  VERIFICATORE C

    [3 percorsi distinti; visivamente ripetitivi]
       «Logica duplicata, manutenzione difficile»
```

**Stato B (DOPO, sostituisce COMPLETAMENTE A):**

```text
       «Separare i criteri dalla logica software»

    REGOLA DSL A ─┐
    REGOLA DSL B ─┼──→ [UN UNICO MOTORE / PIPELINE]
    REGOLA DSL C ─┘                     ↓
                                 [ESITO + REPORT]

      La DSL descrive ENTRAMBI:
      (1) quali evidenze selezionare
      (2) quali criteri/proprietà verificare
```

Puoi usare dissolvenza/morph/transizione breve, ma **non deve creare doppioni né spostare/riscalare tutto in maniera confusa**. Se ci sono controlli «Spiega per passi / Vista completa», il primo passo mostra PRIMA, il secondo DOPO; dalla vista DOPO il successivo Avanti passa alla slide 5. La modalità vista completa può mostrare direttamente DOPO. **Verificare entrambi gli stati con due screenshot diversi.**

**Non dire:** la DSL traduce automaticamente le SCAS in linguaggio naturale. Le regole sono definite/formalizzate dal progettista; il sistema le interpreta. **Non aggiungere OpenAPI o altre analogie qui**: in questa revisione il modello PRIMA→DOPO è il messaggio principale richiesto dall'utente.

## SLIDE 05 — Architettura generale [RIDISEGNARE IL FLUSSO, NON SOLO CAMBIARE COLORI]

L'utente vuole la metafora semplice: **PCAP in alto → entra verticalmente nella PIPELINE → report sotto**. A sinistra, **DSL come input che raggiunge precisamente le fasi di selezione e verifica**. Il pubblico deve riconoscere la continuità con la slide 4: stesso motore, regole diverse.

**Composizione desiderata:**

```text
                              [ PCAP ]
                                 │
                                 ↓
              ┌────── PIPELINE DI VERIFICA ──────┐
              │                                  │
              │  [1 Estrazione · TShark]          │
              │              ↓                   │
              │  [2 Normalizzazione per protocollo]│
              │              ↓                   │
              │  [3 Resolver semantico, se serve] │
              │              ↓                   │
 [ REGOLE     │  [4 Selezione delle evidenze] ←───┤
   DSL ] ─────┼──→ [5 Verifica statica/temporale] │
              │              ↓                   │
              │  [6 Generazione del report]       │
              └──────────────┬───────────────────┘
                             ↓
                    [ REPORT + VERDETTO ]
```

Lo schema è **logico**, non un ordine di coordinate pixel obbligatorio. La DSL deve avere **due ingressi riconoscibili** verso *selezione* e *verifica*, anche se rappresentati da due connettori corti oppure da un nodo che si biforca. Se scegli di disporre alcuni stage orizzontalmente per sfruttare meglio i 16:9, va bene, MA il cammino principale PCAP→pipeline→report deve rimanere ovvio e senza ritorni ambigui.

Si possono aggiungere **piccole** etichette ai passaggi reali: `JSON EK` dopo TShark; `MessageEvent` dopo normalizzazione/risoluzione; `Match / collezioni` dopo selezione. NON servono un diagramma UML o classi astratte inventate. Non far sembrare che la DSL sia l'input di TShark o che scelga i protocolli. Il tipo di estrazione può dipendere dalla configurazione del test (senza mostrare necessariamente `tests.json`).

**Da evitare:** pipeline verticale alta pochi pixel con sei piccoli rettangoli indistinguibili; DSL a destra senza collegamenti chiari; report all'interno della PCAP; collegamenti intrecciati; ripetere sulla slide 5 tutta la slide 6.

## SLIDE 06 — Da PCAP a MessageEvent, poi a evidenze selezionate [RIFARE COMPLETAMENTE]

**La trasformazione dei dati deve essere il centro visivo**. Non devono essere solo parole in un diagramma. Mostra almeno un piccolo esempio del formato PRIMA e DOPO.

**Due fasi nettamente distinguibili:**

1. **Elaborazione per protocollo** (riusabile fra test): PCAP → TShark → record JSON EK con campi protocollari → normalizzatori NAS/HTTP/2 [PFCP presente ma attenuato come terza possibilità] → eventuale resolver semantico → eventi strutturati `MessageEvent`.
2. **Selezione per il test**: l'insieme dei `MessageEvent` è esaminato usando le **regole DSL** → soltanto gli eventi rilevanti diventano **evidenze selezionate**.

**Layout suggerito:**

```text
TITOLO: «Dal traffico grezzo alle evidenze del test»

[PCAP: tanti frame] → [TShark] → [JSON EK: campi protocollari]
                                          │
                                          ↓
                           ┌────────────────────────┐
                           │ NORMALIZZATORI         │
                           │ NAS    HTTP/2   PFCP*  │
                           └───────────┬────────────┘
                                       ↓
                             [Resolver, se serve]
                                       ↓
                         [MessageEvent · formato comune]
                                   │
                           [Selezione DSL]
                                   ↓
                           [EVIDENZE SELEZIONATE]

  * PFCP attenuato SOLO come esempio di sorgente non usata
    nel caso illustrativo; non è «non supportato».
```

Mostra un riquadro piccolo di **record TShark JSON** (campi grezzi/protocollari) e, vicino, un `MessageEvent` di dimensione leggibile con campi concettualmente veri: `frame_number`, `timestamp`, `protocol`, `kind`, `fields`. Questi sono campi REALI del `MessageEvent` nel repository. Puoi rappresentare i dati con notazione **JSON-like per facilitare la lettura**, ma non affermare che l'oggetto Python sia un file JSON. Il `MessageEvent` del codice è una `dataclass`.

**Nota di precisione:** TShark produce record strutturati con `-T ek` (e filtri configurabili, es. `-Y`); i normalizzatori per NAS, HTTP/2 e PFCP sono moduli/funzioni specifici del protocollo, **NON** un'ereditarietà UML artificiale. Il resolver semantico interviene quando necessario. La DSL interviene **dopo** la normalizzazione, nella scelta delle evidenze del singolo test.

**Non fare:** frecce dalla DSL che tornano indietro ai normalizzatori, una colonna infinita di 9 box minuscoli, protocolli NAS/HTTP2/PFCP ingranditi più del `MessageEvent`, scambiare eventi normalizzati con eventi già selezionati, far sembrare `PFCP` disabilitato in tutta l'applicazione.

## SLIDE 07 — Dalle evidenze al verdetto e al report [PRESERVARE]

La composizione attuale è sostanzialmente approvata. Mantieni il report come esempio visivo, la distinzione tra verifica statica e temporale e gli esiti `PASS`, `FAIL`, `INCONCLUSIVE`, insieme a riferimenti a frame, criteri e hash del PCAP quando mostrati.

**Fare solo:** sfondo bianco; pulizia marginale delle scritte; assicurare che il JSON del report sia leggibile senza diventare un muro di testo. Evita cambiamenti sostanziali alla logica della slide.

## SLIDE 08 — La DSL spiegata con UNA SOLA regola, non due [RIFARE E SEMPLIFICARE]

Il pubblico non deve ricevere contemporaneamente due regole intere e una legenda piena di termini. Mostra **UNA SOLA regola concreta**, chiaramente spezzata visivamente tra:

- **SELEZIONE**: quali eventi trovare;
- **VERIFICA**: che condizione controllare sui campi dei messaggi trovati.

**Esempio consigliato, REALE nel repository (NRF):**

```dsl
SEQUENCE {
    nrf.discovery.request AS request
    nrf.discovery.response AS response
}

REQUIRE response.status == 403
```

La regola descrive un caso concreto: **una discovery non autorizzata dovrebbe essere rifiutata con HTTP 403**. Non indicare `PASS` per la cattura baseline NRF: quella baseline è **FAIL**, perché non soddisfa l'atteso. Qui mostri soltanto cosa la regola *richiede*, non l'esito osservato.

**Composizione:**

```text
TITOLO: «La DSL: selezionare gli eventi e verificarli»

   BREVE FRASE UMANA (sopra, solo 1 riga):
   «Cerco richiesta e risposta, poi controllo HTTP 403»

   ┌──────────── UNICA REGOLA DSL ────────────┐
   │ [SELEZIONE]                             │
   │ SEQUENCE { ... request ... response }   │
   │                                         │
   │ [VERIFICA]                              │
   │ REQUIRE response.status == 403          │
   └─────────────────────────────────────────┘

   DUE CALLOUT CORTI: SEQUENCE = individua eventi
                       REQUIRE  = verifica proprietà

   STRISCIA SECONDARIA, PICCOLA MA LEGGIBILE:
      «Altri costrutti: OPTIONAL · COLLECT · IF · MFOTL»
```

Le due parti devono essere **due aree della stessa regola**, non due regole separate. Evita legende lunghe. A voce si potranno spiegare `OPTIONAL` e `COLLECT` e poi vedere l'`OPTIONAL` nell'automa della slide 9. Il codice deve avere caratteri grandi abbastanza per essere letto in aula. Non inventare una grammatica o codice che sembri autentico ma non lo sia.

## SLIDE 09 — Dalla regola all'automa di Thompson [NON TOCCARE LA LOGICA]

Preserva l'esempio con `A`, `OPTIONAL B`, `C`, gli atom, le transizioni epsilon e l'animazione progressiva **già funzionante**. Cambia soltanto background in bianco e, se serve, qualche micro-misura per la leggibilità. Non ricostruire né reinventare il grafo. Mantieni «Spiega per passi» e «Vista completa» con navigazione coerente.

## SLIDE 10 — Matcher sulla sequenza A X A B X C [NON TOCCARE LA LOGICA]

Preserva il riconoscimento e l'animazione. Sequenza osservata `A X A B X C` e risultato `A(3)`, `B(4)`, `C(6)`; 3, 4 e 6 sono **posizioni nell'esempio, non numeri di frame PCAP**. Non eliminare gli `X` né cambiare la logica del riavvio del candidato. Solo sfondo bianco e piccole migliorie di leggibilità.

## SLIDE 11 — Come è fatto e a cosa serve il BindingContext [RIFARE IN MODO PIÙ CONCRETO]

Nella versione attuale si ripete l'esempio didattico della slide 10 (A3, B4, C6) e si mette una freccia verso `BindingContext`, ma **non si vede bene che cosa contenga e perché sia utile**. Qui l'utente vuole mettere al centro la struttura del dato, non ripetere il match.

**Messaggio:** il **Matcher produce un `Match`**, nel quale gli alias indicano gli eventi riconosciuti. Dal `Match` si ottiene un **`BindingContext`**: per le sequenze è una mappa alias → oggetto `MessageEvent`; negli altri percorsi può contenere anche liste di `MessageEvent` o dati derivati. Il verificatore può quindi accedere ai campi tramite gli alias, senza ripercorrere la PCAP.

```text
             [MATCHER]
                 ↓
              [MATCH]
                 ↓
         ┌── BINDING CONTEXT ─────────────────┐
         │ alias «a» → MessageEvent {          │
         │     frame_number, protocol, kind,  │
         │     timestamp, fields: {...}       │
         │ }                                  │
         │ alias «b» → MessageEvent { ... }    │
         └────────────────────┬───────────────┘
                              ↓
                ESEMPIO ACCESSO AI CAMPI
                a.fields["nome_campo"]
                      ↓
             [VERIFICATORE STATICO]
```

Se utile, usa il micro-esempio `a.fields["rand"]` **solo se l'evento illustrato è del tipo corretto e ha davvero quel campo**; altrimenti usa genericamente `fields["campo"]`. I campi reali della dataclass `MessageEvent` sono `frame_number`, `timestamp`, `protocol`, `kind`, e opzionali `src`, `dst`, `message_type`, `related_frames`, `correlation`, `fields`.

**Molto importante:** non dire «il BindingContext è in formato JSON». È una struttura Python (`BindingContext.bindings`) i cui valori, secondo il percorso, possono essere `MessageEvent`, liste di `MessageEvent` o dizionari. **La raffigurazione può essere JSON-like solo per semplicità visiva**. La notazione della DSL è del tipo `authentication_request.rand`: il resolver raggiunge il valore nel `fields` del relativo evento, non bisogna scrivere `a.fields[...]` come se fosse obbligatoriamente sintassi DSL. Si può mantenere un richiamo molto piccolo `A(3), B(4), C(6)` per continuità, ma non deve occupare la maggior parte della slide. Deve prevalere un esempio **interno alla struttura** e la possibilità di leggere i campi con un alias.

## SLIDE 12 — Motore di verifica [PRESERVARE]

L'impostazione attuale funziona: verifica statica e temporale conducono al risultato, con `PASS/FAIL/INCONCLUSIVE`. Eventuali ritocchi minimi, sfondo bianco.

La verifica temporale usa **formule MFOTL** e il motore esterno **MonPoly**; non sono la stessa cosa. Non introdurre un nuovo diagramma enorme: l'integrazione del verificatore esterno può essere spiegata anche a voce. Mantieni la modularità percepibile.

## SLIDE 13 — AMF Synchronization Failure, Case B [PRESERVARE, MIGLIORARE SOLO IL TIMER]

La composizione attuale piace: codice/controlli da un lato, `PASS` chiaro, riquadro temporale. **Non rifarla**. Concentrati soltanto sul diagramma T3520 per renderlo più intuitivo a chi non ha esperienza.

**Dati da NON cambiare:** timer **15 s**; evento di *Synchronization Failure* al **frame 358**; nuova *Authentication Request* al **frame 606**; intervallo osservato **25,018 s**; i **quattro controlli statici PASS** e la verifica temporale PASS portano a verdetto complessivo **PASS**.

**Timer desiderato:** una linea/asse temporale semplice, marcatura evidente `0 s → 15 s` come finestra in cui una nuova richiesta **non deve comparire**, segnale `25,018 s` oltre la soglia. Evita 4–5 colori per timer e frecce. Il pubblico deve capire con un colpo d'occhio **25 > 15, quindi PASS**.

## SLIDE 14 — UPF TEID Uniqueness [PRESERVARE]

Questa slide va bene. Mantieni `COLLECT`, `REQUIRE UNIQUE`, la tabella delle **5 risposte PFCP / 10 coppie (TEID, IPv4)**, nessun duplicato, `PASS`. Solo sfondo bianco ed eventuale messa a punto del testo. Non cambiare dati, tabella, esempio o gerarchia.

## SLIDE 15 — AMF RES*: quattro varianti [RIFARE IN MATRICE 2×2 PULITA]

La matrice attuale è troppo verbosa e non convince. NON devi trasformarla in quattro schede dense di testo. **Deve essere una vera griglia 2×2, compatta e immediatamente leggibile**, con un asse che distingue il percorso di identificazione e uno che distingue la sorgente del fallimento.

```text
TITOLO: «AMF RES*: quattro casi, una regola DSL»

                  ORIGINE DEL FALLIMENTO
                 AMF locale       AUSF
              ┌──────────────┬──────────────┐
SUCI diretto   │ CASE A       │ CASE C       │
              │    PASS      │    PASS      │
              ├──────────────┼──────────────┤
GUTI → SUCI    │ CASE B       │ CASE D       │
              │    PASS      │    PASS      │
              └──────────────┴──────────────┘

      [un piccolo frammento/nota]
      «OPTIONAL = parti della procedura possibili»
      «IF = criteri scelti dalla configurazione del caso»
```

**Questa associazione NON va cambiata:** A=(SUCI diretto, AMF locale), B=(GUTI→SUCI, AMF locale), C=(SUCI diretto, AUSF), D=(GUTI→SUCI, AUSF). I quattro casi hanno tutti un match completo e verdetto PASS.

Riduci drasticamente scritte interne alle celle: al massimo `Case A` + `PASS` e, se proprio serve, un piccolo contatore; **non ripetere «1 match completo» quattro volte**, non mettere `7 PASS 2 SKIPPED` ecc. in grande. Gli `SKIPPED` possono essere spiegati **a voce**. L'estratto DSL non deve occupare metà schermo: 2 microetichette `OPTIONAL` e `IF` sotto/accanto alla matrice sono sufficienti.

**Correttezza tecnica:** i blocchi `IF` fanno riferimento alla **configurazione del caso** (`case.identity_path`, `case.failure_source`), non vengono automaticamente attivati dalla presenza di un evento `OPTIONAL`. Non dire che l'algoritmo “indovina” il caso dai soli eventi.

## SLIDE 16 — Risultati baseline [PRESERVARE]

La tabella è corretta e va lasciata sostanzialmente com'è. **10/10** indica che i dieci risultati osservati coincidono con i dieci **attesi**; **9 PASS e 1 FAIL NRF atteso**, NON dieci PASS. Cambia solo lo sfondo e dettagli minori di leggibilità.

## SLIDE 17 — Il PROCESSO di mutation testing [RIFARE RADICALMENTE: UNA PIPELINE E UN CICLO]

La versione consegnata è sbagliata VISIVAMENTE: frecce che non guidano, riquadri disseminati e perdita dell'idea fondamentale. L'utente vuole **una composizione simile alla slide 5** (la stessa metafora della pipeline), con **il motore di mutazione ESTERNO che crea una PCAP modificata, la quale rientra nella STESSA pipeline**.

**Messaggio unico:** due elaborazioni successive della **stessa pipeline con la stessa DSL**; cambia la PCAP. La prima produce il report baseline. Un mutatore esterno usa **PCAP originale + report baseline** per individuare i frame pertinenti e generare **PCAP mutata**. La PCAP mutata viene reinserita come input nella medesima pipeline, che produce un report mutato. Il confronto è tra risultati osservati e attesi.

**Metafora visiva obbligatoria, poche linee pulite:**

```text
                         [ PCAP ORIGINALE ]
                                 │
                                 ↓  (1. baseline)
                        ┌──────────────────┐
  [ STESSE REGOLE DSL ] →│    PIPELINE      │────→ [ REPORT BASELINE ]
                        │    DI VERIFICA   │           │
                        └────────↑─────────┘           │ frame/evidenze
                                 │                      │
                                 │ (2. riesecuzione)    │
                         [ PCAP MUTATA ]               │
                                 ↑                      │
                        ┌──────────────────┐           │
  PCAP ORIGINALE ───────→│ MUTATORE ESTERNO │←──────────┘
                        └──────────────────┘

          [REPORT MUTATO]  →  [CONFRONTO CON ATTESI]
```

Il diagramma ASCII esprime le **dipendenze**, ma in layout 16:9 disponi con criterio report e confronto per **non incrociare i connettori**. Se necessario organizza visivamente la zona in tre colonne: **a sinistra ingressi + mutatore**, **al centro un'unica pipeline**, **a destra report baseline, report mutato e confronto**. Puoi animare due brevi passaggi: (1) baseline, (2) mutazione e riesecuzione. **Non disegnare una seconda pipeline** e non disegnare un motore di mutazione dentro quella principale.

**Dati/interfacce tecnicamente corretti:** il mutatore offline usa la PCAP originale e il report baseline contenente i frame di evidenza. Non riceve le regole DSL come programma di mutazione, e non è un componente che la pipeline chiama automaticamente a ogni esecuzione. `FAIL→PASS` può essere una mutazione attesa (esempio NRF), quindi **non dire che le mutazioni devono necessariamente trasformare PASS in FAIL**.

## SLIDE 18 — Risultati mutation testing [RIFARE CON MENO COLORI, PIÙ ORDINE]

**Non fare tre palette diverse o cartoncini colorati per le categorie.** Usa background bianco, testo scuro e colori esclusivamente per gli esiti. Deve risultare immediata questa idea: **15/15 esperimenti con verdetto osservato coerente con l'atteso**; seguono due esempi di ciò che il verificatore distingue.

**Composizione raccomandata:**

```text
TITOLO: «Mutation testing: risultati»

               15/15
    «esiti osservati coerenti con gli attesi»

  ┌────────────── AMF ──────────────┐ ┌────── UPF ──────────────┐
  │  Mutazione   Stat.   Temp.     │ │ TEID duplicato → FAIL   │
  │  statica      FAIL    PASS      │ │ Evidenze assenti        │
  │  temporale    PASS    FAIL      │ │            → INCONCLUSIVE│
  │  combinata    FAIL    FAIL      │ └─────────────────────────┘
  └─────────────────────────────────┘

   «Rilevare una violazione ≠ non avere dati sufficienti»
```

Per l'AMF puoi mantenere anche la colonna di verdict complessivo (`FAIL` in tutti e tre), ma la tabella deve rimanere semplice e grande. Per l'UPF devono apparire distinti i due risultati. `15/15` è **concordanza atteso/osservato**, non numero di PASS, né prova di correttezza universale. Puoi aggiungere in una micro-nota, **se verificato dai report**: 13 mutazioni con `FAIL` atteso, 1 `PASS`, 1 `INCONCLUSIVE`; questa informazione NON deve competere visivamente con gli esperimenti mostrati.

Il relatore aveva suggerito TP/TN/FP/FN. **Non mettere una matrice di confusione confusa e non definita soltanto per rispettare una vecchia richiesta**. Se scegli di includerla, prima devi indicare classe positiva («violazione»), unità di osservazione e gestione della classe `INCONCLUSIVE`. Preferisco nel corpo principale della slide 15/15 ed esempi chiarissimi; le altre metriche possono essere in una nota/discussione separata verificata. Se vuoi modificarne l'enfasi, chiedi all'utente **solo dopo** aver implementato questa versione semplice.

## SLIDE 19 — Conclusione [PRESERVARE]

Non trasformare la slide conclusiva in un elenco di tutte le sezioni o nel testo del discorso. Tieni l'impostazione essenziale attuale e lo sfondo bianco. È sufficiente una frase forte, con «Grazie per l'attenzione» discreto. Il discorso conclusivo dell'utente **non deve essere riscritto sulle slide**. Non creare un titolo diverso da quello della tesi in slide 1: la frase conclusiva della 19 è un messaggio, non il titolo ufficiale.

---

# 2. COSA NON DEVE SUCCEDERE DI NUOVO

Questa sezione fa parte dei requisiti, non è un suggerimento stilistico.

1. **Non** implementare un elenco di concetti come quattro riquadri indipendenti se l'utente richiede una trasformazione o un flusso.
2. **Non** lasciare visibili contemporaneamente il PRIMA e il DOPO nella slide 4, nemmeno in vista completa. Se si vede DOPO, PRIMA non c'è più.
3. **Non** mettere SCAS nella slide 2; le SCAS arrivano **alla slide 3**.
4. **Non** avere gradienti azzurrini, verdi, lavanda, sabbia a seconda delle sezioni. **Sfondo bianco su tutte le 19 slide**.
5. **Non** cambiare le slide 9, 10, 13, 14 e 16 solo per “uniformarle al nuovo stile”. Il bianco e piccoli ritocchi bastano.
6. **Non** disegnare UML di classi astratte che non esistono nel repository. NAS, HTTP/2, PFCP hanno normalizzatori specifici; `MessageEvent` è una dataclass comune.
7. **Non** chiamare la DSL un convertitore automatico da linguaggio naturale SCAS. Le condizioni sono interpretate e formalizzate da chi progetta il test.
8. **Non** chiamare MFOTL un verificatore esterno: è la logica; **MonPoly** è lo strumento esterno integrato.
9. **Non** descrivere i numeri degli esempi didattici `3,4,6` come frame di catture reali.
10. **Non** presentare i `SKIPPED` come errori; sono condizioni non applicabili alla configurazione del caso.
11. **Non** confondere `FAIL` e `INCONCLUSIVE`, né «15/15 risultati attesi» con «15 PASS».
12. **Non** usare il titolo della slide 1 inventato dal vecchio progetto: copia quello ufficiale esatto.
13. **Non** consegnare soltanto un piano, SVG di esempio, mockup non integrati o il testo di un prompt. Devi modificare il progetto reale e consegnarlo in ZIP.

---

# 3. ANIMAZIONI E NAVIGAZIONE: COSA PRESERVARE

- Slide 4: **vera sostituzione** A→B, come spiegato, con uno stato iniziale, uno stato successivo e pulsanti coerenti. Screenshot di ENTRAMBI obbligatori.
- Slide 9: Thompson/NFA, passaggi e transizioni epsilon corretti, senza alterare il contenuto.
- Slide 10: matcher, `A X A B X C`, restart e riconoscimento finali corretti.
- Slide 11: se scegli un'animazione, usala soltanto per rivelare `Match`→`BindingContext`→accesso ai campi, non per riesporre l'intero matcher.
- Il controllo «Avanti» percorre i passi quando si usa «Spiega per passi» e, dopo l'ultimo, passa realmente alla slide seguente (senza dover premere due volte inutilmente). La vista completa deve permettere di passare direttamente alla slide successiva.
- La navigazione fra slide, la barra di avanzamento, i comandi tastiera e la possibilità di andare a una slide precisa non devono regredire.
- Niente animazioni decorative continue, lampeggiamenti o dissolvenze che nascondono contenuto durante l'orale.

---

# 4. COME DEVI LAVORARE (PER NON SPRECARE TEMPO/TOKEN)

**Non voglio un'altra conversazione di progettazione infinita.** Questo documento contiene le decisioni. Procedi a implementare il progetto, senza iniziare chiedendo se desidero una palette di colore, se posso mantenere il bianco o se devo mettere i box più piccoli. Ho già risposto a questi punti.

1. Apri lo ZIP delle 19 slide e modifica **quei file** (`index.html`, `style.css`, `interactive-slides.js`, `script.js` se necessario). Non rigenerare una presentazione nuova da zero.
2. Correggi per prime slide **1, 2, 3, 4, 5, 6, 8, 11, 15, 17, 18**; per le altre applica SOLO i cambiamenti minimi richiesti. Questo riduce le regressioni e la produzione di codice inutile.
3. Rendi white background **globalmente e realmente** in tutti gli SVG, senza trasformare ogni slide in uno schema completamente diverso.
4. **Apri la presentazione nel browser** alla dimensione target, genera screenshot di tutte le slide e ispezionali. Controlla in particolare quelli dei due stati della 4, della pipeline della 5 e della 17, della trasformazione della 6, della matrice 15 e della tabella 18.
5. Correggi sovrapposizioni, tagli, testi troppo piccoli, allineamenti, connettori inutili, errori di ordine di lettura. Non considerare il lavoro finito finché ci sono tali problemi.
6. Esegui un test di navigazione completo slide 1→19; verifica `Spiega per passi`, `Vista completa`, indietro, avanti, restart, stampa/esportazione se presenti.
7. Non modificare i dati sperimentali per farli stare meglio nella slide. Se trovi un conflitto con il repository/rapporti, segnalalo esplicitamente nel changelog e non inventare un dato alternativo.
8. Consegna **uno ZIP completo e apribile localmente**, un contact sheet/screenshot delle 19 slide, **2 screenshot della slide 4 (PRIMA e DOPO)**, un changelog piccolo che elenca che cosa hai effettivamente modificato. Verifica prima di consegnare che lo ZIP contenga tutti i file necessari.

### Requisiti di accettazione rapidi (devi poter dire SÌ a tutti)

- [ ] 19 slide, tutte con sfondo bianco vero.
- [ ] Titolo tesi di slide 1 identico al PDF; correlatore «Dott. Francesco Mancini».
- [ ] Slide 2: NF/protocolli/requisiti, **nessuna SCAS**.
- [ ] Slide 3: documento SCAS leggibile da persone → PCAP di molti eventi → verdetto senza collegamento esplicito ai criteri.
- [ ] Slide 4: **PRIMA visibile da solo**, poi **DOPO visibile da solo**; DSL con due responsabilità chiare.
- [ ] Slide 5: PCAP SOPRA, pipeline al CENTRO, report SOTTO, DSL che entra in selezione e verifica.
- [ ] Slide 6: record JSON EK → normalizzazione NAS/HTTP2 → `MessageEvent` → selezione guidata DSL → evidenze selezionate. PFCP attenuato come esempio, non dichiarato unsupported.
- [ ] Slide 8: **una sola** regola reale con selezione e verifica evidenziate, altri operatori secondari.
- [ ] Slide 9–10: automa e matcher non compromessi.
- [ ] Slide 11: interno `BindingContext` e campi reali di `MessageEvent`, non solo il match ripetuto.
- [ ] Slide 13: timeline con 15 s / 25,018 s chiara, verdetto PASS.
- [ ] Slide 14: UPF tabella ed esito conservati.
- [ ] Slide 15: matrice **2×2** A/C sopra, B/D sotto; poche scritte e niente SKIPPED in grande.
- [ ] Slide 16: baseline 10/10 attesi=osservati, 9 PASS e 1 FAIL atteso.
- [ ] Slide 17: **UN SOLO** blocco pipeline; mutatore esterno, PCAP mutata che rientra, report baseline e mutato/confronto.
- [ ] Slide 18: prevale 15/15, matrice AMF chiara, UPF FAIL vs INCONCLUSIVE, pochi colori.
- [ ] Slide 19: conclusione minimale, non il discorso trascritto.
- [ ] Browser: nessun testo sovrapposto/tagliato; navigazione e animazioni funzionanti.

**Se non riesci a rispettare uno dei vincoli, non barrare la casella e non scrivere che è stato completato. Indica il problema specifico.**

---

# 5. MESSAGGIO PRINCIPALE DA CAPIRE

La tesi **non** automatizza la traduzione di una SCAS in linguaggio naturale, e **non** inventa test: permette di **specificare in una DSL quali evidenze di rete selezionare e quali proprietà verificare**, poi una pipeline riutilizzabile analizza i PCAP, seleziona gli eventi e genera risultati tracciabili. Il pubblico deve percepire questa differenza chiaramente, senza dover leggere dozzine di riquadri. **Le slide sono un supporto al discorso, non la trascrizione del discorso.**
