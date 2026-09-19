PROMPT_ID=672841

Obiettivo unico: portare `chrome-codex-switcher` allo smoke test reale PASS end-to-end sul Fedora corrente.

Lavora SOLO su `/home/daniele/projects/chrome-codex-switcher`. Riusa tutto quanto già verificato in PROMPT_ID=519564; non rifare audit o esplorazione generale del repo.

Procedi autonomamente:

1. Aggiorna il checkout a `origin/main` e verifica che includa il merge `f63f28dfe35293ac4989773b86af6fc48a45b361`.
2. Esegui `./install.sh` e verifica `context-twin status`.
3. Sei esplicitamente autorizzato a usare/interagire con Chrome per caricare o ricaricare l'estensione unpacked da:
   `/home/daniele/.local/share/chrome-codex-switcher/extension`
   Usa il metodo meno invasivo disponibile. Non modificare/resetta il profilo Chrome e non eliminare dati.
4. Verifica che il companion GNOME sia installato e attivo. Prova ad abilitarlo direttamente se necessario. NON fare logout/reboot salvo assoluta impossibilità di proseguire.
5. Esegui un pairing reale tra una tab Chrome normale e il thread Codex attivo seguendo il workflow dell'app.
6. Smoke test reale **Chrome → Codex**: dalla tab Chrome associata, verifica che lo switch apra/focalizzi esattamente il thread Codex associato.
7. Smoke test reale **Codex → Chrome**: dal thread Codex associato usa “Copy chat deep link” e verifica che venga focalizzata esattamente la tab Chrome associata.
8. Verifica anche che pairing e mapping persistano dopo il test e che daemon/service restino sani.

Se incontri un problema:
- diagnostica SOLO il blocker concreto;
- applica il minimo fix necessario se è nel repo;
- reinstalla/ricarica solo ciò che il fix richiede;
- ripeti esclusivamente il test fallito;
- niente refactor, cleanup o miglioramenti fuori scope;
- niente retry identici senza nuova evidenza;
- non fermarti per chiedere conferme su operazioni non distruttive necessarie al test.

Test automatici già passati non vanno rieseguiti salvo modifica del relativo codice. Se tocchi codice, esegui soltanto i test mirati pertinenti e amplia solo in caso di failure.

Acceptance criteria:
- extension loaded/active;
- daemon/service healthy;
- clipboard backend attivo;
- pairing reale PASS;
- Chrome → Codex PASS;
- Codex → Chrome PASS;
- persistenza pairing PASS;
- nessun blocker residuo per il workflow core.

Termina immediatamente appena questi criteri sono verificati.

Prima riga del report finale obbligatoria:
`PROMPT_ID=672841`

Poi massimo:
`RESULT=PASS|BLOCKED`
`EXTENSION=...`
`BACKEND=...`
`PAIRING=...`
`CHROME_TO_CODEX=...`
`CODEX_TO_CHROME=...`
`PERSISTENCE=...`
`CHANGES=...`
`BLOCKER=none|...`
