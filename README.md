# 5G Security Assurance

Framework sperimentale per verificare criteri di sicurezza 5G SCAS a partire da catture di traffico di rete.

Il progetto prende in ingresso una cattura PCAP, estrae e normalizza il traffico tramite TShark, riconosce sequenze di messaggi descritte nella DSL, applica verifiche statiche e temporali e produce un report strutturato che collega ogni verdetto ai frame e ai valori osservati.

È inoltre supportato il **mutation testing**: una copia del PCAP originale viene modificata offline e analizzata nuovamente tramite la stessa pipeline, così da verificare che il criterio bersaglio reagisca alla modifica prevista.

> I pacchetti mutati **non vengono reinviati alle Network Function 5G**. Il mutation testing valida la pipeline di verifica, non il comportamento runtime dell’implementazione 5G.

---

## Struttura della repository

```text
captures/           Catture PCAP originali e mutate
config/             Configurazione dei test e delle mutazioni
dsl/                DSL, grammatica Lark e parser
traffic/            Lettura TShark e normalizzazione protocollare
traffic/resolvers/  Resolver semantici
matcher/            Modelli di matching, sequence matcher e collector
pipeline/           Pipeline generica di verifica
verifier/           Binding verifier, verifier legacy e temporal verifier
mfotl/              Signature, formule e log MonPoly
reporter/           Reporter generico e reporter legacy ancora necessari
mutation_testing/   Mutatori offline delle catture
├── fail/            Mutator che producono violazioni verificabili
├── inconclusive/    Mutator che rimuovono l'evidenza necessaria
└── ...              Mutator legacy/non ancora riorganizzati
utils/              Funzioni condivise
scasdk/             Componenti ScasDK originali e adattati
main.py             Runner principale
```

`scasdk/original/` contiene il sottoinsieme di ScasDK utilizzato come riferimento durante lo sviluppo, mentre `scasdk/adapted/` contiene la versione adattata impiegata dal progetto.

I file `subscriber.json` inclusi nella repository contengono esclusivamente parametri dell’ambiente sperimentale e vengono mantenuti per garantire la riproducibilità dei casi di test.


---


## Stato del refactoring
Il framework è attualmente in fase di refactoring con l'obiettivo di sostituire progressivamente la logica specifica dei singoli test con componenti generici e riutilizzabili.

Il principale cambiamento consiste nella separazione tra normalizzazione del traffico, selezione dell'evidenza guidata dalla DSL, verifica e reporting.

### Nuovi componenti principali

#### `traffic/`

Contiene il livello di elaborazione del traffico specifico per protocollo.

Il suo scopo è trasformare l'output strutturato di TShark in una rappresentazione semantica comune, riutilizzabile da più test SCAS.

File principali:

- `traffic/models.py`
    - definisce la rappresentazione comune `MessageEvent`;
- `traffic/tshark_reader.py`
    - legge l'output strutturato prodotto da TShark;
- `traffic/http2_normalizer.py`
    - normalizza il traffico HTTP/2;
- `traffic/nas_normalizer.py`
    - normalizza il traffico NAS;
- `traffic/pfcp_normalizer.py`
    - normalizza il traffico PFCP;
- `traffic/resolvers/sbi_resolver.py`
    - assegna un significato semantico 5G agli scambi SBI trasportati su HTTP/2.

I normalizzatori sono specifici del protocollo e non del singolo test.

Possono quindi esporre più campi di quelli richiesti da uno specifico SCAS, con l'obiettivo di riutilizzare la stessa rappresentazione normalizzata in più test che utilizzano lo stesso protocollo.

---

#### `matcher/`

Contiene il livello di selezione dell'evidenza.

File principali:

- `matcher/models.py`
    - definisce `Match` e `BindingContext`;
- `matcher/matcher.py`
    - individua le sequenze di eventi richieste dai pattern `SEQUENCE`;
- `matcher/collector.py`
    - raccoglie gli insiemi di eventi richiesti da `COLLECT`.

Per i test basati su sequenze, il matcher individua una traccia compatibile con il pattern dichiarato nella DSL e associa gli eventi trovati agli alias definiti nel pattern.

Per i test basati su collezioni, il collector raccoglie tutti gli eventi semantici corrispondenti senza imporre un vincolo di ordinamento.

Entrambi i meccanismi producono un `BindingContext` comune, che viene poi utilizzato dal verificatore.

---

#### `pipeline/`

Contiene le pipeline generiche di verifica.

File principali:

- `pipeline/sequence_pipeline.py`
    - esegue la verifica basata su sequenze;
- `pipeline/collect_pipeline.py`
    - esegue la verifica basata su collezioni.

