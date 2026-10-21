# Domain-Specific Language e motore di verifica

## Progettazione della DSL
La progettazione della DSL parte dai requisiti individuati nel Capitolo 3 e dall'esigenza di rappresentare, in forma dichiarativa, gli elementi del test necessari alla verifica. Il linguaggio è stato quindi definito a partire dalle caratteristiche ricorrenti osservate nei casi di test considerati, privilegiando un insieme limitato di capacità direttamente riconducibili alle esigenze del dominio.

La DSL è stata mantenuta volutamente circoscritta, privilegiando un equilibrio tra espressività e semplicità. L'obiettivo non è fornire un linguaggio generale per l'analisi del traffico di rete, ma definire una sintassi compatta e leggibile, capace di esprimere i criteri di verifica considerati senza esporre i dettagli dei protocolli e dei componenti sottostanti. A tale scopo, le regole utilizzano il vocabolario semantico prodotto dalle fasi di normalizzazione e risoluzione, anziché i campi originariamente estratti dalla cattura.

A livello strutturale, una specifica distingue due responsabilità: la descrizione dell'evidenza da ricercare e la definizione delle proprietà da valutare su di essa. Questa separazione si riflette direttamente nella grammatica del linguaggio: alla prima infatti appartengono i costrutti dedicati all'individuazione di eventi, mentre alla seconda appartengono le espressioni utilizzate dai meccanismi di verifica statica e temporale.

Le scelte progettuali descritte costituiscono la base della grammatica presentata nella sezione successiva, nella quale vengono formalizzati i costrutti sintattici e le relative modalità di composizione.

## Struttura della grammatica
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

## Rappresentazione interna delle regole
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

## Selezione mediante `SEQUENCE`
Questa sezione descrive il meccanismo utilizzato per individuare, all'interno del traffico osservato, le sequenze di eventi definite attraverso il costrutto `SEQUENCE`.

### Il pattern sequenziale
La selezione tramite `SEQUENCE` richiede di individuare, all'interno della traccia di eventi, una successione di messaggi che rispetti l'ordine specificato nella DSL.

Una possibile soluzione consisterebbe nell'implementare un algoritmo di ricerca dedicato a ciascuna sequenza. Tale approccio richiederebbe tuttavia di adattare la logica di riconoscimento alle diverse strutture dei pattern, limitando la generalità del sistema.

L'approccio adottato consiste invece nel compilare il pattern, precedentemente rappresentato mediante un AST, in un **automa a stati finiti non deterministico**. L'automa descrive formalmente gli eventi attesi e le possibili transizioni degli stati, fornendo una rappresentazione del pattern indipendente dallo specifico caso di test.

### Formalizzazione dell'automa
Per rappresentare i pattern sequenziali viene utilizzato un **Nondeterministic Finite Automaton (NFA)**, che può essere formalizzato mediante la quintupla: 
$$
A = \langle \Sigma, \ Q, \ q_{0}, \ Q_{F}, \ \delta \rangle
$$
dove
- $\Sigma$ è l'alfabeto, costituito dall'insieme dei **tipi semantici di evento** riconosciuti dall'automa;
- $Q$ è l'insieme finito degli stati;
- $q_{0} \in Q$ è lo stato iniziale;
- $Q_{F} \subseteq Q$ è l'insieme degli stati finali. Nell'implementazione proposta viene utilizzato un unico stato di accettazione, pertanto $Q_{F} = \{ q_{f} \}$;
- $\delta$ è la funzione di transizione non deterministica, definita come $$\delta: Q \times (\Sigma \ \cup \ \{  \varepsilon \}) \to \mathcal{P}(Q)$$

dove $\mathcal{P}(Q) = 2^{Q}$ indica l'insieme delle parti di $Q$, ossia l'insieme di tutti i suoi sottoinsiemi.

A differenza degli automi tradizionalmente impiegati per il riconoscimento di stringe, l'alfabeto considerato non è costituito da caratteri, ma dai tipi semantici associati ai `MessageEvent` prodotti dalle fasi precedenti della pipeline.

L'automa definisce quindi le possibili successioni di eventi ammesse dal pattern, mentre il **matcher**
è il componente incaricato di utilizzarlo per individuare le corrispondenze all'interno della traccia osservata. Il funzionamento di tale componente verrà approfondito dopo aver descritto il processo di costruzione dell'automa.

