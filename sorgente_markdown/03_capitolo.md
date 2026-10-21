# Definizione del problema e requisiti

## Formulazione del problema
I casi di test SCAS, descritti nel capitolo precedente, sono espressi attraverso specifiche **human-readable**, destinate quindi alla lettura e all'interpretazione umana. Sebbene questa rappresentazione sia adatta alla documentazione delle procedure e dei comportamenti attesi, non costituisce direttamente una specifica interpretabile da un motore automatico.

Per automatizzare la verifica dell'esito di un test è quindi necessario tradurre le informazioni rilevanti della specifica in una forma strutturata e interpretabile. Il problema può quindi essere ricondotto alla seguente domanda: *è possibile esprimere in forma machine-readable la logica necessaria a verificare l'esito di un test SCAS, utilizzando come evidenza il traffico di rete acquisito durante la sua esecuzione?*

## Dalla specifica SCAS alla rappresentazione dichiarativa
Il passaggio da una specifica scritta in linguaggio naturale a una rappresentazione strutturata non è immediato. Dalla descrizione del test è infatti necessario ricavare diverse informazioni operative, come i messaggi da osservare, il loro eventuale ordine, i campi da confrontare, i valori attesi e, quando previsto, i vincoli temporali da verificare.

In assenza di un livello dichiarativo intermedio, questa interpretazione tende a essere incorporata direttamente nel codice. Ne deriva un approccio fortemente *test-specifico*, nel quale l'introduzione di un nuovo caso di test può richiedere l'implementazione di nuova logica dedicata, comportando duplicazione del codice, forte accoppiamento tra specifica e implementazione e scarsa riusabilità.

Per separare le caratteristiche proprie del singolo test dalla logica generale del motore di verifica, viene quindi introdotto un **Domain-Specific Language (DSL)**. Il linguaggio permette di rappresentare in forma dichiarativa gli eventi da individuare nel traffico osservato e le proprietà che devono essere soddisfatte per determinare l'esito del test.

L'obiettivo non è riprodurre integralmente nella DSL la procedura descritta dalla specifica SCAS, ma esprimere soltanto i criteri necessari alla verifica dell'esito sulla base dell'evidenza disponibile. La variabilità tra test differenti può così essere trasferita, per quanto possibile, dal codice applicativo a regole interpretabili da un motore comune.

La progettazione del linguaggio richiede quindi di individuare quali capacità espressive siano necessarie per rappresentare le diverse tipologie di verifica emerse dall'analisi dei test.

## Capacità espressive richieste dalla DSL
Per definire le capacità espressive della DSL sono state analizzate le esigenze di verifica dei casi di test SCAS considerati, individuando gli elementi che devono poter essere rappresentati attraverso il linguaggio. Da questa analisi emergono due esigenze principali:
1. **Selezione dell'evidenza rilevante**.
	A seconda della natura del test, può essere necessario individuare una sequenza ordinata di eventi oppure raccogliere tutte le occorrenze di una determinata tipologia. Nel primo caso assumono rilevanza l'ordine degli eventi e l'eventuale presenza di sottoflussi opzionali; nel secondo, l'obiettivo è costruire una collezione di evidenze sulla quale valutare proprietà che coinvolgono più occorrenze.
	 
2. **Verifica delle proprietà sull'evidenza selezionata**.
	Una volta individuata l'evidenza, il linguaggio permette di esprimere criteri che determinano l'esito del test. Questi possono riguardare relazioni tra valori osservati in eventi differenti, confronti con valori attesi, proprietà riferite a un insieme di evidenze e, nei casi in cui il tempo costituisca parte del requisito, vincoli temporali tra eventi osservati.

Le capacità individuate derivano dalle esigenze emerse nell'analisi dei casi di test SCAS considerati. La tabella seguente mette in relazione ciascuna capacità espressiva con il costrutto introdotto nella DSL e con un caso di test in cui tale capacità viene utilizzata.

