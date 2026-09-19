PROMPT_ID=735218 | PARENT_PROMPT_ID=684913 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Chiudi definitivamente PersonalHub PR #15. Il precedente 684913 è terminato BLOCKED perché l'instrumentation Oracle richiede un runtime privato ma il repository non aveva GitHub Actions secrets configurati. L'utente ha ora chiarito che i secret necessari esistono già nella cartella `secrets/` del checkout MegaVault canonico.

# Stato già verificato
- PR #15 è ancora il candidate da integrare.
- I gate locali precedenti non vanno rifatti salvo che un nuovo commit li invalidi.
- `DatasetteSyncInstrumentedTest.configureFromPrivateRuntimeFile()` legge `noBackupFilesDir/datasette-runtime.json` con campi `url`, `database`, `table`, `token`.
- `oracleFullRoundTripUpload()` richiede che quella configurazione privata sia stata caricata.
- Il workflow `.github/workflows/android-instrumentation-ci.yml` oggi non stagea tale runtime.
- I secret GitHub/Oracle necessari sono già disponibili localmente sotto `MegaVault/secrets/`.
- 684913 è storico BLOCKED: NON riusare o riattivare quell'ID.

# Regole sui secret
1. Individua i file canonici sotto MegaVault/secrets senza stampare valori, token, URL sensibili o fingerprint. Usa solo nomi/path redatti nei report.
2. Non committare mai secret, runtime JSON reale, token o credenziali in PersonalHub, MegaVault o artifact/log.
3. Se serve configurare GitHub Actions, usa `gh secret set`/meccanismo equivalente leggendo i valori direttamente da file/stdin; nessun valore in argv, echo, report o shell history quando evitabile.
4. Preferisci un unico secret runtime JSON se esiste già un file canonico compatibile; altrimenti mappa i secret esistenti nei quattro campi richiesti senza duplicare fonti di verità.
5. Qualunque file temporaneo con credenziali deve vivere solo in storage privato/runner temp, permessi restrittivi, cleanup con trap/finally.

# Esecuzione autonoma
1. Riprendi nella stessa chat di 684913. Ispeziona e preserva le modifiche locali non pushate lasciate dal tentativo precedente; non rifare l'analisi già svolta.
2. Acquisisci il lease solo quando richiesto dalle regole PersonalHub e recupera automaticamente lock stale secondo AGENTS.md.
3. Correggi la CI in modo che l'intera copertura rimanga reale:
   - suite hermetica/emulator-safe deve continuare a passare senza dipendere da rete privata quando non la richiede;
   - il test Oracle reale deve ricevere il runtime privato in modo sicuro e deve essere eseguito, non skipped/disabled/assumed.
   Puoi serializzare moduli/test, separare job/step o usare un'invocazione instrumentation mirata se questo risolve l'aggregazione multi-modulo, purché tutti i test richiesti restino coperti.
4. Configura i GitHub Actions secrets necessari dal materiale già presente in MegaVault/secrets. Non chiedere all'utente di ricopiare valori che sono già disponibili localmente.
5. Stagia `datasette-runtime.json` nel sandbox Android con il confine già documentato dal test ("private run-as stdin"); non passare credenziali come instrumentation args e non mostrarle nei log.
6. Verifica localmente solo il minimo gate necessario con timeout espliciti. Se il test Oracle fallisce, diagnostica la root cause e correggila; non trasformare failure reale in skip.
7. Push una volta il candidate corretto. Porta required CI/instrumentation a PASS reale. CI pending, rate-limit temporaneo, runner hang recuperabile, conflitto Git o lease stale non sono BLOCKED: recupera e continua.
8. Quando tutti i required checks del commit finale sono verdi:
   - verifica exact candidate head;
   - merge PR #15;
   - verifica ancestry in origin/main;
   - elimina i branch del task quando completamente contenuti in main;
   - lascia main sincronizzato e working tree pulito.
9. Finalizza 735218=completed esclusivamente via single writer. Mantieni 684913 storico BLOCKED e registra la relazione fix 684913 -> 735218.
10. Non modificare altri prompt della roadmap.

# Stop
PASS solo se:
- nessun secret è esposto o committato;
- test Oracle reale PASS con runtime privato;
- tutta la required instrumentation/CI finale PASS;
- PR #15 integrata in main;
- ancestry + cleanup branch + working tree pulito;
- 735218 completed via single writer.

BLOCKED solo per credenziale realmente mancante/invalida o permesso esterno non ottenibile dopo aver verificato la fonte MegaVault esistente; non per semplice assenza iniziale di GitHub Actions secret.

Prima riga finale: PROMPT_ID=735218
Seconda riga: RESULT=PASS|BLOCKED|FAIL
Output max 7 righe: SECRET_SETUP(redatto), CI, FIX, MERGE, CLEANUP, ROADMAP, BLOCKER.
