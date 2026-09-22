# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]] · [[prompt-registry|Registro prompt]] · [[obsidian/Dashboards/Roadmap|Dashboard Obsidian]] · [[STANDARD_PROMPT|Esecuzione Codex]] · [[SQLITE_ROADMAP|SQLite]]

Coda minima di lavoro **solo per attività che richiedono davvero Codex**: filesystem/toolchain locale, device/emulatore, VM, segreti/config runtime, servizi locali o altre risorse non disponibili nella normale chat. Se ChatGPT può completare il lavoro direttamente sui repository remoti, va fatto subito e non inserito in roadmap.

## Architettura minima

1. **MegaVault**: registry/routing dei progetti e delle invarianti globali.
2. **`roadmap.sqlite`**: unica source of truth di task, dipendenze, stato, testo canonico dei prompt ed esecuzioni.
3. **GitHub Actions single writer**: unico writer ordinario del DB canonico.
4. **Workflowy**: unica centralina operativa visibile; proietta roadmap + pipeline reale di `github-autosync` + link Chrome/Codex.
5. **Markdown/Obsidian**: output di compatibilità/audit, non interfaccia operativa e non fonte di stato.
6. **codex-usage-monitor**: telemetria automatica di esiti/costi; non deve creare lavoro meta salvo eccezioni reali.

Non aggiungere altri strati senza un beneficio operativo misurabile.

## Regola anti-overengineering

L'infrastruttura è considerata **stabile**. Il default è non modificarla.

Una nuova feature, tabella, vista, monitor, notifica, protocollo o automazione è ammessa solo se soddisfa almeno una di queste condizioni:

- elimina lavoro manuale ricorrente già osservato;
- elimina una classe di errori/conflitti già osservata;
- è necessaria per correttezza, sicurezza o rischio dati;
- sblocca direttamente un progetto applicativo.

Non implementare miglioramenti per eleganza, completezza teorica, telemetria aggiuntiva o casi ipotetici. Un problema collaterale non bloccante si segnala e si lascia fuori scope.

**PASS chiude il sottosistema.** Dopo un PASS non creare audit, follow-up o “ulteriori ottimizzazioni” salvo nuova evidenza concreta.

## Analisi prompt: solo per eccezioni

Non analizzare sistematicamente ogni prompt Codex riuscito. La telemetria viene raccolta automaticamente; un'analisi ChatGPT approfondita si apre solo quando c'è almeno un segnale utile:

- `FAIL`, `BLOCKED`, `UNKNOWN` o retry multipli;
- costo/durata/tool-call chiaramente anomali rispetto a task simili;
- conflitto Git, output enorme, discovery ripetuta o loop osservato;
- bug dell'infrastruttura emerso durante l'esecuzione;
- richiesta esplicita dell'utente.

Un PASS ordinario senza anomalie non genera file `audits/`, task di follow-up o modifiche al sistema.

Le strutture storiche `analyses` e `analysis_code_changes` restano nel DB per compatibilità e casi eccezionali; non sono un obbligo per ogni PROMPT_ID.

## Source of truth e writer unico

`roadmap.sqlite` è l'unica fonte autorevole di metadati **e testo canonico dei prompt**. Workflowy è la dashboard operativa. `roadmap.md`, `spiegazioni.md`, `prompt-registry.md`, `obsidian/` e i file prompt restano materializzazioni di compatibilità/audit e non devono essere usati per dedurre lo stato operativo.

ChatGPT, Codex e il sync `codex-usage` inviano richieste come **GitHub Issues** con titolo `[roadmap-mutation] <request_key>` e body JSON immutabile. Ogni run del workflow drena **tutte** le mutation Issue aperte in ordine, le applica serialmente, materializza eventuali nuovi prompt, verifica ogni mutation e rigenera le viste **una sola volta per batch**, poi aggiorna `main` e chiude le Issue processate. Se GitHub cancella un run pending per la concurrency, la Issue resta aperta e viene raccolta automaticamente dal run successivo. Una mutation invalida/collidente viene isolata, commentata e chiusa `not_planned` senza impedire l'applicazione delle Issue valide successive.

