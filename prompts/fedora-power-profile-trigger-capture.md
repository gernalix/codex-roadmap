[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=491736 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST`

# Goal
Sostituisci SOLO il watcher ad-hoc creato dal run `PROMPT_ID=814627` con una cattura locale affidabile, a privilegi corretti e già validata, capace di attribuire il **prossimo** passaggio spontaneo Fedora da `Performance` a `Power Saver` a uno dei trigger concreti: richiesta/hold D-Bus oppure cambio ACPI `platform_profile`. Non tentare ancora di “risolvere” il comportamento senza aver catturato il trigger reale.

# Starting point autoritativo
- host: Fedora 44 / GNOME 50 su ThinkPad P14s Gen 5 AMD;
- repo canonico locale: `/home/daniele/projects/fedora-system-monitor`, MegaVault project `15`;
- backend già provato: `tuned.service` + `tuned-ppd.service`; `power-profiles-daemon` non è il backend attivo;
- mapping già provato: PPD `power-saver` → TuneD `powersave` → `platform_profile=low-power`;
- transizione spontanea osservata il 2026-09-16 alle **03:36:38**: TuneD ha caricato `powersave`; ritorno a `throughput-performance` alle **05:35:24**;
- trigger di quella transizione NON è stato provato;
- storico utile ma non conclusivo: in precedenza `tuned-ppd` ha registrato hold `power-saver` da `org.gnome.SettingsDaemon.Power`;
- il run 814627 ha creato `/home/daniele/.local/bin/power-profile-watch` + `~/.config/systemd/user/power-profile-watch.service` + log `~/.local/state/power-profile-watch/power-profile-watch.log`;
- quel watcher utente NON è prova sufficiente: `dbus-monitor --system` ha riportato `AccessDenied` sul new-style monitoring ed è ricaduto in eavesdropping; inoltre la prima versione confrontava anche il timestamp e generava falsi change finché non è stata patchata;
- `fedora-system-monitor` possiede già un watcher D-Bus root nel servizio `fedora-system-monitor-events.service`, con risoluzione sender→PID/UID/processo. Non creare un terzo monitor se puoi riusare quello o aggiungere solo la cattura mancante localmente;
- il watcher remoto esistente è noto per osservare `Properties.Set ActiveProfile` sul path `/org/freedesktop/UPower/PowerProfiles`; per questa diagnosi servono anche `HoldProfile`/`ReleaseProfile`, il path `/net/hadess/PowerProfiles` se usato da `tuned-ppd`, e il percorso ACPI/sysfs che può attivare `sysfs_acpi_monitor=true`.

Lo starting point è completo: NON leggere README/roadmap/spiegazioni, `~/.codex/memories/MEMORY.md`, MegaVault o fare audit generale del repo/sistema salvo blocker concreto.

# Esecuzione minima
1. Una sola fotografia Git/runtime: stato del repo `fedora-system-monitor`, stato di `fedora-system-monitor-events.service`, stato del vecchio user watcher e profilo corrente. Raggruppa i controlli compatibili.
2. Verifica con un solo controllo mirato se il watcher root già installato sta effettivamente catturando richieste D-Bus. Non leggere l'intero repo: usa soltanto il boundary già noto del power-profile watcher se serve distinguere cosa manca.
3. Predisponi la **cattura minima mancante**, preferendo il servizio root canonico o un sidecar root diagnostico locale strettissimo. Deve registrare solo cambi/eventi pertinenti con timestamp e:
   - D-Bus `Properties.Set` di `ActiveProfile`;
   - `HoldProfile` e `ReleaseProfile`;
   - entrambi i path `/org/freedesktop/UPower/PowerProfiles` e `/net/hadess/PowerProfiles` quando presenti;
   - sender D-Bus e, finché ancora risolvibile, PID/UID/process/executable;
   - cambio reale di `/sys/firmware/acpi/platform_profile` (o path canonico equivalente già esposto dall'host), registrando solo variazioni e non polling rumoroso;
   - stato AC/batteria essenziale al momento dell'evento;
   - abbastanza contesto per correlare la stessa finestra con `tuned-ppd`, senza dump generali del journal.
4. Non fare modifiche al repository remoto in questo task. Se serve una modifica di codice permanente al repo, segnala esattamente il gap ma usa per ora solo il minimo strumento locale necessario alla cattura runtime.
5. Valida la cattura **prima** di dismettere il vecchio watcher. È consentito un solo test innocuo e reversibile che porti temporaneamente il profilo a `balanced` e subito di nuovo a `performance`, solo se necessario a dimostrare che la cattura vede il metodo D-Bus e attribuisce il caller. Alla fine il profilo deve essere `performance` e nessun hold di test deve restare attivo.
6. Se la cattura root è valida, disabilita/rimuovi il vecchio `power-profile-watch.service` utente e lo script ad-hoc del run 814627; conserva solo il log storico se utile per confronto. Non lasciare due watcher equivalenti attivi.
7. NON aspettare in sessione il prossimo evento spontaneo. Il PASS di questo task significa “cattura affidabile pronta”. Non fare `sleep` lunghi, polling manuale o audit aggiuntivi.

# Verifica
- processo/service della nuova cattura attivo e senza errori di autorizzazione/eavesdropping;
- prova controllata catturata con sender/processo quando eseguita;
- prova o snapshot del canale `platform_profile` senza eventi artificiali continui;
- profilo finale `performance`;
- vecchio watcher utente non più attivo dopo il PASS;
- output/log persistente con percorso esplicito da poter leggere al prossimo evento spontaneo.

# Non-goal
Nessun cambio di policy energetica permanente, nessuna disabilitazione di protezioni termiche/firmware, niente aggiornamenti Fedora/TuneD/GNOME, niente audit generale, niente refactor repo, niente tentativo di dedurre il colpevole dal solo storico, niente attesa indefinita del prossimo switch.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 491736 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 491736`

`push_verified=git_push_exit_0` è terminale. Output massimo 6 righe: RESULT, CAPTURE_PATH, DBUS_COVERAGE, PLATFORM_PROFILE_COVERAGE, OLD_WATCHER, FINAL_PROFILE/BLOCKER.
