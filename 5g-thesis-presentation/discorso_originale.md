## Parte 1: Introduzione (~5 minuti)
#### APERTURA -- Slide 1
Buongiorno, oggi vi presenterò il lavoro svolto per la mia tesi, che riguarda la progettazione di un linguaggio per verificare gli esiti dei test di sicurezza SCAS del 5G, utilizzando come evidenze le catture di traffico di rete.

#### 5G e SCAS -- Slide 2
L'evoluzione delle reti mobili verso la quinta generazione ha introdotto un'architettura di rete più articolata rispetto alle precedenti. 

In particolare, il 5G _Core_ è organizzato in diversi componenti, denominati _Network Functions_, ciascuno responsabile di specifiche funzionalità, come l'autenticazione degli utenti, la gestione della mobilità e delle sessioni. È queste funzioni cooperano tra loro attraverso lo scambio di messaggi e informazioni.

Tale organizzazione offre, da un lato, maggiora flessibilità, ma introduce anche nuove complessità dal punto di vista della sicurezza, perché non è sufficiente valutare il comportamento delle singole 
funzioni, ma bisogna considerare anche le loro interazioni.

Per supportare questa valutazione, il 3GPP ha definito le *Security Assurance Specification*, o *SCAS*, ossia specifiche tecniche che descrivono requisiti di sicurezza e procedure di test per le diverse funzioni della rete 5G.
In particolare, per ciascun caso di test vengono definite le condizioni iniziali, le operazioni da eseguire e i risultati attesi, oltre che quali evidenze raccogliere per documentare l'esecuzione della prova. 

#### Problema del verificabilità e idea del report -- Slide 3
Una volta eseguita una di queste prove è quindi necessario valutare se il comportamento osservato sia conforme a quanto previsto dalla specifica. 

Tra le evidenze disponibili possiamo avere una cattura del traffico di rete, in formato PCAP, insieme al verdetto ottenuto dal test. Il problema, però, è che la disponibilità di queste informazioni non rende necessariamente evidenti le motivazioni che hanno portato a quel risultato.

Infatti, all'interno della cattura sono presenti numerosi messaggi, tra cui anche quelli rilevanti per il test in esame, ma la cattura, da sola, non indica quali di questi messaggi siano stati utilizzati per la verifica, né quali condizioni siano state effettivamente soddisfatte o violate.

L'esigenza da cui nasce questo lavoro è quindi quella di rendere più esplicito e ricostruibile il legame tra il verdetto e le evidenze che lo giustificano.

L'idea è ottenere un risultato di verifica accompagnato da un report strutturato, che documenti i criteri valutati, le informazioni osservate e gli elementi della cattura che hanno contribuito a determinare quel risultato.

#### Da human-readable a machine-readable: la DSL -- Slide 4 e 5
Per realizzare un sistema di questo tipo, però, bisogna affrontare un problema più generale.

***Come può un software sapere quali messaggi cercare, quali informazioni confrontare e quali condizioni verificare, se i criteri sono descritti prevalentemente in linguaggio naturale all'interno delle specifiche SCAS?***

Una possibile soluzione sarebbe sviluppare un programma specifico per ciascun test, implementando direttamente nel codice la relativa logica di verifica; ma questo approccio legherebbe troppo il sistema al singolo test specifico con conseguenti problemi di forte accoppiamento e di scarsa riusabilità.

Per rendere il sistema riutilizzabile, serve quindi separare i criteri, che possono cambiare da test a test, dalla logica software che si occupa di verificarli.

E proprio da questa necessità nasce l'idea centrale della lavoro: progettare un *DSL*, ossia *Domain Specific Language*, che permetta di esprimere in forma dichiarativa e strutturata i criteri ricavati dalle specifiche SCAS. 
L'aspetto fondamentale è che questo linguaggio non deve limitarsi a descrivere quali condizioni verificare, ma deve permettere anche di specificare **quali evidenze individuare all'interno della cattura.**
I criteri vengono quindi interpretati e formalizzati nella DSL, mentre il sistema software si occupa di applicare automaticamente le regole alle evidenze raccolte.

I criteri vengono quindi interpretati e formalizzati nella DSL da chi definisce il test, mentre il sistema software si occupa di applicare automaticamente queste regole alle evidenze raccolte.

