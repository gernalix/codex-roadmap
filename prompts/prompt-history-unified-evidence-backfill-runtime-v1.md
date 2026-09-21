PROMPT_ID=925731 | project_id=92 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD
WORKDIR=/home/daniele/projects/prompt-history

# Goal
Attiva end-to-end `gernalix/prompt-history` sul Fedora reale come evidence warehouse DERIVATO e rigenerabile per storico ChatGPT + Codex. Esegui il backfill dello storico già disponibile, collega solo identità supportate da evidenza deterministica, installa il sync periodico e verifica che le query possano davvero guidare future decisioni su modello/reasoning/prompt structure.

Non trasformare prompt-history in un source of truth concorrente: roadmap, codex-usage, chrome-codex-switcher, Workflowy/GitHub restano proprietari dei rispettivi dati.

# Starting point autoritativo
- repo: `/home/daniele/projects/prompt-history`;
- remoto: `gernalix/prompt-history/main`, include almeno commit `95667890f0aebb271c755b9f99488f978840328e` o successivo;
- codice già implementato da ChatGPT:
  - schema SQLite derivato con prompts/executions/relations/artifacts/source_records + FTS5;
  - identità Codex canonica `codex:<PROMPT_ID>`;
  - text-quality precedence per non sovrascrivere materializzazioni canoniche con copie redatte;
  - adapter read-only `codex-roadmap/roadmap.sqlite`;
  - adapter `codex-usage/index/prompts.jsonl` + per-cycle `metrics.json`;
  - adapter OpenAI `conversations.json`;
  - JSONL normalization contract;
  - link deterministico ChatGPT→Codex per literal `PROMPT_ID`, parent link per `PARENT_PROMPT_ID`;
  - `resolved_by` solo per fix con PASS registrato;
  - query similar/model-stats/blockers/token-efficiency + recommender con minimum sample count;
  - CI stdlib Python/SQLite, nessun venv.
- sorgenti locali già note:
  - roadmap: `/home/daniele/projects/codex-roadmap/roadmap.sqlite`;
  - codex usage: `/home/daniele/projects/codex-usage`;
  - ChatGPT archive storico sotto `/home/daniele/Documents/ChatGPT/archive`;
  - chrome-codex-switcher state: `~/.local/state/chrome-codex-switcher/state.sqlite3`.
- Non committare DB derivati, export ChatGPT, note, transcript o altri dati privati.

