PROMPT_ID=413258 | PARENT_PROMPT_ID=482761 | ROOT_PROMPT_ID=206756 | project_id=23 | MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Completa SOLO l'esplorazione UI e-Boks necessaria a classificare la capacità nativa di export A/B/C, sostituendo la probe MV3 persistente che rompe il post-login con una probe strettamente on-demand e non invasiva.

# Evidenza già verificata
- La precedente `.eboks-ui-probe` con content script persistente interferisce con `digitalpost.e-boks.dk`: con probe attiva il redirect post-MitID resta bianco; con probe disattivata e-Boks si apre normalmente.
- Non riusare né riattivare quella probe.
- 206756 è BLOCKED; 482761 è pending ma il suo fallback consente ancora la probe problematica e viene superseduto da questo prompt.
- 218695 dipende dal completamento di questa classificazione.

# Vincoli tecnici obbligatori
- NON dichiarare `content_scripts` per e-boks.dk/digitalpost.e-boks.dk.
- NON eseguire codice durante login, redirect MitID, bootstrap o page load.
- Se serve una estensione, usare solo `activeTab` + `scripting` e iniettare `chrome.scripting.executeScript` ESCLUSIVAMENTE dopo che l'utente è già autenticato e la Inbox è completamente renderizzata.
- Nessun `host_permissions` persistente salvo prova tecnica indispensabile; preferire zero host permissions.
- Nessun cookie/token/localStorage/sessionStorage/indexedDB/network interception/API privata.
- Nessuna automazione MitID, CAPTCHA/rate-limit bypass.
- La probe deve essere read-only: leggere DOM/ARIA/label/state e, solo per il test bounded, azionare controlli UI ufficiali già visibili.
- Mai ricaricare la callback `session_state`; mai iniettare sul dominio MitID/NemLog-in.

# Esecuzione minima
1. Avvia con `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 413258`.
2. Elimina/disabilita la vecchia `/home/daniele/Documents/ChatGPT/Chrome/.eboks-ui-probe` dal flusso operativo; non riusarla.
3. Implementa la minima probe on-demand necessaria. Se puoi ottenere lo stesso risultato con un meccanismo già disponibile e non persistente, preferiscilo alla creazione di nuova infrastruttura.
4. Prima verifica che e-Boks continui ad aprirsi normalmente SENZA alcuna injection. Solo quando la Inbox autenticata è visibile, attiva una singola lettura on-demand del DOM.
5. Verifica esclusivamente:
   - multi-select;
   - select-all della pagina;
   - eventuale select-all dell'intera cartella/inbox;
   - Save local copy/equivalente;
   - output PDF multipli/ZIP/altro;
   - paginazione/scroll e limiti UI;
   - messaggi con più allegati, se osservabile senza ampliare il test.
6. Esegui al massimo un test su 2-5 documenti. Non esportare l'intera inbox.
7. Verifica esplicitamente il regression gate: e-Boks deve continuare a funzionare anche dopo logout/login successivo o, se non vuoi forzare un logout, almeno dopo navigazione completa e reload normale con probe inattiva; nessun blank screen causato dalla probe.
8. Se il runtime Codex non può materialmente attivare una injection on-demand senza un singolo gesto umano, NON tentare fallback persistenti. Prepara la probe sicura e termina BLOCKED con l'unico gesto richiesto, senza reintrodurre content scripts.
9. Finalizza e STOP.

# Acceptance
PASS solo se:
- la vecchia probe persistente non viene più usata;
- nessuna injection avviene durante login/redirect/page-load;
- e-Boks resta funzionante;
- A/B/C è dimostrato con percorso UI, SELECT_ALL_SCOPE, OUTPUT_FORMAT e LIMITS;
- test bounded <=5 documenti;
- nessun accesso a credenziali/session data/API private.

# Report
Massimo 9 righe:
PROMPT_ID
RESULT
PROBE_MODE
E_BOKS_REGRESSION
MAX_EXPORT_SCOPE
SELECT_ALL_SCOPE
OUTPUT_FORMAT
BOUNDED_TEST
BLOCKER
