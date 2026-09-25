PROMPT_ID=107210 | PARENT_PROMPT_ID=175908 | project_id=49 | MegaVault=STRICT

# Goal
P0 assoluto C2: produrre ORA un PersonalHub temporaneo ma affidabile per uso quotidiano, con APK minificato e DB reale compatibile, testarli in modo proporzionato e installare automaticamente ENTRAMBI sul Pixel senza perdere dati. Poi lasciare PersonalHub funzionante e riprendibile per la catena finale.

# Stato/precedenze
- 857906 è già mergiato su main.
- 707603 è canonically running ma non ha un worker Codex vivo; il worktree task/707603 va PRESERVATO integralmente e ripreso dopo questo P0. Non cancellare né sovrascrivere il suo test non tracciato.
- Questo task PREEMPTA la normale catena PH. Se roadmap/single-writer rifiuta l’avvio solo perché 707603 è parcheggiato, non trasformarlo in blocker: crea/usa un worktree isolato 107210 dal main corrente e continua, senza mutare 707603.
- Obiettivo è un interim daily-driver, NON la release finale Play e non 913264.

# Esecuzione
1. Prima di modificare il Pixel, identifica seriale Pixel esatto, package installato/versione e localizza il DB live. Crea backup immutabile verificato (DB + sidecar WAL/SHM se necessari o snapshot consistente) sul Fedora con timestamp+SHA256. Nessun clear-data/uninstall distruttivo.
2. Congela la baseline di codice dal main PersonalHub corrente. Leggi solo schema Room corrente, build config, tooling DB/device e test strettamente pertinenti. Niente audit repo-wide.
3. Determina il DB target esatto richiesto dal codice corrente. Migra ESTERNAMENTE una copia del backup live fino a quello schema con migrazioni SQL/Room equivalenti e solo fix dati realmente necessari. quick_check/integrity_check/FK PASS; confronta conteggi/record rappresentativi dei moduli principali.
4. Produci un APK MINIFICATO. Preferisci la variante più vicina alla produzione che consenta aggiornamento sicuro del package quotidiano e sostituzione DB automatica. Se la build release non permette una sostituzione DB sicura via ADB, implementa il MINIMO meccanismo one-shot/import necessario nell’interim build, fail-closed, con backup+validazione+rollback; niente backdoor permanente generica.
5. Test prima dell’installazione reale: unit/migration/test mirati; build minificata; smoke su emulatore con DB rappresentativo. Se TCL è online e testabile senza intervento, installa/smoke anche lì. Non rendere TCL offline un blocker del Pixel.
6. Sul Pixel: installa l’APK senza wipe; installa/sostituisci automaticamente il DB migrato con percorso sicuro e verificabile; riavvia app/processo. Verifica che il DB effettivamente aperto sia quello previsto.
7. Smoke reale obbligatorio sul Pixel con dati reali: Home + apertura di tutti i moduli almeno una volta, History/Search, lettura/scrittura minima non distruttiva dove sicuro; zero crash. Verifica presenza dati e record rappresentativi. Se un failure è riproducibile e in-scope, fix minimo, rebuild minificata e ripeti solo gate falliti.
8. Registra artifact path, SHA256, package/version, schema DB, backup rollback e risultato device. Non chiamare questo artifact “finale”.
9. Preserva/ripristina il worktree 707603 esattamente come trovato; non incorporarne il WIP salvo necessità dimostrata per il P0.

# Telegram milestone notifications
Dopo OGNI milestone significativa completata invia UNA notifica al proprietario usando le credenziali/helper Telegram canonici già installati, senza stampare segreti. Testo italiano semplice, massimo poche righe: ✅ C2 P0 — <milestone>; risultato concreto; prossimo passo. Milestone minimi: backup Pixel; DB migrato/validato; APK minificato+test emulator; eventuale TCL; installazione APK+DB Pixel; smoke finale PASS. Non notificare ogni comando/test individuale.

# Acceptance
PASS solo se: backup+rollback verificati; DB interim supera quick/integrity/FK e conserva dati; APK è realmente minificato; test mirati+migration+emulatore PASS; TCL testato se disponibile senza diventare blocker; APK e DB sono entrambi installati automaticamente sul Pixel; app apre tutti i moduli con dati reali senza crash; artifact/hash/schema/version sono registrati; notifiche milestone inviate; nessun dato perso; 707603 preservato.

Dopo PASS finalizza 107210 e STOP. Non iniziare la release finale.
