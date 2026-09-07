# Fedora GitHub autosync + Codex completion guard hardening

PROMPT_ID: 781264

**Modello consigliato:** GPT-5.5  
**Reasoning:** medium  
**MegaVault:** FAST

## Goal

Correggere in modo localizzato l'implementazione appena introdotta in `gernalix/codex-usage-monitor` per autosync GitHub e controllo Git post-Codex, preservando tutto ciò che già funziona.

Il risultato deve rendere affidabile il guard anche per sessioni Codex multi-repo, eliminare la rescansione globale di `~/.codex/sessions` a ogni minuto, rendere fail-safe la registrazione automatica in MegaVault e far sì che un terminal report esplicito `RESULT=PASS|BLOCKED|FAIL` non venga esportato come `status=UNKNOWN`.

## Scope stretto / starting points

Parti soltanto da questi file/simboli remoti correnti e dai relativi test:

- `gernalix/codex-usage-monitor/codex_usage_publisher.py`
  - `connect_state`
  - `parse_session`
  - `classify_git_repo`
  - `record_git_completion_guard`
  - `command_run`
- `gernalix/codex-usage-monitor/github_autosync.py`
  - `run_ghorg`
  - `register_in_megavault`
  - `command_run`
- `gernalix/codex-usage-monitor/tests/test_usage_publisher.py`
- eventuale nuovo test autosync nello stesso repo, solo se necessario
- `gernalix/MegaVault/ai/megavault_core.py` e test del solo `register-github-repo` **solo se un fix concreto lo richiede**

Non fare audit generale di `codex-usage-monitor`, MegaVault, altri repo o vecchie sessioni. Non leggere `~/.codex/memories/MEMORY.md`: i fatti decisivi sono già qui.

## Evidenza già verificata

Riusa questi fatti senza riscoprirli:

1. Il precedente task `PROMPT_ID=628431` ha installato `ghorg v1.11.15`, creato `codex-github-autosync.timer`, clonato/sincronizzato i repo e registrato 40 nuovi project ID; questa parte è sostanzialmente funzionante e va preservata.
2. Il publisher gira tramite `codex-usage-publisher.timer` ogni minuto.
3. Il nuovo guard oggi ricava un solo repo da `metrics.repo_project`, che viene popolato dal CWD/`turn_context`. Nella sessione reale 628431 il valore esportato è `/home/daniele/Documents/ChatGPT/Fedora`, mentre la sessione ha realmente modificato almeno:
   - `/home/daniele/projects/codex-usage-monitor`
   - `/home/daniele/MegaVault`
   - `/home/daniele/projects/codex-roadmap`
   Quindi il guard attuale non verifica i repo realmente toccati da una sessione multi-repo.
4. `command_run()` del publisher, dopo il publisher legacy, esegue attualmente un secondo `source_root.glob("**/*.jsonl")` e riparsa tutte le sessioni pubblicate. L'idempotenza evita duplicati nel DB ma non evita questa scansione/parsing globale ogni minuto.
5. `github_autosync.py` chiama attualmente `register_in_megavault(...)` anche se `ghorg_result.returncode != 0`.
6. In `register_in_megavault`, `git add` e `git commit` non verificano esplicitamente il return code prima del push.
7. La sessione 628431 contiene chiaramente `RESULT=PASS` nella final response, ma `codex-usage/prompts/628431/metrics.json` è stato esportato con `status=UNKNOWN`.
8. Il precedente sviluppo ha sporcato temporaneamente il `megavault.sqlite` reale durante un test fixture prima di correggersi. Da ora i test del registrar devono usare soltanto DB/repo temporanei: nessun test deve scrivere sul DB MegaVault reale.

## Fix A — guard multi-repo reale

Il guard deve classificare **tutti e soli i repository Git realmente associati alle operazioni della completion**, non il solo CWD iniziale.

Implementa il minimo necessario:

- durante il parsing già necessario della rollout, raccogli i working directory espliciti dei tool call (`workdir`/`cwd` o equivalente nativo realmente presente negli eventi) e risolvili con `git rev-parse --show-toplevel`;
- deduplica i repo per path canonico;
- usa il CWD di sessione/turno solo come fallback se è esso stesso dentro un repo Git;
- non dedurre repo da semplici stringhe/testo del prompt o da una scansione di `/home/daniele/projects`;
- se un tool di modifica espone un path file esplicito ma non un workdir, è consentito risalire al repo da quel path; non fare parsing euristico arbitrario dei comandi;
- una completion multi-repo deve conservare una classificazione separata per ciascun repo (`clean_synced`, `dirty`, `ahead`, `behind`, `diverged`, `no_upstream`, `unknown` come applicabile);
- evolvi **minimamente** lo state SQLite esistente per conservare N risultati per completion. Preferisci estendere in modo backward-compatible la riga esistente con dati strutturati se evita una migrazione complessa; non creare un nuovo DB e non perdere le righe esistenti;
- il guard resta passivo: può fare al massimo il fetch mirato già previsto, ma mai commit/merge/rebase/reset/pull/push/stash.

Aggiungi un test realistico in cui una singola rollout contiene tool call con workdir in **3 repo Git temporanei distinti** e verifica che vengano registrati tutti e tre una sola volta.

## Fix B — zero rescansione globale post-publisher

Elimina il secondo passaggio `source_root.glob("**/*.jsonl")` da `command_run()`.