Da questa idea derivano i due contributi principali che sono stati realizzati per questo lavoro: da una parte, la progettazione dell'effettivo linguaggio DSL; dall'altra, lo sviluppo di una pipeline software capace di interpretare le regole, analizzare le catture di traffico, individuare le evidenze rilevanti, verificarne le proprietà e produrre un report che documenti il verdetto e le motivazioni su cui si basa.


---

## Parte 2: Architettura (~3 minuti)

#### Architettura generale — Slide 5 (attuale slide 6)
Per realizzare la soluzione appena introdotta, il sistema è stato organizzato in una pipeline composta da più fasi, che parte dalle catture di traffico raccolte durante l'esecuzione dei test e arriva a produrre un risultato di verifica motivato.
La pipeline riceve in input le catture PCAP e le regole espresse nella DSL.

#### Estrazione, normalizzazione e selezione — Slide 6 (attuale slide 7)
Una delle scelte principali nella progettazione di questa pipeline riguarda proprio il modo in cui vengono individuate le evidenze da verificare.

Per rendere il sistema riutilizzabile, questa elaborazione è stata organizzata su **due livelli distinti**.
1. Il primo è dedicato all'estrazione e alla normalizzazione per protocollo.
	Partendo dalla cattura PCAP, che può contenere numerosi messaggi appartenenti a protocolli differenti, attraverso TShark vengono estratte le informazioni dei protocolli configurati per il test.
	Queste informazioni mantengono tuttavia ancora la struttura e i campi specifici dei diversi protocolli.
	
2. Per questo motivo, vengono elaborate da normalizzatori specifici per protocollo, che le trasformano in eventi strutturati, rappresentati attraverso una struttura comune denominata _MessageEvent_.
	
3. Quando necessario, interviene anche un resolver semantico, che completa l'interpretazione degli eventi normalizzati.

Attualmente il sistema supporta tre protocolli: NAS, HTTP/2 e PFCP. Tuttavia, per ogni test vengono utilizzati soltanto quelli necessari. Ad esempio, se un test coinvolge NAS e HTTP/2, vengono elaborate queste sorgenti, mentre il normalizzatore PFCP rimane disponibile per altri casi.

Questa separazione è importante perché **test SCAS differenti possono utilizzare gli stessi protocolli**, e quindi possiamo riutilizzare i normalizzatori senza dover sviluppare un estrattore specifico per ciascun test.

A questo punto abbiamo ottenuto un insieme di eventi normalizzati, ma questi possono contenere ancora molte più informazioni di quelle necessarie per il singolo caso SCAS.

Ed è qui che interviene il **secondo livello, cioè la selezione delle evidenze guidata dalla DSL**.

A partire dagli eventi normalizzati, il sistema utilizza le regole dichiarate nella DSL per individuare e mettere in relazione soltanto gli eventi rilevanti per la verifica.

In questo modo passiamo da un insieme di eventi strutturati per protocollo a un insieme di evidenze specifiche per il test, sulle quali sarà possibile applicare i criteri previsti.

#### Verifica e report — Slide 7 (attuale slide 8)
Una volta selezionate le evidenze, il sistema applica i criteri definiti nella DSL attraverso verifiche statiche e, quando richiesto, temporali.

Dai risultati di queste verifiche viene determinato un verdetto complessivo, che può essere `PASS`, quando i criteri risultano soddisfatti, `FAIL`, quando viene rilevata una violazione, oppure `INCONCLUSIVE`, quando le evidenze disponibili non consentono di arrivare a una conclusione.
- Quest'ultima distinzione è importante, perché la mancanza di evidenze sufficienti non equivale necessariamente alla violazione di un criterio.

Infine, viene prodotto un report strutturato che documenta il verdetto, i criteri valutati, i valori osservati e i riferimenti ai frame della cattura.

Come possiamo vedere nell'estratto, vengono conservate anche informazioni utili alla tracciabilità e alla riproducibilità della verifica, come l'hash SHA-256 della cattura e la versione di TShark utilizzata.

Abbiamo quindi visto il funzionamento generale della pipeline. Le due operazioni fondamentali, cioè **selezionare le evidenze e definire le proprietà da verificare**, sono entrambe descritte attraverso la DSL, che andiamo ora ad approfondire.


---

## Parte 3: DSL e motore di verifica (~5 minuti e 45 secondi)

#### La DSL: selezione e verifica — Slide 8 (attuale 9)
Come abbiamo visto, la DSL è organizzata in due blocchi principali: uno dedicato alla selezione delle evidenze e uno alla definizione dei criteri di verifica.

Per rappresentare questi due aspetti è stata progettata una sintassi specifica, descritta attraverso una grammatica che stabilisce come devono essere scritte le regole.

