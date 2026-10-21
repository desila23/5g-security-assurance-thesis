# Introduzione
L'evoluzione delle reti mobili verso la quinta generazione ha introdotto architetture caratterizzate da una maggiore modularità e da numerose interazioni tra funzioni di rete distinte. In questo contesto, la valutazione della sicurezza assume un ruolo rilevante, poiché richiede di verificare non soltanto le proprietà dei singoli componenti, ma anche i comportamenti osservabili durante le comunicazioni tra essi.

Per supportare tale attività, il 3GPP definisce le _Security Assurance Specifications_ (SCAS), che comprendono requisiti di sicurezza e relativi casi di test per le diverse funzioni della rete 5G. \cite{gsma_fs13_2025,gsma_fs63_2025} Questi test descrivono le procedure da eseguire e i risultati attesi, fornendo un riferimento per valutare il comportamento dei componenti rispetto ai requisiti previsti.

Sebbene le specifiche SCAS definiscano il comportamento atteso durante l'esecuzione dei test, la verifica dei risultati richiede di confrontare tali aspettative con quanto effettivamente osservato. Questo passaggio diventa particolarmente rilevante quando la valutazione viene effettuata a partire dalle catture di traffico di rete, poiché è necessario riconoscere, tra le comunicazioni acquisite, quelle significative per il requisito considerato e stabilire se soddisfino le condizioni previste dalla specifica.

Il presente lavoro affronta questo problema proponendo un **Domain-Specific Language (DSL)** per rappresentare in forma dichiarativa i criteri necessari alla verifica degli esiti di test SCAS a partire da catture di traffico di rete. L'obiettivo è separare le caratteristiche specifiche dei singoli test dalla logica generale di verifica, favorendo il riutilizzo dei componenti e riducendo la necessità di sviluppare procedure dedicate per ciascun caso.

A tale scopo è stato progettato e implementato un sistema che estrae informazioni dalle catture di rete, le trasforma in eventi strutturati e seleziona le evidenze rilevanti sulla base delle regole DSL. Il linguaggio consente di descrivere sequenze ordinate di eventi, raccogliere occorrenze di una determinata tipologia ed esprimere criteri di verifica sui valori osservati. Il processo produce un verdetto accompagnato dai riferimenti alle evidenze utilizzate, distinguendo tra criteri soddisfatti, violazioni rilevate e situazioni nelle quali non è possibile formulare una valutazione conclusiva.

Per valutare il sistema sviluppato, sono stati considerati diversi casi di test SCAS relativi alle funzioni della 5G Core Network, caratterizzati da differenti requisiti di sicurezza e modalità di verifica. La validazione è stata inoltre approfondita mediante attività di *mutation testing*, introducendo alterazioni controllate nelle catture originali per verificare se il sistema fosse in grado di riconoscere le modifiche rilevanti e restituire i verdetti attesi.

L'elaborato è organizzato come segue:
- **Capitolo 2 – Background:** introduce il contesto delle reti 5G e delle specifiche SCAS, descrivendo la struttura dei test e il ruolo delle evidenze.
- **Capitolo 3 – Definizione del problema e requisiti:** presenta il problema affrontato, le capacità espressive richieste alla DSL e i requisiti del sistema.
- **Capitolo 4 – Architettura proposta:** descrive l'architettura del sistema e le responsabilità dei suoi componenti.
- **Capitolo 5 – Domain-Specific Language e motore di verifica:** approfondisce la progettazione della DSL e il funzionamento dei meccanismi di selezione e verifica.
- **Capitolo 6 – Testing e Mutation testing:** illustra la validazione sperimentale e i risultati ottenuti attraverso i test e le mutazioni controllate.
- **Capitolo 7 – Discussione, conclusioni e sviluppi futuri:** discute i risultati raggiunti, i limiti dell'approccio e le possibili direzioni di sviluppo.
