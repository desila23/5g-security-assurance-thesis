# Dove modificare tutte le scritte

Questa guida corrisponde alla revisione 14 del pacchetto. Le righe sono quelle dei file consegnati. Dopo una modifica possono spostarsi: usa anche gli ID e i commenti indicati qui.

## Da quale file partire

| Cosa vuoi cambiare | File | Come trovarlo |
|---|---|---|
| Sottotitolo di una slide | `index.html` | Cerca `SOTTOTITOLO SLIDE 10` (cambia il numero) o `slide-subtitle-10`. |
| Spiegazione di un passo dell’automa | `interactive-slides.js` | `constructionSteps`: modifica il valore `label`. |
| Spiegazione di un passo del matcher | `interactive-slides.js` | `matcherSteps`: modifica il valore `label`. |
| Testi dei pulsanti dei passi e della vista completa | `interactive-slides.js` | `uiText`. |
| Titoli, diagrammi, tabelle, legenda, codice DSL o JSON | `index.html` | Mappa completa delle scritte in fondo a questa guida. |
| Note del relatore | `index.html` | `<template class="speaker-note">` della slide. |
| Navigazione, indice e finestre | `index.html` | Tabella dei testi dell’interfaccia. |
| Messaggi aggiornati da JavaScript | `script.js` | Tabella dei testi dinamici. |
| Font, colori e posizione della barra dei passi | `style.css` | Tabella di stile qui sotto. |

## Tutti i sottotitoli

Ogni sottotitolo ha un commento nell’HTML e un gruppo con ID stabile. Modifica il testo tra `<text>` e `</text>`. Ogni riga qui sotto corrisponde a una riga del sottotitolo. La copertina e la frase conclusiva sono incluse.

| Slide | Cerca nell’HTML | Riga | Testo attuale |
|---|---|---|---|
| 01 | `slide-subtitle-1` | 76 | Un linguaggio per descrivere i criteri SCAS |
| 01 | `slide-subtitle-1` | 77 | e verificarli sui messaggi osservati nelle catture di rete. |
| 02 | `slide-subtitle-2` | 205 | Le Network Functions cooperano attraverso scambi che devono rispettare requisiti di sicurezza. |
| 02 | `slide-subtitle-2` | 206 | Le SCAS descrivono le condizioni della prova, le azioni e il comportamento atteso. |
| 03 | `slide-subtitle-3` | 320 | La cattura contiene i messaggi della prova, ma non esplicita quali soddisfano i criteri SCAS. |
| 03 | `slide-subtitle-3` | 321 | Per motivare il verdetto servono criteri valutati, valori osservati e frame di evidenza. |
| 04 | `slide-subtitle-4` | 373 | I criteri cambiano da test a test: la loro descrizione deve restare separata dal software che li valuta. |
| 05 | `slide-subtitle-5` | 477 | Il progettista formalizza nella DSL quali evidenze cercare e quali proprietà verificare. |
| 05 | `slide-subtitle-5` | 478 | La pipeline interpreta quelle regole e produce un esito documentato sui messaggi osservati. |
| 06 | `slide-subtitle-6` | 564 | PCAP e DSL guidano la verifica; tests.json descrive il test e le sorgenti da usare. |
| 07 | `slide-subtitle-7` | 721 | Normalizzatore e resolver semantico organizzano gli eventi per protocollo e ne completano i campi. |
| 08 | `slide-subtitle-8` | 840 | Il report rende ricostruibile la verifica: documenta i criteri valutati e le evidenze che motivano il verdetto. |
| 09 | `slide-subtitle-9` | 969 | La regola descrive il comportamento atteso e le informazioni da confrontare. |
| 09 | `slide-subtitle-9` | 970 | Sequenze e collezioni individuano l’evidenza; i criteri statici e temporali ne valutano le proprietà. |
| 10 | `slide-subtitle-10` | 1146 | La sequenza diventa un NFA: gli Atom riconoscono gli eventi e le transizioni ε gestiscono i collegamenti. |
| 11 | `slide-subtitle-11` | 1339 | Il matcher considera i possibili inizi della sequenza; qui riconosce A(3), B(4), C(6). |
| 12 | `slide-subtitle-12` | 1470 | Il binding context rende disponibili alle regole di verifica gli eventi individuati durante la selezione. |
| 13 | `slide-subtitle-13` | 1573 | I verifier applicano i criteri della DSL alle evidenze selezionate. |
| 14 | `slide-subtitle-14` | 1701 | Il caso AMF combina controlli sui dati della risincronizzazione e sul rispetto del timer T3520. |
| 14 | `slide-subtitle-14` | 1702 | La sequenza riconosciuta e i timestamp della cattura motivano il verdetto PASS. |
| 15 | `slide-subtitle-15` | 1806 | COLLECT raccoglie le risposte PFCP; REQUIRE UNIQUE controlla le coppie F-TEID {teid, ipv4}. |
| 16 | `slide-subtitle-16` | 1920 | Una sola regola rappresenta quattro varianti della procedura e applica i criteri pertinenti a ciascun caso. |
| 17 | `slide-subtitle-17` | 1991 | Il confronto con gli esiti attesi verifica la risposta della pipeline sulle dieci catture originali. |
| 18 | `slide-subtitle-18` | 2127 | Modificando le evidenze nel PCAP, si valuta la risposta della pipeline mantenendo invariate le regole. |
| 19 | `slide-subtitle-19` | 2222 | Le mutazioni distinguono una proprietà violata da un caso in cui mancano le evidenze per valutarla. |
| 20 | `slide-subtitle-20` | 2291 | Casi studiati e mutazioni considerate: verifica tracciabile entro il perimetro del linguaggio. |

