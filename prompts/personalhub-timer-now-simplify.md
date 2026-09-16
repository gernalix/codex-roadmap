[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=314719 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=2/4 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Semplificare SOLO Timer > Now e, nella stessa unica sessione emulator necessaria a questo task, chiudere anche la QA UI deferred della fase 1 già completata.

# Starting point autoritativo
- repo locale canonico: `/home/daniele/projects/PersonalHub`;
- fase 1 `PROMPT_ID=838979` è già completata: implementazione `3cfd170cc8a2b2155f8f531ce6efcb0fc116247f`;
- follow-up remoto già applicato dopo il PASS della fase 1: `99bcf743965d9d9508d33ad50ad97946285d08c8`, che evita letture ripetute di `SnapshotStore` nel Timer Hub adapter senza cambiare il contratto UI;
- la fase 1 ha aggiunto unit test host, NON un androidTest UI dedicato: questa fase deve quindi creare/eseguire il minimo test strumentale necessario per chiudere davvero la QA UI Hub/episodi/fatigue differita;
- prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY/MegaVault salvo blocker concreto.

# Lease + sync + emulator helper — niente discovery
1. Esegui direttamente `python3 tools/personalhub_task_lock.py acquire --prompt-id 314719`. Se non acquisisce, `RESULT=BLOCKED` senza attesa.
2. Subito dopo il lease, prima di leggere/modificare codice: richiedi worktree pulito, poi `git fetch --prune origin && git pull --ff-only origin main`; registra lo SHA di `origin/main` come base remota del task. Se non è possibile fast-forwardare pulitamente, BLOCKED: niente rebase/merge.
3. Per l'emulatore usa soltanto `python3 tools/android_emulator_control.py status|start|wait|stop`; `start`/`wait` restituiscono il `target.serial` canonico Pixel_8a. Non aprire `AGENTS.md` per scoprire lease/emulator e non fare discovery ADB/AVD parallela salvo blocker concreto dell'helper.
4. Prima del commit/push finale esegui UNA sola `git fetch origin` e confronta `origin/main` con la base remota registrata. Se è avanzato durante il task, `RESULT=BLOCKED`: non fare rebase/merge né ripetere tutti i gate dentro questa sessione. Questo evita il churn osservato nel run 838979.
5. Dopo PASS/BLOCKED/FAIL rilascia sempre `python3 tools/personalhub_task_lock.py release --prompt-id 314719`.

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
1. Prima esegui i soli unit/leaf test Now interessati dal diff **più una sola volta** il leaf host della fase 1 `HubContextVerticalSliceTest.timerHubSummaryUsesTitleThenTagNamesThenHumanTimeFallback`, perché il follow-up `99bcf743` ha toccato quell'adapter dopo il PASS originario.
2. Aggiungi, solo se ancora assente, UN test androidTest focalizzato per la QA UI differita della fase 1: Home mostra le spiegazioni Context/Search/Activity; Search mostra `Episodi salvati`, consente riapertura di un episodio titolato e mostra il wording fatigue previsto. Riusa fixture/helper esistenti; niente nuova infrastruttura.
3. Avvia UNA volta l'emulatore canonico Pixel_8a con `android_emulator_control.py start` + `wait`; riusa il serial restituito per tutta la QA.
4. In UNA singola invocazione Gradle androidTest, con `--quiet --console=plain` e filtro alle sole classi pertinenti, esegui:
   - il test UI Hub/episodi/fatigue appena descritto;
   - i test Now realmente pertinenti (`QuickStartIdleLayoutInstrumentedTest`, `QuickStartTagLauncherInstrumentedTest`, `QuickStartTimedHierarchyInstrumentedTest`, `NowTimerRulesRegressionInstrumentedTest` solo se toccato il relativo comportamento).
   Non lanciare tutta `connectedDebugAndroidTest` senza filtro. Questa invocazione compila gli APK necessari: NON fare un `assembleDebug` separato. Su PASS non ristampare output Gradle verboso.
5. Dopo i test, una sola ispezione semantica con `android_ui_summary.py --serial <serial>` + un solo screenshot finale Now con una sessione attiva. Nessuna seconda navigazione/QA se i criteri sono già evidenti.
6. Stop emulator con `python3 tools/android_emulator_control.py stop`. Failure => leaf fix basato sull'errore + solo il test fallito; poi una sola riconferma finale del set filtrato. Non rilanciare identico l'intero set dopo ogni ipotesi intermedia.

# Non-goal
Niente refactor Timer, persistence, hierarchy, Random Timer scheduling, Alerts, Timeline, navigation globale, Pixel/TCL reale o benchmark.

# Campagna
Fase intermedia: niente bump `version.txt`, install Pixel reale o APK/Telegram. Push una volta dopo PASS. Questa fase è proprietaria della QA UI emulator di fase 1+2 per evitare due bootstrap device separati.

# Acceptance
PASS se UI Hub deferred di fase 1 passa, Now non mostra più `Active tags`, Quick Start è compatto/completo, tap/long-press funzionano, `Nuova sessione` è esplicita, Random Timer resta disponibile e il singolo screenshot/summary conferma il viewport richiesto.

# Stop
Solo se tutti gli acceptance gate sono PASS e la base remota non è avanzata: commit/push PersonalHub una volta, quindi
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 314719 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 314719`.
Se `roadmap_guard` rifiuta il completamento, il risultato complessivo è `RESULT=BLOCKED`, anche se il codice è PASS; non manipolare manualmente la roadmap. Rilascia poi il lease. Prima riga dell'output: `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe totali.
