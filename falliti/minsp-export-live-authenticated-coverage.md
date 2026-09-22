PROMPT_ID=682741
/goal

Porta `gernalix/minsp-export` fino a un export REALE, completo e verificato di tutto ciò che l'account autenticato Min Sundhedsplatform rende leggibile. Non considerare mai completato il goal dopo bootstrap, lettura file, setup o un singolo fix: continua finché tutti gli acceptance criteria sono verificati.

GPT-5.6 Sol, reasoning medium, MegaVault FAST. Repo unico: `gernalix/minsp-export`. Acquisisci il claim roadmap, usa il worktree assegnato e risolvi/registra il project_id reale in MegaVault. Nessun venv.

Autonomia: modifica codice, adapter, selector, seed route e normalizzazione quanto serve; usa Chrome/Playwright, DOM/accessibility tree, network inspection, SQLite, file locali e test. Installa dipendenze non segrete necessarie. Per ogni ostacolo tecnico raccogli evidenza, applica il minimo fix, rilancia solo il gate pertinente e prosegui. Selector/route mancanti, JS senza href, timeout, crash browser, lazy-load, download, parser, FTS/SQLite, resume, PDF, packaging, dipendenze installabili e test falliti NON sono BLOCKED. Niente retry identici senza nuova evidenza; niente audit/refactor fuori scope.

MitID resta manuale. Non automatizzare/bypassare/intercettare MitID; non leggere o salvare password, cookie, Authorization header o secret. Se serve login, apri/riusa il profilo Chrome persistente e chiedi solo all'utente di completare MitID; poi riprendi automaticamente dal checkpoint. Non inviare messaggi, prenotare/cancellare appuntamenti, richiedere refill, fare pagamenti o cambiare l'account. Ammessi solo flussi read-only: dettagli, tab, paginazione, “vis mere”, infinite scroll e download.

Ciclo fino a completion:
1. Inventaria tutte le sezioni/sottosezioni visibili: lab, note/journal, visite/ricoveri, imaging/referti, diagnosi, farmaci, allergie/CAVE, appuntamenti, messaggi read-only, procedure, questionari, documenti/PDF/allegati, provider/reparti e ogni altra categoria trovata.
2. Inventaria route, pulsanti senza href, modal, paginazione/lazy-load e XHR/fetch generati dalla UI.
3. Confronta inventario e cattura. Per ogni gap aggiungi il minimo adapter/selector/read-only flow e riprendi dal checkpoint.
4. Preserva ogni payload clinico utile anche HTML/XML/text/binary. Se una LETTURA usa POST, lascia che la UI read-only la generi e cattura la response; non costruire richieste rischiose a mano.
5. Esegui l'export fino a esaurimento. Interrompilo deliberatamente una volta dopo dati reali, riavvialo e prova resume + deduplicazione senza perdita.
6. Costruisci `normalized/health.sqlite` e `text/complete-medical-record.md`; verifica `PRAGMA foreign_key_check` vuoto, tabelle pertinenti, FTS/search su termine reale e un campione raw→normalized→search/Markdown.
7. Verifica che Git contenga solo codice/test/docs generici: mai export, DB sanitari, screenshot, profile, cookie o dati personali.

PASS solo se tutte le sezioni leggibili osservate sono catturate oppure marcate con motivo preciso come non esposte/non esportabili; paginazione/lazy-load sono esauriti; raw HTML/JSON/PDF/allegati hanno hash/manifest; resume reale è provato; SQLite/FTS/Markdown sono verificati; non restano failure retryable note; nessun dato sanitario/secret è in Git; nessuna azione mutativa è stata eseguita.

BLOCKED solo per hard blocker esterno non risolvibile localmente: MitID non completabile, account bloccato, portale persistentemente down, rete assente o permesso esterno indispensabile mancante. Prima salva checkpoint e prova recovery locali. FAIL solo per impossibilità tecnica dimostrata.

Finalizza una sola volta:
PASS: `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 682741 --confirm-executed`
BLOCKED/FAIL: usa `roadmap_result.py` con lo stesso prompt-id e risultato corretto.

Output finale max 10 righe: PROMPT_ID, RESULT, PROJECT_ID, COVERAGE, RAW, NORMALIZED, RESUME, SEARCH, TESTS, BLOCKER.