# codex-roadmap

[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]] · [[STANDARD_PROMPT|Esecuzione Codex]]

Coda di lavoro **solo per attività che richiedono Codex**: filesystem/toolchain locale, device/emulatore, VM, segreti/config runtime, servizi locali o altre risorse non disponibili nella normale chat. Se una modifica può essere completata direttamente sui repository remoti in chat, va fatta subito e **non** aggiunta alla roadmap.

## Struttura
- `roadmap.md`: lista numerata dei soli pendenti, una riga per task.
- `spiegazioni.md`: stessa sequenza, spiegazioni semplici.
- `prompts/*.md`: task autosufficienti da incollare direttamente in Codex.
- `completed/*.md`: task conclusi con PASS.
- `tools/roadmap_guard.py`: primitive fail-closed per selezione/completamento/reconcile.
- `tools/roadmap_finish.py`: finalizzatore PASS race-safe da usare nei prompt normali.

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
- ripetere un PASS con un helper “ancora più efficiente”;
- modificare soltanto repository/workflow/Actions GitHub quando ChatGPT può farlo direttamente tramite GitHub. Se serve prima un audit locale, Codex deve produrre un handoff strutturato e fermarsi lì.

**PASS chiude il sottosistema.** Un follow-up dopo PASS è ammesso solo con nuova evidenza concreta emersa nell'uso reale. Le ottimizzazioni marginali si riportano in chat e si fermano lì.

Quando due task dello stesso repo/campagna richiedono lo stesso checkout/build/emulatore e hanno failure domain compatibili, accorpa i gate nel task funzionale invece di creare un prompt di sola verifica separato. Non accorpare invece migrazioni/rischio dati con feature ordinarie se questo rende il failure domain ambiguo.

Quando due fasi consecutive della stessa campagna richiedono lo stesso device/emulatore, concentra la QA device non indispensabile alla prima fase nella prima fase successiva che deve già avviare quel target. La fase precedente resta host-only quando compile/test host forniscono sicurezza sufficiente.

## Contratto prompt
Ogni prompt deve bastare da solo insieme alle regole globali già caricate. Deve dichiarare almeno metadata, goal, starting point verificato, scope/non-goal, verification, stop e comando di finalizzazione. Vietati inventory/audit generali quando file/boundary sono già noti.

Tipi:
- **Prompt**: default. Usalo quando il lavoro è delimitato e può ragionevolmente concludersi in un singolo turno operativo, anche se tocca più componenti.
- **Goal**: usalo solo quando la persistenza multi-turn è concretamente utile al risultato (per esempio campagne seriali lunghe multi-repo o verifiche che devono proseguire attraverso continuazioni). Complessità o rischio, da soli, non giustificano Goal.

### Modello/reasoning
- GPT-5.6 Luna `low`: task semplici, localizzati o meccanici, gate deterministici, test/build/ADB mirati e implementazioni con soluzione evidente.
- GPT-5.6 Terra `medium`: **default** per il lavoro Codex non banale, inclusi debugging runtime già pre-localizzato, lifecycle, migrazioni/schema delimitati e audit guidati da scanner/test deterministici.
- GPT-5.6 Sol `medium`: solo quando la capacità aggiuntiva è concretamente utile, per esempio debugging ambiguo/difficile, decisioni architetturali, modifiche trasversali complesse o task ad alto rischio che Terra non gestirebbe con sufficiente affidabilità.
- `high`: solo con difficoltà concreta non gestibile bene a medium.

Una migrazione, un audit o un task lungo **non giustificano da soli Sol**. Prima riduci scope, discovery, round-trip e output tool; passa da Terra a Sol solo se resta complessità o rischio di ragionamento reale.

## Esecuzione manuale
Apri il primo file indicato da `roadmap.md`, imposta modello/reasoning dai metadata e incolla **solo quel file**. Non inviare meta-prompt, non far leggere roadmap/README/spiegazioni e non eseguire `select` nelle sessioni manuali.

Default: un task per sessione. Raggruppa letture/comandi indipendenti; non ripetere test PASS; retry solo dopo nuova evidenza o stato cambiato; stop immediato a PASS/BLOCKED/FAIL. Per build/comandi lunghi già avviati, preferisci una sola attesa bloccante o controlli radi: niente polling ravvicinato né messaggi che riportano solo stato invariato.

