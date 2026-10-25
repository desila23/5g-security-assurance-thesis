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

## 5. Da human-readable a machine-readable

Le Network Functions sono prevalentemente software, mentre le SCAS sono scritte in linguaggio naturale. Come può il programma sapere quali messaggi cercare, quali campi confrontare e quali condizioni verificare? Serve una rappresentazione strutturata. Il progettista interpreta i criteri e li formalizza: la traduzione SCAS → DSL non è automatica. Il breve esempio concettuale richiama il test NRF: selezionare richiesta e risposta, poi controllare lo status 403. OpenAPI è soltanto un’analogia nel dominio delle API, non è il linguaggio del progetto e non esegue test SCAS. La domanda prepara il motore comune e la DSL delle prossime due slide.

## 6. Da verificatori dedicati a un motore comune

Un primo approccio consiste nello scrivere un programma specifico per ciascun test: i criteri sono incorporati nel codice e la logica è poco riutilizzabile. L’animazione mostra la separazione dei criteri dalla logica software. Regole differenti alimentano un unico motore, che seleziona le evidenze, applica i criteri e produce verdetto e report. La DSL, introdotta nella slide successiva, esprime queste regole.

## 7. La proposta: una DSL per i test SCAS

Per esprimere le regole ho progettato una Domain-Specific Language. I due compiti sono selezionare le evidenze pertinenti nella cattura e definire le condizioni da verificare: valori, unicità e vincoli temporali. Il progettista interpreta i criteri SCAS e li formalizza nella DSL; il sistema applica automaticamente le regole alle evidenze. Il contributo comprende il linguaggio e una pipeline comune che analizza il traffico, verifica le condizioni e produce un report con verdetto ed evidenze. La grammatica sarà approfondita nella sezione dedicata.

## 8. Architettura della pipeline

Vediamo come la pipeline passa dalla cattura alle evidenze e al verdetto.

## 9. Architettura proposta

Per realizzare la soluzione appena introdotta, il sistema è stato organizzato in una pipeline composta da più fasi, che parte dalle catture di traffico raccolte durante l'esecuzione dei test e arriva a produrre un risultato di verifica motivato.
  La pipeline riceve in input le catture PCAP e le regole espresse nella DSL.

## 10. Dal traffico alle evidenze del test

La PCAP contiene molti pacchetti. TShark estrae i dati relativi ai protocolli selezionati; i normalizzatori li organizzano in MessageEvent. I resolver intervengono quando serve ricostruire il significato degli eventi. Il riquadro inferiore mostra la struttura comune: numero di frame e timestamp, protocollo e tipo, estremi della comunicazione, message_type, riferimenti ai frame, correlazioni e campi specifici. La DSL seleziona le evidenze rilevanti. La slide successiva riparte dalle evidenze selezionate e mostra verifica, verdetto e report.

## 11. Dalle evidenze al verdetto e al report

Una volta selezionate le evidenze, il sistema applica i criteri definiti nella DSL attraverso verifiche statiche e, quando richiesto, temporali.
  Dai risultati di queste verifiche viene determinato un verdetto complessivo, che può essere `PASS`, quando i criteri risultano soddisfatti, `FAIL`, quando viene rilevata una violazione, oppure `INCONCLUSIVE`, quando le evidenze disponibili non consentono di arrivare a una conclusione.
  - Quest'ultima distinzione è importante, perché la mancanza di evidenze sufficienti non equivale necessariamente alla violazione di un criterio.
  Infine, viene prodotto un report strutturato che documenta il verdetto, i criteri valutati, i valori osservati e i riferimenti ai frame della cattura.
  Come possiamo vedere nell'estratto, vengono conservate anche informazioni utili alla tracciabilità e alla riproducibilità della verifica, come l'hash SHA-256 della cattura e la versione di TShark utilizzata.
  Abbiamo quindi visto il funzionamento generale della pipeline. Le due operazioni fondamentali, cioè **selezionare le evidenze e definire le proprietà da verificare**, sono entrambe descritte attraverso la DSL, che andiamo ora ad approfondire.

## 12. DSL e motore di verifica

Entriamo nella DSL e nel motore comune di verifica.

## 13. La DSL: selezionare gli eventi e verificarli

