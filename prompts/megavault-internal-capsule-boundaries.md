PROMPT_ID=805417 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Rafforza i boundary interni di MegaVault eliminando il principale anti-pattern architetturale attuale (`import *` + re-export dinamico + monkey-patching tra `strict_tag_wrapper` e `megavault_core`) senza cambiare schema, dati o comportamento CLI. Blocca la regressione con un gate automatico.

# Starting point autoritativo
- repo: `/home/daniele/projects/MegaVault`, branch `master`, MegaVault project `23`;
- baseline remota verificata: `a78d7b76e737a6e52103889e99575f75b1d9f309` o successiva;
- `megavault.py` è il composition root e importa oggi `from ai.strict_tag_wrapper import *`;
- `ai/strict_tag_wrapper.py` importa `ai.megavault_core as _core`, modifica attributi/funzioni su `_core`, re-esporta dinamicamente con loop + `globals()` e poi `globals().update(...)`;
- moduli già separati esistenti: `ai/operational_indexes.py`, `ai/workflow_events.py`, `ai/reporting.py`;
- `ai/megavault_core.py` resta il legacy core maggiore: NON fare un big-bang split solo per ridurre il numero di righe;
- CI remota già esegue `python3 megavault.py validate` + unittest completi;
- DB canonico locale: `/home/daniele/projects/MegaVault/megavault.sqlite`.

Questo file è autosufficiente per il task: non leggere README/roadmap/spiegazioni/MEMORY/MEGAVAULT_PROTOCOL/GLOBAL_INDEX salvo blocker concreto. Non creare Markdown e non leggere repository esterni.

# Target architetturale
1. `megavault.py` deve importare e comporre API/dispatcher espliciti: niente wildcard import.
2. Elimina da runtime code `globals().update(...)`/loop di re-export e l'assegnazione monkey-patch di funzioni su `megavault_core`.
3. Sposta la logica incident/tag oggi nel wrapper in un modulo/capsule con ownership esplicita oppure integrala nel core tramite dipendenza/API esplicita; scegli la soluzione con meno churn e meno rischio.
4. Mantieni `megavault_core.py` come legacy capsule temporanea se uno split ulteriore non porta beneficio concreto. Non trasformare il task in una riscrittura dell'intero CLI.
5. Le API usate da test/moduli interni devono essere importate esplicitamente. Se serve compatibilità interna, crea un piccolo facade con `__all__` esplicito; niente namespace magici.
6. Aggiungi un gate architetturale deterministico che fallisca almeno su wildcard import nel runtime MegaVault, re-export dinamici via `globals`, monkey-patching di funzioni tra moduli e logica non delegata nel root `megavault.py`.
7. Collega il gate alla validazione/test esistente o alla CI già presente senza creare workflow duplicati.

# Esecuzione minima
1. Fotografia Git; se pulito esegui UNA sola sync: `timeout 20s git fetch origin master && git merge --ff-only origin/master`. Dirty non pertinente, fetch/merge fallisce o divergenza => `BLOCKED`, niente stash/rebase/retry.
2. Leggi solo: `megavault.py`, `ai/strict_tag_wrapper.py`, le firme/dispatcher pertinenti di `ai/megavault_core.py`, `ai/operational_indexes.py`, `ai/workflow_events.py` e i test che importano i simboli toccati. Per `megavault_core.py` usa ricerca simboli/firme, non dump completo.
3. Prima delle modifiche cattura in un solo comando bounded l'output/exit code di un set minimo read-only di CLI sul DB reale: `project-show 23`, `project-path --status 23`, più `--help` o un altro comando puro necessario a coprire il dispatch toccato. Salva solo output non sensibile.
4. Applica il refactor boundary con il minimo numero di file. Nessuna modifica a `megavault.sqlite`, schema, migrations o dati.
5. Aggiungi/aggiorna test di architettura e compatibilità import/dispatch.
6. Esegui: gate architetturale, test mirati, `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py validate`. Se PASS, esegui UNA sola suite unittest completa. Failure => leaf fix + riconferma leaf; non rilanciare la suite completa finché i leaf non passano.
7. Ripeti UNA volta lo stesso smoke CLI read-only del punto 3 e confronta semanticamente exit code/identità/output rilevante.
8. Commit/push una volta e verifica la CI finale. Se fallisce, apri solo il job/log fallito e correggi il failure domain relativo.
9. Dopo tutti i PASS stop immediato: niente ulteriore audit architetturale o cleanup.

# Acceptance
PASS se:
- `megavault.py` è composition root esplicito;
- non restano wildcard import, re-export dinamici o monkey-patching nel percorso runtime toccato;
- incident/tag handling ha ownership/API esplicita;
- gate architetturale + test + `megavault.py validate` + CI finale PASS;
- i CLI smoke sul DB canonico hanno comportamento equivalente;
- schema e dati canonici non sono stati modificati dal refactor.

# Non-goal
Niente split totale di `megavault_core.py`, redesign schema, migrazione DB, rinomina project_id, cambi Kuma/Telegram, cleanup Markdown, refactor reporting, audit repository esterni o ottimizzazioni non richieste.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 805417 --confirm-executed`

Non fare dry-run separati né controlli Git equivalenti dopo finalizzazione.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `BOUNDARY`, `INCIDENT_API`, `GATE`, `VALIDATE`, `TESTS`, `CI`, `PUSH/BLOCKER`.
