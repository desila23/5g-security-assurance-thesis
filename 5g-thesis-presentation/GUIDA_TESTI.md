# Guida ai testi — versione 9, 21 slide

HTML in `slides/`, stili in `css/`, logica e frasi dei passi in `js/`.

## 1 — Titolo della tesi

File: `slides/01-titolo.html`

- Corso di laurea in Informatica
- A Domain-Specific Language
- for Security Assurance
- of 5G SCAS Tests
- from Network Traffic Captures
- Laureando
- Samuele De Santis
- Relatrice: Prof.ssa Paola Vocca
- Correlatore: Dott. Francesco Mancini
- Anno accademico 2025/2026
- PCAP
- cattura di rete
- DSL
- regole del test
- VERDETTO
- PASS · FAIL · INCONCLUSIVE
- REPORT
- criteri ed evidenze

## 2 — 5G Core: Network Functions e interazioni

File: `slides/02-rete-5g.html`

- INTRODUZIONE
- 5G Core: Network Functions e interazioni
- Le NF cooperano tramite protocolli e procedure standardizzati.
- 5G RAN
- 5G CORE
- CONTROL PLANE
- USER PLANE
- AMF
- SMF
- AUSF
- UDM
- UPF
- SBI
- N4
- UE
- gNB
- N2
- N3
- N6
- Internet
- Funzioni e interazioni devono rispettare requisiti di sicurezza

## 3 — Le SCAS descrivono come verificare la sicurezza

File: `slides/03-scas.html`

- INTRODUZIONE
- Le SCAS descrivono come verificare la sicurezza
- Il test produce messaggi e un esito: quali evidenze giustificano il verdetto?
- Specifica SCAS
- Test
- File PCAP
- Verdetto
- Precondizioni
- Stato iniziale
- Azioni
- Operazioni previste
- Risultato atteso
- Comportamento richiesto
- Procedura
- eseguita sulla rete
- Messaggi della prova
- Molti messaggi osservati
- Quali evidenze
- giustificano
- questo esito?
- Per automatizzare la verifica, i criteri SCAS vanno formalizzati in codice.

## 4 — Da verificatori dedicati a un motore comune

File: `slides/04-motore-comune.html`

- INTRODUZIONE
- Da verificatori dedicati a un motore comune
- Cambiano le regole dei test, non il motore che le interpreta.
- Separare le regole dalla logica del verificatore
- Ogni test richiede una logica dedicata
- TEST A
- VERIFICATORE A
- Verdetto A
- TEST B
- VERIFICATORE B
- Verdetto B
- TEST C
- VERIFICATORE C
- Verdetto C
- REGOLA A
- REGOLA B
- REGOLA C
- Unico motore
- Selezione + verifica
- Verdetto + report
- TEST A
- VERIFICATORE A
- Verdetto A
- TEST B
- VERIFICATORE B
- Verdetto B
- TEST C
- VERIFICATORE C
- Verdetto C
- Selezione + verifica

## 5 — Una DSL per i test SCAS

File: `slides/05-dsl.html`

- INTRODUZIONE
- Una DSL per i test SCAS
- OpenAPI è un esempio esterno: mostra il valore di una specifica formale.
- ESEMPIO ESTERNO · ALTRO DOMINIO
- OpenAPI
- Descrive interfacce HTTP in YAML
- Non è la DSL della tesi.
- IDEA COMUNE
- descrizione formale
- Scopi diversi
- IL CONTRIBUTO DELLA TESI
- DSL per verificare i test SCAS
- Formalizza evidenze e criteri da controllare.
- 1 · SELEZIONE DELLE EVIDENZE
- Quali messaggi cercare, in che ordine o gruppo
- A → B → C
- 2 · VERIFICA DEI CRITERI
- Valori, unicità, condizioni e vincoli temporali
- REQUIRE
- MFOTL / MonPoly
- I criteri SCAS sono formalizzati dal progettista; il motore li verifica sulle evidenze.

YAML nel pannello sinistro, non nel linguaggio della tesi: `esempi/openapi-esempio.yaml`.

## 6 — Architettura proposta

File: `slides/06-architettura.html`

- ARCHITETTURA
- Architettura proposta
- PCAP
- PIPELINE DI VERIFICA
- 1  Estrazione · TShark
- 2  Normalizzazione per protocollo
- 3  Resolver semantico, se serve
- 4  Selezione delle evidenze
- 5  Verifica statica / temporale
- 6  Generazione del report
- DSL
- REPORT + VERDETTO
- Record JSON EK
- MessageEvent
- Eventi risolti, se serve
- Match / collezioni
- Esiti dei criteri
- Report

