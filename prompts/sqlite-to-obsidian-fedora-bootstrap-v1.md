PROMPT_ID=893025
PARENT_PROMPT_ID=649781
PROJECT_ID=23
MEGAVAULT=STANDARD
REPO=gernalix/MegaVault

# Goal
Crea e porta in produzione il progetto Fedora condiviso `sqlite-to-obsidian`: una proiezione read-only e ricostruibile verso un'unica vault Obsidian, con `gernalix/PersonalHub-data` come prima sorgente. Completa end-to-end repository, codice, test, runtime systemd, primo sync reale, registrazione MegaVault e monitoraggio centrale. Non aggiungere alcun exporter Obsidian all'app Android PersonalHub.

# Evidenza già verificata
- PersonalHub mantiene `personalhub.db` come unica source of truth e pubblica già il proprio stato nel repo privato `gernalix/PersonalHub-data`.
- PersonalHub-data corrente usa schema 21 e contiene `state/manifest.json`, `state/schema.json`, shard `state/tables/**`, `changes/**`, `history/**` e object store.
- `PersonalHub/docs/OBSIDIAN_ARCHIVE.md` e `docs/ARCHITECTURE.md` sono già stati aggiornati: Obsidian è un consumer Fedora esterno; non serve modificare codice Android.
- MegaVault contiene già `ai/SQLITE_TO_OBSIDIAN.md` e la relativa policy in `ai/MEGAVAULT_PROTOCOL.md`. Usali come contratto; non riscoprire l'architettura.
- PROMPT_ID 649781 è superseded. La catena PH finale non dipende più da Obsidian.
- Il repo `gernalix/sqlite-to-obsidian` non esisteva al momento della preparazione di questo goal.

# Esecuzione
1. Prima azione: esegui il claim canonico con `roadmap_start.py` per 893025 e usa il worktree restituito. Leggi solo `ai/SQLITE_TO_OBSIDIAN.md`, la sezione Obsidian del protocollo MegaVault e gli helper espressamente necessari. Niente audit repo-wide.
2. Verifica una sola volta l'assenza di `gernalix/sqlite-to-obsidian`. Se è ancora assente, crealo **privato**, default branch `main`, senza dati personali. Se esiste per un bootstrap parziale di questo stesso task, riusalo dopo una verifica minima; non crearne un duplicato.
3. Clona il nuovo repo in `~/projects/sqlite-to-obsidian`. Registra poi il repo nel MegaVault canonico con `megavault.py register-github-repo --owner gernalix --name sqlite-to-obsidian --remote-url ... --default-branch main --worktree ...`; usa l'ID restituito e non scrivere manualmente nel DB.
4. Implementa un package Python 3.12 piccolo e modulare con CLI `sync`, `rebuild`, `status`, `validate`. Usa XDG: config in `~/.config/sqlite-to-obsidian/`, stato in `~/.local/state/sqlite-to-obsidian/`, cache/source clone in `~/.cache/sqlite-to-obsidian/`. Stato incrementale atomico in SQLite e lock single-process. Nessun token/secret/path personale tracciato.
5. Implementa adapter separati dal renderer. Primo adapter: PersonalHub-data. Mantieni un clone/cache read-only del repo privato usando l'autenticazione Git/GitHub già disponibile sul sistema, senza copiare token nella config. Ogni run fa fetch/fast-forward della sorgente e non la modifica mai.
6. Per PersonalHub usa `state/manifest.json` come indice dello stato corrente; `changes/**` serve solo per restringere il delta. Se manca continuità, cambia schema o lo stato incrementale non è affidabile, esegui un rebuild bounded dal manifest/shard correnti.
7. Proietta solo contenuto semanticamente utile:
   - People: contatti, campi significativi, tag/relazioni utili;
   - Places: luoghi, alias e visite/check-in significativi;
   - Timer: sessioni/attività/quick events e dati utente utili; niente plumbing snapshot/cache come note autonome;
   - Soldi: conti, transazioni, ricorrenze e relazioni esplicite;
   - Substances: sostanze, prescrizioni, intake e stock history utile;
   - WordPulse: sessioni/sommari/aggregati; non una nota per ogni keystroke/word-entry;
   - Hub shared: contexts, tag e relazioni quando migliorano la navigazione.
   Ignora queue/ack/cache/generation/integrity/transport internals e analoghi dettagli tecnici salvo valore umano concreto.