## Slide 10: Costruzione dell’automa

File: `interactive-slides.js`. Cerca `TESTI PASSI SLIDE 10` o `constructionSteps`. Nell’HTML, il commento `TESTI PASSI SLIDE 10` vicino ai pulsanti indica lo stesso file e intervallo di righe.

| Passo visualizzato | Riga in `interactive-slides.js` | Testo da modificare: `label` |
|---|---|---|
| 1/8 | 31 | La regola descrive A, B facoltativo e C. |
| 2/8 | 32 | event.a AS a → Atom(event.a). |
| 3/8 | 33 | event.b AS b → Atom(event.b). |
| 4/8 | 34 | event.c AS c → Atom(event.c). |
| 5/8 | 35 | Dispongo i tre atomi nell’NFA; q5 diventa finale. |
| 6/8 | 36 | Aggiungo ε tra A e B e tra B e C. |
| 7/8 | 37 | Aggiungo ε che salta B: è il gruppo OPTIONAL. |
| 8/8 | 38 | L’automa accetta A → B → C oppure A → C. |

Cambia solo la frase in `label`. Lascia invariati `visible`, `bindings`, `atoms`, `cursor`, `current`, `restart` e `restarted`: controllano ciò che compare e si accende. Il numero 1/8 è calcolato dal programma.

Esempio:

```js
{ label: 'Qui scrivo la mia spiegazione.', visible: ['atom-a'], current: 'a' },
```

## Slide 11: Riconoscimento e riavvio del matcher

File: `interactive-slides.js`. Cerca `TESTI PASSI SLIDE 11` o `matcherSteps`. Nell’HTML, il commento `TESTI PASSI SLIDE 11` vicino ai pulsanti indica lo stesso file e intervallo di righe.

| Passo visualizzato | Riga in `interactive-slides.js` | Testo da modificare: `label` |
|---|---|---|
| 1/8 | 42 | La regola attende un evento A. |
| 2/8 | 43 | Riconosco A(1): creo a(1) e accendo Atom A. |
| 3/8 | 44 | X(2) non contribuisce al match: continuo a cercare. |
| 4/8 | 45 | Qui A(3) non è consumabile: chiudo il primo candidato e spengo Atom A. |
| 5/8 | 46 | Riconosco A(3): creo a(3) e riaccendo Atom A. |
| 6/8 | 47 | Riconosco B(4): creo b(4) e accendo Atom B. |
| 7/8 | 48 | Ignoro X(5); il candidato continua da A(3), B(4). |
| 8/8 | 49 | Riconosco C(6): creo c(6). Match A(3), B(4), C(6). |

## Pulsanti e messaggio della vista completa

Questi testi sono in `interactive-slides.js`, dentro `uiText`. Cambia il valore a destra; conserva la chiave a sinistra.

| Campo | Riga in `interactive-slides.js` | Testo attuale |
|---|---|---|
| `start` | 20 | Spiega per passi |
| `full` | 21 | Vista completa |
| `previous` | 22 | Indietro |
| `next` | 23 | Avanti |
| `reset` | 24 | Ricomincia |
| `fullStatus` | 25 | Vista completa · attiva i passaggi per spiegare la slide. |

I pulsanti della slide 10 e 11 hanno anche un testo iniziale nell’HTML. Quando la pagina si apre, JavaScript applica `uiText`: per cambiarli in modo stabile modifica questo blocco. Le frasi dei singoli passi restano nei due array sopra.

## Note del relatore, titoli e indice

| Slide | Inizio della `<section>`: titolo usato nella navigazione | Riga delle note |
|---|---|---|
| 01 | `index.html`, riga 17 | `index.html`, riga 80 |
| 02 | `index.html`, riga 86 | `index.html`, riga 209 |
| 03 | `index.html`, riga 222 | `index.html`, riga 328 |
| 04 | `index.html`, riga 339 | `index.html`, riga 414 |
| 05 | `index.html`, riga 417 | `index.html`, riga 481 |
| 06 | `index.html`, riga 500 | `index.html`, riga 567 |
| 07 | `index.html`, riga 575 | `index.html`, riga 747 |
| 08 | `index.html`, riga 771 | `index.html`, riga 843 |
| 09 | `index.html`, riga 882 | `index.html`, riga 973 |
| 10 | `index.html`, riga 999 | `index.html`, riga 1159 |
| 11 | `index.html`, riga 1191 | `index.html`, riga 1356 |
| 12 | `index.html`, riga 1375 | `index.html`, riga 1481 |
| 13 | `index.html`, riga 1506 | `index.html`, riga 1576 |
| 14 | `index.html`, riga 1598 | `index.html`, riga 1705 |
| 15 | `index.html`, riga 1734 | `index.html`, riga 1809 |
| 16 | `index.html`, riga 1826 | `index.html`, riga 1923 |
| 17 | `index.html`, riga 1958 | `index.html`, riga 2052 |
| 18 | `index.html`, riga 2060 | `index.html`, riga 2130 |
| 19 | `index.html`, riga 2148 | `index.html`, riga 2225 |
| 20 | `index.html`, riga 2254 | `index.html`, riga 2294 |

