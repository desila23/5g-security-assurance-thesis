# Revisione v9 — rifiniture finali (16/10/2026)

Base: Presentazione_5G_revisionata_v8. Il numero di slide resta **21**.

## Cosa è cambiato

- **Slide 5:** riorganizzata per distinguere nettamente un *esempio esterno* (OpenAPI) dal *contributo della tesi* (DSL SCAS). OpenAPI è un'analogia sul vantaggio di descrizioni formali: non è il linguaggio della tesi né un test SCAS. La DSL è rappresentata come contributo principale, con due attività: selezione delle evidenze e verifica dei criteri. Esempio YAML sempre esterno e modificabile. Aggiornate le note orali.
- **Slide 13:** preservata l'area unica di verifica con le due modalità statica e temporale. Ingresso dal BindingContext ramificato con segmenti verticali leggibili; **una sola uscita centrale** dall'area, poi tre diramazioni verso FAIL, PASS e INCONCLUSIVE. Report e verdetti invariati.
- **Sottotitoli:** sostituite soltanto frasi genericamente descrittive nelle slide 3, 4, 5, 7, 9, 10, 11, 12, 13, 19 e 20. Conservati i sottotitoli già specifici delle slide con risultati sperimentali.
- **Testi delle spiegazioni per passi:** rese più discorsive le didascalie delle slide 4, 10, 11 e 12; nessuna modifica alla sequenza degli step o alle animazioni.
- **Sfondo e stile:** lasciati bianchi e coerenti con la v8.

## Come modificare in autonomia

- Composizione della slide 5: `slides/05-dsl.html` (pannelli `openapi-example-panel` e `designed-language-panel`).
- Codice OpenAPI: `esempi/openapi-esempio.yaml`; dimensioni del testo: `css/openapi.css`.
- Frecce della slide 13: `slides/13-verifica.html` cercando `context-entry-` e `verification-exit-`.
- Sottotitoli: riga `<text ... y="222" ...>` nei rispettivi file `slides/*.html`.
- Frasi dei passi 4/10/11/12: `js/config.js`.
- Per ricompilare `index.html`: esegui `python build.py` (o gli script RICOMPILA inclusi).

Non sono state ripristinate transizioni tra slide 7/8 o 12/13.
