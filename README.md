# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]] · [[STANDARD_PROMPT|Esecuzione Codex]]

Coda di lavoro **solo per attività che richiedono Codex**: filesystem/toolchain locale, device/emulatore, VM, segreti/config runtime, servizi locali o altre risorse non disponibili nella normale chat. Se una modifica può essere completata direttamente sui repository remoti in chat, va fatta subito e **non** aggiunta alla roadmap.

## Struttura
- `roadmap.md`: lista numerata dei soli pendenti, una riga per task.
- `spiegazioni.md`: stessa sequenza, spiegazioni semplici.
- `prompts/*.md`: task autosufficienti da incollare direttamente in Codex.
- `completed/*.md`: task conclusi con PASS.
- `tools/roadmap_guard.py`: selezione unattended/finalizzazione canonica.

`spiegazioni.md` usa `# | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt`; ordine, reasoning e link devono coincidere con la roadmap.

## Regola di ammissione — niente spirali
Un nuovo task entra in roadmap solo se soddisfa **entrambi**:
1. richiede davvero una risorsa locale non disponibile in chat;
2. risolve un bug/blocco, rischio dati, requisito funzionale o verifica indispensabile prima di una release.

Non creare task Codex per:
- micro-ottimizzare un helper/monitor/gate che ha già PASS;
- misurare il costo del prompt precedente;
- validare una micro-ottimizzazione appena introdotta da ChatGPT quando test statici/remoti sono sufficienti;
- investigare colli di bottiglia solo potenziali o senza impatto pratico osservato;
- ripetere un PASS con un helper “ancora più efficiente”.

**PASS chiude il sottosistema.** Un follow-up dopo PASS è ammesso solo con nuova evidenza concreta emersa nell'uso reale. Le ottimizzazioni marginali si riportano in chat e si fermano lì.

Quando due task dello stesso repo/campagna richiedono lo stesso checkout/build/emulatore e hanno failure domain compatibili, accorpa i gate nel task funzionale invece di creare un prompt di sola verifica separato. Non accorpare invece migrazioni/rischio dati con feature ordinarie se questo rende il failure domain ambiguo.

## Contratto prompt
Ogni prompt deve bastare da solo insieme alle regole globali già caricate. Deve dichiarare almeno metadata, goal, starting point verificato, scope/non-goal, verification, stop e comando di finalizzazione. Vietati inventory/audit generali quando file/boundary sono già noti.

Tipi:
- **Prompt**: lavoro già delimitato, diff/test minimi.
- **Goal**: risultato cross-component, ma scope e stop restano espliciti.

### Modello/reasoning
- GPT-5.5 `low`: default per gate deterministici, test/build/ADB mirati e task localizzati con stop chiaro.
- GPT-5.5 `medium`: solo quando serve diagnosi runtime non banale o scelta tra più fix plausibili.
- GPT-5.6 Sol `medium`: schema/migrazioni, rischio dati, undo/audit o architettura realmente cross-module.
- `high`: solo con difficoltà concreta non gestibile bene a medium.

Non usare GPT-5.6 o reasoning superiore solo perché il task è lungo: prima riduci scope, round-trip e contesto.

## Esecuzione manuale
Apri il primo file indicato da `roadmap.md`, imposta modello/reasoning dai metadata e incolla **solo quel file**. Non inviare meta-prompt, non far leggere roadmap/README/spiegazioni e non eseguire `select` nelle sessioni manuali.

Default: un task per sessione. Raggruppa letture/comandi indipendenti; non ripetere test PASS; retry solo dopo nuova evidenza o stato cambiato; stop immediato a PASS/BLOCKED/FAIL. Per build/comandi lunghi già avviati, preferisci una sola attesa bloccante o controlli radi: niente polling ravvicinato né messaggi che riportano solo stato invariato.

**Ordine dei gate:** esegui sempre prima i controlli più economici e indipendenti dal device (static check/unit test/build), poi avvia emulatore/device/servizi solo se quei gate sono PASS. Se l'APK è già stato costruito nello stesso task, installa esattamente quell'artefatto senza una seconda invocazione Gradle. Fanno eccezione solo i test il cui prerequisito tecnico richiede esplicitamente il runtime prima del gate host.