Partendo dalla selezione, abbiamo tre costrutti principali.
- `SEQUENCE` permette di descrivere una successione di eventi da individuare all'interno del traffico normalizzato. A ogni evento possiamo associare un _alias_, che ci permetterà successivamente di richiamarlo durante la verifica.
	
- `OPTIONAL` consente invece di rappresentare parti della sequenza che possono essere presenti oppure assenti, senza impedire il riconoscimento dell'intera sequenza.
	
- Infine, `COLLECT` permette di raccogliere una collezione di eventi dello stesso tipo, quando non siamo interessati a ricostruire una successione di messaggi.

Il secondo blocco riguarda la verifica e permette di esprimere sia regole statiche, attraverso costrutti come `REQUIRE`, sia proprietà temporali, utilizzando formule in _Metric First-Order Temporal Logic_, o MFOTL.

#### Dalla regola all'automa — Slide 9 (attuale 10)
Uno degli aspetti principali dell'implementazione riguarda il riconoscimento delle sequenze descritte attraverso `SEQUENCE`.

Per questo è stato realizzato un _matcher_ basato su un automa a stati finiti non deterministico, o NFA, costruito secondo il metodo di Thompson.

L'idea è partire dagli eventi descritti nella regola e associare a ciascuno di essi un frammento elementare dell'automa, chiamato _atom_.

Ogni atom è composto da uno stato iniziale, uno stato finale e una transizione che permette di avanzare quando viene riconosciuto l'evento corrispondente.

Una volta costruiti questi frammenti, vengono collegati tra loro per formare un unico automa, che rappresenta la struttura della sequenza da riconoscere.

Per collegarli vengono utilizzate anche le _transizioni epsilon_, che consentono di passare da uno stato all'altro senza consumare alcun evento.

Queste transizioni sono particolarmente importanti per gestire i blocchi opzionali.

Nell'esempio mostrato abbiamo una sequenza composta dagli eventi A, B e C, dove B è opzionale.

L'automa presenta quindi un percorso che attraversa tutti e tre gli eventi, ma anche un percorso alternativo che permette di saltare B.

In questo modo possiamo riconoscere sia la sequenza A, B, C sia la sequenza A, C, attraverso un automa costruito direttamente a partire dalla regola DSL.

#### Riconoscimento della sequenza — Slide 10 (attuale 11)
Una volta costruito l'automa, il matcher lo utilizza per cercare la sequenza all'interno degli eventi normalizzati.

Nell'esempio che vediamo, la sequenza richiesta è sempre A, B opzionale e C, mentre gli eventi osservati sono A, X, A, B, X, C.

Partendo dal primo evento A, il matcher avvia un possibile riconoscimento della sequenza.

Il messaggio successivo, X, non è previsto dalla regola, quindi non contribuisce al riconoscimento.

Quando però incontriamo la seconda A, il candidato precedente non può consumare questo nuovo evento, perché sta cercando B oppure C.

Interviene quindi la _politica di riavvio_: il candidato precedente viene terminato e ne viene avviato uno nuovo a partire dalla seconda A.

A questo punto incontriamo B, che è compatibile con la sequenza, e successivamente un'altra X, che viene ignorata.

Infine, incontriamo C, che completa il riconoscimento.

Il risultato è quindi la sequenza formata da A in posizione 3, B in posizione 4 e C in posizione 6.

La politica di riavvio consente quindi di considerare nuovi punti di partenza quando vengono incontrati eventi compatibili con l'inizio della regola, senza dipendere esclusivamente dalla prima occorrenza.

#### BindingContext — Slide 11 (attuale 12)
Una volta riconosciuta la sequenza, il matcher produce un risultato chiamato _Match_, che contiene le associazioni tra gli eventi individuati e gli alias dichiarati nella DSL.

Nel nostro esempio, l'alias `a` viene associato all'evento A in posizione 3, `b` all'evento B in posizione 4 e `c` all'evento C in posizione 6.

Queste associazioni vengono poi rese disponibili attraverso una struttura chiamata _BindingContext_.

In questo modo, il verificatore può utilizzare gli alias per accedere ai campi degli eventi riconosciuti, senza doverli cercare nuovamente all'interno della cattura.

Il BindingContext rappresenta quindi il collegamento tra la selezione delle evidenze e l'applicazione delle regole di verifica.

