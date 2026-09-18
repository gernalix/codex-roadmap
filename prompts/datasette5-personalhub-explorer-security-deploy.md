PROMPT_ID=527184 | project_id=10 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Valida e distribuisci SOLO il nuovo accesso SQL read-only autenticato del Data Explorer PersonalHub nel runtime `datasette5`, senza modificare l'API mobile di sync.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/datasette5`, project_id `10`;
- branch canonico: `main`;
- origin/main minimo atteso: `b3fdddd3c7e6b8cbe35ba03aea982f17e7810a81`; il commit funzionale `be112dd9fee631fe64b28d1df6f1d7d080f36b2b` deve esserne antenato;
- diff già delimitato a `scripts/personalhub_projection.py`, `tests/test_personalhub_projection.py`, `README.md`;
- policy desiderata già codificata: `personalhub_read` è visibile e interrogabile con `execute-sql` solo dall'actor umano `root`; anonimo negato; `execute-write-sql`, schema changes e mutazioni righe negati; `personalhub-sync` resta limitato al solo envelope tecnico;
- runtime canonico già documentato nel repo: Datasette 1.0a38, profilo Oracle privato esistente, `personalhub-projection.service` indipendente.

# Esecuzione minima
1. Preflight unico: worktree, un solo fetch main, fast-forward a origin/main e richiedi che `be112dd9...` sia antenato; dirty overlap/divergenza => BLOCKED, niente stash/reset/rebase.
2. Leggi SOLO i tre file del diff e gli helper di deploy già nominati nel README se necessari. Niente audit repo-wide.
3. Esegui prima il test mirato `tests.test_personalhub_projection.PersonalHubProjectionTest.test_datasette_native_clickable_fk_labels_and_read_only_permissions`. Se fallisce, correggi solo questo failure domain e rilancia solo quel test.
4. Dopo PASS mirato esegui una sola suite pertinente `python3 -m unittest tests.test_personalhub_projection -v` e `python3 launch_datasette.py --check`. Nessun test duplicato.
5. Nessuna integrazione branch è necessaria: il codice è già su main. Se un fix strettamente necessario emerge dai test, applicalo direttamente su main, test leaf, quindi un solo push.
6. Usa il deploy Oracle canonico già documentato, con il profilo privato esistente e senza mostrare secret. Non cambiare autenticazione, nginx, token o servizi non pertinenti.
7. Readback runtime bounded:
   - actor umano autenticato può aprire `personalhub_read` ed eseguire una SELECT innocua;
   - richiesta anonima a browse/query è negata;
   - write SQL e mutazioni della proiezione restano negate;
   - un check read-only dell'endpoint mobile esistente conferma che il route/envelope di sync è ancora disponibile; non inviare dati sintetici di produzione.
8. PASS => stop. Nessun plugin nuovo, tuning, benchmark, schema redesign o audit post-PASS.

# Acceptance
PASS solo se test mirati/suite/check PASS, main contiene il diff validato, runtime Oracle usa la policy aggiornata, SQL read-only autenticato funziona su `personalhub_read`, anonimo e ogni write sono negati, sync mobile non è stato alterato.

# Non-goal
Niente modifiche PersonalHub Android, nuovi token, Tailscale/Cloudflare redesign, query salvate, plugin Datasette, benchmark, migrazioni DB o modifiche ai dati.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 527184 --confirm-executed`

Output massimo 6 righe: `RESULT`, `HEAD`, `TESTS`, `DEPLOY`, `ACCESS_POLICY`, `BLOCKER`.
