PROMPT_ID=318764 | PARENT_PROMPT_ID=604812 | project_id=96 | MODEL=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Chiudi SOLO il blocker residuo di 604812. Non rieseguire la diagnosi GNOME, non usare input injector privilegiati e non rifare il fix: PR #22 ha già sostituito il keybinding GNOME Shell con un custom keybinding GNOME Settings Daemon per Google Chrome RPM.

# Evidenza già verificata
- 604812 è canonically BLOCKED; fix-packet: `No privileged Wayland input injector/native UI control to prove Alt+Shift+S.`
- work-state 604812: commit `beca7f936357fbb1550dfe9201acb5a742cf80d0`.
- PR #22 `Fix GNOME Context Search shortcut` è merged; merge commit `53c93f1ba1391605c1c89653e35f4c1bc21a0312`.
- Il fix installa idempotentemente un custom keybinding `org.gnome.settings-daemon.plugins.media-keys` per `<Alt><Shift>s` che lancia Google Chrome RPM su `http://127.0.0.1:43817/ui/search`.
- 741928 è un follow-up più ampio sul runtime CCS; NON duplicarne i test o le altre feature.

# Esecuzione minima
1. Avvia SOLO 318764 con `roadmap_start.py`; non riavviare 604812.
2. Leggi SOLO il record 604812, PR #22/merge e i file direttamente responsabili della shortcut (`contrib/configure-global-search-shortcut.sh`, install/uninstall contract e test mirati).
3. Sul Fedora reale verifica senza sintetizzare tasti:
   - readback GSettings del custom-keybinding: path presente, binding esatto `<Alt><Shift>s`, command punta a Google Chrome RPM + `/ui/search`;
   - nessun conflitto duplicato per Alt+Shift+S nei custom keybindings rilevanti;
   - esegui UNA volta lo stesso command registrato nel binding da una sessione grafica normale e dimostra apertura/focus della dashboard + campo ricerca disponibile;
   - esegui solo i test mirati già esistenti per install/config/uninstall; niente suite repo-wide se questi passano.
4. La pressione fisica/sintetica Alt+Shift+S NON è gate automatico: su Wayland senza injector sicuro, la prova deterministica dei due lati (binding registrato + command/launcher funzionante) è sufficiente. Non installare xdotool/ydotool/uinput né chiedere click manuali.
5. Se i due lati PASS e PR #22 resta merged, NON modificare codice. Tramite single writer registra la recovery canonica minima di 604812 preservando la sua execution storica BLOCKED e collegandola a 318764 PASS.
6. Modifica CCS SOLO se uno dei due lati deterministici fallisce realmente; in quel caso fix minimo + solo test mirato, senza toccare pairing/note/overlay/741928.
7. Verifica idempotenza del reconcile, finalizza 318764 e STOP.

# Acceptance
PASS solo se binding GSettings e launcher/dashboard sono entrambi dimostrati sul runtime reale, PR #22 resta merged, nessun input injector/manual gate è richiesto, 604812 non resta blocker operativo irrisolto e nessun lavoro di 741928 viene duplicato.

# Report
Massimo 7 righe: RESULT, PARENT_604812, BINDING, LAUNCHER, PR22, MUTATION, BLOCKER.
