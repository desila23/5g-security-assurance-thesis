# PROMPT DA INVIARE A UNA NUOVA CHAT — Revisione e implementazione della presentazione di tesi 5G

Sto preparando la discussione di una **tesi triennale in Informatica**, da esporre in italiano davanti a una commissione universitaria, **in circa 20 minuti**. Voglio che tu lavori sulla **presentazione web HTML/SVG interattiva già esistente**, applicando con precisione le modifiche progettate in un file XML. Non voglio una presentazione nuova da zero: lo scopo è ottenere una versione finale più leggibile, coerente, accurata e professionale, **preservando le parti già riuscite**.

## 1. File che ti allego e gerarchia delle fonti

Ti fornisco **tre file fondamentali**:

1. **`5g-thesis-presentation.zip`**: sorgente originale COMPLETO, con **20 slide**, `index.html`, `style.css`, `script.js`, `interactive-slides.js`, asset/font e altri file. Questo è il progetto da modificare. Non usare come base una versione eventualmente diversa pubblicata su GitHub Pages.
2. **`Modifiche_presentazione_tesi_5G_v1_4.xml`**: specifica CUMULATIVA e dettagliata degli interventi approvati, sulla struttura, le slide, la navigazione, gli sfondi, i sottotitoli, i risultati e la conclusione. **Leggilo per intero**, comprese le sezioni finali: non limitarti ai primi nodi o all'ultima versione.
3. **`Testo incollato(20261015-134524).txt`**: **testo ORALE più aggiornato** della presentazione, dalla prima frase fino alla conclusione. Ti serve per assicurare che ciò che è proiettato abbia senso rispetto a ciò che dirò; NON trasformarlo in testo da incollare nelle slide.

Se disponibile, posso allegare anche **`Bozza_Tesi_DeSantis_Samuele (1).pdf`**, come riferimento tecnico facoltativo per verificare i dettagli. Il codice è pubblico: `https://github.com/desila23/5g-security-assurance-thesis`, branch **`refactor/generic-pipeline`**. Non usare altri branch per ricostruire le funzionalità implementate.

**Regole di precedenza in caso di conflitto:**
- Per le **modifiche al deck**, XML v1.4, integrato dalle precisazioni di questo prompt.
- Per **le frasi da pronunciare**, il TXT che allego ora è più aggiornato dell'eventuale testo orale riportato nel file XML.
- **Attenzione speciale alla conclusione**: ho VOLUTAMENTE conservato nel TXT la mia conclusione originale, quella che parla dei risultati, dei limiti del sistema, degli sviluppi futuri e dell'importanza di una verifica ricostruibile. **Non sostituirla** con il paragrafo orale alternativo proposto nell'XML. La **slide conclusiva** va invece progettata come indicato dall'XML, con una frase visiva sintetica e di impatto, SENZA copiare parola per parola il discorso orale.
- Dati sperimentali, comportamento dell'implementazione e formule: attenersi a ciò che è attestato dal codice, dai report e, se allegata, dalla tesi; non inventare esempi o metriche.
- Se due istruzioni sono inconciliabili, segnalami precisamente il conflitto e la proposta di soluzione. Non decidere tacitamente di eliminare una funzionalità.

## 2. Obiettivo e formato della consegna

**Lavora davvero sui file originali HTML/CSS/JavaScript/SVG**, non su mockup statici, screenshot o una riscrittura in PowerPoint. La presentazione dovrà poter essere pubblicata su GitHub Pages mantenendo gli URL e la struttura relativa degli asset; in particolare deve rimanere compatibile con un percorso tipo `/5g-thesis-presentation/` e con i link diretti `#slide-N` se presenti.

- Partiamo da **20 slide originali** e dobbiamo arrivare a **19 slide finali**: **originali 4 e 5 si fondono nella nuova 4**. Le originali 1–3 rimangono 1–3; la 6 originale diventa la nuova 5; e così via fino alla 20 originale che diventa la nuova 19.
- Non aggiungere slide divisorie, sezioni con solo titolo o slide riassuntive superflue.
- Non eliminare o stravolgere i contenuti già validi. Non inventare nuovi dati, test, formule o verifiche.
- Restituisci un **ZIP completo e funzionante**, con HTML, CSS, JavaScript, asset, font già presenti, report locali e file necessari, **non singoli pezzi di codice** da copiare a mano.
- Produci anche un **changelog** leggibile che indichi le slide **originali e finali** coinvolte e una **contact sheet delle 19 slide**, più screenshot dettagliati delle slide modificate. Non servono font esterni nuovi.
- **Non pubblicare o eseguire push sul mio GitHub senza una mia richiesta esplicita.** Consegnami il materiale pronto per essere caricato.