8. Identità globale: `<source>/<module>/<kind>/<canonical-id>`. I path devono restare stabili ai rename. Crea wikilink solo da FK/relazioni canoniche o mapping cross-project espliciti; vietato inferire relazioni dalla sola uguaglianza di nomi/label.
9. Scrivi solo sotto un namespace generato, es. `Generated/PersonalHub/**`, con frontmatter `generated_by`, `source`, `source_revision`, `projection_version`, `canonical_id`. Mantieni manifest ownership e content hash; non toccare file manuali/non posseduti.
10. Risolvi la vault locale senza inventare path: usa la configurazione Obsidian locale e scegli la vault attiva; fallback solo se esiste una singola vault registrata e scrivibile. Se restano zero o più candidati ambigui, non crearne una arbitraria: quello è l'unico blocker utente ammesso per il deploy live.
11. Aggiungi test sintetici mirati: rendering/escaping stabile, rename senza cambio identità, link esplicito, collisione label senza falso link, create/update/delete incrementale, revision invariata=no write, fallback rebuild, cambio schema, crash/retry, preservazione file manuale, mapping cross-project, esclusione tabelle PH tecniche. Non usare dati personali nei fixture/log.
12. Installa runtime Fedora come **oneshot + systemd user timer** secondo lo standard MegaVault, default ogni 5 minuti, `Persistent=true`, piccolo jitter e timeout bounded. Una run invariata deve uscire rapidamente con successo. Non creare daemon polling always-on.
13. Esegui un sync reale contro l'HEAD corrente di PersonalHub-data e la vault risolta. Verifica una selezione minima di note/Properties/wikilink senza stampare contenuti personali nel report. `status` deve mostrare revision sorgente, generation/schema se disponibili, ultimo successo ed eventuale errore compatto.
14. Integra il job nel control plane Uptime Kuma esistente come timer/oneshot: monitorare **successo + freschezza dell'ultima run**, non `ActiveState=active`. Riusa MegaVault/fedora-system-monitor; non creare provisioning Kuma proprietario nel nuovo repo. Esegui readback del monitor/target live.
15. README/AGENTS del nuovo repo devono dichiarare source-of-truth, layout, privacy, comandi, systemd, test e regola per aggiungere futuri adapter. Non duplicare il protocollo MegaVault: linkalo.
16. Nessun refactor o fix collaterale. Se trovi un problema fuori scope, riportalo senza investigarlo salvo che blocchi direttamente il goal.
17. Quando acceptance è PASS, finalizza 893025 con `roadmap_finish.py` e STOP.

# Acceptance
PASS solo se:
- `gernalix/sqlite-to-obsidian` esiste, è privato, ha `main` pulito e nessun dato/secret personale tracciato;
- il nuovo repo è registrato in MegaVault con project_id canonico;
- test mirati PASS;
- PersonalHub-data è consumato read-only e lo stato locale registra l'esatto revision elaborato;
- la vault reale contiene la proiezione PersonalHub sotto namespace generato, con link espliciti e file manuali preservati;
- rebuild e sync incrementale convergono allo stesso stato per la stessa sorgente/versione;
- timer systemd è enabled/active e una run reale termina PASS;
- monitor Kuma centrale per esito+freschezza è presente e verificato con readback;
- nessun codice runtime Android PersonalHub è stato aggiunto/modificato per Obsidian.

# Stop
Dopo PASS termina senza audit aggiuntivi. Output finale massimo 10 righe: PROMPT_ID, RESULT, NEW_PROJECT_ID, REPO, SOURCE_REVISION, VAULT, GENERATED, TESTS, SYSTEMD_KUMA, BLOCKER.