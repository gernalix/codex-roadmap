[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=892067 | project_id=51 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Generare una checklist privata e completa di **tutti i repository GitHub posseduti da `gernalix`**, ordinata per data dell'ultimo commit **DESC**, così l'utente possa marcare con `[x]` solo i repo da conservare. Questo task è SOLO inventario: non modificare, archiviare o cancellare repository.

Output canonico:
- `/home/daniele/projects/MegaVault/ai/repository-retention-checklist.md`
- `/home/daniele/projects/MegaVault/ai/repository-retention-checklist.generated.json`

# Inventory minima
Usa `gh api graphql` in una sola query/paginazione minima su repository con `ownerAffiliations: OWNER`; recupera almeno nome esatto, visibility, archived, default branch e `defaultBranchRef.target.committedDate` quando esiste. Non usare Chrome e non aprire le codebase.

Ordina localmente:
1. repo con commit: `committedDate` DESC;
2. repo senza commit: in fondo, nome case-insensitive ASC.

Verifica che ogni repo posseduto compaia esattamente una volta. Nessun repo collaborato/non posseduto.

# Formato checklist
Il Markdown deve essere facile da editare e contenere, dopo una breve istruzione, **solo una checkbox per repository** nel formato esatto:

```text
- [ ] PersonalHub
- [ ] script_manager
```

Preserva spelling/case GitHub. Tutte le checkbox nascono **vuote**. Non aggiungere date o metadati sulla stessa riga delle checkbox. Spiega in testa: `[x] = CONSERVA`, `[ ] = ARCHIVIA E CANCELLA` e che il task successivo non procederà finché il file non sarà stato modificato dall'utente.

# Proof of human edit
Dopo aver scritto la checklist calcola SHA256 del file e salva nel JSON sidecar almeno:
- `owner`
- `generated_at`
- `repository_count`
- `checklist_sha256`

Il sidecar non va rigenerato automaticamente dal task successivo: serve a dimostrare che l'utente ha realmente modificato la checklist.

# Verifica / push
- confronta count inventario ↔ checkbox 1:1;
- verifica ordinamento per committedDate DESC;
- `git diff --check` sui due soli file;
- commit+push MegaVault una volta;
- nessuna modifica ad altri repo.

# Acceptance
PASS solo se la checklist contiene tutti e soli i repo owned, una volta ciascuno, ordine ultimo commit DESC corretto, tutte le checkbox inizialmente vuote e sidecar SHA256 coerente.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 892067 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 892067`

STOP immediato. **Non eseguire il task successivo:** l'utente deve prima modificare la checklist. Output massimo 5 righe: RESULT, repo_count, first/last repo, checklist path, MegaVault commit.