Le due pipeline condividono la stessa architettura generale e convergono sul livello comune di binding e verifica.

---

#### `reporter/generic_reporter.py`

La precedente logica di reporting specifica per singolo test viene sostituita da un reporter comune.

Il reporter generico produce la stessa struttura di output indipendentemente dal test e include:

- metadati del test;
- PCAP sorgente e hash SHA-256;
- configurazione della pipeline;
- criteri di verifica;
- risultati delle verifiche;
- binding dell'evidenza;
- spiegazione del verdict;
- verdict finale.

Il reporter supporta:

- test esclusivamente statici;
- test con verifica temporale;
- test basati su sequenze;
- test basati su collezioni;
- esiti `PASS`, `FAIL` e `INCONCLUSIVE`.

Le informazioni temporali vengono rappresentate in modo uniforme e risultano `N/A` quando il test non prevede alcun requisito temporale.

---

## Estensioni della DSL

La DSL è stata estesa per descrivere non soltanto le regole di verifica, ma anche il modo in cui l'evidenza richiesta dal test deve essere individuata nel traffico normalizzato.

File rilevanti:

- `dsl/grammar.lark`
- `dsl/parse_rule.py`

I principali costrutti di selezione dell'evidenza attualmente supportati sono:

### `SEQUENCE`

Utilizzato quando il test richiede un pattern ordinato di eventi semantici.

Esempio:

```
SEQUENCE {
    nrf.discovery.request AS request
    nrf.discovery.response AS response
}

REQUIRE response.status == 403
```

La sequenza viene elaborata dal matcher, che costruisce binding del tipo:

```
request  -> MessageEvent(...)
response -> MessageEvent(...)
```

I binding risultanti costituiscono l'evidenza specifica del test utilizzata dal verificatore.

### `COLLECT`

Utilizzato quando il test richiede un insieme di eventi piuttosto che una sequenza ordinata.

Esempio:

```
COLLECT pfcp.session_establishment_response AS responses

REQUIRE UNIQUE responses.f_teids
```

Il collector associa tutti gli eventi corrispondenti all'alias `responses`, dopo di che il verificatore applica la proprietà aggregata richiesta.

---

## Verifica generica sui binding

File rilevante:

- `verifier/binding_verifier.py`

Il verificatore ora opera su `BindingContext` invece che su strutture di evidenza specifiche per singolo test.

Un binding può contenere:

```
alias -> MessageEvent
```

oppure:

```
alias -> list[MessageEvent]
```

a seconda che l'evidenza sia stata ottenuta tramite `SEQUENCE` o `COLLECT`.

Il verificatore supporta regole di confronto generiche e operatori aggregati come `UNIQUE`.

Ad esempio:

```
REQUIRE UNIQUE responses.f_teids
```

verifica che lo stesso F-TEID non venga riutilizzato tra eventi raccolti differenti, mantenendo il riferimento ai frame che costituiscono l'evidenza.

---

## Verifica temporale

La verifica temporale rimane separata dalla verifica statica dei campi e viene eseguita tramite regole MFOTL valutate con MonPoly.

File rilevante:

- `verifier/temporal_verifier.py`

Il verificatore temporale ora agisce come componente generico della pipeline e non contiene più logica di esecuzione specifica per il test AMF.

I test di synchronization failure dell'AMF mostrano attualmente l'interazione tra:

- matching di sequenze;
- verifica statica dei binding;
- verifica temporale.

---

## Requisiti

- Python 3.10+
- TShark / Wireshark
- MonPoly per le proprietà temporali dei test AMF
- Dipendenze Python elencate in `requirements.txt`

Creazione e attivazione dell’ambiente virtuale:

```bash
python3 -m venv ~/.venvs/5g-security-assurance
source ~/.venvs/5g-security-assurance/bin/activate
pip install -r requirements.txt
```

Verifica degli strumenti esterni:

```bash
tshark --version
monpoly -version
```

`MonPoly` è richiesto soltanto per i test che includono proprietà MFOTL.

---

## Esecuzione dei test

Tutti i comandi devono essere eseguiti dalla root del progetto.

Elenco dei test disponibili:

```bash
python main.py --list
```

Esecuzione di un singolo test:

```bash
python main.py --test nrf_disc_auth_slice
```

Esecuzione dello scenario di mutazione associato:

```bash
python main.py --mutation nrf_disc_auth_slice
python main.py --mutation amf_sync_failure_case_a --variant static
python main.py --mutation upf_teid_uniqueness --variant inconclusive
```

Esecuzione dell’intera suite di validazione:

```bash
python main.py --all
```

---

## Test migrati alla nuova pipeline

### NRF Discovery Authorization