## 7 — Dal traffico alle evidenze del test

File: `slides/07-normalizzazione.html`

- ARCHITETTURA
- Dal traffico alle evidenze del test
- Da TShark ai MessageEvent, fino alle evidenze pertinenti al test.
- ELABORAZIONE PER PROTOCOLLO
- PCAP
- Molti pacchetti
- TShark
- Estrazione filtrata
- Normalizzatori
- NAS
- HTTP/2
- PFCP
- Resolver, se serve
- MessageEvent
- Formato comune
- Selezione DSL
- EVIDENZE
- SELEZIONATE
- MessageEvent · struttura comune
- Oggetto Python
- frame_number, timestamp
- protocol, kind
- src, dst
- message_type
- related_frames, correlation
- fields: { … }
- Ogni normalizzatore produce lo stesso formato di evento.

## 8 — Dalle evidenze al verdetto e al report

File: `slides/08-report.html`

- Dalle evidenze al verdetto e al report
- Evidenze selezionate
- Verifica
- Statica · Temporale
- Verdetto
- PASS · FAIL · INCONCLUSIVE
- Report
- Estratto del report UPF
- {
-   "metadata": {
-     "tshark_version":
-       "TShark (Wireshark) 3.6.2 (Git v3.6.2 packaged as 3.6.2-2)"
-   },
-   "source": {
-     "pcap": "captures/upf_teid_uniqueness_open5gs.pcapng",
-     "sha256":
-    "e025648617e4911b36253580a6fd924fbdbc86352974b6ead6b428df56d8f20a"
-   },
-   "verification": {
-     "results": [{
-       "verdict": "PASS",
-       "evidence_frames": [37, 38, 46, 47, 48],
-       "details": { "field": "responses.f_teids",
-         "operator": "UNIQUE", "duplicates": [] }
-     }],
-     "overall_verdict": "PASS"
-   }
- }
- Il report collega il verdetto ai criteri, ai valori e ai frame osservati.
- ARCHITETTURA

## 9 — La DSL: selezionare gli eventi e verificarli

File: `slides/09-sintassi-dsl.html`

- DSL · NFA · VERIFICA
- La DSL: selezionare gli eventi e verificarli
- Un test NRF: selezioniamo richiesta e risposta, poi verifichiamo HTTP 403.
- SELEZIONE
- SEQUENCE {
-     nrf.discovery.request AS request
-     nrf.discovery.response AS response
- }
- VERIFICA
- REQUIRE response.status == 403
- Selettori disponibili
- SEQUENCE
- Messaggi in ordine
- OPTIONAL
- Gruppo facoltativo
- COLLECT
- Eventi dello stesso tipo
- Criteri disponibili
- REQUIRE
- Vincoli sui valori
- REQUIRE UNIQUE
- Valori distinti
- IF
- Condizioni sul caso
- MFOTL
- Proprietà temporali

## 10 — Dalla regola all’automa

File: `slides/10-nfa.html`

- Dalla regola all’automa
- REGOLA
- FRAMMENTI ELEMENTARI
- AUTOMA COMPLETO
- SEQUENCE {
- event.a AS a
-   OPTIONAL {
- event.b AS b
-   }
- event.c AS c
- }
- Atom(event.a)
- q0
- q1
- a
- Atom(event.b)
- q2
- q3
- b
- Atom(event.c)
- q4
- q5
- c
- q0
- q1
- q2
- q3
- q4
- q5
- inizio
- a
- b
- c
- ε
- ε
- ε
- Percorsi accettati
- A
- B
- C
- A
- C
- Da SEQUENCE a NFA: atomi, transizioni ε e percorso opzionale.
- DSL · NFA · VERIFICA

## 11 — Riconoscimento della sequenza

File: `slides/11-matcher.html`

