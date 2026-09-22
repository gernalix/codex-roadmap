PROMPT_ID=327684
PARENT_PROMPT_ID=682741
ROADMAP_PROJECT=minsp-export
MODEL=GPT-5.5
REASONING=medium
MEGAVAULT=FAST

# Goal
Esegui SOLO il bootstrap iniziale sicuro di gernalix/minsp-export: il remoto esiste ma non ha ancora alcun commit, quindi crea il primo main canonico a partire dal checkout locale già implementato. Non eseguire ancora scraping sanitario.

# Stato verificato
- https://github.com/gernalix/minsp-export esiste, default branch main, ma repository remoto vuoto.
- 682741 è BLOCKED solo perché repo-task non può creare un worktree isolato senza una base Git committata.
- Il codice applicativo dovrebbe già esistere localmente in ~/projects/minsp-export.
- Questo prompt NON ha repo metadata di proposito: serve esclusivamente a creare la prima baseline; dal task successivo torna obbligatorio il normale single-writer.

# Esecuzione
1. Claim 327684.
2. Ispeziona SOLO ~/projects/minsp-export e MegaVault quanto basta a identificare il progetto. Nessun audit di altri repo.
3. Verifica/crea in modo non distruttivo il repository Git locale:
   - branch canonico main;
   - origin esatto https://github.com/gernalix/minsp-export.git;
   - preserva ogni file esistente.
4. Prima di stage/commit applica un gate privacy severo. NON committare:
   - export sanitari, raw/, normalized data, health.sqlite o altri DB con dati utente;
   - PDF/allegati/screenshot clinici;
   - profilo browser, cookie, storage/sessioni;
   - .env, credenziali, token, Authorization, secret;
   - log/runtime state/checkpoint contenenti dati personali.
   Aggiorna .gitignore solo se necessario per escluderli.
5. Se il checkout locale NON contiene il codice sorgente atteso, BLOCKED con LOCAL_SOURCE_MISSING; non inventare/reimplementare l'app.
6. Esegui test mirati già presenti solo se non richiedono login/dati reali.
7. Crea UN primo commit con soli codice/test/docs generici sicuri e pushalo a origin main.
8. Verifica con fetch + rev-parse che origin/main esista e coincida con il commit pushato.
9. Registra/riconcilia MegaVault per minsp-export usando solo project_id reale trovato; non inventare ID.
10. STOP immediato. Nessuna visita a Min Sundhedsplatform.

# Acceptance
PASS solo se origin/main ha una baseline reale, il working tree locale è preservato e nessun dato sanitario/segreto è nel commit.

# Report
Max 7 righe: PROMPT_ID, RESULT, PROJECT_ID, FIRST_COMMIT, REMOTE_MAIN, PRIVACY_GATE, BLOCKER.