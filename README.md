# 5G Security Assurance

Proof of concept per verificare criteri di sicurezza 5G su catture PCAP già disponibili. Il progetto collega un criterio SCAS ai valori estratti, ai frame della cattura e al verdetto finale.

Il *mutation testing* modifica offline una copia del PCAP originale e riesegue la stessa pipeline. Serve a controllare che il criterio rilevi la modifica prevista. Non invia i pacchetti mutati alle Network Function e non misura una loro nuova risposta.

## Avvio rapido

Richiede Python 3.10, TShark/Wireshark e MonPoly per i test temporali AMF. Le dipendenze Python sono in `requirements.txt`, inclusi Scapy, Lark e la versione adattata di ScasDK.

```bash
python3 -m venv ~/.venvs/5g-security-assurance
source ~/.venvs/5g-security-assurance/bin/activate
pip install -r requirements.txt
```

TShark e MonPoly vanno installati separatamente. Per verificare che siano disponibili:

```bash
tshark --version
monpoly -version
```

Dalla radice del progetto:

```bash
python main.py --list
python main.py --test nrf_disc_auth_slice
python main.py --mutation nrf_disc_auth_slice
python main.py --all
```

`--test` analizza una cattura originale. `--mutation` analizza la cattura originale, genera un PCAP mutato e verifica anche quest'ultimo. I casi RES* richiedono `--case A|B|C|D`; le mutazioni AMF richiedono `--variant static|temporal|both`. `--list` mostra i comandi disponibili.

`--all` esegue 10 test originali e 14 scenari di mutazione. Per ciascuno mostra il verdetto osservato, quello atteso e `OK` se coincidono. Un verdetto `FAIL` può quindi avere esito `OK` quando è quello atteso. Ogni test originale viene eseguito una sola volta; le mutazioni riusano l'evidenza appena prodotta. Il comando termina con errore se almeno uno scenario non dà il risultato previsto.

Il runner mostra normalmente un riepilogo con i verdetti DSL, temporale (quando presente) e del report. Per vedere anche l'output dettagliato dei singoli componenti, aggiungi `--verbose`, per esempio:

```bash
python main.py --mutation amf_sync_failure_case_a --variant both --verbose
```

Quando il report dà **FAIL**, il riepilogo indica i criteri falliti e i frame coinvolti. Per le regole DSL mostra valore osservato e atteso; per l'unicità F-TEID mostra il duplicato; per le regole temporali mostra il timer e l'intervallo osservato.

Se un componente termina con errore, il suo output viene mostrato anche senza `--verbose`.

## Come funziona

La pipeline è definita in `config/tests.json`:

```text
PCAP → TShark/extractor → evidence.json → verifier → verification.json
                                                    ↓
                                                reporter → report.json
```

Nel test UDM resynchronization l'extractor calcola anche la verifica dei MAC dei vettori; le relative regole sono controllate dal verifier DSL. Nei casi AMF, il verifier temporale ricava la formula MFOTL dal file DSL e produce `temporal_verification.json` tramite MonPoly. Il reporter combina il risultato statico e quello temporale.

Il runner esegue il reporter indicato nella configurazione del test. Le funzioni condivise caricano l'evidenza e i risultati delle verifiche; il reporter costruisce il contenuto specifico del test e salva `report.json`.

Le mutazioni sono definite in `config/mutation_tests.json`. Il runner:

1. Esegue il test originale e controlla il verdetto atteso.
2. Usa l'evidenza appena estratta per scegliere i valori da modificare. I mutatori verificano che l'hash SHA-256 dell'evidenza corrisponda al PCAP sorgente.
3. Salva una nuova cattura, esegue di nuovo la pipeline e controlla il verdetto del report.
4. Controlla la regola bersaglio nel `verification.json`. Per AMF controlla anche separatamente il verdetto statico e quello temporale.
5. Controlla che l'hash del PCAP mutato sia diverso da quello originale.

Le catture originali rimangono sorgenti separate dagli output mutati. A parità di cattura ed evidenza, le mutazioni di questo progetto scelgono gli stessi valori: il comando rigenera il PCAP, ma non seleziona ogni volta una mutazione casuale.