Se cambi il titolo della slide, aggiorna il testo SVG e `data-title` nella `<section>`. Aggiorna anche `aria-label`, il tag `<title>` SVG e la voce con `data-go` nell’indice. Il sottotitolo è indipendente dal titolo.

## Altri testi dell’interfaccia HTML

| Elemento / ID | Riga in `index.html` | Testo attuale |
|---|---|---|
| prev | 2299 |  |
| next | 2305 |  |
| outline-button | 2312 | Indice |
| fullscreen | 2313 | Schermo intero |
| notes-button | 2319 | Note |
| print | 2320 | PDF |
| outline-title | 2323 | Indice della presentazione |
| data-go=0 | 2326 | 01 Titolo della tesi |
| data-go=1 | 2329 | 02 5G Core e SCAS |
| data-go=2 | 2332 | 03 Dal risultato alla motivazione |
| data-go=3 | 2335 | 04 Perché una DSL? |
| data-go=4 | 2338 | 05 Una DSL per criteri SCAS |
| data-go=5 | 2341 | 06 Architettura generale |
| data-go=6 | 2344 | 07 Dagli eventi estratti agli eventi normalizzati |
| data-go=7 | 2347 | 08 Dalle evidenze al verdetto e al report |
| data-go=8 | 2350 | 09 La DSL: selezione e verifica |
| data-go=9 | 2353 | 10 Dalla regola all’automa |
| data-go=10 | 2356 | 11 Riconoscimento della sequenza |
| data-go=11 | 2359 | 12 Il binding context |
| data-go=12 | 2362 | 13 Motore di verifica |
| data-go=13 | 2365 | 14 AMF Synchronization Failure, Case B |
| data-go=14 | 2368 | 15 UPF TEID Uniqueness |
| data-go=15 | 2371 | 16 AMF RES*: una famiglia di quattro casi |
| data-go=16 | 2374 | 17 Risultati dei test baseline |
| data-go=17 | 2377 | 18 Mutation testing: il processo |
| data-go=18 | 2380 | 19 Mutation testing: risposta del verificatore |
| data-go=19 | 2383 | 20 Grazie per l’attenzione |
| close-outline | 2386 | Chiudi |
| speaker-notes-title | 2390 | Note del relatore |
| close-notes | 2391 | Chiudi |
| noscript | 2397 | Per la navigazione serve JavaScript. Sono disponibili tutte le slide tramite la stampa. |

Titoli di pulsanti e descrizioni per l’accessibilità sono negli attributi `title` e `aria-label` delle stesse righe. Non cambiare `id` e `data-go` per una modifica del solo testo.

## Testi dinamici della navigazione

| Scritta | File | Riga |
|---|---|---|
| Messaggio “Slide … di …” e titolo letto dagli screen reader | `script.js` | 38 |
| Suggerimento F11 quando lo schermo intero non è disponibile | `script.js` | 59 |
| “Durata stimata” nelle note | `script.js` | 105 |
| Titolo della finestra note: numero e titolo della slide | `script.js` | 103 |

## Dimensioni e aspetto delle scritte

| Cosa modificare | Dove |
|---|---|
| Un testo SVG | Nella stessa riga HTML: `font-size`, `x`, `y`, `text-anchor`; il colore dipende anche dalla classe `fill-*`. |
| Spiegazione del passo corrente | `style.css`, `.step-status`, riga 637: `font` e `line-height`. |
| Posizione e spazio della barra dei passi | `style.css`, `.step-controls`, riga 603. |
| Font e colori generali | `style.css`, `:root`, riga 2. |

La superficie delle slide è 1600 × 900. Nelle slide 10 e 11 mantieni il sottotitolo su una riga: subito sotto c’è la barra dei passi. I testi SVG non vanno a capo automaticamente; per una seconda riga aggiungi un altro `<text>` con una `y` diversa. Conserva `xml:space="preserve"` nel codice DSL e JSON.

## Tutte le scritte presenti nelle slide

