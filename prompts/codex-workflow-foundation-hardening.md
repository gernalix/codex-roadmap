[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=418562 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Verificare e attivare localmente il foundation hardening già implementato sui remoti. **Non reimplementare e non fare discovery generale**: modifica codice solo se un test mirato dimostra un difetto concreto.

# Stato remoto già implementato
Questi commit sono il punto di partenza autorevole:
- `gernalix/codex-roadmap` `main`: `397c99d1e3a9c2aadcbbafba8036c71089b84d7f` — `tools/roadmap_guard.py`, test, README workflow/efficienza;
- `gernalix/MegaVault` `master`: `51bc4434c70502788a9f37602a39e5f19b456dd1` — CLI `event-create` / `event-validate`, test e routing docs;
- `gernalix/github-autosync` `main`: `119ea7ecfc8f066b287f6dfdd58fe19afcc64276` — discovery GitHub unica, fingerprint persistente, update mirato, status truthful, test e `.gitignore`.

Sincronizza i checkout canonici solo con fast-forward sicuro. **Mai stash/reset/force per adattarli al task.** Se un checkout ha dirt non correlato che impedisce il fast-forward, preservalo e usa un worktree/clone temporaneo da `origin/<canonical>` per i test; segnala blocker solo se serve realmente attivare quel codice nel runtime canonico.

# A — codex-roadmap
1. Esegui solo `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` nel codice remoto corrente: devono passare i test dirty-worktree, isolamento commit e identity guard.
2. Su checkout locale volutamente dirty o fixture equivalente, verifica una volta che `python3 tools/roadmap_guard.py select` non modifica/stasha il worktree e legge da `origin/main`.
3. Non usare il guard `complete` sulla roadmap reale finché questo prompt non ha PASS; il suo comportamento di finalizzazione è già coperto dal test isolato.
4. Ispeziona **una sola volta** l'eventuale stash `codex-preserve-local-spiegazioni`: eliminalo solo se il contenuto è provatamente ridondante rispetto al remoto corrente; altrimenti preservalo e riportalo. Niente ulteriori audit stash/branch.
5. Non leggere `MEMORY.md`: questo prompt + README + remoti contengono il contesto necessario.

# B — MegaVault
1. Esegui solo i test `workflow_events` e poi la suite MegaVault esistente se il test mirato passa.
2. Verifica la compatibilità con lo **schema reale corrente** di `megavault.sqlite` senza mutare il DB canonico: crea una snapshot/copia temporanea consistente e prova lì un `event-create` valido, `event-validate --event-id ...` e `event-validate --project-id ...`.
3. Verifica su copia che metadata JSON invalido e `project_id` inesistente non lascino write parziali.
4. Conferma che la scoped validation del progetto/evento appena toccato non sia bloccata da un problema globale estraneo. Il validator globale `megavault.py validate` deve restare disponibile e PASS sul repository reale.
5. Se lo schema reale usa nomi non coperti dall'adapter, applica **solo** il mapping minimo necessario e relativo test; niente schema redesign.

# C — github-autosync
1. Esegui `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`.
2. Esegui una sola query live `gh repo list` con i campi già usati dal codice per confermare che `name,url,defaultBranchRef,pushedAt,isArchived` siano disponibili; non fare query per-repo.
3. Esegui `python3 github_autosync.py --dry-run --no-telegram run` una volta. Se PASS, attiva/verifica il runtime canonico già esistente senza cambiare la cadenza di 5 minuti.
4. Verifica da test + massimo due run live consecutive che, senza cambi remoti tra i due tick, la seconda non faccia fetch/pull dei repo invariati. Non rieseguire un comando equivalente se l'evidenza è già sufficiente.
5. Conferma: repo cambiato => solo quello entra nel sync; repo nuovo => clone; dirty/ahead/diverged => nessuno stash/reset/force; MegaVault `deferred_dirty`/`deferred_not_synced` => status globale non `ok` ma exit 0; errori reali GitHub/clone/update => `error` e non-zero; nessun `__pycache__`/`*.pyc` tracciato.

# Acceptance / stop
PASS quando A+B+C sono verificati sullo stato remoto sopra o con soli fix minimi causati da failure concreta. Non fare refactor, cleanup, audit organizzazione, documentazione aggiuntiva o nuove feature.

Se hai dovuto modificare qualcosa, test mirato → commit/push solo del repo modificato → una verifica finale. Se non hai dovuto modificare codice, non creare commit cosmetici.

Dopo PASS usa `python3 tools/roadmap_guard.py complete --prompt-id 418562 --dry-run`; se restituisce `ready`, eseguilo una sola volta senza `--dry-run` e STOP. Se questo prompt non è ancora il primo pendente, **non archiviarlo**: lascia la roadmap invariata e riporta che la verifica è PASS ma la finalizzazione deve attendere il suo turno.

Output finale conciso: `PROMPT_ID`, `RESULT`, roadmap guard tests + stash disposition, MegaVault real-schema/event CLI result, autosync tests + live steady-state result + status semantics, eventuali fix/commit SHA, blocker.