#### Motore di verifica — Slide 12 (attuale 13)
Una volta ottenute le evidenze selezionate e organizzate nel BindingContext, possiamo applicare i criteri definiti nel secondo blocco della DSL.

Il sistema prevede due modalità principali di verifica.
- La prima è la **verifica statica**, che permette di controllare proprietà sui valori osservati, ad esempio confrontando campi di eventi differenti oppure verificando l'unicità dei valori raccolti.
	
- La seconda è la **verifica temporale**, utilizzata quando i criteri riguardano anche le relazioni temporali tra gli eventi.
	In questo caso vengono utilizzate formule MFOTL, mentre la loro valutazione è affidata a _MonPoly_, un motore di verifica temporale esterno integrato nella pipeline.

Il sistema prepara quindi gli eventi temporizzati e le formule richieste, esegue le verifiche e ne raccoglie i risultati, che contribuiranno alla determinazione del verdetto e alla produzione del report.


---

## Parte 4: Testing e Mutation testing
#### Introduzione ai test — Slide 13 (attuale 14)
Per valutare il sistema sono stati considerati diversi casi di test SCAS.
Tra questi, vorrei soffermarmi su tre esempi particolarmente rappresentativi, perché permettono di mostrare come i diversi costrutti della DSL vengono utilizzati in situazioni concrete.

#### AMF Synchronization Failure — Case B — Slide 13
Il primo esempio riguarda il test _AMF Synchronization Failure, Case B_.

Durante la procedura di autenticazione, può verificarsi un errore di sincronizzazione tra il dispositivo e la rete. In questa situazione, l'AMF deve gestire il fallimento rispettando le condizioni previste dalla specifica, tra cui alcuni vincoli temporali.

Attraverso `SEQUENCE` vengono individuati i messaggi della procedura di risincronizzazione, mentre le condizioni `REQUIRE` permettono di controllare la coerenza dei parametri scambiati.

In questo caso, però, non basta verificare i valori, perché è necessario rispettare anche un vincolo temporale.

La proprietà MFOTL richiede che, dopo il messaggio di _Synchronization Failure_, non venga osservata una nuova _Authentication Request_ nei primi 15 secondi.

Nella cattura analizzata, tra il messaggio al frame 358 e la nuova richiesta al frame 606 trascorrono circa 25 secondi, quindi il vincolo risulta soddisfatto.

Anche i quattro controlli statici hanno restituito esito positivo, producendo quindi un verdetto complessivo `PASS`.

#### UPF TEID Uniqueness — Slide 14 (attuale 15)
Il secondo esempio riguarda il test _UPF TEID Uniqueness_.

L'UPF gestisce il traffico dati degli utenti attraverso dei tunnel, identificati anche tramite valori denominati TEID. Il test serve a verificare che gli identificativi degli endpoint dei tunnel non presentino duplicati nelle risposte analizzate.

In questo caso, attraverso `COLLECT` vengono raccolte cinque risposte PFCP di instaurazione della sessione, dalle quali vengono estratte dieci coppie formate da TEID e indirizzo IPv4.

Successivamente, `REQUIRE UNIQUE` verifica che queste coppie siano tutte distinte.

Nella cattura analizzata non sono stati rilevati duplicati e il sistema ha quindi restituito `PASS`.

#### AMF RES* Verification Failure — Slide 15 (attuale 16)
Il terzo esempio riguarda _AMF RES_ Verification Failure*, una famiglia composta da quattro casi che siamo riusciti a rappresentare attraverso un'unica regola DSL.

Questo test riguarda la gestione di un fallimento nella verifica della risposta di autenticazione RES*, cioè quando la risposta fornita dal dispositivo non viene riconosciuta come valida. In questa situazione, il sistema deve gestire correttamente il fallimento, secondo quanto previsto dalla specifica SCAS.

I casi differiscono per il percorso di identificazione dell'utente, che può avvenire direttamente tramite SUCI oppure attraverso GUTI e successivamente SUCI, e per l'origine del fallimento, che può essere locale all'AMF oppure provenire dall'AUSF.

Per gestire queste differenze, `OPTIONAL` permette di rappresentare parti della procedura non presenti in tutte le varianti, mentre `IF` consente di applicare i criteri pertinenti in base alla configurazione del caso.

In ciascuna delle quattro catture il sistema ha individuato un unico match completo e ha restituito `PASS`.

Il numero di controlli soddisfatti varia in base al caso, mentre le condizioni non applicabili vengono contrassegnate come `SKIPPED`.

