# Presentazione tesi 5G

Apri questo link: https://desila23.github.io/5g-security-assurance-thesis/5g-thesis-presentation/#slide-1.
La presentazione funziona offline e contiene 14 slide.

Il formato 16:9 si adatta proporzionalmente alla finestra. Per la presentazione su desktop usa il pulsante “Schermo intero”, il tasto F o F11. Tutti i caratteri sono inclusi, senza dipendenze esterne.

- Frecce destra e sinistra: slide successiva e precedente.
- Home e End: prima e ultima slide.
- I: indice.
- P o pulsante PDF: stampa tutte le slide, anche quelle non attive. Scegli “Salva come PDF”, margini assenti e grafica di sfondo.
- Su telefono: ruota in orizzontale e scorri lateralmente.

Il file HTML singolo fornito separatamente contiene la stessa presentazione e si apre direttamente, senza estrarre questa cartella.

## Fonti del progetto

Contenuti basati sul brief XML, sulle versioni precedenti e sul report di correzioni allegati.

Repository: https://github.com/desila23/5g-security-assurance-thesis/tree/refactor/generic-pipeline
Snapshot consultato: `53891636cfbed35c6bf55236e3dd1dcb72346e01`.

Il caso UPF usa i dati di `reports/upf_teid_uniqueness/report.json` e `reports/upf_teid_uniqueness_offline_mutation/report.json`: 5 risposte, 10 F-TEID, nessun duplicato nella cattura originale; un F-TEID riutilizzato nei frame 37 e 38 nella cattura mutata.

La slide 5 descrive il ruolo di config/tests.json e mostra AMF synchronization failure, caso A. L'estratto omette description e i dettagli della sezione temporal, mantenendo traffic e sources completi, compresi display_filter e decode_as. Il file amf-test-example.json contiene l'intera voce AMF originale, senza omissioni.

L'estratto JSON della slide 13 mantiene i valori e la struttura delle sezioni mostrate nello schema 2.0. Il report completo contiene anche source, metadata, configuration, criteria, evidence ed explanation.

Il valore 25/25 riprende la regressione documentata nel progetto. La configurazione e il runner definiscono 10 scenari baseline e 15 scenari mutati. Questa revisione della presentazione non riesegue i test di rete del repository.

La slide 10 è un esempio illustrativo del flusso di verifica: la freccia verde evidenzia un esito PASS. Il caso UPF nelle slide 11 e 13 usa invece i report reali.

Gli SVG restano testo e forme modificabili in `index.html`; colori, font e controlli sono definiti in `style.css` e la navigazione in `script.js`. I font Nimbus Sans e DejaVu Sans Mono sono inclusi come WOFF. Le licenze sono in `FONT-LICENSE.txt` e nel CSS.
