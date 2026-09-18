# Esecuzione Codex della roadmap

> `roadmap.sqlite` è la source of truth. Le viste Markdown sono generate.

## Percorso normale

Per una sessione Codex Desktop:

1. scegli il primo task lanciabile dalla roadmap;
2. imposta progetto, modello e reasoning indicati;
3. incolla **solo il file `prompts/<task>.md`**.

Non usare launcher intermedi e non far leggere a Codex README, roadmap, spiegazioni, MegaVault o memoria quando il prompt contiene già lo starting point necessario.

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

## Recovery

Goal + acceptance criteria sono il contratto terminale. Un errore intermedio è evidenza, non automaticamente un esito terminale.

- diagnosticare il minimo artefatto utile;
- applicare il fix minimo nello stesso failure domain;
- rilanciare prima il leaf gate fallito;
- riprendere il goal originale;
- niente retry identici senza nuova evidenza;
- niente audit, cleanup, refactor o modernizzazione collaterali.

`BLOCKED` è riservato a dipendenze esterne/umane indispensabili, runtime richiesto indisponibile senza alternativa valida, concorrenza unsafe o azioni distruttive/ambigue che richiedono consenso.

`FAIL` è ammesso solo quando il recovery ragionevole in-scope è esaurito o l'unico fix residuo sarebbe unsafe/materialmente fuori scope.

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
- un comando lungo già avviato va atteso, non controllato con polling ravvicinato;
- niente comandi no-op o verifiche di rassicurazione dopo PASS.

Per task localizzati l'obiettivo è ridurre soprattutto i round-trip modello↔tool. Un budget di tool-call è un obiettivo, non una ragione per sacrificare correttezza.

## Git

Usare il checkout canonico indicato nel prompt.

Quando serve sincronizzare:
- una sola fotografia iniziale dello stato;
- fast-forward/sync minimo sicuro;
- una sola verifica remota finale prima del commit/push.

Dirty work non sovrapposto o remote advance non sono blocker automatici. Non usare stash/reset distruttivi per ottenere artificialmente un worktree pulito.

Evitare commit intermedi se il task richiede un solo commit finale e il checkout è soggetto ad autosync.

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
