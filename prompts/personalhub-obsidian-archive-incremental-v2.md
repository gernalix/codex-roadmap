PROMPT_ID=528163 | project_id=49 | campaign_id=ph-obsidian-archive | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD


# Contratto Git/integrazione PH aggiornato — prevale su ogni istruzione successiva incompatibile
- `main` è baseline/target finale, non area di implementazione. Qualunque riferimento successivo a “branch obbligatorio main”, “lavora su main”, “push main”, “non creare PR”, “mantieni il branch separato” o equivalenti è superato da questo contratto.
- Se il task parte già da un branch feature nominato nel prompt, continua su QUEL branch. Altrimenti crea/usa il branch dedicato `codex/528163-obsidian-archive-incremental` dal più recente `origin/main`.
- Durante implementazione/fix branch-local NON acquisire il lock PH. Esegui i gate host branch-local necessari e pusha solo il branch candidato.
- Quando il branch è pronto, apri/aggiorna una PR verso `main`. A quel punto la stessa sessione può diventare integratore: acquisisci `tools/personalhub_task_lock.py`, fai un solo refresh di `origin/main`, usa `tools/personalhub_integration_context.py --branch <branch>`, rileggi il diff rispetto al main corrente e valuta semanticamente le interazioni. Un merge Git senza conflitti non basta.
- Se servono fix di compatibilità, applicali SOLO sul branch candidato e rilancia i gate pertinenti. Ambiguità sostanziale/out-of-scope => BLOCKED senza toccare `main`.
- Solo dopo review semantica + gate pertinenti PASS, integra la PR in `main`, pusha il canonico, elimina subito il branch remoto+locale e rilascia il lock. Se il task include QA condivisa su AVD/device o release, il lock deve essere acquisito prima di quella fase e può restare detenuto fino a fine integrazione/release.
- Se il task è davvero read-only e non produce alcuna modifica, branch/PR non sono necessari; resta comunque obbligatorio il lock per QA condivisa/release.

# Goal
Su PersonalHub `main`, rendi l'export Obsidian incrementale, coalescente e crash-safe senza condividere acknowledgements con Datasette. Implementa create/update/delete convergence, WorkManager bounded e recovery; nessuna copertura renderer generale in questa fase.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- esegui SOLO dopo PROMPT_ID=946238 PASS/finalizzato;
- branch obbligatorio `main`, già contenente full rebuild/manifest PASS dal task precedente;
- contratto: `docs/OBSIDIAN_ARCHIVE.md`;
- non consumare né cancellare `hub_sync_pending` come acknowledgement Obsidian;
- projection bookkeeping è stato tecnico ricostruibile: non deve diventare semantic Git History, dominio Datasette o archivio utente;
- `version.txt` resta 50.

# Esecuzione minima
1. Acquisisci task lock PH con PROMPT_ID 528163. Usa solo i file/seam introdotti da 946238 più `SyncJournal`, `DatasetteSync`, `HubAutoExport`, `PersonalHubDatabase` e migration/schema; niente inventory generale.
2. Implementa progress tracking indipendente:
   - preferisci una dedicated Obsidian pending queue coalescente se è il cambiamento minimo sicuro;
   - un refactor multi-consumer è ammesso solo se più piccolo e chiaramente testabile;
   - in entrambi i casi Datasette e Obsidian devono poter ackare indipendentemente;
   - INSERT/UPDATE/DELETE e PK change devono convergere;
   - disabilitare Obsidian non deve alterare Datasette.
3. Se serve nuova tabella/schema:
   - migrazione solo additiva per stato tecnico;
   - primary key/indici bounded;
   - nessun dato domain duplicato;
   - exclude esplicito da projection/domain sync/semantic history dove necessario;
   - migration fixture + quick_check/FK PASS;
   - nessuna destructive fallback.
4. WorkManager:
   - unique work Obsidian separato;
   - coalescing/debounce ragionevole, recovery periodica solo se serve;
   - batch bounded per record/byte/tempo;
   - OFF o SAF non configurato => nessuna projection I/O;
   - nessun writer gate durante SAF/rendering;
   - process death/reboot lascia lavoro retryable.
5. Convergenza file:
   - create => file generato;
   - update => stesso stable path aggiornato;
   - rename label => stable path invariato;
   - delete => rimuove solo il file PH-owned corrispondente;
   - projection version mismatch => richiede/programma full rebuild sicuro;
   - manifest aggiornato atomicamente/coerentemente;
   - failure SAF non rollbacka il DB canonico.
6. Non generare backlink inversi duplicati: bastano i forward wikilink espliciti; Obsidian calcola backlinks.
7. Fault-injection/unit tests:
   - Datasette ack non consuma pending Obsidian e viceversa;
   - mutazioni ripetute coalescono;
   - crash/failure tra render e publish converge al retry;
   - revoke SAF lascia DB sicuro e pending;
   - delete non tocca file manuali;
   - OFF non impedisce write DB;
   - bookkeeping Obsidian escluso da semantic history/sync;
   - full rebuild recovery riparte senza duplicati/orfani PH-owned.
8. Consumer preflight prima di API/schema pubblici; poi migration/unit/compile leaf interessati e un solo `checkArchitectureBoundaries` finale. Nessun AVD.
9. Solo dopo i gate PASS, commit/push `main` una sola volta; non creare branch remoti temporanei e non bump/release. Rilascia lock.

# Acceptance
PASS solo se Datasette e Obsidian hanno acknowledgements indipendenti, le mutazioni convergono incrementalmente senza whole-vault scan ordinario, failure/reboot sono retry-safe, DB canonico non dipende dall'I/O Markdown e tutti i gate migration/host/architecture sono PASS.

# Non-goal
Renderer completi di tutti i moduli, inferenza temporale in Obsidian, import Markdown, UI redesign, AVD, release/install/delivery.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 528163 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, JOURNAL, DATASETTE_ISOLATION, WORKMANAGER, CONVERGENCE, HOST_GATES, BLOCKER.
