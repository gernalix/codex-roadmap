PROMPT_ID=570349

# Goal
Ripristina SOLO il publisher live delle sessioni Codex sul Fedora reale, usando i fix già mergiati da ChatGPT. Il risultato finale deve essere: `gernalix/codex-usage` resta un repository dati posseduto direttamente da `codex-usage-publisher`, il generic single-writer non ne blocca `main`, il timer torna a scattare ogni minuto e i dump nativi tornano visibili remotamente senza copia-incolla.

# Starting point autoritativo
- checkout Fedora github-autosync: `/home/daniele/projects/github-autosync`;
- checkout dati: `/home/daniele/projects/codex-usage`;
- runtime publisher: `codex-usage-publisher.service/.timer`;
- github-autosync remoto contiene già il fix almeno fino a `6a260de8e460a9e475edf24c84ecdd7589578240`: `gernalix/codex-usage` è in `INDEPENDENT_CANONICAL_WRITER_REPOSITORIES`, con test e docs;
- codex-usage-monitor remoto contiene la documentazione del writer ownership almeno fino a `feb2e72902d75c5611310455a1cfd0017f5020d9`;
- evidenza del failure reale: il publisher veniva rifiutato con `refs/heads/main is single-writer protected`; è comparso anche `~/projects/codex-usage/.git/index.lock`; il timer risultava active ma con `Trigger: n/a`;
- NON modificare né interrompere il goal PersonalHub 822595.

# Esecuzione stretta
1. Prima azione: esegui `roadmap_start.py` per 570349 e procedi solo se lo stato diventa running. Usa il worktree restituito solo se emerge una modifica codice realmente necessaria.
2. Aggiorna il checkout canonico `~/projects/github-autosync` al `origin/main` già corretto con fetch + fast-forward sicuro verso l'esatto remote tip. Nessun reset/stash/clean distruttivo.
3. Esegui solo il gate mirato:
   `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_github_autosync.AutosyncTests.test_independent_canonical_writer_repo_is_not_reconciled -v`
   e `python3 -m py_compile autosync_core.py`.
   Se PASS, non lanciare suite più ampie salvo un failure concreto successivo.
4. Esegui una sola `github-reconcile` reale per applicare l'esenzione al checkout locale. Verifica poi che l'hook generic con marker `github-autosync-single-writer-v1` non protegga più `~/projects/codex-usage`. Non installare un writer alternativo.
5. Gestisci SOLO l'eventuale `.git/index.lock` di `codex-usage`: prima verifica con strumenti di processo/file-holder che nessun Git attivo lo possieda. Se è realmente stale, elimina solo quel lock. Se è posseduto da un processo attivo, non rimuoverlo forzatamente.
6. Avvia una volta `codex-usage-publisher.service`, poi riavvia `codex-usage-publisher.timer`. Verifica `Result=success`/exit 0 del servizio e che il timer sia enabled+active con un prossimo trigger circa un minuto nel futuro. Non creare un secondo timer/service.
7. Controlla il journal dell'ultimo run: nessun `single-writer protected`, nessun `index.lock`, nessun TEMPFAIL. Se emerge un failure direttamente nello stesso dominio, correggi il minimo necessario e ripeti solo il leaf gate fallito; niente retry identici.
8. Verifica il contratto end-to-end remoto: `origin/main` di `gernalix/codex-usage` deve avanzare o risultare già aggiornato dal publisher, e il dump pubblicato deve contenere evidenza della sessione/PROMPT_ID `822595` sotto `native-sessions/` o indice equivalente. Non stampare contenuto sensibile: basta path/contatore/riscontro booleano.
9. Non instradare i dump minuto-per-minuto tramite `repo-task`, branch o PR. Non modificare dati di `codex-usage` a mano, salvo la rimozione sicura del solo lock stale descritta sopra.
10. Appena tutti gli acceptance criteria sono verificati, finalizza 570349 e STOP.

# Acceptance
PASS solo se:
- il checkout locale github-autosync include il fix remoto;
- il test mirato PASS;
- `codex-usage` non ha più il generic single-writer guard;
- nessun lock stale blocca Git;
- un run reale del publisher termina con successo;
- il timer ha un NEXT/Trigger reale e continua con cadenza di circa un minuto;
- il repository remoto riceve di nuovo i dump incrementali e 822595 è riscontrabile senza esporre il contenuto;
- nessun dato/sessione viene cancellato o ricreato.

# Stop
Al PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 570349 --confirm-executed`

Output massimo 8 righe:
PROMPT_ID=570349
RESULT=PASS|BLOCKED|FAIL
AUTOSYNC=<head/test/guard>
LOCK=<absent|stale-removed|active-blocker>
PUBLISHER=<service result>
TIMER=<enabled/active/next>
REMOTE_DUMP=<822595 visible yes/no>
BLOCKER=<none|unico blocker concreto>