La mappa seguente include titoli, riquadri, tabelle, diagrammi, legenda e frammenti di codice. Per una frase normale modifica il contenuto di `<text>`; nel codice possono esserci parole racchiuse in `<tspan>`: modifica il testo mantenendo i tag. Le voci lunghe sono abbreviate nella mappa, ma il testo completo è nell’HTML.
### Slide 01 — Titolo della tesi

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Corso di laurea in Informatica | 49 |
| A Domain-Specific Language | 50 |
| for Security Assurance | 51 |
| of 5G SCAS Tests | 52 |
| from Network Traffic Captures | 53 |
| Laureando | 54 |
| Samuele De Santis | 55 |
| Relatrice: Prof.ssa Paola Vocca | 56 |
| Correlatore: Prof. Francesco Mancini | 57 |
| Anno accademico 2025/2026 | 58 |
| PCAP | 60 |
| cattura di rete | 61 |
| DSL | 63 |
| regole del test | 64 |
| VERDETTO | 68 |
| PASS · FAIL · INCONCLUSIVE | 69 |
| REPORT | 72 |
| criteri ed evidenze | 73 |
| Un linguaggio per descrivere i criteri SCAS | 76 |
| e verificarli sui messaggi osservati nelle catture di rete. | 77 |

### Slide 02 — 5G Core e SCAS

| Scritta / frammento | Riga in `index.html` |
|---|---|
| 5G Core e SCAS | 117 |
| 5G RAN | 120 |
| 5G CORE | 122 |
| CONTROL PLANE | 124 |
| USER PLANE | 126 |
| AMF | 128 |
| SMF | 130 |
| AUSF | 132 |
| UDM | 134 |
| UPF | 136 |
| SBI | 140 |
| N4 | 142 |
| UE | 145 |
| gNB | 151 |
| N2 | 154 |
| N3 | 156 |
| N6 | 158 |
| SCAS del 3GPP | 162 |
| Precondizioni | 164 |
| Stato iniziale della prova | 165 |
| Azioni | 167 |
| Operazioni del test | 168 |
| Risultato atteso | 170 |
| Comportamento previsto | 171 |
| Evidenze | 173 |
| Informazioni da raccogliere | 174 |
| Internet | 194 |
| Le Network Functions cooperano attraverso scambi che devono rispettare requisiti di s… | 205 |
| Le SCAS descrivono le condizioni della prova, le azioni e il comportamento atteso. | 206 |

### Slide 03 — Dal risultato alla motivazione

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Dal risultato alla motivazione | 253 |
| Test SCAS eseguito | 255 |
| Cattura PCAP | 257 |
| Verdetto | 259 |
| Autorizzazione discovery NRF | 265 |
| TS 33.518 · §4.2.2.2.1 | 266 |
| Condizioni iniziali | 267 |
| Procedura | 268 |
| Esito atteso | 269 |
| NF1 appartiene alla slice B. | 270 |
| NF2 consente discovery dalla slice A. | 271 |
| NF1 cerca NF2 tramite il NRF. | 272 |
| HTTP 403 Forbidden | 273 |
| Messaggi osservati | 308 |
| La domanda aperta | 312 |
| Quali evidenze | 313 |
| giustificano il | 314 |
| verdetto? | 315 |
| La cattura contiene i messaggi della prova, ma non esplicita quali soddisfano i crite… | 320 |
| Per motivare il verdetto servono criteri valutati, valori osservati e frame di eviden… | 321 |
| Oggetto della tesi: verifica degli esiti da PCAP già disponibili. | 325 |

### Slide 04 — Perché una DSL?

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Perché una DSL? | 370 |
| I criteri cambiano da test a test: la loro descrizione deve restare separata dal soft… | 373 |
| Logica specifica nel codice | 379 |
| Criteri dichiarati nella DSL | 380 |
| Test 1 | 382 |
| Verificatore 1 | 385 |
| Regola DSL 1 | 387 |
| Test 2 | 390 |
| Verificatore 2 | 393 |
| Regola DSL 2 | 395 |
| Test 3 | 398 |
| Verificatore 3 | 401 |
| Regola DSL 3 | 403 |
| Unico motore | 406 |
| Selezione + verifica | 407 |
| Formalizzazione manuale dei criteri | 408 |
| Verifica automatica sulle catture | 409 |
| Nuovo test: si descrivono i criteri, senza riscrivere la logica generale del motore. | 411 |

### Slide 05 — Una DSL per criteri SCAS

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Una DSL per criteri SCAS | 448 |
| Specifiche SCAS | 450 |
| DSL | 452 |
| Pipeline | 454 |
| Formalizzazione | 457 |
| del progettista | 458 |
| Interpretazione | 459 |
| automatica | 460 |
| Verifica motivata | 462 |
| Il riutilizzo riguarda i protocolli supportati e le proprietà esprimibili nella DSL. | 464 |
| Selezione delle evidenze | 467 |
| Definizione dei criteri | 468 |
| Il progettista formalizza nella DSL quali evidenze cercare e quali proprietà verifica… | 477 |
| La pipeline interpreta quelle regole e produce un esito documentato sui messaggi osse… | 478 |

### Slide 06 — Architettura generale

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Architettura generale | 531 |
| Cattura PCAP | 533 |
| Estrazione strutturata | 535 |
| Normalizzazione per protocollo | 537 |
| Risoluzione semantica e correlazione | 539 |
| Selezione dell’evidenza | 541 |
| Verifica statica / temporale | 543 |
| Report JSON | 545 |
| tests.json | 553 |
| Specifica DSL | 556 |
| selezione e verifica | 557 |
| PCAP e DSL guidano la verifica; tests.json descrive il test e le sorgenti da usare. | 564 |

