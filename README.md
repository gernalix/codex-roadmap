# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]] · [[prompt-registry|Registro prompt]] · [[obsidian/Dashboards/Roadmap|Dashboard Obsidian]] · [[STANDARD_PROMPT|Esecuzione Codex]] · [[SQLITE_ROADMAP|SQLite]]

Coda minima di lavoro **solo per attività che richiedono davvero Codex**: filesystem/toolchain locale, device/emulatore, VM, segreti/config runtime, servizi locali o altre risorse non disponibili nella normale chat. Se ChatGPT può completare il lavoro direttamente sui repository remoti, va fatto subito e non inserito in roadmap.

## Architettura minima

1. **MegaVault**: registry/routing dei progetti e delle invarianti globali.
2. **`roadmap.sqlite`**: unica source of truth di task, dipendenze, stato ed esecuzioni.
3. **GitHub Actions single writer**: unico writer ordinario del DB canonico e delle viste derivate.
4. **Markdown/Obsidian**: sole viste generate; non sono fonti autoritative.
5. **codex-usage-monitor**: telemetria automatica di esiti/costi; non deve creare lavoro meta salvo eccezioni reali.

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

`roadmap.sqlite` è l'unica fonte autorevole dei metadati. `roadmap.md`, `spiegazioni.md`, `prompt-registry.md` e `obsidian/` sono generate.

ChatGPT, Codex e il sync `codex-usage` inviano richieste come **GitHub Issues** con titolo `[roadmap-mutation] <request_key>` e body JSON immutabile. Ogni run del workflow drena **tutte** le mutation Issue aperte in ordine, le applica serialmente, materializza eventuali nuovi prompt, rigenera le viste, aggiorna `main` e chiude le Issue processate. Se GitHub cancella un run pending per la concurrency, la Issue resta aperta e viene raccolta automaticamente dal run successivo. Una mutation invalida/collidente viene isolata, commentata e chiusa `not_planned` senza impedire l'applicazione delle Issue valide successive.

I client non committano più file di inbox, prompt, DB o viste. Le directory `mutations/inbox/` e `mutations/applied/` restano solo come storico del trasporto precedente. Gli entry point operativi di mutazione diretta sono bloccati: `roadmap_db.py` è read-only da CLI, `import_codex_usage.py` delega a `roadmap_sync.py`, l'inbox legacy è test-only e `bootstrap_roadmap.py` richiede il contesto writer esplicito.

**Regola operativa automatica:** una richiesta umana come “aggiungi/aggiorna/sposta/chiudi questo task nella roadmap” significa sempre creare una mutation Issue tramite `tools/submit_mutation.py` (o API GitHub equivalente) e lasciare al workflow single-writer DB, prompt materializzati e viste. L'utente non deve ricordare o ripetere “usa il writer unico”. Una modifica diretta a `roadmap.sqlite`, `roadmap.md`, `spiegazioni.md`, `prompt-registry.md`, `obsidian/`, `prompts/`, `completed/` o `falliti/` per cambiare lo stato canonico è un bug di processo.

Dettagli tecnici: [[SQLITE_ROADMAP|Roadmap SQLite]].

## Viste

- `roadmap.md`: sola sequenza dei task pendenti/running.
- `spiegazioni.md`: vista operativa **minima**: task, ID, stato, progetto, chat, dipendenze, **eseguibilità corrente**, spiegazione, modello/reasoning e tipo.
- `prompt-registry.md`: storico completo, inclusi esiti e metadati di analisi quando esistono.
- `obsidian/`: navigazione storica per prompt/progetto e dashboard.

La vista operativa non deve duplicare dati storici che non servono a scegliere o lanciare il prossimo task.

### `spiegazioni.md`

È scritto per Daniele, non per uno sviluppatore. Ogni spiegazione deve essere comprensibile senza aprire il prompt: massimo tre frasi brevi in italiano quotidiano, nello schema **“Fa X. Serve perché Y. Richiede Codex perché Z.”**. Evitare nomi di classi/file, gergo architetturale e dettagli di implementazione salvo quando sono indispensabili per capire il risultato.

La colonna **Eseguibile ora?** deve permettere di vedere a colpo d'occhio cosa si può lanciare: **Sì** solo se tutte le dipendenze sono completate e non esiste un prerequisito manuale registrato; altrimenti mostra cosa manca.

I dettagli tecnici completi appartengono al file in `prompts/`.

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
- libertà esplicita di modificare qualunque codice/test/config in-scope necessario al goal;
- comandi terminali PASS/BLOCKED/FAIL.

Non copiare interi protocolli globali dentro ogni prompt. Includere solo le regole realmente applicabili al task. Se starting point/path/helper/test sono già noti, evitare rediscovery generale **finché l'evidenza non smentisce lo starting point**. In quel caso Codex ha autonomia per fare discovery mirata e correggere codice/test/config adiacenti necessari allo stesso goal. I passi del prompt sono un piano iniziale, non una whitelist.

Non usare **overlay di precedenza** del tipo “questa sezione prevale sulle istruzioni successive” per rattoppare un prompt già materializzato: aumenta token e ambiguità. Se una policy cambia in modo da rendere incoerente un prompt **ancora pending e non avviato**, si può creare una nuova materializzazione con nuovo PROMPT_ID e supersedere la vecchia. Se invece il prompt è `running`, è **immutabile per il writer**: nessun aggiornamento della roadmap può cambiarne stato, modello, spiegazione, posizione, dipendenze, tag o relazioni, né archiviarlo/spostarlo fuori da `prompts/`. `spiegazioni.md` deve continuare a mostrarlo con stato `running`. Anche `roadmap_result.py` non lo rimuove immediatamente: registra soltanto una richiesta terminale; il passaggio a completed/failed/blocked avviene solo quando la telemetria Codex conferma che l'esecuzione è realmente terminata. Se l'utente vuole interromperlo manualmente, fermare prima Codex; la chiusura effettiva arriverà dalla telemetria terminale. Non correggere in-place il testo di un PROMPT_ID già materializzato.

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

Apri il primo task lanciabile, imposta modello/reasoning e incolla **solo il file prompt**. Prima di qualunque lavoro sul progetto, Codex deve eseguire `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id <PROMPT_ID>` e procedere solo se il writer conferma `running`. Non inviare meta-prompt e non far rileggere roadmap/README/MegaVault se il prompt contiene già lo starting point necessario. `MegaVault=FAST` con progetto/workdir già risolti non autorizza un dump preventivo di MegaVault, memoria o storico: si consulta solo un fatto specifico se emerge davvero come mancante.

Default: un task per sessione; stesso thread solo per una continuazione diretta che riusa davvero contesto utile.

Durante il task, un failure locale correggibile non deve trasformarsi in un nuovo prompt: Codex deve correggerlo e continuare. BLOCKED/FAIL sono terminali solo per blocker esterni/safety o recovery realmente esaurito.

Un PASS deve dimostrare tutti gli acceptance criteria obbligatori. `NOT VERIFIED`, output perso/non recuperato o gate non eseguito non sono compatibili con PASS: Codex deve recuperare un'evidenza equivalente in modo bounded oppure usare un esito terminale coerente.

Dopo PASS: finalizzazione e stop immediato.

## Verifica manutenzione

Quando si modifica il motore della roadmap:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 tools/roadmap_db.py --repo . verify
```

Non creare un task Codex soltanto per verificare una modifica remota se test/CI remoti sono sufficienti.
