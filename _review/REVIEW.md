# Revisione documento - istruzioni per l'AI

Progetto: `C:\Users\samu1\Downloads\Tesi_5G_LaTeX_REV022\Tesi_5G_LaTeX`  ·  file principale: `main.tex`  ·  generato: 2026-10-21 11:28

Revisioni aperte: **1** (totali: 1). Dati completi in `_review/review.json`.

## Come procedere

1. Per ogni revisione qui sotto, apri il file `.tex` indicato e localizza il punto usando **`Sorgente ancorato`** come stringa esatta (old_string). Il numero di riga e' indicativo: se il file e' cambiato, cerca per testo. Se manca il sorgente ancorato, usa `Testo nel PDF` e la riga SyncTeX.
2. Applica l'**azione** richiesta (vedi legenda) con la modifica *minima* necessaria. Preserva comandi LaTeX, `\ref`, `\cite`, `\label`, ambienti e formattazione. Mantieni lo stile accademico italiano della tesi.
3. Dopo ogni revisione aggiorna l'item corrispondente (stesso `id`) in `review.json` (stessa cartella di questo file): `"status": "done"` (oppure `"skipped"` se non applicabile/ambigua) e `"ai_note"`: breve descrizione di cosa hai fatto o del dubbio. Non modificare gli altri campi.
4. Se un'indicazione richiede contenuti che non conosci (dati, fonti), NON inventare: `skipped` + spiegazione in `ai_note`.
5. **Revisioni marcate `PROPONI ALTERNATIVE`: NON modificare il file.** L'autore vuole scegliere lui. Scrivi in `review.json`, nello stesso item:
   `"status": "proposed"` e `"proposals": [{"text": "...", "why": "..."}, ...]` con **3 alternative davvero diverse tra loro**
   (es. una piu' concisa, una piu' formale/precisa, una ristrutturata), ciascuna pronta da sostituire al testo ancorato
   (stesso markup LaTeX, `\cite`/`\ref` preservati) e con `why` = una frase sul perche' funziona meglio. In `ai_note` puoi aggiungere
   un breve commento su cosa non andava nell'originale. Se l'item ha `Proposte gia' scartate`, proponi strade diverse da quelle.
6. **Anche senza quel marcatore**, se l'indicazione e' vaga o soggettiva (es. "non mi piace", "suona male", "poco chiaro", "migliorare")
   e non dice cosa scrivere, **non decidere tu**: comportati come al punto 5 e proponi alternative.
7. Alla fine riassumi in chat le revisioni saltate, dubbie o con proposte da scegliere. Non ricompilare a meno che non sia richiesto.

### Legenda azioni

- **SOSTITUISCI** (`replace`): Sostituisci il testo ancorato con il nuovo testo indicato.
- **ELIMINA** (`delete`): Elimina il testo ancorato (sistema punteggiatura/raccordo se serve).
- **INSERISCI DOPO** (`insert`): Inserisci il testo indicato subito dopo il testo ancorato.
- **RIFORMULA** (`rewrite`): Riscrivi il testo ancorato mantenendone il significato, seguendo l'indicazione.
- **COMMENTO** (`comment`): Osservazione libera: decidi tu l'intervento minimo che la risolve.
- **CITAZIONE** (`cite`): Serve/va corretta una citazione: usa chiavi esistenti in references.bib; se non esiste una fonte adatta NON inventarla, segnala in ai_note.
- **VERIFICA** (`check`): Verifica correttezza/coerenza (fatto, numero, termine, riferimento). Modifica solo se l'errore e' certo, altrimenti riporta in ai_note.
- **SPOSTA** (`move`): Sposta il testo ancorato subito DOPO il testo di destinazione indicato (sistema i raccordi in entrambi i punti).
- **IMPAGINAZIONE** (`layout`): Problema di layout (figura/tabella fuori posto, testo che esce dal margine, spazio vuoto, titolo isolato a fine pagina, salto pagina...). Intervieni sull'impaginazione, NON riscrivere il testo: opzioni di posizionamento dei float ([htbp], \FloatBarrier), \resizebox/\adjustbox o larghezze relative per tabelle e figure, \clearpage/\newpage, \needspace o \nopagebreak per i titoli, sillabazione con \hyphenation o \-, \sloppy/\emergencystretch locali. Preferisci la modifica piu' piccola e locale; non cambiare l'impostazione globale del documento senza segnalarlo in ai_note.
- **MI PIACE** (`like`): Passaggio che piace all'autore: NON e' una revisione e non va modificato; usalo come riferimento di stile.
- **MODIFICA DIRETTA** (`edit`): Modifica gia' applicata a mano dall'autore: non fare nulla.
- **NOTA GENERALE** (`general`): Nota non ancorata a un punto preciso: applicala dove pertinente.


## `capitoli/01_capitolo.tex`

### R001 · SOSTITUISCI · `capitoli/01_capitolo.tex:4` · pag. PDF 4

