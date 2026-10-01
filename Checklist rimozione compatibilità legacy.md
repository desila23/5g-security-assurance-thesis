# Checklist rimozione compatibilità legacy

## main.py

- [ ] Rimuovere `run_legacy_pipeline()`.
- [ ] Semplificare `run_pipeline()` eliminando il branch:
      `if pipeline == "sequence" ... else legacy`.
- [ ] Eliminare il valore di default `"legacy"` da:
      `test_config.get("pipeline", "legacy")`.
- [ ] Rimuovere la gestione di:
      - `extractor`
      - `pre_verifiers`
      - `verifier`
      - `reporter`
      dalla vecchia pipeline.
- [ ] Rimuovere la gestione del vecchio `temporal.verifier` se il temporal verifier sarà stato integrato nella nuova architettura.
- [ ] Semplificare `get_source_sha256()` affinché legga sempre:
      `report["source"]["sha256"]`.
- [ ] Semplificare `check_target_rule()` affinché legga sempre le regole dal report unificato.
- [ ] Rimuovere ogni accesso a:
      `config["evidence"]`
      e
      `config["output"]`.
- [ ] Rimuovere il branch del mutation command che passa `--evidence`.
- [ ] Fare in modo che tutti i mutator ricevano sempre `--report`.
- [ ] Controllare `run_all()` e rimuovere eventuali assunzioni sulla struttura legacy.

## utils/mutation_utils.py

- [ ] Rimuovere `load_mutation_context()`.
- [ ] Rinominare eventualmente `load_sequence_mutation_context()` in un nome più definitivo, ad esempio:
      `load_mutation_context()`.
- [ ] Eliminare ogni riferimento a `evidence.json`.
- [ ] Usare sempre il report unificato come fonte dell'evidenza per le mutazioni.

## config/tests.json

- [ ] Rimuovere dai test migrati:
      - `extractor`
      - `pre_verifiers`
      - `verifier`
      - `output`
      - eventuale `evidence`
      - `reporter`
- [ ] Uniformare tutti i test alla configurazione della nuova pipeline.
- [ ] Valutare se il campo `"pipeline": "sequence"` sia ancora necessario.
      Se esiste una sola pipeline, può essere eliminato.
- [ ] Uniformare:
      - `pcap`
      - `rules`
      - `traffic`
      - `report`
      - metadata del test.

## config/mutation_tests.json

- [ ] Eliminare configurazioni che dipendono da `evidence.json`.
- [ ] Uniformare tutte le `target_rule` ai nuovi field path del DSL.
- [ ] Fare in modo che i test mutati ereditino solo configurazioni compatibili con la nuova pipeline.
- [ ] Eliminare eventuali riferimenti ai vecchi file `verification.json`.

## extractor/

- [ ] Verificare quali extractor specifici non sono più utilizzati.
- [ ] Rimuovere gli extractor dei test migrati.
- [ ] Eliminare completamente `extractor/` se nessun test finale ne dipende.

## verifier/

- [ ] Rimuovere o archiviare `simple_verifier.py` quando tutte le regole statiche saranno gestite dal binding verifier.
- [ ] Migrare completamente:
      - `==`
      - `!=`
      - `UNIQUE`
      - `IF`
      nella nuova architettura.
- [ ] Rimuovere verifier specifici per singolo test.
- [ ] Integrare definitivamente il temporal verification nella nuova pipeline.
- [ ] Rimuovere i vecchi file di output separati `verification.json`.

## reporter/

- [ ] Rimuovere i reporter specifici per test.
- [ ] Mantenere un solo reporter generico.
- [ ] Verificare che il generic reporter supporti:
      - static rules
      - temporal rules
      - UNIQUE
      - cardinalità
      - PASS / FAIL / INCONCLUSIVE
      - bindings
      - evidence frames
      - SHA-256
- [ ] Valutare se rinominare `generic_reporter.py` semplicemente in `reporter.py`.

## traffic/

- [ ] Generalizzare i resolver necessari per tutti i test finali.
- [ ] Eliminare eventuali workaround temporanei specifici di NRF.
- [ ] Rivedere `_first()` nell'HTTP/2 normalizer.
- [ ] Gestire correttamente pacchetti contenenti più frame HTTP/2.
- [ ] Verificare la strategia di correlation per protocolli diversi da HTTP/2.

## matcher/

- [ ] Estendere Thompson oltre la sola sequenza lineare.
- [ ] Supportare epsilon transition.
- [ ] Supportare:
      - alternative `|`
      - optional `?`
      - repetition `*`
      - repetition `+`
- [ ] Implementare simulazione NFA completa.
- [ ] Gestire correttamente più candidate sequence.
- [ ] Integrare cardinalità:
      - exactly_one
      - any
      - all
- [ ] Rivedere la semantica del noise skipping.

## DSL

- [ ] Stabilizzare la sintassi definitiva di `SEQUENCE`.
- [ ] Aggiungere eventuali:
      - alternative
      - optional
      - repetition
      - cardinalità
- [ ] Uniformare static e temporal rules.
- [ ] Eliminare sintassi o costrutti mantenuti solo per retrocompatibilità.
- [ ] Aggiornare tutti i file DSL dei test mantenuti.

## temporal verification

- [ ] Migrare AMF alla nuova pipeline.
- [ ] Collegare i bindings del matcher agli eventi temporali.
- [ ] Decidere chiaramente quando usare:
      - confronto timestamp diretto
      - MFOTL / MonPoly
- [ ] Eliminare la dipendenza dal vecchio evidence format.
- [ ] Integrare i risultati temporali nel report unificato.

## mutation_testing/

- [ ] Migrare tutti i mutator mantenuti affinché leggano il report generico.
- [ ] Rimuovere dipendenze da `evidence.json`.
- [ ] Verificare che tutti i mutator controllino SHA-256 della sorgente.
- [ ] Validare baseline e mutation con la nuova pipeline.
- [ ] Eseguire `python main.py --all` dopo la rimozione definitiva della legacy.

## Cleanup finale

- [ ] Cercare nel repository:
      `COMPATIBILITÀ LEGACY`
      e rimuovere tutti i blocchi marcati.
- [ ] Cercare:
      `evidence`
      e verificare che non restino dipendenze dal vecchio evidence format.
- [ ] Cercare:
      `extractor`
      e verificare che non restino dipendenze dai vecchi extractor.
- [ ] Cercare:
      `verification.json`
      e verificare che non venga più prodotto/usato.
- [ ] Eseguire tutti i test finali.
- [ ] Eseguire tutte le mutation finali.
- [ ] Eseguire `python main.py --all`.
- [ ] Aggiornare README e architettura della tesi.