# 5G Security Assurance

Framework sperimentale per verificare criteri di sicurezza 5G SCAS a partire da catture di traffico di rete.

Il progetto prende in ingresso una cattura PCAP, estrae e normalizza il traffico tramite TShark, riconosce sequenze di messaggi descritte nella DSL, applica verifiche statiche e temporali e produce un report strutturato che collega ogni verdetto ai frame e ai valori osservati.

È inoltre supportato il **mutation testing**: una copia del PCAP originale viene modificata offline e analizzata nuovamente tramite la stessa pipeline, così da verificare che il criterio bersaglio reagisca alla modifica prevista.

> I pacchetti mutati **non vengono reinviati alle Network Function 5G**. Il mutation testing valida la pipeline di verifica, non il comportamento runtime dell’implementazione 5G.

---

## Architettura attuale

Per i test già migrati, la pipeline corrente è:

```text
PCAP
  ↓
TShark generic structured extraction
  ↓
Protocol-specific normalization
  ↓
Semantic MessageEvent[]
  ↓
Correlation / event grouping
  ↓
DSL sequence
  ↓
AST
  ↓
Thompson NFA
  ↓
Sequence matcher
  ↓
Binding verifier
  ↓
MFOTL / MonPoly temporal verification
  ↓
Generic JSON report
```

L’obiettivo dell’architettura è separare:

- acquisizione del traffico;
- normalizzazione protocollare;
- riconoscimento della sequenza;
- verifica dei criteri;
- produzione dell’evidenza.

La logica specifica del singolo test viene progressivamente spostata dalla fase di estrazione verso:

- la DSL;
- i resolver semantici;
- la configurazione del test;
- le regole statiche e temporali.

Alcune famiglie di test non ancora migrate continuano temporaneamente a utilizzare la pipeline legacy basata su extractor specifici.

---

## Rappresentazione del traffico

Gli eventi normalizzati utilizzano il modello `MessageEvent`, che contiene informazioni comuni come:

```text
frame_number
timestamp
protocol
kind
src
dst
message_type
related_frames
correlation
fields
```

La normalizzazione attualmente implementata comprende:

- traffico HTTP/2;
- messaggi NAS 5GS;
- resolver semantici per messaggi SBI.

Esempi di tipi semantici prodotti:

```text
nrf.discovery.request
nrf.discovery.response
ausf.authentication.response
ausf.resynchronization.request
nas.authentication_request
nas.authentication_failure
```

---

## DSL e sequence matching

La DSL supporta la descrizione esplicita delle sequenze di messaggi.

Esempio:

```text
SEQUENCE {
    nrf.discovery.request AS request
    nrf.discovery.response AS response
}

REQUIRE response.status == 403
```

La `SEQUENCE` viene:

```text
DSL
 ↓
Lark parser
 ↓
AST
 ↓
Thompson compiler
 ↓
NFA
 ↓
matcher
```

Il matcher associa gli eventi ai rispettivi alias e produce un insieme di binding utilizzato successivamente dai verifier.

Le regole statiche possono confrontare:

- campo con valore costante;
- campo con campo appartenente a un altro binding.

Esempio:

```text
REQUIRE initial_auth.rand == initial_vector.rand
REQUIRE sync_failure.cause == 21
REQUIRE resync.auts == sync_failure.auts
```

---

## Verifica temporale

Le proprietà temporali vengono espresse in MFOTL ed eseguite tramite MonPoly.

### AMF Synchronization Failure — Case A

La proprietà temporale verifica che una nuova risposta AUSF venga osservata entro `T3520` dopo la richiesta di risincronizzazione.

```text
ResynchronizationRequest()
IMPLIES
EVENTUALLY[0,{TIMER_MS}] AusfAuthenticationResponse()
```

### AMF Synchronization Failure — Case B

La proprietà temporale verifica che non venga osservata una nuova Authentication Request entro `T3520` dopo il Synchronization Failure.

```text
SyncFailure()
IMPLIES
NOT EVENTUALLY[0,{TIMER_MS}] AuthenticationRequest()
```

Il valore corrente di `T3520` utilizzato nei test è:

```text
15000 ms
```

La generazione del log temporale è generica e guidata tramite `event_mapping` nella configurazione del test.

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

---

## Famiglie di test implementate

| Famiglia di test | Proprietà principale | Pipeline |
| --- | --- | --- |
| NRF Discovery Authorization | Status HTTP della risposta | Generic sequence pipeline |
| AMF Synchronization Failure — Case A | Static rules + risposta AUSF entro T3520 | Generic sequence pipeline |
| AMF Synchronization Failure — Case B | Static rules + assenza Authentication Request entro T3520 | Generic sequence pipeline |
| UDM AKA Resynchronization | Coerenza RAND, AUTS e MAC | Legacy |
| UDM SUCI De-concealment | SUPI restituito uguale a quello atteso | Legacy |
| UPF TEID Uniqueness | Unicità F-TEID `{teid, ipv4}` | Legacy |
| RES* Verification Failure — Cases A–D | Verifiche sui vettori di autenticazione e failure path | Legacy |

Le famiglie indicate come `Legacy` sono ancora funzionanti ma non sono ancora state migrate alla nuova architettura generica.

---

## Mutation testing

Le mutazioni sono definite in:

```text
config/mutation_tests.json
```

Il flusso generale è:

```text
PCAP originale
    ↓
esecuzione baseline
    ↓
selezione del target
    ↓
generazione del PCAP mutato
    ↓
riesecuzione della stessa pipeline
    ↓
confronto tra verdetto osservato e verdetto atteso
```

Esempi di mutazione:

- modifica dello status HTTP NRF;
- modifica del RAND nella richiesta di risincronizzazione;
- modifica dei timestamp per violare una proprietà temporale;
- combinazione di mutazioni statiche e temporali;
- duplicazione di F-TEID;
- modifica di valori RES* e `authResult`.

Uno scenario di mutation testing viene indicato come:

```text
Result: OK
```

quando il verdetto osservato coincide con quello atteso.

Questo significa che anche una transizione:

```text
FAIL -> PASS
```

può essere corretta, come nel caso NRF.

---

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

---

## Struttura della repository

```text
captures/           Catture PCAP originali e mutate
config/             Configurazione dei test e delle mutazioni
dsl/                DSL, grammatica Lark e parser
traffic/            Lettura TShark e normalizzazione protocollare
traffic/resolvers/  Resolver semantici
matcher/            AST, Thompson compiler, NFA e sequence matcher
pipeline/           Pipeline generica di verifica
verifier/           Binding verifier, verifier legacy e temporal verifier
mfotl/              Signature, formule e log MonPoly
reporter/           Reporter generico e reporter legacy ancora necessari
mutation_testing/   Mutatori offline delle catture
utils/              Funzioni condivise
scasdk/             Componenti ScasDK originali e adattati
main.py             Runner principale
```

`scasdk/original/` contiene il sottoinsieme di ScasDK utilizzato come riferimento durante lo sviluppo, mentre `scasdk/adapted/` contiene la versione adattata impiegata dal progetto.

I file `subscriber.json` inclusi nella repository contengono esclusivamente parametri dell’ambiente sperimentale e vengono mantenuti per garantire la riproducibilità dei casi di test.

---

## Stato dello sviluppo

La nuova architettura generica è attualmente utilizzata per:

```text
NRF Discovery Authorization
AMF Synchronization Failure — Case A
AMF Synchronization Failure — Case B
```

Questi test utilizzano:

```text
generic traffic extraction
→ semantic normalization
→ DSL sequence
→ AST
→ Thompson NFA
→ sequence matcher
→ static binding verification
→ MFOTL / MonPoly
→ generic report
```

Le restanti famiglie di test verranno migrate progressivamente eliminando gli extractor e i reporter specifici dove non più necessari.

Tra i principali sviluppi ancora previsti:

- migrazione di UPF, UDM e RES*;
- miglioramento della correlazione cross-protocol;
- estensione del matcher oltre le sequenze lineari;
- supporto a pattern opzionali, alternativi o ripetuti;
- ulteriore consolidamento della DSL;
- progressiva eliminazione della compatibilità legacy.
