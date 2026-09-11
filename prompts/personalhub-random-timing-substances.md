[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=381527 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

# Goal
Accorpare in un solo pass Timer/Substances lavori che condividono settings, notification/scheduler, button identities e QA: Random timer, Random alerts e i piccoli fix Substances. Un solo bump versione, una sola build/install/device QA.

Assorbe `640217`, `731864`, `684731`. Prima inventaria una sola volta scheduler/reboot/deep-link/settings esistenti e i modelli button Timer/Substances; riusali, niente motori paralleli.

# A — Substances
- sostituisci `Order epoch day`/`Prescription epoch day` con date picker leggibili IT/EN usando `LocalDate`; persistenza resta epoch-day;
- new prescription conserva entrambe le date default=today; existing round-trip esatto; cambiare una data non cambia l'altra;
- un configured action button deve registrare esattamente una entry anche con stock=0, senza refill/acquisto automatico o cambio di semantica inventario.

# B — Random timer
Home card + setting max minuti (default 60, >0). Un solo run attivo; target casuale `0<target<=max` completamente nascosto fino alla risposta, anche da accessibility/notification. Persisti run per process death/reboot usando scheduler esistente. Alla scadenza notifica `Quanto tempo è passato?`; tap apre input numerico focalizzato. Solo dopo submit mostra elapsed reale e `perceived/actual`, persistendo attempt/timestamp/precisione sufficiente. QA usa clock/duration controllati, non attese reali.

# C — Random alerts Timer + Substances
Per ogni button configurabile: enabled, N positivo, per-hour/per-day, persistiti per stable button identity. Master switch globale sospende/cancella delivery senza cancellare config e al ri-enable riparte dal futuro senza catch-up.

Con clock/random testabili genera esattamente N istanti unici per finestra attiva (60m/24h), persisti pending state, sopravvivi process death/reboot, cancella stale schedule su config/delete e impedisci duplicati. Notifica identifica modulo/button e NON esegue/recorda automaticamente l'azione.

# Verification
Test focalizzati condividendo fixture/scheduler: picker round-trip + stock0; hidden timer/one-active/deep-link/ratio/recreation; multi-button random alerts/master OFF-ON/N bounds/no duplicates. UNA smoke Pixel: date picker+stock0, Random timer breve controllato, un Timer+un Substances Random alert forzato. Niente broad QA.

PASS solo se A+B+C passano; poi una build APK, Pixel install, Telegram delivery, commit/push e STOP.

Output: `PROMPT_ID`, `RESULT`, Substances fixes, scheduler condiviso, Random timer semantics, Random alerts/master, test/Pixel, version/APK/delivery, SHA, blocker.
