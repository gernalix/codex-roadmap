PROMPT_ID=604812
PARENT_PROMPT_ID=917403
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Indaga e risolvi il bug reale per cui Alt+Shift+S non funziona come shortcut globale GNOME per Context Search. Il browser autorevole è ora SOLO Google Chrome RPM; Chrome Flatpak è stato disinstallato. L'estensione Chrome dello switcher è già installata nel Chrome RPM e funziona normalmente: il solo comportamento noto non funzionante è la shortcut globale.

# Evidenza già verificata
- Fedora/GNOME Wayland.
- Repo target: ~/projects/chrome-codex-switcher / gernalix/chrome-codex-switcher.
- Chrome Flatpak: disinstallato. Non reinstallarlo e non investigare path/ID/runtime Flatpak.
- Google Chrome RPM: installato e operativo.
- Estensione unpacked Chrome ↔ Codex Switcher: installata nel Chrome RPM e funzionante; non trattarla come sospetta principale.
- Companion GNOME: chrome-codex-switcher@gernalix.github.com, risulta enabled.
- Installer: GNOME global search shortcut schema: OK (['<Alt><Shift>s']).
- Verifica bundled GSettings già PASS:
  GSETTINGS_SCHEMA_DIR="$HOME/.local/share/gnome-shell/extensions/chrome-codex-switcher@gernalix.github.com/schemas" gsettings get org.gnome.shell.extensions.chrome-codex-switcher open-search-dashboard
  => ['<Alt><Shift>s']
- Alt+Shift+S premuto da Terminale non produce alcun effetto.
- Main contiene già schema bundled, Main.wm.addKeybinding e dashboard /ui/search. Non riscoprire queste parti da zero.

# Esecuzione
1. Prima di qualunque lavoro esegui roadmap_start.py per 604812 e usa SOLO il worktree_path restituito.
2. Riproduci il failure sul Fedora reale concentrandoti sul percorso:
   GNOME Shell -> keybinding globale -> callback/launcher -> Chrome RPM -> http://127.0.0.1:43817/ui/search.
3. Raccogli solo l'evidenza necessaria:
   - versione/stato REALI del companion GNOME caricato e relativi errori journal;
   - se il keybinding è realmente registrato nel runtime GNOME Shell, non solo presente in GSettings;
   - conflitti reali di Alt+Shift+S con GNOME/altre estensioni;
   - prova separata che il launcher possa aprire l'URL della dashboard nel Chrome RPM;
   - smoke rapido della dashboard e dell'estensione Chrome già funzionante, senza audit o reinstallazioni inutili.
4. NON indagare Chrome Flatpak, Native Messaging/transport Flatpak, sandbox Flatpak o migrazioni browser: sono fuori scope.
5. Correggi la causa nel repo. Se Main.wm.addKeybinding non è affidabile/attivo su questo GNOME, sostituiscilo con un meccanismo GNOME-native robusto e persistente, preferibilmente un custom keybinding di org.gnome.settings-daemon.plugins.media-keys gestito idempotentemente da install.sh/uninstall.sh.
6. Il target del launcher deve essere Chrome RPM. Risolvi in modo robusto il desktop entry/eseguibile reale del pacchetto RPM presente sul sistema; non usare comandi Flatpak. Mantieni Alt+Shift+S salvo conflitto reale dimostrato.
7. Installa/reinstalla SOLO i componenti in-scope del fix, reload/restart quanto necessario e prova davvero Alt+Shift+S con Terminale o altra app non-Chrome in focus.
8. Aggiungi test mirati per installazione/configurazione/uninstall/launcher. Dopo un failure correggi sulla nuova evidenza e rilancia solo il leaf gate fallito. Niente retry identici, audit repo-wide, refactor o cleanup.
9. Finalizza con roadmap_finish.py solo dopo PASS reale; altrimenti BLOCKED/FAIL con blocker concreto.

# Acceptance
PASS solo se TUTTI:
- il meccanismo globale attivo è dimostrato nel runtime GNOME corrente;
- nessun errore pertinente del companion/keybinding resta nel journal dopo reload;
- con focus iniziale fuori da Chrome, Alt+Shift+S apre o focalizza Google Chrome RPM sulla dashboard Context Search;
- la dashboard risponde e il campo ricerca riceve focus;
- l'estensione switcher nel Chrome RPM continua a funzionare;
- install.sh è idempotente e configura il binding corretto; uninstall.sh rimuove ciò che il fix introduce;
- nessuna dipendenza da Chrome Flatpak;
- test mirati e CI pertinente PASS;
- dopo login/reboot non serve alcuna azione manuale ricorrente oltre all'installazione iniziale.

# Non-goal
Non modificare pairing Chrome↔Codex, note persistenti, Workflowy o altre feature dello switcher. Non reinstallare Chrome Flatpak. Non diagnosticare l'estensione Chrome oltre allo smoke minimo necessario a evitare regressioni.

# Report
Massimo 8 righe. Prima PROMPT_ID=604812; seconda RESULT=PASS|BLOCKED|FAIL. Poi: ROOT_CAUSE, MECHANISM, RPM_LAUNCHER, GLOBAL_SHORTCUT_TEST, TESTS_CI, COMMIT, BLOCKER.