## 3. Scopo della tesi: ciò che la presentazione deve comunicare

Titolo: *A Domain-Specific Language for Verifying the Outcome of 5G SCAS Security Tests from Network Traffic Captures*.

Il punto centrale NON è il report in sé: il contributo è una **DSL dichiarativa che specifica sia la selezione delle evidenze sia le proprietà da verificare**, interpretata da una **pipeline software riutilizzabile**. L'output è un verdetto documentato da evidenze e riferimenti ai frame. La pipeline tratta inizialmente i protocolli in modo riutilizzabile e soltanto dopo seleziona le evidenze specifiche del test tramite DSL.

Non presentare la formalizzazione dei criteri SCAS come completamente automatica: **è il progettista a tradurli nella DSL**, poi il software applica le regole alle catture. Non presentare la DSL come il sistema che sceglie i protocolli da estrarre: **le sorgenti e i filtri sono configurati a parte**. Non descrivere tutti i test SCAS come basati obbligatoriamente su PCAP: sono le evidenze su cui lavora questo progetto.

Nel codice attuale, TShark legge la cattura e usa `-T ek` per generare **record JSON con i campi decodificati**, con eventuali filtri `-Y` e opzioni `-d`; i normalizzatori NAS / HTTP/2 / PFCP elaborano questi record per creare `MessageEvent`; il resolver semantico completa, quando serve, l'interpretazione applicativa. La DSL applica **successivamente** la selezione dichiarativa di sequenze o collezioni.

## 4. Mappa sintetica degli interventi (il dettaglio vincolante è nell'XML)

| Slide originale | Finale | Modifica attesa |
|---|---:|---|
| 1–2 | 1–2 | Conservare l'impostazione, migliorare coerenza grafica/sfondi/sottotitoli |
| 3 | 3 | Mettere in relazione **criteri SCAS, traffico PCAP e verdetto**; motivazione della tracciabilità |
| 4 + 5 | 4 | **Unificare** in una slide animata: prima software test-specifico, poi DSL con **selezione** e **verifica**, interpretata da una pipeline comune. Non descriverne ancora tutte le fasi interne |
| 6 | 5 | Architettura: **PCAP e DSL come due input concettuali esterni**, riquadro attorno alle fasi della pipeline; report come output. **Non visualizzare `tests.json`** sulla slide |
| 7 | 6 | Riprogettare la trasformazione **PCAP → record estratti da TShark → normalizzazione per protocollo (NAS/HTTP2/PFCP) e risoluzione semantica → MessageEvent → selezione DSL → evidenze selezionate**. Mostrare i **due livelli distinti**; esempio NAS e HTTP/2 attivi, PFCP visibile ma sbiadito |
| 8 | 7 | Conservare il percorso **evidenze → verifica → PASS/FAIL/INCONCLUSIVE → report reale** |
| 9 | 8 | Conservare i blocchi DSL **selezione / verifica**; differenziare i colori di `SEQUENCE`, `OPTIONAL`, `COLLECT` dal titolo; legenda inferiore leggermente più discreta |
| 10 | 9 | **NON ridisegnare** l'NFA di Thompson o le sue animazioni; esempio A / OPTIONAL B / C, atomi e transizioni ε. Ingresso in vista completa, opzione «Spiega per passi» |
| 11 | 10 | **NON ridisegnare** il matcher o le sue animazioni; stessa sequenza **A X A B X C** e riconoscimento **A(3), B(4), C(6)**. Ingresso al **primo passo** (non subito vista completa), con opzione Vista completa |
| 12 | 11 | **Ridisegnare** il BindingContext in continuità con le due slide prima: `a → A(3)`, `b → B(4)`, `c → C(6)`. Animazione facoltativa con «Spiega per passi» / «Vista completa». **3, 4, 6 sono posizioni nell'esempio, non frame reali della PCAP** |
| 13 | 12 | Conservare quasi invariato il motore: BindingContext → verifiche statiche / temporali MFOTL + MonPoly → risultati |
| 14 | 13 | AMF Sync Failure Case B: **PASS più evidente**, meno codice, timeline T3520 più grande, **15 secondi**, osservati ~**25,018 secondi**, frame **358** e **606**, **4 controlli statici PASS + 1 temporale PASS** |
| 15 | 14 | **Conservare**: `COLLECT` di **5** risposte PFCP, **10** coppie `{TEID, IPv4}` senza duplicati, frame **37/38/46/47/48**, `REQUIRE UNIQUE`, PASS |
| 16 | 15 | **Rifare** come matrice **2×2**: percorso **SUCI diretto** vs **GUTI→SUCI**; origine **fallimento locale AMF** vs **fallimento lato AUSF**. Casi A/B/C/D esattamente come XML, tutti PASS; `OPTIONAL` e `IF` ben visibili. Le condizioni IF possono dipendere da **parametri di configurazione del caso**: non rappresentarle come semplice test della presenza di un OPTIONAL |
| 17 | 16 | Conservare tabella baseline: **10/10 concordanze**, con **9 PASS e 1 FAIL atteso (NRF)**. Non trasformare in «10 test PASS» |
| 18 | 17 | **Ridisegnare** mutation testing come **ciclo** con **una sola pipeline**: PCAP+DSL → esecuzione originale → report baseline con frame rilevanti → mutatore offline esterno che riceve report e PCAP originale → PCAP mutata → **stessa** pipeline e DSL → report e verdetto mutati → confronto con atteso. Non inventare un collegamento diretto dal selettore DSL al mutatore |
| 19 | 18 | Migliorare senza perdere le matrici: **15/15 esperimenti coerenti con gli attesi**; AMF mutazione statica / temporale / combinata; UPF duplicato = **FAIL**, evidenze insufficienti = **INCONCLUSIVE** |
| 20 | 19 | Conclusione visiva forte e ariosa, non un elenco né una copia del parlato: **«Non basta un verdetto. Serve poterlo giustificare con le evidenze.»**; «Grazie per l'attenzione» e «Domande?» piccoli. Vedere XML per grafica e vincoli. Il mio parlato finale rimane quello del TXT |