### Le $\varepsilon$-transizioni
Una transizione ordinaria richiede di consumare un simbolo dell'alfabeto, ossia la lettura di un evento il cui tipo semantico corrisponda a quello atteso dalla transizione. Tale operazione può essere rappresentata come:

$$
q_{i} \xrightarrow{a} q_{j}
$$
dove $a \in \Sigma$ è il tipo di evento richiesto per passare dallo stato $q_{i}$ allo stato $q_{j}$.

Una transizione $\varepsilon$, invece, ha la forma:

$$
q_{i} \xrightarrow{\varepsilon} q_{j}
$$
e permette di passare da uno stato all'altro **senza consumare alcun evento**, ossia senza avanzare nella lettura della traccia.

Questa possibilità è fondamentale per la costruzione dei pattern sequenziali, in particolare per rappresentare blocchi `OPTIONAL`. Le modalità con cui tali transizioni vengono introdotte nell'automa saranno approfondite nella sezione successiva, dedicata alla costruzione di Thompson.

### Compilazione del pattern mediante Thompson
Una volta ottenuto l'AST, il pattern sequenziale viene compilato in un NFA mediante la **costruzione di Thompson**. \cite{thompson_1968} Tale procedimento si basa su un approccio composizionale: a ciascun nodo dell'albero viene associato un frammento dell'automa, dotato di uno stato iniziale e uno finale; i frammenti vengono successivamente collegati per ottenere l'automa corrispondente alla sequenza completa.

La costruzione dipende dal tipo di nodo considerato:
- **Atom:** genera un frammento costituito da due stati collegati da una transizione etichettata con il tipo semantico dell'evento atteso.
- **Sequence:** combina i frammenti dei propri elementi nell'ordine specificato, collegando lo stato finale di ciascun frammento allo stato iniziale del successivo mediante una transizione $\varepsilon$. 
- **Optional:** introduce due percorsi alternativi mediante transizioni $\varepsilon$. Il primo attraversa il frammento corrispondente agli elementi opzionali, mentre il secondo permette di raggiungere direttamente lo stato di uscita, senza consumare gli eventi contenuti nel blocco.

Considerando il pattern sequenziale già introdotto nella Sezione 5.3, il compilatore costruisce i frammenti relativi ai singoli nodi dell'AST e li collega mediante transizioni ε, ottenendo un automa che ammette sia il percorso completo `a → b → c`, sia quello in cui l'evento opzionale viene omesso, `a → c`.


