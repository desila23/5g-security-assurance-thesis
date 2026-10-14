# Dove modificare le slide

Per tutte le scritte e le spiegazioni dei passi, parti da `GUIDA_TESTI.md`. Apri la cartella in VS Code. Attiva i numeri di riga e modifica i file indicati sotto. Non serve compilare: salva e ricarica `index.html` nel browser.

Le righe si riferiscono esattamente al pacchetto consegnato. Dopo una modifica possono spostarsi: i commenti `SLIDE 01`, `SLIDE 02` ecc. restano un riferimento per la ricerca.

## Scelta rapida

| Voglio modificare… | Dove andare |
|---|---|
| Una scritta | `index.html`: cerca il testo con Ctrl+F, oppure usa la mappa delle scritte qui sotto. Modifica il contenuto del tag `<text>`. |
| Dimensione o posizione di una scritta | Nella stessa riga, modifica `font-size`, `x` e `y`. `y` è la linea di base. |
| Un riquadro | `index.html`: cerca il suo ID o il gruppo della figura, poi modifica il tag `<rect>`: `x`, `y`, `width`, `height`, `rx`. |
| Una freccia | `index.html`, dentro la stessa slide: modifica il `d` del tag `<path>`. `M` è il punto iniziale, `L` un punto successivo, `C` una curva. |
| Un gruppo di un diagramma | I gruppi `<g>` sono indicati nella mappa. Per spostarli insieme, aggiungi `transform="translate(40, 0)"`. |
| Colori di slide, NAS o HTTP/2 | `style.css`, sezione 01. Le variabili `--slide-nas-strong` e `--slide-http-strong` controllano i relativi quadrati. |
| Logo o immagine | Il logo è `assets/logo.png`. Sostituisci il file, oppure cambia `href` nel tag `<image>` indicato sotto. |
| Note del relatore | `index.html`, nel `<template class="speaker-note">` della slide. |
| Durata di una slide | `index.html`, nell’attributo `data-seconds` della sua `<section>`. |
| Navigazione e scorciatoie | `script.js`; usa i commenti e le righe della tabella generale. |

## File e righe generali

| File | Punto | Riga |
|---|---|---|
| `style.css` | Colori e font del tema | 2 |
| `style.css` | NAS: quadrati più marcati | 18 |
| `style.css` | HTTP/2: colore distinto dalle evidenze | 19 |
| `style.css` | Palco e ridimensionamento | 204 |
| `style.css` | Navigazione | 257 |
| `style.css` | Stampa | 437 |
| `script.js` | Cambio slide e hash | 23 |
| `script.js` | Tastiera | 71 |
| `script.js` | Note del relatore | 102 |
| `index.html` | Logo: tag image | 48 |
| `assets/logo.png` | File immagine del logo | — |
| `assets/fonts.css` | Definizioni e licenze dei font | 1 |
| `data/upf-report-excerpt.json` | Estratto JSON con hash completo | 1 |

## Mappa delle 20 slide

| Slide | Titolo | HTML: inizio–fine | Titolo visibile | Note |
|---|---|---|---|---|
| 01 | Titolo della tesi | 17–84 | 50 | 80 |
| 02 | 5G Core e SCAS | 86–220 | 117 | 209 |
| 03 | Dal risultato alla motivazione | 222–337 | 253 | 328 |
| 04 | Perché una DSL? | 339–415 | 370 | 414 |
| 05 | Una DSL per criteri SCAS | 417–498 | 448 | 481 |
| 06 | Architettura generale | 500–573 | 531 | 567 |
| 07 | Dagli eventi estratti agli eventi normalizzati | 575–769 | 606 | 747 |
| 08 | Dalle evidenze al verdetto e al report | 771–880 | 802 | 843 |
| 09 | La DSL: selezione e verifica | 882–997 | 913 | 973 |
| 10 | Dalla regola all’automa | 999–1189 | 1030 | 1159 |
| 11 | Riconoscimento della sequenza | 1191–1373 | 1222 | 1356 |
| 12 | Il binding context | 1375–1504 | 1406 | 1481 |
| 13 | Motore di verifica | 1506–1596 | 1537 | 1576 |
| 14 | AMF Synchronization Failure, Case B | 1598–1732 | 1629 | 1705 |
| 15 | UPF TEID Uniqueness | 1734–1824 | 1765 | 1809 |
| 16 | AMF RES*: una famiglia di quattro casi | 1826–1956 | 1857 | 1923 |
| 17 | Risultati dei test baseline | 1958–2058 | 1989 | 2052 |
| 18 | Mutation testing: il processo | 2060–2146 | 2091 | 2130 |
| 19 | Mutation testing: risposta del verificatore | 2148–2252 | 2179 | 2225 |
| 20 | Grazie per l’attenzione | 2254–2295 | 2285 | 2294 |

