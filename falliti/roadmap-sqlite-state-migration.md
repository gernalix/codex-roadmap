PROMPT_ID=809537 | project_id=51 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD
Codex Desktop project: codex-roadmap

# Goal
Completa il cutover di `gernalix/codex-roadmap` da stato Markdown manuale a **SQLite canonico + viste Markdown/Obsidian generate**. Il DB deve tracciare l'intero ciclo di vita di ogni PROMPT_ID, inclusi run Codex, correzioni ChatGPT, analisi dei report, eventuali modifiche di codice fatte direttamente da ChatGPT dopo l'analisi e genealogia dei prompt di fix. Migra lo storico esistente senza perdere informazioni. Dopo il PASS, `roadmap.md`, `spiegazioni.md` e le note Obsidian sono proiezioni ricostruibili: non sono più fonti di verità.

# Starting point autoritativo
- repo canonico: `/home/daniele/projects/codex-roadmap`, branch `main`;
- archivio run/costi: usa soltanto le fonti canoniche già presenti sotto `/home/daniele/projects/codex-usage-monitor` e/o il relativo output `codex-usage` se configurato; niente scansioni esterne;
- il repo contiene già prompt in `prompts/`, `completed/`, `falliti/` e audit ChatGPT in `audits/`;
- regola PROMPT_ID invariata: 1 materializzazione = 1 ID unico di 6 cifre; mai riuso;
- preserva il contenuto dei prompt storici: la migrazione aggiunge metadati nel DB, non riscrive retroattivamente i prompt eseguiti;
- `roadmap.sqlite` deve essere committato nel repo ed essere la source of truth; niente WAL/SHM committati;
- tutte le viste `.md` devono essere rigenerabili deterministicamente dal DB;
- nessun nuovo servizio persistente è richiesto.

# Modello dati minimo obbligatorio
Implementa schema versionato almeno con queste entità:

1. `prompts`
   - prompt_id, slug/path corrente, stato corrente, posizione in coda;
   - project_id/progetto Codex, model, reasoning, MegaVault, tipo Prompt/Goal, campaign_id;
   - parent prompt, istruzione stessa/nuova chat, spiegazione umana;
   - created/updated, ultimo attore che ha corretto lo stato e motivazione.
2. `prompt_dependencies` e relazioni padre→figlio/fix/retry/supersedes.
3. `prompt_executions`
   - una riga per ogni run reale;
   - launched_at, finished_at, outcome `PASS|FAIL|BLOCKED|UNKNOWN`;
   - titolo/chat/progetto Codex quando osservabili, commit/evidenza finale e riepilogo;
   - i run sono storico: una correzione successiva dello stato corrente NON deve riscrivere il loro outcome.
4. `status_events`: audit append-only di ogni cambio/correzione di stato, con attore `codex|chatgpt|migration`.
5. `chatgpt_analyses`
   - se/quando ChatGPT ha analizzato il report;
   - report/audit sorgente;
   - se ha trovato colli di bottiglia;
   - eventuale fix_prompt_id;
   - se la roadmap è stata modificata.
6. `chatgpt_code_changes`
   - **obbligatorio**: per ogni analisi ChatGPT, registra separatamente se ChatGPT ha poi modificato codice;
   - una riga per ciascun intervento/repo: repository, tipo (`fix`, `optimization`, `bottleneck-removal`, `tests`, `ci`, `docs`, ecc.), commit SHA se disponibile, breve riepilogo;
   - deve supportare più repository e più commit per la stessa analisi.

Aggiungi view/query di comodo per ottenere in una riga: stato, ultimo run/esito, prima/ultima esecuzione, analizzato sì/no, codice modificato da ChatGPT sì/no, ultimo fix child.

# Backfill storico
1. Importa tutti i PROMPT_ID materializzati presenti in `prompts/`, `completed/`, `falliti/`.
2. Riconcilia launch/end/outcome con l'archivio `codex-usage` quando disponibile. Non inventare timestamp: se manca evidenza, lascia NULL/unknown e annota provenance.
3. Importa gli audit ChatGPT già presenti in `audits/`.
4. Caso di regressione obbligatorio: `PROMPT_ID=424261` deve risultare `completed`, analizzato da ChatGPT e con `chatgpt_code_changes` sul repo `gernalix/activity-watch-uploader`, includendo i commit già documentati nell'audit: `2b5f527...`, `c836d113...`, `fd91c70d...`, `7427be591...`.
5. Collega i prompt figli/fix usando `PARENT_PROMPT_ID` e l'evidenza roadmap/audit; non inferire genealogie ambigue.

