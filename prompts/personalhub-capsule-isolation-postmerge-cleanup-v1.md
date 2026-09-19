PROMPT_ID=418844 | PARENT_PROMPT_ID=223679 | project_id=49 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST

# Goal
Chiudi il residuo lasciato da 223679 senza rifare l'integrazione capsule. La PR PersonalHub #14 è già merged e, alla verifica remota del 2026-09-19, `main` e `feature/100-capsule-isolation` risultavano identici: verifica questo stato una sola volta e rimuovi il branch ormai merged locale/remoto.

# Starting point
- repo: `/home/daniele/projects/PersonalHub`;
- PR #14: merged, merge commit `83f052e8ad94a84baef983621f2df47dc1284655`;
- branch residuo: `feature/100-capsule-isolation`;
- non reimplementare capsule isolation, non rifare QA/build già superati e non fare bump versione.

# Esecuzione minima
1. Un solo fetch mirato di `origin/main` e del branch residuo. Verifica che PR #14 sia merged, che il merge commit sia antenato di `origin/main` e che il branch non contenga commit unici rispetto a `origin/main`.
2. Se il branch è identico o completamente contenuto in main, non eseguire Gradle, emulatori, lease PH, test o modifiche prodotto.
3. Porta il checkout locale su `main` solo in modo non distruttivo; non perdere dirty work non correlato.
4. Elimina `feature/100-capsule-isolation` localmente con delete safe e da origin. Verifica infine che non esista più né locale né remoto.
5. Se trovi commit unici/divergenza inattesa, non cancellare il branch e non tentare una nuova integrazione ampia: diagnostica solo la divergenza e termina BLOCKED con evidenza concisa.

# Acceptance / stop
PASS se il lavoro capsule è già contenuto in main e il branch residuo è assente locale/remoto. Nessun commit di prodotto, nessun bump, nessun build/test non necessario.
Finalizza PROMPT_ID 418844 con roadmap_finish; BLOCKED/FAIL con roadmap_result. Output max 6 righe.
