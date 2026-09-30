# 5G Security Assurance

Framework sperimentale per verificare criteri di sicurezza 5G SCAS a partire da catture di traffico di rete.

Il progetto prende in ingresso una cattura PCAP, estrae l’evidenza rilevante tramite TShark, applica verifiche statiche e temporali e produce un report strutturato che collega ogni verdetto ai frame e ai valori osservati.

È inoltre supportato il **mutation testing**: una copia del PCAP originale viene modificata offline e analizzata nuovamente tramite la stessa pipeline, così da verificare che il criterio bersaglio reagisca alla modifica prevista.

> I pacchetti mutati **non vengono reinviati alle Network Function 5G**. Il mutation testing valida la pipeline di verifica, non il comportamento runtime dell’implementazione 5G.

---

## Pipeline attuale

```text
PCAP
  ↓
TShark / extractor specifico del test
  ↓
evidence.json
  ↓
verifier statico
  ↓
verification.json
  ↓
verifier temporale (quando richiesto)
  ↓
temporal_verification.json
  ↓
reporter
  ↓
report.json
```

Questa repository rappresenta la baseline funzionante sviluppata prima del refactoring attualmente in corso verso un’architettura generica e guidata dalla DSL.

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

`MonPoly` è richiesto soltanto per le verifiche temporali dei test AMF Synchronization Failure.

---

## Esecuzione dei test

Tutti i comandi devono essere eseguiti dalla root del progetto.

Elenco dei test disponibili:

```bash
python main.py --list
```

Esecuzione di un singolo test originale:

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


### Varianti AMF

I test AMF Synchronization Failure supportano le varianti:

```bash
python main.py --test amf_sync_failure_case_a

python main.py --mutation amf_sync_failure_case_a --variant static
python main.py --mutation amf_sync_failure_case_a --variant temporal
python main.py --mutation amf_sync_failure_case_a --variant both
```

`Static` se si vuole testare la mutazione sulle regole statiche.
`Temporal` se si vuole testare la mutazione sulle regole temporali.
`Both` per entrambe.

Gli stessi comandi valgono per `amf_sync_failure_case_b`.

### Casi RES*

Il test RES* Verification Failure richiede l’identificatore del caso:

```bash
python main.py --test resstar_verification_failure --case A
python main.py --mutation resstar_verification_failure --case A
```

Sostituire `A` con `B`, `C` o `D`.

---

## Famiglie di test implementate

| Famiglia di test | Proprietà principale | Verdetto originale |
| --- | --- | --- |
| NRF Discovery Authorization | Lo status HTTP della risposta deve essere `403` | FAIL |
| UDM AKA Resynchronization | Coerenza del RAND, differenze tra vettori e verifica MAC | PASS |
| UDM SUCI De-concealment | Il SUPI restituito deve coincidere con quello atteso | PASS |
| AMF Synchronization Failure — Caso A | Verifiche statiche + risposta AUSF entro `T3520` | PASS |
| AMF Synchronization Failure — Caso B | Verifiche statiche + assenza di una nuova Authentication Request entro `T3520` | PASS |
| UPF TEID Uniqueness | Unicità della coppia F-TEID `{teid, ipv4}` tra risposte PFCP | PASS |
| RES* Verification Failure — Casi A–D | Verifiche sui vettori di autenticazione e sul percorso di fallimento RES* | PASS |

Il baseline NRF produce intenzionalmente `FAIL`: nella cattura la risposta ha status HTTP `200`, mentre la DSL richiede `403`.

---

## Mutation testing

Le mutazioni sono definite in:

```text
config/mutation_tests.json
```

Il flusso di mutation testing è:

```text
PCAP originale
    ↓
esecuzione della verifica originale
    ↓
selezione del target a partire dall’evidenza estratta
    ↓
generazione del PCAP mutato
    ↓
riesecuzione della stessa pipeline
    ↓
confronto tra verdetto osservato e verdetto atteso
```

Esempi di mutazione:

- modifica dello status NRF da `200` a `403`;
- modifica del RAND nella risincronizzazione UDM;
- modifica del SUPI restituito;
- mutazioni statiche, temporali o combinate sui casi AMF;
- duplicazione di un F-TEID nel test UPF;
- modifica di valori RES* / `authResult` nei casi di autenticazione.


---

## Output

Ogni test genera i propri artefatti sotto `reports/`.

I file principali sono:

```text
evidence.json
verification.json
temporal_verification.json   # solo AMF
report.json
```

Il report finale contiene:

- metadati del test;
- PCAP sorgente e SHA-256;
- criteri verificati;
- valori osservati e attesi;
- frame di evidenza;
- risultati delle verifiche statiche e temporali;
- verdetto finale.

I report generati sono esclusi da Git perché possono essere riprodotti eseguendo nuovamente i test.

---

## Struttura della repository

```text
captures/           Catture PCAP originali e mutate
config/             Configurazione di test e mutazioni
dsl/                Regole DSL, grammatica e parser Lark
extractor/          Extractor TShark specifici dei test nella baseline attuale
verifier/           Verifiche statiche, MAC e temporali
mfotl/              Firma MonPoly e artefatti temporali
reporter/           Costruzione dei report
mutation_testing/   Mutatori offline delle catture
utils/              Funzioni condivise
scasdk/             Componenti ScasDK originali e adattati
main.py             Runner principale per test e mutazioni
```

`scasdk/original/` contiene il sottoinsieme di ScasDK utilizzato come riferimento durante lo sviluppo, mentre `scasdk/adapted/` contiene la versione adattata impiegata dal progetto.

I file `subscriber.json` inclusi nella repository contengono **esclusivamente parametri dell’ambiente sperimentale** e vengono mantenuti per garantire la riproducibilità dei casi di test.

---

## Riproduzione della validazione attuale

Dopo aver installato le dipendenze e gli strumenti esterni:

```bash
source ~/.venvs/5g-security-assurance/bin/activate
python main.py --all
```

Uno scenario viene indicato come `OK` quando il verdetto osservato coincide con quello configurato come atteso.

Di conseguenza, anche un verdetto SCAS `FAIL` può produrre:

```text
OK
```

se il `FAIL` è proprio il risultato atteso per quello scenario sperimentale (è il caso del test `NRF DISCOVERY`).

---

## Stato dello sviluppo

La repository rappresenta attualmente la baseline stabile del prototipo sviluppato per la tesi.

Il passo architetturale successivo consiste nel sostituire gli extractor specifici dei singoli test con una pipeline generica di elaborazione del traffico, nella quale le sequenze di messaggi vengano descritte direttamente nella DSL e riconosciute su eventi normalizzati prima dell’applicazione delle verifiche statiche e temporali.
