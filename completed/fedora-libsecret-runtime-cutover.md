PROMPT_ID=729462 | project_id=92 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Completa il cutover libsecret/Secret Service per i due soli servizi Fedora user-session già preparati da ChatGPT: `gernalix/github-autosync` e `gernalix/activity-watch-uploader`. Elimina i sink custom di segreti plaintext dove è sicuro farlo, senza sacrificare l'esecuzione con systemd --user/linger e senza mai mostrare token o Push URL completi.

# Starting point autoritativo
- github-autosync main include almeno `cb5c199398e4a8184a73beacbced7625503299f6`: runtime order = env esplicito -> Secret Service (`application=github-autosync credential=github-reconcile-push-url`) -> systemd credential -> legacy file. `configure_kuma.py` è il solo writer legacy rimasto.
- activity-watch-uploader main include almeno `b5c2a7c52f3ff4d840fcc31ce41eaece7e63c9b7`: lookup Secret Service (`application=activity-watch-uploader credential=kuma-push-url`), setter via stdin e fallback legacy `KUMA_PUSH_URL`.
- workflowy-importer è già conforme e NON va toccato.
- Nessun venv. Usa solo Python/pacchetti globali. Non fare un nuovo audit generale dei repository.

# Esecuzione minima
1. Parti dai due file direttamente pertinenti: `github-autosync/configure_kuma.py` + test credential esistenti; per activity-watch-uploader usa il codice già merged e modifica sorgenti solo se una verifica mirata dimostra un difetto reale.
2. Verifica una sola volta che `secret-tool`/libsecret sia disponibile. Se manca, installa il pacchetto Fedora di sistema minimo necessario; niente librerie Python/keyring alternative.
3. github-autosync:
   - sostituisci il writer plaintext di `configure_kuma.py` con `secret-tool store`/Secret Service usando gli attributi già definiti dal reader;
   - passa il segreto esclusivamente su stdin, mai argv/log/output;
   - aggiungi solo i test mirati necessari;
   - non stampare mai token, URL completa o output di `secret-tool lookup`.
4. Migra i valori runtime esistenti nei due item Secret Service senza rigenerare token Kuma e senza copiarli in /tmp. Riusa i valori attuali in memoria/process pipe; nessun echo terminale.
5. Verifica dal vero contesto systemd --user che entrambi i servizi riescano a leggere la credenziale. Poiché i timer usano/possono usare linger, NON assumere che Secret Service sia disponibile prima del login:
   - testa il contesto reale del user manager in modo non distruttivo;
   - se non puoi dimostrare affidabilità pre-login, conserva un fallback boot-safe standard systemd e rimuovi il segreto dall'EnvironmentFile/custom parsing quando possibile;
   - preferisci `LoadCredentialEncrypted=` se supportato e verificato su questo host; altrimenti mantieni temporaneamente il fallback protetto già esistente. Non peggiorare l'availability solo per eliminare il file.
6. activity-watch-uploader: dopo import in Secret Service, rimuovi `KUMA_PUSH_URL` dal file env SOLO se il servizio/timer ha un provider boot-safe verificato. Mantieni nello stesso env soltanto configurazione non segreta.
7. github-autosync: rimuovi `LoadCredential=reconcile.env:...` e il legacy file SOLO se il percorso Secret Service/boot-safe sostitutivo è verificato. In caso contrario lascia il fallback ma assicurati che libsecret sia la prima fonte e documenta il motivo operativo.
8. Verifica mirata, senza audit ridondanti:
   - test credential dei due repo;
   - `python3 -m py_compile` solo dei Python modificati;
   - `bash -n` solo degli shell modificati;
   - `systemd-analyze --user verify` solo delle unit coinvolte;
   - un run controllato per ciascun servizio e stato timer/service/journal, senza mostrare segreti;
   - conferma heartbeat Kuma solo come esito booleano/HTTP, mai con URL/token.
9. Commit/push solo modifiche in scope secondo il normale workflow repo-task/PR. Nessun refactor, cleanup, modernizzazione, scansione secrets generale o modifica di altri repo.
10. Se trovi un problema collaterale non bloccante, segnalalo senza investigarlo. Dopo acceptance PASS, STOP immediato.

# Acceptance
PASS se:
- github-autosync non scrive più nuove credenziali Kuma in plaintext tramite `configure_kuma.py`;
- entrambi i runtime preferiscono Secret Service/libsecret e i due item sono realmente presenti/leggibili;
- nessun segreto compare in argv, stdout/stderr, journal o diff Git;
- entrambi i servizi funzionano con test/runtime mirati;
- il supporto a linger non viene rotto: eventuale fallback residuo è standard, minimo e motivato da una verifica concreta;
- test/compile/shell/systemd verify pertinenti PASS.

# Stop
Finalizza una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 729462 --result PASS --confirm-executed`

Output finale massimo 8 righe: RESULT, GITHUB_AUTOSYNC, ACTIVITY_WATCH, SECRET_SERVICE, LINGER_FALLBACK, TESTS, RUNTIME, COMMIT_PR.