## Diagrammi e riquadri: punti precisi

| Slide | Elemento / ID da cercare | File | Riga |
|---|---|---|---|
| 01 | node-1-cover-pcap | `index.html` | 59 |
| 01 | node-1-cover-dsl | `index.html` | 62 |
| 01 | node-1-cover-verdict | `index.html` | 67 |
| 01 | node-1-cover-report | `index.html` | 71 |
| 01 | slide-subtitle-1 | `index.html` | 75 |
| 02 | rete-5g | `index.html` | 118 |
| 02 | node-2-AMF | `index.html` | 127 |
| 02 | node-2-SMF | `index.html` | 129 |
| 02 | node-2-AUSF | `index.html` | 131 |
| 02 | node-2-UDM | `index.html` | 133 |
| 02 | node-2-UPF | `index.html` | 135 |
| 02 | specifiche-scas | `index.html` | 160 |
| 02 | internet-globo | `index.html` | 176 |
| 02 | slide-subtitle-2 | `index.html` | 204 |
| 03 | node-3-test | `index.html` | 254 |
| 03 | node-3-pcap | `index.html` | 256 |
| 03 | node-3-verdict | `index.html` | 258 |
| 03 | dettaglio-specifica | `index.html` | 262 |
| 03 | dettaglio-pcap | `index.html` | 275 |
| 03 | domanda-verdetto | `index.html` | 310 |
| 03 | slide-subtitle-3 | `index.html` | 319 |
| 03 | perimetro-verifica | `index.html` | 324 |
| 04 | slide-subtitle-4 | `index.html` | 372 |
| 04 | confronto-riutilizzo | `index.html` | 376 |
| 05 | node-5-spec | `index.html` | 449 |
| 05 | node-5-dsl | `index.html` | 451 |
| 05 | node-5-pipeline | `index.html` | 453 |
| 05 | dsl-responsibilities | `index.html` | 465 |
| 05 | node-5-dsl-description | `index.html` | 466 |
| 05 | dsl-description-link | `index.html` | 470 |
| 05 | slide-subtitle-5 | `index.html` | 476 |
| 06 | node-6-pcap | `index.html` | 532 |
| 06 | node-6-extract | `index.html` | 534 |
| 06 | node-6-norm | `index.html` | 536 |
| 06 | node-6-semantic | `index.html` | 538 |
| 06 | node-6-select | `index.html` | 540 |
| 06 | node-6-verify | `index.html` | 542 |
| 06 | node-6-report | `index.html` | 544 |
| 06 | node-6-config | `index.html` | 552 |
| 06 | node-6-dsl | `index.html` | 555 |
| 06 | slide-subtitle-6 | `index.html` | 563 |
| 07 | pacchetti-pcap | `index.html` | 611 |
| 07 | eventi-per-protocollo | `index.html` | 692 |
| 07 | protocol-events-0 | `index.html` | 695 |
| 07 | protocol-events-1 | `index.html` | 702 |
| 07 | protocol-events-2 | `index.html` | 709 |
| 07 | slide-subtitle-7 | `index.html` | 720 |
| 07 | normalized-message-event | `index.html` | 725 |
| 07 | protocols-used | `index.html` | 730 |
| 07 | dsl-evidence-selection | `index.html` | 737 |
| 08 | node-8-evidence | `index.html` | 803 |
| 08 | node-8-report | `index.html` | 811 |
| 08 | slide-subtitle-8 | `index.html` | 839 |
| 09 | dsl-selezione | `index.html` | 916 |
| 09 | dsl-verifica | `index.html` | 935 |
| 09 | dsl-legenda | `index.html` | 947 |
| 09 | slide-subtitle-9 | `index.html` | 968 |
| 10 | construction-rule | `index.html` | 1034 |
| 10 | construction-atom-a | `index.html` | 1065 |
| 10 | construction-atom-b | `index.html` | 1075 |
| 10 | construction-atom-c | `index.html` | 1085 |
| 10 | construction-nfa | `index.html` | 1095 |
| 10 | construction-eps-links | `index.html` | 1118 |
| 10 | construction-eps-skip | `index.html` | 1124 |
| 10 | construction-paths | `index.html` | 1128 |
| 10 | slide-subtitle-10 | `index.html` | 1145 |
| 11 | restart-policy | `index.html` | 1235 |
| 11 | matcher-event-0 | `index.html` | 1243 |
| 11 | matcher-binding-0 | `index.html` | 1247 |
| 11 | matcher-event-1 | `index.html` | 1254 |
| 11 | matcher-event-2 | `index.html` | 1259 |
| 11 | matcher-binding-2 | `index.html` | 1263 |
| 11 | matcher-event-3 | `index.html` | 1270 |
| 11 | matcher-binding-3 | `index.html` | 1274 |
| 11 | matcher-event-4 | `index.html` | 1281 |
| 11 | matcher-event-5 | `index.html` | 1286 |
| 11 | matcher-binding-5 | `index.html` | 1290 |
| 11 | matcher-nfa | `index.html` | 1296 |
| 11 | matcher-atom-a | `index.html` | 1298 |
| 11 | matcher-atom-b | `index.html` | 1307 |
| 11 | matcher-atom-c | `index.html` | 1315 |
| 11 | matcher-eps-ab | `index.html` | 1324 |
| 11 | matcher-eps-bc | `index.html` | 1328 |
| 11 | matcher-eps-skip | `index.html` | 1332 |
| 11 | slide-subtitle-11 | `index.html` | 1338 |
| 11 | matcher-candidato-nota | `index.html` | 1342 |
| 12 | node-12-match | `index.html` | 1407 |
| 12 | node-12-context | `index.html` | 1409 |
| 12 | binding-closeup | `index.html` | 1413 |
| 12 | binding-context | `index.html` | 1416 |
| 12 | binding-initial_auth | `index.html` | 1421 |
| 12 | binding-sync_failure | `index.html` | 1427 |
| 12 | binding-resync | `index.html` | 1433 |
| 12 | binding-more | `index.html` | 1439 |
| 12 | binding-serializzato | `index.html` | 1447 |
| 12 | binding-detail-link | `index.html` | 1463 |
| 12 | slide-subtitle-12 | `index.html` | 1469 |
| 12 | binding-context-description | `index.html` | 1473 |
| 13 | Motore di verifica | `index.html` | 1539 |
| 13 | node-13-context | `index.html` | 1540 |
| 13 | node-13-results | `index.html` | 1556 |
| 13 | slide-subtitle-13 | `index.html` | 1572 |
| 14 | regola-amf-completa | `index.html` | 1630 |
| 14 | risultati-amf | `index.html` | 1660 |
| 14 | timeline-amf | `index.html` | 1673 |
| 14 | temporal-explanation-link | `index.html` | 1694 |
| 14 | slide-subtitle-14 | `index.html` | 1700 |
| 15 | slide-subtitle-15 | `index.html` | 1805 |
| 16 | slide-subtitle-16 | `index.html` | 1919 |
| 17 | slide-subtitle-17 | `index.html` | 1990 |
| 17 | baseline-table | `index.html` | 1994 |
| 17 | baseline-summary | `index.html` | 2044 |
| 18 | node-18-pcap | `index.html` | 2092 |
| 18 | node-18-extract | `index.html` | 2094 |
| 18 | node-18-select | `index.html` | 2096 |
| 18 | node-18-verify | `index.html` | 2098 |
| 18 | node-18-report | `index.html` | 2100 |
| 18 | node-18-dsl | `index.html` | 2106 |
| 18 | node-18-mutated | `index.html` | 2114 |
| 18 | node-18-mutator | `index.html` | 2116 |
| 18 | slide-subtitle-18 | `index.html` | 2126 |
| 19 | slide-subtitle-19 | `index.html` | 2221 |
| 20 | slide-subtitle-20 | `index.html` | 2290 |

