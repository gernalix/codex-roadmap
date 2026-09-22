PROMPT_ID=334210 | PARENT_PROMPT_ID=943492 | project_id=92 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
Codex Desktop project: Fedora

# Goal
Chiudi il blocker emerso in PROMPT_ID=943492: determina in modo non distruttivo come viene realmente sbloccato il volume root LUKS /dev/nvme0n1p3 e verifica che esista un percorso di recovery affidabile prima dell'aggiornamento firmware Lenovo ThinkPad P14s Gen 5 AMD 0.1.22 -> 0.1.23.

# Starting point autoritativo
- PROMPT_ID=943492 ha terminato BLOCKED;
- LUKS_DEVICE=/dev/nvme0n1p3;
- TPM2=absent;
- ACTIVE_KEYSLOTS=1;
- RECOVERY_PATH=FAIL con la passphrase provata;
- BITLOCKER=PRESENT;
- la recovery key BitLocker è già conservata in Bitwarden; NON richiederne, mostrarne o copiarne il valore;
- il firmware 1.23 non va ancora installato in questo task.

# Scope e sicurezza
Task di sola diagnosi/verifica. Non modificare LUKS, keyslot, token, crypttab, initramfs, bootloader, TPM, Secure Boot, BIOS/UEFI o BitLocker. Non aggiungere/rimuovere credenziali e non eseguire l'update firmware. Non usare dmsetup --showkeys o qualunque comando che esponga chiavi di cifratura. Non stampare contenuti di keyfile/segreti.

# Esecuzione
1. Prima di qualunque lavoro esegui:
   `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 334210`
   Procedi solo se il writer conferma `running`.
2. Conferma rapidamente che il root attivo mappi davvero a `/dev/nvme0n1p3`. Se lo starting point è falso, correggi il device con evidenza read-only e continua.
3. Ricostruisci il percorso di unlock reale con discovery mirata:
   - `cryptsetup status`, `lsblk`, `findmnt`;
   - `cryptsetup luksDump` e `systemd-cryptenroll --dump`;
   - `/etc/crypttab`, unit/generated unit systemd-cryptsetup pertinenti e journal del boot corrente;
   - configurazione initramfs/dracut solo quanto necessario;
   - verifica presenza di meccanismi FIDO2/PKCS#11/TPM2/Clevis/Tang o keyfile senza mostrare materiale segreto.
4. Se crypttab/initramfs indica un keyfile:
   - verifica solo path, ownership/permessi e presenza;
   - non mostrarne il contenuto;
   - se tecnicamente sicuro, usa `cryptsetup open --test-passphrase --key-file <path> <device>` o equivalente read-only per provare che quel percorso sblocchi davvero il volume.
5. Se il percorso reale è una passphrase interattiva:
   - identifica quale prompt/stack la usa al boot;
   - ripeti al massimo un test `cryptsetup open --test-passphrase <device>` lasciando all'utente l'inserimento locale;
   - non chiedere mai la passphrase in chat, argv, log o output.
6. Se esiste un altro token/meccanismo di unlock, verifica in modo non distruttivo che sia realmente utilizzabile e documenta solo il tipo, non il segreto.
7. BitLocker:
   - considera la recovery key coperta perché conservata in Bitwarden;
   - verifica solo che il volume BitLocker sia identificabile e che la recovery key non sia necessaria a questo task;
   - non aprire Bitwarden, non leggere la key e non eseguire operazioni BitLocker.
8. Classifica il risultato:
   - PASS: esiste ed è stato verificato un percorso di unlock/recovery LUKS indipendente da un TPM assente, e la recovery BitLocker è già disponibile fuori dal disco;
   - BLOCKED: non è possibile dimostrare un percorso LUKS affidabile senza una decisione/credenziale umana aggiuntiva;
   - FAIL: evidenza di configurazione incoerente/pericolosa non risolvibile in-scope.
9. Non installare il firmware 1.23. Questo prompt chiude solo il preflight recovery.

# Acceptance
PASS solo se:
- il meccanismo reale di unlock di /dev/nvme0n1p3 è identificato con evidenza;
- almeno un percorso di unlock/recovery LUKS è verificato realmente senza modificare la configurazione;
- nessun segreto è stato esposto;
- BitLocker è coperto dalla recovery key già disponibile in Bitwarden;
- è esplicito se, dal solo punto di vista recovery del disco, l'update firmware 1.23 può procedere.

# Stop
Finalizza una sola volta con:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 334210 --result PASS|BLOCKED|FAIL --confirm-executed`

Output finale massimo 8 righe:
PROMPT_ID=334210
RESULT=PASS|BLOCKED|FAIL
LUKS_DEVICE=<device>
UNLOCK_MECHANISM=<passphrase|keyfile|fido2|pkcs11|clevis|other|unknown>
TPM2=absent|present|unknown
RECOVERY_PATH=PASS|FAIL
BITLOCKER_RECOVERY=AVAILABLE_IN_BITWARDEN
FIRMWARE_RECOVERY_GATE=PASS|BLOCKED
BLOCKER=<none|testo breve>