PROMPT_ID=519564 | project=chrome-codex-switcher | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Porta a PASS sul Fedora reale il sistema già implementato in gernalix/chrome-codex-switcher: pairing persistente Chrome tab ↔ Codex Desktop thread, switch bidirezionale e note flottanti, incluso overlay Codex opzionale.

# Starting point
- Repo remoto: https://github.com/gernalix/chrome-codex-switcher
- Implementazione ChatGPT già su main: commit 389dfa16b4e348686e0fef94f1ecbd4b3e69a6c2.
- Non rifare discovery generale né riscrivere l'architettura.
- Il protocol handler Fedora è già verificato: x-scheme-handler/codex -> chatgpt.desktop e `gio open 'codex://threads/<id>'` apre correttamente la chat specifica.
- Core previsto: Chrome MV3 extension + daemon Python/systemd + SQLite + wl-paste watcher + loopback 127.0.0.1; niente automazione finestre Wayland nel percorso critico.
- Il repo contiene anche un prototipo GNOME Shell overlay in `contrib/`.

# Scope
1. Esegui `roadmap_start.py` per 519564. Porta/aggiorna il checkout locale `~/projects/chrome-codex-switcher` al main remoto in modo sicuro.
2. Esegui solo i gate locali già definiti dal repo: unittest Python, py_compile, JSON manifest, shell syntax. Riusa CI remota se già PASS; non duplicare test equivalenti.
3. Installa il servizio con `install.sh`; verifica `systemctl --user`, `context-twin status`, persistenza SQLite e watcher `wl-paste`. Se manca solo `wl-clipboard` e serve sudo, fermati esclusivamente per quella singola azione utente esplicita.
4. Carica/verifica l'estensione nella Chrome reale usata dall'utente. Controlla che l'ID effettivo corrisponda all'origin accettata dal daemon; se no, correggi il minimo necessario. Verifica che Chrome/Flatpak raggiunga 127.0.0.1:43817.
5. Esegui un solo smoke end-to-end con una coppia reale:
   - Chrome Y: crea/modifica nota; arma Link Twin.
   - Codex X: usa Copy chat deep link; verifica pairing persistente.
   - Chrome Y -> Codex X: shortcut/pulsante apre esattamente X.
   - Codex X -> Chrome Y: Copy chat deep link fa focus sulla finestra e sulla tab Y esatta.
   - chiudi/riapri la tab Y e verifica che il mapping persistente la ritrovi o la riapra.
   - riavvia il daemon e verifica che il ritorno Codex -> Chrome continui a funzionare.
6. Verifica nota Chrome: autosave, drag, resize, collapse/hide e side panel search.
7. Installa e prova il prototipo GNOME overlay solo dopo il core PASS. Su GNOME 50/Wayland deve comparire esclusivamente quando Codex/ChatGPT Desktop è focused e mostrare titolo+nota della coppia attiva. Se API GNOME/runtime differiscono, applica il minimo fix; non far dipendere il core da questo overlay.
8. Se trovi bug in-scope, correggi solo quelli, aggiungi/aggiorna test mirati, commit/push. Nessun refactor/cleanup fuori scope.
9. Aggiorna README solo se i comandi reali o le shortcut finali differiscono dall'attuale documentazione.

# Constraints
- Preserva il design senza xdotool/ydotool/coordinate o window scraping Wayland.
- Non introdurre server/cloud/database aggiuntivi.
- Non fare polling o retry identici senza nuova evidenza.
- Non investigare problemi collaterali non bloccanti.
- Dopo PASS termina subito.
- Se un passaggio GUI non è automatizzabile in sicurezza, chiedi/riporta una sola azione manuale precisa, non una procedura generica.

# Acceptance
PASS solo se: servizio user attivo; Chrome extension operativa; pairing persistente; switch Chrome→Codex apre il thread esatto; switch Codex→Chrome porta in focus la tab esatta; note Chrome persistono e sono usabili; restart daemon non rompe il flusso; overlay GNOME è verificato oppure, se il solo overlay resta incompatibile, il core è PASS e l'overlay è riportato separatamente come OPTIONAL_BLOCKED senza degradare il risultato core.

# Output
Prima riga `PROMPT_ID=519564`. Poi massimo 10 righe: RESULT, COMMIT, SERVICE, EXTENSION, PAIRING, CHROME_TO_CODEX, CODEX_TO_CHROME, NOTES, GNOME_OVERLAY, TESTS, BLOCKER.
