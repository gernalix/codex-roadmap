[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=734581 | project_id=49 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

> Esecuzione diretta. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Parti dai fatti verificati qui sotto e usa solo i file/tool direttamente pertinenti.

# Goal
Verificare sul Pixel 8a fisico il fix startup già presente in PersonalHub `main` e ridurre ulteriormente il cold start solo se una misura reale dimostra ancora un collo di bottiglia materiale.

# Fatti già verificati
- `gernalix/PersonalHub` deve restare trunk-only: esiste solo `main`; non creare branch.
- Baseline precedente sul Pixel reale: cold start `Displayed ...MainActivity: +13s293ms`, `Launch timeout`, `Skipped 687 frames`.
- Root cause dimostrata: `LegacyTagSessionRepair.repairIfNeeded()` eseguiva I/O/query/transaction DB sincrone in `PersonalHubApplication.onCreate()`.
- `main` contiene già il fix che sposta il repair nel `PostFirstFrameStartup`/executor esistente, dopo il primo frame; `DatabaseVault.ensureStartupReady()` e recovery DB restano volutamente sincroni per sicurezza dati.
- Package reale da misurare: `com.gernalix.personalhub`; ignora `com.gernalix.personalhub.qa` salvo che blocchi tecnicamente il test.

# Scope
1. Pull fast-forward di PersonalHub `main`; nessuna esplorazione generale del repo.
2. Esegui prima il gate host più economico pertinente: compile/test mirati alle classi startup/Timer cambiate. Non eseguire suite globale se i mirati passano.
3. Costruisci una sola APK debug necessaria al test; installala sul Pixel con `adb install -r` preservando i dati. Nessun `pm clear`, uninstall o reset dati.
4. Misura **3 cold start** del package reale: per ogni prova `am force-stop` + `am start -W`, raccogliendo in un unico log bounded per prova solo `Displayed`, launch timeout, frame skip, ANR/FATAL e `MTT_STARTUP`/startup markers. Non fare dump logcat ripetuti equivalenti.
5. Riporta min/mediana/max `TotalTime` (o metrica `am start -W` equivalente) e confronta col baseline 13.293 s.
6. Se mediana <= 2.5 s, nessun `Launch timeout`, nessun ANR/FATAL e nessun frame skip massivo (>100 frame): PASS e STOP, senza profiler/audit aggiuntivi.
7. Solo se il gate 6 fallisce: acquisisci **una sola** traccia Perfetto/System Trace del cold start, identifica il maggiore blocco sulla critical path e applica il minimo fix dimostrato. Non ottimizzare componenti non presenti nella traccia. Poi ripeti una sola volta compile/test mirati + le stesse 3 misure.
8. Se serve una modifica, commit+push diretto su `main`. Se non serve, nessun commit artificiale.

# Non-goal
- niente refactor/cleanup/modernizzazione;
- niente branch, PR o audit generale;
- niente modifica a `DatabaseVault.ensureStartupReady()` senza evidenza esplicita della traccia;
- niente bump `version.txt`, release finale o Telegram delivery;
- niente test su TCL/emulatore se il Pixel è disponibile: il requisito è il comportamento del Pixel reale.

# Stop
PASS quando il Pixel dimostra startup rapido/stabile secondo il gate sopra, oppure dopo **un solo** ciclo evidence-based di profiling+fix se necessario. Se resta lento dopo quel ciclo, BLOCKED con il singolo hotspot residuo e i numeri misurati; non aprire una nuova indagine.

Su PASS completa solo questo prompt:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 734581 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 734581`

`push_verified=git_push_exit_0` è terminale: niente status/fetch/rev-parse successivi sulla roadmap.

Output massimo 7 righe: RESULT, baseline→nuovi tempi, timeout/frame/ANR, eventuale hotspot+fix, test/build, Pixel install/test, commit/push o blocker.
