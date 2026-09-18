PROMPT_ID=527184 | project_id=10 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Valida e distribuisci SOLO l'accesso SQL read-only autenticato del Data Explorer PersonalHub già integrato in `main` nel runtime `datasette5`, senza modificare l'API mobile di sync.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/datasette5`, project_id `10`, branch `main`;
- remoto: unico branch persistente `main`;
- HEAD remoto atteso: `b3fdddd3c7e6b8cbe35ba03aea982f17e7810a81`;
- commit funzionale già integrato: `be112dd9fee631fe64b28d1df6f1d7d080f36b2b`; i commit successivi hanno solo aggiunto/rimosso il workflow one-shot di branch cleanup;
- diff funzionale già delimitato a `scripts/personalhub_projection.py`, `tests/test_personalhub_projection.py`, `README.md`;
- policy già codificata: `personalhub_read` è visibile e interrogabile con `execute-sql` solo dall'actor umano `root`; anonimo negato; write/schema/mutazioni negate; `personalhub-sync` resta limitato al solo envelope tecnico;
- runtime canonico: Datasette 1.0a38, profilo Oracle privato esistente, `personalhub-projection.service` indipendente.

# Esecuzione minima
1. Preflight unico: worktree non in conflitto, branch `main`, un solo fetch di `origin/main`, fast-forward locale e requisito `HEAD=origin/main=b3fdddd3c7e6b8cbe35ba03aea982f17e7810a81`. Niente branch discovery, stash o rebase.
2. Leggi SOLO i tre file funzionali sopra e, se serve per gli argomenti esatti di deploy, la sola sezione Oracle del README. Niente audit repo-wide.
3. Esegui prima `tests.test_personalhub_projection.PersonalHubProjectionTest.test_datasette_native_clickable_fk_labels_and_read_only_permissions`. Se fallisce, correggi solo quel failure domain e rilancia solo quel test.
4. Dopo PASS mirato esegui una sola volta `python3 -m unittest tests.test_personalhub_projection -v` e `python3 launch_datasette.py --check`. Nessun test duplicato.
5. Se non hai modificato codice, non creare commit. Se una correzione strettamente necessaria è stata fatta, dopo i gate fai un solo fetch finale: se `origin/main` è avanzato rispetto allo starting HEAD => `BLOCKED`; altrimenti un solo commit/push diretto su `main`.
6. Usa il deploy Oracle canonico già documentato, col profilo privato esistente e senza mostrare secret. Non cambiare autenticazione, nginx, token o servizi non pertinenti.
7. Readback runtime bounded: actor umano autenticato può aprire `personalhub_read` ed eseguire una SELECT innocua; anonimo è negato; write SQL e mutazioni restano negate; un check read-only conferma che il route/envelope mobile esistente è ancora disponibile. Non inviare dati sintetici di produzione.
8. PASS => stop immediato. Nessun plugin nuovo, tuning, benchmark, schema redesign o audit post-PASS.

# Acceptance
PASS solo se test/suite/check PASS, `main` contiene la policy, runtime Oracle usa la configurazione aggiornata, SQL read-only autenticato funziona su `personalhub_read`, anonimo e ogni write sono negati e il sync mobile non è stato alterato.

# Non-goal
Niente modifiche PersonalHub Android, nuovi token, Tailscale/Cloudflare redesign, query salvate, plugin Datasette, benchmark, migrazioni DB o modifiche ai dati.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 527184 --confirm-executed`

Output massimo 6 righe: `RESULT`, `HEAD`, `TESTS`, `DEPLOY`, `ACCESS_POLICY`, `BLOCKER`.
