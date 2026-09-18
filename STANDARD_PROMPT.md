# Esecuzione Codex della roadmap

> `roadmap.sqlite` è la source of truth. Le viste Markdown sono generate.

## Percorso normale

Per una sessione Codex Desktop:

1. scegli il primo task lanciabile dalla roadmap;
2. imposta progetto, modello e reasoning indicati;
3. incolla **solo il file `prompts/<task>.md`**.

Non usare launcher intermedi e non far leggere a Codex README, roadmap, spiegazioni, MegaVault o memoria quando il prompt contiene già lo starting point necessario. In particolare, con `MegaVault=FAST`, `project_id`/workdir già risolti e nessun fatto canonico mancante, **non leggere né dumpare MegaVault protocol, MEMORY o rollout summary**: FAST significa usare solo l'eventuale fatto specifico che manca, non caricare contesto preventivo.

Riusa la chat precedente solo quando il contesto non materializzato riduce davvero discovery o rischio. Dopo una sessione lunga di debugging/retry, se il follow-up ha già uno starting point completo, preferisci una **nuova chat**: evita di trascinare un contesto enorme soltanto perché esiste una relazione padre/figlio.

## Contratto minimo del prompt

Un prompt deve essere autosufficiente ma piccolo. Deve contenere soltanto:

- `PROMPT_ID`, progetto, modello/reasoning;
- goal e acceptance criteria;
- checkout/workdir e starting point già verificati;
- scope e non-goal;
- test/verifiche minime sufficienti;
- recovery dai failure;
- finalizzazione PASS/BLOCKED/FAIL.

**Non copiare interi protocolli o checklist globali nel prompt.** Inserire solo le regole che cambiano concretamente l'esecuzione di quel task.

Se path, file, helper, test, servizio o device sono già noti, trattarli come autoritativi e non rifare discovery generale.

## Autonomia e recovery

**Goal + acceptance criteria definiscono lo scope; i passi del prompt sono il piano iniziale, non una whitelist di file o comandi.** Codex deve portare autonomamente il goal a termine quando può farlo in sicurezza.

Dentro lo stesso failure domain Codex è autorizzato a:
- leggere, modificare, aggiungere o rimuovere codice, test, adapter, config e documentazione tecnica necessari al goal, anche se il prompt non li nomina;
- correggere un test obsoleto o incoerente quando l'evidenza dimostra che il test, non il comportamento richiesto, è errato;
- sostituire un comando/helper/API non più valido con l'equivalente canonico corrente;
- fare discovery **mirata** aggiuntiva quando un'assunzione del prompt risulta falsa;
- gestire lock/transienti con attesa bounded, retry con stato cambiato, restart/reload di servizi in-scope e temp diagnostics;
- correggere più blocker indipendenti dello stesso dominio in batch;
- commit/pushare fix in-scope quando il repository/task lo richiede;
- proseguire automaticamente dal leaf gate corretto fino agli acceptance criteria senza chiedere conferma.

Non sono da soli motivi per BLOCKED/FAIL: simbolo/API mancante, test/compile failure, file diverso da quello atteso, helper obsoleto, warning riproducibile, remote advance riconciliabile, lock transitorio, servizio riavviabile o necessità di toccare un file adiacente.

Codex deve fermarsi solo quando serve davvero qualcosa che non può ottenere autonomamente: credenziale/permesso o decisione utente indispensabile, hardware/runtime necessario indisponibile senza alternativa, conflitto semantico sostanziale fuori scope, rischio concreto di perdita dati, azione distruttiva/pubblicazione esterna non autorizzata o redesign materialmente diverso dal goal.

Recovery:
- diagnosticare il minimo artefatto utile;
- correggere la causa più locale supportata dall'evidenza;
- rilanciare prima il leaf gate fallito;
- riprendere il goal originale;
- niente retry identici senza nuova evidenza/stato cambiato;
- niente audit, cleanup o modernizzazione non necessari al goal.

`FAIL` è ammesso solo dopo recovery ragionevole realmente tentato e documentato. `BLOCKED` è riservato ai blocker esterni/safety sopra.

### Evidenza terminale

