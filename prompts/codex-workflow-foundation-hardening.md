[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=418562 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Ridurre il costo ricorrente dei task Codex con tre fix coordinati in un'unica sessione: (A) roadmap/finalizzazione Git sicura e più economica; (B) CLI MegaVault stabile per registrare e validare eventi senza SQL/schema discovery; (C) `github-autosync` leggero, con stato machine-friendly corretto.

Assorbe i vecchi prompt `561274` e `804316` e i colli di bottiglia emersi da `PROMPT_ID=684215`. Non modificare PersonalHub.

# A — codex-roadmap / workflow Codex
Stato noto: `origin/main` è autorevole; recenti run hanno creato stash solo per leggere la roadmap, archiviato per inferenza un prompt diverso da quello attivo, incluso modifiche preesistenti nel commit e speso tool-call in letture/verifiche ridondanti.

Implementa il percorso minimo che garantisca:
- lettura/selezione del primo pendente direttamente dal remoto o da stato isolato, senza stash e senza modificare il worktree locale;
- scritture roadmap in stato pulito/isolato oppure blocker preciso; mai inglobare dirt preesistente;
- archiviazione solo con identità esplicita dello stesso file/PROMPT_ID o continuazione dichiarata, mai per somiglianza;
- prima del commit, scope task-owned verificabile;
- per l'orchestrazione roadmap, non leggere `/home/daniele/.codex/memories/MEMORY.md` se prompt selezionato + README/AGENTS + MegaVault contengono già i fatti necessari; consultarlo solo per una lacuna storica concreta e dichiarata;
- raggruppare letture/check indipendenti, evitare status/schema discovery ripetuti e non ripetere un comando equivalente senza nuova evidenza o cambio di stato;
- ispeziona `codex-preserve-local-spiegazioni` una volta: elimina solo se provatamente ridondante, altrimenti preserva e segnala.

Persisti le regole di efficienza sopra nella documentazione autorevole minima necessaria affinché valgano anche ai futuri launcher della roadmap, senza duplicare istruzioni già presenti.

Test mirati: dirty worktree leggibile senza stash; modifica locale intatta; prompt ad-hoc non può archiviare un altro pendente; commit non assorbe dirt preesistente; conflitto reale viene isolato o bloccato.

# B — MegaVault
Aggiungi/estendi, nello stile CLI esistente, due comandi stabili:
- registra un event con project/category/type/status/summary e metadata opzionali, generando ID/timestamp e usando transazione;
- valida solo l'evento/progetto appena cambiato, lasciando invariato il validator globale per audit espliciti.

Il comando deve fallire senza write parziali su input invalido e produrre output machine-friendly. Aggiorna solo la documentazione autorevole necessaria affinché i task futuri usino questi comandi invece di SQLite manuale.

Test solo su DB temporaneo/copia: event valido, input invalido atomico, scoped validation non bloccata da issue globale estranea, global validation ancora disponibile.

# C — github-autosync
Stato già verificato da `PROMPT_ID=684215`, da riusare senza rediscovery generale:
- repo: `gernalix/github-autosync`, checkout canonico `/home/daniele/projects/github-autosync`;
- timer user `github-autosync.timer` ogni 5 minuti;
- la run osservata ha scoperto 66 repo e l'implementazione corrente usa ghorg con `--fetch-all --fetch-prune`, causando fetch concorrenti dell'intero parco repo a ogni tick;
- la stessa run ha restituito `status=ok` mentre MegaVault era `validation=deferred_dirty` con tutti i repo deferred;
- i test Python creano `__pycache__`, oggi da ripulire manualmente.

Modifica solo `github-autosync` per ottenere:
1. **Steady-state leggero**: il tick periodico deve usare una singola discovery/metadata query GitHub (o equivalente altrettanto economico) e uno stato persistente/fingerprint per individuare repo nuovi o realmente cambiati. Non eseguire più `fetch-all`/pull su tutti i repo invariati a ogni tick. `ghorg` può restare solo dove serve davvero (bootstrap/recovery), non come fetch globale periodico.
2. **Update mirato e sicuro**: clona i repo nuovi e aggiorna solo quelli identificati come cambiati; conserva le protezioni esistenti. Worktree dirty, ahead o diverged non vanno stashati/reset/pullati automaticamente e devono risultare skipped/deferred in modo esplicito.
3. **Status veritiero**: `status=ok` solo quando tutte le fasi attese della run sono complete. Se GitHub sync riesce ma MegaVault viene differito per condizioni previste come `deferred_dirty`/`deferred_not_synced`, restituisci uno stato machine-friendly distinto (`partial`/`deferred` o equivalente), mantenendo exit 0 per questi defer attesi; errori reali restano non-zero. Il JSON deve rendere immediatamente distinguibili success, partial/deferred ed error.
4. **Niente artefatti Python**: aggiungi `.gitignore` minimo per `__pycache__/`, `*.pyc` e artefatti equivalenti prodotti dai test, senza cleanup fuori scope.

Test mirati, senza audit o sync reale dell'intera organizzazione:
- due run consecutive senza cambi remoti => la seconda non effettua fetch/pull per repo invariati;
- repo remoto cambiato => solo quel repo viene aggiornato;
- repo nuovo => viene clonato;
- dirty/ahead/diverged => nessuna mutazione locale e stato skipped/deferred esplicito;
- MegaVault dirty/not-synced => stato globale non è `ok`, registrazione differita, exit 0 se il defer è atteso;
- fallimento GitHub/clone/update reale => stato error e non-zero;
- suite esistente + nuovi test PASS; nessun `__pycache__` tracciato.

Non cambiare la cadenza di 5 minuti salvo necessità tecnica dimostrata: il fix deve ridurre il lavoro per tick, non semplicemente eseguirlo meno spesso.

# Discipline
Una lettura raggruppata per repo, niente audit generali/refactor. Parti dai file direttamente pertinenti e riusa lo stato già verificato sopra. Non leggere MEMORY.md salvo lacuna concreta. Nessun retry equivalente senza nuova evidenza. Commit/push separati per i repo effettivamente modificati, una verifica finale ciascuno. PASS solo se A+B+C passano; poi aggiorna roadmap e STOP.

Output conciso: `PROMPT_ID`, `RESULT`, bootstrap/write path roadmap, identity/commit guard, regole efficienza persistite, stash disposition, comando event, comando scoped validate, autosync change-detection strategy, status semantics, test, SHA per repo, blocker.
