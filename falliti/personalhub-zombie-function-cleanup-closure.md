PROMPT_ID=793678 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Chiudi SOLO la bonifica dei residui “app standalone” nei moduli PersonalHub già iniziata da ChatGPT. Parti dalla PR #20 / branch `cleanup/zombie-feature-functions-v57` e porta il lavoro a PASS: nessuna implementazione duplicata per-modulo di import/export DB, backup/restore, sync remoto, Git data transport o infrastruttura equivalente deve restare nel codice/UI quando l'autorità è globale in PersonalHub.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`, project_id=49;
- branch candidato già esistente: `cleanup/zombie-feature-functions-v57`;
- PR: #20 verso `main`;
- baseline minima del branch: `9eb490fcf090c9e86fe11cea7161913f378e3ed3`;
- `version.txt=57` è già stato incrementato: NON incrementarlo ancora;
- ChatGPT ha già rimosso ~4.6k righe: backup/restore Places e People, import/export Sostanze, backup CSV WordPulse, remote sync Timer, Git/FinanceExchange Soldi, feature backup/data-extraction XML, vari compatibility alias DB;
- architecture boundary CI era già PASS; i precedenti failure di compilazione per `LuoghiDatabase` / `PersistentMutationTracker` / `RemoteSyncScheduler` sono già stati corretti sul branch dopo quei run;
- il global Data Explorer è una funzione globale valida: i moduli possono avere entrypoint che lo aprono, ma non implementazioni locali duplicate;
- receipt OCR/import di Soldi è dominio, NON database import/export globale e va preservato;
- TimeFenceRestoreReceiver è restore di alarm runtime, non DB restore: preservalo.

# Esecuzione minima
1. Esegui `roadmap_start.py` e continua sul branch esistente. Un solo fetch iniziale. Non fare audit Git generale.
2. Parti dal diff PR #20 e dal CODE_MAP. Fai una ricerca bounded SOLO nei moduli per segnali standalone: backup/restore DB, import/export DB/CSV, SAF/file-picker di backup, feature-local Datasette/remote sync, feature-local Git transport, feature Room DB aliases/builders/schemas, dipendenze ormai inutili collegate a questi percorsi. Non esplorare business logic non correlata.
3. Correggi ogni riferimento residuo causato dalle rimozioni. Rimuovi anche UI, stato, stringhe/resources, helper, test, dipendenze Gradle, schemi Room legacy e righe CODE_MAP/documentazione che descrivono funzioni cancellate, ma SOLO se non hanno più consumer/owner reale.
4. Non eliminare funzionalità di dominio solo perché contengono parole import/restore/sync: esempi da preservare sono receipt import Soldi, restore di alarm Timer, sync interno UI/runtime non remoto, Data Explorer globale.
5. Prima prova compile leaf mirate dei moduli toccati; usa il primo failure concreto per fix leaf. Poi esegui una sola aggregazione finale:
   - `:feature:luoghi:compileDebugKotlin`
   - `:feature:multitimetracker:compileDebugKotlin`
   - `:feature:sostanze:compileDebugKotlin`
   - `:feature:supercontacts:compileDebugKotlin`
   - `:feature:wordpulse:compileDebugKotlin`
   - `:feature:soldi:compileDebugKotlin`
   - `:app:compileDebugKotlin`
   - `checkArchitectureBoundaries`
   e i test unitari mirati direttamente colpiti dalle rimozioni. Niente suite ridondanti dopo PASS.
6. Verifica la PR/CI corrente una sola volta dopo il push finale. Se una pipeline fallisce, correggi solo il failure domain reale e riesegui/ripusha; niente retry identico senza nuova evidenza.
7. Sotto lease PH, fai review semantica del diff contro il `main` più recente. Se compatibile e gate PASS, integra PR #20 in `main`, elimina subito branch remoto+locale e rilascia lease. Se `main` è avanzato, riconcilia solo gli overlap necessari al goal.
8. Nessun APK/release/device QA salvo che un acceptance test esistente richieda esplicitamente runtime per una regressione causata da questa modifica.

# Acceptance
PASS solo se:
- nessuna UI per-modulo offre import/export DB, backup/restore DB o sync/Git duplicati;
- nessun runtime per-modulo esegue tali duplicati;
- nessun file/helper/dependency/schema legacy resta senza consumer reale per queste funzioni;
- funzioni di dominio legittime sopra indicate restano intatte;
- compile/test/architecture gate pertinenti PASS;
- CI finale della PR non ha failure causati dal branch;
- PR #20 è integrata semanticamente in main e il branch è eliminato.

# Non-goal
Niente refactor, cleanup estetico, modernizzazione, redesign UI, cambio schema dati non necessario, nuove feature, ottimizzazione APK o audit di codice non correlato.

# Stop
Dopo PASS finalizza con:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 793678 --confirm-executed`
Poi stop. Output massimo 8 righe: PROMPT_ID, RESULT, HEAD, REMOVED_RESIDUES, TESTS, CI, MERGE, BLOCKER.