## Diagnostica runtime a basso round-trip
Per task locali/VM/servizi, il costo principale è spesso il numero di round-trip modello↔tool, non i token uncached. Quindi:
- se prompt/starting point forniscono path, helper, unit, DB, monitor ID o schema già verificati, trattali come autoritativi e non rifare discovery generale;
- raggruppa nello stesso batch i controlli indipendenti; evita sequenze di micro-comandi quando una sola query/lettura mirata può rispondere;
- **worktree dirty non significa automaticamente `BLOCKED`**: fotografa una volta i dirty path e i file che il task o il fast-forward remoto toccherebbero. Se gli insiemi sono disgiunti e l'operazione resta deterministicamente sicura, procedi senza modificare il lavoro utente; blocca solo su overlap, divergenza o ambiguità concreta. Non usare stash/reset/checkout distruttivi per ottenere artificiosamente un worktree pulito;
- SQLite: non indovinare colonne. Se lo schema non è già noto, fai **una sola** `PRAGMA table_info`/schema query e poi la query corretta. Per WAL read-only usa helper del progetto o URI `mode=ro&immutable=1`, non tentativi `sqlite3 -readonly` destinati a creare `-shm`;
- se è già noto un helper privilegiato/canonico (SSH wrapper, installer Android, emulator facade, ecc.), usalo direttamente: niente probe preliminari con permessi insufficienti o reimplementazioni manuali;
- limita `rg`, `journalctl`, tree/XML/log e query a file/unit/finestra pertinenti; evita output da migliaia di token e output troncati. Un dump ampio è ammesso solo dopo failure concreta di una query stretta;
- usa subito l'invocazione test canonica già dichiarata (`PYTHONPATH`, cwd, serial, runner). Non eseguire prima una variante nota destinata a fallire per “provare”; dopo un failure cambia approccio usando la nuova evidenza, niente retry quasi equivalenti;
- dopo PASS dei criteri richiesti non fare audit, status o readback aggiuntivi “per sicurezza”.

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
- l'ultima fase non ripete automaticamente gate già PASS delle fasi precedenti: li riesegue solo se il diff finale tocca i file, dipendenze o boundary che quei gate coprivano;
- una campagna PH deve essere seriale: niente task PH concorrenti.

Non creare mega-task se le fasi hanno failure domains indipendenti; consolida build/install/delivery e gate comuni. Una verifica locale di fix già pushati va assorbita nella fase funzionale successiva dello stesso repo quando può condividere lo stesso host gate e la stessa QA.

## PASS
Ogni prompt normale deve finalizzare con **una sola invocazione** race-safe:
```bash
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id PROMPT_ID --confirm-executed
```

`roadmap_finish.py` usa `complete` nel caso normale e passa automaticamente al `reconcile` canonico solo se la roadmap è avanzata mentre il task era in esecuzione. Non anteporre un dry-run nel percorso normale: raddoppia processi/round-trip e apre una finestra di race senza aggiungere sicurezza al guard fail-closed.

`status=completed|already_completed` con `finish_mode=complete|reconcile` e, quando c'è una mutazione, `push_verified=git_push_exit_0` è prova terminale. Dopo non eseguire `git status`, `rev-parse`, `ls-remote`, pull/fetch o verifiche equivalenti sulla roadmap e non aprire il task successivo.

## BLOCKED/FAIL
Non invocare il finalizzatore, non archiviare né avanzare. Riporta solo blocker/evidenza minima e fermati.

## `roadmap_guard.py` / `roadmap_finish.py`
`select` è solo fallback unattended. `complete` e `reconcile` lavorano fail-closed; il worktree principale può essere sporco e non va stashato/reset. I prompt normali non devono orchestrare manualmente `complete`→`reconcile`: lo fa `roadmap_finish.py` nello stesso processo.

Usa direttamente `roadmap_guard.py` solo per diagnostica/manutenzione del guard o per il fallback unattended documentato in `STANDARD_PROMPT.md`.

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