### Slide 07 — Dagli eventi estratti agli eventi normalizzati

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Dagli eventi estratti agli eventi normalizzati | 606 |
| Eventi estratti dalla PCAP | 607 |
| Eventi normalizzati | 608 |
| NAS | 687 |
| HTTP/2 | 688 |
| PFCP | 689 |
| Protocollo | 693 |
| Eventi | 694 |
| NAS | 697 |
| HTTP/2 | 704 |
| PFCP | 711 |
| Normalizzatore | 718 |
| Normalizzatore e resolver semantico organizzano gli eventi per protocollo e ne comple… | 721 |
| + resolver semantico | 723 |
| MessageEvent | 727 |
| Protocolli utilizzati | 731 |
| NAS | 732 |
| HTTP/2 | 733 |
| PFCP | 734 |
| Selezione DSL | 740 |
| Evidenze | 743 |
| selezionate | 744 |

### Slide 08 — Dalle evidenze al verdetto e al report

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Dalle evidenze al verdetto e al report | 802 |
| Evidenze selezionate | 804 |
| Verifica | 806 |
| Statica · Temporale | 807 |
| Verdetto | 809 |
| PASS · FAIL · INCONCLUSIVE | 810 |
| Report | 812 |
| Estratto del report UPF | 816 |
| { | 818 |
| "metadata": { | 819 |
| "generator": "generic_verification_pipeline", | 820 |
| "tshark_version": | 821 |
| "TShark (Wireshark) 3.6.2 (Git v3.6.2 packaged as 3.6.2-2)" | 822 |
| }, | 823 |
| "source": { | 824 |
| "pcap": "captures/upf_teid_uniqueness_open5gs.pcapng", | 825 |
| "sha256": "e025648617e4911b36253580…d6b428df56d8f20a" | 826 |
| }, | 827 |
| "verification": { | 828 |
| "results": [{ | 829 |
| "verdict": "PASS", | 830 |
| "evidence_frames": [37, 38, 46, 47, 48], | 831 |
| "details": { "field": "responses.f_teids", | 832 |
| "operator": "UNIQUE", "duplicates": [] } | 833 |
| }], | 834 |
| "overall_verdict": "PASS" | 835 |
| } | 836 |
| } | 837 |
| Il report rende ricostruibile la verifica: documenta i criteri valutati e le evidenze… | 840 |

### Slide 09 — La DSL: selezione e verifica

| Scritta / frammento | Riga in `index.html` |
|---|---|
| La DSL: selezione e verifica | 913 |
| SELEZIONE | 914 |
| VERIFICA | 915 |
| Sequenza | 918 |
| SEQUENCE { | 919 |
| ausf.authentication.response | 920 |
| AS authentication_vector | 921 |
| nas.authentication_request | 922 |
| AS authentication_request | 923 |
| ... | 924 |
| OPTIONAL { | 925 |
| ... | 926 |
| ausf.confirmation.response | 927 |
| AS ausf_confirmation_response | 928 |
| } | 929 |
| } | 930 |
| Collezione | 931 |
| COLLECT pfcp.session_establishment_response | 932 |
| AS responses | 933 |
| Statica | 937 |
| REQUIRE authentication_request.rand | 938 |
| == authentication_vector.rand | 939 |
| Temporale | 940 |
| MFOTL CASE B """ | 941 |
| SyncFailure() IMPLIES | 942 |
| NOT EVENTUALLY[0,{TIMER_MS}] | 943 |
| AuthenticationRequest() | 944 |
| """ | 945 |
| SEQUENCE | 949 |
| — eventi in ordine | 950 |
| OPTIONAL | 951 |
| — gruppo facoltativo | 952 |
| COLLECT | 953 |
| — eventi dello stesso tipo | 954 |
| AS | 955 |
| — alias delle evidenze | 956 |
| REQUIRE | 957 |
| — vincoli sui valori | 958 |
| MFOTL | 959 |
| — proprietà temporali | 960 |
| IMPLIES | 961 |
| — se … allora … | 962 |
| NOT EVENTUALLY | 963 |
| — nessun evento | 964 |
| nell’intervallo indicato | 965 |
| La regola descrive il comportamento atteso e le informazioni da confrontare. | 969 |
| Sequenze e collezioni individuano l’evidenza; i criteri statici e temporali ne valuta… | 970 |