- **Testo nel PDF:** «L’evoluzione delle reti mobili verso la quinta generazione ha introdotto un’architettura di rete più articolata rispetto alle precedenti. Un elemento centrale di questa architettura è il 5G Core, organizzato in diversi componenti, denominati Network Functions (NF), che cooperano per fornire i servizi della rete. Questa organizzazione offre maggiore flessibilità, ma rende anche più complessa la valutazione della sicurezza, poiché è necessario considerare sia il comportamento delle singole funzioni sia le loro interazioni. Per supportare tale valutazione, il 3GPP ha definito le Security Assurance Specifications (SCAS) [1, 2], documenti tecnici che raccolgono requisiti di sicurezza e procedure di test specifiche per le diverse funzioni della rete. Queste specifiche costituiscono un riferimento per verificare la conformità dei comportamenti osservati rispetto a quanto previsto dagli standard. La disponibilità di una procedura ben definita, tuttavia, non rende necessariamente immediata la valutazione del suo esito. La difficoltà deriva dal fatto che i criteri sono formulati prevalentemente in linguaggio naturale, mentre le catture di traffico contengono informazioni che devono essere interpretate e correlate. Per rendere automatizzabile questa valutazione, occorre rappresentare i criteri in una forma strutturata, interpretabile da un sistema software. Il presente lavoro affronta questa difficoltà proponendo un Domain-Specific Language (DSL), pensato per esprimere in forma dichiarativa i criteri necessari a verificare gli esiti delle prove SCAS. Il contributo principale non consiste nell’automatizzazione di una singola procedura di test, ma nella separazione tra la descrizione dei criteri di verifica e il codice che li valuta. Anziché incorporare le condizioni di ciascun test in una logica applicativa dedicata, la soluzione proposta permette di specificarle attraverso regole DSL interpretate da un motore comune, riutilizzabile tra casi di test differenti. A partire dalle catture di traffico prodotte durante prove già eseguite, il sistema sviluppato utilizza le regole definite nella DSL per individuare le evidenze rilevanti e stabilire se i criteri previsti siano soddisfatti, determinando così un verdetto e documentando in un report gli elementi su cui tale verdetto si basa. La soluzione è stata infine valutata su diversi test case SCAS, anche attraverso esperimenti di mutation testing, nei quali vengono introdotte alterazioni controllate nelle catture originali per esaminare la capacità del sistema di rilevarne gli effetti sui risultati»
- **Sorgente ancorato** (confidenza 0.99):

```latex
L'evoluzione delle reti mobili verso la quinta generazione ha introdotto un'architettura di rete più articolata rispetto alle precedenti. Un elemento centrale di questa architettura è il \emph{5G Core}, organizzato in diversi componenti, denominati \emph{Network Functions} (NF), che cooperano per fornire i servizi della rete. Questa organizzazione offre maggiore flessibilità, ma rende anche più complessa la valutazione della sicurezza, poiché è necessario considerare sia il comportamento delle singole funzioni sia le loro interazioni.

Per supportare tale valutazione, il 3GPP ha definito le \emph{Security Assurance Specifications} (SCAS) \cite{3gpp_ts33117_2019,gsma_fs13_2025}, documenti tecnici che raccolgono requisiti di sicurezza e procedure di test specifiche per le diverse funzioni della rete. Queste specifiche costituiscono un riferimento per verificare la conformità dei comportamenti osservati rispetto a quanto previsto dagli standard.

La disponibilità di una procedura ben definita, tuttavia, non rende necessariamente immediata la valutazione del suo esito. La difficoltà deriva dal fatto che i criteri sono formulati prevalentemente in linguaggio naturale, mentre le catture di traffico contengono informazioni che devono essere interpretate e correlate. Per rendere automatizzabile questa valutazione, occorre rappresentare i criteri in una forma strutturata, interpretabile da un sistema software.


Il presente lavoro affronta questa difficoltà proponendo
un \emph{Domain-Specific Language} (DSL), pensato per
esprimere in forma dichiarativa i criteri necessari a
verificare gli esiti delle prove SCAS. Il contributo
principale non consiste nell'automatizzazione di una
singola procedura di test, ma nella separazione tra
la descrizione dei criteri di verifica e il codice
che li valuta. Anziché incorporare le condizioni
di ciascun test in una logica applicativa dedicata,
la soluzione proposta permette di specificarle
attraverso regole DSL interpretate da un motore
comune, riutilizzabile tra casi di test differenti.
A partire dalle catture di traffico prodotte durante prove già eseguite, il sistema sviluppato utilizza le regole definite nella DSL per individuare le evidenze rilevanti e stabilire se i criteri previsti siano soddisfatti, determinando così un verdetto e documentando in un report gli elementi su cui tale verdetto si basa. La soluzione è stata infine valutata su diversi test case SCAS, anche attraverso esperimenti di \emph{mutation testing}, nei quali vengono introdotte alterazioni controllate nelle catture originali per esaminare la capacità del sistema di rilevarne gli effetti sui risultati.
```
- **Nuovo testo:**

```
L'evoluzione delle reti mobili verso la quinta generazione ha introdotto un'architettura più articolata, composta da diverse funzioni di rete che cooperano per fornire i servizi del sistema. In questo contesto, la verifica della sicurezza assume un ruolo importante ed è supportata dalle \emph{Security Assurance Specifications} (SCAS), che definiscono requisiti e procedure di test per valutare specifiche proprietà di sicurezza \cite{3gpp_ts33117_2019,gsma_fs13_2025}. Tuttavia, determinare l'esito di una prova a partire dalle catture di traffico non è sempre immediato: i criteri di verifica sono descritti in linguaggio naturale, mentre le evidenze necessarie possono essere distribuite tra messaggi e protocolli differenti.

Il presente lavoro affronta questo problema proponendo una \emph{Domain-Specific Language} (DSL) che permette di esprimere i criteri di verifica in forma dichiarativa, separandoli dalla logica del software che li valuta. Il sistema sviluppato seleziona gli eventi rilevanti dalle catture di traffico, applica le regole specificate e produce un report contenente il verdetto e le evidenze che lo giustificano. La soluzione è stata valutata su diversi casi SCAS e attraverso esperimenti di \emph{mutation testing}, nei quali vengono introdotte alterazioni controllate nelle catture per verificare la capacità del sistema di rilevare le modifiche apportate.
```
