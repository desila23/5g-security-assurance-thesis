# Note del relatore — revisione finale

Generate dai sorgenti canonici. I nomi dei file storici mantengono la vecchia numerazione; l’ordine effettivo è in slides.json.

## 1. Titolo della tesi

Buongiorno, oggi vi presenterò il lavoro svolto per la mia tesi, che riguarda la progettazione di un linguaggio per verificare gli esiti dei test di sicurezza SCAS del 5G, utilizzando come evidenze le catture di traffico di rete.

## 2. Introduzione

Passiamo al contesto e al problema.

## 3. 5G Core: Network Functions e interazioni

Il 5G Core comprende diverse Network Functions che cooperano tra loro. Le comunicazioni seguono protocolli e procedure standardizzati. Funzioni e interazioni devono soddisfare requisiti di sicurezza. Lo schema riutilizza la topologia semplificata: control plane, user plane e interfacce principali.

## 4. Le SCAS descrivono come verificare la sicurezza

Una volta eseguita una di queste prove è quindi necessario valutare se il comportamento osservato sia conforme a quanto previsto dalla specifica.
  Tra le evidenze disponibili possiamo avere una cattura del traffico di rete, in formato PCAP, insieme al verdetto ottenuto dal test. Il problema, però, è che la disponibilità di queste informazioni non rende necessariamente evidenti le motivazioni che hanno portato a quel risultato.
  Infatti, all'interno della cattura sono presenti numerosi messaggi, tra cui anche quelli rilevanti per il test in esame, ma la cattura, da sola, non indica quali di questi messaggi siano stati utilizzati per la verifica, né quali condizioni siano state effettivamente soddisfatte o violate.
  L'esigenza da cui nasce questo lavoro è quindi quella di rendere più esplicito e ricostruibile il legame tra il verdetto e le evidenze che lo giustificano.
  L'idea è ottenere un risultato di verifica accompagnato da un report strutturato, che documenti i criteri valutati, le informazioni osservate e gli elementi della cattura che hanno contribuito a determinare quel risultato.

## 5. Da verificatori dedicati a un motore comune

Prima ciascun test richiede un verificatore dedicato. La trasformazione separa le regole dalla logica software. Le regole di test diversi alimentano un unico motore, che seleziona le evidenze, applica i criteri e produce verdetto e report. La DSL viene introdotta soltanto nella slide successiva.

## 6. La proposta: una DSL per i test SCAS

Il contributo della tesi è una DSL minimale per formalizzare due responsabilità: selezionare nel traffico le evidenze pertinenti e verificare i criteri SCAS, inclusi valori, unicità, condizioni e vincoli temporali. La traduzione dai testi SCAS alla DSL resta manuale; un motore comune esegue le regole sulle evidenze. OpenAPI, nel riquadro secondario a destra, è solo un’analogia da un altro dominio: mostra il valore di una descrizione formale delle interfacce HTTP. La DSL non deriva da OpenAPI.

## 7. Architettura della pipeline

Vediamo come la pipeline passa dalla cattura alle evidenze e al verdetto.

## 8. Architettura proposta

Per realizzare la soluzione appena introdotta, il sistema è stato organizzato in una pipeline composta da più fasi, che parte dalle catture di traffico raccolte durante l'esecuzione dei test e arriva a produrre un risultato di verifica motivato.
  La pipeline riceve in input le catture PCAP e le regole espresse nella DSL.

## 9. Dal traffico alle evidenze del test

La PCAP contiene molti pacchetti. TShark estrae i dati relativi ai protocolli selezionati; i normalizzatori li organizzano in MessageEvent. I resolver intervengono quando serve ricostruire il significato degli eventi. Il riquadro inferiore mostra la struttura comune: numero di frame e timestamp, protocollo e tipo, estremi della comunicazione, message_type, riferimenti ai frame, correlazioni e campi specifici. La DSL seleziona le evidenze rilevanti. La slide successiva riparte dalle evidenze selezionate e mostra verifica, verdetto e report.

## 10. Dalle evidenze al verdetto e al report

