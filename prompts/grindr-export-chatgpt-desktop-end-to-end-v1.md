PROMPT_ID=556372 | MegaVault=FAST
WORKDIR=/home/daniele/projects/grindr-export

# Goal
Prendi in carico in ChatGPT Desktop l'intero workflow di `gernalix/grindr-export` senza chiedermi di eseguire comandi manualmente: prepara il checkout locale canonico, registra il nuovo repo in MegaVault, valida codice/test, usa la sessione Grindr Web reale già autenticata quando disponibile, acquisisci la conversazione attualmente aperta/selezionata, genera l'archivio offline e verifica end-to-end gli output.

# Starting point autoritativo
- remoto già pronto: `https://github.com/gernalix/grindr-export`, branch `main`;
- main contiene `grindr_dom_archive.py`, `GRINDR_EXPORT_MINIPROMPT.md`, `README.md`, `.gitignore` e 3 test stdlib;
- commit d'integrazione noto: `6b77ac5d215b872353f28c2756bf501e110ee432`;
- il transcript storico allegato NON deve entrare in Git;
- export utente sotto `/home/daniele/Documents/ChatGPT/Pixel 8a/grindr_archive/`;
- Python globale; venv/virtualenv/poetry/uv vietati;
- `grindr-export` non è ancora registrato nel `megavault.sqlite` canonico;
- PROMPT_ID=354882 lavora sul diverso repo `grindr-web-exporter` e condivide la stessa risorsa browser/Grindr: questo task parte solo dopo la sua finalizzazione, come imposto dalla dependency della roadmap. Non riaprire o correggere 354882.

# Esecuzione
1. Prima azione: `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 556372`. Procedi solo se conferma `running`.
2. Porta il repo locale a `/home/daniele/projects/grindr-export` dal remoto canonico. Se già presente, riusalo: niente secondo clone. Verifica che `main` corrisponda al remoto senza distruggere modifiche locali.
3. Registra il repository in MegaVault usando il CLI canonico del checkout `/home/daniele/projects/MegaVault`. Usa `register-github-repo` con owner `gernalix`, nome `grindr-export`, remote URL, default branch `main` e worktree canonico. Leggi poi il project_id assegnato dal DB/CLI e verifica che repo/path siano risolvibili. Non inventare project_id e non creare registri paralleli.
4. Esegui i test mirati già presenti:
   `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`.
   Se falliscono per un bug reale del repo, correggi il minimo necessario nello stesso task; se serve modificare Git, usa il flusso single-writer/repo-task previsto dal protocollo. Niente refactor/cleanup fuori scope.
5. Controlla la sessione Chrome reale. Riusa una tab `web.grindr.com` già autenticata se esiste. Non chiudere il Chrome predefinito, non cancellare cookie/profili e non avviare loop di login.
6. Se esiste evidenza positiva di logout/login richiesto, chiedi UN SOLO handoff per il login nella stessa finestra e, appena autenticato, continua automaticamente. Assenza di un selettore o DOM inatteso non equivale a logout: diagnostica il DOM invece di chiedere un altro login.
7. Usa `GRINDR_EXPORT_MINIPROMPT.md` come specifica di acquisizione, ma esegui tu direttamente i passi: sulla conversazione Grindr attualmente aperta/selezionata raggiungi il marker/inizio disponibile, acquisisci `[data-testid="chat-container"]` con snapshot incrementali fino al fondo e salva `raw/dom_snapshots.json`. Non chiedermi di copiare/incollare prompt o lanciare script.
8. Per media usa solo normali asset browser/pageAssets. Non bypassare album privati, view-once, protezioni o URL firmati; registra come non esportabile ciò che non è normalmente acquisibile. Non salvare cookie, auth header, token, session secret o query string firmate.
9. Esegui direttamente:
   `python3 /home/daniele/projects/grindr-export/grindr_dom_archive.py "<ARCHIVE_DIR>"`
   sull'archive appena acquisito.
10. Valida davvero:
   - `raw/acquisition_summary.json`;
   - `archive.sqlite` con `PRAGMA integrity_check` e `PRAGMA foreign_key_check`;
   - coerenza conteggio messaggi JSON/CSV/SQLite;
   - `index.html` apribile offline e ricerca funzionante;
   - nessuna dipendenza remota attiva nel viewer;
   - nessun export/chat/media personale tracciato in Git.
11. Se il workflow reale smentisce una premessa (DOM Grindr cambiato, path diverso, helper non più valido), fai discovery solo mirata, correggi il minimo e riprendi il goal. Non creare follow-up per failure locali correggibili.
12. Se hai modificato il repo, completa il flusso single-writer e attendi l'integrazione canonica verificata. Se non hai modificato codice, lascia il checkout pulito e sincronizzato.
13. Dopo acceptance PASS, finalizza:
   `python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 556372 --result PASS --confirm-executed`
   e STOP.

# Acceptance
PASS solo se:
- checkout canonico `/home/daniele/projects/grindr-export` esiste ed è coerente col remoto;
- repo registrato nel MegaVault canonico con project_id reale e path risolvibile;
- test del repo PASS;
- una conversazione reale attualmente selezionata viene acquisita end-to-end senza loop di login;
- normalizzazione produce `messages.json`, `messages.csv`, `archive.sqlite`, `index.html`, `README.md` e `raw/acquisition_summary.json`;
- tutti i check di integrità passano; `PASS WITH WARNINGS` è ammesso solo per media/album non esportabili normalmente;
- nessuna credenziale, token, transcript o media personale finisce in Git/log/report;
- nessun passaggio terminale viene scaricato sull'utente salvo login/permesso realmente indispensabile.

# Non-goal
Esportare automaticamente tutte le chat senza un target selezionato, bypassare protezioni Grindr, riscrivere `grindr-web-exporter`, audit generale di Chrome/MegaVault/roadmap, nuovi daemon/monitor/dashboard.

# Output finale
Massimo 9 righe: RESULT, PROJECT_ID, REPO_STATE, TESTS, AUTH/LOGIN_HANDOFFS, ARCHIVE_DIR, MESSAGE_COUNTS, MEDIA_WARNINGS, BLOCKER.