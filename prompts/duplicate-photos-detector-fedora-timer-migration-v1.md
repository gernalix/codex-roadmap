PROMPT_ID=970051
PROJECT_ID=102
REPO=gernalix/duplicate-photos-detector
MEGAVAULT=FAST

# Goal
Migra il runtime Fedora di duplicate-photos-detector dal vecchio processo always-on `grindr-photo watch` al nuovo servizio oneshot + timer periodico già presente su `main`. Non cambiare il matcher né aggiungere feature.

# Starting point
- Repo remoto autoritativo: `gernalix/duplicate-photos-detector`.
- `main` contiene già:
  - `systemd/duplicate-photos-detector-index.service.template`;
  - `systemd/duplicate-photos-detector-index.timer.template`;
  - rimozione del vecchio `duplicate-photos-detector-watch.service.template`.
- Il servizio oneshot esegue `grindr-photo index <archive> --db <db> --prune`.
- Il timer parte dopo 2 minuti e poi ogni 5 minuti.
- Archivio locale canonico: `~/Pictures/GrindrPhotos`.
- DB locale: `~/.local/share/duplicate-photos-detector/index.sqlite3`.
- Il precedente PROMPT_ID 817056 è storico/BLOCKED e non va riusato né modificato.

# Execution
1. Prima azione:
   `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 970051`
   Procedi solo se il claim diventa `running`; usa il worktree/repo path restituito come autoritativo per leggere il codice. Non modificare direttamente il checkout canonico.
2. Fai solo discovery locale mirata a:
   - stato dell'eventuale `duplicate-photos-detector-watch.service`;
   - eventuali unit locali correlate in `~/.config/systemd/user/`;
   - stato dell'archivio e del DB;
   - template systemd presenti nel current main/worktree.
   Niente audit generale del repository o di systemd.
3. Se il vecchio watcher è installato/abilitato/attivo:
   - `disable --now`;
   - rimuovi la vecchia unit locale solo se appartiene a questo progetto;
   - verifica che non rimanga alcun processo `grindr-photo watch`.
4. Installa le due nuove unit user dai template del repo, sostituendo i placeholder con i path locali reali:
   - `duplicate-photos-detector-index.service`;
   - `duplicate-photos-detector-index.timer`.
5. Esegui `systemctl --user daemon-reload` e `systemctl --user enable --now duplicate-photos-detector-index.timer`.
6. Avvia una sola run controllata del service e verifica che termini con successo. Conferma che:
   - il DB esista e sia leggibile;
   - l'indicizzazione incrementale funzioni;
   - `--prune` sia effettivamente nella ExecStart;
   - nessuna foto, DB, cache, embedding o diagnostica venga tracciata da Git.
7. Verifica `systemctl --user list-timers`/equivalente: il timer deve risultare enabled/active e avere una prossima attivazione coerente con ~5 minuti.
8. Se scopri un bug reale nei template/codice che impedisce la migrazione, applica SOLO il fix minimo nel worktree con test mirato. Niente refactor, cleanup o ottimizzazioni collaterali. Se il runtime passa senza modifiche sorgente, non creare commit.
9. Non installare OpenCLIP/FAISS, non ricalibrare soglie e non eseguire test di matching su foto private: sono fuori scope.
10. Dopo PASS finalizza e STOP:
    `python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 970051 --result PASS --confirm-executed`
    Per blocker esterno reale usa BLOCKED; per failure non recuperabile usa FAIL.

# Acceptance
PASS solo se:
- il vecchio watcher always-on non è più enabled/active e non esiste un processo `grindr-photo watch`;
- le nuove unit locali derivano dai template correnti di `main`;
- `duplicate-photos-detector-index.timer` è enabled/active;
- una run manuale del oneshot termina con successo;
- la prossima run è pianificata a circa 5 minuti;
- ExecStart usa `index ... --prune`;
- DB locale presente, nessun dato privato tracciato;
- git resta pulito salvo un fix sorgente realmente necessario e mirato.

# Stop
Dopo aver verificato gli acceptance criteria, finalizza immediatamente. Output finale max 8 righe:
PROMPT_ID
RESULT
OLD_WATCHER
TIMER
ONESHOT
DB
GIT
BLOCKER