Una volta selezionate le evidenze, il sistema applica i criteri definiti nella DSL attraverso verifiche statiche e, quando richiesto, temporali.
  Dai risultati di queste verifiche viene determinato un verdetto complessivo, che può essere `PASS`, quando i criteri risultano soddisfatti, `FAIL`, quando viene rilevata una violazione, oppure `INCONCLUSIVE`, quando le evidenze disponibili non consentono di arrivare a una conclusione.
  - Quest'ultima distinzione è importante, perché la mancanza di evidenze sufficienti non equivale necessariamente alla violazione di un criterio.
  Infine, viene prodotto un report strutturato che documenta il verdetto, i criteri valutati, i valori osservati e i riferimenti ai frame della cattura.
  Come possiamo vedere nell'estratto, vengono conservate anche informazioni utili alla tracciabilità e alla riproducibilità della verifica, come l'hash SHA-256 della cattura e la versione di TShark utilizzata.
  Abbiamo quindi visto il funzionamento generale della pipeline. Le due operazioni fondamentali, cioè **selezionare le evidenze e definire le proprietà da verificare**, sono entrambe descritte attraverso la DSL, che andiamo ora ad approfondire.

## 11. DSL e motore di verifica

Entriamo nella DSL e nel motore comune di verifica.

## 12. La DSL: selezionare gli eventi e verificarli

Come abbiamo visto, la DSL è organizzata in due blocchi principali: uno dedicato alla selezione delle evidenze e uno alla definizione dei criteri di verifica.
  Per rappresentare questi due aspetti è stata progettata una sintassi specifica, descritta attraverso una grammatica che stabilisce come devono essere scritte le regole.
  Partendo dalla selezione, abbiamo tre costrutti principali.
  - `SEQUENCE` permette di descrivere una successione di eventi da individuare all'interno del traffico normalizzato. A ogni evento possiamo associare un _alias_, che ci permetterà successivamente di richiamarlo durante la verifica.
  - `OPTIONAL` consente invece di rappresentare parti della sequenza che possono essere presenti oppure assenti, senza impedire il riconoscimento dell'intera sequenza.
  - Infine, `COLLECT` permette di raccogliere una collezione di eventi dello stesso tipo, quando non siamo interessati a ricostruire una successione di messaggi.
  Il secondo blocco riguarda la verifica e permette di esprimere sia regole statiche, attraverso `REQUIRE` e `REQUIRE UNIQUE`, che controlla l'assenza di duplicati, sia proprietà temporali, utilizzando formule in _Metric First-Order Temporal Logic_, o MFOTL.

## 13. Dalla regola all’automa

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

## 14. Riconoscimento della sequenza

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

## 15. Dal Match al BindingContext

Il matcher riceve NFA ed eventi normalizzati e produce il Match. Nell’esempio della slide precedente riconosce A(3), B(4), C(6). Nel codice Match contiene start_index, end_index e bindings: una mappa dagli alias agli oggetti MessageEvent. Per la traccia illustrata, gli indici Python sono 2 e 5, corrispondenti alle posizioni 3 e 6 della numerazione da 1 usata nel disegno. I binding sono a → evento A in posizione 3, b → evento B in posizione 4, c → evento C in posizione 6. to_binding_context() crea un nuovo dizionario con le stesse associazioni e gli stessi oggetti evento; non ne trasforma i campi e non porta gli indici nel BindingContext. I numeri indicano posizioni nell’esempio, non frame reali. event.a, event.b ed event.c sono tipi didattici. Nel close-up vediamo gli oggetti MessageEvent riferiti dai tre alias.

## 16. Motore di verifica

Una volta ottenute le evidenze selezionate e organizzate nel BindingContext, possiamo applicare i criteri definiti nel secondo blocco della DSL.
  Il sistema prevede due modalità principali di verifica.
  - La prima è la **verifica statica**, che permette di controllare proprietà sui valori osservati, ad esempio confrontando campi di eventi differenti oppure verificando l'unicità dei valori raccolti.
  - La seconda è la **verifica temporale**, utilizzata quando i criteri riguardano anche le relazioni temporali tra gli eventi.
  In questo caso vengono utilizzate formule MFOTL, mentre la loro valutazione è affidata a _MonPoly_, un motore di verifica temporale esterno integrato nella pipeline.
  Il sistema prepara quindi gli eventi temporizzati e le formule richieste, esegue le verifiche e ne raccoglie i risultati, che contribuiranno alla determinazione del verdetto e alla produzione del report.