**Disciplina dei retry Gradle:** un gate aggregato serve per scoprire problemi e per la conferma finale, non come inner loop. Se un gate aggregato fallisce:
1. leggi in una volta l'intero report disponibile del task/modulo fallito e raccogli tutti i blocker dello stesso failure domain;
2. applica i fix in batch quando indipendenti;
3. rilancia solo il leaf task fallito (`compile`, test mirato, `lint<Variant>` o modulo specifico), non l'intero `check`/`assemble`;
4. quando tutti i leaf failure sono PASS, esegui **un solo gate aggregato finale**.

Non rilanciare `./gradlew check ...` dopo ogni singolo lint/compile fix. Obiettivo normale: al massimo un gate aggregato di discovery + uno finale; un terzo è ammesso solo se il finale espone un failure domain realmente nuovo che non era presente nei report precedenti. Se il prompt è una fase intermedia e non richiede lint globale, preferisci test mirati + build dell'artefatto necessario e lascia il gate globale alla fase finale/release.

## Campagne
Usa `campaign_id` per più fasi dello stesso prodotto quando questo evita release ripetute.

Per PersonalHub:
- le fasi intermedie fanno implementazione, test mirati, eventuale QA isolata e push;
- **non** incrementano `version.txt`, non installano il package reale Pixel e non inviano APK;
- l'ultima fase fa un solo bump, gate finali consolidati, un solo APK finale, una sola installazione Pixel e una sola Telegram delivery;
- una campagna PH deve essere seriale: niente task PH concorrenti.

Non creare mega-task se le fasi hanno failure domains indipendenti; consolida build/install/delivery e gate comuni. Una verifica locale di fix già pushati va assorbita nella fase funzionale successiva dello stesso repo quando può condividere lo stesso host gate e la stessa QA.

## PASS
Ogni prompt include:
```bash
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id PROMPT_ID --dry-run && \
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id PROMPT_ID
```

`status=completed` + `push_verified=git_push_exit_0` è prova terminale. Dopo non eseguire `git status`, `rev-parse`, `ls-remote`, pull/fetch o verifiche equivalenti sulla roadmap e non aprire il task successivo.

## BLOCKED/FAIL
Non archiviare né avanzare. Riporta solo blocker/evidenza minima e fermati.

## `roadmap_guard.py`
`select` è solo fallback unattended. `complete` lavora su worktree isolato, accetta soltanto il primo pendente, limita i path modificabili e fa push fast-forward senza force. Il worktree principale può essere sporco e non va stashato/reset.

Eccezione di bookkeeping: se l'implementazione di un prompt è **già stata completata e pushata**, ma nel frattempo la roadmap è avanzata e `complete` restituisce `prompt_identity_mismatch`, non replicare manualmente la logica del guard. Usa:
```bash
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap reconcile --prompt-id PROMPT_ID --dry-run && \
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap reconcile --prompt-id PROMPT_ID --confirm-executed
```
`reconcile` non può sostituire `complete` per il task attualmente selezionato, richiede conferma esplicita prima di mutare la roadmap ed è idempotente se il prompt è già in `completed/`.

Prima di modificare guard/workflow:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Manutenzione
Quando aggiorni la roadmap:
- mantieni roadmap/spiegazioni/prompt pendenti 1:1;
- elimina dal prompt facts ormai già implementati o verificabili automaticamente;
- preferisci test automatici a QA manuale ripetitiva;
- sposta build/device/delivery alla fase finale di una campagna quando sicuro;
- non aggiungere task che ChatGPT può già completare direttamente sui repo remoti;
- non assorbire task già in esecuzione;
- non usare la roadmap come backlog generico: deve restare una coda Codex minima e operativa;
- dopo un PASS, non cercare “il prossimo collo di bottiglia” salvo evidenza concreta di malfunzionamento o rischio.
