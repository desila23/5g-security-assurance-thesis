# Come è rappresentato il Match nella slide 12

Versione 8: gli indici Python sono spiegati qui, ma le due righe tecniche sono state tolte dal riquadro della slide. Il Match è stato ridotto mantenendo sequenza e associazioni degli alias.

Il flusso è **Matcher → Match → BindingContext**. La sequenza riconosciuta è un risultato del matcher.

Nell'esempio della slide precedente, il matcher riconosce gli eventi **A(3), B(4), C(6)**. I numeri tra parentesi sono le posizioni nella traccia didattica, numerate da 1. Non sono numeri di frame PCAP.

Il codice definisce `Match` con tre campi:

| Campo | Contenuto nell'esempio |
|---|---|
| `start_index` | `2`: indice Python dell'evento in posizione 3 |
| `end_index` | `5`: indice Python dell'evento in posizione 6, incluso |
| `bindings` | Una mappa da alias a oggetti `MessageEvent` |

La mappa associa:

| Alias della regola | Oggetto evento riconosciuto | Tipo didattico |
|---|---|---|
| `a` | A in posizione 3 | `event.a` |
| `b` | B in posizione 4 | `event.b` |
| `c` | C in posizione 6 | `event.c` |

Le tre tessere con A(3), B(4), C(6) riassumono la sequenza riconosciuta: non rappresentano un ulteriore campo chiamato `sequence`. La tabella sottostante rende esplicita la mappa `bindings`.

`to_binding_context()` costruisce un `BindingContext` con un nuovo dizionario che copia quelle associazioni. Gli oggetti evento sono gli stessi: non vengono trasformati né duplicati. Gli indici di inizio e fine restano nel Match e non diventano campi del BindingContext.

Il close-up mostra gli oggetti `MessageEvent` richiamati dagli alias e i campi che rimangono disponibili per le verifiche. La struttura generale di BindingContext può contenere anche collezioni e dizionari; questa slide illustra il caso di una sequenza con tre binding singoli.

## Fonte del controllo

Verificato sul branch `refactor/generic-pipeline`, commit `30a7cb4a04d3174485c73c3b336089abdba98162`:

- [Definizione di Match e BindingContext](https://github.com/desila23/5g-security-assurance-thesis/blob/30a7cb4a04d3174485c73c3b336089abdba98162/matcher/models.py)
- [Produzione dei Match nel matcher](https://github.com/desila23/5g-security-assurance-thesis/blob/30a7cb4a04d3174485c73c3b336089abdba98162/matcher/matcher.py)

Il controllo automatico registra anche che il dizionario è nuovo e i riferimenti agli eventi rimangono identici.
