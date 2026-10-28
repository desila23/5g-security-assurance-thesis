# Discorso e riferimenti — versione da 5 minuti

Copertina più cinque slide di contenuto. Tempi indicativi: 4:45 complessivi.

## 1. Titolo della tesi

Tempo indicativo: 10 secondi.

Buongiorno. Il lavoro riguarda un linguaggio per descrivere i criteri di verifica dei test SCAS e un sistema che li applica alle catture di rete.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/01-titolo.html

## 2. Security Assurance

Tempo indicativo: 42 secondi.

La Security Assurance serve a verificare che un sistema rispetti effettivamente i requisiti di sicurezza. Definire un requisito non significa che il software lo implementi correttamente. Bisogna quindi confrontare il comportamento previsto con quello reale. Nel 5G le funzionalità sono realizzate da componenti software chiamate Network Functions. Il 3GPP ha definito le Security Assurance Specifications, o SCAS, che descrivono i requisiti e le procedure per verificarne la sicurezza.

Fonti:

- https://www.etsi.org/deliver/etsi_ts/133500_133599/133518/18.00.00_60/ts_133518v180000p.pdf
- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/02_capitolo.tex

## 3. Dagli SCAS al DSL

Tempo indicativo: 70 secondi.

Le specifiche SCAS sono scritte in linguaggio naturale, quindi il mio sistema non può interpretarle direttamente. Per automatizzare la verifica del risultato occorre rappresentare i criteri in una forma strutturata. Il Python qui è soltanto un esempio illustrativo di verifica scritta a mano, non codice del progetto. [Primo clic] Dall’analisi di diversi test ho identificato due operazioni comuni: selezionare i messaggi rilevanti e verificare che soddisfino certe condizioni. Nel caso NRF selezioniamo richiesta di discovery e risposta associata, poi controlliamo lo stato HTTP 403. Il requisito è qui sintetizzato, non citato letteralmente. [Secondo clic] Ho quindi progettato un DSL con costrutti riutilizzabili. SEQUENCE descrive la selezione e REQUIRE esprime il criterio. Questa è la sintassi reale del progetto. Le regole vengono scritte usando i costrutti del linguaggio: non ho realizzato una traduzione automatica NLP dalle specifiche.

Fonti:

- https://www.etsi.org/deliver/etsi_ts/133500_133599/133512/17.03.00_60/ts_133512v170300p.pdf (p. 9, ritaglio originale)
- https://www.etsi.org/deliver/etsi_ts/133500_133599/133518/18.00.00_60/ts_133518v180000p.pdf (p. 8, ritaglio originale)
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/dsl/nrf_sequence_test.dsl

## 4. Sistema di verifica

Tempo indicativo: 53 secondi.

Il secondo contributo è il sistema che interpreta le regole del DSL ed esegue la verifica. Parte da un file PCAP, cioè una cattura dei messaggi scambiati in rete durante il test, comprese le richieste e le risposte che ci interessano. Il sistema legge queste evidenze, non esegue il test. Estrae e normalizza i messaggi, seleziona quelli richiesti e applica le verifiche statiche o temporali, queste ultime tramite MonPoly. Il DSL guida sia la selezione sia la verifica. Infine genera un report con il verdetto e le evidenze che lo motivano.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/05_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/dsl/nrf_sequence_test.dsl

## 5. Testing sulle catture originali

Tempo indicativo: 50 secondi.

Ho valutato il sistema su 16 catture provenienti da test eseguiti su due implementazioni open source 5G, Open5GS e free5GC. Le evidenze sono state prodotte da strumenti di test separati dal verificatore. Per NRF e UDM sono stati adattati componenti di ScasDK, mentre non attribuisco tutte le catture allo stesso strumento. Ho ottenuto 12 PASS, un FAIL e tre INCONCLUSIVE: risultati coerenti con le rispettive evidenze. Il FAIL NRF segnala HTTP 200 dove il criterio richiede 403. Gli INCONCLUSIVE indicano evidenze insufficienti. I raggruppamenti in tabella corrispondono a dieci catture Open5GS e sei free5GC.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/06_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/18-baseline.html

## 6. Mutation testing

Tempo indicativo: 60 secondi.

I risultati baseline da soli non bastano a valutare la sensibilità del sistema, anche perché alcuni casi sono stati usati durante lo sviluppo. Ho quindi applicato modifiche controllate alle catture con un mutatore separato. Il mutatore usa la PCAP originale e i riferimenti alle evidenze contenuti nel report baseline per individuare i dati da alterare. La PCAP mutata viene analizzata dallo stesso sistema, con la stessa DSL. Il confronto dei verdetti deve corrispondere alla modifica introdotta: per esempio, il caso NRF passa da FAIL a PASS sostituendo HTTP 200 con 403. Nei 13 scenari completati ho ottenuto tutti i verdetti attesi. Dei 15 previsti, due scenari AMF Case B temporali e combinati non sono stati completati per limiti del mutatore. Uno sviluppo futuro è renderlo meno dipendente dalla forma specifica della regola DSL.

Fonti:

- https://github.com/desila23/5g-security-assurance-thesis/blob/TESI-LATEX/capitoli/06_capitolo.tex
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/mutation_testing/mutate_nrf_status.py
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/mutation_testing/mutate_udm_supi.py
- https://github.com/desila23/5g-security-assurance-thesis/blob/main/mutation_testing/fail/mutate_pfcp_fteid.py
- https://github.com/desila23/5g-security-assurance-thesis/blob/gh-pages/5g-thesis-presentation/slides/19-mutazioni.html
