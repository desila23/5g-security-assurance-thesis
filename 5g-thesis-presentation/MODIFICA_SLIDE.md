# Dove modificare la presentazione — versione 9

Ogni slide ha un HTML separato. CSS e JavaScript sono in cartelle proprie. I percorsi sono relativi alla cartella `5g-thesis-presentation` estratta dallo ZIP.

## File da modificare

| Cosa | File | Dopo la modifica |
|---|---|---|
| Testi, diagrammi, geometria e note di una slide | Il relativo HTML in `slides/` | Ricomponi |
| Esempio OpenAPI della slide 5 | `esempi/openapi-esempio.yaml` | Ricomponi |
| Colori, caratteri, controlli e stampa | `css/presentation.css` | Aggiorna il browser |
| Font e interlinea del codice OpenAPI | `css/openapi.css` | Aggiorna il browser |
| Frasi dei passi e durata del close-up | `js/config.js` | Aggiorna il browser |
| Animazioni interne alle slide | `js/steps.js` | Aggiorna il browser |
| Navigazione, tastiera, indice e note | `js/deck.js` | Aggiorna il browser |
| Finestre integrali JSON e DSL | `js/dialogs.js`, `templates/dialogs.html` | Ricomponi solo se cambi HTML |
| Struttura della pagina | `templates/page.html` | Ricomponi |
| Ordine delle slide | `slides.json` | Ricomponi |

## Ricomporre

Salva le modifiche e avvia `RICOMPILA.bat` su Windows o `RICOMPILA.command` su Mac. In alternativa, esegui `python3 build.py` nella cartella. Serve Python 3, senza librerie aggiuntive.

Poi riapri o aggiorna `index.html`. Il file fornito è già pronto e per visualizzarlo non serve Python.

`index.html` viene generato: le modifiche fatte direttamente lì vengono sostituite alla ricomposizione. `python3 build.py --check` controlla se è aggiornato senza riscriverlo.

## Mappa degli HTML

| Slide | Titolo | File |
|---:|---|---|
| 1 | Titolo della tesi | `slides/01-titolo.html` |
| 2 | 5G Core: Network Functions e interazioni | `slides/02-rete-5g.html` |
| 3 | Le SCAS descrivono come verificare la sicurezza | `slides/03-scas.html` |
| 4 | Da verificatori dedicati a un motore comune | `slides/04-motore-comune.html` |
| 5 | Una DSL per i test SCAS | `slides/05-dsl.html` |
| 6 | Architettura proposta | `slides/06-architettura.html` |
| 7 | Dal traffico alle evidenze del test | `slides/07-normalizzazione.html` |
| 8 | Dalle evidenze al verdetto e al report | `slides/08-report.html` |
| 9 | La DSL: selezionare gli eventi e verificarli | `slides/09-sintassi-dsl.html` |
| 10 | Dalla regola all’automa | `slides/10-nfa.html` |
| 11 | Riconoscimento della sequenza | `slides/11-matcher.html` |
| 12 | Dal Match al BindingContext | `slides/12-binding.html` |
| 13 | Motore di verifica | `slides/13-verifica.html` |
| 14 | Testing e Mutation testing | `slides/14-testing.html` |
| 15 | AMF Synchronization Failure, Case B | `slides/15-amf-sync.html` |
| 16 | UPF TEID Uniqueness | `slides/16-upf.html` |
| 17 | AMF RES*: quattro casi, una regola DSL | `slides/17-resstar.html` |
| 18 | Risultati dei test baseline | `slides/18-baseline.html` |
| 19 | Mutation testing: il processo | `slides/19-mutazioni.html` |
| 20 | Risultati del mutation testing | `slides/20-risultati-mutazioni.html` |
| 21 | Non basta un verdetto | `slides/21-conclusioni.html` |

## Elementi modificabili nell’HTML

- Testi: contenuto di `<text>`. Posizione: `x` e `y`. Dimensione: `font-size`.
- Riquadri: `<rect>`, con `x`, `y`, `width`, `height` e `rx`.
- Frecce: `<path>`, con percorso nel campo `d`.
- Colori: `fill` e `stroke`. Le classi comuni sono nel CSS.
- Titolo dell’indice: `data-title` della sezione. Titolo visibile: testo a `y="167"`.
- Note: `<template class="speaker-note">` in fondo al file.

Mantieni `{{N}}`, `{{NN}}` e `{{TOTAL}}`: sono segnaposto compilati automaticamente. Gli ID interni dei componenti rimangono stabili anche quando una slide cambia numero.

## OpenAPI nella slide 5

È il pannello sinistro `openapi-example-panel`, etichettato come esempio esterno. La DSL progettata è il pannello principale destro `designed-language-panel`. Il codice mostrato da `<pre id="openapi-example">` viene dal YAML tramite `{{OPENAPI_EXAMPLE}}`.

Cambia il contenuto nel YAML, la posizione nell’HTML e il carattere in `css/openapi.css`. Dettagli in `GUIDA_OPENAPI.md`.

## Slide 7 e 8

Sono di nuovo due slide separate. La 7 mostra normalizzazione, struttura MessageEvent e selezione delle evidenze. La 8 mostra verifica, verdetto, estratto del report e pulsante per il JSON completo. Non ci sono fasi 1/2–2/2 né transizioni fra le due pagine.

## Passi interni

In `js/config.js`: `rationaleSteps` e `rationaleCaptions` per la slide 4; `constructionSteps` per la 10; `matcherSteps` per la 11; `bindingSteps` per la 12.

`motion.rationale` vale 560 ms. `motion.bindingZoom` vale 850 ms: è l’ingrandimento interno della slide 12. Il passaggio 12→13 è immediato, senza animazione. Non ci sono file per transizioni fra slide.

## Frecce dei verdetti nella slide 13

`verification-area` delimita l’area comune dei due verificatori. Dal bordo inferiore dell’area parte una sola uscita centrale, che poi si dirama verso FAIL, PASS e INCONCLUSIVE. I percorsi sono identificati dagli ID `verification-exit-trunk`, `verification-exit-left`, `verification-exit-center` e `verification-exit-right`. Anche il BindingContext usa una diramazione comune, identificata da `context-entry-`. PASS è verde nell’esempio, gli altri due collegamenti sono grigi.

## Dati originali

I report sono in `data/reports/`, le regole in `data/regole/`. Il builder incorpora il report UPF e le regole AMF/RES* nei dialoghi senza modificarli. Logo e font locali sono in `assets/`.
