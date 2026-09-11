# WordPulse — verifica locale Alertness/Fatigue e finalizzazione v3

PROMPT_ID=483217 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD | type=Prompt

Esegui direttamente questo file come specifica autoritativa. Non eseguire `roadmap_guard.py select` e non rileggere `roadmap.md`, `README.md`, `spiegazioni.md` o altri prompt. Usa MegaVault solo per fatti operativi che servono davvero; non rifare discovery già presente qui.

# Goal

Finalizza e verifica **solo localmente** l'implementazione Alertness/Fatigue già presente sul remoto `gernalix/wordpulse`, generando l'artefatto Room schema 4 che richiede KSP/Gradle locale, eseguendo i test/build necessari e facendo un QA isolato sul Pixel. Non riprogettare la feature.

# Starting point già verificato

- repo remoto: `gernalix/wordpulse`, branch canonico `main`;
- checkout locale atteso: `/home/daniele/projects/wordpulse`;
- il remoto contiene già l'implementazione completa della feature Alertness/Fatigue, inclusi:
  - metriche di typing aggiuntive: mediana/P95 degli intervalli, CV, micro-pause e last-edit-to-submit;
  - score continuo fatigue `0-100` e alertness `100-fatigue`, con domini speed/rhythm/session-drift/sleep/control;
  - baseline personale con lunghezza, complessità motoria della parola e fascia oraria quando il campione storico è sufficiente;
  - Health Connect opzionale con sola lettura `SleepSessionRecord`;
  - calibrazione PVT/vigilance di 3 minuti con soli aggregati persistiti;
  - Room schema version impostata a `4` e migrazione `3 -> 4`;
  - backup/import aggiornati;
  - overlay UI Alertness;
  - test JVM e instrumented dedicati;
  - `version.txt=3`;
- commit remoto di riferimento che contiene l'ultima correzione sui baseline storici: `dc39350782562dfeda6ba327d98d44afd917553c` o un suo discendente;
- `app/schemas/com.wordpulse.app.data.WordPulseDatabase/4.json` non è stato generato intenzionalmente: richiede la toolchain locale ed è uno degli output di questo task.

Considera già verificati questi fatti. Non fare audit generale del repository, ricerca architetturale o rilettura completa dei sorgenti.

# Scope operativo

1. Sincronizza **una sola volta** il checkout locale con `origin/main` senza perdere lavoro locale. Se esistono modifiche locali o commit non pushati che impediscono un fast-forward sicuro, fermati `BLOCKED`: niente reset/stash/force.
2. Parti dai file/test direttamente coinvolti nella feature e dalla configurazione Gradle esistente. Non esplorare moduli non pertinenti.
3. Esegui prima i gate locali in modo compatto:
   - test JVM;
   - lint;
   - build debug firmata con `--no-configuration-cache` come richiesto dal repo.
   Raggruppa comandi compatibili e non ripetere gate già PASS.
4. Verifica che KSP/Room generi `app/schemas/com.wordpulse.app.data.WordPulseDatabase/4.json` e che lo schema corrisponda alla migration 3→4. Non costruire manualmente l'identity hash.
5. Se un gate fallisce, correggi **solo** l'errore concreto necessario al PASS. Nessun refactor, cleanup, modernizzazione o modifica funzionale fuori scope. Non fare retry identici senza nuova evidenza.
6. Esegui i test Android isolati sul **Pixel 8a** usando `applicationIdSuffix=.qa`, senza toccare il database della app reale. Imposta il device target in modo esplicito se sono collegati più device.
7. QA Pixel minimo e mirato sulla app QA:
   - apertura overlay Alertness senza crash;
   - stato iniziale/baseline insufficiente coerente su DB QA nuovo;
   - flusso richiesta permesso Health Connect se il provider è disponibile;
   - dopo consenso, verifica soltanto che il percorso di lettura sleep non crashi e che l'app distingua correttamente dato presente/assente; **non stampare, esportare o riportare nel log valori di sonno personali**;
   - avvia il test PVT, verifica almeno attesa → stimolo → tap e poi annullalo: non serve attendere 3 minuti per il QA UI;
   - verifica che negare/assenza Health Connect lasci attivo lo scoring typing-only.
8. A fine QA disinstalla dal Pixel il package QA/clone eventualmente installato. Non installare l'APK v3 sopra la app reale in questo task.
9. Se tutto passa, committa e pusha su `gernalix/wordpulse` **solo**:
   - lo schema Room 4 generato;
   - eventuali fix strettamente necessari emersi da compiler/test/QA.
   Non committare APK, build output, database runtime, cache, log, segreti o artefatti QA.

# Verification / acceptance

PASS solo se:

- checkout locale è allineato a `origin/main` senza perdita di lavoro;
- `./gradlew test` PASS;
- `./gradlew lint` PASS;
- `./gradlew --no-configuration-cache assembleDebug` PASS e produce la v3 firmata secondo la configurazione esistente;
- schema Room `4.json` è generato da Room/KSP e migration 3→4 passa;
- test Android isolati sul Pixel PASS;
- smoke QA Alertness/Health Connect/PVT sopra descritto PASS oppure, per Health Connect, il provider è oggettivamente indisponibile e il fallback typing-only è verificato;
- nessun package QA WordPulse resta installato sul Pixel;
- il diff finale WordPulse resta limitato allo schema generato e a eventuali fix strettamente necessari;
- commit/push WordPulse riesce senza force.

Se uno di questi gate non può essere soddisfatto con una correzione locale e strettamente in scope, termina `BLOCKED` o `FAIL` con l'evidenza minima utile. Non ampliare l'indagine.

# Stop e finalizzazione roadmap

Dopo PASS del repo WordPulse, finalizza **solo questo prompt** e fermati. Non aprire il task successivo:

```bash
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483217 --dry-run && \
python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 483217
```

La risposta `status=completed` con `push_verified=git_push_exit_0` è prova sufficiente del push roadmap: niente controlli Git aggiuntivi dopo.

# Output finale

Massimo 6 righe: `PASS/BLOCKED/FAIL`, SHA WordPulse pushato se presente, gate eseguiti, esito Pixel/Health Connect/PVT, cleanup QA, eventuale blocker. Nessuna narrazione dell'esplorazione.