Questo esempio mostra quindi come una stessa regola DSL possa gestire varianti differenti senza dover definire ogni volta una logica di verifica separata.

#### Risultati baseline — Slide 16 (attuale 17)
Questi sono soltanto tre esempi della valutazione effettuata.

Complessivamente, sulle dieci catture originali, o _baseline_, tutti i verdetti ottenuti dal sistema sono risultati coerenti con quelli attesi.

In particolare, abbiamo ottenuto nove `PASS` e un `FAIL` atteso, relativo al test NRF, nel quale il comportamento osservato non soddisfaceva il criterio richiesto.

#### Mutation testing: il processo — Slide 17 (attuale slide 18)
Dopo aver valutato il sistema sulle catture originali, abbiamo voluto verificare anche come reagisse a modifiche controllate delle evidenze.

Questo è particolarmente importante perché la DSL e la pipeline sono state sviluppate utilizzando proprio alcuni dei test analizzati. Ottenere i risultati attesi sulle catture originali, quindi, non è sufficiente per valutare come il verificatore si comporti in situazioni differenti.

Per questo abbiamo introdotto una fase di _mutation testing_.

Come possiamo vedere nella slide, partiamo da una PCAP originale, che viene analizzata normalmente dalla pipeline utilizzando le regole definite nella DSL.

Questa prima esecuzione produce un verdetto, chiamato _baseline_, e un report che contiene anche i riferimenti alle evidenze e ai frame rilevanti per la verifica.

A questo punto interviene un motore di mutazione esterno alla pipeline, che utilizza la cattura originale e le informazioni del report per introdurre modifiche controllate, per esempio alterando dei valori, modificando gli intervalli temporali oppure rimuovendo alcuni messaggi.

La nuova PCAP viene quindi analizzata nuovamente attraverso **la stessa pipeline e le stesse regole DSL**.

In questo modo, ciò che cambia sono le evidenze fornite in ingresso, mentre la logica del verificatore rimane invariata.

Possiamo quindi confrontare il nuovo verdetto con quello atteso per la mutazione introdotta e valutare se il sistema abbia riconosciuto correttamente il cambiamento.

#### Mutation testing: risultati — Slide 18 (attuale slide 19)
Complessivamente sono stati realizzati **15 esperimenti di mutazione**, e in tutti i casi i risultati osservati sono stati coerenti con quelli attesi.

Tra questi, due esempi sono particolarmente significativi.

Il primo riguarda _AMF Synchronization Failure_, dove abbiamo introdotto mutazioni statiche, temporali e combinate.

Come si vede nella tabella, modificando soltanto i valori dei messaggi fallisce la verifica statica, mentre quella temporale continua a essere soddisfatta. Alterando invece gli intervalli di tempo avviene il contrario; modificando entrambi, falliscono entrambe le verifiche.

Il secondo esempio riguarda _UPF TEID Uniqueness_, dove abbiamo valutato due situazioni differenti.

Introducendo un F-TEID duplicato, il sistema rileva la violazione del criterio di unicità e restituisce `FAIL`.

Rimuovendo invece gli eventi necessari alla verifica, il sistema non dispone più di evidenze sufficienti e restituisce `INCONCLUSIVE`.

Quest'ultimo risultato è particolarmente importante, perché mostra che il verificatore distingue **una proprietà effettivamente violata da una proprietà che non può essere valutata con le evidenze disponibili**.


---

## Parte 6: Conclusioni e sviluppi futuri
I risultati ottenuti, anche attraverso il mutation testing, mostrano quindi come sia possibile valutare il comportamento osservato durante un test non soltanto in base al suo esito, ma anche alla capacità di individuare le condizioni che lo hanno determinato.

È importante però considerare che questa valutazione dipende dalle evidenze effettivamente disponibili e dai criteri che siamo in grado di rappresentare. Il sistema, infatti, è stato sviluppato e sperimentato su un insieme specifico di casi SCAS e non può ancora essere considerato una soluzione generale per qualsiasi procedura di test.

Proprio da questi limiti emergono possibili sviluppi futuri, come l'estensione del linguaggio a nuove tipologie di criteri, il supporto a ulteriori protocolli e una valutazione su un insieme più ampio di casi, anche più complessi.

In questa prospettiva, il contributo del lavoro non consiste nel sostituire l'analisi della sicurezza con un verdetto automatico, ma nel rendere la verifica un processo più sistematico, in cui le conclusioni possano essere ricostruite, motivate e ricondotte alle evidenze da cui derivano.