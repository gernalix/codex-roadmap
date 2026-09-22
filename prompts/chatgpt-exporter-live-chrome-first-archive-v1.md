PROMPT_ID=736284 | project_id=92 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
REPO=gernalix/prompt-history
WORKDIR=/home/daniele/projects/prompt-history
PARENT_PROMPT_ID=571364

# Goal
Usa il Chrome reale già aperto sul Fedora e porta ChatGPTExporter dal dashboard bloccato al primo archivio locale realmente creato e ingerito da prompt-history. Non limitarti a diagnosticare o a dire all'utente cosa cliccare: controlla direttamente Chrome/UI/devtools con gli strumenti disponibili, prova il flusso reale e correggi solo ciò che blocca.

# Stato già verificato
- 571364 ha già installato/buildato gli upstream e attivato prompt-history runtime/timer.
- ChatGPTExporter pinned: siraht/ChatGPTExporter@c5618b3cc06eeb5b273d3727fe8729071441f291 (0.1.6), build locale sotto ~/.local/share/prompt-history/upstream/ChatGPTExporter/dist/extension.
- L'estensione unpacked è già caricata in Chrome e il dashboard si apre.
- Problema live osservato: nel dashboard tutti gli step restano bloccati; Open ChatGPT apre chatgpt.com, ma il normale ciclo Open ChatGPT -> reload tab -> Find tab non sblocca i workspace.
- Non rifare il deploy Session Bandit né audit generali di prompt-history.

# Esecuzione minima
1. Claim:
   python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 736284
   Se il claim non diventa running, stop.
2. Riusa la stessa istanza/profilo Chrome reale già aperta e autenticata. Identifica una sola volta binary/profile e l'ID reale di ChatGPTExporter dal dashboard corrente. NON creare profili nuovi, NON fare logout/login, NON cancellare cookie/storage/sessioni.
3. Controlla direttamente Chrome:
   - verifica che esista una tab https://chatgpt.com/ autenticata;
   - ricaricala una volta;
   - torna al dashboard ChatGPTExporter;
   - prova realmente Find tab e osserva il testo/stato risultante.
   Non chiedere all'utente di fare questi click se puoi farli tu.
4. Se Find tab non funziona, diagnostica SOLO il bridge dell'estensione:
   - chrome://extensions -> ChatGPTExporter -> stato/permessi/site access/service worker;
   - errori del service worker e della dashboard;
   - presenza/iniezione di page-bridge.js e content-relay.js sulla tab chatgpt.com;
   - messaggio CHATGPT_EXPORTER_FIND_TAB e successivo discoverWorkspaces;
   - eventuali errori CHATGPT_TAB_UNREACHABLE, auth, endpoint/API shape o service-worker stale.
   Usa DevTools/console/log mirati; niente audit di tutte le estensioni o di Chrome.
5. Applica il fix minimo dimostrato dalla causa:
   - se basta Reload dell'estensione / refresh ordinato della tab / site access corretto, fallo e ritesta una volta;
   - se il build locale è stale/corrotto, rebuilda SOLO il checkout pinned già presente e ricarica l'estensione;
   - se esiste un bug reale nel codice pinned dovuto al comportamento attuale di ChatGPT, modifica SOLO il checkout upstream locale necessario, rebuilda e ritesta. Non fare upgrade upstream generale e non creare fork/PR.
   - modifica prompt-history solo se serve rendere persistente/ripetibile un fix di integrazione locale; in tal caso cambia il minimo necessario direttamente nel repo canonico secondo le regole correnti, senza PR.
6. Quando Find tab funziona:
   - seleziona esplicitamente tutti i workspace personali/accessibili pertinenti;
   - Verify selected workspaces;
   - scegli come parent directory /home/daniele/Documents/ChatGPT;
   - lascia selezionati Main history, Archived, Projects, Shared, Account artifacts, Assets;
   - Build inventory;
   - controlla solo conteggi aggregati e termination evidence, poi Confirm inventory;
   - Start/resume capture.
   Non stampare contenuti di chat, cookie, token, identificatori account raw o dati privati nei log/report.
7. Porta la capture fino a stato terminale accettabile:
   - preferito: complete;
   - accettabile: conversations complete / assets partial solo se le eccezioni asset sono esplicite e il report di validazione è coerente;
   - incomplete = NON PASS.
   Se l'export è lungo, continua/monitora il processo e usa il resume; non dichiarare PASS solo perché è partito.
8. Verifica che esista almeno un archivio:
   /home/daniele/Documents/ChatGPT/ChatGPTExport-*/reports/validation.md
   e che contenga conversation artifacts normalizzati.
9. Esegui una sola sync manuale:
   systemctl --user start prompt-history-sync.service
   poi verifica status SUCCESS e timer enabled+active. Conferma via count/provenance che prompt-history abbia ingerito record ChatGPTExporter dall'archivio, senza duplicare executions Codex.
10. Se un blocco richiede davvero password/2FA/consenso OS non automatizzabile, BLOCKED con UNA sola azione manuale precisa. Non usare l'utente come sostituto per click ordinari che puoi fare tu.
11. Nessun refactor, cleanup, reinstallazione Chrome/ChatGPT Desktop, modifica di altre estensioni o esplorazione repo-wide. Dopo acceptance PASS finalizza e STOP.

# Acceptance
PASS solo se:
- Codex ha provato direttamente il flusso nel Chrome reale;
- la causa del blocco iniziale è identificata con evidenza concreta;
- Find tab scopre almeno un workspace accessibile e la UI procede oltre lo step 1;
- inventory completato e confermato;
- capture terminale accettabile e validation.md presente;
- archivio creato sotto /home/daniele/Documents/ChatGPT/ChatGPTExport-*;
- prompt-history sync SUCCESS e ingest ChatGPTExporter verificato;
- Flatpak/RPM/profilo Chrome, cookie e account non sono stati distruttivamente alterati.

# Stop
Dopo PASS:
python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 736284 --result PASS --confirm-executed

Per BLOCKED/FAIL usa lo stesso finalizzatore con l'esito reale.

Output massimo 8 righe:
RESULT, CHROME_PROFILE, EXTENSION_STATE, ROOT_CAUSE, WORKSPACES, ARCHIVE, PROMPT_HISTORY, NEXT_ACTION.