# Esecuzione minima
1. Acquisisci il claim 925731. Fai un solo fetch/fast-forward sicuro di prompt-history. Se il checkout ha modifiche locali sovrapposte, BLOCKED; niente stash/reset distruttivo.
2. Verifica il CI del commit corrente. Se verde, non rifare audit generali: esegui localmente solo:
   - `python3 -m py_compile prompt_history/*.py`;
   - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`;
   - smoke FTS5 con il SQLite di sistema.
   Correggi esclusivamente failure del repo prompt-history.
3. MegaVault: cerca il progetto/repo `prompt-history`. Se manca, registralo col meccanismo canonico MegaVault e conserva l'ID assegnato; non inventare un ID e non duplicare record.
4. Runtime locale:
   - DB derivato fuori dal repo: `~/.local/share/prompt-history/prompt_history.sqlite`;
   - config sorgenti sotto `~/.config/prompt-history/`;
   - permessi user-only ragionevoli;
   - nessun venv, container o DB committato.
5. Backfill Codex/roadmap usando gli adapter già presenti. Importa tutto lo storico disponibile, non solo gli ultimi prompt. Rerun dello stesso importer deve essere idempotente: nessun duplicato logico.
6. Backfill ChatGPT:
   - ispeziona SOLO `/home/daniele/Documents/ChatGPT/archive` e gli script/export ChatGPT direttamente pertinenti;
   - se esiste un `conversations.json` autorevole, usalo;
   - se l'archivio attuale è Markdown/metadata normalizzato ma non esiste più il JSON sorgente, implementa il minimo adapter read-only per QUEL formato reale, senza aprire le chat una a una e senza riscaricare manualmente la cronologia;
   - conserva conversation_id/message_id/role/title/timestamp/model_slug quando disponibili.
7. chrome-codex-switcher:
   - leggi read-only `~/.local/state/chrome-codex-switcher/state.sqlite3`;
   - aggiungi un adapter minimo solo dopo aver verificato le tabelle reali;
   - importa per ogni PROMPT_ID i riferimenti stabili a Chrome context/Codex thread e i metadata utili come artifacts/provenance; le note possono essere indicizzate solo nel DB locale derivato e NON devono finire in Git;
   - se un URL ChatGPT contiene un conversation id che coincide esattamente con lo storico ChatGPT, crea la relazione esplicita; niente fuzzy/semantic guessing.
8. Workflowy/GitHub:
   - preferisci i dati già normalizzati in roadmap.sqlite (analyses, artifacts, outcomes, fix relations);
   - aggiungi un adapter separato solo se trovi una sorgente locale canonica con informazione non già presente. Vietata duplicazione per comodità.
9. Linking:
   - esegui il linker `PROMPT_ID` già implementato;
   - usa hash/materialization o binding espliciti solo quando l'identità è deterministica;
   - nessun link semantico ipotetico tra ChatGPT e Codex. I match non certi restano non collegati.
10. Aggiungi un comando unico idempotente `sync` (e `rebuild` se serve) che esegua gli importer configurati e il linker senza richiedere parametri ripetitivi.
11. Installa `prompt-history-sync.service` come Type=oneshot e `prompt-history-sync.timer` come timer periodico user, circa ogni 15 minuti con Persistent=true. Non usare Restart=always su un oneshot/timer. Riusa la policy systemd canonica MegaVault se già disponibile.
12. Esegui UNA sincronizzazione completa reale e poi UNA seconda sync invariata. La seconda deve essere sostanzialmente no-op/idempotente.
13. Verifica il valore analitico con query reali:
   - conteggi ChatGPT vs Codex;
   - almeno 3 PROMPT_ID con execution collegate;
   - almeno un chain parent/fix/resolved_by se presente storicamente;
   - `similar` su un task reale;
   - `model-stats` e `recommend --min-samples 3`;
   - blocker e token-efficiency.
   Non falsificare una raccomandazione se il campione è insufficiente.
14. Documenta in README solo i path/runtime realmente installati e la procedura di rebuild. Nessun dato personale di esempio preso dall'archivio.
15. Dopo PASS finalizza 925731 e STOP. Nessun audit/refactor successivo.

# Acceptance
PASS solo se:
- schema/test/FTS5 PASS sul Fedora reale;
- DB locale derivato creato fuori Git e ricostruibile;
- roadmap + codex-usage storico importati;
- storico ChatGPT disponibile importato senza apertura manuale chat-per-chat;
- switcher binding importati read-only se il DB contiene dati pertinenti;
- importer ripetuti senza duplicati logici;
- literal PROMPT_ID ChatGPT↔Codex links verificati; zero link fuzzy inventati;
- fix PASS possono produrre resolved_by, fix non PASS no;
- sync unico + user timer installati/attivi;
- seconda sync invariata è idempotente;
- query similar/model/recommend/blocker/token producono output reale e sample count;
- nessun source of truth upstream modificato e nessun dato privato committato.

# Output
Massimo 10 righe:
PROMPT_ID=925731
RESULT=PASS|BLOCKED|FAIL
PROJECT_ID=<MegaVault id reale prompt-history>
DB=<path + counts prompts/executions/relations>
SOURCES=<roadmap,codex-usage,chatgpt,switcher>
LINKING=<deterministic links + resolved_by>
SYNC=<service/timer + second-run no-op>
ANALYTICS=<similar/model/recommend/blocker smoke>
TESTS=<CI/local>
BLOCKER=<none|unica azione necessaria>