Lo schema 5G Core, la lente, i diagrammi e gli automi sono SVG modificabili. Non sono PNG da sostituire. I tag `<circle>`, `<rect>` e `<path>` si trovano nelle righe della relativa slide o del gruppo sopra indicato.

## Mappa delle scritte

Qui trovi la riga di ogni testo visibile, compresi frammenti DSL e JSON. Le righe lunghe sono abbreviate nella guida; il contenuto completo è nel file HTML.

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

## Esempi

### Cambiare una scritta

Cerca una voce nella mappa, vai alla riga indicata e modifica solo il testo tra `<text>` e `</text>`. Per il codice, le parole chiave possono trovarsi in un `<tspan>`. Mantieni `xml:space="preserve"` per conservare l’indentazione.

### Spostare o cambiare un diagramma

Le coordinate usano una superficie di 1600 × 900. `construction-nfa` contiene l’automa della slide 10. `construction-atom-a`, `construction-atom-b` e `construction-atom-c` contengono i frammenti elementari. I gruppi `matcher-*` sono nella slide 11. Le slide 6 e 18 mantengono i diagrammi originali: cerca i riquadri `node-6-*` e `node-18-*`; i collegamenti sono i relativi elementi `path`.

Per cambiare il percorso di una freccia, modifica i punti del suo `d`. Mantieni la punta fuori dal riquadro di arrivo e lascia spazio tra linea ed etichetta.

