# Discorso e riferimenti — presentazione da 5 minuti

Sette slide, inclusa la copertina. Tempi indicativi: 4:55 complessivi.

## 1. Titolo della tesi

Tempo indicativo: 10 secondi.

Buongiorno. Il lavoro riguarda un linguaggio per descrivere i criteri di verifica dei test SCAS e un sistema che li applica alle catture di rete.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/01-titolo.html

## 2. Security Assurance

Tempo indicativo: 35 secondi.

La Security Assurance serve a verificare che un sistema rispetti effettivamente i requisiti di sicurezza. Definire un requisito non significa che il software lo implementi correttamente. Bisogna quindi confrontare il comportamento previsto con quello reale. Nel 5G le funzionalità sono realizzate da componenti software chiamate Network Functions, e il 3GPP ha definito le specifiche SCAS per verificarne la sicurezza.

Fonti:

- https://www.etsi.org/deliver/etsi_ts/133500_133599/133518/18.00.00_60/ts_133518v180000p.pdf
- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/02_capitolo.tex

## 3. La rete 5G

Tempo indicativo: 20 secondi.

Qui vediamo dove si trovano le Network Functions: nel 5G Core. Sono componenti software che cooperano tra loro, separando il controllo della rete dal trasporto del traffico. Per il mio lavoro è sufficiente questa idea: le funzioni comunicano e il loro comportamento può essere osservato.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/02-rete-5g.html

## 4. Dagli SCAS al DSL

Tempo indicativo: 70 secondi.

Le specifiche SCAS sono scritte in linguaggio naturale e non possono essere interpretate direttamente dal verificatore. La prima schermata mostra tre estratti reali e uno pseudocodice soltanto illustrativo. [Primo clic] Nel caso NRF, riportato in forma semplificata nella tesi, distinguiamo i messaggi da individuare e il criterio da verificare: la risposta HTTP 403 alla discovery non autorizzata. [Secondo clic] Ho progettato il DSL per rappresentare questi due aspetti con costrutti riutilizzabili. Al posto del testo SCAS compare la regola: SEQUENCE descrive i messaggi, REQUIRE il criterio. Le due domande rimangono le stesse. Le regole sono scritte usando i costrutti del DSL: non ho sviluppato una traduzione automatica NLP né un sistema che esegue i test SCAS.

Fonti:

- https://www.etsi.org/deliver/etsi_ts/133500_133599/133512/17.03.00_60/ts_133512v170300p.pdf (p. 9)
- https://www.etsi.org/deliver/etsi_ts/133500_133599/133518/18.00.00_60/ts_133518v180000p.pdf (p. 8)
- https://www.etsi.org/deliver/etsi_ts/133500_133599/133514/16.03.00_60/ts_133514v160300p.pdf (p. 8)
- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/02_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/dsl/nrf_sequence_test.dsl

## 5. Architettura proposta

Tempo indicativo: 50 secondi.

Il secondo contributo è il sistema che interpreta le regole del DSL ed esegue la verifica. Parte da una PCAP, una cattura dei messaggi scambiati durante il test: legge evidenze già prodotte, non esegue il test. La pipeline estrae e normalizza i messaggi, ne risolve il significato, seleziona quelli richiesti e verifica i criteri. La verifica può essere statica o temporale, tramite MonPoly. Infine produce il report e il verdetto.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/06-architettura.html
- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/04_capitolo.tex

## 6. Risultati dei test baseline

Tempo indicativo: 50 secondi.

Ho valutato il sistema su 16 catture provenienti da Open5GS e free5GC, prodotte da esecuzioni separate dal verificatore. La tabella raggruppa i casi. I 16 verdetti sono coerenti con gli esiti attesi: 12 PASS, un FAIL e tre INCONCLUSIVE. Il FAIL NRF segnala HTTP 200 dove il criterio richiede 403; gli INCONCLUSIVE indicano evidenze insufficienti. Il 16/16 non significa quindi che tutte le verifiche abbiano restituito PASS. Per NRF e UDM sono stati adattati componenti di ScasDK: non attribuisco tutte le catture allo stesso strumento.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/06_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/18-baseline.html

## 7. Mutation testing

Tempo indicativo: 60 secondi.

Per valutare la sensibilità del sistema ho introdotto modifiche controllate nelle catture. Il mutatore è separato dalla pipeline: riceve la PCAP originale e le evidenze del report baseline, individua i dati da modificare e produce la PCAP mutata. Questa torna nello stesso sistema di verifica, con la stessa DSL. Il confronto dei risultati deve corrispondere alla modifica introdotta. Nei 13 scenari completati ho ottenuto tutti i verdetti attesi. Due ulteriori scenari AMF Case B temporali e combinati non sono stati completati per limiti del mutatore, non per due errori del verificatore.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/19-mutazioni.html
- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/06_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/mutation_testing/mutate_nrf_status.py
