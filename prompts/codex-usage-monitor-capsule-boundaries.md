PROMPT_ID=374862 | project_id=8 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD

# Goal
Porta `codex-usage-monitor` a una vera architettura capsule-first senza cambiare comportamento, formati dati, timer/systemd o output pubblicati. Il runtime Fedora deve continuare a funzionare dopo il refactor e la nuova struttura deve avere un gate automatico che impedisca il ritorno a moduli monolitici/top-level.

# Perché richiede Codex
Il refactor tocca import/package e packaging runtime, ma l'acceptance richiede anche il checkout Fedora reale, `~/.codex`, le unità systemd utente e `deploy_runtime.py`; questi elementi non sono verificabili integralmente dalla chat remota.

# Starting point autoritativo
- repo: `/home/daniele/projects/codex-usage-monitor`, branch `main`, MegaVault project `8`;
- runtime canonico: Fedora locale; Oracle VM NON è runtime per questo repo;
- oggi l'implementazione è ancora prevalentemente flat: `codex_usage_monitor.py`, `codex_session_archive*.py`, `codex_usage_publisher*.py`, `codex_task_costs*.py`, `codex_curated_vault.py`, `github_actions_watch.py`, ecc.;
- `codex_usage_publisher.py` importa/re-esporta oggi da `codex_usage_publisher_base.py`; esiste anche `codex_usage_publisher_legacy.py`;
- CI remota già esegue la suite deterministica tramite `scripts/verify_repo.py`;
- `deploy_runtime.py` e `systemd/` sono parte del contratto operativo e vanno preservati.

Non leggere roadmap/README/MegaVault oltre ai fatti sopra salvo blocker concreto. Niente audit repo-wide narrativo: per localizzare usa una sola inventory AST/import compatta e poi apri solo i file dei domini che stai migrando.

# Target architetturale
Usa `src/codex_monitor/` come package di implementazione e `src/codex_monitor/capsules/` come boundary. Mantieni capsule coarse-grained, non una cartella per funzione. Il set minimo atteso è equivalente a:
- quota/notification policy;
- session archive/index;
- publishing;
- prompt/task analysis;
- GitHub Actions watch;
- runtime/deploy support.

Regole obbligatorie:
1. i file Python top-level necessari per compatibilità CLI/systemd restano solo adapter sottili e delegano a API esplicite delle capsule;
2. nessuna nuova business/shared logic nei wrapper top-level;
3. niente `import *`, re-export dinamici con `globals()` o monkey-patching di moduli;
4. accesso cross-capsule solo tramite superfici pubbliche esplicite (`api.py` o contratto equivalente); niente import di implementazioni private di un'altra capsule;
5. shared logic solo se realmente condivisa, con ownership esplicita: niente nuovo `utils.py` generico;
6. preserva nomi entrypoint, argomenti CLI, schema SQLite, JSON/transcript/metrics e semantics esistenti;
7. aggiorna `deploy_runtime.py` affinché il package venga distribuito atomicamente insieme ai wrapper, senza doppia sorgente runtime.

# Esecuzione a costo controllato
1. Fotografia Git; se pulito `git fetch origin && git pull --ff-only origin main`. Se dirty non pertinente o remoto divergente: `BLOCKED`, niente stash/rebase.
2. Esegui UNA inventory locale compatta basata su AST per: file Python runtime, import tra moduli, entrypoint richiamati da `systemd/`/`deploy_runtime.py`, line count. Non stampare sorgenti interi.
3. Migra per domini mantenendo shim compatibili. Evita modifiche funzionali; se un test espone comportamento ambiguo, conserva il comportamento corrente.
4. Aggiungi `scripts/check_architecture_boundaries.py` con test dedicati. Il gate deve almeno fallire su: runtime logic top-level oltre agli adapter consentiti, wildcard import, re-export dinamico, monkey-patching di namespace e import cross-capsule che bypassano la superficie pubblica.
5. Collega il gate a `scripts/verify_repo.py` e alla CI esistente; non creare un secondo workflow sovrapposto se basta aggiornare quello esistente.
6. Esegui UNA volta il gate architetturale e UNA volta la suite deterministica completa. Failure => correggi il failure domain specifico e rilancia solo il leaf test/gate necessario; una sola suite completa finale dopo i leaf PASS.
7. Commit/push una volta. Verifica la GitHub Actions del commit finale; se fallisce, usa solo job/log fallito e una correzione mirata.
8. Sul Fedora reale esegui UNA volta `python3 deploy_runtime.py`. Poi avvia in modo bounded le tre unità oneshot/runtime pertinenti già esistenti (`codex-usage-monitor.service`, `codex-session-archive.service`, `codex-usage-publisher.service`) e verifica solo che completino senza `ImportError`, `ModuleNotFoundError` o traceback introdotti dal refactor. Non aspettare timer multipli e non ripubblicare manualmente l'intero archivio.

# Acceptance
PASS solo se:
- tutta la logica applicativa nuova/esistente è dietro capsule esplicite e i vecchi entrypoint sono adapter di compatibilità;
- il gate architetturale PASS e viene eseguito dalla CI;
- suite deterministica completa + CI finale PASS;
- `deploy_runtime.py` distribuisce correttamente package + adapter;
- le tre unità Fedora completano il smoke senza regressioni di import/runtime;
- nessun formato/schema/comportamento funzionale è stato intenzionalmente cambiato.

# Non-goal
Niente nuove metriche, policy quota, modifiche publisher funzionali, backfill, modifica `codex-usage`, migrazioni DB, ottimizzazione prestazioni non richiesta, Oracle VM, cleanup generale o rinomina delle unità systemd.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 374862 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 374862`

Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `ARCHITECTURE`, `GATE`, `TESTS`, `CI`, `DEPLOY`, `RUNTIME`, `PUSH/BLOCKER`.
