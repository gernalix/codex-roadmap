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

## Contratto prompt
Ogni prompt deve bastare da solo insieme alle regole globali già caricate. Deve dichiarare almeno metadata, goal, starting point verificato, scope/non-goal, verification, stop e comando di finalizzazione. Vietati inventory/audit generali quando file/boundary sono già noti.

Tipi:
- **Prompt**: lavoro già delimitato, diff/test minimi.
- **Goal**: risultato cross-component, ma scope e stop restano espliciti.

### Modello/reasoning
- GPT-5.5 `low`: task meccanico/localizzato con poche decisioni.
- GPT-5.5 `medium`: default per runtime, ADB, systemd, Git, filesystem, tool esterni e diagnosi mirate.
- GPT-5.6 Sol `medium`: schema/migrazioni, rischio dati, undo/audit o architettura realmente cross-module.
- `high`: solo con difficoltà concreta non gestibile bene a medium.

Non usare GPT-5.6 solo perché il task è lungo: prima riduci scope e contesto.

## Esecuzione manuale
Apri il primo file indicato da `roadmap.md`, imposta modello/reasoning dai metadata e incolla **solo quel file**. Non inviare meta-prompt, non far leggere roadmap/README/spiegazioni e non eseguire `select` nelle sessioni manuali.

Default: un task per sessione. Raggruppa letture/comandi indipendenti; non ripetere test PASS; retry solo dopo nuova evidenza o stato cambiato; stop immediato a PASS/BLOCKED/FAIL. Per build/comandi lunghi già avviati, preferisci una sola attesa bloccante o controlli radi: niente polling ravvicinato né messaggi che riportano solo stato invariato.

## Campagne
Usa `campaign_id` per più fasi dello stesso prodotto quando questo evita release ripetute.

Per PersonalHub:
- le fasi intermedie fanno implementazione, test mirati, eventuale QA isolata e push;
- **non** incrementano `version.txt`, non installano il package reale Pixel e non inviano APK;
- l'ultima fase fa un solo bump, gate finali consolidati, un solo APK finale, una sola installazione Pixel e una sola Telegram delivery;
- una campagna PH deve essere seriale: niente task PH concorrenti.

Non creare mega-task se le fasi hanno failure domains indipendenti; consolida solo build/install/delivery e gate comuni.

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
- mantieni roadmap/spiegazioni/prompt 1:1;
- elimina dal prompt facts ormai già implementati o verificabili automaticamente;
- preferisci test automatici a QA manuale ripetitiva;
- sposta build/device/delivery alla fase finale di una campagna quando sicuro;
- non aggiungere task che ChatGPT può già completare direttamente sui repo remoti;
- non assorbire task già in esecuzione;
- non usare la roadmap come backlog generico: deve restare una coda Codex minima e operativa.
