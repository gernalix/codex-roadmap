[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=381527 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD | campaign_id=PH_FINAL_20260912 | type=Goal`

# Goal — fase 1/3
Completa in PH, con diff minimo: (A) date picker prescrizioni Substances; (B) Random timer; (C) Random alerts Timer+Substances; (D) bulk end Since When; (E) residui UI/People già localizzati. **Niente bump/final APK/Pixel main/Telegram**.

# Starting point
Riusa boundary esistenti: `EpochDayPickerField`; `TimeFence*`/`AlertsCapsuleViewModel`; `SostanzeNotificationScheduler`+receiver/restore/ViewModel; `SinceWhenCapsuleViewModel`/`LifePeriodsScreen`. stock=0 intake è già corretto: non cambiarlo. Home conserva l'unica versione host. `SoldiTheme` esiste. People call overlay ha già intent/gate/redaction: verifica, non ri-auditare.

# Implementa
- **Substances dates:** sostituisci solo i 2 epoch-day raw con `EpochDayPickerField`; new=oggi, edit round-trip, campi indipendenti; no migration.
- **Random timer:** Home card, max minuti >0 default 60, un run; target `0<target<=max` invisibile UI/accessibility/notifica fino al submit; persistenza+process death/reboot riusando scheduling; scadenza→`Quanto tempo è passato?`→input numerico→solo submit mostra reale+rapporto. Clock/random iniettabili, zero wait reali nei test.
- **Random alerts:** per pulsante: enabled,N>0, per-hour/day, stable identity persistita; master OFF cancella future senza perdere config, ON solo futuro; esattamente N istanti unici/finestra; reboot-safe/no duplicate/stale cancel su config/delete; notifica identifica modulo+pulsante e NON esegue/registra azione. Riusa scheduler esistenti, niente secondo motore.
- **Since When:** multiselect soli attivi; `Termina selezionati ora` cattura 1 timestamp e assegna stesso `endMs>startMs`; singola operazione bulk + un refresh/persist/backup; selection saveable/clear success/cancel; no migration.
- **UI/People:** rimuovi solo versioni visibili già localizzate: Timer `AppPatchVersion/versione_patch_v`, Substances `BuildConfig.VERSION_NAME`, Places Home version item/footer, WordPulse `v${BuildConfig.VERSION_NAME}`/duplicato root, Soldi root, People `patch-version.txt/loadPatchVersion()` visibile. Non eliminare helper tecnici usati altrove. Risultato: Home PH=1 versione host, root moduli=0. In `SoldiActivity` usa `SoldiTheme` al posto del root `MaterialTheme` se ancora presente. Esegui test esistenti `HomeAutoExportStatusTest` + `CallOverlayRequestGateTest`; niente nuovo audit People.

# Verifica/stop
Test mirati soltanto per picker+stock0, random timer, random alerts, bulk Since When, version matrix/theme/overlay. Una sola QA isolata emulator/TCL per ciò che i test non dimostrano. Niente broad suite/package reale Pixel. Commit/push PH; non cambiare `version.txt`. Side issue non bloccanti: segnala senza investigare. Stop appena PASS.

Su PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 381527 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 381527`

Output ≤8 righe: RESULT, picker, random timer, random alerts, SinceWhen, UI/People, test/QA, SHA/blocker.