- Riconoscimento della sequenza
- SEQUENCE
- Eventi osservati
- Binding
- Automa
- SEQUENCE {
- event.a AS a
-   OPTIONAL {
- event.b AS b
-   }
- event.c AS c
- }
- Politica di riavvio
- Un nuovo inizio avvia un candidato.
- Il precedente si interrompe solo se
- non può consumare quell’evento.
- 1
- A
- a(1)
- event.a
- 2
- X
- 3
- A
- a(3)
- event.a
- 4
- B
- b(4)
- event.b
- 5
- X
- 6
- C
- c(6)
- event.c
- q0
- q1
- a
- inizio
- q2
- q3
- b
- q4
- q5
- c
- ε
- ε
- ε
- Il matcher riconosce A(3), B(4) e C(6), ignorando gli eventi estranei.
- Esempio del caso in cui il nuovo A non è consumabile dal candidato precedente.
- DSL · NFA · VERIFICA

## 12 — Dal Match al BindingContext

File: `slides/12-binding.html`

- DSL · NFA · VERIFICA
- Dal Match al BindingContext
- Gli alias del Match diventano riferimenti ai MessageEvent nel BindingContext.
- Matcher
- NFA + eventi
- Match
- Sequenza riconosciuta
- A(3)
- B(4)
- C(6)
- bindings
- tipo di evento
- a
- →
- A(3)
- event.a
- b
- →
- B(4)
- event.b
- c
- →
- C(6)
- event.c
- BindingContext
- bindings
- a → A(3)
- b → B(4)
- c → C(6)
- Stessi eventi, accessibili per alias
- Il matcher produce il Match; il BindingContext ne conserva i binding.
- BindingContext.bindings
- alias a → A(3)
- MessageEvent
- message_type: event.a
- frame_number, timestamp
- protocol, kind
- fields: { … }
- alias b → B(4)
- MessageEvent
- message_type: event.b
- frame_number, timestamp
- protocol, kind
- fields: { … }
- alias c → C(6)
- MessageEvent
- message_type: event.c
- frame_number, timestamp
- protocol, kind
- fields: { … }
- 3, 4, 6 sono posizioni dell’esempio. Ogni alias conserva il riferimento al suo evento.

## 13 — Motore di verifica

File: `slides/13-verifica.html`

- Motore di verifica
- Verifica statica e temporale, un unico esito motivato dalle evidenze.
- Esempio illustrativo: esito PASS
- BindingContext
- Verifica statica
- Confronti e unicità
- Condizioni IF
- Verifica temporale
- Formule MFOTL
- Valutazione con MonPoly
- FAIL
- Un criterio violato
- PASS
- Criteri soddisfatti
- INCONCLUSIVE
- Evidenza insufficiente
- Report · criteri, valori, frame e verdetto
- DSL · NFA · VERIFICA

## 14 — Testing e Mutation testing

File: `slides/14-testing.html`

- VALUTAZIONE SPERIMENTALE
- Testing e
- Mutation testing

## 15 — AMF Synchronization Failure, Case B

File: `slides/15-amf-sync.html`

- AMF Synchronization Failure, Case B
- Estratto DSL · parti omesse
- SEQUENCE {
-   …
-   nas.authentication_failure
-     AS sync_failure
-   …
- }
- REQUIRE sync_failure.cause == 21
- …
- MFOTL CASE B """
-   SyncFailure() IMPLIES
-   NOT EVENTUALLY[0,{TIMER_MS}]
-     AuthenticationRequest()
- """
- Verdetto complessivo
- 4 controlli statici: PASS
- 1 controllo temporale: PASS
- PASS
- T3520 = 15 s
- Nessuna nuova Authentication Request nei primi 15 s.
- Finestra senza nuove richieste
- 0 s
- 15 s
- 25,018 s
- Frame 358
- Sync Failure
- Frame 606
- Authentication Request
- Intervallo osservato: 25,018 s (>15 s)
- AMF: quattro controlli statici e il vincolo T3520 soddisfatti.
- TEST E BASELINE

## 16 — UPF TEID Uniqueness

File: `slides/16-upf.html`

- UPF TEID Uniqueness
- COLLECT pfcp.session_establishment_response AS responses
- REQUIRE UNIQUE responses.f_teids
- Evidenze osservate
- Frame
- F-TEID 1
- F-TEID 2
- 37
- 0x00006a75
- 0x0000ecf4
- 38
- 0x0000a5de
- 0x00000f66
- 46
- 0x0000b101
- 0x0000a697
- 47
- 0x0000a7dc
- 0x0000113a
- 48
- 0x00001ee9
- 0x0000e1cf
- IPv4 comune: 127.0.0.7
- Verdetto complessivo
- Nessun duplicato
- 10 coppie distinte
- in 5 risposte
- PASS
- Cinque risposte PFCP, dieci coppie F-TEID, nessun duplicato.
- TEST E BASELINE