## 5. Interattività e navigazione: requisito NON negoziabile

Il progetto non è una semplice serie di immagini: alcune slide hanno controlli interattivi e animazioni a passi. L'XML contiene la specifica **`NAV-01`**: applicala per intero.

- **Vista completa**: un solo comando **Avanti** (pulsante o freccia destra / Space / PageDown) passa **immediatamente alla slide successiva**, senza che sia obbligatorio attivare «Spiega per passi».
- **Spiega per passi**: Avanti mostra il **passo successivo**; se l'ultimo passo è già visibile, **un altro Avanti apre direttamente la slide successiva**, senza blocchi, doppio clic o obbligo di premere Vista completa.
- I pulsanti locali e globali devono essere coerenti; il tasto non deve generare due avanzamenti; Indietro deve rimanere sensato. Collaudare anche i ritorni sulle slide animate, i link diretti e la vista stampa/esportazione.
- NON sostituire `interactive-slides.js` e `script.js` con una gestione parallela inventata senza comprenderne gli handler. Correggi l'implementazione esistente e testa davvero tastiera e pulsanti.

## 6. Direzione visiva globale

Le slide originali mi piacciono per morbidezza, riquadri arrotondati e contenuti tecnici. **Non voglio sfondo nero, gradienti saturi, grafica aziendale aggressiva, né un cambio completo di stile.** Voglio però evitare 19 slide quasi identiche e troppo bianche.

Utilizza il **sistema cromatico e i valori suggeriti nell'XML v1.4**. A grandi linee: introduzione azzurro nebbia; architettura blu ghiaccio/teal; DSL lavanda delicata; test salvia leggera; mutation testing neutro caldo tenue; conclusione pervinca più riconoscibile. Bordi sottili, ombre discrete, buon contrasto e molto spazio, senza ridurre la leggibilità di tabelle, DSL, NFA e timeline.

**Sottotitoli**: sostituisci quelli attuali usando il piano editoriale dell'XML. Devono contenere una sola idea utile, non un placeholder descrittivo. Non allungarli, non farli diventare slogan e non obbligare un sottotitolo dove è ridondante. Mantieni i font del pacchetto originale; non condividere o sostituire i file font.

## 7. Collegamento con il parlato e rispetto del tempo

Il TXT è un **copione di lavoro definitivo nei contenuti**, non il testo da proiettare. Per le prime fasi di questo incarico, NON riscriverlo automaticamente e non forzare i diagrammi a ripetere frasi intere pronunciate a voce. Ogni slide deve sostenere il punto che sto spiegando in quel momento.

