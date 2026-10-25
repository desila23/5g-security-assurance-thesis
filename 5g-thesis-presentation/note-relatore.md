# Note del relatore — revisione finale

Generate dai sorgenti canonici. I nomi dei file storici mantengono la vecchia numerazione; l’ordine effettivo è in slides.json.

## 1. Titolo della tesi

Buongiorno, oggi vi presenterò il lavoro svolto per la mia tesi, che riguarda la progettazione di un linguaggio per verificare gli esiti dei test di sicurezza SCAS del 5G, utilizzando come evidenze le catture di traffico di rete.

## 2. Introduzione

Passiamo al contesto e al problema.

## 3. 5G Core: Network Functions e interazioni

Il 5G Core comprende diverse Network Functions che cooperano tra loro. Le comunicazioni seguono protocolli e procedure standardizzati. Funzioni e interazioni devono soddisfare requisiti di sicurezza. Lo schema riutilizza la topologia semplificata: control plane, user plane e interfacce principali.

## 4. Le Security Assurance Specification

Una volta eseguita una di queste prove è quindi necessario valutare se il comportamento osservato sia conforme a quanto previsto dalla specifica.
  Tra le evidenze disponibili possiamo avere una cattura del traffico di rete, in formato PCAP, insieme al verdetto ottenuto dal test. Il problema, però, è che la disponibilità di queste informazioni non rende necessariamente evidenti le motivazioni che hanno portato a quel risultato.
  Infatti, all'interno della cattura sono presenti numerosi messaggi, tra cui anche quelli rilevanti per il test in esame, ma la cattura, da sola, non indica quali di questi messaggi siano stati utilizzati per la verifica, né quali condizioni siano state effettivamente soddisfatte o violate.
  L'esigenza da cui nasce questo lavoro è quindi quella di rendere più esplicito e ricostruibile il legame tra il verdetto e le evidenze che lo giustificano.
  L'idea è ottenere un risultato di verifica accompagnato da un report strutturato, che documenti i criteri valutati, le informazioni osservate e gli elementi della cattura che hanno contribuito a determinare quel risultato.

## 5. Da human-readable a machine-readable

Le NF sono componenti software, mentre le SCAS sono scritte in linguaggio naturale. Come può il sistema sapere quali messaggi cercare, quali informazioni confrontare e quali condizioni verificare? Serve una rappresentazione strutturata dei criteri. La formalizzazione è del progettista; il software applica automaticamente le regole alle evidenze. La traduzione SCAS → DSL non è automatica.

## 6. Regole differenti, verificatore comune

Un primo approccio consiste nello scrivere un programma specifico per ciascun test: i criteri sono incorporati nel codice e la logica è poco riutilizzabile. L’animazione mostra la separazione dei criteri dalla logica software. Regole differenti alimentano un unico motore, che seleziona le evidenze, applica i criteri e produce verdetto e report. La DSL, introdotta nella slide successiva, esprime queste regole.

## 7. Una DSL per selezionare e verificare

Per esprimere le regole ho progettato una Domain-Specific Language. Ha due compiti: selezionare le evidenze all’interno della cattura e definire le condizioni da verificare su quelle evidenze. Le evidenze selezionate collegano i due passaggi. Il contributo comprende quindi il linguaggio e una pipeline comune che analizza il traffico.

## 8. Architettura della pipeline

Vediamo come la pipeline passa dalla cattura alle evidenze e al verdetto.

## 9. Architettura proposta

Per realizzare la soluzione appena introdotta, il sistema è stato organizzato in una pipeline composta da più fasi, che parte dalle catture di traffico raccolte durante l'esecuzione dei test e arriva a produrre un risultato di verifica motivato.
  La pipeline riceve in input le catture PCAP e le regole espresse nella DSL.

## 10. Dal traffico alle evidenze del test

L’individuazione delle evidenze ha due livelli. Prima TShark estrae le informazioni dei protocolli coinvolti nel test e i normalizzatori le trasformano in MessageEvent. Poi la DSL seleziona gli eventi necessari per quel caso SCAS. Test differenti possono quindi riutilizzare gli stessi normalizzatori.

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

La DSL ha due blocchi. Selezione: SEQUENCE per successioni ordinate, OPTIONAL per eventi facoltativi e COLLECT per eventi dello stesso tipo. Gli alias permettono di richiamare eventi e collezioni. Verifica: REQUIRE e UNIQUE per controlli statici, MFOTL per proprietà temporali. L’esempio NRF collega richiesta, risposta e status atteso 403.

## 14. Dalla regola all’automa

Per riconoscere le sequenze DSL il sistema costruisce un NFA con l’algoritmo di Thompson. Da ogni Atom, nodo che rappresenta un evento nella regola, deriva un frammento con stato iniziale, stato finale e transizione. Le transizioni epsilon uniscono i frammenti senza consumare eventi. B è opzionale: l’automa riconosce A-B-C oppure A-C. Seguire i passi mantenendo questa distinzione tra Atom e frammento.