Il controllo Git deve essere attivato soltanto per le completion nuove/aggiornate già incontrate dal normale parsing del publisher nella run corrente:

- riusa gli oggetti/cycle già prodotti da `parse_session()` o una piccola collezione in-memory equivalente;
- dopo che il publisher ha concluso con successo, processa solo quelle completion eleggibili;
- una successiva run no-op non deve riparsare l'intero archivio una seconda volta per il guard e non deve fare nuovi fetch;
- non creare un secondo watcher, daemon o timer.

Aggiungi un test che renda osservabile questo requisito: una run no-op successiva non deve invocare il guard/fetch per cicli già registrati.

## Fix C — status terminale corretto

Correggi localmente il parsing dello stato finale affinché almeno queste forme esplicite siano riconosciute dalla `final_response_redacted`:

- `RESULT=PASS`
- `RESULT: PASS`
- `RESULT=BLOCKED`
- `RESULT=FAIL`

Tollera backtick/markdown e `PROMPT\_ID` senza ampliare inutilmente il parser.

Non inventare stato quando `RESULT` manca: in quel caso `UNKNOWN` può restare corretto.

Test obbligatori:

- PASS/BLOCKED/FAIL espliciti -> status corrispondente;
- nessun RESULT -> UNKNOWN;
- riprocessando la fixture equivalente alla sessione 628431, `RESULT=PASS` deve produrre `status=PASS` senza duplicare ciclo/chat/prompt né Telegram.

Se il normale publisher idempotente può correggere automaticamente l'export reale già esistente del prompt 628431 senza forzature o riscritture distruttive, fallo una sola volta e verifica che il remoto `codex-usage` mostri `status=PASS`. Se non può farlo in sicurezza, non modificare manualmente l'archivio: segnala soltanto il limite.

## Fix D — autosync/MegaVault fail-safe

In `github_autosync.py`:

1. Se ghorg termina con errore, **non avviare la fase di registrazione MegaVault** in quella run. Restituisci errore coerente e lascia MegaVault intatto.
2. Prima di registrare un repo come worktree locale, verifica che la directory locale sia realmente un repository Git coerente col remoto atteso; se il clone manca/fallisce, deferisci quel repo invece di registrarlo come locale.
3. Per l'eventuale commit metadata MegaVault, controlla il return code di ogni operazione critica: `git add`, `git commit`, `git push` e verifica finale HEAD/upstream. Su errore, fallisci esplicitamente senza fingere PASS e senza retry identici.
4. Mantieni il preflight già esistente: MegaVault deve essere clean e sincronizzato prima di una scrittura automatica.
5. Non cambiare il comportamento sicuro ghorg (`--protect-local`, `--fetch-all`, `--fetch-prune`, `--no-clean`) e non introdurre prune distruttivo.
6. I test devono usare repo/DB temporanei; vietato scrivere nel vero `/home/daniele/MegaVault/megavault.sqlite` durante unit test.

## Token/tool-call discipline specifica

Questo è un fix pre-localizzato. Quindi:

- non rileggere file non elencati salvo dipendenza concreta;
- non interrogare MEMORY.md;
- non ristudiare ghorg o reinstallarlo se `ghorg --version` conferma la versione già presente;
- non ripetere `git status/log/rev-parse` se lo stato non è cambiato;
- dopo un test fallito, correggi la causa specifica e rilancia solo il test coinvolto;
- niente suite complete salvo evidenza concreta che i test mirati non bastino;
- nessuna nuova run reale sui 65 repo salvo che sia strettamente necessaria per verificare il fix D; preferisci fixture temporanee;
- STOP immediato quando gli acceptance criteria sono soddisfatti.

## Acceptance criteria

PASS solo se tutti i punti seguenti sono veri:

- una singola completion con 3 repo toccati produce 3 classificazioni corrette e idempotenti;
- il CWD iniziale fuori repo non impedisce di rilevare i repo reali usati dai tool call;
- `command_run()` non contiene più una seconda scansione globale `**/*.jsonl` per il guard;
- una run no-op successiva non rifà fetch/guard sui cicli già processati;
- `RESULT=PASS|BLOCKED|FAIL` viene esportato correttamente; assenza di RESULT resta UNKNOWN;
- il caso equivalente a 628431 produce PASS senza duplicazioni o Telegram extra;
- se ghorg fallisce, MegaVault non viene modificato;
- repo non clonati/non coerenti non vengono registrati come worktree locali;
- add/commit/push/verifica MegaVault sono fail-fast e controllati;
- nessun unit test tocca il DB MegaVault reale;
- i test mirati passano;
- `codex-usage-monitor` è committato e pushato una sola volta al termine, con singola verifica finale;
- se MegaVault viene modificato per questo fix, stesso schema: commit finale, singolo push, singola verifica;
- nessun refactor o lavoro fuori scope.

## Output finale

Solo:

- `PROMPT_ID=781264`
- `RESULT=PASS|BLOCKED|FAIL`
- `multi_repo_guard=PASS|FAIL` + numero repo fixture
- `global_rescan_removed=YES|NO`
- `result_status_mapping=PASS|FAIL`
- `autosync_fail_safe=PASS|FAIL`
- test mirati eseguiti
- commit SHA `codex-usage-monitor`
- commit SHA MegaVault solo se modificato
- eventuale correzione reale status 628431: `updated|not_needed|safely_not_possible`
- blocker reale, se presente