## Test e mutazioni

Le sezioni seguono l'ordine dei test originali. Ogni mutazione è descritta accanto al test a cui appartiene.

### 1. NRF Discovery Authorization

La regola `dsl/nrf_rule.dsl` richiede che la risposta alla richiesta di NF Discovery abbia status HTTP `403`. L'evidenza include requester, target, S-NSSAI e risposta HTTP/2. Nella cattura originale la risposta ha status `200`, quindi il verdetto è **FAIL**.

```bash
python main.py --test nrf_disc_auth_slice
python main.py --mutation nrf_disc_auth_slice
```

Il mutatore cambia offline lo status `200` in `403` nell'header HTTP/2. La codifica HPACK cresce di quattro byte: il mutatore aggiorna la lunghezza HTTP/2 e IP, i numeri di sequenza/acknowledgment TCP successivi e i checksum. La regola passa da **FAIL a PASS**.

Il body della risposta originale resta nella cattura modificata. Questo PASS mostra che il verifier riconosce lo status `403`; non significa che il NRF reale abbia negato la richiesta o prodotto una risposta semanticamente coerente con `403`.

### 2. UDM AKA Resynchronization

Il test correla il vettore iniziale con la richiesta di risincronizzazione e il nuovo vettore. Verifica status HTTP, RAND, differenze tra i vettori e MAC. La cattura originale dà **PASS**.

```bash
python main.py --test udm_resynchronization
python main.py --mutation udm_resynchronization
```

Il mutatore cambia una cifra esadecimale del RAND nella richiesta di risincronizzazione, dentro il body HTTP/2. Il RAND non coincide più con quello del vettore iniziale. La relativa regola passa da **PASS a FAIL** e il report finale diventa **FAIL**. Il MAC dei vettori resta valido: i vettori non sono stati modificati.

### 3. UDM SUCI De-concealment

La DSL richiede status HTTP `200` e uguaglianza tra il SUPI restituito dalla UDM e quello atteso dal file del subscriber. La cattura originale dà **PASS**.

```bash
python main.py --test udm_suci_deconcealment
python main.py --mutation udm_suci_deconcealment
```

Il mutatore sostituisce nel body HTTP/2 il SUPI della risposta con un altro valore della stessa lunghezza. La regola sullo status resta **PASS**; la regola sull'uguaglianza dei SUPI passa a **FAIL**. Il report finale dà **FAIL**.

### 4. AMF Synchronization Failure, caso A

La verifica statica controlla la causa NAS `21`, la presenza di AUTS e la coerenza di AUTS e RAND tra Authentication Failure, richiesta di risincronizzazione e vettore iniziale. La verifica temporale richiede una risposta AUSF entro la finestra configurata di `T3520 = 15000 ms` dopo la richiesta di risincronizzazione. La cattura originale dà **PASS**.

```bash
python main.py --test amf_sync_failure_case_a
python main.py --mutation amf_sync_failure_case_a --variant static
python main.py --mutation amf_sync_failure_case_a --variant temporal
python main.py --mutation amf_sync_failure_case_a --variant both
```

`static` modifica il RAND della richiesta di risincronizzazione nel body HTTP/2. `temporal` sposta i timestamp dopo la richiesta: l'intervallo fino alla risposta AUSF passa da circa 0,025 a 20 secondi. `both` applica le due modifiche allo stesso PCAP.

### 5. AMF Synchronization Failure, caso B

Le regole statiche sono le stesse del caso A. La formula temporale richiede che non compaia una nuova Authentication Request entro i 15 secondi dopo il Synchronization Failure. Nella cattura originale la richiesta successiva arriva dopo circa 25 secondi: il verdetto è **PASS**.

```bash
python main.py --test amf_sync_failure_case_b
python main.py --mutation amf_sync_failure_case_b --variant static
python main.py --mutation amf_sync_failure_case_b --variant temporal
python main.py --mutation amf_sync_failure_case_b --variant both
```

`static` modifica il RAND nella richiesta di risincronizzazione. `temporal` comprime l'intervallo tra Synchronization Failure e Authentication Request a 10 secondi. `both` applica le due modifiche allo stesso PCAP.