### Slide 10 — Dalla regola all’automa

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Dalla regola all’automa | 1030 |
| REGOLA | 1031 |
| FRAMMENTI ELEMENTARI | 1032 |
| AUTOMA COMPLETO | 1033 |
| SEQUENCE { | 1036 |
| event.a AS a | 1037 |
| OPTIONAL { | 1038 |
| event.b AS b | 1039 |
| } | 1040 |
| event.c AS c | 1041 |
| } | 1042 |
| Atom(event.a) | 1067 |
| q0 | 1069 |
| q1 | 1071 |
| a | 1073 |
| Atom(event.b) | 1077 |
| q2 | 1079 |
| q3 | 1081 |
| b | 1083 |
| Atom(event.c) | 1087 |
| q4 | 1089 |
| q5 | 1091 |
| c | 1093 |
| q0 | 1098 |
| q1 | 1100 |
| q2 | 1102 |
| q3 | 1104 |
| q4 | 1106 |
| q5 | 1109 |
| inizio | 1110 |
| a | 1112 |
| b | 1114 |
| c | 1116 |
| ε | 1120 |
| ε | 1122 |
| ε | 1126 |
| Percorsi accettati | 1129 |
| A | 1131 |
| B | 1134 |
| C | 1137 |
| A | 1139 |
| C | 1142 |
| La sequenza diventa un NFA: gli Atom riconoscono gli eventi e le transizioni ε gestis… | 1146 |

### Slide 11 — Riconoscimento della sequenza

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Riconoscimento della sequenza | 1222 |
| SEQUENCE | 1223 |
| Eventi osservati | 1224 |
| Binding | 1225 |
| Automa | 1226 |
| SEQUENCE { | 1228 |
| event.a AS a | 1229 |
| OPTIONAL { | 1230 |
| event.b AS b | 1231 |
| } | 1232 |
| event.c AS c | 1233 |
| } | 1234 |
| Politica di riavvio | 1237 |
| Un nuovo inizio avvia un candidato. | 1238 |
| Il precedente si interrompe solo se | 1239 |
| non può consumare quell’evento. | 1240 |
| 1 | 1242 |
| A | 1245 |
| a(1) | 1250 |
| event.a | 1251 |
| 2 | 1253 |
| X | 1256 |
| 3 | 1258 |
| A | 1261 |
| a(3) | 1266 |
| event.a | 1267 |
| 4 | 1269 |
| B | 1272 |
| b(4) | 1277 |
| event.b | 1278 |
| 5 | 1280 |
| X | 1283 |
| 6 | 1285 |
| C | 1288 |
| c(6) | 1293 |
| event.c | 1294 |
| q0 | 1300 |
| q1 | 1302 |
| a | 1304 |
| inizio | 1305 |
| q2 | 1309 |
| q3 | 1311 |
| b | 1313 |
| q4 | 1317 |
| q5 | 1320 |
| c | 1322 |
| ε | 1326 |
| ε | 1330 |
| ε | 1334 |
| Il matcher considera i possibili inizi della sequenza; qui riconosce A(3), B(4), C(6)… | 1339 |
| Esempio del caso in cui il nuovo A non è consumabile dal candidato precedente. | 1343 |

### Slide 12 — Il binding context

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Il binding context | 1406 |
| Match | 1408 |
| BindingContext | 1410 |
| produce | 1412 |
| bindings | 1418 |
| Alias | 1419 |
| Evento | 1420 |
| initial_auth | 1423 |
| NAS | 1424 |
| frame 357 | 1425 |
| sync_failure | 1429 |
| NAS | 1430 |
| frame 358 | 1431 |
| resync | 1435 |
| HTTP/2 | 1436 |
| frame 359 | 1437 |
| Esempio: sync_failure | 1446 |
| "sync_failure": { | 1449 |
| "message_type": | 1450 |
| "nas.authentication_failure", | 1451 |
| "frame": 358, | 1452 |
| "timestamp": | 1453 |
| 1789490528.073905, | 1454 |
| "protocol": "nas_5gs", | 1455 |
| "fields": { | 1456 |
| "cause": 21, | 1457 |
| "auts": | 1458 |
| "94030fb233222a37b4220286604d" | 1459 |
| } | 1460 |
| } | 1461 |
| Il binding context rende disponibili alle regole di verifica gli eventi individuati d… | 1470 |
| I binding associano | 1475 |
| gli alias agli eventi | 1476 |
| selezionati, rendendone | 1477 |
| accessibili i campi. | 1478 |

### Slide 13 — Motore di verifica

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Motore di verifica | 1537 |
| Esempio illustrativo: esito PASS | 1538 |
| BindingContext | 1541 |
| Verifica statica | 1546 |
| Confronti tra campi e valori | 1547 |
| Unicità e condizioni IF | 1548 |
| Verifica temporale | 1549 |
| Formule MFOTL | 1550 |
| Valutazione con MonPoly | 1551 |
| Solo se la regola contiene | 1552 |
| una formula temporale | 1553 |
| Risultati delle verifiche | 1557 |
| FAIL | 1562 |
| Un criterio violato | 1563 |
| PASS | 1565 |
| Criteri soddisfatti | 1566 |
| INCONCLUSIVE | 1568 |
| Evidenza insufficiente | 1569 |
| I verifier applicano i criteri della DSL alle evidenze selezionate. | 1573 |

### Slide 14 — AMF Synchronization Failure, Case B

