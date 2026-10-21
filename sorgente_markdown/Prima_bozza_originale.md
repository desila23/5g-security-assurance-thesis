# 1. Introduzione
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


---

# 2. Background
## 2.1 Architettura 5G e implicazioni per la Security Assurance
L’architettura della 5G Core Network adotta un modello fortemente modulare, nel quale le principali funzionalità della rete sono distribuite tra componenti distinti, denominati **Network Functions (NF)**. \cite{3gpp_ts23501_2023} Ciascuna funzione svolge compiti specifici, come l’autenticazione degli utenti, la gestione della mobilità, la registrazione dei servizi o la gestione delle sessioni.

Le Network Functions del piano di controllo cooperano secondo il paradigma della **Service-Based Architecture (SBA)**, attraverso il quale espongono e utilizzano servizi mediante interfacce standardizzate. Tra le principali funzioni coinvolte nei casi di test considerati rientrano l'**AMF** (_Access and Mobility Management Function_), responsabile della registrazione e della mobilità degli utenti; l'**AUSF** (_Authentication Server Function_), coinvolta nell'autenticazione; l'**UDM** (_Unified Data Management_), che gestisce i dati degli abbonati; e l'**NRF** (_Network Repository Function_), che supporta la registrazione e la scoperta delle Network Functions. Sul piano utente opera invece l'**UPF** (_User Plane Function_), responsabile dell'instradamento e dell'elaborazione del traffico dati degli utenti. \cite{3gpp_ts23501_2023,3gpp_ts33501_2021}

La presenza di funzioni distinte e di numerose interazioni tra esse rende necessario valutare la sicurezza sia dei singoli componenti, sia dei comportamenti osservabili nelle comunicazioni. In questo contesto si inserisce il modello di **Security Assurance** sviluppato da GSMA e 3GPP, che comprende il **Network Equipment Security Assurance Scheme (NESAS)** e le **Security Assurance Specifications (SCAS)**.

Il NESAS definisce uno schema di valutazione della sicurezza delle apparecchiature di rete, comprendendo la valutazione dei processi di sviluppo e gestione del prodotto adottati dai fornitori. Le specifiche SCAS, sviluppate dal 3GPP, definiscono invece requisiti di sicurezza e relativi casi di test tecnici per valutare le diverse funzioni di rete, costituendo il riferimento normativo per le verifiche affrontate nel presente lavoro. \cite{gsma_fs13_2025,gsma_fs63_2025}


## 2.2 Test SCAS ed evidenze di verifica
Le specifiche SCAS organizzano i requisiti di sicurezza attraverso casi di test tecnici, progettati per verificare il comportamento delle Network Functions rispetto alle proprietà definite dal 3GPP. Ciascun test descrive una procedura di verifica e i risultati attesi, fornendo un riferimento per la sua esecuzione e documentazione. \cite{3gpp_ts33117_2019,3gpp_tr33916_2024}

La descrizione di un test case comprende generalmente i seguenti elementi:
- **Test Name:** identificatore e denominazione del caso di test;
- **Purpose:** obiettivo della verifica e proprietà di sicurezza considerata;
- **Pre-Conditions:** condizioni iniziali necessarie all'esecuzione;
- **Execution Steps:** operazioni da eseguire durante il test;
- **Expected Results:** comportamento atteso per il soddisfacimento del requisito;
- **Expected Format of Evidence:** indicazioni sulle evidenze da raccogliere a supporto della valutazione.

A titolo esemplificativo, si consideri il test `TC_DISC_AUTHORIZATION_SLICE_NRF`, relativo all'autorizzazione delle richieste di discovery presso l'NRF. Una rappresentazione semplificata della specifica è riportata di seguito \cite{3gpp_ts33518_2024}. 
```
Test Case Name: TC_DISC_AUTHORIZATION_SLICE_NRF

Purpose:
	Verify that the NRF rejects a slice-specific NF discovery request 
	when the requested NF instance does not allow discovery from the requester's network slice.

Pre-Conditions:
	- NF1 and NF2 are authenticated with the NRF.
	- NF1 belongs to slice B.
	- NF2 allows discovery only from slice A.

Execution Steps
	1. NF2 registers its slice information with the NRF.
	2. NF1 sends an NF discovery request targeting NF2.
	3. The NRF evaluates the slice-specific authorization conditions.

Expected Results:
	The NRF returns a 403 Forbidden response.
	
Expected Format of Evidence:
	Evidence suitable for the interface
```

Come illustrato nell'esempio, oltre alla procedura e al risultato atteso, la descrizione del test può specificare anche le evidenze da raccogliere, tra cui catture di traffico di rete (PCAP), log applicativi e di sistema e documentazione dei risultati. Le catture PCAP consentono, in particolare, di osservare i messaggi scambiati tra i componenti della rete, i valori dei campi protocollari e le informazioni temporali associate alle comunicazioni.

La disponibilità di tali evidenze permette di documentare il comportamento osservato durante il test, ma non implica che tutte le proprietà di sicurezza siano direttamente osservabili nel traffico acquisito. Le informazioni necessarie alla valutazione dipendono infatti dalla natura del requisito e dalle modalità con cui il test viene eseguito.


---

# 3. Definizione del problema e requisiti
## 3.1 Formulazione del problema
I casi di test SCAS, descritti nel capitolo precedente, sono espressi attraverso specifiche **human-readable**, destinate quindi alla lettura e all'interpretazione umana. Sebbene questa rappresentazione sia adatta alla documentazione delle procedure e dei comportamenti attesi, non costituisce direttamente una specifica interpretabile da un motore automatico.

Per automatizzare la verifica dell'esito di un test è quindi necessario tradurre le informazioni rilevanti della specifica in una forma strutturata e interpretabile. Il problema può quindi essere ricondotto alla seguente domanda: *è possibile esprimere in forma machine-readable la logica necessaria a verificare l'esito di un test SCAS, utilizzando come evidenza il traffico di rete acquisito durante la sua esecuzione?*

## 3.2 Dalla specifica SCAS alla rappresentazione dichiarativa
Il passaggio da una specifica scritta in linguaggio naturale a una rappresentazione strutturata non è immediato. Dalla descrizione del test è infatti necessario ricavare diverse informazioni operative, come i messaggi da osservare, il loro eventuale ordine, i campi da confrontare, i valori attesi e, quando previsto, i vincoli temporali da verificare.

In assenza di un livello dichiarativo intermedio, questa interpretazione tende a essere incorporata direttamente nel codice. Ne deriva un approccio fortemente *test-specifico*, nel quale l'introduzione di un nuovo caso di test può richiedere l'implementazione di nuova logica dedicata, comportando duplicazione del codice, forte accoppiamento tra specifica e implementazione e scarsa riusabilità.

Per separare le caratteristiche proprie del singolo test dalla logica generale del motore di verifica, viene quindi introdotto un **Domain-Specific Language (DSL)**. Il linguaggio permette di rappresentare in forma dichiarativa gli eventi da individuare nel traffico osservato e le proprietà che devono essere soddisfatte per determinare l'esito del test.

L'obiettivo non è riprodurre integralmente nella DSL la procedura descritta dalla specifica SCAS, ma esprimere soltanto i criteri necessari alla verifica dell'esito sulla base dell'evidenza disponibile. La variabilità tra test differenti può così essere trasferita, per quanto possibile, dal codice applicativo a regole interpretabili da un motore comune.

La progettazione del linguaggio richiede quindi di individuare quali capacità espressive siano necessarie per rappresentare le diverse tipologie di verifica emerse dall'analisi dei test.

## 3.3 Capacità espressive richieste dalla DSL
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

## 3.4 Obiettivi e requisiti di sistema
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


## 3.5 Scope e assunzioni
Il lavoro considera come sorgente primaria di evidenza le catture di traffico generate durante l'esecuzione dei test, pertanto la possibilità di effettuare una verifica dipende dalla disponibilità e dalla completezza delle informazioni osservabili nel file PCAP.

L'analisi sperimentale è focalizzata sulla **5G Core Network** e sui protocolli coinvolti nei casi di test considerati, e si assume che tali protocolli possano essere correttamente decodificati e trasformati in una rappresentazione strutturata utilizzabile dai componenti successivi della pipeline.

Queste assunzioni definiscono quindi il perimetro entro cui viene valutato il sistema proposto.


---

# 4. Architettura proposta
## 4.1 Architettura generale
A partire dai requisiti definiti nel Capitolo 3, l'architettura proposta è stata organizzata in componenti con responsabilità distinte, separando le fasi di estrazione e interpretazione del traffico, selezione dell'evidenza, verifica dei criteri e produzione del report finale. Questa suddivisione consente di limitare l'accoppiamento tra i diversi livelli della pipeline e di favorire la riusabilità dei componenti.

Il sistema utilizza due input principali: la cattura di traffico, che costituisce la sorgente primaria dell'evidenza osservata, e la specifica DSL, che definisce gli eventi da individuare e i criteri da verificare.

