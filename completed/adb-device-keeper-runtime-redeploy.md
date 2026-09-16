PROMPT_ID=746323 | project_id=15 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Distribuisci sul Fedora reale il fix post-analisi di `635814` e verifica una sola riconnessione reale del Pixel 8a usando gli helper già versionati, senza rieseguire controlli equivalenti a mano.

# Starting point autoritativo
- repo locale: `/home/daniele/projects/adb-device-keeper`, branch `main`;
- remote canonico: `gernalix/adb-device-keeper`;
- commit remoto minimo: `912a436174b9f655607cdd4f9e3ad0a4d650d14a`;
- GitHub Actions run `35110215967` su quel commit è **PASS**;
- il fix rende `scripts/deploy.sh` fail-closed su checkout dirty, installa la sorgente canonica, esegue un `systemctl --user restart` esplicito anche se il servizio era già attivo e poi lancia `scripts/runtime-check.sh`;
- `runtime-check.sh` verifica drift binario/unit, config leggibile, service enabled/active, ExecStart/restart policy; stampa il journal bounded solo su FAIL;
- `runtime-check.sh --reconnect-model Pixel_8a` fa un solo disconnect controllato e riporta il path reale `lan|tailscale|mdns|other`;
- `742615` ha già provato il fallback Tailscale quando necessario: NON manipolare rete/firewall per forzarlo.

Prompt autosufficiente: niente README/roadmap/MegaVault/MEMORY, niente audit repo-wide e niente suite locale perché la CI del commit richiesto è già verde.

# Esecuzione minima
1. In UN solo blocco: verifica checkout pulito + branch, fai `timeout 20s git fetch origin main`, `git merge --ff-only origin/main`, salva `RUN_HEAD`, verifica `RUN_HEAD == origin/main` e che `912a436174b9f655607cdd4f9e3ad0a4d650d14a` sia antenato. Se dirty/diverge/fetch fallisce: `BLOCKED`, stop. Nessun stash/rebase/retry.
2. Esegui UNA volta `bash scripts/deploy.sh`. Il suo `RUNTIME=PASS reconnect=not-requested` è sufficiente per deploy/systemd/drift: NON ripetere `systemctl`, `cmp`, journal o controlli equivalenti.
3. Solo se deploy PASS, esegui UNA volta `bash scripts/runtime-check.sh --reconnect-model Pixel_8a --timeout 90`.
4. PASS se il Pixel torna `device` entro il timeout. Riporta esattamente `reconnect_path` restituito; non chiamarlo Tailscale se il valore è `lan` o `mdns`.
5. Se uno degli helper fallisce, usa solo il suo output/journal già bounded e termina `BLOCKED` o `FAIL`; niente debugging esplorativo o retry identici.

# Acceptance
PASS solo se `RUN_HEAD` è sincronizzato a `origin/main` e include il commit minimo, `scripts/deploy.sh` termina con `DEPLOY=PASS` + `RUNTIME=PASS`, e l'unico smoke reconnect termina con `RUNTIME=PASS model=Pixel_8a` riportando il path reale.

# Non-goal
Niente modifiche codice, test locali, CI rerun, MegaVault, PersonalHub, TCL reale, pairing nuovo, firewall/rete globale, journal aggiuntivo, altri repo o audit post-PASS.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 746323 --confirm-executed`

Stop immediato dopo finalizzazione. Output massimo 5 righe: `RESULT`, `COMMIT`, `DEPLOY`, `PIXEL_RECONNECT`, `BLOCKER`.
