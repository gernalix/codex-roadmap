PROMPT_ID=621471 | PARENT_PROMPT_ID=404936 | project_id=92 | model=GPT-5.5 | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Esegui SOLO il deploy/validazione locale dei fix postmortem gia mergiati da ChatGPT:
- github-autosync main commit a4649b035a4c48ba31e90380daebc3cff35dd53c (PR #21);
- codex-usage-monitor main commit 21ef9f029bac2867efda08776869a2617713fd87 (PR #5).

Non rifare il postmortem, non fare audit generale e non modificare codice salvo un difetto direttamente introdotto da questi due commit che blocchi l'acceptance.

# Scope stretto
1. Claim con roadmap_start.py.
2. Sincronizza i due checkout canonici con i rispettivi origin/main usando i percorsi/helper canonici e preservando qualunque lavoro locale non correlato.
3. Esegui SOLO i test mirati pertinenti ai cambiamenti:
   - github-autosync: classificazione git_object_corrupt + watchdog fail-closed;
   - codex-usage-monitor: test 404936 wait-heavy/explicit-wait.
   Se i test mirati PASS, non lanciare suite equivalenti/ridondanti salvo che il deploy richieda un gate canonico.
4. Distribuisci i runtime con gli installer canonici gia esistenti; nessun venv.
5. Verifica una sola volta il runtime sano di github-autosync: service/timer/watchdog coerenti e un run reale termina status=ok senza peggiorare Kuma #46.
6. Esegui l'analisi di efficienza per PROMPT_ID=404936 usando i dati aggiornati disponibili e verifica almeno:
   total_tokens=125635; uncached_input_tokens=649; tool_call_count=86;
   explicit_wait_call_count=3; explicit_wait_seconds=150;
   findings includono roundtrip_heavy_cached_session, explicit_wait_time, wait_heavy_session.
7. Non attendere nuovi cicli per 3+ minuti: quella stabilita e' gia stata provata da 404936. Basta un run reale sano post-deploy + readback corrente.
8. Quando tutti i gate sopra sono PASS, roadmap_finish.py --prompt-id 621471 --confirm-executed e STOP immediato.

# Safety
- Nessun reset/clean/stash/rebase distruttivo.
- Nessun retry identico senza nuova evidenza.
- Nessuna modifica a monitor Kuma/config/token salvo che il deploy dei fix lo renda strettamente necessario; in tal caso fermati al primo blocker concreto invece di ampliare lo scope.
- Non stampare segreti.

# Report finale
Massimo 7 righe:
PROMPT_ID=621471
RESULT=PASS|BLOCKED|FAIL
AUTOSYNC=<commit/runtime/test>
USAGE_MONITOR=<commit/runtime/test>
EFFICIENCY_404936=<tokens/tools/wait findings>
KUMA=<#46 stato corrente>
BLOCKER=<none|unico blocker concreto>