## 15. Riconoscimento della sequenza

Il matcher usa l’automa sugli eventi normalizzati. Gli eventi selezionati rispettano l’ordine, ma non devono essere consecutivi: quelli non richiesti sono ignorati. Se arriva un nuovo possibile inizio che il candidato corrente non può consumare, il candidato viene interrotto e il matcher riparte. Nell’esempio A(1) viene scartato a favore di A(3); il risultato è A(3), B(4), C(6).

## 16. Dal Match al BindingContext

Il matcher riceve NFA ed eventi normalizzati e produce il Match. Nell’esempio della slide precedente riconosce A(3), B(4), C(6). Nel codice Match contiene start_index, end_index e bindings: una mappa dagli alias agli oggetti MessageEvent. Per la traccia illustrata, gli indici Python sono 2 e 5, corrispondenti alle posizioni 3 e 6 della numerazione da 1 usata nel disegno. I binding sono a → evento A in posizione 3, b → evento B in posizione 4, c → evento C in posizione 6. to_binding_context() crea un nuovo dizionario con le stesse associazioni e gli stessi oggetti evento; non ne trasforma i campi e non porta gli indici nel BindingContext. I numeri indicano posizioni nell’esempio, non frame reali. event.a, event.b ed event.c sono tipi didattici. Nel close-up vediamo gli oggetti MessageEvent riferiti dai tre alias.

## 17. Motore di verifica

Il verificatore usa gli eventi nel BindingContext per valutare i criteri della DSL. I controlli statici valutano i valori; quelli temporali usano MFOTL e MonPoly. La pipeline prepara formule ed eventi compatibili con MonPoly, che li valuta. I risultati vengono combinati nel verdetto e nel report.

## 18. Testing

Per valutare il sistema sono stati considerati diversi casi SCAS. La valutazione comprende le catture originali e una successiva fase di mutation testing.

## 19. Risultati dei test baseline

16 catture originali da Open5GS e free5GC: 12 PASS, 1 FAIL e 3 INCONCLUSIVE. NRF richiede HTTP 403, ma nella cattura si osserva 200: il FAIL è quindi il risultato atteso dal verificatore. AMF Synchronization Failure ha controlli statici e temporali soddisfatti su entrambe le implementazioni. I tre INCONCLUSIVE sono le varianti Open5GS AMF RES* B–D con evidenze insufficienti. Il trattino indica un caso non riportato per quell’implementazione. Distinguere criteri soddisfatti, violati e non valutabili.

## 20. Mutation testing

I risultati sulle catture originali non bastano da soli a valutare l’affidabilità del verificatore, perché alcuni test ne hanno guidato lo sviluppo. Per osservare la risposta a condizioni differenti si introduce una fase di mutation testing.

## 21. Mutation testing: il processo

Si parte dalla PCAP originale e dal report baseline. Un mutatore esterno e offline usa i riferimenti del report per selezionare i frame rilevanti e introdurre modifiche controllate. La nuova cattura viene analizzata con la stessa pipeline e le stesse regole DSL. Si confronta il verdetto osservato con quello atteso per la mutazione.

## 22. Risultati del mutation testing

13 scenari di mutazione su 13 hanno dato il verdetto atteso. Nel Case A AMF su Open5GS, le mutazioni statiche fanno fallire soltanto i controlli statici; quelle temporali soltanto i temporali; quelle combinate entrambi. Il secondo esempio riprende NRF dalla baseline: sostituendo nella cattura lo status HTTP 200 con 403, il criterio invariato response.status == 403 passa da FAIL a PASS. I due report NRF confermano valori osservati 200 e 403 e lo stesso criterio atteso 403. La distribuzione complessiva resta NRF 1, UDM 2, AMF Sync 4, UPF 2, AMF RES* 4.

## 23. Conclusioni e sviluppi futuri

Chiudiamo con i limiti emersi e le direzioni di sviluppo.

## 24. Futuri sviluppi

I risultati mostrano la possibilità di verificare i criteri SCAS sulle evidenze del traffico, producendo verdetti motivati e tracciabili. I limiti sono la disponibilità delle evidenze e l’insieme specifico di test sperimentati. Sviluppi futuri: nuovi protocolli e casi SCAS, maggiore automazione del mutation testing guidata dalla DSL. L’obiettivo è una verifica più sistematica, riproducibile e riconducibile alle evidenze. Questo discorso conclusivo accompagna la slide 24; la 25 è soltanto il ringraziamento.

## 25. Grazie per l’attenzione. Domande?

Grazie per l’attenzione. Sono a disposizione per le domande.

