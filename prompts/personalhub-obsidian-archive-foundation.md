PROMPT_ID=582741 | project_id=49 | campaign_id=ph-obsidian-archive | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Implementa la fondazione **opzionale e one-way** PersonalHub → Obsidian definita in `docs/OBSIDIAN_ARCHIVE.md`: contratto di proiezione, renderer Markdown/YAML, manifest PH-owned, SAF, impostazioni OFF-by-default e full rebuild manuale deterministico. Nessun incremental journal in questa fase.

# Starting point autoritativo
- repo: `/home/daniele/projects/PersonalHub`;
- esegui SOLO dopo PROMPT_ID=724615 PASS/finalizzato; Salute canonica deve essere già presente in `main`;
- branch obbligatorio: `main`; non creare/pushare `feature/obsidian-archive` o altri branch remoti temporanei. La feature resta OFF-by-default durante le fasi intermedie;
- contratto autoritativo: `docs/OBSIDIAN_ARCHIVE.md`;
- `personalhub.db` è l'unica source of truth; PH non legge Markdown; nessun import Obsidian→PH;
- Datasette resta indipendente e pienamente supportato;
- `version.txt` resta 50; fase intermedia, nessun Pixel fisico/delivery;
- usa i seam già esistenti `HubEntityAdapter`, `HubAdapterRegistry`, `DatabaseVault`/SAF e settings; non reinventare un secondo storage framework.

# Esecuzione minima
1. Acquisisci il task lock PH con PROMPT_ID 582741. Un solo fetch `origin main` + fast-forward; resta su `main`. Usa prima `.codex/CODE_MAP.tsv` per `hub.context`, `database.export`, settings e Salute; amplia solo se un seam necessario manca.
2. Definisci un contratto condiviso piccolo per la proiezione (nomi liberi ma semantica conforme al doc), separato da `HubEntitySummary`: stable ref, title, properties, body Markdown, explicit links, updatedAt e paginazione/bounded reads. Nessuna feature implementation dependency.
3. Implementa l'engine Obsidian fuori dai feature module:
   - path stabile basato su canonical identity, non sul solo label;
   - alias leggibile nei wikilink;
   - YAML/frontmatter e Markdown escaping deterministici;
   - `ph_generated=true`, projection version, module/kind/canonical_id/title;
   - manifest PH-owned con generated paths + refs;
   - stessa DB state + stessa projection version => stessi byte/path.
4. Implementa full rebuild SAF sicuro:
   - directory scelta con permission persistente;
   - staging/pubblicazione bounded;
   - elimina solo file precedentemente presenti nel manifest PH, mai file manuali/unrelated;
   - vault assente/revocata => errore compatto e nessun impatto sul DB;
   - nessun DB writer gate durante rendering/I/O lento;
   - nessuna scansione Markdown usata dal runtime PH.
5. Settings minime globali:
   - Obsidian export OFF di default;
   - enable/disable;
   - choose/change vault directory;
   - Export/Rebuild now;
   - last success/error compatto;
   - nessun requisito che Obsidian app sia installata.
6. Implementa solo i provider rappresentativi necessari per chiudere end-to-end il contratto, senza fare ancora la copertura completa del task finale:
   - People: una nota contatto sintetica;
   - Places: una nota luogo sintetica;
   - Salute: almeno una nota journal lunga sintetica;
   - link espliciti People↔Places/Salute solo quando la relazione canonica esiste.
   Non esportare raw log/technical rows.
7. Test host sintetici mirati:
   - path stabile al rename;
   - wikilink con alias;
   - frontmatter/body escaping;
   - full rebuild idempotente;
   - unrelated manual file sopravvive;
   - OFF => zero projection I/O;
   - nota Salute lunga conserva correttamente il testo e separa clinico/AI;
   - nessun normale read path PH dipende dai Markdown;
   - `checkArchitectureBoundaries`.
8. Prima del primo Gradle dopo API pubbliche nuove/modificate usa `android_consumer_preflight.py` come da AGENTS. Failure => leaf correction; niente AVD in questa fase.
9. Aggiorna CODE_MAP solo per ownership/seam realmente nuovi e il doc solo se l'implementazione richiede una correzione del contratto, non per aggiungere narrativa.
10. Solo dopo i gate PASS, commit/push `main` una sola volta; lascia `version.txt=50`, non release. Non creare branch remoti temporanei. Rilascia lock.

# Acceptance
PASS solo se un full rebuild manuale produce una vault deterministica e sicura da dati sintetici, Obsidian resta totalmente opzionale/read-only, Datasette/PH non dipendono dal vault, manifest e SAF non possono cancellare file non-PH, architecture/test host PASS.

# Non-goal
Incremental export, mutation journal, WorkManager automatico, copertura completa di tutti i moduli, inferenze temporali Obsidian, import Markdown, AVD, release.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 582741 --confirm-executed`

Output massimo 8 righe: RESULT, HEAD, CONTRACT, FULL_REBUILD, SAF_MANIFEST, REPRESENTATIVE_PROVIDERS, HOST_GATES, BLOCKER.