Esecuzione baseline:

```bash
python main.py --test nrf_disc_auth_slice
```

Mutation:

```bash
python main.py --mutation nrf_disc_auth_slice
```

La cattura originale produce intenzionalmente:

```text
FAIL
```

perché la risposta NRF ha status HTTP `200`, mentre la DSL richiede:

```text
403
```

La mutation modifica lo status e produce:

```text
PASS
```

---

### AMF Synchronization Failure — Case A

Baseline:

```bash
python main.py --test amf_sync_failure_case_a
```

Mutation static:

```bash
python main.py --mutation amf_sync_failure_case_a --variant static
```

Mutation temporal:

```bash
python main.py --mutation amf_sync_failure_case_a --variant temporal
```

Mutation combinata:

```bash
python main.py --mutation amf_sync_failure_case_a --variant both
```

Risultati attesi:

```text
Baseline       Static PASS   Temporal PASS
Static mut.    Static FAIL   Temporal PASS
Temporal mut.  Static PASS   Temporal FAIL
Both mut.      Static FAIL   Temporal FAIL
```

---

### AMF Synchronization Failure — Case B

Baseline:

```bash
python main.py --test amf_sync_failure_case_b
```

Mutation static:

```bash
python main.py --mutation amf_sync_failure_case_b --variant static
```

Mutation temporal:

```bash
python main.py --mutation amf_sync_failure_case_b --variant temporal
```

Mutation combinata:

```bash
python main.py --mutation amf_sync_failure_case_b --variant both
```

Risultati attesi:

```text
Baseline       Static PASS   Temporal PASS
Static mut.    Static FAIL   Temporal PASS
Temporal mut.  Static PASS   Temporal FAIL
Both mut.      Static FAIL   Temporal FAIL
```


### UPF F-TEID Uniqueness

Dimostra:

- normalizzazione PFCP;
- `COLLECT`;
- verifica aggregata;
- operatore `UNIQUE`;
- gestione esplicita di `INCONCLUSIVE`.

Baseline:
```
python main.py --test upf_teid_uniqueness
```

Mutation FAIL
```
python main.py --mutation upf_teid_uniqueness --variant fail
```

Mutation INCONCLUSIVE
```
python main.py --mutation upf_teid_uniqueness --variant inconclusive
```

Risulati attesi
```
Baseline                  PASS
Fail mutation             FAIL
Inconclusive mutation     INCONCLUSIVE
```



---

## Esiti della verifica

Il framework distingue attualmente tre possibili esiti:

### `PASS`

L'evidenza richiesta è disponibile e tutti i criteri applicabili risultano soddisfatti.

### `FAIL`

L'evidenza richiesta è disponibile, ma almeno un criterio di verifica risulta violato.

### `INCONCLUSIVE`

La cattura disponibile non contiene evidenza sufficiente per valutare il criterio richiesto.

Ad esempio, se:

```
COLLECT pfcp.session_establishment_response AS responses
```

non raccoglie alcun evento, il test non viene considerato `FAIL`.

Il risultato è invece `INCONCLUSIVE`, perché manca l'evidenza necessaria per eseguire la verifica.

Il report include anche:

- motivo dell'esito inconclusivo;
- tipo di messaggio atteso;
- alias DSL coinvolto;
- numero di eventi raccolti.



---

## Famiglie di test implementate

| Famiglia di test | Proprietà principale | Pipeline |
| --- | --- | --- |
| NRF Discovery Authorization | Status HTTP della risposta | Generic sequence pipeline |
| AMF Synchronization Failure — Case A | Static rules + risposta AUSF entro T3520 | Generic sequence pipeline |
| AMF Synchronization Failure — Case B | Static rules + assenza Authentication Request entro T3520 | Generic sequence pipeline |
| UDM AKA Resynchronization | Coerenza RAND, AUTS e MAC | Legacy |
| UDM SUCI De-concealment | SUPI restituito uguale a quello atteso | Legacy |
| UPF TEID Uniqueness | Unicità F-TEID `{teid, ipv4}` | Generic collect pipeline |
| RES* Verification Failure — Cases A–D | Verifiche sui vettori di autenticazione e failure path | Legacy |

Le famiglie indicate come `Legacy` sono funzionanti ma non sono ancora state migrate alla nuova architettura generica.

---

## Mutation testing

Anche il mutation testing è stato riorganizzato.

Le configurazioni possono ora contenere più varianti sotto lo stesso test baseline.

Esempio:

```
amf_sync_failure_case_a
└── variants
    ├── static
    ├── temporal
    └── both
```

e:

```
upf_teid_uniqueness
└── variants
    ├── fail
    └── inconclusive
```

