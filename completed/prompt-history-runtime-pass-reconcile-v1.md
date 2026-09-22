PROMPT_ID=413647 | PARENT_PROMPT_ID=925731 | project_id=92
MODEL=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
REPO=gernalix/prompt-history

# Goal
Chiudi SOLO il residuo canonico di 925731. Il parent deve restare storicamente BLOCKED: non tentare più reactivation/terminalizzazione di 925731 e non rifare implementazione/backfill già completati.

# Evidenza già verificata
- 925731 è canonically BLOCKED senza fix/replacement.
- Il fix-packet più recente dice che il single writer mantiene 925731 terminale blocked e rifiuta ulteriori reactivation/terminalizzazioni.
- Una terminal_request precedente con note `verified-runtime-pass` è stata rifiutata dal writer proprio perché il parent era già terminale.
- gernalix/prompt-history PR #1 `[single-writer] 925731` è MERGED in main; merge commit `ee68948617e4c66f17b9eddc737889fdd0e27211`.
- prompt-history/main contiene quindi il lavoro prodotto da task/925731.

# Esecuzione minima
1. Claim SOLO 413647. Leggi il record canonico 925731 e NON riavviare 925731.
2. Verifica una sola volta che prompt-history/main contenga `ee68948617e4c66f17b9eddc737889fdd0e27211` o un successore. Nessun audit history/PR.
3. Sul Fedora reale fai SOLO readback non distruttivo dello stato già creato da 925731:
   - `~/.local/share/prompt-history/prompt_history.sqlite` esiste ed è leggibile;
   - `prompt-history-sync.timer` è enabled/active o equivalente già installato;
   - una query/count minima conferma dati importati da roadmap e codex-usage;
   - esegui al massimo UNA `sync` e poi UNA seconda sync invariata solo per confermare idempotenza/no duplicati;
   - un solo smoke `similar` o `model-stats` basta per provare che l'analytics runtime risponde.
4. Non leggere/stampare contenuti di chat, note, transcript o URL privati; riporta solo count/stato/hash se necessari.
5. Se i readback sono già PASS, NON modificare codice e NON rifare backfill. Se uno specifico gate runtime manca, correggi solo quel gate e ritestalo una volta.
6. Finalizza 413647 PASS e STOP. Il parent 925731 resta BLOCKED storico ma viene risolto dalla relazione fix verso questo prompt.

# Acceptance
PASS solo se PR #1 resta merged, DB/runtime/sync risultano realmente operativi, la seconda sync è idempotente, nessun dato privato viene pubblicato e 925731 non viene mutato di nuovo.

# Report
Massimo 7 righe: RESULT, PARENT_925731, MAIN_REVISION, DB, SYNC, ANALYTICS, BLOCKER.