## 17 — AMF RES*: quattro casi, una regola DSL

File: `slides/17-resstar.html`

- TEST E BASELINE
- AMF RES*: quattro casi, una regola DSL
- Una sola regola descrive quattro combinazioni di identità e origine del fallimento.
- Estratto DSL · parti omesse
- SEQUENCE {
-   nas.registration_request
-     AS registration_request
-   OPTIONAL { ... }
-   ausf.authentication.response
-     AS authentication_vector
-   ...
-   OPTIONAL { ... }
-   nas.authentication_reject
-     AS authentication_reject
- }
- REQUIRE
-   authentication_reject.present == true
- IF case.identity_path
-    == guti_then_suci { ... }
- IF case.failure_source
-    == ausf { ... }
- ORIGINE DEL FALLIMENTO
- AMF locale
- AUSF
- Case A
- PASS
- Nessun gruppo opzionale
- 7 PASS
- · 2 SKIPPED
- 1 match completo
- Case C
- PASS
- Confirmation presente
- 9 PASS
- · 2 SKIPPED
- 1 match completo
- Case B
- PASS
- Identity presente
- 9 PASS
- · 2 SKIPPED
- 1 match completo
- Case D
- PASS
- Identity + Confirmation
- 11 PASS
- · 2 SKIPPED
- 1 match completo
- IF: criteri scelti dalla configurazione del caso
- PERCORSO DI IDENTIFICAZIONE
- SUCI
- diretto
- GUTI
- SUCI

## 18 — Risultati dei test baseline

File: `slides/18-baseline.html`

- Risultati dei test baseline
- Dieci verdetti coerenti con gli attesi, incluso un FAIL previsto.
- Caso di test
- Atteso
- Osservato
- NRF Discovery Authorization
- FAIL
- FAIL
- UDM Resynchronization
- PASS
- PASS
- UDM SUCI De-concealment
- PASS
- PASS
- AMF Sync Failure — Case A
- PASS
- PASS
- AMF Sync Failure — Case B
- PASS
- PASS
- UPF TEID Uniqueness
- PASS
- PASS
- RES* Verification Failure — A
- PASS
- PASS
- RES* Verification Failure — B
- PASS
- PASS
- RES* Verification Failure — C
- PASS
- PASS
- RES* Verification Failure — D
- PASS
- PASS
- 10 / 10
- corrispondenze
- 9 PASS1 FAIL atteso
- TEST E BASELINE

## 19 — Mutation testing: il processo

File: `slides/19-mutazioni.html`

- MUTATION TESTING
- Mutation testing: il processo
- Si modifica la PCAP, non il verificatore: la pipeline rimane la stessa.
- PCAP ORIGINALE
- PIPELINE DI VERIFICA
- 1  Estrazione · TShark
- 2  Normalizzazione per protocollo
- 3  Resolver semantico, se serve
- 4  Selezione delle evidenze
- 5  Verifica statica / temporale
- 6  Generazione del report
- DSL
- Report baseline
- Report mutation
- MOTORE
- di mutazione
- PCAP MUTATA

## 20 — Risultati del mutation testing

File: `slides/20-risultati-mutazioni.html`

- MUTATION TESTING
- Risultati del mutation testing
- 15 mutazioni su 15: il verdetto osservato coincide con quello atteso.
- Famiglia
- Esperimenti
- Transizione attesa
- NRF
- 1
- FAIL → PASS
- UDM
- 2
- PASS → FAIL
- AMF
- 6
- PASS → FAIL
- UPF
- 2
- PASS → FAIL / INCONCLUSIVE
- AMF RES*
- 4
- PASS → FAIL
- 15 / 15
- corrispondenze
- Due esempi utili
- AMF
- UPF
- Mutazione
- Statica
- Temporale
- Complessivo
- Statica
- FAIL
- PASS
- FAIL
- Temporale
- PASS
- FAIL
- FAIL
- Combinata
- FAIL
- FAIL
- FAIL
- Mutazione
- Baseline
- Esito
- Coppia F-TEID
- duplicata
- PASS
- FAIL
- Risposte PFCP
- rimosse
- PASS
- INCONCLUSIVE

## 21 — Non basta un verdetto

File: `slides/21-conclusioni.html`

- Non basta un verdetto.
- Serve poterlo giustificare
- con le evidenze.
- Grazie per l’attenzione
- Domande?
- Samuele De Santis