Per entrambi i casi AMF i risultati attesi sono:

| Variante | Verifica statica | Verifica temporale | Report |
| --- | --- | --- | --- |
| Originale | PASS | PASS | PASS |
| `static` | FAIL | PASS | FAIL |
| `temporal` | PASS | FAIL | FAIL |
| `both` | FAIL | FAIL | FAIL |

Le mutazioni temporali cambiano i timestamp, conservando l'ordine e i byte dei pacchetti. Le mutazioni statiche cambiano un valore nel payload; Scapy aggiorna il checksum TCP. Le formule MFOTL dei casi A e B sono in `dsl/amf_sync_failure.dsl`; il valore del timer è nella configurazione del test. Il verifier genera le formule con il timer risolto in `mfotl/generated/` e le controlla con MonPoly usando `mfotl/amf_sync_failure.sig`.

### 6. UPF TEID Uniqueness

La DSL richiede che la coppia `{teid, ipv4}` degli F-TEID nelle PFCP Session Establishment Response sia unica tra risposte diverse. La cattura originale non ha duplicati e dà **PASS**.

```bash
python main.py --test upf_teid_uniqueness
python main.py --mutation upf_teid_uniqueness
```

Il mutatore sceglie dall'evidenza due risposte compatibili e copia un F-TEID della prima nella seconda. TShark individua il campo `pfcp.f_teid.teid` nel frame; Scapy cambia i byte e aggiorna il checksum UDP. Il verifier segnala i frame del duplicato e il risultato passa da **PASS a FAIL**. Il frame e i valori sono scelti dall'evidenza, senza fissare il TEID nel runner.

### 7. RES* Verification Failure, casi A–D

I quattro casi usano catture diverse. La DSL controlla i vettori di autenticazione, il percorso d'identità e l'esito del controllo RES*. Tutte le catture originali danno **PASS**.

```bash
python main.py --test resstar_verification_failure --case A
python main.py --mutation resstar_verification_failure --case A
```

Sostituisci `A` con `B`, `C` o `D` per gli altri casi.

| Casi | Mutazione | Regola che passa a FAIL |
| --- | --- | --- |
| A, B | Copia `HRES*` nel campo `HXRES*` del vettore | La verifica locale richiede `HRES* != HXRES*` |
| C, D | Cambia `authResult` da `AUTHENTICATION_FAILURE` a `AUTHENTICATION_SUCCESS` | La risposta AUSF deve indicare `AUTHENTICATION_FAILURE` |

Il mutatore usa i frame e i valori nell'evidenza. La sostituzione nel JSON del payload TCP conserva la lunghezza e Scapy aggiorna i checksum. Ogni caso dà **PASS → FAIL**.

## File e risultati

```text
main.py                      Runner dei test originali e delle mutazioni
config/tests.json            PCAP e pipeline dei test originali
config/mutation_tests.json   Mutatori, test mutati e verdetti attesi
captures/                    Catture originali e catture mutate
extractor/                   Estrazione degli eventi con TShark
dsl/                         Regole e parser Lark
verifier/                    Verifica DSL, MAC e proprietà temporali
mfotl/                       Formule, firme e log per MonPoly
reporter/                    Report che collega criteri ed evidenze
mutation_testing/            Mutatori delle catture
utils/                       Funzioni condivise
reports/                     Evidenze e risultati di ciascun test
scasdk/adapted/              Codice ScasDK adattato
```

Ogni test produce nella propria cartella `reports/`:

- `evidence.json`: sorgente e SHA-256 del PCAP, eventi, valori e frame estratti;
- `verification.json`: esito delle regole DSL;
- `temporal_verification.json`: esito MonPoly, per i casi AMF;
- `report.json`: criteri, riferimenti all'evidenza e verdetto complessivo.

Tutti i `report.json` usano lo schema `2.0`. Le sezioni comuni sono `metadata`, `test`, `source`, `configuration`, `criteria`, `verification`, `evidence`, `explanation` e `verdict`. Ogni risultato collega un criterio al verificatore, ai frame interessati e ai dettagli della verifica. I dettagli cambiano in base alla regola, mentre la struttura generale resta la stessa.
