PROMPT_ID=517308 | project_id=51 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Risolvi SOLO il merge conflict locale attivo di `codex-roadmap` senza perdere l'unico lavoro locale non ancora upstream, e termina con `/home/daniele/projects/codex-roadmap` su `main` pulito e sincronizzato all'ultimo `origin/main`.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/codex-roadmap`, branch `main`;
- GitHub Desktop mostra un merge in corso con **1 file in conflitto: `spiegazioni.md`**; al momento dello screenshot la branch mostrava circa `1 ↑ / 11 ↓`;
- il commit locale appena creato era mostrato come `Update spiegazioni.md`;
- il remoto canonico aveva già almeno `4123b796e839ce0959361d9f780e0b396a5d5e09` e, dopo la registrazione di questo task, `origin/main` sarà necessariamente un suo discendente;
- il remoto attuale è autoritativo per ordine roadmap, esclusione della campagna CI `483921` dalla coda Codex e metadata modello/reasoning dei prompt;
- NON risolvere il conflitto contro lo snapshot remoto vecchio già inglobato nel merge in corso: prima preserva il commit locale, poi riallineati all'ultimo `origin/main`.

Prompt autosufficiente: non leggere altri repo, MegaVault, MEMORY o report storici. Lavora solo su Git/stato e, se necessario, `roadmap.md`, `spiegazioni.md` e il singolo commit locale non upstream.

# Esecuzione minima
1. In UN blocco read-only raccogli: `git status --porcelain=v2 --branch`, presenza di `.git/MERGE_HEAD`, `HEAD`, `origin/main` e massimo gli ultimi 3 commit locali. Nessun dump ampio.
2. Se esiste un merge attivo, crea prima una branch di salvataggio locale `backup/conflict-517308` puntata all'HEAD pre-merge (se esiste già deve puntare allo stesso commit), poi esegui UNA volta `git merge --abort`. Se abort fallisce, `BLOCKED`: niente reset/checkout distruttivi.
3. Esegui UNA sola sync metadata: `timeout 20s git fetch origin main`. Verifica che `origin/main` includa `4123b796e839ce0959361d9f780e0b396a5d5e09`.
4. Confronta SOLO i commit presenti in `backup/conflict-517308` ma non in `origin/main`. Caso atteso: un solo commit locale che modifica `spiegazioni.md`. Leggi soltanto il suo diff e la versione corrente `origin/main:spiegazioni.md`.
5. Se emergono commit locali inattesi su altri file o più di un'intenzione non chiaramente ricostruibile, `BLOCKED` lasciando intatta la backup branch. Non fare rebase/cherry-pick esplorativi.
6. Se il diff locale su `spiegazioni.md` è ormai obsoleto/ridondante rispetto al remoto, NON reapplicarlo. Se contiene informazione unica ancora valida, annotala in memoria, senza conservare struttura/ordine obsoleti. Poi riallinea `main` in modo fail-safe all'ultimo `origin/main` usando la backup branch come garanzia; applica solo l'eventuale informazione unica sul file remoto corrente.
7. Vincoli semantici: non reintrodurre `retained-repositories-github-ci-completion` sotto `prompts/` o in `roadmap.md`; non ripristinare vecchio ordine o vecchi metadata; mantieni `roadmap.md` / `spiegazioni.md` / `prompts/*.md` 1:1 secondo lo stato remoto più recente.
8. Verifica una sola volta: nessun file unmerged (`git diff --name-only --diff-filter=U` vuoto), nessun conflict marker nei file toccati, `git diff --check`. Se hai reapplicato informazione unica, crea UN commit mirato e pushalo; altrimenti non creare commit artificiale.
9. Verifica che `main` sia pulito e che `HEAD` sia uguale o discendente dell'ultimo `origin/main`. Solo dopo PASS elimina la branch locale `backup/conflict-517308`.

# Acceptance
PASS solo se il merge conflict è sparito, nessun lavoro locale unico è stato perso, `main` è pulito/sincronizzato, `spiegazioni.md` riflette lo stato remoto corrente senza regressioni e GitHub Desktop può tornare a Pull/Push normale senza stato di merge.

# Non-goal
Niente modifica di prompt funzionali, riordino ulteriore roadmap, refactor, test di altri repo, audit Git generale, rebase history, force-push o cleanup non necessario.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 517308 --confirm-executed`

Il finalizzatore può avanzare la roadmap rispetto al remote appena sincronizzato; non fare dry-run separato né `git status`/fetch/readback dopo `status=completed|already_completed`.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe: `RESULT`, `BACKUP`, `LOCAL_ONLY`, `RESOLUTION`, `SYNC`, `BLOCKER`.
