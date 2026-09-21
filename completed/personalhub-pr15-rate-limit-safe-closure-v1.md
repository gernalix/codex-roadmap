PROMPT_ID=684913 | PARENT_PROMPT_ID=576041 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Chiudi definitivamente il recovery di 576041/PR #15 senza ricadere nel ciclo BLOCKED causato dal polling GitHub REST. Il rate-limit è transitorio e NON è di per sé un esito terminale: attendi il reset in-process e continua automaticamente.

# Stato già verificato: non rifare
- Repo: /home/daniele/projects/PersonalHub
- PR #15 OPEN, head esatto 439152af29e291b1b45a93158a005ef78ff59631.
- Tutti i check del head sono verdi tranne `instrumentation`.
- Instrumentation run: 35413045975; job 105816278795.
- Il job è partito 2026-09-19T01:34:00Z e il workflow ha `timeout-minutes: 60`.
- QA AVD locale e build debug 52: PASS.
- Lease test: PASS e lease rilasciato.
- Non rifare questi gate salvo nuovo commit che li invalidi.

# Strategia rate-limit-safe
1. Niente loop modello↔GitHub e niente polling frequente. Prima di interrogare GitHub, se l'orologio locale è ancora precedente a 2026-09-19T02:36:00Z, usa un singolo `sleep` shell fino a quell'istante: zero API durante l'attesa.
2. Poi fai UNA sola lettura dello stato del run/check. Se ricevi HTTP 403 rate-limit:
   - non dichiarare BLOCKED;
   - interroga al massimo una volta l'endpoint rate_limit/headers per ottenere il reset quando disponibile;
   - attendi in un unico comando shell fino al reset + 60 s (fallback 10 min se è secondary-rate-limit senza reset);
   - ritenta una sola volta.
3. Se serve attendere un nuovo run, usa un solo watcher shell a intervallo >=300 s, non una sequenza di tool-call/modello. Nessun retry identico senza sleep/reset.

# Escalation instrumentation
A. Se run 35413045975 è SUCCESS: vai direttamente alla chiusura PR.
B. Se è ancora IN_PROGRESS oltre 60 min + 2 min di grace: trattalo come stale; cancellalo una volta e rilancia una sola volta lo stesso workflow/head. Non cambiare codice.
C. Se il rerun termina SUCCESS: vai alla chiusura PR.
D. Se il rerun FAIL/CANCELLED/TIMED_OUT:
- leggi una sola volta job/step/log pertinenti;
- se emerge failure applicativo reale, correggi solo quello e riesegui il gate invalidato;
- se emerge ancora hang/timeout infrastrutturale del comando Gradle, applica sul candidate il minimo hardening CI: avvolgi `connectedDebugAndroidTest` in un timeout interno <=50m con TERM + breve kill-after, lasciando margine al cleanup del runner; niente refactor CI;
- push una volta e osserva solo il nuovo instrumentation run con la strategia rate-limit-safe sopra.

# Chiusura PR
4. Prima del merge verifica una volta che il candidate head non sia cambiato e che tutti i check richiesti del commit finale siano verdi.
5. Preferisci il normale merge PR. Se l'unico ostacolo è REST 403 dopo che i check verdi sono già stati verificati:
   - attendi il reset come sopra e ritenta una volta;
   - se REST resta indisponibile ma Git push è consentito, usa fallback git SOLO dopo aver verificato che il candidate finale è esattamente quello approvato: fetch mirato, main aggiornato, merge non distruttivo, push main. Lascia che le protezioni server rifiutino l'operazione se non consentita. Non bypassare required checks.
6. Verifica per ancestry che il candidate sia contenuto in origin/main, poi elimina il branch feature/shared-alerts-place-tags locale/remoto e qualsiasi branch recovery di questo task quando il suo diff è contenuto in main. Deve restare solo main, salvo branch estranei realmente attivi che non appartengono a questo task.

# Roadmap
7. Mantieni 576041 storico BLOCKED. Questo prompt è il suo recovery/fix.
8. Finalizza 684913 via single writer solo dopo merge+cleanup. Se la mutation finale incontra 403, attendi il reset e ritenta: NON chiudere BLOCKED al primo rate-limit.
9. Registra la relazione fix 576041 -> 684913 se non già presente.
10. Non modificare altri prompt della roadmap.

# Stop conditions
PASS solo se:
- PR #15 è integrata in main;
- instrumentation finale è verde oppure il workflow è stato corretto e la nuova run è verde;
- cleanup branch completato;
- roadmap 684913 completata e relazione fix presente;
- working tree pulito.

BLOCKED solo per un ostacolo non transitorio che resta dopo almeno un reset rate-limit e una sola strategia di recovery pertinente. Non usare BLOCKED solo perché GitHub chiede di attendere.

Prima riga report: PROMPT_ID=684913
Poi RESULT=PASS|BLOCKED|FAIL.
Output max 7 righe, con CI, MERGE, CLEANUP, ROADMAP, BLOCKER se presente.
