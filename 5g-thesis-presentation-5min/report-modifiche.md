# Revisione con sottotitoli e annotazioni del report UI

28 ottobre 2026.

## Modifiche

- Aggiunti i sottotitoli alle slide di contenuto, con l’eccezione dell’architettura proposta. La copertina originale conserva il proprio sottotitolo.
- Inserita dopo la Security Assurance la slide della rete 5G, riprendendo lo schema della presentazione lunga. La presentazione ha ora sette slide in totale.
- Prima fase SCAS/DSL: aggiunto un terzo ritaglio originale UDM, rimossa la dicitura «a mano» e mantenuta soltanto «PSEUDOCODICE ILLUSTRATIVO» sotto il codice. I ritagli non si sovrappongono al testo.
- Seconda fase: esempio NRF semplificato del capitolo 2 della tesi, con regioni blu e verdi per messaggi e criteri. Domande sulla destra: «Quali messaggi cercare?» e «Quali criteri verificare?».
- Terza fase: nello stesso riquadro compare la regola DSL reale; le domande restano fisse e le frecce sono invertite. Rimossa la precedente didascalia di contributo in basso.
- Architettura: ripresa la slide originale della versione lunga, eliminando le uscite intermedie laterali. Nessun sottotitolo e nessuna etichetta MonPoly: il riferimento resta nelle note orali.
- Baseline: mantenute le righe raggruppate, aggiunto a lato «16/16 verdetti attesi». Il conteggio comprende 12 PASS, un FAIL e tre INCONCLUSIVE, non 16 PASS.
- Aggiunto in fondo il riferimento alle catture NRF e UDM ottenute con componenti ScasDK adattati. La tesi documenta questa attribuzione: non viene estesa indistintamente a tutti i PCAP.
- Mutation testing: schema a sinistra, simile alla versione lunga, con un solo piccolo blocco della pipeline. Tabella a destra, 13/13 in evidenza e nota sui due casi non completati per limiti del mutatore.

## Controlli

Controllati visivamente tutti gli stati delle sette slide, compresi A/B/C della slide SCAS/DSL. Testato automaticamente il codice di navigazione avanti/indietro, tastiera 1–7, salti fra slide, stato finale e ripristino URL. Controllati i sottotitoli e la loro assenza nella pipeline, i tre ritagli e le due direzioni delle frecce.

PPTX validato, reimportato e convertito con LibreOffice. PDF di sette pagine renderizzato e controllato. Corretta l’intestazione della tabella di mutation testing perché non vada a capo. Il PPTX è statico, con testi e tabelle modificabili. La grafica originale degli schemi riutilizzati è incorporata con testi nativi. Microsoft PowerPoint non è disponibile in questo ambiente.

Tempi indicativi complessivi: 4:55. Non è una prova orale reale.

Pubblicazione limitata alla cartella `5g-thesis-presentation-5min/`. Il confronto degli oggetti Git verifica che la versione da venti minuti e ogni altro percorso restino invariati.
