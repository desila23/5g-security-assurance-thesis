# Checklist XML v1.4 — mappa di implementazione

| ID | Specifica | File / elementi |
|---|---|---|
| A01 | 19 slide dopo l'unione 4+5. Vecchie 14→nuova13, 15→14, 16→15, 17→16, 18→17, 19→18, 20→19. Nessuna nuova slide divisoria. | index.html: 19 section, indice e numerazione |
| A02 | PASS unico prominente, quattro controlli statici e uno temporale, T3520 15 s, frame 358 e 606 e intervallo osservato 25,018 s. | slide-13: DSL, PASS e timeline |
| A03 | COLLECT e UNIQUE invariati, 5 risposte PFCP, 10 coppie distinte, frame 37/38/46/47/48, verdetto PASS. | slide-14: tabella originale PFCP |
| A04 | Matrice 2×2 corretta A/B/C/D con righe di identificazione e colonne origine della verifica; 7/9/9/11 PASS e 2 SKIPPED per caso; non descrivere IF come test della sola OPTIONAL. | slide-15: matrice e parametri IF |
| A05 | 10/10 atteso/osservato, 9 PASS e 1 FAIL atteso NRF; nessuna perdita di righe nella tabella. | slide-16: tabella baseline |
| A06 | PCAP baseline e DSL ingressi concettuali, unica pipeline, report baseline → motore mutazione, PCAP originale → mutatore, PCAP mutata ritorna alla stessa pipeline, report mutato e confronto finale; mutatore fuori dal perimetro. | slide-17: unico blocco pipeline e ciclo offline |
| A07 | 15/15 correttamente etichettati come esiti attesi; AMF tre mutazioni con esiti componenti corretti; UPF PASS→FAIL e PASS→INCONCLUSIVE. | slide-18: tabella AMF, esiti UPF e 15/15 |
| A08 | Rispettare interamente NAV-01 della versione 1.2; testare Vista completa e Spiega per passi, avanzamento dopo ultimo step, tasti e pulsante Avanti. | script.js + interactive-slides.js |
| A09 | Rendere screenshot reali a 1600×900 e almeno 1280×720, senza sovrapposizioni/clipping/testo illeggibile, senza cambiare lo stile morbido già adottato. | anteprime e report di collaudo |
| A10 | Non introdurre slogan generici o lunghe frasi placeholder; registrare i sottotitoli da sottoporre a revisione globale successiva. | slide-subtitle-1…18; nessun sottotitolo 19 |
| A11 | Nessun numero mutato, nessun nome di protocollo o costrutto improprio; riusare report e dati reali, non inventare fonti. | data/reports + data/regole |
| A12 | Fornire ZIP completo HTML/CSS/JS e breve changelog riferito ai numeri ORIGINALI e FINALI, verificando funzionamento sia su desktop sia GitHub Pages con URL relativo. | ZIP e README |
| A13 | Nuova slide 19 presenta in grande «Non basta un verdetto. Serve poterlo giustificare con le evidenze.»; ringraziamento e Domande? marginali; nessuna lista riepilogativa, nessun nuovo dato sperimentale. | slide-19: frase conclusiva |
| A14 | Ogni sezione finale 1–4, 5–7, 8–12, 13–16, 17–18, 19 usa variazioni sottili e coordinate; nessuno sfondo nero o eccessivamente saturo. | background-N / corner-N / glow-N |
| A15 | Controllare gradienti/rect/defs inline in index.html e variabili di style.css: fondo migliorato su OGNI SLIDE e non solo in CSS; nessun cambio accidentale nei colori dei dati e delle animazioni. | defs SVG + style.css |
| A16 | Applicare il piano editoriale v1.4 a tutte le 19 slide; nessuna frase placeholder o sottotitolo originale della 20 ricompare; massimo una idea sintetica per slide. | slide-subtitle-N |
| A17 | Titoli, frammenti di DSL, tabelle, annotazioni temporali, etichette degli NFA e badge PASS/FAIL/INCONCLUSIVE leggibili anche quando il contenitore riceve sfondo colorato. | testo SVG / font locali / anteprime |
| A18 | Nessun rifacimento non richiesto delle figure o delle animazioni Thompson/matcher delle slide originali 10–11; nessuna modifica ai risultati o alle formule. | construction-* / matcher-* originali |
| A19 | Collaudare le slide nuove anche dopo il redesign cromatico, in ingresso, dopo ogni step e in vista completa; tasti avanti/indietro e nessun blocco sull’ultimo passo. | rationale / construction / matcher / binding |
| A20 | Esportare almeno una contact sheet delle 19 slide e renderizzare ognuna a 1600x900, controllando anche riduzione a 1280x720; nessun testo troncato, crop, card sovrapposta o annotazione illeggibile. | anteprime 1600×900 e 1280×720 |
| A21 | Conclusione con messaggio centrale statica o animazione facoltativa brevissima; non introdurre slide divisorie o nuove animazioni obbligatorie che allarghino i 20 minuti. | tempi-slide.md + report_durata.md |
| A22 | Changelog che distingue interventi strutturali, sottotitoli, sfondi e conclusione; consegnare ZIP completo più screenshot anteprima prima/dopo di almeno slide 3, 4, 6, 15, 17, 19 finali. | changelog e confronti prima/dopo |
