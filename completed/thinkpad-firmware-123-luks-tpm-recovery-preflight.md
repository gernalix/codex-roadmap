PROMPT_ID=943492 | project_id=92 | model=GPT-5.6 Terra | reasoning=low | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Verifica, prima dell'aggiornamento firmware Lenovo ThinkPad P14s Gen 5 AMD 0.1.22 -> 0.1.23, che il volume Fedora cifrato con LUKS sia recuperabile anche se l'update invalida eventuali secret/PCR TPM.

# Scope
SOLO preflight LUKS/TPM/recovery sul Fedora reale. NON installare il firmware, NON modificare enrollment TPM/LUKS, NON aggiungere/rimuovere keyslot, NON fare backup/restore del disco, NON cambiare Secure Boot/BIOS, NON stampare segreti.

# Starting point
- dispositivo: Lenovo ThinkPad P14s Gen 5 AMD;
- GNOME Software/fwupd propone System Firmware 0.1.22 -> 0.1.23;
- release note mostrata: FIT InROM diagnostics 04.47.000; enhancement per vulnerabilità di sicurezza; dopo UEFI BIOS 1.23+ non è più possibile rollback a versioni precedenti alla 1.23;
- fwupd avverte che alcuni platform secrets potrebbero essere invalidati e chiede di avere la volume recovery key;
- obiettivo: provare che esista un metodo di sblocco LUKS indipendente dal TPM prima di autorizzare l'update.

# Esecuzione minima
1. Prima di qualunque verifica esegui il claim canonico:
   `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 943492`
   Procedi solo se il writer conferma `running`.
2. Identifica root device e volume cifrato con un singolo inventario read-only, usando `findmnt`/`lsblk`/`cryptsetup status` quanto basta. Non assumere `/dev/nvme0n1p3`.
3. Se il root non è su LUKS, termina con risultato `NOT_APPLICABLE` e spiega perché.
4. Sul device LUKS corretto esegui SOLO letture:
   - `sudo cryptsetup luksDump <device>`;
   - `sudo systemd-cryptenroll --dump <device>` se supportato;
   - determina se sono presenti token TPM2 e quanti keyslot LUKS risultano attivi, senza esporre materiale segreto.
5. Determina se il boot corrente dipende dal TPM oppure se esiste già un percorso passphrase/recovery indipendente. Non inferire dal solo fatto che esista un token TPM.
6. Verifica il percorso indipendente con:
   `sudo cryptsetup open --test-passphrase <device>`
   Lascia che l'utente inserisca la passphrase esclusivamente nel prompt locale del terminale. Non richiederla in chat, non passarla in argv/stdin automatizzato, non registrarla in log.
7. Se il test passphrase è PASS, registra `RECOVERY_PATH=PASS`.
8. Se il test fallisce o non è disponibile una passphrase/recovery indipendente, termina `BLOCKED` e NON modificare LUKS/TPM per crearne una: la decisione su aggiungere/ruotare credenziali deve restare separata.
9. Controlla soltanto se esistono volumi BitLocker/Windows pertinenti; se non esistono, annota `BITLOCKER=NOT_APPLICABLE`. Non fare operazioni Windows.
10. Non eseguire `fwupdmgr update`, non cliccare Download/Install e non schedulare reboot.

# Acceptance
PASS solo se:
- device LUKS del root identificato senza assunzioni;
- token TPM/keyslot descritti senza segreti;
- una passphrase/recovery indipendente dal TPM è stata verificata realmente con `cryptsetup --test-passphrase`;
- nessuna configurazione LUKS/TPM/firmware è stata modificata;
- è chiaro se l'update firmware 1.23 può procedere dal punto di vista del recovery del volume.

# Stop / risultato roadmap
Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 943492 --result PASS --confirm-executed`

Su BLOCKED/FAIL:
usa lo stesso `roadmap_result.py` con l'esito coerente.

Output finale massimo 7 righe:
PROMPT_ID=943492
RESULT=PASS|BLOCKED|NOT_APPLICABLE|FAIL
LUKS_DEVICE=<device|none>
TPM2=<present|absent|unknown>
ACTIVE_KEYSLOTS=<count|unknown>
RECOVERY_PATH=PASS|FAIL|NOT_APPLICABLE
BITLOCKER=NOT_APPLICABLE|PRESENT|UNKNOWN
