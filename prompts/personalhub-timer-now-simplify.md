[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=314719 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=2/4 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Semplificare SOLO Timer > Now e, nella stessa unica sessione emulator necessaria a questo task, chiudere anche la QA UI deferred della fase 1.

# Lease + emulator helper — niente discovery
Prima di implementazione/QA esegui direttamente `python3 tools/personalhub_task_lock.py acquire --prompt-id 314719`. Se non acquisisce, BLOCKED senza attesa. Dopo PASS/BLOCKED/FAIL esegui `python3 tools/personalhub_task_lock.py release --prompt-id 314719`.
Per l'emulatore usa soltanto `python3 tools/android_emulator_control.py status|start|wait|stop`; `start`/`wait` restituiscono il `target.serial` canonico Pixel_8a. Non aprire `AGENTS.md` per scoprire lease/emulator e non fare discovery ADB/AVD parallela salvo blocker concreto dell'helper.

# Routing — niente esplorazione Timer
Usa `.codex/CODE_MAP.tsv` riga `timer.now_ui` come entrypoint; `timer.tags` solo se serve al filtro/ranking. Apri `MainViewModel`/persistence/altri tab solo se un errore concreto lo impone.
Evidenza già verificata: Now mostra sessione attiva + `Active tags` duplicativo + Quick Start + FAB ambiguo nello stesso viewport.

# Layout richiesto
1. Prima sezione `Sessioni in corso`; preserva card/tap/long-press/edit/stop.
2. Rimuovi `Active tags` dalla home Now; non cancellare backend/calcoli usati altrove.
3. Subito dopo `Avvia per tag`: search + massimo 6 tag recenti/frequenti a query vuota; ricerca su tutti i tag quando si digita; `Mostra tutti/Nascondi` solo se necessario.
4. Tap tag = start immediato; long-press = multiselect; in multiselect conferma/annulla evidenti. Nessuna conferma nel caso singolo.
5. Elimina FAB Play orfano; usa una piccola azione esplicita `Nuova sessione` vicino a Quick Start.
6. Random Timer resta accessibile ma secondario/compatto sotto Quick Start; NON toccare scheduling/notifiche/result logic.
7. Pixel 8a viewport: con una sessione attiva, sessione + Quick Start devono essere leggibili senza il precedente caos/whitespace.

# Verifica economica + UNA sessione emulator
1. Prima esegui i soli unit/leaf test Now interessati dal diff.
2. Avvia UNA volta l'emulatore canonico Pixel_8a con `android_emulator_control.py start` + `wait`; riusa il serial restituito per tutta la QA.
3. In UNA singola invocazione Gradle androidTest, con `--quiet --console=plain` e filtro alle classi pertinenti, esegui:
   - il/i test UI Hub/episodi/fatigue aggiunti da `PROMPT_ID=838979`;
   - i test Now realmente pertinenti (`QuickStartIdleLayoutInstrumentedTest`, `QuickStartTagLauncherInstrumentedTest`, `QuickStartTimedHierarchyInstrumentedTest`, `NowTimerRulesRegressionInstrumentedTest` solo se toccato il relativo comportamento).
   Non lanciare tutta `connectedDebugAndroidTest` senza filtro. Questa invocazione compila gli APK necessari: NON fare un `assembleDebug` separato. Su PASS non ristampare output Gradle verboso.
4. Dopo i test, una sola ispezione semantica con `android_ui_summary.py --serial <serial>` + un solo screenshot finale Now con una sessione attiva. Nessuna seconda navigazione/QA se i criteri sono già evidenti.
5. Stop emulator con `python3 tools/android_emulator_control.py stop`. Failure => leaf fix + solo il test fallito; una sola riconferma finale del set filtrato.

# Non-goal
Niente refactor Timer, persistence, hierarchy, Random Timer scheduling, Alerts, Timeline, navigation globale, Pixel/TCL reale o benchmark.

# Campagna
Fase intermedia: niente bump `version.txt`, install Pixel reale o APK/Telegram. Push una volta dopo PASS. Questa fase è proprietaria della QA UI emulator di fase 1+2 per evitare due bootstrap device separati.

# Acceptance
PASS se UI Hub deferred di fase 1 passa, Now non mostra più `Active tags`, Quick Start è compatto/completo, tap/long-press funzionano, `Nuova sessione` è esplicita, Random Timer resta disponibile e il singolo screenshot/summary conferma il viewport richiesto.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 314719 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 314719`
Poi rilascia il lease con il comando già indicato. Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.