Come abbiamo visto, la DSL è organizzata in due blocchi principali: uno dedicato alla selezione delle evidenze e uno alla definizione dei criteri di verifica.
  Per rappresentare questi due aspetti è stata progettata una sintassi specifica, descritta attraverso una grammatica che stabilisce come devono essere scritte le regole.
  Partendo dalla selezione, abbiamo tre costrutti principali.
  - `SEQUENCE` permette di descrivere una successione di eventi da individuare all'interno del traffico normalizzato. A ogni evento possiamo associare un _alias_, che ci permetterà successivamente di richiamarlo durante la verifica.
  - `OPTIONAL` consente invece di rappresentare parti della sequenza che possono essere presenti oppure assenti, senza impedire il riconoscimento dell'intera sequenza.
  - Infine, `COLLECT` permette di raccogliere una collezione di eventi dello stesso tipo, quando non siamo interessati a ricostruire una successione di messaggi.
  Il secondo blocco riguarda la verifica e permette di esprimere sia regole statiche, attraverso `REQUIRE` e `REQUIRE UNIQUE`, che controlla l'assenza di duplicati, sia proprietà temporali, utilizzando formule in _Metric First-Order Temporal Logic_, o MFOTL.

## 14. Dalla regola all’automa

Uno degli aspetti principali dell'implementazione riguarda il riconoscimento delle sequenze descritte attraverso `SEQUENCE`.
  Per questo è stato realizzato un _matcher_ basato su un automa a stati finiti non deterministico, o NFA, costruito secondo il metodo di Thompson.
  L'idea è partire dagli eventi descritti nella regola e rappresentarli internamente con nodi chiamati Atom. Da ciascun Atom si costruisce un frammento elementare dell'automa.
  Ogni frammento è composto da uno stato iniziale, uno stato finale e una transizione che permette di avanzare quando viene riconosciuto l'evento corrispondente.
  Una volta costruiti questi frammenti, vengono collegati tra loro per formare un unico automa, che rappresenta la struttura della sequenza da riconoscere.
  Per collegarli vengono utilizzate anche le _transizioni epsilon_, che consentono di passare da uno stato all'altro senza consumare alcun evento.
  Queste transizioni sono particolarmente importanti per gestire i blocchi opzionali.
  Nell'esempio mostrato abbiamo una sequenza composta dagli eventi A, B e C, dove B è opzionale.
  L'automa presenta quindi un percorso che attraversa tutti e tre gli eventi, ma anche un percorso alternativo che permette di saltare B.
  In questo modo possiamo riconoscere sia la sequenza A, B, C sia la sequenza A, C, attraverso un automa costruito direttamente a partire dalla regola DSL.

## 15. Riconoscimento della sequenza

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

## 16. Dal Match al BindingContext

Il matcher riceve NFA ed eventi normalizzati e produce il Match. Nell’esempio della slide precedente riconosce A(3), B(4), C(6). Nel codice Match contiene start_index, end_index e bindings: una mappa dagli alias agli oggetti MessageEvent. Per la traccia illustrata, gli indici Python sono 2 e 5, corrispondenti alle posizioni 3 e 6 della numerazione da 1 usata nel disegno. I binding sono a → evento A in posizione 3, b → evento B in posizione 4, c → evento C in posizione 6. to_binding_context() crea un nuovo dizionario con le stesse associazioni e gli stessi oggetti evento; non ne trasforma i campi e non porta gli indici nel BindingContext. I numeri indicano posizioni nell’esempio, non frame reali. event.a, event.b ed event.c sono tipi didattici. Nel close-up vediamo gli oggetti MessageEvent riferiti dai tre alias.

## 17. Motore di verifica

Una volta ottenute le evidenze selezionate e organizzate nel BindingContext, possiamo applicare i criteri definiti nel secondo blocco della DSL.
  Il sistema prevede due modalità principali di verifica.
  - La prima è la **verifica statica**, che permette di controllare proprietà sui valori osservati, ad esempio confrontando campi di eventi differenti oppure verificando l'unicità dei valori raccolti.
  - La seconda è la **verifica temporale**, utilizzata quando i criteri riguardano anche le relazioni temporali tra gli eventi.
  In questo caso vengono utilizzate formule MFOTL, mentre la loro valutazione è affidata a _MonPoly_, un motore di verifica temporale esterno integrato nella pipeline.
  Il sistema prepara quindi gli eventi temporizzati e le formule richieste, esegue le verifiche e ne raccoglie i risultati, che contribuiranno alla determinazione del verdetto e alla produzione del report.