## 17. Testing

Passiamo ai test sulle catture originali.

## 18. AMF Synchronization Failure, Case B

Per valutare il sistema sono stati considerati diversi casi di test SCAS.
  Tra questi, vorrei soffermarmi su tre esempi particolarmente rappresentativi, perché permettono di mostrare come i diversi costrutti della DSL vengono utilizzati in situazioni concrete.
  Il primo esempio riguarda il test _AMF Synchronization Failure, Case B_.
  Durante la procedura di autenticazione, può verificarsi un errore di sincronizzazione tra il dispositivo e la rete. In questa situazione, l'AMF deve gestire il fallimento rispettando le condizioni previste dalla specifica, tra cui alcuni vincoli temporali.
  Attraverso `SEQUENCE` vengono individuati i messaggi della procedura di risincronizzazione, mentre le condizioni `REQUIRE` permettono di controllare la coerenza dei parametri scambiati.
  In questo caso, però, non basta verificare i valori, perché è necessario rispettare anche un vincolo temporale.
  La proprietà MFOTL richiede che, nell’intervallo configurato dopo il _Synchronization Failure_, non compaia una nuova _Authentication Request_ prima della successiva risposta AUSF. T3520 è configurato a 15 secondi: non impone un’attesa minima di 15 secondi.
  Su free5GC si osservano il failure al frame 358, la risposta AUSF al frame 604 e la nuova richiesta al frame 606, a circa 25 secondi dal failure. Su Open5GS i frame sono 276, 432 e 434, a circa 11 secondi: anche qui la risposta AUSF precede la richiesta e la proprietà è PASS.
  Su entrambe le catture, i quattro controlli statici e quello temporale sono `PASS`, producendo un verdetto complessivo `PASS` per i criteri applicati. Questo risultato non dimostra da solo il rispetto di tutte le precondizioni SCAS: in particolare, gli 11 secondi di Open5GS non attestano un eventuale ritardo oltre T3520.

## 19. UPF TEID Uniqueness

Il secondo esempio riguarda il test _UPF TEID Uniqueness_.
  L'UPF gestisce il traffico dati degli utenti attraverso dei tunnel, identificati anche tramite valori denominati TEID. Il test serve a verificare che gli identificativi degli endpoint dei tunnel non presentino duplicati nelle risposte analizzate.
  In questo caso, attraverso `COLLECT` vengono raccolte cinque risposte PFCP di instaurazione della sessione, dalle quali vengono estratte dieci coppie formate da TEID e indirizzo IPv4.
  Successivamente, `REQUIRE UNIQUE` verifica che queste coppie siano tutte distinte.
  Nella cattura analizzata non sono stati rilevati duplicati e il sistema ha quindi restituito `PASS`.

## 20. AMF RES*: quattro varianti, un'unica specifica DSL

I quattro risultati mostrati appartengono alle catture free5GC: A, B, C e D sono tutti `PASS`. Su Open5GS, A è `PASS`, mentre B, C e D sono `INCONCLUSIVE`: B ha un match completo ma mancano binding di identità richiesti da criteri applicabili; C e D non hanno match completi.
  Il terzo esempio riguarda _AMF RES_ Verification Failure*, una famiglia composta da quattro casi che siamo riusciti a rappresentare attraverso un'unica regola DSL.
  Questo test riguarda la gestione di un fallimento nella verifica della risposta di autenticazione RES*, cioè quando la risposta fornita dal dispositivo non viene riconosciuta come valida. In questa situazione, il sistema deve gestire correttamente il fallimento, secondo quanto previsto dalla specifica SCAS.
  I casi differiscono per il percorso di identificazione dell'utente, che può avvenire direttamente tramite SUCI oppure attraverso GUTI e successivamente SUCI, e per l'origine del fallimento, che può essere locale all'AMF oppure provenire dall'AUSF.
  Per gestire queste differenze, `OPTIONAL` permette di rappresentare parti della procedura non presenti in tutte le varianti, mentre `IF` consente di applicare i criteri pertinenti in base alla configurazione del caso.
  In ciascuna delle quattro catture il sistema ha individuato un unico match completo e ha restituito `PASS`.
  Il numero di controlli soddisfatti varia in base al caso, mentre le condizioni non applicabili vengono contrassegnate come `SKIPPED`.
  Questo esempio mostra quindi come una stessa regola DSL possa gestire varianti differenti senza dover definire ogni volta una logica di verifica separata.

