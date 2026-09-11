# github-autosync-pull-reliability

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

PROMPT_ID=684217
model=GPT-5.5
reasoning=low
MegaVault=FAST

## Goal

Rendere affidabile il pull automatico di `gernalix/github-autosync` senza indebolire le protezioni Git esistenti.

## Starting point

Repo runtime Fedora: `/home/daniele/projects/github-autosync`.

Prima di modificare codice, aggiorna questo repo da `origin/main` con fast-forward **solo se il worktree è clean**. Se è dirty/diverged, non fare stash/reset/force: segnala il blocker e STOP.

Il remoto contiene già il commit `57e66a7066e8d040f88cd4dadf25b70289247ed1`, che ha introdotto deduplicazione per remote, uso del worktree canonico MegaVault e autoriparazione parziale di `no_upstream`. Riusa quanto già presente; non reimplementarlo.

## Fix richiesti

1. **`no_upstream` non deve essere deciso usando refs remote stale.**
   - Se il branch locale non ha upstream, esegui prima un singolo `git fetch --prune origin` mirato a quel repo.
   - Dopo il fetch, se `origin/<branch-locale>` esiste, imposta automaticamente quell'upstream e continua la normale riconciliazione nello stesso run.
   - Solo se il branch remoto continua a non esistere restituisci `no_upstream`.
   - Evita fetch duplicati nello stesso percorso: riusa l'evidenza del fetch appena fatto.

2. **Risolvi il worktree canonico prima del fast-skip per fingerprint invariato.**
   - In `command_run`, determina prima `inventory_entry`/worktree canonico per remote.
   - Il controllo `previous == fingerprint` non deve basarsi ciecamente su `~/projects/<repo>` quando MegaVault indica un altro worktree.
   - Una copia duplicata in `~/projects/<repo>` non deve causare lo skip del checkout canonico.
   - Mantieni una sola riconciliazione per remote e preserva il relativo `project_id` nelle issue.

3. **Mantieni le protezioni esistenti.**
   - `dirty_worktree`, dirty+behind, diverged, detached, origin mismatch e casi realmente ambigui restano deferred.
   - Nessun auto-stash, reset, force-pull, force-push o merge non-fast-forward.
   - Repository clean + behind-only deve arrivare a fast-forward automatico; clean + ahead-only può usare il normale push già previsto.

## Scope

Lavora solo in `gernalix/github-autosync` e, se necessario per registrare il risultato secondo protocollo, MegaVault. Non fare refactor, cleanup o modifiche a PersonalHub/codex-roadmap oltre alla finalizzazione standard del task.

Parti da `autosync_core.py` e `tests/test_github_autosync.py`; non esplorare il repository oltre questi file salvo failure concreta.

## Verification

Aggiungi/aggiorna test mirati che provino almeno:

- branch senza upstream + `origin/<branch>` non ancora presente localmente: il fetch lo rende visibile, upstream viene impostato e il sync prosegue;
- branch senza upstream e senza corrispondente branch remoto anche dopo fetch: resta `no_upstream`;
- worktree canonico MegaVault diverso da `~/projects/<nome>` con eventuale copia duplicata: il canonical non viene erroneamente saltato;
- dirty/diverged continuano a non essere modificati automaticamente.

Esegui solo i test unitari mirati del repo; amplia la suite solo se questi falliscono per dipendenze non isolate.

Poi esegui una sola verifica runtime non distruttiva/controllata del servizio (`github-autosync.service`) e conferma dal JSON/journal che non resta alcun `no_upstream` falso sui casi autoriparabili. Non correggere dirty worktree fuori scope.

## Acceptance / stop

PASS quando i test mirati passano, il runtime usa il checkout aggiornato e i due edge case sopra sono coperti. Commit + push normale, mai force. Dopo PASS finalizza la roadmap con `roadmap_guard` e STOP.

Output finale conciso: commit, test eseguiti, risultato runtime, eventuali repository ancora deferred con il solo motivo.