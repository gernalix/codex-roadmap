PROMPT_ID=649781 | PARENT_PROMPT_ID=728918 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
WORKDIR=/home/daniele/projects/PersonalHub

# Goal
Completa SOLO il lavoro residuo dell'archivio Obsidian opzionale di PersonalHub lasciato da 728918. Non reimplementare la feature e non fare audit generali.

# Evidenza già verificata
- ultimo esito 728918: BLOCKED;
- core compile PASS e UI compile PASS;
- blocker concreto: migration gate FAIL;
- il contratto resta quello di `docs/OBSIDIAN_ARCHIVE.md` e `docs/health/OBSIDIAN_PROJECTION.md`;
- SQLite resta source of truth; Obsidian è solo projection opzionale; Datasette resta indipendente.

# Esecuzione minima
1. Esegui `roadmap_start.py` per 649781 e usa il worktree restituito.
2. Parti dal main corrente. Se esistono residui/worktree/branch di 728918, ispeziona SOLO quelli pertinenti prima di riscrivere codice; preserva lavoro estraneo. Non rieseguire esplorazione repo-wide.
3. Riproduci UNA volta il migration gate fallito e identifica il primo errore concreto. Correggi il minimo necessario e rilancia prima il leaf fallito.
4. Verifica lo stato reale dell'implementazione rispetto al contratto e completa solo ciò che manca ancora: settings OFF-by-default, scelta vault, rebuild esplicito, manifest/stato tecnico ricostruibile, export incrementale/coalesced/retry e provider dei moduli mantenuti incluso Health. Non duplicare parti già presenti.
5. Test mirati: migration gate, idempotenza rebuild, incremental/retry, OFF=no I/O, vault rimosso, indipendenza Datasette e provider pertinenti. Esegui UN solo I/O reale su AVD se richiesto dal contratto. Allarga i test solo se un failure lo giustifica.
6. Nessun refactor, cleanup, modernizzazione o fix collaterale. Nessun retry identico senza nuova evidenza.
7. Quando gli acceptance criteria sono soddisfatti, finalizza 649781 e STOP.

# Acceptance
PASS solo se l'archivio Obsidian è opzionale, deterministico, incrementale e recuperabile; copre i moduli mantenuti incluso Health; nessuna funzione PH dipende dalla vault; il migration gate è PASS; i test mirati sono PASS; l'I/O reale AVD richiesto passa una volta.

# Output
Massimo 7 righe: PROMPT_ID, RESULT, ROOT_CAUSE, FIX, MIGRATION_GATE, TESTS, BLOCKER.
