PROMPT_ID=754406 | project_id=23 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Attiva sul MegaVault Fedora canonico il registro PROMPT_ID già implementato su `gernalix/MegaVault/master`: migra il DB reale, riserva gli ID storici pre-allocator, verifica unicità/concorrenza/lifecycle e pubblica il `megavault.sqlite` migrato. Fai SOLO questo.

# Starting point verificato
- codice remoto MegaVault già implementato; baseline minima da includere: `896d7637ea317469eb314870d3a6a6c0b802e2e7`;
- `ai/megavault_core.py` espone schema/migrazione, CSPRNG, `BEGIN IMMEDIATE`, backfill, materialize/mark-used/cancel e CLI `prompt-id`;
- `tests/test_megavault.py` contiene test di 32 allocazioni concorrenti, revisione con contenuto identico ma nuovo ID, immutabilità, lifecycle e backfill;
- regola assoluta: 1 prompt materializzato = 1 PROMPT_ID nuovo; nessun ID storico/cancellato/usato può essere riutilizzato;
- questo prompt, creato prima dell'attivazione del registro, ha `PROMPT_ID=754406` e deve essere incluso nel backfill, poi materializzato dal file esatto e marcato `used`;
- fonti locali note per il backfill: repo `codex-roadmap` (inclusa history), repo MegaVault (inclusa history), `/home/daniele/Documents/ChatGPT/archive`, `/home/daniele/.local/share/codex-session-archive`. Non fare scansioni generiche del filesystem.

# Esecuzione minima
1. Risolvi il checkout MegaVault corrente secondo il protocollo/DB, sincronizzalo a `origin/master` con ff-only e verifica che includa la baseline. Se ci sono modifiche locali sovrapposte ai file/DB del task, `BLOCKED`; non stash/reset.
2. Prima di mutare il DB crea UNA copia consistente owner-only del `megavault.sqlite` canonico usando SQLite backup API. Conserva il backup fino al PASS.
3. Costruisci in `/tmp` un file ordinato/unico con soli ID a 6 cifre estratti esclusivamente da:
   - diff/history Git di `codex-roadmap` e MegaVault cercando marker `PROMPT_ID`;
   - archivio ChatGPT noto;
   - archivio sessioni Codex noto.
   Usa query/regex strette; niente dump dei contenuti. Verifica esplicitamente che `754406` sia presente. Se una fonte nota esiste ma non è leggibile, `BLOCKED`.
4. Esegui una sola volta `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py migrate`.
5. Importa il file storico con `python3 megavault.py prompt-id backfill --source historical-pre-allocator --ids-file <file>`. Nessun ID del file può essere perso. Il backfill è solo bootstrap: non usarlo per creare nuovi prompt.
6. Materializza questo prompt con il file roadmap esatto:
   `python3 megavault.py prompt-id materialize 754406 --content-file /home/daniele/projects/codex-roadmap/prompts/megavault-prompt-id-registry-activation.md`
   quindi marcane subito l'uso con `python3 megavault.py prompt-id mark-used 754406`.
7. Gate host, in questo ordine:
   - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`;
   - un singolo smoke live: `prompt-id allocate --source activation-smoke --project-id 23`, verifica formato 6 cifre e presenza nel registro, poi `prompt-id cancel <ID>`;
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py validate`.
   Al primo failure usa solo l'evidenza del failure per il fix minimo; niente audit/refactor. Se il fix richiede cambiare codice, applicalo solo se strettamente necessario, test mirato prima del gate finale.
8. Verifica con UNA query SQLite che:
   - `prompt_id_registry` e `prompt_id_events` esistano;
   - tutti gli ID storici raccolti siano presenti;
   - non esistano duplicati/out-of-range;
   - `754406` sia `used`;
   - il probe sia `cancelled`;
   - `PRAGMA integrity_check='ok'` e `foreign_key_check` vuoto.
9. Rimuovi solo i file temporanei del task. Commit unico delle modifiche MegaVault necessarie, incluso `megavault.sqlite`, quindi push `master`. Non modificare roadmap manualmente.

# Acceptance
PASS solo se migrazione e backfill sono persistiti nel DB canonico, gli ID storici non sono riutilizzabili, il task 754406 è `used`, concorrenza/lifecycle test PASS, smoke live PASS, integrity/FK/validate PASS e commit/push MegaVault riusciti.

# Non-goal
Niente redesign allocator, nuovi servizi/endpoint, scansione generale repo/filesystem, modifica PersonalHub, cleanup non correlato, audit token, branch nuovi o test aggiuntivi dopo PASS.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 754406 --confirm-executed`

Se BLOCKED/FAIL non finalizzare la roadmap. Output finale massimo 8 righe: `RESULT`, `BACKFILL`, `REGISTRY`, `TESTS`, `VALIDATE`, `COMMIT`, `PUSH`, `BLOCKER`.
