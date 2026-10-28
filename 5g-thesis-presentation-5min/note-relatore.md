# Discorso per le cinque slide

## Slide 1 - Il problema della Security Assurance

Tempo indicativo: 50 secondi.

La Security Assurance è il processo attraverso cui si verifica che un sistema rispetti determinati requisiti di sicurezza.
La definizione di un requisito, però, non garantisce che questo venga effettivamente rispettato dal software. È quindi necessario verificarne il comportamento.
Nel contesto 5G, le funzionalità di rete sono realizzate da componenti software chiamate Network Functions.
Per verificarne la sicurezza, il 3GPP ha definito le Security Assurance Specifications, o SCAS, che descrivono requisiti e procedure di test.
I test interagiscono con queste componenti dall’esterno, inviando richieste e osservando le risposte. Le comunicazioni generate possono essere registrate in catture di rete, che costituiscono le evidenze su cui effettuare la verifica.

Fonti:

- https://www.etsi.org/deliver/etsi_ts/133500_133599/133518/18.00.00_60/ts_133518v180000p.pdf (ambito e procedure di test)
- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/02_capitolo.tex

## Slide 2 - Il problema dell’automazione

Tempo indicativo: 50 secondi.

Le specifiche SCAS sono però scritte in linguaggio naturale, quindi sono pensate per essere lette e interpretate da un operatore.
Per automatizzare i test, queste procedure devono essere implementate in codice. Il frammento mostrato rappresenta soltanto lo schema dell’esecuzione.
Mentre l’esecuzione può cambiare in base al test e all’implementazione della rete, la verifica presenta caratteristiche comuni.
Analizzando diversi test SCAS, ho individuato due operazioni ricorrenti: selezionare i messaggi rilevanti e verificare che soddisfino le condizioni previste.
Da questa osservazione nasce la proposta di utilizzare un linguaggio specifico per descrivere i criteri di verifica.

Fonti:

- https://www.etsi.org/deliver/etsi_ts/133500_133599/133512/17.03.00_60/ts_133512v170300p.pdf (p. 9, Purpose)
- https://www.etsi.org/deliver/etsi_ts/133500_133599/133514/16.03.00_60/ts_133514v160300p.pdf (p. 8, Purpose)
- https://www.etsi.org/deliver/etsi_ts/133500_133599/133518/18.00.00_60/ts_133518v180000p.pdf (p. 8, Expected Results)

## Slide 3 - La soluzione proposta

Tempo indicativo: 75 secondi.

Partendo da questa analisi, ho sviluppato due componenti.
Il primo è un Domain-Specific Language, un linguaggio che permette di rappresentare i criteri di verifica attraverso costrutti riutilizzabili.
L’esempio è NRF Discovery Authorization: una richiesta di discovery non autorizzata deve ricevere una risposta HTTP 403.
La SEQUENCE individua richiesta e risposta. Il REQUIRE controlla lo status della risposta. Quella mostrata è la sintassi realmente utilizzata nel progetto. Le regole sono definite esplicitamente, a partire dall’analisi della specifica.
Il secondo contributo è il sistema che interpreta queste regole ed esegue la verifica.
Il sistema parte da una cattura PCAP, estrae e normalizza i messaggi, seleziona quelli rilevanti e applica i criteri del DSL.
La verifica può essere statica oppure temporale, quest’ultima gestita attraverso l’integrazione con MonPoly.
Infine, produce un report che associa il verdetto alle evidenze utilizzate per determinarlo.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/main/dsl/nrf_sequence_test.dsl
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/config/tests.json
- https://www.etsi.org/deliver/etsi_ts/133500_133599/133518/18.00.00_60/ts_133518v180000p.pdf
- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/05_capitolo.tex

## Slide 4 - Testing sulle catture originali

Tempo indicativo: 55 secondi.

Il sistema è stato valutato su 16 catture di traffico relative a diversi test SCAS.
Le catture provengono da due implementazioni 5G open source, Open5GS e free5GC. Sono state prodotte separatamente dal verificatore. Per le prove NRF e UDM sono stati adattati alcuni componenti di ScasDK.
Il mio sistema non genera quindi le evidenze, ma valuta quelle già ottenute.
Dei 16 casi, 12 hanno prodotto PASS, uno FAIL e tre INCONCLUSIVE.
Questi risultati sono coerenti con il comportamento osservato nelle singole catture. Nel caso NRF, il FAIL rileva una risposta HTTP 200 dove il criterio richiede 403. Nei tre casi INCONCLUSIVE, le evidenze disponibili non consentono una conclusione.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/06_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/18-baseline.html

## Slide 5 - Mutation testing

Tempo indicativo: 70 secondi.

I risultati sulle catture originali non sono sufficienti, da soli, a valutare l’affidabilità del verificatore: alcuni test hanno guidato anche lo sviluppo.
Per questo ho introdotto una fase di mutation testing. Uno strumento separato modifica in modo controllato le catture, che vengono poi valutate con la stessa DSL e la stessa pipeline.
Riprendendo il caso NRF, nella cattura originale lo status è HTTP 200 e il risultato è FAIL. Modificando lo status in 403, il risultato diventa PASS, come previsto.
Complessivamente, tutti i 13 scenari completati hanno prodotto il verdetto atteso. Dei 15 previsti, due scenari temporali e combinati AMF Case B non sono stati completati per limiti del mutatore attuale.
Il lavoro mostra quindi come un DSL e un sistema comune possano produrre verifiche motivate e riproducibili. Un possibile sviluppo futuro riguarda la generalizzazione del mutatore.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/06_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/20-risultati-mutazioni.html
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/reports/nrf_disc_auth_slice_report.json
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/reports/nrf_disc_auth_slice_status_mutation/report.json

