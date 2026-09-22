PROMPT_ID=472615
ROADMAP_PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Correggi la regressione reale osservata dopo un riavvio completo del PC: tutte le note degli overlay Chrome risultano vuote dopo il boot. Verifica prima se i dati sono ancora nel DB e il problema è solo di reidratazione/startup race; non trattare come data loss finché non è dimostrato.

# Evidenza live
- 741928 è PASS ed è già integrato.
- Dopo un successivo reboot del PC, le note di TUTTE le schede sono visivamente vuote.
- Prima del reboot le note risultavano persistenti nei normali reload/reopen testati.
- Lo store canonico salva le note in ~/.local/state/chrome-codex-switcher/state.sqlite3, tabella contexts(note,codex_note,...).
- Il content script parte con textarea vuota e chiama refresh() una volta; se il daemon/API non è ancora raggiungibile al boot, oggi può rimanere senza context reidratato.
- background.js onStartup esegue recoverEligibleTabs(), ma una content script viva può rispondere al probe senza avere ancora ricaricato il context dal daemon.
Questa è un'ipotesi forte, NON una root cause già provata.

# Esecuzione
1. Claim con roadmap_start.py --prompt-id 472615 e usa solo il worktree restituito.
2. Prima di installare/modificare:
   - backup consistente read-only di state.sqlite3 + WAL/SHM se presenti;
   - query read-only di contexts: conta righe con note/codex_note non vuote e salva SOLO conteggi/id/url abbreviati, non stampare testo privato;
   - verifica il path DB effettivo del daemon e che non esista un secondo DB vuoto usato dopo login.
3. Classifica il failure:
   A) dati presenti nel DB ma UI vuota => hydration/startup identity race;
   B) DB canonico realmente vuoto/troncato => data-loss/storage lifecycle;
   C) note presenti ma tab restaurate ricevono nuovi context_id/URL non riconciliati => identity remap.
   Non procedere con fix speculativo finché A/B/C non è dimostrato.
4. Riproduci il reboot senza dover riavviare ripetutamente il PC:
   - fixture SQLite con almeno 3 context e note diverse;
   - daemon inizialmente OFF;
   - avvia/riapri browser/content scripts con tab restaurate e nuovi tab IDs;
   - avvia daemon con ritardo;
   - verifica che le note vengano automaticamente reidratate senza refresh manuale della pagina.
   Simula anche daemon restart mentre Chrome resta aperto.
5. Se root cause A:
   - implementa recovery esplicito daemon-offline -> online;
   - preferisci un meccanismo idempotente: content refresh retry bounded/backoff finché context è null, oppure background che rileva health transition e invia refreshContext alle tab supportate;
   - dopo recovery, non sovrascrivere textarea focused o edit non ancora persistiti;
   - niente polling aggressivo permanente.
6. Se root cause C:
   - correggi ensureContext/tab-map reconciliation per il Chrome session restore;
   - URL/context identity deve riusare il context persistente corretto anche con nuovi tab IDs;
   - due tab con stesso URL non devono rubarsi note a vicenda: fail closed o usa una chiave stabile più forte quando disponibile.
7. Se root cause B:
   - trova esattamente chi crea/sostituisce/tronca il DB al boot/install;
   - correggi il lifecycle senza ripristinare automaticamente backup vecchi sopra dati più nuovi;
   - aggiungi atomicità/backup solo se supportato dall'evidenza.
8. Aggiungi regression test obbligatori:
   - DB note sopravvive a chiusura/reopen Store;
   - daemon delayed-start + tab già aperta => nota si popola automaticamente;
   - daemon restart => UI si riconnette;
   - Chrome session restore con nuovi tab IDs => note corrette;
   - 3 tab/3 note diverse restano distinte;
   - note independent Chrome/Codex restano distinte;
   - edit focused durante reconnect non viene sovrascritto;
   - nessun nuovo context vuoto se esiste mapping persistente deterministico.
9. Esegui test mirati, poi un solo E2E aggregato con DB/profilo temporanei.
10. Runtime Fedora reale:
   - installa dal worktree;
   - verifica prima che le note reali esistano nel DB senza stamparle;
   - restart controllato del solo daemon;
   - restart controllato Chrome se possibile senza perdita sessione;
   - se serve un vero reboot per l'ultimo gate, prepara un self-check persistente che al login confronti SOLO hash/count/IDs e stato UI, senza esporre note; chiedi reboot all'utente solo come ultimo gate.
11. Non cancellare/ripristinare il DB reale, non svuotare Chrome profile, non fare clear storage.
12. Dopo PASS finalizza e STOP.

# Acceptance
PASS solo se:
- root cause A/B/C è dimostrata;
- le note reali risultano ancora presenti oppure l'eventuale data loss è spiegata con evidenza;
- 3 note diverse sopravvivono a Store reopen, daemon delayed-start/restart e Chrome session restore;
- dopo startup la UI si reidrata automaticamente senza refresh manuale per-tab;
- reconnect non sovrascrive edit locali;
- split Chrome/Codex resta corretto;
- test mirati + E2E + smoke Fedora PASS;
- nessun dato reale viene cancellato o sovrascritto.

# Non-goal
Niente launcher 989559, indice PROMPT_ID, redesign note, refactor generale o cleanup non necessario.

# Report
Max 9 righe: PROMPT_ID, RESULT, ROOT_CAUSE, DB_PRESERVED, HYDRATION, SESSION_RESTORE, SPLIT_NOTES, TESTS, BLOCKER.