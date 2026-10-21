# Tesi triennale — progetto LaTeX

## File principali

- `main.tex` — documento principale, frontespizio, indice automatico, elenco figure, bibliografia.
- `capitoli/01_capitolo.tex` … `07_capitolo.tex` — capitoli editabili separatamente.
- `figure/` — le TRE figure approvate, importate senza modifiche dal tuo `BOZZE.zip`.
- `bibliografia_tesi.bib` — 18 riferimenti già selezionati.
- `sorgente_markdown/` — copia della bozza originale completa e versione normalizzata di ogni capitolo (backup, non compilate da LaTeX).
- `main.pdf` — anteprima PDF generata dalla compilazione del progetto, se presente.

## Compilazione

Apri **main.tex** in VS Code (LaTeX Workshop), TeXstudio oppure Overleaf.

Compilazione consigliata con LuaLaTeX + Biber:

```sh
latexmk -lualatex -interaction=nonstopmode -file-line-error main.tex
```

Se l'ambiente non gestisce `latexmk`, esegui in ordine:

```sh
lualatex main.tex
biber main
lualatex main.tex
lualatex main.tex
```

Le nuove sezioni, figure e citazioni vengono numerate automaticamente.

## Scelte editoriali

- Impaginazione A4, 12 pt, Latin Modern Roman, margini da tesi.
- I titoli delle sezioni sono derivati dalla bozza, ma i numeri 1, 2, 2.1, ecc. vengono prodotti automaticamente da LaTeX.
- I due segnaposto scartati (UPF e RES*) NON vengono inclusi.
- Le formule e i frammenti di codice restano coerenti con la bozza; sono stati cambiati solo i delimitatori necessari per la conversione.
- Lo schema del report nel Capitolo 4 rimane volutamente illustrativo e non è stato convertito in un esempio JSON eseguibile.
- I contenuti delle figure sono incorporati come PNG; il PDF include le relative didascalie.

## Da controllare prima della consegna

1. Conferma i dati del frontespizio, l'anno accademico e il titolo ufficiale con il relatore.
2. Verifica visivamente le figure nel PDF e le eventuali richieste di impaginazione dell'ateneo.
3. Controlla la versione delle specifiche tecniche in bibliografia e gli estremi delle citazioni.
