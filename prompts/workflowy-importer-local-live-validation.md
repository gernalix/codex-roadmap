PROMPT_ID=746193 | project_id=23 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Chiudi SOLO le parti che richiedono il runtime locale per `gernalix/workflowy-importer`: registra/risolvi il nuovo repo in MegaVault, predisponi il checkout canonico sotto `/home/daniele/projects`, esegui i gate locali e un unico smoke test reale contro Workflowy usando il segreto locale già configurato. Non fare audit generale né importare dati reali dell'utente.

# Starting point autoritativo
- repo remoto: `https://github.com/gernalix/workflowy-importer`, branch persistente unico `main`;
- baseline minima da contenere: `9389edd7650a209aee424a42460087ccfb1bd56e`;
- GitHub CI sulla baseline: PASS;
- il repo implementa già CLI/API/parser/test; ChatGPT ha già completato tutto ciò che era possibile sul remoto;
- MegaVault autorevole locale: `/home/daniele/projects/MegaVault`, `project_id=23` è usato SOLO come contesto bootstrap perché `workflowy-importer` può non avere ancora un proprio `project_id`;
- worktree canonico richiesto per il nuovo repo: `/home/daniele/projects/workflowy-importer`;
- registrazione canonica disponibile:
  `python3 megavault.py register-github-repo --owner gernalix --name workflowy-importer --remote-url https://github.com/gernalix/workflowy-importer --default-branch main --worktree /home/daniele/projects/workflowy-importer`;
- API key Workflowy: usare solo il secret-ref/env locale canonico se già presente. Non stampare, non leggere valori in chiaro nei log, non committare segreti. Se nessun segreto locale è disponibile, `RESULT=BLOCKED` e stop dopo i gate host;
- nessun contenuto Workflowy esistente va modificato. Lo smoke può creare SOLO un root temporaneo dedicato e deve eliminarlo alla fine;
- non leggere roadmap/README generici o memoria Codex: i fatti necessari sono qui. Usa MegaVault solo per lookup/registrazione mirata e secret-ref.

# Esecuzione
1. In un batch breve:
   - porta `/home/daniele/projects/MegaVault` al remoto con solo `fetch` + `merge --ff-only`, senza stash/reset;
   - esegui `python3 megavault.py project workflowy-importer`;
   - se assente, esegui UNA volta il comando `register-github-repo` sopra;
   - cattura il `project_id` reale restituito e verifica con `project-show`/`project-path` che remote, branch e worktree siano esattamente quelli attesi;
   - se la registrazione ha modificato `megavault.sqlite`, committa SOLO quella modifica e pushala sul branch canonico MegaVault. Nessun altro cambiamento MegaVault.
2. Checkout:
   - se `/home/daniele/projects/workflowy-importer` non esiste, clona lì il repo;
   - se esiste, verifica che `origin` sia il repo atteso e che non ci siano dirty path che il task debba toccare;
   - resta su `main`, `git fetch` + `git merge --ff-only origin/main`;
   - verifica che la baseline minima sia antenata di `HEAD`.
3. Gate host, senza esplorazione:
   - crea/riusa `.venv`;
   - `python -m pip install -e .`;
   - `python -m unittest discover -s tests -v`;
   - `python -m workflowy_importer.cli --help`;
   - crea sotto `/tmp` un fixture minimo con 2 file Markdown che includa H1/H2, lista annidata, todo aperto+completato, quote, fenced code, `[[B#Beta|alias]]` e `[Alpha](A.md#Alpha)`;
   - esegui UNA volta `workflowy-import-md <fixture> --dry-run`; devono risultare 2 file, nessun link interno ambiguo/non risolto e nessuna scrittura API.
   Se uno di questi gate fallisce, correggi SOLO il difetto direttamente dimostrato, test mirato, push su `main`, poi ripeti solo il leaf fallito e un unico gate host finale.
4. Secret gate:
   - individua SOLO tramite MegaVault secret-ref/env canonico un `WORKFLOWY_API_KEY` già configurato localmente;
   - se manca: `RESULT=BLOCKED`, non creare key, non aprire browser, non cercare credenziali altrove.
5. Smoke reale, una sola campagna:
   - usa il fixture temporaneo, `--parent inbox`, `--root-name "workflowy-importer smoke 746193"` e uno state file dentro `/tmp`;
   - prima importazione: deve creare un solo root e completare il secondo pass dei link;
   - verifica tramite API, con output redatto, che il root esista, che il todo `[x]` risulti completato e che almeno il wikilink/Markdown-link interno sia stato trasformato in hyperlink Workflowy verso un nodo dello smoke;
   - rilancia identico: deve essere `NOOP` e non creare un secondo root;
   - modifica una riga del fixture e rilancia SENZA `--replace`: deve rifiutare l'operazione senza creare duplicati;
   - rilancia con `--replace`: deve creare il nuovo import completo e rimuovere il vecchio root tracciato;
   - elimina infine il root smoke finale tramite API e verifica soltanto che quel root non esista più. Non usare `nodes-export` se non strettamente necessario; preferisci GET/list children mirati.
6. Se tutto PASS, rimuovi solo fixture/state/venv temporanei non appartenenti al checkout (la `.venv` del repo può restare), poi finalizza UNA volta:
   `python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 746193 --confirm-executed`

# Non-goal / stop
Niente import dei file Markdown reali dell'utente, niente browser automation, niente systemd, niente refactor/cleanup, niente sync bidirezionale, niente scansione generale dei repo, niente secondo smoke completo, niente lettura di segreti in chiaro, niente modifiche a Workflowy fuori dal root smoke dedicato. Se emerge un limite API non aggirabile con il codice già previsto, riporta il blocker minimo e fermati.

Output massimo 7 righe e prima riga obbligatoria `RESULT=PASS|BLOCKED|FAIL`: `RESULT`, `PROJECT_ID`, `HOST_GATES`, `DRY_RUN`, `LIVE_SMOKE`, `CLEANUP`, `BLOCKER`.