La loro elaborazione è organizzata attraverso il file di configurazione `tests.json`, nel quale vengono specificati, per ciascun caso di test, i percorsi della cattura e delle regole DSL, le sorgenti protocollari da analizzare e la destinazione del report. La configurazione può inoltre comprendere parametri aggiuntivi, come le modalità di correlazione degli eventi, le informazioni necessarie alla verifica temporale ed eventuali binding esterni o derivati.

[Inserire figura dell'architettura generale]

La pipeline trasforma progressivamente il traffico osservato in una rappresentazione adatta alla verifica. Le prime fasi riguardano l'estrazione, la normalizzazione e, quando necessaria, la risoluzione semantica degli eventi di rete; successivamente, la specifica DSL guida la selezione dell'evidenza rilevante e l'applicazione dei criteri di verifica. Il processo termina con la determinazione del verdetto e la produzione di un report strutturato contenente le evidenze utilizzate.

## 4.2 Estrazione strutturata del traffico
Il file PCAP costituisce la sorgente osservabile dell'analisi, ma il contenuto della cattura non viene elaborato direttamente dai componenti successivi della pipeline. È quindi necessaria una fase preliminare di estrazione, che trasformi i pacchetti acquisiti in una rappresentazione strutturata dei dati osservati.

A tale scopo viene utilizzato **TShark**, un analizzatore di protocolli di rete che applica i _dissector_ dei protocolli presenti nella cattura e rende accessibili i relativi campi decodificati. L'estrazione avviene mediante l'opzione `-T ek`, che produce record strutturati in formato JSON, consentendo alla pipeline di operare sui campi decodificati anziché sui byte grezzi dei pacchetti. \cite{wireshark_tshark_docs}

La rappresentazione prodotta mantiene ancora la struttura e la terminologia esposte da TShark e può comprendere sia informazioni generali associate ai pacchetti, come numero di frame, timestamp e indirizzi IP, sia campi propri dei protocolli decodificati, come identificatori degli stream HTTP/2, tipi di messaggio NAS, campi PFCP e payload applicativi.

In questa fase non viene ancora attribuita una rappresentazione semantica uniforme agli eventi osservati né viene selezionata l'evidenza rilevante per uno specifico caso di test. L'output strutturato ottenuto dalla cattura costituisce invece l'ingresso della successiva fase di **normalizzazione protocol-specifica**.

## 4.3 Normalizzazione protocol-specifica
L'output strutturato ottenuto nella fase precedente conserva ancora una rappresentazione fortemente eterogenea: nomi dei campi, struttura dei dati e modalità con cui le informazioni vengono esposte variano in funzione del protocollo decodificato. Utilizzare direttamente tale rappresentazione nei moduli successivi introdurrebbe una dipendenza dai dettagli specifici del protocollo.

Per ridurre questo accoppiamento, viene introdotto un livello di **normalizzazione protocol-specifica**.  A ciascun protocollo supportato è associato un normalizzatore incaricato di interpretare i campi estratti e ricondurli a una rappresentazione comune di eventi osservati, denominata `MessageEvent`. La struttura comune conserva informazioni generali, come numero di frame, timestamp, sorgente e destinazione, insieme ai dati specifici del messaggio e alle eventuali informazioni necessarie alla sua correlazione o ricostruzione.

Le operazioni svolte dipendono dalle caratteristiche del protocollo. Per NAS e PFCP, le informazioni necessarie sono generalmente riconducibili ai singoli messaggi e possono essere rappresentate direttamente come eventi semanticamente identificati.

Per HTTP/2, invece, è necessaria una ricostruzione più articolata, poiché le informazioni relative a una stessa interazione applicativa possono essere distribuite su più frame. Il normalizzatore correla le informazioni utilizzando gli identificatori `tcp.stream` e `http2.streamid`, ricostruisce richieste e risposte con i relativi dati applicativi e conserva i riferimenti ai frame coinvolti.

La struttura comune adottata può essere schematizzata attraverso i principali attributi del `MessageEvent`:
```python
class MessageEvent:
    frame_number: int
    timestamp: float
    protocol: str
    kind: str
	
    src: str | None = None
    dst: str | None = None
	
    message_type: str | None = None
	
    related_frames: list[int] = field(default_factory=list)
	
    correlation: dict[str, Any] = field(default_factory=dict)
	
    fields: dict[str, Any] = field(default_factory=dict)
```

I normalizzatori attualmente implementati riguardano **NAS, HTTP/2 e PFCP**. Il loro compito è quindi descrivere in modo uniforme ciò che è stato osservato nel traffico, senza incorporare logica specifica del test. La selezione dell'evidenza rilevante viene effettuata nelle fasi successive.

L'output della normalizzazione è quindi costituito da una sequenza di `MessageEvent`, che rappresenta il formato comune utilizzato dal resto del sistema.

## 4.4 Risoluzione semantica
La normalizzazione produce eventi rappresentati secondo una struttura comune, ma in alcuni casi il loro significato applicativo non è ancora completamente esplicito. Ciò avviene soprattutto per messaggi relativi alle interazioni della Service-Based Architecture, dove i messaggi HTTP/2 possono rappresentare operazioni differenti in funzione del servizio richiesto e del contenuto applicativo.

Per gestire questa esigenza, viene introdotto un **resolver semantico**, incaricato di interpretare gli eventi normalizzati e associarli a tipologie coerenti con il dominio 5G. Ad esempio, analizzando il percorso della richiesta HTTP/2, il resolver può riconoscere un'operazione di _NF Discovery_ presso l'NRF e classificare gli eventi correlati come `nrf.discovery.request` e `nrf.discovery.response`.

Il resolver opera quindi ad un livello di astrazione superiore rispetto ai normalizzatori, in quanto non ricostruisce nuovamente i messaggi, ma utilizza le informazioni già disponibili per completarne l'interpretazione e rendere esplicito il tipo semantico degli eventi. Questi ultimi possono così essere selezionati attraverso i riferimenti dichiarati nella DSL.

## 4.5 Selezione dell'evidenza tramite DSL
Al termine delle fasi precedenti, il traffico è stato trasformato in una sequenza di eventi strutturati e, quando necessario, semanticamente risolti. Non tutti questi eventi sono però rilevanti per il caso di test considerato, ed è quindi necessario individuare quelli richiesti dalla specifica per procedere alla verifica.

Questa operazione è guidata dalla DSL, che mette a disposizione i costrutti sintattici `SEQUENCE` e `COLLECT`, utilizzati rispettivamente per descrivere successioni ordinate di eventi e collezioni di occorrenze dello stesso tipo. Le caratteristiche dell'evidenza da ricercare vengono così definite attraverso la regola dichiarativa, anziché essere incorporate nella logica di selezione.

Gli eventi individuati vengono associati agli identificatori simbolici definiti nella DSL, denominati **alias**. Tali associazioni, dette _binding_, consentono di riferirsi all'evidenza selezionata indipendentemente dalla sua posizione nella cattura. A seconda del costrutto utilizzato, un alias può identificare un singolo evento oppure una collezione di eventi.

I binding vengono raccolti in un `BindingContext`, che costituisce la rappresentazione dell'evidenza selezionata e il punto di collegamento con i successivi meccanismi di verifica.


## 4.6 Verifica
Una volta costruito il `BindingContext`, l'evidenza individuata può essere valutata rispetto ai criteri definiti per il caso di test. La DSL non descrive infatti soltanto quali eventi debbano essere ricercati, ma anche le proprietà che devono essere verificate sull'evidenza ottenuta.

La fase di verifica riceve quindi il `BindingContext` insieme ai criteri espressi nella specifica e determina se il comportamento osservato soddisfi le condizioni previste.
Nell'architettura sono previste due modalità complementari di verifica: **statica** e **temporale**.

La **verifica statica** opera direttamente sui valori contenuti nei binding e consente di esprimere proprietà quali uguaglianza (`==`), disuguaglianza (`!=`) e unicità (`UNIQUE`). È quindi utilizzata quando il risultato del test dipende dal confronto o dalle proprietà dei dati estratti dagli eventi selezionati. La valutazione di tali proprietà è affidata a un verificatore statico dedicato.

La **verifica temporale**, invece, viene utilizzata in casi in cui il criterio dipende dalle relazioni temporali tra gli eventi, ad esempio la loro occorrenza entro determinati intervalli. Tali proprietà vengono espresse mediante la **Metric First Order Temporal Logic (MFOTL)** e valutate attraverso **MonPoly**; il loro funzionamento verrà approfondito nel Capitolo $5$. 

I risultati delle verifiche statiche e temporali contribuiscono alla determinazione del verdetto complessivo del caso di test, secondo le modalità approfondite nella Sezione $5.8$.

## 4.7 Reporting
Il verdetto prodotto dalla fase di verifica rappresenta il risultato conclusivo dell'analisi, ma da solo non è sufficiente a descrivere come tale risultato sia stato ottenuto. È necessario conservarlo insieme ai criteri valutati e all'evidenza che ha contribuito alla decisione, in modo da rendere l'esito interpretabile e riconducibile ai dati osservati.

A questo scopo, l'ultimo componente dell'architettura è un reporter generico, comune ai diversi casi di test, che organizza i risultati in un documento strutturato in formato `JSON`. Lo schema rimane uniforme indipendentemente dal test eseguito, mentre il contenuto varia in funzione della specifica utilizzata, dell'evidenza disponibile e delle verifiche realmente applicate.

Il report mette quindi in relazione tre elementi principali: la **sorgente dell'analisi**, i **criteri di verifica** insieme con i relativi **risultati** e l'**evidenza osservata**; a questi si aggiungono le informazioni identificative del test, la configurazione dell'esecuzione e una spiegazione sintetica dell'esito complessivo.

Una rappresentazione ridotta della struttura è la seguente:
```json
{
    "metadata": {
        "generator": "generic_verification_pipeline",
        "tshark_version": "..."
    },
    "test": {
        "id": "..."
    },
    "source": {
        "pcap": "...",
        "sha256": "..."
    },
    "configuration": {
        "pipeline": "...",
        "rules": "...",
        "traffic": { }
    },
    "criteria": [ ... ],
    "verification": {
        "results": [ ... ],
        "overall_verdict": "PASS"
    },
    "evidence": {
        "bindings": { ... }
    },
    "explanation": {
        "summary": "..."
    },
    "verdict": "PASS"
}
```
In particolare, ogni risultato di verifica conserva il riferimento al criterio valutato e ai frame che ne costituiscono l'evidenza, mentre la sezione `evidence` riporta i binding prodotti nelle fasi precedenti. Il report mantiene così il collegamento tra il verdetto finale, le proprietà valutate e gli eventi della cattura da cui tale valutazione è stata ricavata.

La stessa struttura contribuisce anche alla **riproducibilità** dell'analisi: il riferimento al file PCAP e il relativo hash SHA-256 permettono di identificare la sorgente esaminata, mentre le informazioni sulla configurazione e sulla versione di TShark documentano alcune delle condizioni in cui è stata eseguita la verifica.


---

# 5. Domain-Specific Language e motore di verifica
## 5.1 Progettazione della DSL
La progettazione della DSL parte dai requisiti individuati nel Capitolo 3 e dall'esigenza di rappresentare, in forma dichiarativa, gli elementi del test necessari alla verifica. Il linguaggio è stato quindi definito a partire dalle caratteristiche ricorrenti osservate nei casi di test considerati, privilegiando un insieme limitato di capacità direttamente riconducibili alle esigenze del dominio.

La DSL è stata mantenuta volutamente circoscritta, privilegiando un equilibrio tra espressività e semplicità. L'obiettivo non è fornire un linguaggio generale per l'analisi del traffico di rete, ma definire una sintassi compatta e leggibile, capace di esprimere i criteri di verifica considerati senza esporre i dettagli dei protocolli e dei componenti sottostanti. A tale scopo, le regole utilizzano il vocabolario semantico prodotto dalle fasi di normalizzazione e risoluzione, anziché i campi originariamente estratti dalla cattura.

A livello strutturale, una specifica distingue due responsabilità: la descrizione dell'evidenza da ricercare e la definizione delle proprietà da valutare su di essa. Questa separazione si riflette direttamente nella grammatica del linguaggio: alla prima infatti appartengono i costrutti dedicati all'individuazione di eventi, mentre alla seconda appartengono le espressioni utilizzate dai meccanismi di verifica statica e temporale.

Le scelte progettuali descritte costituiscono la base della grammatica presentata nella sezione successiva, nella quale vengono formalizzati i costrutti sintattici e le relative modalità di composizione.

## 5.2 Struttura della grammatica
La sintassi della DSL è formalizzata mediante una grammatica definita con Lark, una libreria Python che consente di descrivere grammatiche formali e costruire un parser in grado di riconoscere le strutture da esse definite. 
Una specifica è composta da una sequenza di statement, ciascuno dei quali appartiene a una delle due categorie introdotte nella Sezione precedente: la descrizione dell'evidenza da individuare e la definizione dei criteri da applicare su di essa.

Per la selezione dell'evidenza, la grammatica mette a disposizione i costrutti `SEQUENCE` e `COLLECT`. Il primo consente di dichiarare una successione di eventi, ciascuno identificato attraverso un tipo semantico e associato a un alias mediante la parola chiave `AS`. All'interno di una sequenza possono inoltre essere presenti blocchi `OPTIONAL`, utilizzati per indicare porzioni della specifica la cui presenza non è obbligatoria.
`COLLECT` utilizza la stessa associazione tra tipo di evento e alias, ma attraverso una forma sintattica distinta.

I criteri applicati all'evidenza selezionata vengono invece espressi principalmente attraverso la parola chiave `REQUIRE`. La grammatica ammette confronti mediante gli operatori `==` e `!=`, nei quali l'operando può essere un valore letterale oppure il riferimento a un altro campo della specifica. È inoltre previsto il costrutto `REQUIRE UNIQUE`, dedicato all'espressione di proprietà di unicità, e il costrutto `IF`, che consente di raggruppare una o più regole di verifica sotto una determinata condizione. Il comportamento di questi costrutti durante la valutazione verrà approfondito nella Sezione $5.6$. 

Le proprietà temporali sono rappresentate separatamente mediante il costrutto `MFOTL`, che verrà approfondito nella Sezione $5.7$.

Le principali produzioni della grammatica sono riportate di seguito in forma semplificata, omettendo per brevità le definizioni lessicali dei terminali.
```
start: statement+

?statement: sequence_rule
          | collect_rule
          | rule

?rule: static_rule
     | temporal_rule

?static_rule: comparison_rule
            | unique_rule
            | if_rule

sequence_rule: "SEQUENCE" "{" sequence_element+ "}"
?sequence_element: sequence_item | optional_block
sequence_item: FIELD "AS" NAME
optional_block: "OPTIONAL" "{" sequence_element+ "}"

collect_rule: "COLLECT" FIELD "AS" NAME

comparison_rule: "REQUIRE" FIELD OP operand
unique_rule: "REQUIRE" "UNIQUE" FIELD
if_rule: "IF" FIELD OP operand "{" rule+ "}"

temporal_rule: "MFOTL" "CASE" VALUE MFOTL_BLOCK

?operand: FIELD -> field_operand
        | VALUE -> literal_operand
```

I riferimenti agli eventi e ai relativi attributi sono rappresentati attraverso `FIELD`, che utilizza una notazione gerarchica separata da punti. Nella parte dedicata alla selezione, ad esempio, è possibile dichiarare: 
```
SEQUENCE {
    ausf.authentication.response AS initial_vector
    nas.authentication_request AS auth_request
}
``` 

In questo esempio, i due eventi semantici vengono associati rispettivamente agli alias `initial_vector` e `auth_request`, attraverso i quali è possibile accedere ai relativi campi nelle successive regole di verifica:
```
REQUIRE auth_request.rand == initial_vector.rand
```

`NAME` identifica gli alias introdotti dalla specifica, mentre `VALUE` rappresenta valori letterali utilizzabili nelle espressioni. Gli operatori di confronto attualmente previsti sono `==` e `!=`.

La grammatica definisce in questo modo il vocabolario e le forme sintattiche attraverso cui viene espressa la specifica del test. Il passaggio dalla rappresentazione testuale alle strutture interne utilizzate dai componenti successivi viene descritto nella sezione seguente.

## 5.3 Rappresentazione interna delle regole
Per interpretare le regole scritte nella DSL, il sistema utilizza un parser che produce inizialmente una rappresentazione sintattica della specifica. Tale rappresentazione viene successivamente trasformata, mediante un `Transformer` di Lark, in strutture interne più semplici e direttamente utilizzabili dai componenti successivi.

Questa trasformazione consente di **separare la sintassi concreta del linguaggio dalla logica che  ne utilizza il contenuto**. Il matcher e i verificatori non operano quindi direttamente sul testo della DSL, ma su rappresentazioni strutturate che conservano esclusivamente le informazioni necessarie all'elaborazione.

A seconda dello statement considerato, vengono mantenute informazioni differenti, quali il tipo di operatore, i riferimenti ai campi, gli alias, gli operandi di confronto, eventuali regole annidate e, nel caso di proprietà temporali, la relativa formula.

Ad esempio, una regola come 
```
REQUIRE initial_auth.rand == initial_vector.rand
```

viene trasformata concettualmente in una struttura del tipo:
```
field: initial_auth.rand
operator: ==
expected:
	type: field
	value: initial_vector.rand
```
In questo modo viene mantenuta anche la distinzione tra un operando costituito da un valore letterale e un operando che rappresenta invece il riferimento a un altro campo della specifica.

Per il costrutto `SEQUENCE`, la rappresentazione ottenuta dal parsing viene ulteriormente trasformata in un **Abstract Syntax Tree (AST)** dedicato alla descrizione del pattern sequenziale. I tipi di nodo attualmente necessari sono:
- `Sequence`, che rappresenta l'insieme ordinato degli elementi del pattern;
- `Atom`, associato a un singolo tipo di evento atteso e al relativo alias;
- `Optional`, utilizzato per racchiudere elementi la cui presenza è opzionale.

Ad esempio, la specifica
```
SEQUENCE {
	event.a AS a
	OPTIONAL {
		event.b AS b
	}
	event.c AS c
}
```

può essere rappresentata concettualmente attraverso il seguente albero:
```
Sequence
├── Atom(event.a, a)
├── Optional
│   └── Atom(event.b, b)
└── Atom(event.c, c)
```

È importante precisare che **non tutti gli elementi della DSL vengono trasformati nello stesso AST**.  La struttura composta da `Sequence`, `Atom` e `Optional` è specificamente utilizzata per rappresentare i pattern sequenziali, mentre le regole statiche e temporali vengono mantenute in strutture interne adatte ai rispettivi meccanismi di verifica.

Le rappresentazioni ottenute costituiscono quindi il livello di collegamento tra il parsing della specifica e i componenti incaricati della sua elaborazione. 

## 5.4 Selezione mediante `SEQUENCE`
Questa sezione descrive il meccanismo utilizzato per individuare, all'interno del traffico osservato, le sequenze di eventi definite attraverso il costrutto `SEQUENCE`.

### 5.4.1 Il pattern sequenziale
La selezione tramite `SEQUENCE` richiede di individuare, all'interno della traccia di eventi, una successione di messaggi che rispetti l'ordine specificato nella DSL.

Una possibile soluzione consisterebbe nell'implementare un algoritmo di ricerca dedicato a ciascuna sequenza. Tale approccio richiederebbe tuttavia di adattare la logica di riconoscimento alle diverse strutture dei pattern, limitando la generalità del sistema.

L'approccio adottato consiste invece nel compilare il pattern, precedentemente rappresentato mediante un AST, in un **automa a stati finiti non deterministico**. L'automa descrive formalmente gli eventi attesi e le possibili transizioni degli stati, fornendo una rappresentazione del pattern indipendente dallo specifico caso di test.

### 5.4.2 Formalizzazione dell'automa
Per rappresentare i pattern sequenziali viene utilizzato un **Nondeterministic Finite Automaton (NFA)**, che può essere formalizzato mediante la quintupla: 
$$
A = \langle \Sigma, \ Q, \ q_{0}, \ Q_{F}, \ \delta \rangle
$$
dove
- $\Sigma$ è l'alfabeto, costituito dall'insieme dei **tipi semantici di evento** riconosciuti dall'automa;
- $Q$ è l'insieme finito degli stati;
- $q_{0} \in Q$ è lo stato iniziale;
- $Q_{F} \subseteq Q$ è l'insieme degli stati finali. Nell'implementazione proposta viene utilizzato un unico stato di accettazione, pertanto $Q_{F} = \{ q_{f} \}$;
- $\delta$ è la funzione di transizione non deterministica, definita come $$\delta: Q \times (\Sigma \ \cup \ \{  \varepsilon \}) \to \mathcal{P}(Q)$$dove $\mathcal{P}(Q) = 2^{Q}$ indica l'insieme delle parti di $Q$, ossia l'insieme di tutti i suoi sottoinsiemi.

A differenza degli automi tradizionalmente impiegati per il riconoscimento di stringe, l'alfabeto considerato non è costituito da caratteri, ma dai tipi semantici associati ai `MessageEvent` prodotti dalle fasi precedenti della pipeline.

L'automa definisce quindi le possibili successioni di eventi ammesse dal pattern, mentre il **matcher**
è il componente incaricato di utilizzarlo per individuare le corrispondenze all'interno della traccia osservata. Il funzionamento di tale componente verrà approfondito dopo aver descritto il processo di costruzione dell'automa.

### 5.4.3 Le $\varepsilon$-transizioni
Una transizione ordinaria richiede di consumare un simbolo dell'alfabeto, ossia la lettura di un evento il cui tipo semantico corrisponda a quello atteso dalla transizione. Tale operazione può essere rappresentata come:$$
q_{i} \xrightarrow{a} q_{j}
$$
dove $a \in \Sigma$ è il tipo di evento richiesto per passare dallo stato $q_{i}$ allo stato $q_{j}$.

Una transizione $\varepsilon$, invece, ha la forma $$
q_{i} \xrightarrow{\varepsilon} q_{j}
$$
e permette di passare da uno stato all'altro **senza consumare alcun evento**, ossia senza avanzare nella lettura della traccia.

Questa possibilità è fondamentale per la costruzione dei pattern sequenziali, in particolare per rappresentare blocchi `OPTIONAL`. Le modalità con cui tali transizioni vengono introdotte nell'automa saranno approfondite nella sezione successiva, dedicata alla costruzione di Thompson.

### 5.4.4 Compilazione del pattern mediante Thompson
Una volta ottenuto l'AST, il pattern sequenziale viene compilato in un NFA mediante la **costruzione di Thompson**. \cite{thompson_1968} Tale procedimento si basa su un approccio composizionale: a ciascun nodo dell'albero viene associato un frammento dell'automa, dotato di uno stato iniziale e uno finale; i frammenti vengono successivamente collegati per ottenere l'automa corrispondente alla sequenza completa.

La costruzione dipende dal tipo di nodo considerato:
- **Atom:** genera un frammento costituito da due stati collegati da una transizione etichettata con il tipo semantico dell'evento atteso.
- **Sequence:** combina i frammenti dei propri elementi nell'ordine specificato, collegando lo stato finale di ciascun frammento allo stato iniziale del successivo mediante una transizione $\varepsilon$. 
- **Optional:** introduce due percorsi alternativi mediante transizioni $\varepsilon$. Il primo attraversa il frammento corrispondente agli elementi opzionali, mentre il secondo permette di raggiungere direttamente lo stato di uscita, senza consumare gli eventi contenuti nel blocco.

Considerando il pattern sequenziale già introdotto nella Sezione 5.3, il compilatore costruisce i frammenti relativi ai singoli nodi dell'AST e li collega mediante transizioni ε, ottenendo un automa che ammette sia il percorso completo `a → b → c`, sia quello in cui l'evento opzionale viene omesso, `a → c`.

[Inserire figura: NFA generato dalla costruzione di Thompson per la sequenza con OPTIONAL; VOGLIO AVERE UNA FIGURA CHE PERMETTE DI SEPARARE costruzione dei frammenti + unione di questi]

### 5.4.5 Configurazioni attive e riconoscimento degli eventi
L'automa costruito mediante Thompson descrive i percorsi ammessi dal pattern, ma non conosce informazioni sugli eventi effettivamente presenti nella cattura. Il suo utilizzo è affidato al **matcher**, che riceve in ingresso l'NFA e la sequenza ordinata di `MessageEvent`, con il compito di individuare i percorsi che consentono di raggiungere lo stato finale.

Durante questa operazione non è sufficiente conoscere lo stato raggiunto nell'automa, poiché è necessario conservare anche i riferimenti agli eventi che hanno contribuito al riconoscimento. A questo scopo viene introdotta una struttura denominata `ActiveConfiguration`, formalizzabile  come: $$C = \langle q, B \rangle$$
dove 
- $q \in Q$ è lo stato corrente dell'automa;
- $B$ è una funzione parziale che associa gli alias definiti nella DSL ai `MessageEvent` già riconosciuti.

Il matcher può mantenere contemporaneamente più configurazioni attive, ciascuna caratterizzata dal proprio stato e dai binding progressivamente costruiti.

Poiché l'automa può contenere transizioni $\varepsilon$, per ogni stato corrente devono essere considerati anche quelli raggiungibili senza consumare ulteriori eventi. A tale scopo viene utilizzata una $\varepsilon \text{-closure}$, definita formalmente come: $$\varepsilon\text{-closure}(q) = \{ p \in Q \mid q \xrightarrow{ \ \ \varepsilon^{*} \ } p\}$$
La chiusura comprende tutti gli stati raggiungibili da $q$ attraverso zero o più transizioni $\varepsilon$, incluso lo stesso $q$ . L'espansione di una configurazione attraverso tali transizioni mantiene invariati i binding già acquisiti, poiché non viene riconosciuto alcun nuovo evento.

Durante la scansione della traccia, il matcher confronta il `message_type` di ciascun evento con quello richiesto dalle transizioni uscenti dagli stati delle configurazioni attive. Quando viene individuata una transizione compatibile, la configurazione avanza verso lo stato di destinazione e il `MessageEvent` osservato viene associato all'alias definito nel corrispondente `Atom`. I binding vengono quindi aggiornati e vengono considerate le ulteriori transizioni $\varepsilon$ raggiungibili dal nuovo stato.

Una caratteristica importante è che la selezione non richiede che gli eventi previsti dal pattern siano consecutivi nella traccia. Quando un evento non può essere consumato da una determinata configurazione, quest'ultima può rimanere attiva, consentendo di proseguire la ricerca con gli eventi successivi, fatta salva la politica di riavvio del candidato descritta nella sezione successiva.

La possibilità di mantenere più configurazioni attive consente inoltre di seguire contemporaneamente i percorsi alternativi prodotti da `OPTIONAL`, senza dover stabilire anticipatamente se gli eventi opzionali saranno presenti. Le modalità con cui vengono avviati e gestiti i diversi tentativi di riconoscimento saranno approfondite nella sezione successiva.

### 5.4.6 Politica di matching e produzione dei risultati
All'interno di una cattura possono essere presenti più occorrenze degli eventi descritti sulla stessa `SEQUENCE`, anche in posizioni differenti della traccia. Il matcher deve quindi essere in grado di riconoscere il pattern senza presupporre che questo abbia inizio con il primo evento osservato. A tale scopo, ogni volta che incontra un evento compatibile con l'inizio della sequenza, avvia un nuovo **candidato di riconoscimento**, ossia un tentativo indipendente di individuare tutti gli eventi richiesti dal pattern a partire da quella posizione. La compatibilità viene determinata considerando le transizioni disponibili a partire dallo stato iniziale dell'NFA, comprese quelle raggiungibili attraverso $\varepsilon \text{-transizioni}$.

Durante l'elaborazione di ciascun candidato viene applicata una specifica **politica di riavvio (*restart policy*)**, introdotta per evitare che eventi appartenenti a tentativi distinti vengano associati alla stessa sequenza. In particolare, quando viene osservato un evento che potrebbe avviare un nuovo riconoscimento, il matcher verifica se questo possa essere consumato dalle configurazioni attive del candidato corrente. Qualora nessuna di esse risulti compatibile, il tentativo viene interrotto, lasciando che l'evento possa costituire il punto di partenza di un nuovo candidato.

Il riconoscimento si considera completo quando almeno una configurazione raggiunge lo stato finale dell'NFA. Il matcher produce allora un oggetto `Match`, nel quale vengono conservate la posizione iniziale del candidato (`start_index`), la posizione in cui è stato raggiunto lo stato finale (`end_index`) e le associazioni tra alias ed eventi riconosciuti (`bindings`). Per ciascun candidato viene considerato il primo punto di completamento, nel quale possono tuttavia essere presenti più configurazioni accettanti, corrispondenti a percorsi differenti dell'automa.

Questa possibilità assume particolare rilevanza in presenza di blocchi `OPTIONAL`, poiché percorsi diversi possono completare il riconoscimento nello stesso intervallo della traccia, pur avendo individuato quantità differenti di evidenza. Per gestire tali situazioni viene adottato un **criterio di dominanza**, attraverso il quale vengono eliminati i match che risultano meno completi rispetto ad altri equivalenti. Un match domina un altro soltanto quando vengono rispettate le seguenti condizioni:
- i due match condividono `start_index` e `end_index`;
- gli alias del secondo costituiscono un sottoinsieme proprio di quelli del primo;
- per tutti gli alias comuni, le associazioni fanno riferimento agli stessi eventi osservati.
In questo modo vengono eliminati i match che non aggiungono evidenza rispetto ad altri più completi, preservando quelli che contengono associazioni differenti tra alias ed eventi.

Al termine del processo, il matcher restituisce l'insieme dei match completi individuati, ciascuno corredato dai relativi binding. Tali associazioni possono essere successivamente trasferite in un `BindingContext`, rendendo l'evidenza selezionata disponibile ai meccanismi di verifica descritti nelle sezioni successive.


## 5.5 Selezione mediante `COLLECT`
Non tutti i casi di test richiedono il riconoscimento di una successione ordinata di eventi. In alcuni casi, l'evidenza necessaria è costituita dall'insieme delle occorrenze di una determinata tipologia, indipendentemente dall'ordine con cui queste compaiono nella traccia.
Per rispondere a tale esigenza, la DSL introduce il costrutto `COLLECT`, che consente di selezionare tutti i `MessageEvent` corrispondenti a uno specifico tipo semantico.

Una regola di raccolta può essere espressa come segue:
```
COLLECT pfcp.session_establishment_response AS responses
```
In questo esempio, `pfcp.session_establishment_response` identifica il tipo di evento da ricercare, mentre `responses` è l'alias assegnato alla collezione risultante.
La selezione avviene confrontando il `message_type` degli eventi disponibili con quello indicato nella regola, senza richiedere la costruzione di un automa.

Gli eventi individuati vengono associati all'alias all'interno del `BindingContext`. A differenza di `SEQUENCE`, dove ciascun alias identifica un singolo evento riconosciuto, nel caso di `COLLECT` il valore associato è una lista di `MessageEvent`, rappresentabile come: $$
B(\texttt{responses}) = [e_1, e_2, e_3, ..., e_n]
$$
La struttura del `BindingContext` rimane quindi invariata, mentre cambia la natura dell'evidenza associata all'alias. Le due modalità di selezione, pur adottando meccanismi differenti, producono così una rappresentazione comune dei risultati.


## 5.6 Verifica statica
Entrambe le modalità di selezione descritte nelle Sezioni precedenti producono un `BindingContext` contenente l'evidenza individuata. Il verificatore statico riceve tale contesto insieme alle regole di verifica ottenute dal parsing della DSL, con il compito di valutare le proprietà richieste sui dati precedentemente selezionati, senza effettuare ulteriori ricerche nella cattura.

Le regole di confronto sono introdotte dalla parola chiave `REQUIRE` e possono essere espresse nella forma generale:
```
REQUIRE alias.campo OP valore
```
dove OP identifica l'operatore di confronto, mentre l'operando a destra può essere un valore letterale oppure un riferimento a un altro campo.

Per effettuare la valutazione, il verificatore deve innanzitutto risolvere i riferimenti presenti nella regola. Nel caso di un binding associato a un singolo evento, viene individuato l'alias interno del `BindingContext` e recuperato il relativo `MessageEvent`. Il percorso gerarchico specificato nella DSL viene quindi utilizzato per accedere ai campi, anche annidati, contenuti nell'attributo `fields` dell'evento. 
Quando invece il binding contiene una collezione, il campo richiesto viene recuperato da ciascuna evidenza, conservando anche il riferimento ai frame da cui proviene.
Il medesimo meccanismo consente inoltre di accedere a informazioni esterne o derivate, eventualmente aggiunte al `BindingContext`, attraverso gli stessi riferimenti gerarchici utilizzati per gli eventi selezionati.

Una volta risolti gli operandi, il verificatore applica l'operatore richiesto. I confronti attualmente supportati sono l'uguaglianza (`==`) e la disuguaglianza (`!=`), utilizzabili sia per confrontare un valore osservato con un valore atteso, sia per stabilire relazioni tra campi appartenenti a eventi differenti.

Accanto ai confronti, la DSL prevede il criterio `REQUIRE UNIQUE`, utilizzato per verificare proprietà di unicità su un insieme di valori osservati. In questo caso il verificatore esamina i valori recuperati dalle diverse occorrenze della collezione, considerando anche gli eventuali campi contenenti più elementi. I valori vengono confrontati per individuare quelli presenti in eventi distinti e, quando vengono rilevate ripetizioni, il sistema conserva i relativi frame di provenienza. Tale meccanismo supporta anche valori strutturati, che vengono ricondotti a una rappresentazione confrontabile senza alterarne il contenuto.

Oltre ai criteri precedenti, il linguaggio supporta verifiche condizionali attraverso il costrutto `IF`, il quale permette di subordinare l'applicazione di una o più regole al soddisfacimento di una condizione preliminare. Il verificatore valuta inizialmente la condizione attraverso gli operatori di confronto già descritti e, soltanto quando questa risulta soddisfatta, procede con la valutazione delle regole contenute nel blocco. In caso contrario, le regole interne non vengono eseguite e il blocco viene contrassegnato come `SKIPPED`. 
Tale indicazione riguarda esclusivamente la mancata applicazione della verifica condizionale e non costituisce un ulteriore verdetto del caso di test.

Per ciascuna regola valutata, il verificatore produce un risultato strutturato contenente il criterio applicato, i valori osservati e attesi, e l'esito della valutazione. Possono inoltre essere incluse informazioni aggiuntive, come i valori duplicati e i relativi frame nel caso di `UNIQUE`.
Questa scelta consente di superare una verifica limitata alla sola restituzione di un esito, fornendo le informazioni necessarie alla successiva generazione di un report che, oltre al verdetto, documenta le evidenze utilizzate e permette di ricostruire le motivazioni alla base del risultato ottenuto.


## 5.7 Verifica temporale
La valutazione delle proprietà temporali è affidata all'integrazione tra le formule **MFOTL (Metric First-Order Temporal Logic)** \cite{basin_mfotl_2015} dichiarate nella DSL e **MonPoly** \cite{basin_monpoly_2017}, uno strumento di monitoraggio utilizzato per verificare tali formule su tracce temporizzate. In questo modo MFOTL definisce le proprietà da controllare attraverso predicati e operatori temporali, mentre MonPoly ne valuta il soddisfacimento rispetto agli eventi osservati.

All'interno della DSL, una proprietà temporale può essere dichiarata mediante il costrutto:
```
MFOTL CASE X """
	...
"""
```

La grammatica permette di associare una formula MFOTL a uno specifico caso della procedura considerata. Questa scelta consente di integrare il formalismo senza doverne implementare direttamente gli operatori e la relativa logica di valutazione, delegando tale compito a MonPoly.

Per effettuare la verifica, il sistema recupera gli eventi riconosciuti durante la selezione e ne utilizza i timestamp per costruire una traccia temporizzata nel formato richiesto da MonPoly. La corrispondenza tra gli alias degli eventi selezionati e i predicati temporali è definita nella configurazione del caso di test, che indica anche la signature contenente le dichiarazioni dei predicati riconosciuti dal monitor.

La preparazione della formula prevede inoltre la sostituzione del parametro `{TIMER_MS}` con il valore dell'intervallo temporale configurato per il caso di test. In questo modo, il vincolo temporale può essere specificato attraverso la configurazione, senza richiedere modifiche al codice del verificatore.
Una volta preparati gli input, il sistema richiama MonPoly con l'opzione `-negate` e ne interpreta l'output per individuare eventuali violazioni della proprietà temporale e produrre il relativo risultato di verifica.

Anche in questo caso, il risultato non si limita all'indicazione dell'esito, ma conserva le informazioni disponibili sulla valutazione effettuata.

## 5.8 Determinazione del verdetto
Una volta completata la selezione dell'evidenza e l'eventuale valutazione dei criteri statici e temporali, il sistema deve determinare l'esito complessivo del caso di test. A tale scopo, non è sufficiente distinguere tra condizioni soddisfatte e violate, perché possono verificarsi situazioni in cui l'evidenza disponibile non consente di effettuare una valutazione conclusiva.

Per gestire queste situazioni, il sistema prevede tre possibili verdetti: **PASS**, quando l'evidenza selezionata consente di verificare il soddisfacimento dei criteri richiesti; **FAIL**, quando viene rilevata una violazione; e **INCONCLUSIVE**, quando non è possibile formulare una valutazione conclusiva, ad esempio per l'assenza dell'evidenza necessaria o per l'impossibilità di individuare un'unica corrispondenza completa.

Nel caso della selezione mediante `SEQUENCE`, quest'ultima situazione può verificarsi quando nessun percorso dell'NFA raggiunge uno stato accettante. In assenza di un match completo, infatti, il sistema non dispone dei binding necessari per procedere alla verifica e restituisce `INCONCLUSIVE`. Lo stesso verdetto viene assegnato quando vengono individuati più match completi, poiché l'attuale implementazione richiede una selezione univoca per valutare i criteri.
Analogamente, nel caso di `COLLECT`, l'assenza di eventi corrispondenti al tipo semantico richiesto impedisce la valutazione dei criteri e determina un esito `INCONCLUSIVE`.

Per i casi di test che prevedono sia verifiche statiche che temporali, il verdetto complessivo viene determinato considerando i risultati di entrambe. Il test assume esito `PASS` quando tutti i criteri applicabili risultano soddisfatti e `FAIL` quando almeno uno di essi rileva una violazione. Qualora, invece, non sussistano le condizioni per una valutazione conclusiva, viene restituito `INCONCLUSIVE`, secondo i principi precedentemente descritti.

La determinazione del verdetto conclude il processo di verifica, distinguendo le violazioni effettivamente rilevate dai casi in cui l'evidenza non consente una valutazione conclusiva, mentre i risultati strutturati delle singole verifiche permettono di documentare nel report le motivazioni dell'esito ottenuto.


---

# 6. Testing e Mutation testing
## 6.1 Obiettivi e metodologia della validazione
La validazione sperimentale del sistema proposto ha l'obiettivo di valutare la capacità della pipeline di applicare criteri di verifica dichiarativi a differenti casi di test SCAS, utilizzando come evidenza le informazioni ricavate dalle catture di traffico di rete.

L'analisi considera casi di test relativi a diverse funzioni della 5G Core Network, selezionati per esaminare le principali capacità introdotte nella DSL e descritte nei capitoli precedenti.

La valutazione viene inoltre integrata attraverso un'attività di _mutation testing_, ispirata all'impiego di alterazioni controllate per valutare la capacità di un sistema di verifica di individuare comportamenti non conformi \cite{jia_harman_mutation_2011}. Nel presente lavoro le mutazioni vengono applicate alle catture di traffico, anziché al codice del verificatore, e le evidenze così ottenute vengono analizzate mediante la stessa pipeline. Il confronto tra gli esiti originali e quelli successivi alla mutazione consente di valutare se il sistema rilevi le variazioni introdotte quando queste modificano il soddisfacimento dei criteri dichiarati, distinguendo anche i casi in cui l'evidenza diventa insufficiente per formulare un verdetto conclusivo.

## 6.2 Ambiente sperimentale e casi di test
Per la sperimentazione dell'architettura proposta sono stati utilizzati i seguenti ambienti e strumenti:
- **Open5GS** \cite{open5gs_docs}, implementazione open-source della 5G Core Network, utilizzata per le catture relative ai test NRF, UDM e UPF;
- **free5GC** \cite{free5gc_docs}, altra implementazione open-source della 5G Core Network, da cui provengono le catture relative ai test AMF Synchronization Failure e RES* Verification Failure;
- **ScasDK** \cite{mancini_scasdk_2025}, piattaforma per l'esecuzione automatizzata di test di sicurezza SCAS, utilizzata come riferimento e attraverso componenti adattati per alcuni casi di test, in particolare NRF e UDM.

Il sistema proposto opera su catture di traffico già disponibili. L'esecuzione delle procedure SCAS e la generazione del traffico rimangono quindi distinte dalla verifica dell'esito e non rientrano tra le funzionalità della pipeline sviluppata, in accordo con il perimetro definito nella Sezione $3.5$.

I casi considerati fanno riferimento alle specifiche SCAS dedicate alle funzioni NRF, UDM, AMF e UPF \cite{3gpp_ts33518_2024,3gpp_ts33514_2021,3gpp_ts33512_2022,3gpp_ts33513_2023}.

I casi di test considerati e i verdetti ottenuti sulle rispettive catture originali sono riportati nella tabella seguente:

| Caso di test                | Protocolli  | Criterio di verifica                          | Costrutti DSL                           | Verdetto baseline |
| --------------------------- | ----------- | --------------------------------------------- | --------------------------------------- | ----------------- |
| NRF Discovery Authorization | HTTP/2      | Risposta HTTP 403                             | `SEQUENCE`, `REQUIRE`                   | FAIL              |
| UDM Resynchronization       | HTTP/2      | Coerenza parametri di autenticazione          | `SEQUENCE`, `REQUIRE`                   | PASS              |
| UDM SUCI De-concealment     | HTTP/2      | SUPI restituito uguale al valore atteso       | `SEQUENCE`, `REQUIRE`                   | PASS              |
| AMF Sync Failure A          | NAS, HTTP/2 | Coerenza messaggi e risposta AUSF entro T3520 | `SEQUENCE`, `REQUIRE`, MFOTL            | PASS              |
| AMF Sync Failure B          | NAS, HTTP/2 | Coerenza messaggi e vincolo T3520             | `SEQUENCE`, `REQUIRE`, MFOTL            | PASS              |
| UPF TEID Uniqueness         | PFCP        | Assenza di F-TEID duplicati                   | `COLLECT`, `UNIQUE`                     | PASS              |
| AMF RES* A–D                | NAS, HTTP/2 | Gestione fallimento autenticazione            | `SEQUENCE`, `OPTIONAL`, `IF`, `REQUIRE` | PASS (4/4)        |

I verdetti riportati rappresentano l'esito della verifica dei criteri dichiarati rispetto all'evidenza osservata. Un risultato `FAIL` non indica quindi necessariamente un malfunzionamento della pipeline, ma può corrispondere alla corretta rilevazione di un criterio non soddisfatto. È il caso del test NRF, nel quale la risposta osservata presenta uno status HTTP `200`, mentre la regola DSL richiede `403`.


## 6.3 Valutazione delle capacità di verifica
In questa sezione vengono approfonditi tre gruppi di casi di test, selezionati per esaminare il comportamento delle principali capacità di verifica implementate. L'analisi si concentra sull'evidenza individuata e sui risultati ottenuti, mentre la valutazione delle alterazioni introdotte nelle catture viene affrontata nella Sezione $6.4$.
### 6.3.1 AMF Synchronization Failure - Case B
Il test `AMF Synchronization Failure - Case B` permette di esaminare contemporaneamente tre componenti del sistema: la selezione mediante `SEQUENCE`, la verifica statica sui campi degli eventi e la verifica temporale attraverso MonPoly.

Il caso riguarda la gestione di un fallimento di sincronizzazione durante la procedura di autenticazione 5G AKA. A seguito della ricezione di un'`Authentication Request`, l'UE segnala un `Authentication Failure` con causa di sincronizzazione e fornisce il parametro `AUTS` necessario alla risincronizzazione. L'AMF inoltra quindi le informazioni necessarie all'AUSF. Nel Case B viene inoltre verificato che non venga inviata una nuova `Authentication Request` entro il limite temporale `T3520` considerato.

[INSERIRE SEQUENCE DIAGRAM: AMF Synchronization Failure – Case B, con UE, AMF, AUSF, scambio dei messaggi e intervallo T3520]

La specifica DSL del caso descrive la successione degli eventi attesi e i criteri statici da valutare:
```
SEQUENCE {
    ausf.authentication.response AS initial_vector
    nas.authentication_request AS initial_auth
    nas.authentication_failure AS sync_failure
    ausf.resynchronization.request AS resync
    ausf.authentication.response AS new_vector
    nas.authentication_request AS subsequent_auth_request
}

REQUIRE initial_auth.rand == initial_vector.rand
REQUIRE sync_failure.cause == 21
REQUIRE resync.auts == sync_failure.auts
REQUIRE resync.rand == initial_auth.rand
```

A questa si affianca la proprietà temporale MFOTL, che richiede l'assenza di una successiva `Authentication Request` entro l'intervallo configurato dopo il fallimento di sincronizzazione:
```
MFOTL CASE B """
	SyncFailure()
	IMPLIES
	NOT EVENTUALLY[0,{TIMER_MS}] AuthenticationRequest()
"""
```

L'esecuzione del test ha prodotto un unico match completo, associando agli alias dichiarati gli eventi individuati nella cattura. Il report registra quattro verifiche statiche, tutte con esito `PASS`:
- corrispondenza del `RAND` tra risposta `AUSF` iniziale e l'Authentication Request;
- presenza della causa `NAS 21` nell'Authentication Failure;
- corrispondenza di `AUTS` tra l'Authentication Failure e la richiesta di risincronizzazione;
- corrispondenza del `RAND` iniziale con quello utilizzato nella richiesta di risincronizzazione.

Anche la verifica temporale produce `PASS`. Nella cattura, l'`Authentication Failure` viene individuato al frame `358`, mentre la successiva `Authentication Request` compare al frame `606`, circa 25 secondi dopo. Tale intervallo supera il limite T3520 configurato a 15 secondi, risultando quindi coerente con la proprietà temporale dichiarata.

Il verdetto complessivo è `PASS`. L'aspetto significativo di questo risultato non è soltanto il soddisfacimento dei criteri, ma la possibilità di selezionare e valutare, attraverso la stessa pipeline, eventi provenienti da protocolli differenti, confrontarne i valori mediante una rappresentazione comune e applicare anche vincoli temporali.


### 6.3.2 UPF TEID Uniqueness
Il test `UPF TEID Uniqueness` permette di esaminare il funzionamento del costrutto `COLLECT` e del criterio di verifica `REQUIRE UNIQUE`, utilizzati per raccogliere più occorrenze dello stesso tipo di evento e verificare una proprietà sull'insieme dei valori osservati, senza imporre un ordinamento tra i messaggi.

Il caso riguarda la verifica dell'unicità degli `F-TEID`, identificatori utilizzati per distinguere i tunnel GTP-U associati al traffico del piano utente. Durante l'instaurazione delle sessioni PFCP, l'UPF comunica tali identificatori attraverso i messaggi `PFCP Session Establishment Response`.
Il test richiede di raccogliere le risposte osservate e verificare che gli `F-TEID` assegnati non vengano riutilizzati tra eventi differenti.

[INSERIRE FIGURA – Estrazione e raccolta delle evidenze UPF: cinque PFCP Session Establishment Responses, F-TEID associati ai rispettivi frame e costruzione della collezione `responses` tramite `COLLECT`.]

La specifica DSL utilizzata è la seguente:
```
COLLECT pfcp.session_establishment_response AS responses

REQUIRE UNIQUE responses.f_teids
```

La prima istruzione raccoglie tutti gli eventi corrispondenti al tipo semantico indicato, associandoli all'alias `responses`. La seconda applica il criterio di unicità ai valori `F-TEID` contenuti nella collezione, rappresentati come coppie strutturate `{teid, ipv4}`.

Nella cattura analizzata, il sistema ha individuato **5 risposte PFCP**, corrispondenti ai frame 37, 38, 46, 47 e 48, dalle quali sono stati estratti complessivamente **10 F-TEID**, due per ciascuna risposta. Sebbene gli identificatori condividano lo stesso indirizzo IPv4, i rispettivi valori TEID risultano differenti. Non essendo stata rilevata alcuna coppia `{teid, ipv4}` duplicata tra eventi distinti, il verificatore restituisce il verdetto complessivo `PASS`.

Il risultato mostra come il sistema possa verificare proprietà che coinvolgono più occorrenze dello stesso tipo di evento, utilizzando una modalità di selezione distinta da `SEQUENCE` e mantenendo la stessa rappresentazione comune dell'evidenza attraverso `BindingContext`.


### 6.3.3 AMF RES* Verification Failure - Cases A/B/C/D
Il test `AMF RES* Verification Failure` permette di esaminare l'utilizzo congiunto dei costrutti `OPTIONAL` e `IF`, attraverso i quali una stessa specifica DSL può rappresentare percorsi differenti e applicare criteri di verifica condizionali.

Il caso riguarda la gestione di un fallimento nella verifica della risposta di autenticazione `RES*` durante le procedure 5G AKA. Le quattro varianti considerate differiscono per il percorso di identificazione della UE e per l'origine del fallimento. In particolare, l'identificazione può avvenire direttamente tramite SUCI oppure attraverso un'identificazione iniziale mediante GUTI, seguita da una richiesta d'identità. Il fallimento può invece essere rilevato localmente dall'AMF oppure comunicato dall'AUSF.

Le combinazioni considerate sono riportate nella tabella seguente:

|Caso|Identificazione|Origine del fallimento|Eventi opzionali presenti|
|---|---|---|---|
|A|SUCI diretto|AMF|Nessuno|
|B|GUTI → SUCI|AMF|Identity Request/Response|
|C|SUCI diretto|AUSF|Confirmation Request/Response|
|D|GUTI → SUCI|AUSF|Entrambi i gruppi|
[INSERIRE FIGURA – Percorsi alternativi del test AMF RES* Verification Failure: sequenza comune, identificazione opzionale e conferma AUSF opzionale, con indicazione dei casi A/B/C/D.]

La specifica DSL utilizza un'unica `SEQUENCE` contenente due blocchi `OPTIONAL`, rispettivamente dedicati agli scambi di identificazione e alla conferma dell'autenticazione con l'AUSF. I criteri comuni verificano la coerenza dei parametri `RAND` e `AUTN` e la presenza dell'`Authentication Reject` finale. Attraverso i blocchi `IF`, vengono inoltre applicate le verifiche specifiche del percorso d'identificazione e dell'origine del fallimento.

```
SEQUENCE {
    nas.registration_request AS registration_request
	
    OPTIONAL {
        nas.identity_request AS identity_request
        nas.identity_response AS identity_response
    }
	
    ausf.authentication.response AS authentication_vector
    nas.authentication_request AS authentication_request
    nas.authentication_response AS authentication_response
	
    OPTIONAL {
        ausf.confirmation.request AS ausf_confirmation_request
        ausf.confirmation.response AS ausf_confirmation_response
    }
	
    nas.authentication_reject AS authentication_reject
}

REQUIRE authentication_vector.rand == authentication_request.rand
REQUIRE authentication_vector.autn == authentication_request.autn
REQUIRE authentication_reject.present == true

IF case.identity_path == direct_suci {
    REQUIRE registration_request.identity_type == SUCI
}

IF case.identity_path == guti_then_suci {
    REQUIRE registration_request.identity_type == 5G_GUTI
    REQUIRE identity_request.requested_identity == SUCI
    REQUIRE identity_response.identity_type == SUCI
}

IF case.failure_source == local {
    REQUIRE hres_star.value != authentication_vector.hxres_star
}

IF case.failure_source == ausf {
    REQUIRE hres_star.value == authentication_vector.hxres_star
    REQUIRE authentication_response.res_star == ausf_confirmation_request.res_star
    REQUIRE ausf_confirmation_response.auth_result == AUTHENTICATION_FAILURE
}
```

Oltre ai binding prodotti dal matcher attraverso il riconoscimento degli eventi della sequenza, la specifica utilizza informazioni aggiuntive fornite al verificatore. In particolare, `case.identity_path` e `case.failure_source` sono *binding di configurazione* che identificano rispettivamente il percorso di identificazione e l'origine del fallimento previsti dalla variante del test, mentre `hres_star.value` è un *binding derivato*, calcolato a partire dai parametri di autenticazione. Questi valori, pur non essendo ottenuti direttamente dal matcher, vengono integrati nel `BindingContext` insieme agli eventi selezionati, permettendo alla DSL di utilizzarli nelle regole di verifica.

L'esecuzione ha prodotto un match completo per ciascuna delle quattro catture, riconoscendo correttamente la presenza o l'assenza dei gruppi di eventi opzionali. I risultati delle verifiche sono riportati nella tabella seguente:

|Caso|Criteri riportati|PASS|SKIPPED|Verdetto|
|---|---|---|---|---|
|A|9|7|2|PASS|
|B|11|9|2|PASS|
|C|11|9|2|PASS|
|D|13|11|2|PASS|
La differenza nel numero di criteri riportati dipende dalle verifiche applicabili a ciascuna variante. Tutti i casi condividono tre regole `REQUIRE` iniziali e quattro condizioni `IF`, ma il numero di regole interne eseguite varia in funzione del percorso osservato. Nel Case A, ad esempio, l'identificazione diretta tramite `SUCI` e il fallimento locale richiedono una verifica aggiuntiva ciascuno; mentre, nel Case D, il percorso `GUTI → SUCI` e il fallimento comunicato dall'AUSF comportano tre verifiche aggiuntive per ciascuno dei due aspetti.

Nel report, anche le condizioni `IF` soddisfatte vengono registrate come criteri con esito `PASS`, mentre i blocchi non applicabili sono contrassegnati come `SKIPPED`, senza valutare le relative regole interne.
Tutte le varianti producono un verdetto complessivo `PASS`, e questo risultato mostra come una singola specifica dichiarativa possa adattarsi a percorsi di autenticazione differenti, mantenendo comuni le verifiche condivise e applicando soltanto i criteri pertinenti nel caso considerato.


## 6.4 Mutation testing
Per poter valutare la capacità del sistema di rilevare alterazioni dell'evidenza osservata sono state realizzate procedure di mutazione specifiche per i casi di test considerati, attraverso le quali vengono introdotte modifiche controllate alle catture di traffico originali.

Queste procedure appartengono all'infrastruttura sperimentale e non intervengono nell'interpretazione delle regole DSL o nella logica del verificatore. Le catture originali e quelle mutate vengono infatti sottoposte agli stessi meccanismi di selezione e verifica, permettendo di osservare se le alterazioni introdotte producano i cambiamenti di risultato attesi.

Per ciascun caso di test sono state introdotte una o più alterazioni controllate, selezionate in funzione dei criteri definiti nella relativa specifica DSL. La tabella seguente riporta le modifiche apportate alle catture, il verdetto ottenuto sull'evidenza originale e quello restituito dopo la mutazione.

|Caso di test|Alterazione introdotta|Baseline|Mutato|
|---|---|---|---|
|**NRF Discovery Authorization**|Modifica dello status HTTP da `200` a `403`|FAIL|PASS|
|**UDM Resynchronization**|Alterazione del parametro RAND|PASS|FAIL|
|**UDM SUCI De-concealment**|Alterazione del SUPI restituito|PASS|FAIL|
|**AMF Sync Failure – A**|Alterazione di RAND nella richiesta di risincronizzazione|PASS|FAIL|
|↳|Modifica dei tempi per violare il vincolo T3520|PASS|FAIL|
|↳|Combinazione delle due alterazioni|PASS|FAIL|
|**AMF Sync Failure – B**|Alterazione di RAND nella richiesta di risincronizzazione|PASS|FAIL|
|↳|Modifica dei tempi per violare il vincolo T3520|PASS|FAIL|
|↳|Combinazione delle due alterazioni|PASS|FAIL|
|**UPF TEID Uniqueness**|Introduzione di una coppia F-TEID duplicata|PASS|FAIL|
|↳|Rimozione delle risposte PFCP rilevanti|PASS|INCONCLUSIVE|
|**AMF RES* – A**|Alterazione di HRES* per invalidare il confronto locale|PASS|FAIL|
|**AMF RES* – B**|Alterazione di HRES* per invalidare il confronto locale|PASS|FAIL|
|**AMF RES* – C**|Alterazione dell'esito della conferma AUSF|PASS|FAIL|
|**AMF RES* – D**|Alterazione dell'esito della conferma AUSF|PASS|FAIL|

Un risultato particolarmente significativo riguarda il test `AMF Sync Failure`, per il quale sono state introdotte tre varianti di mutazione, applicate sia al Case A sia al Case B. Le alterazioni sono state progettate per violare separatamente i criteri statici, i vincoli temporali e infine entrambi. Sebbene il verdetto complessivo sia `FAIL` in tutte le varianti, i risultati dei due componenti di verifica permettono di distinguere quali criteri siano stati violati.

| Mutazione | Verifica statica | Verifica temporale |
| --------- | ---------------- | ------------------ |
| Statica   | FAIL             | PASS               |
| Temporale | PASS             | FAIL               |
| Combinata | FAIL             | FAIL               |
Quando viene alterato il parametro `RAND`, il verificatore statico rileva l'incoerenza tra i valori associati agli eventi, mentre il vincolo temporale rimane soddisfatto. Viceversa, modificando gli intervalli temporali tra gli eventi, le condizioni statiche rimangono valide, ma la formula `MFOTL` non risulta soddisfatta. La combinazione delle due mutazioni produce il fallimento di entrambi i componenti. Questo comportamento evidenzia come le verifiche statiche e temporali possano individuare violazioni differenti sulla stessa evidenza.

Un secondo risultato rilevante emerge dal test `UPF TEID Uniqueness`. L'introduzione di un F-TEID duplicato determina un verdetto `FAIL`, poiché viene violato il requisito di unicità, mentre la rimozione delle risposte PFCP necessarie alla verifica produce `INCONCLUSIVE`, in quanto il sistema non dispone dell'evidenza sufficiente per valutare il criterio.

Complessivamente, nei **15 scenari di mutazione considerati**, i verdetti osservati corrispondono a quelli attesi. I risultati forniscono evidenza sperimentale della capacità del sistema di rilevare le alterazioni introdotte, utilizzando gli stessi meccanismi di selezione e verifica applicati alle catture originali. Tale valutazione rimane tuttavia circoscritta ai casi e alle mutazioni esaminati e non costituisce una dimostrazione di correttezza generale del verificatore.


---

# 7. Discussioni, conclusioni e sviluppi futuri
I risultati ottenuti permettono di rispondere positivamente, nell'ambito dei casi di test considerati, alla domanda posta all'inizio del lavoro: è possibile rappresentare in forma interpretabile i criteri necessari a verificare l'esito di un test SCAS a partire dal traffico osservato. La sperimentazione ha mostrato che tale approccio può essere applicato a requisiti differenti senza dover sviluppare una logica di verifica dedicata per ogni caso, pur richiedendo una fase di interpretazione della specifica per individuare le proprietà effettivamente verificabili.

Un aspetto emerso dal lavoro è che la definizione di un criterio e la possibilità di valutarlo sono due questioni distinte. Anche quando una proprietà può essere espressa nella DSL, la sua verifica dipende dalla disponibilità di evidenze sufficienti nella cattura e dalla possibilità di ricavarne le informazioni necessarie. La distinzione tra `FAIL` e `INCONCLUSIVE` assume quindi un significato importante: l'assenza di evidenze sufficienti per valutare un requisito non equivale all'osservazione di una sua violazione.

Queste considerazioni definiscono anche i limiti dei risultati raggiunti. La DSL supporta attualmente un insieme circoscritto di proprietà e la validazione riguarda un numero selezionato di casi SCAS e di mutazioni controllate. Non è pertanto possibile concludere che qualsiasi requisito di sicurezza possa essere verificato attraverso il solo traffico di rete, né che i risultati ottenuti siano generalizzabili a ogni possibile scenario.

Per ampliare l'applicabilità del sistema, una possibile direzione di sviluppo consisterebbe nell'esaminare requisiti SCAS più diversificati, individuando le proprietà non ancora esprimibili attraverso la DSL e le informazioni che gli attuali normalizzatori non sono in grado di ricavare.
Questo permetterebbe di orientare l'estensione del linguaggio e dei meccanismi di estrazione verso esigenze di verifica concrete, mantenendo la riusabilità dei componenti comuni. Un approccio analogo potrebbe essere adottato anche per il *mutation testing*, introducendo strategie di generazione delle mutazioni più generali, eventualmente guidate dalle regole dichiarative per individuare gli eventi e i campi da alterare, pur mantenendo le operazioni di modifica specifiche dei diversi protocolli.

Il lavoro costituisce quindi un primo passo verso una verifica degli esiti SCAS maggiormente sistematica e riutilizzabile, il cui ambito di applicazione rimane strettamente legato alle proprietà esprimibili e all'evidenza effettivamente osservabile.