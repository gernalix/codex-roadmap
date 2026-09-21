PROMPT_ID=741928 | project_id=96 | MODEL=GPT-5.6 Sol | reasoning=medium | MegaVault=STANDARD
REPO=gernalix/chrome-codex-switcher

# Goal
Porta chrome-codex-switcher a uno stato realmente affidabile sul Fedora reale e costruisci una verifica completa delle sue superfici utente correnti. Non considerare sufficiente CI verde o test statici: correggi i bug riproducibili e dimostra end-to-end che le funzioni esistenti lavorino insieme senza stato stale, cross-talk o dipendenze da refresh/reload manuali non documentati.

# Evidenza live già verificata
- Dopo `git pull --ff-only && ./install.sh` e disable/enable del companion GNOME, il problema di scoping della nota desktop NON risulta risolto: la nota può restare visibile sopra app estranee.
- L'opzione "Separate Chrome/Codex notes" non produce il comportamento atteso.
- Dopo il reload/install dell'estensione, ricliccando "Link Codex" una nota Chrome mostra `Link failed: extension_context_invalidated`.
- Il commit main `6c3d20234ed49e562751ca1dde5623ad9b8b9bd3` aveva CI PASS, quindi i gate correnti non coprono il failure live.
- Chrome autorevole: Google Chrome RPM. GNOME/Wayland reale. Non reintrodurre Chrome Flatpak.
- Stato/note reali dell'utente sono dati: non cancellare DB, Chrome profile o dati ChatGPT per fare test.

# Scope
Tutto il comportamento user-facing GIÀ esistente di chrome-codex-switcher e la sua affidabilità runtime: Chrome extension, content overlay, background/service-worker lifecycle, daemon/host, GNOME companion, note/context state, pairing/linking, switch/focus, dashboard/search, shortcut globale, install/update/uninstall e systemd. Escludi la nuova feature desktop launcher di PROMPT_ID=989559: questo task deve stabilizzare la base su cui quel task dipenderà.

# Esecuzione
1. Prima di leggere/modificare il target esegui `roadmap_start.py --prompt-id 741928` e lavora SOLO nel worktree restituito.
2. Fai UNA inventory bounded delle feature correnti leggendo solo entry point/contratti autorevoli: README, manifest, content/background/sidepanel, host CLI/daemon/store, GNOME companion, installer/systemd e test. Produci una matrice breve feature -> gate automatico -> smoke live. Non esplorare history/branch/PR vecchie salvo evidenza concreta.
3. Riproduci per primi i tre failure live sopra e trova la root cause reale di ciascuno. Correggi in batch solo cause nello stesso failure domain; niente retry identici senza nuova evidenza.

## A. Lifecycle estensione Chrome
- Dopo install/update/reload dell'unpacked extension, le tab ChatGPT già aperte NON devono restare con un content script morto.
- `extension_context_invalidated` non deve essere uno stato permanente né lasciare overlay apparentemente interattivi ma scollegati.
- Implementa recovery robusto e idempotente: il runtime nuovo deve poter sostituire/riattivare istanze stale nelle tab eleggibili senza richiedere refresh manuale di ogni tab, oppure, se Chrome impone un limite tecnico reale, l'UI stale deve autodistruggersi e il percorso di recovery deve essere automatico tramite background reinjection/navigation minima. Non accettare un semplice "ricarica la pagina" come fix.
- Nessun doppio overlay/listener dopo reinstall/reload.

## B. Scoping corretto degli overlay
- Chrome overlay: deve esistere solo nelle pagine/URL supportati e appartenere al contesto corretto.
- GNOME desktop overlay: deve essere visibile solo quando la vera app ChatGPT/Codex Desktop è focused; passando a Obsidian, Terminale, Chrome o altra app deve sparire entro il bound del refresh.
- Non usare il titolo finestra come identità applicativa.
- Verifica con almeno ChatGPT Desktop + Obsidian + Terminale + Chrome e con titoli contenenti parole "ChatGPT"/"Codex" per escludere falsi positivi.
- Passando tra più chat/tabs non mostrare la nota del contesto precedente durante la risoluzione del nuovo contesto.

## C. Note condivise/separate
Definisci e testa esplicitamente la semantica:
- modalità condivisa OFF: una modifica Chrome si riflette in Desktop e viceversa;
- attivando "Separate Chrome/Codex notes": il valore condiviso corrente viene inizializzato in entrambe le superfici e, da quel momento, edit Chrome e Desktop sono indipendenti;
- riavvio/reload/reopen conserva entrambi i valori separati;
- tornando alla modalità condivisa, il valore sorgente corrente viene applicato in modo deterministico secondo il contratto esistente, senza perdita silenziosa o mescolanza casuale;
- toggle ripetuti sono idempotenti.
Aggiungi test store/API + E2E/runtime per questi casi, non solo test unitari del DB.

