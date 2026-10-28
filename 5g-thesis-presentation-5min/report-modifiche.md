# Revisione definitiva della presentazione da cinque minuti

28 ottobre 2026.

## Struttura finale

Sei slide, copertina compresa, come richiesto nel report definitivo. La copertina HTML riutilizza l’SVG della prima slide originale, mantenendo logo, testi, layout, colori e grafica. I riferimenti al logo sono incorporati per il funzionamento offline.

1. Copertina originale.
2. Security Assurance: unico confronto tra requisito e software, con richiamo al 5G. Nessuna PCAP nella slide di contenuto.
3. Dagli SCAS al DSL: due soli avanzamenti A–B–C. Ritagli ufficiali e pseudocodice dichiaratamente illustrativo; caso NRF con selezione e verifica; confronto finale con SEQUENCE blu e REQUIRE verde nella sintassi reale.
4. Sistema di verifica: pipeline verticale, DSL collegato separatamente a selezione e verifica, controlli statici/MonPoly e report con evidenze.
5. Baseline: tabella raggruppata Open5GS/free5GC, 16 catture, 12 PASS, un FAIL e tre INCONCLUSIVE. Provenienza e ScasDK sono nelle note orali, senza riempire la slide.
6. Mutation testing: percorso baseline, PCAP e report al mutatore separato, nuova cattura, stessa DSL e stesso verificatore. Tre esempi documentati, riepilogo 13/13 e nota sui due scenari non completati.

Le slide 1, 2, 4, 5 e 6 sono statiche. Solo la slide 3 cambia stato con due clic. Non ci sono autoplay o comparsate per singola riga.

## Controlli effettuati

- Controllati visivamente gli stati iniziale e finale di tutte le slide e i tre stati della slide 3 tramite rendering SVG. Confrontata la copertina con la sorgente originale.
- Verificati sintassi NRF e ruolo del report baseline nel codice del mutatore NRF. Risultati ed esempi sono tracciati nelle fonti delle note.
- Controllati i totali: dieci catture Open5GS più sei free5GC; 12 PASS più un FAIL più tre INCONCLUSIVE; 13 scenari di mutazione completati.
- Testato automaticamente il codice di navigazione: sei slide, due avanzamenti interni, percorso avanti/indietro, tastiera, selezione 1–6, ripristino URL, stato finale e barra di avanzamento. La stampa HTML seleziona gli stati finali.
- PPTX validato e reimportato, con sei slide e tabelle native nelle slide 5 e 6. I contenuti sono modificabili. La grafica di fondo della copertina è incorporata, con testi nativi.
- PowerPoint aperto e convertito tramite LibreOffice; controllate visivamente tutte le sei pagine del PDF. Microsoft PowerPoint non è disponibile in questo ambiente.
- Il PPTX è statico, con sei stati conclusivi. Il PDF contiene le stesse sei slide. Nessuna slide nascosta o aggiuntiva.
- Tempi indicativi: 10, 42, 70, 53, 50 e 60 secondi, totale 4:45. La prova orale reale resta necessaria.

## Perimetro

Pubblicazione limitata a `5g-thesis-presentation-5min/` sul branch `gh-pages`. Il confronto degli oggetti Git verifica che ogni percorso esterno, inclusa la presentazione da venti minuti, resti invariato. Non sono modificati tesi, verificatore o mutatori.