| Scritta / frammento | Riga in `index.html` |
|---|---|
| AMF Synchronization Failure, Case B | 1629 |
| SEQUENCE { | 1632 |
| ausf.authentication.response | 1633 |
| AS initial_vector | 1634 |
| nas.authentication_request | 1635 |
| AS initial_auth | 1636 |
| nas.authentication_failure | 1637 |
| AS sync_failure | 1638 |
| ausf.resynchronization.request | 1639 |
| AS resync | 1640 |
| ausf.authentication.response | 1641 |
| AS new_vector | 1642 |
| nas.authentication_request | 1643 |
| AS subsequent_auth_request | 1644 |
| } | 1645 |
| REQUIRE initial_auth.rand | 1646 |
| == initial_vector.rand | 1647 |
| REQUIRE sync_failure.cause == 21 | 1648 |
| REQUIRE resync.auts | 1649 |
| == sync_failure.auts | 1650 |
| REQUIRE resync.rand | 1651 |
| == initial_auth.rand | 1652 |
|  | 1653 |
| MFOTL CASE B """ | 1654 |
| SyncFailure() IMPLIES | 1655 |
| NOT EVENTUALLY[0,{TIMER_MS}] | 1656 |
| AuthenticationRequest() | 1657 |
| """ | 1658 |
| 4 controlli statici | 1662 |
| Esito: PASS | 1663 |
| 1 controllo temporale | 1665 |
| Esito: PASS | 1666 |
| PASS | 1671 |
| Rispetto del timer T3520 | 1675 |
| Nessuna nuova Authentication Request nei primi 15 s. | 1676 |
| attesa richiesta: 15 s | 1678 |
| 0 s | 1683 |
| 15 s | 1684 |
| ≈ 25 s | 1685 |
| frame 358 | 1686 |
| frame 606 | 1687 |
| PCAP: nuova Authentication Request | 1690 |
| frame 606 · dopo 25,018 s | 1691 |
| Il caso AMF combina controlli sui dati della risincronizzazione e sul rispetto del ti… | 1701 |
| La sequenza riconosciuta e i timestamp della cattura motivano il verdetto PASS. | 1702 |

### Slide 15 — UPF TEID Uniqueness