La directory del mutation testing è inoltre in fase di organizzazione in base all'esito atteso:

```
mutation_testing/
├── fail/
│   └── mutate_pfcp_fteid.py
│
└── inconclusive/
    └── mutate_pfcp_missing_events.py
```

### Tipi di mutation attualmente utilizzati

#### Mutation statica

Modifica i dati del traffico in modo che una regola statica cambi verdict.

Esempio:

```
PASS -> FAIL
```

sulla regola `resync.rand`.

#### Mutation temporale

Modifica i timestamp dei pacchetti in modo da mantenere valida l'evidenza statica ma violare la proprietà temporale.

Esempio:

```
Static:   PASS
Temporal: FAIL
```

#### Mutation combinata

Introduce contemporaneamente una violazione statica e una temporale.

Esempio:

```
Static:   FAIL
Temporal: FAIL
```

#### Mutation per evidenza mancante

Rimuove dalla PCAP i frame che costituiscono l'evidenza necessaria per il test.

Permette di verificare una transizione del tipo:

```
PASS -> INCONCLUSIVE
```

senza modificare DSL, verificatore o configurazione del test.


## Output della nuova pipeline

I test migrati producono direttamente un report JSON generico.

Il report contiene:

```text
metadata
test
source
configuration
criteria
verification
evidence
explanation
verdict
```

Per ciascun criterio vengono riportati:

- engine utilizzato;
- verdict;
- evidence frames;
- campo verificato;
- operatore;
- valore atteso;
- valore osservato;
- eventuale campo di confronto.

Per i criteri temporali vengono inoltre riportati:

- motore MonPoly;
- modalità di verifica;
- presenza o assenza di una violazione;
- output prodotto da MonPoly.


### Regression corrente
L'intera suite può essere eseguita con:

```bash
python main.py --all
```

Stato corrente:
Completed: 25/25 scenarios



---


## File principali modificati durante il refactoring

I file più rilevanti modificati o introdotti sono:

- `main.py`
    
    - dispatch delle pipeline generiche;
    - configurazione dinamica dei test mutati;
    - supporto alle mutation variants;
    - gestione di `PASS`, `FAIL` e `INCONCLUSIVE`;
    - aggiornamento di `--list`;
    - aggiornamento di `--all`;
    - output CLI compatto per il mutation testing;
- `config/tests.json`
    
    - configurazione delle nuove pipeline per i test migrati;
- `config/mutation_tests.json`
    
    - supporto alle varianti di mutation e all'ereditarietà della configurazione baseline;
- `dsl/grammar.lark`
    
    - supporto a `SEQUENCE`, `COLLECT` e regole aggregate;
- `dsl/parse_rule.py`
    
    - parsing delle dichiarazioni di sequenza e collezione;
- `verifier/binding_verifier.py`
    
    - verifica generica sui `BindingContext`;
    - supporto a `UNIQUE`;
- `verifier/temporal_verifier.py`
    
    - utility generiche per la verifica temporale;
- `utils/mutation_utils.py`
    
    - supporto al report unificato nei mutator migrati;
- `reporter/generic_reporter.py`
    
    - generazione del report comune.


---

## Compatibilità legacy

Alcune parti del codice sono ancora esplicitamente marcate come:

```
LEGACY
```

oppure:

```
COMPATIBILITÀ LEGACY
```

Questi rami sono temporanei.

Sono attualmente necessari perché alcuni test non sono ancora stati migrati alla nuova pipeline e continuano a dipendere dalla precedente architettura basata su:

```
evidence.json
verification.json
extractor specifici per test
```

I rami legacy verranno progressivamente rimossi con la migrazione dei test rimanenti.

I principali test ancora da migrare completamente sono i casi UDM e RES*.


---

## Direzione architetturale attuale

La precedente architettura può essere sintetizzata come:

```
PCAP
  ↓
extractor specifico del test
  ↓
evidenza specifica del test
  ↓
verificatore
  ↓
reporter specifico
```

La nuova architettura è invece:

```
PCAP
  ↓
normalizzazione specifica del protocollo
  ↓
traccia di eventi semantici
  ↓
selezione dell'evidenza guidata dalla DSL
  ├── automa/matcher per SEQUENCE
  └── collector per COLLECT
  ↓
BindingContext
  ↓
verifica statica / temporale generica
  ↓
PASS / FAIL / INCONCLUSIVE
  ↓
reporter generico
```

Il principio progettuale principale è quindi:

> I componenti specifici del protocollo interpretano il traffico di rete, mentre il comportamento specifico del singolo test viene espresso attraverso la DSL e attraverso meccanismi generici di selezione dell'evidenza e verifica.