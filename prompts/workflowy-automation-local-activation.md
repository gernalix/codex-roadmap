PROMPT_ID=330522 | project_id=96 | model=GPT-5.5 | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Attiva sul Fedora reale SOLO il layer locale già implementato in `gernalix/workflowy-importer`: CLI `wf`, bridge localhost e refresh periodico della cache. Installa anche le unità opzionali di backup/review, ma NON abilitarle automaticamente.

# Starting point autoritativo
- checkout canonico: `/home/daniele/projects/workflowy-importer`;
- branch: `main`, origin `https://github.com/gernalix/workflowy-importer`;
- baseline remota minima: `6e5b9090b9e8691673a22e3b0ef70e4b21bf1fea`;
- PROMPT_ID 693572 deve essere PASS prima di questo task; quindi il secret Workflowy canonico è già stato validato:
  `~/.config/codex/secrets/workflowy-api-key`;
- il codice, i test, i template in `deploy/systemd/` e la documentazione sono già nel repo: NON rifare progettazione o audit generale;
- non leggere la chiave in output e non copiarla in unità, log, Git o report.

# Esecuzione
1. `cd /home/daniele/projects/workflowy-importer`.
2. Verifica una sola volta branch/origin; `git fetch origin main && git merge --ff-only origin/main`. Se ci sono modifiche locali non sovrapposte, preservale; niente stash/reset distruttivi.
3. Verifica che la baseline minima sia antenata di HEAD.
4. Riusa `.venv`; esegui `.venv/bin/python -m pip install -q -e .`.
5. Esegui un solo gate host mirato:
   `.venv/bin/python -m unittest discover -s tests -v`.
6. Verifica le unità in `deploy/systemd/` con il controllo locale più economico disponibile. Correggi SOLO errori reali delle unità o del nuovo layer Workflowy.
7. Installa/copia le unità user in `~/.config/systemd/user/` senza toccare servizi non Workflowy; quindi `systemctl --user daemon-reload`.
8. Abilita/avvia SOLO:
   - `workflowy-bridge.service`;
   - `workflowy-cache-sync.timer`.
   Lascia installati ma DISABILITATI:
   - `workflowy-backup.timer`;
   - `workflowy-weekly-review.timer`.
9. Gate runtime minimi:
   - bridge attivo;
   - `GET http://127.0.0.1:8765/health` => stato ok;
   - una sola `.venv/bin/wf sync` completa con successo e crea/aggiorna la cache locale;
   - il timer cache risulta enabled/active.
10. Non creare nodi permanenti di prova e non eseguire dedupe/normalize/archive/PersonalHub link/apply/browser-extension.

# Recovery autonomo
Un failure intermedio non è terminale: leggi il minimo errore utile, applica il minimo fix in-scope, rilancia SOLO il gate fallito e riprendi dal punto successivo. Se il fix riguarda codice/template del repo, committa e pusha su `main` prima del PASS. Vietati retry identici senza nuova evidenza, audit generali, refactor o cleanup collaterali.

`BLOCKED` solo per hard blocker esterno (dipendenza 693572 non PASS, secret/permessi non disponibili, sessione systemd user indisponibile senza alternativa sicura). `FAIL` solo se gli acceptance criteria restano irraggiungibili dopo recovery locale ragionevole.

# Acceptance criteria
- `wf` installato nella venv del checkout canonico;
- test host PASS;
- unità user installate e valide;
- bridge localhost enabled/running e health PASS;
- cache-sync timer enabled/active;
- `wf sync` PASS;
- backup/review timer presenti ma non enabled;
- nessun segreto stampato o persistito fuori dal file canonico.

Dopo PASS finalizza UNA volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 330522 --confirm-executed`

Output massimo 6 righe:
`RESULT=PASS|BLOCKED|FAIL`
`TESTS=PASS|FAIL|NOT_RUN`
`BRIDGE=PASS|FAIL|NOT_RUN`
`CACHE_SYNC=PASS|FAIL|NOT_RUN`
`OPTIONAL_TIMERS=INSTALLED_DISABLED|FAIL|NOT_RUN`
`BLOCKER=<none|testo minimo>`