## D. UI note
Per Chrome e Desktop dove applicabile verifica: edit, move, resize, collapse, hide/close, reopen/toggle, focus testo e persistenza prevista. Geometria/stato non devono saltare tra contesti diversi. Resize/move devono restare entro la finestra/schermo e non rendere la nota irrecuperabile.

## E. Pairing e navigazione
Verifica almeno:
- Link Codex/arm -> acquisizione deep link -> binding corretto;
- late binding esistente;
- stato linked/unlinked coerente;
- switch/focus Chrome -> Codex e Codex -> Chrome verso il twin corretto;
- unlink/relink;
- due tab Chrome e due chat Codex senza cross-pairing;
- thread/chat change non riusa nota o twin precedente.
Fail closed su match ambiguo: mai scegliere una chat/tab "probabile".

## F. Daemon, dashboard e shortcut
- `context-twin status`, health/API e heartbeat Chrome/GNOME coerenti e freschi.
- Context Search trova prompt_id/titoli/note e apre/focalizza il target giusto.
- Alt+Shift+S resta configurata sul Chrome RPM; prova separatamente registrazione runtime + launcher + apertura/focus dashboard. Se la pressione fisica non è sintetizzabile in sicurezza, NON dichiarare automaticamente BLOCKED: costruisci una prova deterministica dei due lati del binding e registra come unico gate manuale opzionale la pressione fisica; tutte le altre funzioni devono essere dimostrate.
- systemd user service deve essere enabled/active e recuperare dopo restart controllato.

## G. Install/update/uninstall
- `install.sh` due volte consecutive = idempotente.
- Update da runtime già aperto non lascia componenti vecchi misti (Chrome extension, daemon, GNOME companion).
- Versioni/heartbeat installati devono corrispondere ai sorgenti del task.
- `uninstall.sh` va testato solo in ambiente fixture/temp o con backup/ripristino; non distruggere configurazione/dati reali.
- Nessuna dipendenza Flatpak.

# Test strategy
1. Prima gate statici/unit mirati.
2. Aggiungi una suite di regressione che copra almeno: extension reload/reinjection; shared/separate notes; context isolation; GNOME app identity; pairing multi-context; UI-state persistence; installer idempotence.
3. Usa profilo Chrome e DB temporanei per i test distruttivi; niente dati reali.
4. Poi un solo E2E aggregato automatizzato.
5. Infine UNA smoke matrix sul Fedora reale, usando dati/contesti di test creati apposta e ripuliti senza toccare note/binding reali. Per interazioni desktop riusa AT-SPI/GNOME hooks esistenti; niente OCR, image matching, xdotool/ydotool o coordinate hardcoded.
6. Se un gate fallisce: correggi la causa, rilancia prima solo quel leaf gate; ripeti l'aggregato finale soltanto dopo cambi che lo invalidano.

# Acceptance
PASS solo se:
- i tre bug live riportati all'inizio sono riprodotti prima del fix e non riproducibili dopo;
- nessun `extension_context_invalidated` resta dopo install/reload e le tab già aperte recuperano senza refresh manuale per-tab;
- overlay Desktop non appare su app estranee;
- shared/separate notes PASS end-to-end con persistenza;
- move/resize/collapse/close/reopen PASS;
- pairing/link/relink/switch PASS anche con almeno 2x2 contesti senza cross-talk;
- daemon/status/heartbeat/dashboard/search PASS;
- global shortcut ha prova deterministica di registrazione+launcher e, se tecnicamente possibile in sicurezza, smoke fisico automatizzato; l'eventuale singola pressione manuale è chiaramente separata e non maschera altri failure;
- install/update idempotente e runtime versions allineate;
- test mirati + E2E aggregato + smoke Fedora reale sono PASS;
- nessun test ha cancellato o sovrascritto stato utente reale.

# Non-goal
Non implementare 989559, non aggiungere nuove feature non necessarie alla stabilità, niente redesign UI, refactor generale, cleanup/modernizzazione, audit history, Chrome Flatpak o modifiche a Workflowy/codex-roadmap salvo finalizzazione automatica.

# Stop / report
Dopo tutti gli acceptance criteria, finalizza con `roadmap_finish.py --prompt-id 741928 --confirm-executed` e STOP.
Output max 12 righe: PROMPT_ID, RESULT, ROOT_CAUSES, EXTENSION_LIFECYCLE, OVERLAY_SCOPE, NOTES_MODE, UI_STATE, PAIRING, DASHBOARD_SHORTCUT, INSTALL_UPDATE, TESTS, BLOCKER.
