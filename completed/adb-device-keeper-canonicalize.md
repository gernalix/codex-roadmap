PROMPT_ID=635814 | project_id=15 | model=GPT-5.5 | reasoning=low | MegaVault=FAST

# Goal
Distribuisci sul Fedora reale la sorgente canonica già pronta di `adb-device-keeper`, verifica la unit user-systemd e prova UNA sola riconnessione reale del Pixel 8a via Tailscale dopo disconnect controllato.

# Starting point autoritativo
- repo canonico già esistente: `/home/daniele/projects/adb-device-keeper`, remote `gernalix/adb-device-keeper`, branch `main`;
- commit minimo richiesto: `170df291e930adb66da485bcdc18781519f99be1` o successivo;
- GitHub Actions run `35086497954` sul commit minimo è **PASS**: NON rieseguire test deterministici localmente;
- sorgente, unit, config example, deploy helper e CI sono già versionati;
- la logica WhatsApp estranea è già rimossa;
- i test CI coprono Tailscale `100.64.0.0/10`, mapping device→peer, preservazione porta ADB, rigetto cross-device, config sanificata e unit systemd;
- runtime Fedora atteso:
  - script: `~/.local/bin/adb-device-keeper`;
  - unit: `~/.config/systemd/user/adb-device-keeper.service`;
  - config privata: `~/.config/codex/secrets/adb-device-keeper/config`;
  - state: `~/.local/state/adb-device-keeper/`;
- MegaVault ha già registrato il repository: NON aggiornarlo in questo task;
- `742615` ha già dimostrato che il Pixel può riconnettersi via Tailscale quando la LAN pubblica non espone la porta ADB.

Prompt autosufficiente: non leggere README/roadmap/spiegazioni/MEMORY/MegaVault, non fare audit repo-wide e non modificare codice salvo blocker concreto che renda impossibile il deploy verificato.

# Esecuzione minima
1. Una fotografia Git del solo checkout `adb-device-keeper`. Se pulito: UNA sync `timeout 20s git fetch origin main && git merge --ff-only origin/main`; se dirty non pertinente, fetch/merge fallisce o diverge: `BLOCKED`, stop. Nessun stash/rebase/retry.
2. Verifica soltanto che `170df291e930adb66da485bcdc18781519f99be1` sia antenato di HEAD. La CI è già PASS: nessuna suite locale duplicata.
3. Verifica senza stampare valori sensibili che il file config atteso esista e sia leggibile. Non mostrare il contenuto.
4. Esegui UNA volta `bash scripts/deploy.sh` dal checkout pulito.
5. Verifica in un solo blocco bounded: `is-enabled`, `is-active` e `systemctl --user show` limitato a `ExecStart`, `Restart`, `RestartUSec`; poi journal recente della sola unit con massimo 50 righe. Nessun dump globale.
6. Se il Pixel 8a è già `device`, individua il suo transport dall'output `adb devices -l`, esegui UNA volta `adb disconnect <transport Pixel>`, poi osserva per al massimo un ciclo keeper + margine con un unico watcher bounded. PASS solo se ricompare come `device` e `model:Pixel_8a`. Non disconnettere né testare realmente il TCL.
7. Se serve nuovo pairing manuale o il Pixel non è disponibile per una prova sicura: `BLOCKED` con il solo passo necessario. Nessun retry identico.
8. Dopo PASS stop immediato: niente audit, test aggiuntivi, modifica sorgente o controlli remoti equivalenti.

# Acceptance
PASS solo se HEAD include il commit minimo già testato, il deploy helper completa, la unit installata usa l'eseguibile canonico ed è enabled/active con restart policy prevista, e il Pixel torna automaticamente `device model:Pixel_8a` dopo l'unico disconnect controllato.

# Non-goal
Niente nuove modifiche codice, CI, MegaVault, WhatsApp, PersonalHub, APK, test TCL reali, firewall/rete globale, audit altri repo o pairing nuovo.

# Stop roadmap
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 635814 --confirm-executed`

Non fare dry-run separati né controlli Git equivalenti dopo `status=completed|already_completed`.
Prima riga finale `RESULT=PASS|BLOCKED|FAIL`; massimo 6 righe: `COMMIT`, `DEPLOY`, `SYSTEMD`, `PIXEL_RECONNECT`, `CI`, `BLOCKER`.