| Scritta / frammento | Riga in `index.html` |
|---|---|
| UPF TEID Uniqueness | 1765 |
| COLLECT pfcp.session_establishment_response AS responses | 1767 |
| REQUIRE UNIQUE responses.f_teids | 1768 |
| Evidenze osservate | 1769 |
| Frame | 1772 |
| F-TEID 1 | 1773 |
| F-TEID 2 | 1774 |
| 37 | 1776 |
| 0x00006a75 | 1777 |
| 0x0000ecf4 | 1778 |
| 38 | 1780 |
| 0x0000a5de | 1781 |
| 0x00000f66 | 1782 |
| 46 | 1784 |
| 0x0000b101 | 1785 |
| 0x0000a697 | 1786 |
| 47 | 1788 |
| 0x0000a7dc | 1789 |
| 0x0000113a | 1790 |
| 48 | 1792 |
| 0x00001ee9 | 1793 |
| 0x0000e1cf | 1794 |
| IPv4 comune: 127.0.0.7 | 1797 |
| NESSUN DUPLICATO | 1799 |
| 10 coppie distinte in 5 risposte | 1800 |
| PASS | 1803 |
| COLLECT raccoglie le risposte PFCP; REQUIRE UNIQUE controlla le coppie F-TEID {teid, … | 1806 |

### Slide 16 — AMF RES*: una famiglia di quattro casi

| Scritta / frammento | Riga in `index.html` |
|---|---|
| AMF RES*: una famiglia di quattro casi | 1857 |
| SEQUENCE { | 1859 |
| ... | 1860 |
| nas.authentication_request | 1861 |
| AS authentication_request | 1862 |
| nas.authentication_response | 1863 |
| AS authentication_response | 1864 |
| OPTIONAL { | 1865 |
| ausf.confirmation.request | 1866 |
| AS ausf_confirmation_request | 1867 |
| ... | 1868 |
| } | 1869 |
| nas.authentication_reject | 1870 |
| AS authentication_reject | 1871 |
| } | 1872 |
| REQUIRE authentication_reject.present | 1873 |
| == true | 1874 |
| IF case.failure_source == local { | 1875 |
| REQUIRE hres_star.value | 1876 |
| != authentication_vector.hxres_star | 1877 |
| } | 1878 |
| Fallimento AMF | 1879 |
| Fallimento AUSF | 1880 |
| Case A | 1882 |
| SUCI diretto | 1883 |
| Nessun gruppo opzionale | 1884 |
| 7 PASS | 1886 |
| 2 SKIPPED | 1888 |
| 1 match completo · verdetto PASS | 1889 |
| Case C | 1891 |
| SUCI diretto | 1892 |
| Confirmation presente | 1893 |
| 9 PASS | 1895 |
| 2 SKIPPED | 1897 |
| 1 match completo · verdetto PASS | 1898 |
| Case B | 1900 |
| GUTI → SUCI | 1901 |
| Identity presente | 1902 |
| 9 PASS | 1904 |
| 2 SKIPPED | 1906 |
| 1 match completo · verdetto PASS | 1907 |
| Case D | 1909 |
| GUTI → SUCI | 1910 |
| Identity + Confirmation | 1911 |
| 11 PASS | 1913 |
| 2 SKIPPED | 1915 |
| 1 match completo · verdetto PASS | 1916 |
| Estratto DSL: selezioni e criteri omessi. | 1917 |
| Una sola regola rappresenta quattro varianti della procedura e applica i criteri pert… | 1920 |

### Slide 17 — Risultati dei test baseline

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Risultati dei test baseline | 1989 |
| Il confronto con gli esiti attesi verifica la risposta della pipeline sulle dieci cat… | 1991 |
| Caso di test | 1997 |
| Atteso | 1998 |
| Osservato | 1999 |
| NRF Discovery Authorization | 2001 |
| FAIL | 2002 |
| FAIL | 2003 |
| UDM Resynchronization | 2005 |
| PASS | 2006 |
| PASS | 2007 |
| UDM SUCI De-concealment | 2009 |
| PASS | 2010 |
| PASS | 2011 |
| AMF Sync Failure — Case A | 2013 |
| PASS | 2014 |
| PASS | 2015 |
| AMF Sync Failure — Case B | 2017 |
| PASS | 2018 |
| PASS | 2019 |
| UPF TEID Uniqueness | 2021 |
| PASS | 2022 |
| PASS | 2023 |
| RES* Verification Failure — A | 2025 |
| PASS | 2026 |
| PASS | 2027 |
| RES* Verification Failure — B | 2029 |
| PASS | 2030 |
| PASS | 2031 |
| RES* Verification Failure — C | 2033 |
| PASS | 2034 |
| PASS | 2035 |
| RES* Verification Failure — D | 2037 |
| PASS | 2038 |
| PASS | 2039 |
| 10 / 10 | 2046 |
| corrispondenze | 2047 |
| 9 PASS | 2048 |
| 1 FAIL atteso | 2049 |

### Slide 18 — Mutation testing: il processo

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Mutation testing: il processo | 2091 |
| PCAP originale | 2093 |
| Estrazione e normalizzazione | 2095 |
| Selezione dell’evidenza | 2097 |
| Verifica statica / temporale | 2099 |
| Report e verdetto | 2101 |
| DSL | 2107 |
| MUTAZIONE | 2113 |
| Nuova PCAP mutata | 2115 |
| Motore di mutazione | 2117 |
| frame rilevanti | 2119 |
| Valori, timestamp o frame | 2122 |
| modificati offline in una copia | 2123 |
| del PCAP. | 2124 |
| Modificando le evidenze nel PCAP, si valuta la risposta della pipeline mantenendo inv… | 2127 |

### Slide 19 — Mutation testing: risposta del verificatore

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Mutation testing: risposta del verificatore | 2179 |
| AMF · tre mutazioni, un esito complessivo: FAIL | 2180 |
| Mutazione | 2183 |
| Statica | 2184 |
| Temporale | 2185 |
| Complessivo | 2186 |
| Statica | 2188 |
| FAIL | 2189 |
| PASS | 2190 |
| FAIL | 2191 |
| Temporale | 2193 |
| PASS | 2194 |
| FAIL | 2195 |
| FAIL | 2196 |
| Combinata | 2198 |
| FAIL | 2199 |
| FAIL | 2200 |
| FAIL | 2201 |
| UPF · violazione o evidenza insufficiente: INCONCLUSIVE | 2205 |
| Coppia F-TEID duplicata | 2207 |
| Baseline: PASS | 2209 |
| FAIL | 2212 |
| Risposte PFCP rimosse | 2214 |
| Baseline: PASS | 2216 |
| INCONCLUSIVE | 2219 |
| Le mutazioni distinguono una proprietà violata da un caso in cui mancano le evidenze … | 2222 |

### Slide 20 — Grazie per l’attenzione

| Scritta / frammento | Riga in `index.html` |
|---|---|
| Grazie per l’attenzione | 2285 |
| Domande? | 2286 |
| Samuele De Santis | 2288 |
| Casi studiati e mutazioni considerate: verifica tracciabile entro il perimetro del li… | 2291 |



## Apostrofi e caratteri speciali

Nel JavaScript le frasi sono tra apici. Se scrivi un apostrofo dritto dentro la frase, puoi usare virgolette doppie: `label: "L’automa riconosce la sequenza."`. Conserva la virgola dopo il testo. Puoi usare anche una frase con un apostrofo normale dentro le virgolette doppie.

Nell’HTML, per scrivere un simbolo &lt; usa `&lt;`; per &amp; usa `&amp;`. Lascia intatti i tag `<text>` e `<tspan>`. Le normali lettere accentate possono essere scritte direttamente.

## Dopo la modifica

Salva il file e ricarica `index.html` nel browser. Le modifiche a HTML, CSS e JS non aggiornano il PDF già scaricato: usa P o il pulsante stampa per esportare un nuovo PDF. Per GitHub Pages carica tutti i file della cartella, comprese `assets` e `data`.

Per spostare diagrammi e cambiare frecce o immagini, usa anche `MODIFICA_SLIDE.md`, che contiene la mappa dei gruppi SVG.
