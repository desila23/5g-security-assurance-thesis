# Testing e Mutation testing

## Obiettivi e metodologia della validazione
La validazione sperimentale del sistema proposto ha l'obiettivo di valutare la capacità della pipeline di applicare criteri di verifica dichiarativi a differenti casi di test SCAS, utilizzando come evidenza le informazioni ricavate dalle catture di traffico di rete.

L'analisi considera casi di test relativi a diverse funzioni della 5G Core Network, selezionati per esaminare le principali capacità introdotte nella DSL e descritte nei capitoli precedenti.

La valutazione viene inoltre integrata attraverso un'attività di _mutation testing_, ispirata all'impiego di alterazioni controllate per valutare la capacità di un sistema di verifica di individuare comportamenti non conformi \cite{jia_harman_mutation_2011}. Nel presente lavoro le mutazioni vengono applicate alle catture di traffico, anziché al codice del verificatore, e le evidenze così ottenute vengono analizzate mediante la stessa pipeline. Il confronto tra gli esiti originali e quelli successivi alla mutazione consente di valutare se il sistema rilevi le variazioni introdotte quando queste modificano il soddisfacimento dei criteri dichiarati, distinguendo anche i casi in cui l'evidenza diventa insufficiente per formulare un verdetto conclusivo.

## Ambiente sperimentale e casi di test
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


## Valutazione delle capacità di verifica
In questa sezione vengono approfonditi tre gruppi di casi di test, selezionati per esaminare il comportamento delle principali capacità di verifica implementate. L'analisi si concentra sull'evidenza individuata e sui risultati ottenuti, mentre la valutazione delle alterazioni introdotte nelle catture viene affrontata nella Sezione $6.4$.

### AMF Synchronization Failure - Case B
Il test `AMF Synchronization Failure - Case B` permette di esaminare contemporaneamente tre componenti del sistema: la selezione mediante `SEQUENCE`, la verifica statica sui campi degli eventi e la verifica temporale attraverso MonPoly.

Il caso riguarda la gestione di un fallimento di sincronizzazione durante la procedura di autenticazione 5G AKA. A seguito della ricezione di un'`Authentication Request`, l'UE segnala un `Authentication Failure` con causa di sincronizzazione e fornisce il parametro `AUTS` necessario alla risincronizzazione. L'AMF inoltra quindi le informazioni necessarie all'AUSF. Nel Case B viene inoltre verificato che non venga inviata una nuova `Authentication Request` entro il limite temporale `T3520` considerato.


\begin{figure}[!htbp]
\centering
\includegraphics[width=0.94\textwidth,height=0.73\textheight,keepaspectratio]{figure/amf_sync_failure_case_b.png}
\caption{Scambio di messaggi nell'AMF Synchronization Failure, Case B, con vincolo temporale T3520.}
\label{fig:amf-sync-b}
\end{figure}


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


### UPF TEID Uniqueness
Il test `UPF TEID Uniqueness` permette di esaminare il funzionamento del costrutto `COLLECT` e del criterio di verifica `REQUIRE UNIQUE`, utilizzati per raccogliere più occorrenze dello stesso tipo di evento e verificare una proprietà sull'insieme dei valori osservati, senza imporre un ordinamento tra i messaggi.

Il caso riguarda la verifica dell'unicità degli `F-TEID`, identificatori utilizzati per distinguere i tunnel GTP-U associati al traffico del piano utente. Durante l'instaurazione delle sessioni PFCP, l'UPF comunica tali identificatori attraverso i messaggi `PFCP Session Establishment Response`.
Il test richiede di raccogliere le risposte osservate e verificare che gli `F-TEID` assegnati non vengano riutilizzati tra eventi differenti.


La specifica DSL utilizzata è la seguente:
```
COLLECT pfcp.session_establishment_response AS responses

REQUIRE UNIQUE responses.f_teids
```

La prima istruzione raccoglie tutti gli eventi corrispondenti al tipo semantico indicato, associandoli all'alias `responses`. La seconda applica il criterio di unicità ai valori `F-TEID` contenuti nella collezione, rappresentati come coppie strutturate `{teid, ipv4}`.

Nella cattura analizzata, il sistema ha individuato **5 risposte PFCP**, corrispondenti ai frame 37, 38, 46, 47 e 48, dalle quali sono stati estratti complessivamente **10 F-TEID**, due per ciascuna risposta. Sebbene gli identificatori condividano lo stesso indirizzo IPv4, i rispettivi valori TEID risultano differenti. Non essendo stata rilevata alcuna coppia `{teid, ipv4}` duplicata tra eventi distinti, il verificatore restituisce il verdetto complessivo `PASS`.

Il risultato mostra come il sistema possa verificare proprietà che coinvolgono più occorrenze dello stesso tipo di evento, utilizzando una modalità di selezione distinta da `SEQUENCE` e mantenendo la stessa rappresentazione comune dell'evidenza attraverso `BindingContext`.


### AMF RES* Verification Failure - Cases A/B/C/D
Il test `AMF RES* Verification Failure` permette di esaminare l'utilizzo congiunto dei costrutti `OPTIONAL` e `IF`, attraverso i quali una stessa specifica DSL può rappresentare percorsi differenti e applicare criteri di verifica condizionali.

Il caso riguarda la gestione di un fallimento nella verifica della risposta di autenticazione `RES*` durante le procedure 5G AKA. Le quattro varianti considerate differiscono per il percorso di identificazione della UE e per l'origine del fallimento. In particolare, l'identificazione può avvenire direttamente tramite SUCI oppure attraverso un'identificazione iniziale mediante GUTI, seguita da una richiesta d'identità. Il fallimento può invece essere rilevato localmente dall'AMF oppure comunicato dall'AUSF.

Le combinazioni considerate sono riportate nella tabella seguente:

|Caso|Identificazione|Origine del fallimento|Eventi opzionali presenti|
|---|---|---|---|
|A|SUCI diretto|AMF|Nessuno|
|B|GUTI → SUCI|AMF|Identity Request/Response|
|C|SUCI diretto|AUSF|Confirmation Request/Response|
|D|GUTI → SUCI|AUSF|Entrambi i gruppi|

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


## Mutation testing
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
