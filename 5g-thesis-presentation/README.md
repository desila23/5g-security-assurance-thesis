# Presentazione tesi 5G — revisione finale

28 slide. Budget indicativo: **20:33**, da confermare con una prova orale. L’introduzione è stata ridistribuita sul discorso aggiornato; il totale non è una durata misurata.

Estrai tutta la cartella e apri `index.html`. La presentazione funziona offline. Non serve Python per visualizzarla.

- Frecce, spazio e PageUp/PageDown: passi interni e navigazione.
- V: alterna spiegazione per passi e vista completa sulla slide animata attiva.
- R: ricomincia i passi della slide attiva.
- I: indice. N: note del relatore. F: schermo intero. P: stampa/PDF.
- Home/End: prima/ultima slide.

I pulsanti generici dei passi sono stati rimossi; restano i comandi da tastiera e la navigazione inferiore. Le spiegazioni dei passi sono centrate; sulla slide del motore comune rimane soltanto il titolo interno. I comandi per aprire regole e report completi restano disponibili.

L'ordine è definito da `slides.json`. I nomi dei file originali mantengono i vecchi prefissi. La [mappa generata](mappa-slide.md) contiene i numeri correnti e i collegamenti locali.

Modifica i sorgenti in `slides/`, `css/`, `js/` e `esempi/`. Poi esegui `python3 build.py`, `RICOMPILA.bat` o `RICOMPILA.command`. Il build rigenera anche note, tempi e mappa. `python3 build.py --check` controlla la coerenza dei quattro file generati.

La versione precedente della slide baseline è conservata in `slides/archive/18-baseline-v9.html`, esclusa da `slides.json`. Per ripristinarla, cambia solo il campo `file` dell'elemento con chiave `baseline` nel manifest, poi ricompila.

La tabella completa riunisce i dati delle tabelle `tab:open5gs_results` e `tab:free5gc_results` del capitolo 6 della tesi. I dati e la provenienza sono in `data/baseline-casi-completi.json`. Gli sviluppi futuri riprendono il capitolo 7.

Riferimento di partenza: repository `desila23/5g-security-assurance-thesis`, branch `gh-pages`, commit `8f841edcc696cab944fd2cae7abb64ea800c0551`. Revisione preparata e verificata prima della pubblicazione su `gh-pages`.

Le guide e le revisioni precedenti conservate nella cartella sono documenti storici. Per la versione corrente usare questo README, `mappa-slide.md`, `note-relatore.md` e `tempi-slide.md`.
