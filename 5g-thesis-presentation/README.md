# Presentazione della tesi 5G — 20 slide

Apri `index.html` nel browser. Il pacchetto funziona offline e in una sottocartella di GitHub Pages. Carica tutti i file, comprese `assets` e `data`.

## Dove modificare

| Cosa | File |
|---|---|
| Testi, sottotitoli, snippet, diagrammi SVG e note | `index.html`; commenti `SLIDE NN` e `SOTTOTITOLO SLIDE NN` |
| Colori e font comuni | `style.css`, sezione 01 e variabili `:root` |
| Spiegazioni dei passi | `interactive-slides.js`, `constructionSteps` e `matcherSteps` |
| Pulsanti dei passi | `interactive-slides.js`, `uiText` |
| Navigazione, tastiera, indice e note | `script.js` |
| Logo e font locali | `assets/logo.png` e `assets/fonts.css` |
| Estratto del report originale UPF | `data/upf-report-excerpt.json` |
| Durate indicative | `tempi-slide.md` e `data-seconds` nelle sezioni HTML |

`GUIDA_TESTI.md` elenca ogni scritta con file, riga e ID. `MODIFICA_SLIDE.md` contiene anche la mappa dei diagrammi, delle frecce e delle immagini. Le righe valgono per questa versione; dopo le modifiche usa gli ID e i commenti come riferimenti stabili.

## Comandi

- Frecce sinistra/destra, Page Up/Down e spazio: navigazione.
- I: indice. N: note del relatore. F: schermo intero. P: stampa/PDF.
- Slide 10 e 11: “Spiega per passi”, Avanti, Indietro e Ricomincia.
- Nei passi manuali, le frecce e lo spazio avanzano i passi; Page Up/Down cambiano slide.
- La stampa ripristina la vista completa degli automi, anche se stai spiegando un passo.

## Revisione 14

20 slide. Nella 7 le etichette del normalizzatore e del resolver hanno la stessa dimensione ridotta; PFCP è attenuato e il diagramma prosegue da MessageEvent alla selezione DSL e alle evidenze selezionate. Nella 12 c’è una sola frase sui binding. Il collegamento della spiegazione temporale nella 14 è viola e spostato a destra. La DSL nella 18 è centrata e non c’è la scritta sul rientro. Nella 19 sono ripristinati i colori della foto; solo i titoli AMF e UPF hanno lo stesso blu.

Tutte le scritte e le forme rimangono modificabili. Le guide sono aggiornate ai numeri di riga di questa versione.

## Diagrammi e PDF

Le figure sono SVG nel file HTML: modifica riquadri con `rect`, stati con `circle` e collegamenti con `path`. Il report nella slide 8 conserva l’hash completo su una riga. I dati del file JSON sono indipendenti dai testi SVG della slide.

Le modifiche ai sorgenti non cambiano il PDF già scaricato. Dopo averle fatte, usa la stampa del browser per esportare un nuovo PDF. Per la pubblicazione su GitHub Pages non serve un processo di compilazione.
