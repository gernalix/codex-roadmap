[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=418562 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Ridurre il costo ricorrente di ogni task Codex con due fix di workflow in un'unica sessione: (A) roadmap/finalizzazione Git sicura con worktree locali sporchi; (B) CLI MegaVault stabile per registrare e validare eventi senza SQL/schema discovery.

Assorbe i vecchi prompt `561274` e `804316`. Non modificare PersonalHub.

# A — codex-roadmap
Stato noto: `origin/main` è autorevole; recenti run hanno creato stash solo per leggere la roadmap, archiviato per inferenza un prompt diverso da quello attivo e incluso modifiche preesistenti nel commit.

Implementa il percorso minimo che garantisca:
- lettura/selezione del primo pendente direttamente dal remoto o da stato isolato, senza stash e senza modificare il worktree locale;
- scritture roadmap in stato pulito/isolato oppure blocker preciso; mai inglobare dirt preesistente;
- archiviazione solo con identità esplicita dello stesso file/PROMPT_ID o continuazione dichiarata, mai per somiglianza;
- prima del commit, scope task-owned verificabile;
- ispeziona `codex-preserve-local-spiegazioni` una volta: elimina solo se provatamente ridondante, altrimenti preserva e segnala.

Test mirati: dirty worktree leggibile senza stash; modifica locale intatta; prompt ad-hoc non può archiviare un altro pendente; commit non assorbe dirt preesistente; conflitto reale viene isolato o bloccato.

# B — MegaVault
Aggiungi/estendi, nello stile CLI esistente, due comandi stabili:
- registra un event con project/category/type/status/summary e metadata opzionali, generando ID/timestamp e usando transazione;
- valida solo l'evento/progetto appena cambiato, lasciando invariato il validator globale per audit espliciti.

Il comando deve fallire senza write parziali su input invalido e produrre output machine-friendly. Aggiorna solo la documentazione autorevole necessaria affinché i task futuri usino questi comandi invece di SQLite manuale.

Test solo su DB temporaneo/copia: event valido, input invalido atomico, scoped validation non bloccata da issue globale estranea, global validation ancora disponibile.

# Discipline
Una lettura raggruppata per repo, niente audit generali/refactor. Commit/push separati per i repo effettivamente modificati, una verifica finale ciascuno. PASS solo se A+B passano; poi aggiorna roadmap e STOP.

Output: `PROMPT_ID`, `RESULT`, bootstrap/write path roadmap, identity/commit guard, stash disposition, comando event, comando scoped validate, test, SHA, blocker.