|Capacità|Costrutto DSL|Test SCAS in cui viene utilizzato|
|---|---|---|
|Riconoscere successioni ordinate di messaggi|`SEQUENCE`|NRF Discovery Authorization; UDM Resynchronization; UDM SUCI De-concealment; AMF Synchronization Failure; AMF RES* Verification Failure|
|Gestire eventi o sottoflussi opzionali|`OPTIONAL`|AMF RES* Verification Failure|
|Raccogliere occorrenze dello stesso tipo|`COLLECT`|UPF TEID Uniqueness|
|Confrontare valori osservati e attesi|`REQUIRE ==`, `!=`|NRF Discovery Authorization; UDM Resynchronization; AMF Synchronization Failure; AMF RES* Verification Failure|
|Verificare l'unicità di valori|`REQUIRE UNIQUE`|UPF TEID Uniqueness|
|Applicare criteri in base a condizioni|`IF`|AMF RES* Verification Failure|
|Verificare vincoli temporali|`MFOTL CASE`|AMF Synchronization Failure|
La tabella mostra come alcune capacità, quali il riconoscimento di sequenze e il confronto tra valori, siano utilizzate in più casi di test, mentre altre rispondano a esigenze più specifiche. 

## Obiettivi e requisiti di sistema
A partire dal problema individuato e dalle capacità espressive richieste alla DSL, è possibile definire gli obiettivi del sistema e i principali requisiti che ne guideranno la progettazione.

L'obiettivo principale è consentire l'introduzione di nuovi casi di test principalmente attraverso la definizione di una specifica DSL, evitando di sviluppare una pipeline dedicata per ciascun caso. Tale possibilità è subordinata al supporto dei protocolli e delle proprietà richieste dal test: esigenze non ancora gestite possono richiedere l'estensione dei normalizzatori o delle capacità espressive del linguaggio.

I principali requisiti individuati sono riportati nella tabella seguente:

| ID  | Requisito                             | Descrizione                                                                                                                                                              |
| --- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| R1  | Genericità                            | Il motore di verifica non deve dipendere da uno specifico caso di test SCAS.                                                                                             |
| R2  | Riusabilità                           | I componenti comuni devono poter essere riutilizzati tra test differenti.                                                                                                |
| R3  | Separazione delle responsabilità      | La logica relativa all'interpretazione dei protocolli deve essere separata dalla logica specifica del test.                                                              |
| R4  | Selezione dell’evidenza               | Il sistema deve consentire l'identificazione di eventi, sequenze e collezioni rilevanti ai fini della verifica.                                                          |
| R5  | Verifica statica                      | Il sistema deve poter verificare confronti, condizioni e proprietà definite sui valori osservati                                                                         |
| R6  | Verifica temporale                    | Il sistema deve consentire l'espressione e la valutazione di proprietà temporali.                                                                                        |
| R7  | Gestione dell’evidenza non conclusiva | Il sistema deve distinguere le violazioni dei criteri di verifica dalle situazioni in cui la selezione dell'evidenza non consente di determinare un verdetto conclusivo. |
| R8  | Tracciabilità                         | Il verdetto deve essere riconducibile all'evidenza osservata e ai relativi frame della cattura originale.                                                                |
| R9  | Riproducibilità                       | Il sistema deve conservare informazioni sufficienti a ripetere l'analisi nelle medesime condizioni.                                                                      |
| R10 | Reporting uniforme                    | Test differenti devono produrre risultati strutturati secondo uno schema comune.                                                                                         |
| R11 | Sensibilità alle variazioni           | Il sistema deve essere sensibile ad alterazioni controllate dell'evidenza che modificano il soddisfacimento dei criteri di verifica.                                     |
Questi requisiti costituiscono il riferimento per le scelte architetturali descritte nel Capitolo $4$.


## Scope e assunzioni
Il lavoro considera come sorgente primaria di evidenza le catture di traffico generate durante l'esecuzione dei test, pertanto la possibilità di effettuare una verifica dipende dalla disponibilità e dalla completezza delle informazioni osservabili nel file PCAP.

L'analisi sperimentale è focalizzata sulla **5G Core Network** e sui protocolli coinvolti nei casi di test considerati, e si assume che tali protocolli possano essere correttamente decodificati e trasformati in una rappresentazione strutturata utilizzabile dai componenti successivi della pipeline.

Queste assunzioni definiscono quindi il perimetro entro cui viene valutato il sistema proposto.
