[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=314719 | project_id=49 | campaign_id=personalhub-20260916-usability-reliability | phase=2/4 | model=GPT-5.5 | reasoning=low | MegaVault=FAST`

# Goal
Semplificare SOLO la schermata Timer > Now, eliminando informazioni duplicate e rendendo immediato l'avvio di una sessione per tag senza perdere le funzioni esistenti.

# Evidenza verificata
Nello screenshot reale 2026-09-16 la schermata mostra nello stesso viewport: `Normal sessions` con la sessione attiva, subito sotto `Active tags` che ripete gli stessi tag/tempi, poi `Start by tag` con search + molti chip e un FAB Play isolato. Il codice di `NowScreen.kt` dichiara esplicitamente che `Active tags` è sempre visibile e che Quick Start occupa metà inferiore quando ci sono sessioni: la confusione è quindi strutturale, non un glitch.

Usa `.codex/CODE_MAP.tsv` (`timer.root`, `timer.sessions`, `timer.tags`) e apri solo: `capsules/now/ui/NowScreen.kt`, `NowCapsuleUi.kt`, `QuickStartTagLauncher.kt`, relativo controller/state e i test Now/QuickStart già indicizzati. Niente audit del modulo Timer.

# Layout richiesto
1. Prima sezione = sessioni in corso. Mantieni card, elapsed time, tap/long-press/edit/stop esistenti. Usa un titolo chiaro tipo `Sessioni in corso`; non distinguere “Normal sessions” se non esiste un reale confronto necessario all'utente.
2. Rimuovi `Active tags` come sezione sempre visibile dalla home Now: duplica lo stato delle sessioni e i tag sono già accessibili in `Tags`. Non cancellare i dati/calcoli backend se servono altrove.
3. Subito dopo = `Avvia per tag`: search + massimo 6 tag recenti/frequenti quando la query è vuota. Digitando, cerca nell'intero set di tag. Aggiungi `Mostra tutti`/`Nascondi` solo se serve per accedere senza ricerca.
4. Preserva l'interazione efficiente: tap su un tag = start immediato; long-press = multiselect; in multiselect mostra in modo evidente conferma e annulla. Nessun tap di conferma per il caso singolo.
5. Elimina il FAB Play orfano. Per la sessione manuale/custom usa una piccola azione esplicita `Nuova sessione` vicino alla sezione di avvio, non un controllo fluttuante ambiguo.
6. `Random timer` resta accessibile ma secondario e compatto sotto Quick Start; NON modificare in questa fase scheduling/notifiche/result logic.
7. Evita grandi vuoti verticali e duplicazioni. A larghezza Pixel 8a, sessione attiva + quick start devono essere leggibili nello stesso primo viewport per il caso normale di una sola sessione.

# Verifica mirata
Aggiorna solo i test pertinenti già esistenti (`QuickStartIdleLayoutInstrumentedTest`, `QuickStartTagLauncherInstrumentedTest`, `QuickStartTimedHierarchyInstrumentedTest`, `NowTimerRulesRegressionInstrumentedTest` o equivalenti correnti). Esegui leaf test + un solo build debug. Poi usa UNA QA sull'emulatore canonico Pixel_8a tramite gli helper di `AGENTS.md`: verifica semanticamente con `android_ui_summary.py` e fai un solo screenshot finale della schermata Now con una sessione attiva. Nessun Pixel/TCL, benchmark o full-suite.

# Non-goal
Niente refactor Timer, persistence, tag hierarchy, random-timer scheduling, Alerts, Timeline, navigation globale o redesign grafico degli altri tab.

# Campagna / release
Fase intermedia: NON incrementare `version.txt`, NON installare sul Pixel e NON inviare APK/Telegram. Push una sola volta dopo PASS.

# Acceptance
PASS se non c'è più la sezione duplicativa `Active tags`, Quick Start è compatto e completo, tap/long-press funzionano, la creazione manuale è esplicita, Random timer resta accessibile e il viewport Pixel 8a non presenta il precedente caos/whitespace.

# Stop
Acquisisci/rilascia il lease PH secondo `AGENTS.md`. Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 314719 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 314719`

Dopo `status=completed` + `push_verified=git_push_exit_0` fermati. Output massimo 6 righe.