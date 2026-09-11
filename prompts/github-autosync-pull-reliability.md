# github-autosync-pull-reliability

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

PROMPT_ID=684217
model=GPT-5.5
reasoning=low
MegaVault=FAST

## Goal

Rendere affidabile il pull automatico di `gernalix/github-autosync` e limitarlo rigidamente ai soli repository autorizzati sotto, senza indebolire le protezioni Git esistenti.

## Repository gestiti: allowlist rigida

`github-autosync` deve occuparsi **solo** di questi repository e di nessun altro:

- `gernalix/codex-roadmap`
- `gernalix/vm_oracle`
- `gernalix/MegaVault`
- `gernalix/fedora-system-monitor`
- `gernalix/codex-usage`
- `gernalix/github-autosync`
- `gernalix/PersonalHub`
- `gernalix/codex-usage-monitor`
- `gernalix/fedora-t7-backup`
- `gernalix/amici_fb`
- `gernalix/salute`

Questa lista è la sorgente autoritativa. Tutti gli altri repository GitHub attuali o futuri devono essere ignorati completamente dal servizio finché non vengono aggiunti esplicitamente alla allowlist.

È accettabile mantenere una singola `gh repo list gernalix ...` per discovery efficiente, ma filtra immediatamente il risultato alla allowlist **prima** di qualunque riconciliazione. Per repo fuori allowlist il servizio non deve fare clone, fetch, pull/fast-forward, push, audit Git, registrazione MegaVault, issue/defer, notifica Telegram o persistenza nello state operativo. Rimuovi inoltre dallo state eventuali vecchie entry di repository non più gestiti.

Anche l'inventario MegaVault deve essere filtrato alla stessa allowlist: un repository fuori allowlist non va considerato neppure se ha un worktree canonico, è dirty, ahead, behind o diverged.

## Starting point

Repo runtime Fedora: `/home/daniele/projects/github-autosync`.

Prima di modificare codice, aggiorna questo repo da `origin/main` con fast-forward **solo se il worktree è clean**. Se è dirty/diverged, non fare stash/reset/force: segnala il blocker e STOP.

Il remoto contiene già il commit `57e66a7066e8d040f88cd4dadf25b70289247ed1`, che ha introdotto deduplicazione per remote, uso del worktree canonico MegaVault e autoriparazione parziale di `no_upstream`. Riusa quanto già presente; non reimplementarlo.

## Fix richiesti

1. **Applica la allowlist come confine funzionale del servizio.**
   - Definisci la allowlist in un punto unico e semplice da mantenere.
   - Filtra sia discovery GitHub sia inventario MegaVault prima di sync/audit/registrazione/notifiche.
   - I repo esclusi non devono produrre errori o Telegram alert e non devono essere clonati automaticamente.
   - Pulisci dal repo-state persistente le entry escluse, senza toccare i loro worktree o remoti.
   - Non aggiungere una configurazione complessa o un nuovo database: basta una soluzione minima e testabile.

2. **`no_upstream` non deve essere deciso usando refs remote stale.**
   - Se il branch locale non ha upstream, esegui prima un singolo `git fetch --prune origin` mirato a quel repo.
   - Dopo il fetch, se `origin/<branch-locale>` esiste, imposta automaticamente quell'upstream e continua la normale riconciliazione nello stesso run.
   - Solo se il branch remoto continua a non esistere restituisci `no_upstream`.
   - Evita fetch duplicati nello stesso percorso: riusa l'evidenza del fetch appena fatto.

3. **Risolvi il worktree canonico prima del fast-skip per fingerprint invariato.**
   - In `command_run`, determina prima `inventory_entry`/worktree canonico per remote.
   - Il controllo `previous == fingerprint` non deve basarsi ciecamente su `~/projects/<repo>` quando MegaVault indica un altro worktree.
   - Una copia duplicata in `~/projects/<repo>` non deve causare lo skip del checkout canonico.
   - Mantieni una sola riconciliazione per remote e preserva il relativo `project_id` nelle issue.

4. **Mantieni le protezioni esistenti.**
   - `dirty_worktree`, dirty+behind, diverged, detached, origin mismatch e casi realmente ambigui restano deferred per i soli repo in allowlist.
   - Nessun auto-stash, reset, force-pull, force-push o merge non-fast-forward.
   - Repository clean + behind-only deve arrivare a fast-forward automatico; clean + ahead-only può usare il normale push già previsto.

## Scope

Lavora solo in `gernalix/github-autosync` e, se necessario per registrare il risultato secondo protocollo, MegaVault. Non fare refactor, cleanup o modifiche a PersonalHub/codex-roadmap oltre alla finalizzazione standard del task.

Parti da `autosync_core.py` e `tests/test_github_autosync.py`; non esplorare il repository oltre questi file salvo failure concreta.

## Verification

Aggiungi/aggiorna test mirati che provino almeno:

- un repository GitHub nuovo/modificato **fuori allowlist** viene ignorato: nessun clone/sync/issue/alert/state;
- un worktree MegaVault **fuori allowlist**, anche dirty/ahead/behind, viene ignorato senza issue né mutazioni;
- una vecchia entry state di repo escluso viene rimossa senza operazioni Git sul repo;
- un repository in allowlist continua invece a essere sincronizzato normalmente;
- branch senza upstream + `origin/<branch>` non ancora presente localmente: il fetch lo rende visibile, upstream viene impostato e il sync prosegue;
- branch senza upstream e senza corrispondente branch remoto anche dopo fetch: resta `no_upstream`;
- worktree canonico MegaVault diverso da `~/projects/<nome>` con eventuale copia duplicata: il canonical non viene erroneamente saltato;
- dirty/diverged in allowlist continuano a non essere modificati automaticamente.

Esegui solo i test unitari mirati del repo; amplia la suite solo se questi falliscono per dipendenze non isolate.

Poi esegui una sola verifica runtime non distruttiva/controllata del servizio (`github-autosync.service`) e conferma dal JSON/journal che:

- vengono gestiti esclusivamente gli 11 repository della allowlist;
- nessun repo escluso produce clone/sync/issue/Telegram alert;
- non resta alcun `no_upstream` falso sui casi autoriparabili.

Non correggere dirty worktree fuori scope.

## Acceptance / stop

PASS quando i test mirati passano, il runtime usa il checkout aggiornato, la allowlist è effettivamente il confine unico del servizio e i due edge case di pull sopra sono coperti. Commit + push normale, mai force. Dopo PASS finalizza la roadmap con `roadmap_guard` e STOP.

Output finale conciso: commit, test eseguiti, elenco degli 11 repo gestiti, risultato runtime, eventuali repository in allowlist ancora deferred con il solo motivo.