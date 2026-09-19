PROMPT_ID=728918 | PARENT_PROMPT_ID=355842 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Implementa l'archivio Obsidian opzionale già definito in docs/OBSIDIAN_ARCHIVE.md, completo e incrementale per tutti i moduli mantenuti, incluso Salute canonico. Non trasformarlo in datastore PH.

# Starting point
- repo: /home/daniele/projects/PersonalHub;
- oggi esistono i contratti/docs Obsidian ma non un exporter runtime;
- SQLite resta unica source of truth; Datasette resta parallelo e indipendente;
- usa il DB/schema risultante da 462279.

# Esecuzione
1. Parti da docs/OBSIDIAN_ARCHIVE.md e docs/health/OBSIDIAN_PROJECTION.md; apri solo CODE_MAP/provider dei moduli necessari.
2. Implementa contratto di projection generico, settings OFF-by-default, scelta vault, rebuild esplicito, manifest tecnico e aggiornamenti incrementali/coalesced con recovery.
3. Genera Markdown deterministico con Properties, wikilink/backlink naturali e timestamp completi. Copri tutti i moduli mantenuti; Health deve rendere bene long-form notes/esami senza log tecnici.
4. Lo stato tecnico Obsidian deve essere ricostruibile, separato dal dominio e indipendente dagli ack Datasette; nessuna funzione PH deve dipendere dalla vault.
5. Testa idempotenza rebuild, incremental/retry, OFF/no-I/O, rimozione vault, indipendenza Datasette e provider di tutti i moduli. Prova file I/O reale su AVD una sola volta.

# Acceptance
PASS con exporter opzionale, deterministico, incrementale, recuperabile, completo sui moduli mantenuti e senza dipendenza runtime da Obsidian/vault. Stop dopo PASS.