I client non committano più file di inbox, prompt, DB o viste. Le directory `mutations/inbox/` e `mutations/applied/` restano solo come storico del trasporto precedente. Gli entry point operativi di mutazione diretta sono bloccati: `roadmap_db.py` è read-only da CLI, `import_codex_usage.py` delega a `roadmap_sync.py`, l'inbox legacy è test-only e `bootstrap_roadmap.py` richiede il contesto writer esplicito.

**Regola operativa automatica:** una richiesta umana come “aggiungi/aggiorna/sposta/chiudi questo task nella roadmap” significa sempre creare una mutation Issue tramite `tools/submit_mutation.py` (o API GitHub equivalente) e lasciare al workflow single-writer DB, prompt materializzati e viste. L'utente non deve ricordare o ripetere “usa il writer unico”. Una modifica diretta a `roadmap.sqlite`, `roadmap.md`, `spiegazioni.md`, `prompt-registry.md`, `obsidian/`, `prompts/`, `completed/` o `falliti/` per cambiare lo stato canonico è un bug di processo.

Dettagli tecnici: [[SQLITE_ROADMAP|Roadmap SQLite]].


### Checklist obbligatoria quando ChatGPT deve “mettere un prompt nella roadmap”

Per un **nuovo prompt** il percorso completo è:

```text
richiesta utente
  → MegaVault remote allocator: allocate
  → risposta con PROMPT_ID canonico
  → Issue [roadmap-mutation] con op=register
  → GitHub Actions single writer
  → roadmap.sqlite + prompt materializzato + viste
  → MegaVault remote allocator: materialize sul file canonico
  → verifica di entrambe le conferme
  → solo allora risposta “aggiunto alla roadmap”
```

Regole fail-closed:

- una normale Issue o una Issue `[plan]` **non aggiorna la roadmap**;
- ChatGPT non deve mai usare una `[plan]` come handoff sostitutivo quando l'utente ha chiesto una mutazione reale;
- un Issue number non è un PROMPT_ID;
- non dichiarare “aggiunto alla roadmap” finché la mutation Issue non è stata applicata dal writer;
- per un nuovo prompt, non dichiarare completato il workflow finché MegaVault non conferma anche `status=materialized` per lo stesso PROMPT_ID;
- se il bridge remoto MegaVault non risponde e il checkout canonico locale è disponibile, usare il medesimo allocator tramite `python3 /home/daniele/MegaVault/megavault.py prompt-id allocate --request-id <REQUEST_ID> ...`; se anche il checkout/allocator canonico non è disponibile, lo stato corretto è “allocazione pendente/bloccata”, mai un ID manuale o una Issue informativa;
- per aggiornare un prompt esistente si usa direttamente una mutation Issue e **non** si alloca un nuovo ID, salvo una vera revisione del prompt che richieda una nuova materializzazione.

Bridge remoto PROMPT_ID di MegaVault:

- il trasporto canonico è una GitHub Issue immutabile `[prompt-id-command] <request_id>` nel repository `gernalix/MegaVault`, con il JSON del comando nel body;
- `request_id` è la chiave idempotente del registry SQLite stesso: `megavault.sqlite:prompt_id_allocation_requests` viene scritto atomicamente insieme alla reservation del PROMPT_ID. Retry con gli stessi parametri restituiscono lo stesso ID; parametri diversi con la stessa chiave falliscono chiuso;
- Le receipt JSON restano solo audit/proiezioni di compatibilità. L'autorità per l'idempotenza è `megavault.sqlite`; `.github/prompt-id-response.json` non è una mailbox né una fonte canonica;
- il percorso è sempre `allocate → register → materialize`. Se un tentativo si interrompe, si riprende dal primo stato non confermato senza riallocare o riscrivere gli stati già confermati;
- il vecchio `.github/prompt-id-request.json` non è più un entry point operativo e non va aggiornato per inviare comandi;
- se il runner GitHub Actions privato di MegaVault non parte, usare lo stesso allocator canonico locale con `megavault.py prompt-id allocate ...` / `materialize ...`; non creare un secondo writer e non inventare ID;
- se il bridge è indisponibile dopo `register`, la materializzazione può essere completata localmente sul file canonico ottenuto dopo un `roadmap_pull.py` protetto.

