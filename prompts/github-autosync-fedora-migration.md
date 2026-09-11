[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=684215 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Completa sul Fedora la migrazione dell'autosync da `codex-usage-monitor` al repo dedicato `gernalix/github-autosync`, senza doppio timer o perdita delle protezioni esistenti.

# Stato già verificato
- remoto nuovo: `https://github.com/gernalix/github-autosync`, checkout canonico `/home/daniele/projects/github-autosync`;
- contiene `github_autosync.py`, test e `systemd/github-autosync.service/.timer` (5 min, `Persistent=true`);
- `codex-usage-monitor` remoto non contiene più codice/unit autosync;
- vecchio e nuovo usano intenzionalmente lo stesso lock/state `/home/daniele/.local/state/codex-github-autosync`.

# Esegui
1. Leggi una volta lo stato dei vecchi `codex-github-autosync.*`; ferma/disabilita il timer legacy prima di avviare il nuovo.
2. Clona il nuovo repo se manca; se esiste, verifica `origin` e fai solo fast-forward sicuro. Dirty/ahead/diverged => BLOCKED, niente stash/reset.
3. Esegui solo `python3 -m py_compile github_autosync.py` e `python3 -m unittest discover -s tests`.
4. Installa `github-autosync.service/.timer` in `~/.config/systemd/user`, `daemon-reload`, enable+start timer.
5. Esegui UNA run reale del service; verifica exit/journal e che MegaVault rappresenti `github-autosync` esattamente una volta col worktree canonico.
6. Rimuovi i vecchi user-unit solo dopo il PASS del nuovo service; verifica che nessun autosync legacy possa più partire.

Non toccare Oracle VM, PersonalHub o altri unit. Nessun `reset --hard`, force-push, auto-stash o `ghorg --prune`. Se emerge un bug concreto nel nuovo repo, correggi solo quello, test, commit/push e riprendi.

# PASS
Richiede clone corretto e sync con `origin/main`, test PASS, nuovo timer enabled+active, una run service PASS, vecchio timer non avviabile, nessuna concorrenza, MegaVault senza duplicati e `codex-usage-monitor` ancora separato. Poi aggiorna roadmap e STOP.

Output: `PROMPT_ID`, `RESULT`, HEAD, stato timer nuovo/legacy, service run, MegaVault project_id+duplicate_count, test, eventuale fix SHA, blocker.