## 21. Risultati dei test baseline

La tabella unisce le tabelle Open5GS e free5GC del capitolo 6 della tesi. Open5GS: 6 PASS, 1 FAIL e 3 INCONCLUSIVE su 10 catture. free5GC: 6 PASS su 6 catture. Il trattino indica un caso non riportato per quella implementazione, non un esito INCONCLUSIVE. NRF restituisce HTTP 200 anziché 403. Per RES* su Open5GS, B ha binding di identità mancanti; C e D non hanno match completi.

## 22. Mutation testing

Verifichiamo come cambia il verdetto quando alteriamo le evidenze.

## 23. Mutation testing: il processo

Il collegamento dalla selezione rappresenta la provenienza dei frame di evidenza. Nell’implementazione il motore offline li ricava dal report baseline e riceve anche la PCAP originale. Il mutatore non è un componente chiamato automaticamente dalla pipeline. La PCAP mutata rientra nella medesima pipeline e la seconda elaborazione genera il report mutation.

## 24. Risultati del mutation testing

Complessivamente sono stati realizzati **13 scenari di mutazione**, e in tutti i casi i risultati osservati sono stati coerenti con quelli attesi.
  Tra questi, due esempi sono particolarmente significativi.
  La distribuzione è NRF 1, UDM 2, AMF Synchronization Failure 4 (3 Case A e 1 Case B), UPF 2 e AMF RES* 4. Gli esiti sono quelli attesi nei 13 scenari considerati: non costituiscono una prova di correttezza universale del verificatore.
  Il primo esempio riguarda _AMF Synchronization Failure, Case A_ su Open5GS, dove abbiamo introdotto mutazioni statiche, temporali e combinate.
  Come si vede nella tabella, modificando soltanto i valori dei messaggi fallisce la verifica statica, mentre quella temporale continua a essere soddisfatta. Alterando invece gli intervalli di tempo avviene il contrario; modificando entrambi, falliscono entrambe le verifiche.
  Il secondo esempio riguarda _UPF TEID Uniqueness_, dove abbiamo valutato due situazioni differenti.
  Introducendo un F-TEID duplicato, il sistema rileva la violazione del criterio di unicità e restituisce `FAIL`.
  Rimuovendo invece gli eventi necessari alla verifica, il sistema non dispone più di evidenze sufficienti e restituisce `INCONCLUSIVE`.
  Quest'ultimo risultato è particolarmente importante, perché mostra che il verificatore distingue **una proprietà effettivamente violata da una proprietà che non può essere valutata con le evidenze disponibili**.

## 25. Conclusioni e sviluppi futuri

Chiudiamo con i limiti emersi e le direzioni di sviluppo.

## 26. Futuri sviluppi

Il capitolo conclusivo individua due possibili sviluppi. Primo: rendere la verifica temporale meno dipendente dal completamento della SEQUENCE, perché una violazione dell’ordine può impedire al matcher di selezionare gli eventi necessari. Secondo: riutilizzare la DSL per selezionare eventi e campi delle mutazioni. Le operazioni di modifica restano specifiche del protocollo. Sono sviluppi proposti, non funzionalità già realizzate.

## 27. Grazie per l’attenzione. Domande?

Grazie per l’attenzione. Sono a disposizione per le domande.

