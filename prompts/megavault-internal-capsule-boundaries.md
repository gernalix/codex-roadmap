PROMPT_ID=805417 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Rafforza progressivamente i boundary interni di MegaVault eliminando il principale anti-pattern architetturale attuale (`import *` + re-export dinamico + monkey-patching tra `strict_tag_wrapper` e `megavault_core`) senza cambiare schema, dati o comportamento CLI. Blocca la regressione con un gate automatico.

# Perché richiede Codex
L'acceptance deve usare il checkout MegaVault reale e il `megavault.sqlite` canonico, verificare compatibilità dei comandi sul DB corrente e far passare `megavault.py validate`; il DB privato/runtime locale non è disponibile integralmente dalla chat remota.

# Starting point autoritativo
- repo: `/home/daniele/projects/MegaVault`, branch `master`, MegaVault project `23`;
- `megavault.py` è il composition root;
- `ai/strict_tag_wrapper.py` importa oggi `ai.megavault_core as _core`, usa `from ai.strict_tag_wrapper import *` dal root, copia dinamicamente i nomi pubblici con `globals()` e sostituisce funzioni su `_core` per incident/tag handling;
- moduli già separati esistenti: `ai/operational_indexes.py`, `ai/workflow_events.py`, `ai/reporting.py`;
- `ai/megavault_core.py` resta il legacy core maggiore: NON fare un big-bang split solo per ridurre il numero di righe;
- CI remota già esegue `python3 megavault.py validate` + unittest completi.

Usa il protocollo MegaVault corrente come autoritativo. Non creare nuovi Markdown fuori dalla allowlist del protocollo. Non leggere repository esterni.

# Target architetturale di questa fase
1. `megavault.py` deve importare e comporre API/dispatcher espliciti: niente wildcard import.
2. Elimina da runtime code `globals().update(...)`/loop di re-export e l'assegnazione monkey-patch di funzioni su `megavault_core`.
3. Sposta la logica incident/tag oggi nel wrapper in un modulo/capsule con ownership esplicita oppure integrala nel core tramite dipendenza/API esplicita; scegli la soluzione con meno churn e meno rischio.
4. Mantieni `megavault_core.py` come legacy capsule temporanea se uno split ulteriore non porta un beneficio concreto in questa fase. Non trasformare il task in una riscrittura dell'intero CLI.
5. Le API usate da test/moduli interni devono essere importate esplicitamente. Se serve compatibilità interna, crea un piccolo facade con `__all__` esplicito; niente namespace magici.
6. Aggiungi un gate architetturale deterministico che fallisca almeno su wildcard import nel runtime MegaVault, re-export dinamici via `globals`, monkey-patching di funzioni tra moduli e logica non delegata nel root `megavault.py`.
7. Collega il gate alla validazione/test esistente o alla CI già presente senza creare workflow duplicati.

# Esecuzione minima
1. Fotografia Git; se pulito esegui UNA sola sync: `timeout 20s git fetch origin master && git merge --ff-only origin/master`. Dirty non pertinente, fetch/merge fallisce o divergenza => `BLOCKED`, niente stash/rebase/retry.
2. Leggi solo: `megavault.py`, `ai/strict_tag_wrapper.py`, le firme/dispatcher pertinenti di `ai/megavault_core.py`, `ai/operational_indexes.py`, `ai/workflow_events.py` e i test che importano i simboli toccati. Per `megavault_core.py` usa ricerca simboli/firme, non dump completo.
3. Prima delle modifiche cattura in un solo comando bounded l'output/exit code di un set minimo read-only di CLI sul DB reale: `project-show 23`, `project-path --status 23`, più `--help` o un altro comando puro necessario a coprire il dispatch toccato. Salva solo output non sensibile.
4. Applica il refactor boundary con il minimo numero di file. Nessuna modifica a `megavault.sqlite`, schema, migrations o dati salvo che il protocollo richieda l'evento finale; in tal caso usa solo il comando canonico previsto dal protocollo.
5. Aggiungi/aggiorna test di architettura e compatibilità import/dispatch.
6. Esegui: gate architetturale, test mirati, `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py validate`. Se PASS, esegui UNA sola suite unittest completa. Failure => leaf fix + riconferma leaf; non rilanciare la suite completa finché i leaf non passano.
7. Ripeti UNA volta lo stesso smoke CLI read-only del punto 3 e confronta semanticamente exit code/identità/output rilevante.
8. Commit/push una volta e verifica la CI finale. Se fallisce, apri solo il job/log fallito e correggi il failure domain relativo.

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
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 805417 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 805417`

Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `BOUNDARY`, `INCIDENT_API`, `GATE`, `VALIDATE`, `TESTS`, `CI`, `PUSH/BLOCKER`.
