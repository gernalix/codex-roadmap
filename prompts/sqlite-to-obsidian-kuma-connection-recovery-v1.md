PROMPT_ID=714263
PARENT_PROMPT_ID=893025
REPO=gernalix/fedora-system-monitor
MODEL=GPT-5.6 Luna
REASONING=low
MEGAVAULT=FAST

# Goal
Chiudi SOLO il residuo Kuma di 893025. Non ricreare `sqlite-to-obsidian`, non rifare sync/vault/test/systemd già completati e non creare provisioning Kuma proprietario.

# Evidenza già verificata
- 893025 ha ultimo esito BLOCKED e fix-packet: provisioning Kuma canonico fallito con `ConnectionError`; nessun monitor/token alternativo creato e roadmap non finalizzata.
- `gernalix/sqlite-to-obsidian` esiste, è privato, `main` contiene già l'implementazione (`56b70ef6e861b93e938e90288c399b987dfeddfe`, `04768257b7e04a746233031ba5e46f6b4b1a91ee`) e non ha PR aperte.
- `fedora-system-monitor/main` contiene il control plane Kuma canonico e `src/fedora_system_monitor/capsules/kuma_admin`; main corrente include anche i merge successivi del task 620949.
- Nessun fix/replacement pending o running risulta collegato a 893025.

# Esecuzione minima
1. Claim SOLO 714263 con `roadmap_start.py`; non riavviare 893025.
2. Leggi SOLO il fix-packet di 893025, `src/fedora_system_monitor/capsules/kuma_admin/__init__.py`, `tests/test_kuma_admin.py` e il comando CLI direttamente pertinente. Niente audit repo-wide.
3. Prima di modificare codice, esegui UNA diagnosi bounded del percorso canonico: helper Oracle disponibile -> container Kuma running -> endpoint raggiungibile -> Socket.IO/login autenticato. Riporta solo stato/classe errore; non stampare token, cookie, JWT, URL push completi o session data.
4. Se la connettività ora è sana, esegui UNA sola riconciliazione/provisioning per il job `sqlite-to-obsidian` come timer/oneshot con successo+freschezza, poi readback: monitor unico, attivo, target corretto e heartbeat/freshness verificabile. Nessuna modifica codice.
5. Se fallisce ancora, identifica il PRIMO layer che fallisce. Modifica codice SOLO se il failure è riproducibile e causato dal client/provisioner; patch minima + test mirato `test_kuma_admin` pertinente. Se è rete/Oracle/Kuma/sessione esterna, BLOCKED con una riga precisa e nessun retry identico.
6. Non creare credenziali alternative, non modificare direttamente kuma.db e non leggere/pubblicare segreti.
7. Quando readback PASS, registra la recovery di 893025 tramite il normale finalizer del nuovo prompt, preservando il suo esito BLOCKED storico; finalizza 714263 e STOP.

# Acceptance
PASS solo se il monitor centrale `sqlite-to-obsidian` esiste una sola volta, usa la semantica timer/oneshot successo+freschezza, il readback live è PASS, nessun secret è esposto e nessun lavoro già completato da 893025 viene ripetuto.

# Report
Massimo 7 righe: RESULT, PARENT_893025, CONNECTION_LAYER, MONITOR, READBACK, TESTS, BLOCKER.