PROMPT_ID=817056
PROJECT_ID=92
MODEL=GPT-5.5
REASONING=medium
MEGAVAULT_MODE=FAST
REPO=gernalix/duplicate-photos-detector
WORKDIR=/home/daniele/projects/duplicate-photos-detector

# Goal
Completa SOLO ciò che richiede il Fedora reale per rendere duplicate-photos-detector operativo: checkout locale, registrazione MegaVault del nuovo repo, dipendenze/runtime, smoke reali del matcher, archivio locale, embedding opzionali e servizio systemd resiliente. Il codice sorgente è già su main e la CI remota è PASS: non rifarlo da zero.

# Starting point verificato
- main contiene SHA-256, pHash, crop-resistant hash, SIFT+RANSAC, SQLite/first_seen, classi EXACT/SAME_IMAGE/SCREEN_CAPTURE/VISUALLY_SIMILAR/NO_MATCH, diagnostica visuale, OpenCLIP opzionale, FAISS opzionale, CLI index/find/similar/watch e template systemd.
- GitHub Actions PASS su Python 3.11 e 3.12.
- Nessun riconoscimento facciale/biometrico: il sistema deve stabilire se è la stessa immagine o una variante, non se due foto diverse ritraggono la stessa persona.
- Foto, DB, embedding, diagnostica e pesi locali non devono finire in Git.

# Esecuzione minima
1. Prima azione: claim canonico:
   python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 817056
   Procedi solo con roadmap_status=running.
2. Se WORKDIR manca, clona direttamente origin/main; altrimenti sincronizza in modo sicuro senza audit repo-wide. Leggi AGENTS.md e i soli file pertinenti.
3. Registra il repo in MegaVault, se non già registrato:
   python3 /home/daniele/MegaVault/megavault.py register-github-repo --owner gernalix --name duplicate-photos-detector --remote-url https://github.com/gernalix/duplicate-photos-detector --default-branch main --worktree /home/daniele/projects/duplicate-photos-detector
   Conserva il project_id restituito per futuri task; non modificare manualmente megavault.sqlite.
4. Segui la policy Python locale corrente di AGENTS/MegaVault. Riusa dipendenze già presenti e installa solo quelle mancanti; niente ambienti/cleanup non richiesti.
5. Esegui prima i test mirati esistenti. Poi crea in /tmp un set sintetico feature-rich e verifica via CLI, senza retry equivalenti:
   - copia byte-identica => EXACT;
   - JPEG ricompressa/ridimensionata => SAME_IMAGE;
   - crop significativo => SAME_IMAGE;
   - trasformazione prospettica+ricompressione, rappresentativa di foto di uno schermo => SCREEN_CAPTURE oppure SAME_IMAGE con forte geometria, mai VISUALLY_SIMILAR come unica evidenza.
   Verifica anche --diagnostics e che i file diagnostici restino fuori Git.
6. Archivio canonico locale: usa ~/Pictures/GrindrPhotos. Se non esiste, crealo vuoto; NON cercare/copiarvi automaticamente foto da altre directory. Crea/usa DB ~/.local/share/duplicate-photos-detector/index.sqlite3 e fai un index smoke.
7. OpenCLIP: installa/riusa l'extra solo se necessario, lascia i pesi nella cache locale standard, esegui un singolo smoke di embedding e verifica che --embeddings non rompa il matching base. FAISS: valida il percorso solo se già disponibile o se l'archivio raggiunge la soglia che lo rende utile; non installarlo soltanto per completezza.
8. Se ~/Pictures/GrindrPhotos contiene già immagini, NON mostrarle né caricarle: indicizza localmente e, su al massimo 1-2 immagini, genera in /tmp versioni ricompressa/crop/prospettica per calibrare solo se i default producono falsi negativi evidenti. Non usare nomi/file privati nel report o nei commit.
9. Installa da systemd/duplicate-photos-detector-watch.service.template una unit user locale con path reali, Restart=always/RestartSec=5, DB e archivio sopra; daemon-reload, enable --now e verifica active. Esegui un solo test controllato di restart automatico del processo e conferma che torni active.
10. Se una verifica scopre un bug reale nel repo, applica SOLO il fix minimo con test mirato e integra secondo il workflow single-writer. Vietati refactor, cleanup, feature aggiuntive o esplorazione generale. Se tutto è già PASS, nessuna modifica sorgente.
11. Verifica finale: unit active, DB locale non tracciato, git status pulito, nessuna foto/embedding/cache/diagnostica tracciata. Stop immediato.

# Acceptance
PASS se: test repo PASS; i 4 smoke sopra danno risultati coerenti; diagnostica funziona; OpenCLIP smoke PASS oppure è esplicitamente non richiesto dal percorso base ma l'extra è installabile senza regressioni; archivio+DB locali esistono; servizio user enabled+active e si riavvia dopo il test controllato; repo registrato in MegaVault; nessun dato privato è stato committato/uploadato.

Finalizza una sola volta con roadmap_finish.py sul PROMPT_ID 817056. Output max 10 righe:
PROMPT_ID
RESULT
PROJECT_ID_REGISTERED
TESTS
EXACT
REENCODE_CROP
SCREEN_PERSPECTIVE
EMBEDDINGS
SYSTEMD
BLOCKER