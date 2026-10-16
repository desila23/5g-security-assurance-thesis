# OpenAPI: dove si trova e come modificarlo

**Slide 5, pannello sinistro più piccolo, come analogia esterna.** Il pannello destro, più ampio, presenta il linguaggio progettato per la tesi e i suoi due compiti: selezione delle evidenze e verifica dei criteri.

L'esempio OpenAPI introduce l'idea di un linguaggio specifico del dominio attraverso una descrizione di API HTTP. Il frammento è didattico e minimo: documenta un'operazione `GET /nf-instances` con una risposta `200`. Non è una trascrizione della specifica completa di un servizio 3GPP.

## I tre file da conoscere

| Contenuto | File |
|---|---|
| YAML mostrato a schermo | `esempi/openapi-esempio.yaml` |
| Posizione e dimensioni del pannello | `slides/05-dsl.html` |
| Font, dimensione e interlinea del codice | `css/openapi.css` |

Nel file HTML cerca `openapi-example-panel`, poi `openapi-example`. Il segnaposto `{{OPENAPI_EXAMPLE}}` viene sostituito con il testo YAML da `build.py`.

## Esempio di modifica

Per cambiare la descrizione della risposta, apri il YAML e modifica `description: OK`. Salva e avvia `RICOMPILA.bat` su Windows o `RICOMPILA.command` su Mac. Poi aggiorna il browser.

Mantieni l'indentazione del YAML. La chiave del codice HTTP rimane una stringa, per esempio `"200"`. Se aggiungi molte righe, aumenta l'altezza del `foreignObject` nell'HTML oppure riduci font e interlinea nel CSS.

## Perché è qui

La slide 4 separa le regole dalla logica del verificatore. La 5 risponde alla domanda «Come rappresentiamo queste regole?» e introduce la DSL progettata. L'esempio OpenAPI è un richiamo concreto all'idea di descrivere un dominio con una sintassi dedicata. La slide 9 approfondisce poi i costrutti usati nei test SCAS.

La risposta `200` dell'esempio OpenAPI documenta una risposta possibile dell'API. Il criterio `REQUIRE response.status == 403` mostrato successivamente riguarda invece uno specifico test NRF.

## Riferimento

[OpenAPI Specification 3.0.3](https://spec.openapis.org/oas/v3.0.3): descrizione delle API HTTP, campi obbligatori `openapi`, `info`, `paths`, operazioni e risposte. L'esempio è stato scritto per questa presentazione e controllato sui campi obbligatori di questa versione.