## Pull locale obbligatoriamente protetto

Sul checkout locale di `codex-roadmap`, **`git pull`, `git merge`, `git reset` o altri aggiornamenti diretti di `main` sono vietati**. Il pull canonico è:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_pull.py --repo ~/projects/codex-roadmap
```

Per un checkout nuovo o già aggiornato che contiene questi tool, installare una sola volta il guard locale:

```bash
python3 ~/projects/codex-roadmap/tools/install_roadmap_pull_guard.py --repo ~/projects/codex-roadmap
```

Se invece il checkout locale **non contiene ancora** `roadmap_pull.py`, fare il bootstrap senza applicare prima il remoto:

```bash
cd ~/projects/codex-roadmap
git fetch origin main
tmp="$(mktemp)"
git show origin/main:tools/roadmap_pull.py > "$tmp"
python3 "$tmp" --repo ~/projects/codex-roadmap --bootstrap-guard
rm -f "$tmp"
```

Il bootstrap installa l'hook dal commit remoto appena fetchato, esegue lo stesso confronto locale/remoto e solo dopo PASS applica il fast-forward. Non richiede un `git pull` preliminare.

L'installer configura un hook Git locale `reference-transaction` che blocca ogni aggiornamento non autorizzato di `refs/heads/main`; quindi un normale `git pull` può fare fetch ma **non può applicare il fast-forward**. Solo `roadmap_pull.py` può autorizzare l'esatto passaggio `OLD_SHA -> NEW_SHA` dopo il pre-pull.

Il pre-pull è fail-closed e segue sempre questa sequenza:

1. richiede checkout `main`; se le **sole** modifiche locali tracked sono nelle viste generate (`roadmap.md`, `spiegazioni.md`, `prompt-registry.md`, `obsidian/`), le ripristina automaticamente da HEAD perché non sono fonti canoniche. Qualunque altra modifica o file untracked blocca il pull;
2. fa solo `fetch`, senza modificare il worktree;
3. apre il `roadmap.sqlite` locale e quello del commit remoto appena fetchato;
4. raccoglie tutti i PROMPT_ID `running` locali e remoti;
5. per ogni prompt `running` remoto verifica la riga canonica e la materializzazione del corpo nel DB; durante il cutover accetta come fallback il vecchio file prompt, ma non consulta le dashboard Markdown;
6. per ogni prompt già `running` localmente richiede che il remoto lo conservi **identico** nel corpo canonico SQLite e nei metadati protetti. Qualunque modifica, rimozione, supersede, reorder, cambio dipendenza/tag/relazione o spostamento blocca il pull;
7. unica eccezione: un `running` locale può diventare terminale se il DB remoto contiene una richiesta terminale autorevole coerente (`roadmap_finish.py` / `roadmap_result.py`) oppure, per compatibilità storica, una vera esecuzione terminale `source=codex-usage`; la telemetria non è più un prerequisito per avanzare il pull;
8. solo dopo PASS autorizza e applica un singolo `merge --ff-only` verso lo SHA remoto già verificato;
9. dopo il merge ricontrolla che tutti i prompt ancora running siano presenti e `running`, quindi aggiorna la copia locale dell'hook.

Se una verifica fallisce, **HEAD e worktree locali non avanzano**. Non fare fallback con `git pull`, `git reset --hard origin/main` o merge manuale: va prima corretta la causa remota o lo stato canonico.

## Centralina Workflowy

La dashboard operativa è sincronizzata da `workflowy-importer` e mostra stati derivati da fonti reali:

- **Ready / Waiting** dal DB e dalle dipendenze;
- **Running** dal claim di `roadmap_start.py`;
- **Integration** dallo stato task/PR/CI/rebase di `github-autosync`;
- **Needs fix** solo per stato terminale negativo o hard blocker reale dell'integratore;
- **Done** dal PASS canonico.

Ogni nodo può esporre `🚀 Avvia`, `📋 Copia prompt` e i collegamenti espliciti Chrome/Codex tramite `chrome-codex-switcher`. `🚀 Avvia` è riservato ai task Codex: deve aprire direttamente Codex in ChatGPT Desktop, senza creare una chat/tab ChatGPT in Chrome, usando i metadati canonici `project_id/project_name/repo/model/reasoning` del prompt. I collegamenti Chrome restano azioni separate. La chiave di correlazione è sempre il PROMPT_ID esplicito.

## Viste Markdown di compatibilità

`roadmap.md`, `spiegazioni.md`, `prompt-registry.md` e `obsidian/` possono continuare a essere rigenerati per storico/debug durante il cutover, ma nessun componente deve usarli per stabilire lo stato di un prompt.

## Regola di ammissione

Un nuovo task entra in roadmap solo se:

1. richiede davvero una risorsa locale/non disponibile in chat; e
2. risolve un bug/blocco, rischio dati, requisito funzionale o verifica necessaria.

Non usare la roadmap come backlog generico e non inserirvi:

- micro-ottimizzazioni di helper/monitor già funzionanti;
- analisi del costo del prompt precedente;
- audit o verifiche “per sicurezza” dopo PASS;
- modifiche puramente remote che ChatGPT può fare direttamente;
- refactor/cleanup/modernizzazioni fuori dal goal applicativo.

Quando due task condividono lo stesso checkout/build/device e lo stesso failure domain, consolidare i gate comuni. Non creare mega-task per obiettivi indipendenti.

## Contratto prompt

Ogni file in `prompts/` deve essere autosufficiente e contenere solo ciò che serve al task:

- `PROMPT_ID`, progetto, modello/reasoning;
- goal e acceptance criteria;
- starting point autoritativo e workdir;
- scope/non-goal;
- test/verifiche proporzionati al rischio;
- recovery autonomo dai failure;
- libertà esplicita di modificare qualunque codice/test/config/helper/documentazione tecnica in-scope necessario al goal;
- libertà di cambiare piano o metodo quando lo starting point diventa falso, purché restino invariati goal, acceptance criteria e vincoli di sicurezza/dati;
- comandi terminali PASS/BLOCKED/FAIL.

Non copiare interi protocolli globali dentro ogni prompt. Includere solo le regole realmente applicabili al task. Se starting point/path/helper/test sono già noti, evitare rediscovery generale **finché l'evidenza non smentisce lo starting point**. In quel caso Codex ha autonomia per fare discovery mirata e correggere codice/test/config/helper adiacenti necessari allo stesso goal. **Goal e acceptance criteria sono il contratto; i passi del prompt sono solo un piano iniziale e Codex può sostituirli con un percorso migliore.** Un prompt non deve trasformare un mezzo operativo (branch, helper, lease, test specifico, ordine dei passi) in un blocker terminale quando esiste un'alternativa sicura che porta allo stesso risultato.

Non usare **overlay di precedenza** del tipo “questa sezione prevale sulle istruzioni successive” per rattoppare un prompt già materializzato: aumenta token e ambiguità. Se una policy cambia in modo da rendere incoerente un prompt **ancora pending e non avviato**, si può creare una nuova materializzazione con nuovo PROMPT_ID e supersedere la vecchia. Se invece il prompt è `running`, è **immutabile per il writer durante l'esecuzione** per tutto ciò che può cambiare il lavoro: modello, posizione, dipendenze, tag, relazioni e testo canonico non si modificano, né il prompt viene superseduto/spostato. `explanation` è l'unica eccezione perché è solo testo user-facing della dashboard e può essere riscritta in forma più chiara senza cambiare l'esecuzione. L'unica transizione di stato ammessa è la finalizzazione esplicita tramite `roadmap_finish.py` / `roadmap_result.py`, che è autorevole e applica subito completed/failed/blocked/cancelled; `codex-usage` registra poi telemetria e anomalie senza trattenere il prompt in `running`. Non correggere in-place il testo di un PROMPT_ID già materializzato.

Contratto esecutivo completo: [[STANDARD_PROMPT|Esecuzione Codex]].

## PROMPT_ID

Regola assoluta: **1 prompt materializzato = 1 PROMPT_ID unico e immutabile di 6 cifre**.

Una revisione/retry materializzata riceve un nuovo ID. La genealogia usa `PARENT_PROMPT_ID`; gli ID conclusi non vengono riciclati.

L'allocatore canonico MegaVault è l'autorità; non inventare ID manualmente.

## Modello/reasoning

- GPT-5.6 Luna `low`: task semplici/localizzati/meccanici.
- GPT-5.6 Terra `medium`: default per lavoro Codex non banale.
- GPT-5.6 Sol `medium`: solo per debugging ambiguo/difficile, decisioni architetturali, modifiche trasversali complesse o rischio elevato.
- `high`: solo con necessità concreta.

Prima di aumentare il modello/reasoning, ridurre scope, discovery, output e round-trip.

## Esecuzione manuale

Apri Workflowy → **Ready** e usa `🚀 Avvia`: il launcher deve aprire una nuova thread Codex in ChatGPT Desktop nel progetto/repo canonico, impostare esattamente modello e reasoning indicati e inserire il prompt senza inviarlo. `📋 Copia prompt` resta il fallback manuale. Non usare Work né una chat ChatGPT normale per i task della roadmap. Se progetto, modello o reasoning richiesti non sono selezionabili, il launcher deve fallire chiuso senza scegliere automaticamente un'alternativa. Prima di qualunque lavoro sul progetto, Codex deve eseguire `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id <PROMPT_ID>` e procedere solo se il writer conferma `running`. Non inviare meta-prompt e non far rileggere roadmap/README/MegaVault se il prompt contiene già lo starting point necessario. `MegaVault=FAST` con progetto/workdir già risolti non autorizza un dump preventivo di MegaVault, memoria o storico: si consulta solo un fatto specifico se emerge davvero come mancante.

Default: un task per sessione; stesso thread solo per una continuazione diretta che riusa davvero contesto utile.

Durante il task, un failure locale correggibile non deve trasformarsi in un nuovo prompt: Codex deve correggerlo e continuare. Se il failure è causato da tooling/protocollo/helper del progetto ed è sicuro correggerlo in-scope, Codex può correggere anche quello e riprendere il goal. BLOCKED/FAIL sono terminali solo per blocker esterni/safety o recovery realmente esaurito; un piano diventato obsoleto, una lease orfana recuperabile, un helper difettoso, CI pending/in-progress o correggibile, oppure una divergenza Git riconciliabile non bastano. La prontezza delle dipendenze è decisa dal DB e da `roadmap_start.py`: riferimenti storici del tipo “dopo PROMPT_ID X” dentro vecchi prompt non devono essere ricontrollati autonomamente se il claim remoto del prompt corrente è già stato accettato.

Un PASS deve dimostrare tutti gli acceptance criteria obbligatori. `NOT VERIFIED`, output perso/non recuperato o gate non eseguito non sono compatibili con PASS: Codex deve recuperare un'evidenza equivalente in modo bounded oppure usare un esito terminale coerente.

Dopo PASS: finalizzazione e stop immediato.

## Verifica manutenzione

Quando si modifica il motore della roadmap:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 tools/roadmap_db.py --repo . verify
```

Non creare un task Codex soltanto per verificare una modifica remota se test/CI remoti sono sufficienti.