### Inserire un’immagine propria

Copia il file nella cartella `assets`. Nella slide sostituisci il gruppo grafico desiderato con un elemento come questo:

```html
<image href="assets/mia-figura.png" x="112" y="300" width="900" height="500" preserveAspectRatio="xMidYMid meet"/>
```

### Cambiare colori

Modifica le variabili della sezione 01 di `style.css`. Le classi `fill-blue`, `fill-green`, `fill-nas-strong`, `fill-http-strong` ecc. applicano questi colori. Per cambiare un solo elemento, cambia la sua classe. Gli stati dei passi della slide 11 sono colorati da `interactive-slides.js`, nelle funzioni `paintSVG` e `colourAtom`.

### Modificare il JSON del report

La slide 8 mostra lo SHA-256 completo su una riga; il file `data/upf-report-excerpt.json` conserva lo stesso valore. La slide contiene un estratto SVG indipendente: modificare il JSON nella cartella `data` non cambia automaticamente il testo mostrato. Usa la mappa delle scritte della slide 8.

### Titoli e nuove slide

Se cambi il titolo, aggiorna anche `data-title`, `aria-label` e la voce nell’indice a fine HTML. Se aggiungi una slide, assegna un ID unico, aggiorna l’indice e le durate. La navigazione segue l’ordine delle sezioni nel file.

## GitHub Pages

Carica tutta la cartella del pacchetto, comprese `assets` e `data`. I percorsi sono relativi, quindi la presentazione funziona anche in una sottocartella del repository.


## Testi e sottotitoli: guida dedicata

`GUIDA_TESTI.md` elenca tutte le frasi dei sottotitoli, i 16 testi dei passi di automa e matcher, i pulsanti, i messaggi dinamici, le note e ogni scritta SVG. Nell’HTML cerca `SOTTOTITOLO SLIDE` e `TESTI PASSI SLIDE`: i commenti indicano il punto da modificare.


## Numerazione dopo il brief XML

Nuova slide 4: Perché una DSL?. Le precedenti slide 4–19 sono ora 5–20. Automa: 10. Matcher: 11. BindingContext: 12. Motore di verifica: 13. RES*: 16. Baseline: 17. Mutation testing: 18–19.

Il riavvio nella slide 11 mostra il caso condizionale in cui nessuna configurazione del candidato precedente consuma il nuovo A. Nella vista completa A(1) resta neutro. Le otto spiegazioni sono nel blocco matcherSteps.


## Revisione 14 — correzioni di dettaglio

- Slide 7: `protocols-used` contiene NAS, HTTP/2 e PFCP attenuato; `protocol-events-2` e gli elementi viola di `pacchetti-pcap` usano `opacity`. Le etichette Normalizzatore e resolver semantico hanno entrambe dimensione 18. `normalized-message-event` contiene solo MessageEvent; `dsl-evidence-selection` porta alle evidenze selezionate.
- Slide 12: `binding-context-description` contiene una sola frase sui binding.
- Slide 14: `temporal-explanation-link` è viola a x=1450, separato dai collegamenti verdi a PASS. Il riquadro della timeline rimane bianco.
- Slide 18: `node-18-dsl` è a y=570, centrato tra le due frecce. La scritta sul rientro è rimossa.
- Slide 19: colori delle tabelle e degli esiti ripristinati come nella foto; solo i due titoli AMF e UPF hanno lo stesso blu.