`PASS` richiede evidenza esplicita per **ogni acceptance criterion obbligatorio**. Un report che contiene `NOT VERIFIED`, `non recuperato`, `unknown`, `not run` o equivalente per un criterio richiesto non può dichiarare PASS. Se l'output di un gate si perde ma il gate è riproducibile, rieseguilo una sola volta in modo più robusto; se non è riproducibile, riporta l'esito coerente con ciò che è realmente dimostrato. Non inferire PASS da processi terminati, stato vicino o assenza di errori.

Dopo PASS: stop immediato.

## Efficienza

Regole di default:

- partire dal workdir e dai file direttamente pertinenti;
- riusare evidenza già verificata nella stessa sessione;
- raggruppare letture e controlli indipendenti compatibili;
- evitare dump ampi di repository, log, XML, tree o database;
- dopo un failure leggere il minimo failure artifact e rilanciare solo il test/leaf gate interessato;
- eseguire gate economici host/statici prima di device/servizi costosi;
- non ripetere gate PASS se il diff successivo non li invalida;
- usare helper/runner canonici già noti senza probe equivalenti;
- un comando lungo già avviato va atteso sullo stesso processo/sessione, non controllato con `pgrep`, journal o polling come proxy; se il tool consente timeout/wait esplicito, impostalo una volta in modo coerente con la durata attesa; se l'output può perdersi per il limite foreground, catturalo in un file temporaneo e leggilo una sola volta a fine processo;
- niente comandi no-op o verifiche di rassicurazione dopo PASS.

Per task localizzati l'obiettivo è ridurre soprattutto i round-trip modello↔tool. Un budget di tool-call è un obiettivo, **mai un limite di autonomia**: se emerge nuova evidenza concreta, Codex può superarlo per risolvere lo stesso goal invece di terminare prematuramente.

## Git

Usare il checkout canonico indicato nel prompt.

Quando serve sincronizzare:
- una sola fotografia iniziale dello stato;
- fast-forward/sync minimo sicuro;
- una sola verifica remota finale prima del commit/push.

Dirty work non sovrapposto o remote advance non sono blocker automatici. Non usare stash/reset distruttivi per ottenere artificialmente un worktree pulito.

Evitare commit intermedi se il task richiede un solo commit finale e il checkout è soggetto ad autosync.

Se il recovery modifica file tracciati del repository target, `PASS` richiede che la modifica necessaria sia **committata e pushata** sul branch previsto, salvo task esplicitamente local-only. Solo in quel caso, prima della finalizzazione, verificare in modo mirato che non restino diff tracciati in-scope e che il push sia riuscito. Un fix necessario rimasto soltanto nel checkout locale non è PASS.

## Test e runtime

Usare prima il test più economico che può falsificare la modifica.

Dopo un failure:
1. leggere il report mirato;
2. correggere in batch i blocker dello stesso failure domain;
3. rilanciare il leaf test;
4. eseguire un solo gate aggregato finale se necessario.

Device/emulatore/servizi si avviano solo quando i gate host pertinenti sono PASS, salvo prerequisito tecnico contrario.

## Campagne e PersonalHub

Task indipendenti possono procedere in parallelo solo su branch separati quando il repository lo consente.

Per PersonalHub:
- implementazioni indipendenti possono usare branch dedicati;
- integrazione in `main`, QA condivisa e release restano seriali;
- le fasi intermedie non duplicano bump/versione, APK finale, installazione Pixel o delivery finale;
- branch integrati vengono eliminati subito.

## Finalizzazione roadmap

PASS:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id <PROMPT_ID> --confirm-executed
```

BLOCKED/FAIL:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id <PROMPT_ID> --result BLOCKED --confirm-executed
# oppure --result FAIL
```

Questi comandi inviano una mutazione idempotente al writer remoto. Non modificano direttamente il checkout locale della roadmap.

Un retry/fix materializzato usa sempre un nuovo PROMPT_ID collegato al padre.

La prima riga finale deve essere `RESULT=PASS|BLOCKED|FAIL`, seguita da un report conciso con modifiche, test, commit/push e blocker residui.

## Fallback unattended

Solo quando Codex deve selezionare autonomamente il task:

```text
Esegui SOLO il primo task pendente di gernalix/codex-roadmap. Come prima tool-call esegui `python3 tools/roadmap_guard.py select`, usa `prompt_content` come task completo e non rileggere README/roadmap/spiegazioni salvo incoerenza concreta. Mantieni scope stretto, recupera i failure con fix minimi e fermati a PASS o a un vero BLOCKED/FAIL terminale.
```

Il fallback non è il percorso manuale normale.