# Scrittori
## Codex
Integra il tracking nel percorso normale senza dipendere da modifiche manuali alle tabelle Markdown:
- all'avvio di un prompt registra una nuova esecuzione con timestamp reale;
- a terminale registra `PASS|FAIL|BLOCKED|UNKNOWN`, timestamp finale e riepilogo minimo;
- PASS archivia il file in `completed/`; FAIL/BLOCKED/UNKNOWN lo archivia in `falliti/`;
- rimuove i terminali dalla coda e rigenera le viste;
- operazioni idempotenti/fail-closed; niente doppio run aperto per lo stesso prompt;
- preserva l'attuale sicurezza race-safe del finalizzatore e non tocca il dirty worktree dell'utente.

## ChatGPT
Fornisci CLI/API locale semplice e documentata per permettere a ChatGPT di:
- correggere lo status corrente da failed/completed o viceversa senza cancellare lo storico dei run;
- registrare un'analisi;
- registrare **le modifiche di codice fatte dopo quell'analisi** con repo/tipo/commit/summary;
- registrare fix_prompt_id e relazione padre→figlio;
- aggiungere/aggiornare prompt e dipendenze;
- rigenerare le viste dopo ogni mutazione.
Le mutazioni devono essere transazionali e verificabili con un comando `validate`.

# Obsidian / Markdown generati
Genera almeno:
- `roadmap.md`: sola coda attiva, ordinata;
- `spiegazioni.md`: tabella umana generata con almeno PROMPT_ID, progetto, stato, primo/ultimo lancio, ultimo esito, analizzato ChatGPT, codice modificato da ChatGPT, fix child, chat, dipendenze, spiegazione, model/reasoning/tipo;
- `obsidian/Prompt Index.md`;
- una nota per PROMPT_ID sotto `obsidian/prompts/`;
- indici per progetto e stato.

Ogni nota prompt deve usare frontmatter/tag utili e wiki-link bidirezionali verso file prompt reale, progetto/stato, parent/children/fix/retry, dipendenze, audit/analisi ed eventuali prompt di fix. Le note sono read-only/proiezioni: modifiche manuali vengono sovrascritte al render successivo.

# Cutover e compatibilità
- Mantieni `roadmap_guard.py` / `roadmap_finish.py` compatibili con i prompt esistenti, ma selezione e finalizzazione devono consultare/aggiornare SQLite, non editare tabelle Markdown come source of truth.
- Aggiorna README e STANDARD_PROMPT: da questo task in poi è vietato modificare manualmente `roadmap.md` o `spiegazioni.md`.
- I nuovi prompt devono essere inseriti nel DB e poi renderizzati.
- Durante il cutover, se DB e Markdown divergono, il DB vince.
- Non introdurre ORM/dipendenze: usa `sqlite3` standard library.

# Verifica mirata
Aggiungi test automatici almeno per:
- init/migrazione idempotente;
- queue ordering/compaction senza collisioni;
- start + PASS;
- start + FAIL/BLOCKED con archiviazione in `falliti/`;
- correzione ChatGPT failed↔completed che preserva l'outcome storico;
- analisi senza code change vs analisi con uno/più code change;
- parent/fix child e dipendenze;
- render deterministico Obsidian/Markdown;
- caso 424261;
- finalizer concorrente/race-safe esistente ancora PASS.

Esegui prima i test nuovi/mirati, poi una sola suite completa `python3 -m unittest discover -s tests -v`.

# Scope / stop
- SOLO `gernalix/codex-roadmap` e letture mirate da codex-usage per il backfill.
- Nessun refactor estraneo, nessun nuovo servizio, nessun redesign dei prompt funzionali.
- Non analizzare i report durante questo task: importa solo metadata già esistenti.
- Se un dato storico non è determinabile in modo affidabile, conserva NULL/UNKNOWN + provenance; non indovinare.
- PASS solo se DB, render, test e push sono coerenti e non restano artefatti SQLite `-wal/-shm`.

# Output finale
Prima riga `RESULT=PASS|BLOCKED|FAIL`.
Poi massimo 8 righe: schema version, numero prompt/run/analisi backfillati, test, commit, eventuali dati storici rimasti unknown.