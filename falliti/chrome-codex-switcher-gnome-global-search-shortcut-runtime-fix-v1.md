PROMPT_ID=917403
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Indaga e risolvi il bug reale per cui la shortcut globale GNOME della dashboard Context Search non reagisce, anche se lo schema GSettings bundled esiste e contiene ['<Alt><Shift>s']. Porta il flusso fino a un test end-to-end reale su Fedora/GNOME Wayland; non fermarti a una verifica statica.

# Evidenza già verificata
- Repo target: ~/projects/chrome-codex-switcher / gernalix/chrome-codex-switcher.
- Il companion GNOME installato è chrome-codex-switcher@gernalix.github.com.
- L'installer termina con: GNOME global search shortcut schema: OK (['<Alt><Shift>s']).
- Il companion risulta enabled.
- Verifica manuale bundled:
  GSETTINGS_SCHEMA_DIR="$HOME/.local/share/gnome-shell/extensions/chrome-codex-switcher@gernalix.github.com/schemas" gsettings get org.gnome.shell.extensions.chrome-codex-switcher open-search-dashboard
  => ['<Alt><Shift>s']
- Nonostante questo, Alt+Shift+S premuto da Terminale non apre né focalizza la dashboard.
- Main contiene già: GSettings schema bundled, Main.wm.addKeybinding, launcher /ui/search e fallback Chrome-side. Non riscoprire queste parti da zero.

# Esecuzione
1. Prima di qualunque lavoro esegui roadmap_start.py per 917403 e lavora SOLO nel worktree_path restituito.
2. Riproduci il failure sul runtime Fedora reale e raccogli il minimo necessario:
   - stato/versione reale dell'estensione caricata;
   - errori GNOME Shell pertinenti nel journal;
   - registrazione/lettura effettiva del keybinding;
   - eventuale conflitto di Alt+Shift+S con GNOME, app o altra estensione;
   - verifica che callback e launcher siano raggiungibili separatamente.
   Non fare audit generale del repo o del desktop.
3. Correggi la causa nel repo. Se Main.wm.addKeybinding non è affidabile o non è realmente attivo in questo setup, è autorizzato sostituirlo con un meccanismo GNOME-native più robusto, preferibilmente un custom keybinding persistente gestito da org.gnome.settings-daemon.plugins.media-keys e installato/disinstallato idempotentemente da install.sh/uninstall.sh. Mantieni Alt+Shift+S se non c'è un conflitto reale.
4. Il comando globale deve aprire/focalizzare Google Chrome sulla dashboard http://127.0.0.1:43817/ui/search anche quando il focus iniziale è su Terminale o altra app. Evita simulazione fragile di tasti verso Chrome.
5. Aggiungi test mirati per configurazione/installazione/uninstall e per il launcher; aggiorna documentazione solo quanto necessario.
6. Installa/reinstalla il fix sul Fedora reale, reload/restart solo dei componenti in-scope e riprova il comportamento reale.
7. Dopo ogni failure, correggi sulla nuova evidenza e rilancia solo il leaf gate fallito. Niente retry identici, refactor o cleanup fuori scope.
8. Finalizza con roadmap_finish.py solo dopo PASS reale; altrimenti usa BLOCKED/FAIL con blocker concreto.

# Acceptance
PASS solo se TUTTI:
- il meccanismo globale attivo è dimostrato nel runtime GNOME corrente, non solo presente nei file;
- nessun errore dell'estensione/keybinding rilevante resta nel journal dopo reload;
- Alt+Shift+S funziona con focus iniziale fuori da Chrome e apre/focalizza Context Search in Google Chrome;
- la dashboard caricata risponde e il campo ricerca riceve focus;
- install.sh è idempotente e configura il binding corretto; uninstall.sh rimuove ciò che il fix introduce;
- i test mirati e la CI pertinente sono PASS;
- non serve alcun passaggio manuale ricorrente dopo login/reboot oltre all'installazione iniziale.

# Non-goal
Non modificare pairing Chrome↔Codex, note persistenti, Workflowy, roadmap UI o altre shortcut salvo quanto strettamente necessario per eliminare un conflitto provato.

# Report
Massimo 8 righe. Prima riga PROMPT_ID=917403; seconda RESULT=PASS|BLOCKED|FAIL. Poi: ROOT_CAUSE, MECHANISM, GLOBAL_SHORTCUT_TEST, DASHBOARD_TEST, TESTS_CI, COMMIT, BLOCKER.
