PROMPT_ID=886300

# Obiettivo
Correggi il gap sistemico del finalizer C2 per i task che modificano `gernalix/codex-roadmap`.

# Starting point verificato
- `c2_prepare_codex.py` crea correttamente worktree isolati `task/<PROMPT_ID>` per codex-roadmap senza usare `repo_single_writer.start-roadmap`.
- Il lato finish è incoerente: `roadmap_finish.py` finisce per usare il percorso generico `github-autosync repo_single_writer finish-any`, ma `repo_single_writer` non ha/crea task record per codex-roadmap.
- Questo produce `repo_integration_task_record_missing` e blocca almeno 528123 e 340495.
- 528123 ha PR #1614 già merged; 340495 ha codice/test già verificati nel proprio branch. Non rifare quel coding.
- 891963 resta storico BLOCKED immutabile; non tentare di convertirlo a completed.

# Lavoro
1. Riproduci il failure con test mirato.
2. Implementa il percorso canonico dedicato end-to-end per integrare/finalizzare task codex-roadmap, mantenendo single-writer/fencing/exact-tested-head/fail-closed.
3. Non alterare il comportamento per repo esterni.
4. Test focused-first; amplia solo quanto necessario.
5. Poiché questo leaf modifica proprio codex-roadmap, risolvi anche il bootstrap: usa il nuovo percorso dal worktree per integrare in sicurezza il proprio exact tested head, poi verifica il commit su main.
6. Dopo il merge, riconcilia il blocker `repo_integration_task_record_missing` di 528123 e 340495 senza rieseguire la loro implementazione già verificata.
7. Aggiorna C2 tramite protocollo normale; incidental bugs solo Inbox.

# Stop
Termina appena acceptance è provata. Report finale conciso con RESULT, test, commit/merge e stato 528123/340495.
