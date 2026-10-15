# Dove modificare testi, immagini e passi

## Testi e layout

Apri `index.html`. Cerca `id="slide-N"`, sostituendo N con il numero da 1 a 20. Ogni sezione contiene il proprio SVG e una nota orale in `<template class="speaker-note">`.

- Testi: contenuto di `<text>`; `x`, `y`, `font-size` controllano posizione e dimensione.
- Titolo nell’indice e nella barra: aggiorna anche `data-title`, `aria-label` e il pulsante `data-go` corrispondente, che usa la numerazione da zero.
- Sottotitoli: gruppi `slide-subtitle-N`, dove presenti. Alcune slide ne sono volutamente prive.
- `GUIDA_TESTI.md` elenca i testi presenti in questa consegna.

## Immagini e colori

Il logo è `assets/logo.png`; il riferimento è `<image href="assets/logo.png">` nella slide 1. I diagrammi sono forme SVG modificabili in `index.html`.

I font locali sono in `assets/fonts/`. La palette comune e lo stile dei controlli sono in `style.css`. Il bianco dello sfondo è scritto anche nel rettangolo iniziale di ogni SVG: non aggiungere gradienti a quel rettangolo.

## Slide animate

I passi sono in `interactive-slides.js`:

| Slide | Array | Gruppi SVG |
|---:|---|---|
| 4 | `rationaleSteps` | `dsl-legacy` e `dsl-pipeline`, mutuamente esclusivi |
| 10 | `constructionSteps` | `construction-*` |
| 11 | `matcherSteps` | `matcher-*` |
| 12 | `bindingSteps` | `binding-overview`, `binding-closeup` |

Per cambiare una spiegazione modifica il campo `label`. Gli array della 10 e della 11 mantengono la logica originale. `script.js` coordina navigazione, tastiera, indice, note e stampa.

## Dati ed esempi

- `data/reports/`: report sperimentali completi, invariati.
- `data/regole/nrf_sequence_test.dsl`: unica regola mostrata alla slide 8.
- Slide 7: valori didattici, non frame reali. La notazione è abbreviata.
- Slide 8: estratto del report UPF con SHA256 integrale; il collegamento apre il report completo.
- Slide 12: esempio didattico `event.a`, `event.b`, `event.c`; le posizioni 3, 4, 6 non sono frame reali.
- Slide 16: A/C nella prima riga, B/D nella seconda. IF usa la configurazione del caso.

## Componenti aggiornati

- Slide 4: `paintRationale()` anima la convergenza dei tre verificatori in un unico motore. Non modifica gli array NFA/matcher.
- Slide 6 e 18: gruppi `pipeline-core-6` e `pipeline-core-18`, identici in geometria, colori e testi. Se li modifichi, mantienili coerenti.
- Slide 16: frammento leggibile e pulsante `open-resstar-rule`. Il dialogo `resstar-rule-dialog` contiene il testo integrale di `data/regole/resstar_verification_failure.dsl`.
- I comandi dei passi si chiamano sempre Indietro e Avanti, anche ai confini tra slide.

## Revisione 3

- Il sottotitolo della slide 1 è nel `foreignObject` di `slide-subtitle-1`: è un paragrafo HTML con a capo naturale.
- Slide 4: lo sfondo `rationale-backdrop` e il titolo sono comuni ai due stati. Le forme intermedie mantengono i riempimenti delle regole.
- Slide 6: le etichette a destra sono output dei sei stadi. La freccia PCAP è disegnata dopo il gruppo pipeline, per restare visibile al suo interno.
- Slide 7: gli attributi `data-packet-index`, `data-selected` e `data-extracted-index` mantengono la corrispondenza tra pacchetti evidenziati ed estratti.
- Slide 12: la matrice iniziale dell’animazione corrisponde alla posizione e alla dimensione del BindingContext chiuso.
- Slide 14: il dialogo `amf-rule-dialog` mostra il file completo di selezione/controlli statici e la formula temporale CASE B dal file condiviso.
- Slide 18: la freccia dalle evidenze descrive una dipendenza logica. Il mutatore legge i frame dal report baseline nell’implementazione, come ricordato nella nota orale.
- Slide 19: due tabelle parallele per AMF e UPF; le mutazioni UPF sono su righe distinte.
