[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=742618 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST | type=Prompt`

> Retry strettissimo del blocker persistence già localizzato. La feature Timer e la PR #2 sono già integrate in `main`; non rifare merge, discovery, redesign o le cinque suite strumentali già PASS.

# Goal
Verificare sul Fedora/emulatore reale che il fix remoto del blocker `Critical persistent data loss blocked: tagSessions: 1 -> 0` ripari lo stato persistente esistente senza cancellare dati, e chiudere `PROMPT_ID=742618`.

# Starting point verificato
- PR #2 è già MERGED in `main` con merge commit `2d22a8c`; i fix compile/import trovati nella precedente sessione sono già in `7dfd221`;
- ranking/build e tutte le 5 classi strumentali del quick-start sono già PASS: NON ripeterle;
- il blocker reale era una vecchia relazione `tagSessions` presente nello snapshot ma assente da `session_tags` dopo un bootstrap legacy;
- il `CriticalDataGuard` è corretto e NON va indebolito;
- fix remoto già implementato: `LegacyTagSessionRepair` aggiunge soltanto edge mancanti quando il matching sessione è non ambiguo; gira sia dopo bootstrap sia prima dell'auto-consistency;
- test JVM mirato: `LegacyTagSessionRepairTest`;
- `PersonalHub/main` verificato a `fc7b2bb` al momento di preparare questo prompt; se il remoto è avanzato, il remoto corrente è autoritativo purché contenga quel commit;
- l'emulatore canonico va gestito con `tools/android_emulator_control.py`, non col vecchio preflight diretto.

# Procedura minima
1. Leggi solo `AGENTS.md`. Acquisisci il lock PersonalHub con `PROMPT_ID=742618`; se occupato => `BLOCKED` immediato, niente polling.
2. Nel repo `/home/daniele/projects/PersonalHub`: un solo `git fetch origin`; verifica che `origin/main` contenga `fc7b2bb`. Se il checkout può essere fast-forwardato senza perdere/modificare lavoro locale, fallo. Nessun reset/stash/force.
3. NON cancellare o ricreare lo stato che aveva riprodotto il bug: vietati `pm clear`, wipe AVD, delete/recreate AVD, uninstall che rimuova dati, reset DB o cleanup dei dati app.
4. Avvia/riusa l'AVD esclusivamente con:
   `python3 tools/android_emulator_control.py start --timeout 60`
   Usa il `target.serial` JSON restituito; niente discovery ADB duplicata.
5. In un solo Gradle invocation esegui il test JVM mirato e installa la debug sullo stesso emulatore, preservando i dati:
   `ANDROID_SERIAL=<serial> ./gradlew :feature:multitimetracker:testDebugUnitTest --tests com.example.multitimetracker.persistence.LegacyTagSessionRepairTest :app:installDebug --no-configuration-cache --no-daemon`
   Se compile/test/install fallisce: riporta l'errore esatto e STOP. Non modificare codice.
6. Pulisci solo logcat, NON i dati app. Avvia PersonalHub e attendi che Home/Timer sia realmente utilizzabile.
7. Riproduci soltanto il failure path precedente: crea un nuovo timed tag di QA, ad esempio `QA_timed_repair`, senza creare apposta una sessione con quel tag. Salvalo una volta.
8. PASS del blocker solo se TUTTO questo è vero:
   - non compare `Save failed`;
   - logcat non contiene `Critical persistent data loss blocked` né `tagSessions: 1 -> 0` né crash/FATAL correlati;
   - force-stop + riapertura app mostrano ancora il timed tag appena salvato;
   - l'app resta utilizzabile dopo il reload.
9. Non investigare altri problemi UI/dati non riproducibili e non collegati a questo blocker. Segnalali soltanto se impediscono i quattro check sopra.
10. Dopo PASS, ferma l'emulatore con `python3 tools/android_emulator_control.py stop --timeout 30`, rilascia il lock, quindi completa SOLO `PROMPT_ID=742618` con `roadmap_guard complete` (dry-run + reale). Stop immediato.

# Non fare
- non ripetere ranking test, assemble separato o le cinque classi strumentali già PASS;
- non rifare QA layout/ranking/alarm già superata prima del blocker;
- non modificare sorgenti, test o docs;
- non fare commit/push in PersonalHub;
- non buildare/installare Pixel reale e non inviare APK/Telegram;
- niente audit generale, benchmark, sqlite discovery o esplorazione di MegaVault oltre al routing già disponibile.

# Acceptance
PASS = test `LegacyTagSessionRepairTest` PASS + installDebug PASS + riproduzione sullo stesso stato persistente PASS senza data clearing + nessun `Critical persistent data loss` + persistenza dopo restart + roadmap completion verificata.

Output massimo 6 righe: RESULT, PersonalHub SHA, test/install, QA persistence, logcat, roadmap completion/blocker.
