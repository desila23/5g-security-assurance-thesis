# Revisione della presentazione da cinque minuti

Data: 28 ottobre 2026.

## Modifiche

- Tutte le slide sono complete all’apertura. I passaggi interni scendono da 19 a 3: una evidenziazione nelle slide 2, 3 e 5. Slide 1 e 4 statiche. Nessun autoplay.
- Slide 1: requisito atteso ed evidenze osservate convergono nella Security Assurance. Il caso 5G collega SCAS, Network Function e PCAP allo stesso schema.
- Slide 2: due ritagli originali dai PDF ETSI, attribuiti a 3GPP TS 33.512 V17.3.0, p. 9, e TS 33.518 V18.0.0, p. 8. Sono dettagli ritagliati, non trascrizioni ricostruite. Contrasto più marcato fra esecuzione specifica e verifica generalizzabile. Il codice è dichiarato pseudocodice Python di esecuzione.
- Slide 3: due sezioni esplicite, «DSL progettato» e «Sistema di verifica implementato». Conservate SEQUENCE e REQUIRE con la sintassi reale, pipeline, collegamento del DSL a selezione/verifica e MonPoly.
- Slide 4: conservati 16 baseline, 12 PASS, 1 FAIL e 3 INCONCLUSIVE. Sono visibili Open5GS, free5GC, indipendenza dei PCAP e attribuzione di ScasDK limitata alle prove NRF e UDM. Il FAIL NRF resta un esito atteso.
- Slide 5: confronto HTTP 200/FAIL e HTTP 403/PASS già presente all’apertura. Un clic sottolinea i valori e il PCAP mutato. Conservati 13/13 scenari completati e nota sui 15 previsti, con due AMF Case B temporale/combinato non completati per limiti del mutatore.

## Formati e controlli

- HTML offline con font e ritagli incorporati. Controllati visivamente i rendering SVG dello stato iniziale e dello stato evidenziato di tutte le slide.
- PowerPoint con testi e diagrammi modificabili. È intenzionalmente statico: nessun contenuto dipende da effetti non verificabili in Microsoft PowerPoint. I ritagli originali SCAS restano immagini.
- Controllati il pacchetto PPTX, le dimensioni, i caratteri e la reimportazione. Aperto e convertito con LibreOffice. PDF di cinque pagine renderizzato e controllato pagina per pagina.
- Test automatico del codice HTML di navigazione: avanti/indietro, tastiera, salti alle slide, tre evidenziazioni, estremi del percorso e barra di avanzamento sulle slide statiche. Tutti i testi e le immagini sono presenti allo stato zero.
- Controllati DSL e dati nel repository e nel capitolo 6 della tesi. Le fonti sono anche nelle note. La generazione automatica NLP non viene presentata come contributo realizzato.
- Tempi indicativi: 52, 48, 74, 48 e 68 secondi, per un totale di 4:50. Il discorso orale è conservato. La durata richiede una prova orale reale.
- Microsoft PowerPoint e una prova su proiettore non sono disponibili qui. Il controllo del PPTX è stato eseguito con LibreOffice e Artifact Tool, non in Microsoft PowerPoint.

## Pubblicazione

Aggiornamento limitato a `5g-thesis-presentation-5min/` sul branch `gh-pages`. Gli altri percorsi, inclusa la versione da venti minuti, devono mantenere gli stessi oggetti Git. Il confronto viene verificato prima del push.