Il vincolo resta **20 minuti massimi**. Il copione allegato conta circa **2.960 parole**, corrispondenti a circa **22:45 a 130 parole/minuto, prima delle animazioni**; pertanto è già individuata una criticità di durata. **Non risolverla aggiungendo altre slide o altre animazioni obbligatorie**, e non sacrificare le tre slide dedicate al matcher/BindingContext. Dopo la revisione delle slide ti chiedo un **report separato** con i punti del parlato che si possono accorciare, senza modificare autonomamente il testo originale. Nell'XML vi sono tempi indicativi da trattare come **budget**, non come misure già verificate.

**Nota sulla numerazione dei capitoli e slide nel TXT:** il testo allegato conserva alcuni riferimenti redazionali alle slide ORIGINALI e usa etichette come «attuale slide». Non proiettarli. La numerazione definitiva da implementare è quella a **19 slide**. La sezione conclusiva del TXT è chiamata «Parte 6» per errore redazionale, ma è la quinta parte del discorso.

**Nota sulla conclusione:** il paragrafo orale di conclusione contenuto nell'XML è **superato dal TXT allegato**. Non reinserirlo e non imporre al parlato la frase della slide conclusiva. Si tratta di due mezzi comunicativi complementari.

## 8. Processo operativo da seguire

**Fase A — Analisi preliminare**
1. Scompatta lo ZIP e verifica che siano presenti **20 slide originali** e gli script di navigazione. Leggi l'XML e il copione per intero.
2. Costruisci una checklist concreta che mappi tutti gli interventi dell'XML sui file e sugli elementi HTML/SVG/JS esistenti. Se trovi conflitti tecnici o elementi che non esistono, descrivili in modo specifico; non saltarli.
3. Tieni in evidenza l'obbligo di **preservare integralmente** l'esempio e le animazioni originali di Thompson e matcher.

**Fase B — Implementazione**
4. Applica prima l'accorpamento 4+5, la rinumerazione e la revisione dei diagrammi, poi la navigazione, gli sfondi, i sottotitoli e la nuova conclusione.
5. Mantieni invariati i dati sperimentali verificati e gli esempi coerenti con il codice. Se una visualizzazione nuova implica una semplificazione tecnica, esplicitala correttamente.
6. Non fermarti a una descrizione di come faresti la modifica: **modifica i file**.

**Fase C — Collaudo reale**
7. Avvia o renderizza la presentazione e genera screenshot reali a **1600×900** e controlli a **1280×720**. Verifica una per una tutte le **19 slide finali**, comprese le versioni iniziale/ultimo passo/vista completa per le slide animate.
8. Controlla: testi troncati, SVG deformati, sovrapposizioni, font mancanti, pulsanti inerti, regressioni nei dati, clippings, navigazione bloccata, errori JavaScript e link relativi.
9. Esegui prove di interazione: Vista completa→Avanti; Spiega per passi→ultimo passo→Avanti; tastiera; pulsanti; Indietro; nuovo ingresso sulla slide; link `#slide-N`. Verifica nessun doppio avanzamento.
10. Se il codice o il layout non superano il collaudo, **correggi prima di consegnare**. Non dichiarare test completati che non hai eseguito.

**Fase D — Consegna**
11. Consegnami **ZIP aggiornato**, **contact sheet**, alcune anteprime delle slide modificate, **changelog** e un breve resoconto dei test. Specifica chiaramente eventuali limiti rimasti.
12. **Non pubblicare** direttamente sul repository, non eliminare la versione originale e non consegnare una demo semplificata al posto del progetto completo.

## 9. Criteri di accettazione sintetici

La consegna è valida soltanto se: sono **19 slide**; i risultati e i dati sono corretti; la nuova matrice RES* è interpretabile; il mutation testing usa una sola pipeline nel diagramma e due esecuzioni comparabili; la conclusione parlata originale è rispettata; le animazioni dell'NFA e del matcher sono conservate; il BindingContext riprende esattamente A(3)/B(4)/C(6); Vista completa e Spiega per passi navigano senza blocchi; tutti gli sfondi e i sottotitoli sono stati revisionati; lo ZIP finale è **funzionante** e include gli asset relativi. Usa anche la checklist `A01`–`A22` presente nell'XML.

**Importante:** se hai strumenti per lavorare sul file system e visualizzare pagine web, usali. Non mi serve un altro piano teorico: questa chat deve produrre concretamente la nuova versione della presentazione a partire dai file allegati, rispettando l'XML e il mio testo orale.
