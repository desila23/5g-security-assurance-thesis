# Architettura proposta

## Architettura generale
A partire dai requisiti definiti nel Capitolo 3, l'architettura proposta è stata organizzata in componenti con responsabilità distinte, separando le fasi di estrazione e interpretazione del traffico, selezione dell'evidenza, verifica dei criteri e produzione del report finale. Questa suddivisione consente di limitare l'accoppiamento tra i diversi livelli della pipeline e di favorire la riusabilità dei componenti.

Il sistema utilizza due input principali: la cattura di traffico, che costituisce la sorgente primaria dell'evidenza osservata, e la specifica DSL, che definisce gli eventi da individuare e i criteri da verificare.

La loro elaborazione è organizzata attraverso il file di configurazione `tests.json`, nel quale vengono specificati, per ciascun caso di test, i percorsi della cattura e delle regole DSL, le sorgenti protocollari da analizzare e la destinazione del report. La configurazione può inoltre comprendere parametri aggiuntivi, come le modalità di correlazione degli eventi, le informazioni necessarie alla verifica temporale ed eventuali binding esterni o derivati.


\begin{figure}[!htbp]
\centering
\includegraphics[width=0.94\textwidth,height=0.74\textheight,keepaspectratio]{figure/architettura_generale.png}
\caption{Architettura generale della pipeline di verifica degli esiti SCAS.}
\label{fig:architettura}
\end{figure}


La pipeline trasforma progressivamente il traffico osservato in una rappresentazione adatta alla verifica. Le prime fasi riguardano l'estrazione, la normalizzazione e, quando necessaria, la risoluzione semantica degli eventi di rete; successivamente, la specifica DSL guida la selezione dell'evidenza rilevante e l'applicazione dei criteri di verifica. Il processo termina con la determinazione del verdetto e la produzione di un report strutturato contenente le evidenze utilizzate.

## Estrazione strutturata del traffico
Il file PCAP costituisce la sorgente osservabile dell'analisi, ma il contenuto della cattura non viene elaborato direttamente dai componenti successivi della pipeline. È quindi necessaria una fase preliminare di estrazione, che trasformi i pacchetti acquisiti in una rappresentazione strutturata dei dati osservati.

A tale scopo viene utilizzato **TShark**, un analizzatore di protocolli di rete che applica i _dissector_ dei protocolli presenti nella cattura e rende accessibili i relativi campi decodificati. L'estrazione avviene mediante l'opzione `-T ek`, che produce record strutturati in formato JSON, consentendo alla pipeline di operare sui campi decodificati anziché sui byte grezzi dei pacchetti. \cite{wireshark_tshark_docs}

La rappresentazione prodotta mantiene ancora la struttura e la terminologia esposte da TShark e può comprendere sia informazioni generali associate ai pacchetti, come numero di frame, timestamp e indirizzi IP, sia campi propri dei protocolli decodificati, come identificatori degli stream HTTP/2, tipi di messaggio NAS, campi PFCP e payload applicativi.

In questa fase non viene ancora attribuita una rappresentazione semantica uniforme agli eventi osservati né viene selezionata l'evidenza rilevante per uno specifico caso di test. L'output strutturato ottenuto dalla cattura costituisce invece l'ingresso della successiva fase di **normalizzazione protocol-specifica**.

## Normalizzazione protocol-specifica
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

## Risoluzione semantica
La normalizzazione produce eventi rappresentati secondo una struttura comune, ma in alcuni casi il loro significato applicativo non è ancora completamente esplicito. Ciò avviene soprattutto per messaggi relativi alle interazioni della Service-Based Architecture, dove i messaggi HTTP/2 possono rappresentare operazioni differenti in funzione del servizio richiesto e del contenuto applicativo.

Per gestire questa esigenza, viene introdotto un **resolver semantico**, incaricato di interpretare gli eventi normalizzati e associarli a tipologie coerenti con il dominio 5G. Ad esempio, analizzando il percorso della richiesta HTTP/2, il resolver può riconoscere un'operazione di _NF Discovery_ presso l'NRF e classificare gli eventi correlati come `nrf.discovery.request` e `nrf.discovery.response`.

Il resolver opera quindi ad un livello di astrazione superiore rispetto ai normalizzatori, in quanto non ricostruisce nuovamente i messaggi, ma utilizza le informazioni già disponibili per completarne l'interpretazione e rendere esplicito il tipo semantico degli eventi. Questi ultimi possono così essere selezionati attraverso i riferimenti dichiarati nella DSL.

## Selezione dell'evidenza tramite DSL
Al termine delle fasi precedenti, il traffico è stato trasformato in una sequenza di eventi strutturati e, quando necessario, semanticamente risolti. Non tutti questi eventi sono però rilevanti per il caso di test considerato, ed è quindi necessario individuare quelli richiesti dalla specifica per procedere alla verifica.

Questa operazione è guidata dalla DSL, che mette a disposizione i costrutti sintattici `SEQUENCE` e `COLLECT`, utilizzati rispettivamente per descrivere successioni ordinate di eventi e collezioni di occorrenze dello stesso tipo. Le caratteristiche dell'evidenza da ricercare vengono così definite attraverso la regola dichiarativa, anziché essere incorporate nella logica di selezione.

Gli eventi individuati vengono associati agli identificatori simbolici definiti nella DSL, denominati **alias**. Tali associazioni, dette _binding_, consentono di riferirsi all'evidenza selezionata indipendentemente dalla sua posizione nella cattura. A seconda del costrutto utilizzato, un alias può identificare un singolo evento oppure una collezione di eventi.

I binding vengono raccolti in un `BindingContext`, che costituisce la rappresentazione dell'evidenza selezionata e il punto di collegamento con i successivi meccanismi di verifica.


## Verifica
Una volta costruito il `BindingContext`, l'evidenza individuata può essere valutata rispetto ai criteri definiti per il caso di test. La DSL non descrive infatti soltanto quali eventi debbano essere ricercati, ma anche le proprietà che devono essere verificate sull'evidenza ottenuta.

La fase di verifica riceve quindi il `BindingContext` insieme ai criteri espressi nella specifica e determina se il comportamento osservato soddisfi le condizioni previste.
Nell'architettura sono previste due modalità complementari di verifica: **statica** e **temporale**.

La **verifica statica** opera direttamente sui valori contenuti nei binding e consente di esprimere proprietà quali uguaglianza (`==`), disuguaglianza (`!=`) e unicità (`UNIQUE`). È quindi utilizzata quando il risultato del test dipende dal confronto o dalle proprietà dei dati estratti dagli eventi selezionati. La valutazione di tali proprietà è affidata a un verificatore statico dedicato.

La **verifica temporale**, invece, viene utilizzata in casi in cui il criterio dipende dalle relazioni temporali tra gli eventi, ad esempio la loro occorrenza entro determinati intervalli. Tali proprietà vengono espresse mediante la **Metric First Order Temporal Logic (MFOTL)** e valutate attraverso **MonPoly**; il loro funzionamento verrà approfondito nel Capitolo $5$. 

I risultati delle verifiche statiche e temporali contribuiscono alla determinazione del verdetto complessivo del caso di test, secondo le modalità approfondite nella Sezione $5.8$.

## Reporting
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
