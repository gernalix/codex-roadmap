PROMPT_ID=825147
PROJECT=PersonalHub
MODEL=GPT-5.6 Terra
REASONING=medium
MegaVault=FAST

# Goal
Chiudere SOLO la bonifica dei residui “app standalone” nei moduli PersonalHub già iniziata nella PR #20, riconciliandola con il main corrente DOPO il PASS di 914263. Usare il single writer per-repository corrente; non fare merge o modifiche dirette del checkout canonico/main.

# Starting point
- repo: /home/daniele/projects/PersonalHub, project_id=49;
- sorgente di lavoro già fatto: PR #20, branch cleanup/zombie-feature-functions-v57, baseline 9eb490fcf090c9e86fe11cea7161913f378e3ed3;
- la PR rimuove circa 4.6k righe di backup/import/export/sync/Git feature-local duplicati;
- main può essere avanzato con 697834 e soprattutto con 914263: il loro stato/codice ha precedenza assoluta;
- Data Explorer globale, receipt OCR/import Soldi e TimeFenceRestoreReceiver sono funzionalità legittime da preservare.

# Execution
1. Avvia con roadmap_start.py. Usa ESCLUSIVAMENTE il worktree_path restituito dal single writer; non modificare il checkout canonico e non aggiornare main direttamente.
2. Un solo fetch iniziale. Confronta PR #20 con il main corrente e importa nel task branch solo le rimozioni ancora pertinenti. Non mergiare ciecamente il vecchio branch se reintrodurrebbe codice/versioni precedenti ai fix del P0.
3. Mantieni il versioning monotono del main corrente: non forzare il vecchio bump 56→57 se main è già oltre; fai al massimo il minimo bump richiesto dalle regole correnti del repo.
4. Ricerca bounded SOLO nei moduli per residui standalone: backup/restore DB, import/export DB/CSV, SAF/file-picker di backup, remote sync feature-local, Git data transport feature-local, alias/builder/schema Room legacy e risorse/dipendenze rimaste senza consumer per questi percorsi.
5. Non toccare business logic non correlata. Preserva import di dominio, restore di alarm/runtime, Data Explorer globale e sync interno UI/runtime non remoto.
6. Correggi solo riferimenti rotti dalle rimozioni. Esegui compile leaf dei moduli toccati, checkArchitectureBoundaries e test unitari direttamente colpiti; una sola aggregazione finale. Niente device QA salvo failure reale che non possa essere validato altrimenti.
7. Push del task branch e finalizzazione tramite roadmap_finish.py. Lascia al per-repository single writer PR/check/merge verso main.
8. Solo dopo merge autorevole riuscito, verifica che il contenuto utile della vecchia PR #20 sia presente; quindi chiudi la PR #20 ed elimina il vecchio branch cleanup/zombie-feature-functions-v57 se non contiene lavoro unico residuo.

# Acceptance
- nessuna UI/runtime feature-local duplica import/export DB, backup/restore DB o sync/Git globale;
- nessun helper/resource/dependency/schema zombie resta senza consumer per questi percorsi;
- i fix e lo schema risultanti da 914263 restano intatti;
- compile/test/architecture gate pertinenti PASS;
- integrazione avviene tramite il single writer per-repository, senza direct-main write;
- vecchia PR/branch #20 vengono chiusi/rimossi solo dopo verifica di completa integrazione.

# Stop
Dopo PASS finalizza e stop. Report massimo 8 righe, con PROMPT_ID=825147 in prima riga e RESULT in seconda.