## 18. Testing

Passiamo ai test sulle catture originali.

## 19. Risultati dei test baseline

La tabella unisce le tabelle Open5GS e free5GC del capitolo 6 della tesi. Open5GS: 6 PASS, 1 FAIL e 3 INCONCLUSIVE su 10 catture. free5GC: 6 PASS su 6 catture. Il trattino indica un caso non riportato per quella implementazione, non un esito INCONCLUSIVE. NRF restituisce HTTP 200 anziché 403. Per RES* su Open5GS, B ha binding di identità mancanti; C e D non hanno match completi.

## 20. Mutation testing

Verifichiamo come cambia il verdetto quando alteriamo le evidenze.

## 21. Mutation testing: il processo

La pipeline analizza prima la PCAP originale e produce il report baseline. Un motore di mutazione esterno e offline riceve la PCAP originale e i riferimenti alle evidenze dal report baseline: non viene chiamato automaticamente dalla pipeline. Modifica valori, tempi o messaggi, producendo una PCAP mutata. Questa rientra nella stessa pipeline con le stesse regole DSL e genera il report mutation. Cambiano soltanto le evidenze; il confronto con il verdetto atteso permette di valutare la risposta del verificatore.

## 22. Risultati del mutation testing

Complessivamente sono stati realizzati **13 scenari di mutazione**, e in tutti i casi i risultati osservati sono stati coerenti con quelli attesi.
  Tra questi, due esempi sono particolarmente significativi.
  La distribuzione è NRF 1, UDM 2, AMF Synchronization Failure 4 (3 Case A e 1 Case B), UPF 2 e AMF RES* 4. Gli esiti sono quelli attesi nei 13 scenari considerati: non costituiscono una prova di correttezza universale del verificatore.
  Il primo esempio riguarda _AMF Synchronization Failure, Case A_ su Open5GS, dove abbiamo introdotto mutazioni statiche, temporali e combinate.
  Come si vede nella tabella, modificando soltanto i valori dei messaggi fallisce la verifica statica, mentre quella temporale continua a essere soddisfatta. Alterando invece gli intervalli di tempo avviene il contrario; modificando entrambi, falliscono entrambe le verifiche.
  Il secondo esempio riguarda _UPF TEID Uniqueness_, dove abbiamo valutato due situazioni differenti.
  Introducendo un F-TEID duplicato, il sistema rileva la violazione del criterio di unicità e restituisce `FAIL`.
  Rimuovendo invece gli eventi necessari alla verifica, il sistema non dispone più di evidenze sufficienti e restituisce `INCONCLUSIVE`.
  Quest'ultimo risultato è particolarmente importante, perché mostra che il verificatore distingue **una proprietà effettivamente violata da una proprietà che non può essere valutata con le evidenze disponibili**.

## 23. Conclusioni e sviluppi futuri

Chiudiamo con i limiti emersi e le direzioni di sviluppo.

## 24. Futuri sviluppi

I risultati, anche nel mutation testing, collegano i verdetti alle condizioni osservate e alle evidenze che li giustificano. La valutazione dipende però dalle evidenze disponibili e dai criteri rappresentabili: il sistema è stato sperimentato su un insieme specifico di casi SCAS, non su qualsiasi procedura. Due sviluppi futuri: ampliare i test con normalizzatori per nuovi protocolli e nuove evidenze; automatizzare maggiormente il mutation testing usando la DSL per individuare eventi e campi da alterare, riducendo la logica dedicata. Le operazioni concrete restano specifiche dei protocolli. Il contributo rende la verifica un processo più sistematico, con conclusioni ricostruibili, motivate e riconducibili alle evidenze. Questa è la conclusione del discorso; segue soltanto la schermata dei ringraziamenti.

## 25. Grazie per l’attenzione. Domande?

Grazie per l’attenzione. Sono a disposizione per le domande.

