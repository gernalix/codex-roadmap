# GitHub autosync — Fedora migration to dedicated repo

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

PROMPT_ID: 684215

**Modello consigliato:** GPT-5.5  
**Reasoning:** low  
**MegaVault:** FAST

## Goal

Migrare sul Fedora l'autosync dei repository `gernalix` dal vecchio ownership in `codex-usage-monitor` al nuovo repository dedicato `gernalix/github-autosync`, senza lasciare due timer concorrenti e senza perdere le protezioni gia' esistenti.

Stato remoto autorevole gia' preparato:

- nuovo repo: `https://github.com/gernalix/github-autosync`;
- checkout canonico richiesto: `/home/daniele/projects/github-autosync`;
- contiene `github_autosync.py`, test e `systemd/github-autosync.service/.timer`;
- `gernalix/codex-usage-monitor` non contiene piu' `github_autosync.py`, `tests/test_github_autosync.py` o `systemd/codex-github-autosync.*`;
- nuovo timer: `github-autosync.timer`, ogni 5 minuti, `Persistent=true`;
- il nuovo script conserva intenzionalmente il lock/state path `/home/daniele/.local/state/codex-github-autosync`, cosi' vecchio e nuovo processo condividono lo stesso lock durante la migrazione.

Non riprogettare l'autosync: questo task e' la migrazione/installazione Fedora del nuovo ownership remoto gia' predisposto.

## Procedura

1. Verifica lo stato reale dei vecchi user unit `codex-github-autosync.service` e `codex-github-autosync.timer`.
2. Prima di installare/avviare i nuovi unit, disabilita e ferma il vecchio timer e ferma l'eventuale vecchio service. Da quel momento non deve piu' poter partire una nuova esecuzione legacy.
3. Porta il nuovo repo in `/home/daniele/projects/github-autosync`:
   - se manca, clonalo da `https://github.com/gernalix/github-autosync.git`;
   - se esiste gia', verifica che `origin` sia quello atteso e aggiornalo solo con fast-forward sicuro;
   - se il worktree e' dirty, ahead o diverged, non reset/stash/forzare: `RESULT=BLOCKED` con stato preciso.
4. Verifica il checkout remoto corrente e lancia solo i test pertinenti:
   - `python3 -m py_compile github_autosync.py`;
   - `python3 -m unittest discover -s tests`.
5. Installa i nuovi file `systemd/github-autosync.service` e `.timer` in `~/.config/systemd/user/`, quindi `systemctl --user daemon-reload`.
6. Abilita e avvia `github-autosync.timer`.
7. Esegui una sola run reale controllata di `github-autosync.service` e verifica exit success/journal. Non eseguire loop manuali o run ripetute equivalenti.
8. Verifica che la prima run gestisca anche `github-autosync` come repo `gernalix` e che MegaVault lo rappresenti esattamente una volta con un `project_id` permanente e repository/worktree canonico `/home/daniele/projects/github-autosync`. Se e' gia' registrato, accetta l'idempotenza; non creare duplicati.
9. Solo dopo che il nuovo timer/service e' verificato, rimuovi gli eventuali file user-unit legacy `codex-github-autosync.service/.timer` da `~/.config/systemd/user/`, fai `daemon-reload` e verifica che il vecchio timer non sia enabled/active. Non toccare altri unit Codex.
10. Verifica infine:
    - `github-autosync.timer` enabled + active e con prossima esecuzione prevista;
    - `github-autosync.service` punta a `/home/daniele/projects/github-autosync/github_autosync.py`;
    - nessun `codex-github-autosync.timer` legacy puo' partire;
    - il checkout locale del nuovo repo e' sincronizzato con `origin/main`;
    - `codex-usage-monitor` resta separato dall'autosync e non vengono ripristinati i file rimossi.

## Vincoli

- Fedora soltanto; non toccare Oracle VM.
- Nessun `reset --hard`, force-push, auto-stash o cancellazione di repo locali.
- Non usare `ghorg --prune` o altre opzioni distruttive.
- Non modificare PersonalHub.
- Non ricreare codice autosync dentro `codex-usage-monitor`.
- Se i test del nuovo repo falliscono per un bug concreto, correggi il minimo necessario solo in `github-autosync`, test, commit/push e poi riprendi la migrazione.
- Non iniziare il task successivo della roadmap.

## Acceptance criteria

PASS solo se:

- `/home/daniele/projects/github-autosync` esiste ed e' il clone corretto sincronizzato con `gernalix/github-autosync`;
- test mirati del nuovo repo passano;
- `github-autosync.timer` e' installed, enabled e active con cadenza 5 minuti e `Persistent=true`;
- una run reale di `github-autosync.service` termina con successo;
- il service esegue lo script dal nuovo repo, non da `codex-usage-monitor`;
- `codex-github-autosync.timer` legacy e' disabilitato/inattivo e i vecchi user-unit non sono piu' la sorgente operativa;
- non esistono due autosync concorrenti;
- MegaVault contiene `github-autosync` una sola volta con `project_id` permanente e worktree canonico corretto;
- nessun repo dirty/ahead/diverged e' stato sovrascritto o forzato;
- `codex-usage-monitor` resta privo dei file autosync spostati;
- operazioni terminali roadmap completate e poi STOP.

## Output finale

- `PROMPT_ID=684215`
- `RESULT=PASS|BLOCKED|FAIL`
- `clone_status=` path + HEAD
- `new_timer=` enabled/active + next run
- `legacy_timer=` disabled/inactive/not-found come applicabile
- `service_run=PASS|FAIL`
- `megavault_registration=` project_id + duplicate_count
- test eseguiti
- eventuale commit SHA `github-autosync` solo se e' stato necessario correggere codice
- blocker reale, se presente
