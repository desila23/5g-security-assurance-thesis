REVISIONE LaTeX — 20 ottobre 2026

DOCUMENTO DI RIFERIMENTO
  Bozza_Tesi_DeSantis_Samuele 1 (1).pdf — 38 pagine
  Il progetto ZIP originale era una revisione precedente; il presente pacchetto
  e' una ricostruzione editoriale dai sorgenti disponibili, non il sorgente
  originale esatto da cui e' stato compilato il PDF da 38 pagine.

RICONCILIAZIONE DELLA VERSIONE PDF
  - Frontespizio aggiornato (ateneo, macroarea, relatrice/correlatore,
    matricola) e indice delle figure rimosso come nel PDF di riferimento.
  - Introduzione sostituita con il testo della versione PDF aggiornata.
  - Modifiche del capitolo 2 (citazioni e testo SCAS), capitolo 3
    (formulazione 3.2, punteggiatura), capitolo 4 (resolver/report),
    e ritocchi editoriali dei capitoli 5-6 recepiti.
  - Figure e riferimenti bibliografici esistenti conservati.
  Non e' garantita una riproduzione identica di impaginazione, microtipografia,
  punteggiatura e ritorni a capo rispetto al PDF originario: va ricontrollata.

NUOVE MODIFICHE TECNICHE
  - R7: evidenza insufficiente sia nella selezione che nella verifica statica.
  - 5.3: verifica dichiarativa degli alias usati in REQUIRE/IF (e i binding
    esterni/configurativi/derivati dichiarati); errori DSL separati dai verdetti.
  - 5.6: alias correttamente dichiarato, ma assente nel BindingContext =>
    criterio INCONCLUSIVE; proseguono le altre verifiche e gli IF annidati.
  - 5.8: due origini di INCONCLUSIVE e tabella completa di congiunzione
    PASS/FAIL/INCONCLUSIVE; SKIPPED neutro.
  - 4.7: reporter conserva cause dei binding mancanti a livello del criterio.
  - 6.2-6.4: separazione esperimenti originali free5GC da nuove catture Open5GS,
    con tabella A-D per RES* e nuovi esiti mutation A/AMF Sync; nuove mutazioni
    Open5GS Case B temporali non dichiarate completate.

ASPETTI DA RIVEDERE NELLA REVISIONE FINALE
  - La documentazione AMF Sync Case B e' da verificare rispetto alla formula
    temporale aggiornata nel software e al comportamento della nuova cattura.
  - Riesaminare i risultati sperimentali prima della consegna finale; non
    confondere tabelle delle baseline originali con le nuove Open5GS.
  - Controllare l'impaginazione di tabelle lunghe nel capitolo 6.
  - 'sorgente_markdown/' conserva bozze storiche NON sincronizzate con queste
    modifiche: utilizzare 'capitoli/*.tex' come sorgente autorevole.

COMPILAZIONE
  Dalla cartella Tesi_5G_LaTeX/ su macchina con LuaLaTeX e Biber:
    latexmk -lualatex -interaction=nonstopmode main.tex
  Compilazione di controllo eseguita con LuaLaTeX + Biber: OK; output 41 pagine.
  La differenza rispetto alle 38 pagine del PDF di riferimento riflette anche
  le nuove aggiunte e il reflow tipografico.
