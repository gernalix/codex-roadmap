PROMPT_ID=635814 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal
Rendi `adb-device-keeper.service` riproducibile e versionato partendo ESCLUSIVAMENTE dal runtime Fedora attuale già funzionante: conserva la versione live, porta script/unit/config schema in una sorgente Git canonica, aggiungi i test deterministici minimi che avrebbero impedito la regressione cross-device vista in `742615`, elimina il coupling WhatsApp estraneo all'ADB keeper, quindi ridistribuisci e prova una sola riconnessione reale Pixel via Tailscale.

# Starting point autoritativo
- host/runtime: Fedora locale;
- unit live: `~/.config/systemd/user/adb-device-keeper.service`;
- script live: `~/.local/bin/adb-device-keeper`;
- config live: `~/.config/adb-device-keeper/config`;
- state live: `~/.local/state/adb-device-keeper/`;
- `742615` ha già dimostrato che il Pixel 8a si riconnette automaticamente via Tailscale quando la LAN pubblica non espone la porta ADB;
- il primo tentativo di fix di `742615` accettava qualunque endpoint Tailscale come candidato per qualunque device e il controllo TCL ha scollegato il transport del Pixel; il secondo fix ha ristretto il candidato all'IP Tailscale del device corretto;
- la unit live punta a `file:///home/daniele/MegaVault/ai/global/ADB_DEVICE_KEEPER.md`, path risultato mancante durante `742615`;
- il codice live contiene ancora logica WhatsApp disabilitata: questa responsabilità non appartiene al keeper ADB;
- non esiste oggi una sorgente GitHub indicizzata per `adb-device-keeper`: NON partire da vecchio `adb-wifi-autoconnect`.

# Scope stretto
1. Prima di modificare altro, salva una copia timestamped locale dei tre file live pertinenti: script, unit, config. Non copiare secret in Git.
2. Verifica con UNA query MegaVault mirata se esiste già un owner Git canonico per `adb-device-keeper`. Se esiste, usa quello. Se non esiste, crea un piccolo repo dedicato `~/projects/adb-device-keeper` + remoto `gernalix/adb-device-keeper`; non infilare il servizio in repo non correlati.
3. Porta nel repo solo:
   - script keeper;
   - unit systemd user come template/versionata;
   - config example senza serial/IP/secret reali;
   - install/deploy minimale e idempotente;
   - README operativo breve;
   - test mirati.
4. Mantieni il comportamento live già verificato LAN -> Tailscale fallback. Non ridisegnare il protocollo.
5. Rimuovi completamente dallo script versionato costanti/funzioni/chiamate WhatsApp ormai disabilitate; niente feature nuove.
6. Correggi `Documentation=` della unit verso una fonte realmente esistente e stabile.

# Test deterministici obbligatori
Copri almeno:
- syntax `bash -n`;
- endpoint Tailscale `100.64.0.0/10` valido e porta valida;
- Pixel Tailscale transport NON è candidato per TCL e viceversa;
- mapping device -> peer Tailscale usa il peer corretto;
- fallback conserva la porta ADB scoperta/cached ma sostituisce solo l'host con quello Tailscale del device;
- config example non contiene serial/IP/secret reali;
- nessun riferimento WhatsApp rimane nel keeper;
- unit installata punta all'eseguibile canonico ed ha `Restart=on-failure` con backoff esistente.

Preferisci test puri/mocked; nessun device reale in CI. Se il repo è pubblico, aggiungi una CI minima per questi test. Non installare framework di test nuovo se stdlib/shell bastano.

# Deploy/runtime finale — una sola volta
1. Solo dopo PASS dei test mirati: deploy dal repo canonico ai path live e `systemctl --user daemon-reload` + restart/enable della sola unit.
2. Verifica `is-enabled`, `is-active`, `systemctl --user show` per `Restart/RestartUSec/ExecStart` e journal recente della sola unit.
3. Se il Pixel è già `device`, esegui UNA prova reale: `adb disconnect <transport Pixel>`; attendi al massimo un ciclo keeper + margine con timeout esplicito; verifica riconnessione automatica e identità `model:Pixel_8a`.
4. Non testare un `adb connect` LAN noto irraggiungibile senza `timeout`. Nessun retry identico.
5. Commit/push sorgente canonica e aggiorna MegaVault solo con owner/path/comandi operativi essenziali.

# Stop conditions
- Se worktree destinazione dirty con modifiche non pertinenti: `BLOCKED`, stop.
- Se serve pairing manuale nuovo: `BLOCKED`, indica solo il singolo passo richiesto; non aprire UI a caso.
- Se i test deterministici PASS e la riconnessione reale PASS: stop immediato, niente audit aggiuntivi.

# Acceptance
PASS solo se il servizio live continua a riconnettere il Pixel, la sorgente esatta è ora versionata/riproducibile, la regressione cross-device è coperta da test, il coupling WhatsApp è rimosso, `Documentation=` non è stale e il remoto contiene il commit finale.

# Non-goal
Niente PersonalHub, APK, WhatsApp settings, ExpressVPN, rete globale/firewall, refactor generali Fedora, audit di altri repo o test TCL reali.

# Stop roadmap
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 635814 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 635814`

Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 7 righe: `OWNER`, `COMMIT`, `TEST`, `DEPLOY`, `SYSTEMD`, `PIXEL_RECONNECT`, `BLOCKER`.
