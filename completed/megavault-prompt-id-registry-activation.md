PROMPT_ID=632683 | project_id=23 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT
PARENT_PROMPT_ID=754406

# Goal
Attiva SOLO il registro PROMPT_ID sul MegaVault Fedora canonico: migra il DB reale, riserva gli ID storici recuperabili dalle fonti durevoli, materializza questo prompt, verifica allocator/lifecycle e pubblica il `megavault.sqlite` migrato.

# Starting point verificato
- il tentativo padre `754406` è terminato `BLOCKED` senza mutare DB/codice perché il vecchio path `/home/daniele/Documents/ChatGPT/archive` non esisteva;
- codice remoto MegaVault già corretto; baseline minima: `ab1991c11523280bef52d0e537b5a4ca0c089133`;
- helper disponibili: `prompt-id backup`, `prompt-id backfill-sources`, `prompt-id materialize`, `prompt-id mark-used`, `prompt-id allocate`, `prompt-id cancel`;
- `prompt-id backup` crea un backup SQLite univoco `0600` fuori dal worktree senza `rm`;
- `prompt-id backfill-sources` estrae internamente solo gli ID: history Git di roadmap/MegaVault, directory `prompts/<ID>` di `codex-usage`, più archivi testuali opzionali; un vecchio archivio locale assente non è più blocker;
- test remoti includono concorrenza, immutabilità/lifecycle, backfill, backup privato e source discovery;
- regola assoluta prospettica: ogni nuova materializzazione passa dal registro; ID già registrati non vengono mai riutilizzati.
- Questo task usa il worktree MegaVault canonico corrente già aperto. Non migrare il path del repository durante questa migrazione DB.

# Esecuzione minima
1. Non leggere `AGENTS.md` locale inesistente e non stampare l'intero protocollo. Se le regole non sono già in contesto, leggi SOLO le sezioni `PROMPT_ID canonici`, `Database` e `Git Per MegaVault`.
2. In UNA shell call: verifica worktree/branch, `git fetch origin master`, `git merge --ff-only origin/master`, verifica che `ab1991c11523280bef52d0e537b5a4ca0c089133` sia antenato e che non esistano dirty path sovrapposti a `megavault.sqlite`/file PROMPT_ID. Non interrogare manualmente colonne di `repositories`; non fare schema discovery equivalente.
3. Sincronizza solo se necessario `/home/daniele/projects/codex-roadmap` e `/home/daniele/projects/codex-usage` ai rispettivi branch remoti; se `codex-usage` manca, clonalo SOLO lì. Nessuna discovery generale dei repository.
4. Prima di ogni mutazione DB esegui UNA volta:
   `python3 megavault.py prompt-id backup`
   Conserva il `backup_path` restituito fino al PASS. Niente `rm`, backup manuali o secondo backup equivalente.
5. Esegui UNA volta:
   `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py migrate`
6. Esegui UNA volta il backfill strutturato:
   `python3 megavault.py prompt-id backfill-sources --source historical-pre-allocator --git-repo /home/daniele/projects/codex-roadmap --git-repo "$(git rev-parse --show-toplevel)" --prompt-dir-root /home/daniele/projects/codex-usage --optional-text-tree /home/daniele/.local/share/codex-session-archive --optional-text-tree /home/daniele/Documents/ChatGPT/archive --require-id 632683 --require-id 754406`
   `optional_missing>0` è informazione di copertura legacy, NON blocker. Zero ID, fonti durevoli richieste assenti/non leggibili o assenza di 632683/754406 => BLOCKED.
7. Materializza e usa questo prompt esatto:
   `python3 megavault.py prompt-id materialize 632683 --content-file /home/daniele/projects/codex-roadmap/prompts/megavault-prompt-id-registry-activation.md`
   `python3 megavault.py prompt-id mark-used 632683`
8. Gate, senza ripetizioni:
   - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`;
   - un solo smoke live: alloca con `prompt-id allocate --source activation-smoke --project-id 23`, verifica 6 cifre e poi `prompt-id cancel <ID>`;
   - `PYTHONDONTWRITEBYTECODE=1 python3 megavault.py validate`.
   Al primo failure usa solo l'evidenza disponibile per il fix minimo; leaf test mirato prima dell'unico gate finale necessario.
9. UNA query finale deve provare: tabelle/eventi presenti; nessun duplicato/out-of-range; tutti gli ID scoperti presenti; `632683=used`; `754406` ancora riservato; smoke=`cancelled`; `integrity_check=ok`; `foreign_key_check` vuoto.
10. Commit/push SOLO delle modifiche MegaVault necessarie, incluso `megavault.sqlite`. Dopo push riuscito puoi eliminare il backup temporaneo con Python `Path.unlink()`; non eseguire audit/status post-PASS.

# Acceptance
PASS solo se DB canonico migrato e pushato, backfill persistito, 632683 è `used`, 754406 non è riutilizzabile, test concorrenza/lifecycle/source discovery PASS, smoke live PASS e validate/integrity/FK PASS. Un archivio legacy opzionale assente non invalida il PASS: riportare la copertura nella riga `BACKFILL`.

# Non-goal
Niente redesign allocator, scansione generale filesystem/repo, migrazione del path MegaVault, PersonalHub, endpoint/servizi, cleanup non correlato, audit token, branch nuovi o verifiche dopo PASS.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 632683 --confirm-executed`

Se BLOCKED/FAIL non finalizzare la roadmap. Output massimo 8 righe: `RESULT`, `BACKFILL`, `REGISTRY`, `TESTS`, `VALIDATE`, `COMMIT`, `PUSH`, `BLOCKER`.