\begin{figure}[!htbp]
\centering
\includegraphics[width=\textwidth,height=0.65\textheight,keepaspectratio]{figure/nfa_thompson.png}
\caption{Costruzione dell'automa NFA mediante composizione dei frammenti elementari di Thompson.}
\label{fig:thompson}
\end{figure}


### Configurazioni attive e riconoscimento degli eventi
L'automa costruito mediante Thompson descrive i percorsi ammessi dal pattern, ma non conosce informazioni sugli eventi effettivamente presenti nella cattura. Il suo utilizzo è affidato al **matcher**, che riceve in ingresso l'NFA e la sequenza ordinata di `MessageEvent`, con il compito di individuare i percorsi che consentono di raggiungere lo stato finale.

Durante questa operazione non è sufficiente conoscere lo stato raggiunto nell'automa, poiché è necessario conservare anche i riferimenti agli eventi che hanno contribuito al riconoscimento. A questo scopo viene introdotta una struttura denominata `ActiveConfiguration`, formalizzabile  come: 

$$
C = \langle q, B \rangle
$$

dove 
- $q \in Q$ è lo stato corrente dell'automa;
- $B$ è una funzione parziale che associa gli alias definiti nella DSL ai `MessageEvent` già riconosciuti.

Il matcher può mantenere contemporaneamente più configurazioni attive, ciascuna caratterizzata dal proprio stato e dai binding progressivamente costruiti.

Poiché l'automa può contenere transizioni $\varepsilon$, per ogni stato corrente devono essere considerati anche quelli raggiungibili senza consumare ulteriori eventi. A tale scopo viene utilizzata una $\varepsilon \text{-closure}$, definita formalmente come: 

$$
\varepsilon\text{-closure}(q) = \{ p \in Q \mid q \xrightarrow{ \ \ \varepsilon^{*} \ } p\}
$$

La chiusura comprende tutti gli stati raggiungibili da $q$ attraverso zero o più transizioni $\varepsilon$, incluso lo stesso $q$ . L'espansione di una configurazione attraverso tali transizioni mantiene invariati i binding già acquisiti, poiché non viene riconosciuto alcun nuovo evento.

Durante la scansione della traccia, il matcher confronta il `message_type` di ciascun evento con quello richiesto dalle transizioni uscenti dagli stati delle configurazioni attive. Quando viene individuata una transizione compatibile, la configurazione avanza verso lo stato di destinazione e il `MessageEvent` osservato viene associato all'alias definito nel corrispondente `Atom`. I binding vengono quindi aggiornati e vengono considerate le ulteriori transizioni $\varepsilon$ raggiungibili dal nuovo stato.

Una caratteristica importante è che la selezione non richiede che gli eventi previsti dal pattern siano consecutivi nella traccia. Quando un evento non può essere consumato da una determinata configurazione, quest'ultima può rimanere attiva, consentendo di proseguire la ricerca con gli eventi successivi, fatta salva la politica di riavvio del candidato descritta nella sezione successiva.

La possibilità di mantenere più configurazioni attive consente inoltre di seguire contemporaneamente i percorsi alternativi prodotti da `OPTIONAL`, senza dover stabilire anticipatamente se gli eventi opzionali saranno presenti. Le modalità con cui vengono avviati e gestiti i diversi tentativi di riconoscimento saranno approfondite nella sezione successiva.

### Politica di matching e produzione dei risultati
All'interno di una cattura possono essere presenti più occorrenze degli eventi descritti sulla stessa `SEQUENCE`, anche in posizioni differenti della traccia. Il matcher deve quindi essere in grado di riconoscere il pattern senza presupporre che questo abbia inizio con il primo evento osservato. A tale scopo, ogni volta che incontra un evento compatibile con l'inizio della sequenza, avvia un nuovo **candidato di riconoscimento**, ossia un tentativo indipendente di individuare tutti gli eventi richiesti dal pattern a partire da quella posizione. La compatibilità viene determinata considerando le transizioni disponibili a partire dallo stato iniziale dell'NFA, comprese quelle raggiungibili attraverso $\varepsilon \text{-transizioni}$.

Durante l'elaborazione di ciascun candidato viene applicata una specifica **politica di riavvio (*restart policy*)**, introdotta per evitare che eventi appartenenti a tentativi distinti vengano associati alla stessa sequenza. In particolare, quando viene osservato un evento che potrebbe avviare un nuovo riconoscimento, il matcher verifica se questo possa essere consumato dalle configurazioni attive del candidato corrente. Qualora nessuna di esse risulti compatibile, il tentativo viene interrotto, lasciando che l'evento possa costituire il punto di partenza di un nuovo candidato.

Il riconoscimento si considera completo quando almeno una configurazione raggiunge lo stato finale dell'NFA. Il matcher produce allora un oggetto `Match`, nel quale vengono conservate la posizione iniziale del candidato (`start_index`), la posizione in cui è stato raggiunto lo stato finale (`end_index`) e le associazioni tra alias ed eventi riconosciuti (`bindings`). Per ciascun candidato viene considerato il primo punto di completamento, nel quale possono tuttavia essere presenti più configurazioni accettanti, corrispondenti a percorsi differenti dell'automa.

Questa possibilità assume particolare rilevanza in presenza di blocchi `OPTIONAL`, poiché percorsi diversi possono completare il riconoscimento nello stesso intervallo della traccia, pur avendo individuato quantità differenti di evidenza. Per gestire tali situazioni viene adottato un **criterio di dominanza**, attraverso il quale vengono eliminati i match che risultano meno completi rispetto ad altri equivalenti. Un match domina un altro soltanto quando vengono rispettate le seguenti condizioni:
- i due match condividono `start_index` e `end_index`;
- gli alias del secondo costituiscono un sottoinsieme proprio di quelli del primo;
- per tutti gli alias comuni, le associazioni fanno riferimento agli stessi eventi osservati.
In questo modo vengono eliminati i match che non aggiungono evidenza rispetto ad altri più completi, preservando quelli che contengono associazioni differenti tra alias ed eventi.

Al termine del processo, il matcher restituisce l'insieme dei match completi individuati, ciascuno corredato dai relativi binding. Tali associazioni possono essere successivamente trasferite in un `BindingContext`, rendendo l'evidenza selezionata disponibile ai meccanismi di verifica descritti nelle sezioni successive.


## Selezione mediante `COLLECT`
Non tutti i casi di test richiedono il riconoscimento di una successione ordinata di eventi. In alcuni casi, l'evidenza necessaria è costituita dall'insieme delle occorrenze di una determinata tipologia, indipendentemente dall'ordine con cui queste compaiono nella traccia.
Per rispondere a tale esigenza, la DSL introduce il costrutto `COLLECT`, che consente di selezionare tutti i `MessageEvent` corrispondenti a uno specifico tipo semantico.

Una regola di raccolta può essere espressa come segue:
```
COLLECT pfcp.session_establishment_response AS responses
```
In questo esempio, `pfcp.session_establishment_response` identifica il tipo di evento da ricercare, mentre `responses` è l'alias assegnato alla collezione risultante.
La selezione avviene confrontando il `message_type` degli eventi disponibili con quello indicato nella regola, senza richiedere la costruzione di un automa.

Gli eventi individuati vengono associati all'alias all'interno del `BindingContext`. A differenza di `SEQUENCE`, dove ciascun alias identifica un singolo evento riconosciuto, nel caso di `COLLECT` il valore associato è una lista di `MessageEvent`, rappresentabile come:

$$
B(\texttt{responses}) = [e_1, e_2, e_3, ..., e_n]
$$
La struttura del `BindingContext` rimane quindi invariata, mentre cambia la natura dell'evidenza associata all'alias. Le due modalità di selezione, pur adottando meccanismi differenti, producono così una rappresentazione comune dei risultati.


## Verifica statica
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


## Verifica temporale
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

## Determinazione del verdetto
Una volta completata la selezione dell'evidenza e l'eventuale valutazione dei criteri statici e temporali, il sistema deve determinare l'esito complessivo del caso di test. A tale scopo, non è sufficiente distinguere tra condizioni soddisfatte e violate, perché possono verificarsi situazioni in cui l'evidenza disponibile non consente di effettuare una valutazione conclusiva.

Per gestire queste situazioni, il sistema prevede tre possibili verdetti: **PASS**, quando l'evidenza selezionata consente di verificare il soddisfacimento dei criteri richiesti; **FAIL**, quando viene rilevata una violazione; e **INCONCLUSIVE**, quando non è possibile formulare una valutazione conclusiva, ad esempio per l'assenza dell'evidenza necessaria o per l'impossibilità di individuare un'unica corrispondenza completa.

Nel caso della selezione mediante `SEQUENCE`, quest'ultima situazione può verificarsi quando nessun percorso dell'NFA raggiunge uno stato accettante. In assenza di un match completo, infatti, il sistema non dispone dei binding necessari per procedere alla verifica e restituisce `INCONCLUSIVE`. Lo stesso verdetto viene assegnato quando vengono individuati più match completi, poiché l'attuale implementazione richiede una selezione univoca per valutare i criteri.
Analogamente, nel caso di `COLLECT`, l'assenza di eventi corrispondenti al tipo semantico richiesto impedisce la valutazione dei criteri e determina un esito `INCONCLUSIVE`.

Per i casi di test che prevedono sia verifiche statiche che temporali, il verdetto complessivo viene determinato considerando i risultati di entrambe. Il test assume esito `PASS` quando tutti i criteri applicabili risultano soddisfatti e `FAIL` quando almeno uno di essi rileva una violazione. Qualora, invece, non sussistano le condizioni per una valutazione conclusiva, viene restituito `INCONCLUSIVE`, secondo i principi precedentemente descritti.

La determinazione del verdetto conclude il processo di verifica, distinguendo le violazioni effettivamente rilevate dai casi in cui l'evidenza non consente una valutazione conclusiva, mentre i risultati strutturati delle singole verifiche permettono di documentare nel report le motivazioni dell'esito ottenuto.
