# Presentazione tesi 5G — versione 9, 21 slide

Estrai tutto lo ZIP e apri `index.html`. La presentazione funziona offline e per visualizzarla non serve Python.

Frecce, spazio e PageUp/PageDown: navigazione. I: indice; N: note; F: schermo intero; P: stampa/PDF. Le slide 4, 10, 11 e 12 hanno passi interni e «Vista completa».

Le slide 7 e 8 sono di nuovo separate. Il close-up interno della slide 12 resta disponibile, con durata 850 ms. Il cambio dalla 12 alla 13 è immediato. Nella 13 i due verificatori condividono un’area; una sola uscita si ramifica verso i tre verdetti. «Risultati delle verifiche» rimane eliminato.

Nella slide 5 OpenAPI è a sinistra, in un pannello secondario etichettato «Esempio esterno»; la DSL progettata è a destra, evidenziata come contributo della tesi. Sono ambiti diversi, accomunati dal ricorso a specifiche formali. YAML: `esempi/openapi-esempio.yaml`; HTML: `slides/05-dsl.html`; stile: `css/openapi.css`.

Sorgenti separati in `slides/`, `css/` e `js/`. La mappa completa è in `MODIFICA_SLIDE.md`. Dopo modifiche a HTML o YAML avvia `RICOMPILA.bat`, `RICOMPILA.command` o `python3 build.py`. Per questa operazione serve Python 3, senza pacchetti aggiuntivi. Dopo modifiche a CSS o JavaScript basta ricaricare il browser.

Il riepilogo delle modifiche correnti è `REVISIONE_V9.md`. Le richieste precedenti rimangono come riferimenti storici. Tutti i file scientifici in `data/` sono invariati.
