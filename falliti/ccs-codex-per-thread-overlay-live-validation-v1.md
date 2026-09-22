PROMPT_ID=125435
ROADMAP_PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

# Goal
Rendi effettivo e prova sul Fedora reale il fix per-thread degli overlay Codex già presente su main. L'overlay deve seguire la chat Codex Desktop attiva e non deve mai restare quello della chat precedente.

# Starting point già verificato
- main contiene il fix remoto: commit b432fd3eb2b86db2daa68985c6b7ccf2dec5c0b8 (preceduto da dfd0d6c0f558b2d57dc77bbfa56cb27bc276bf7b).
- GitHub Actions run 35682044804: job python PASS e job e2e PASS.
- Il codice ora preferisce un thread_id esatto esposto dal nodo AT-SPI selected/current; il titolo è solo fallback univoco.
- Su cambio chat/unfocus il daemon cancella subito active_codex_thread, così un refresh/modifica nota non può riaprire l'overlay vecchio.
- Non rifare audit generale, architettura, ricerca storica o test già verdi.

# Scope
1. Prima di qualunque modifica esegui il claim canonico con roadmap_start.py per PROMPT_ID=125435 e usa solo il worktree restituito.
2. Verifica che il worktree contenga b432fd3 o un main successivo che lo includa.
3. Distribuisci il codice usando SOLO l'installer/meccanismo già previsto dal repo; riavvia soltanto i componenti CCS necessari. Non cancellare DB, note, pairing, profilo Chrome o dati ChatGPT/Codex.
4. Con Codex Desktop reale aperto, ispeziona soltanto il subtree AT-SPI selected/current indispensabile per identificare la conversazione attiva.
5. Usa due thread Codex già associati se disponibili. Esegui un vero switch A -> B -> A dalla UI/sidebar, non una prova che si limiti ad aprire deep link e quindi preimposti il thread atteso.
6. Dopo ogni switch verifica `~/.local/bin/context-twin status`: active_codex_thread deve seguire il thread reale; active_codex_resolution deve indicare la fonte. L'overlay deve mostrare il context/note del thread attivo.
7. Durante la transizione il vecchio active_codex_thread deve diventare assente finché il nuovo thread non è risolto. Una modifica/refresh nota durante quello stato non deve far riapparire l'overlay precedente.
8. Prova anche una chat non associata o un caso non risolvibile: l'overlay deve restare nascosto, mai ereditare la nota precedente.
9. Se la build Desktop espone un thread ID/route/attributo stabile, usa e verifica il path `a11y_thread`. Se non lo espone, fai SOLO discovery locale mirata degli attributi/accessibility state o metadati Codex già disponibili per trovare un identificatore esatto e stabile. Non usare OCR, image matching, coordinate, uinput o clipboard come prova finale dell'identità attiva.
10. Se nessun identificatore esatto è disponibile, il fallback per titolo può restare solo per titoli univoci; titoli duplicati devono fallire chiuso. Non dichiarare PASS se due chat con lo stesso titolo possono ancora ricevere l'overlay sbagliato.
11. Modifica codice solo se la prova reale fallisce. In quel caso fai il minimo fix necessario, test mirati e poi una sola suite repo. Se non modifichi codice, non ripetere la CI remota già PASS.
12. Dopo eventuale fix ridistribuisci i componenti necessari e ripeti A -> B -> A. Finalizza e STOP appena gli acceptance criteria sono provati.

# Acceptance
- A -> B -> A cambia realmente thread e overlay senza riutilizzare lo stato della chat precedente.
- Il thread attivo è identificato esattamente quando la UI espone un'identità; i casi ambigui/non associati restano nascosti.
- Nessun overlay vecchio può riapparire durante la finestra di risoluzione.
- Nessuna perdita/modifica dei dati reali salvo gli aggiornamenti di stato previsti dal test.
- Nessun refactor, cleanup, launcher, dashboard o modifica fuori scope.

# Non-goal
Non implementare il launcher di PROMPT_ID=764529, non cambiare selezione modello/reasoning/progetto, non modificare Workflowy/codex-roadmap fuori dalla finalizzazione automatica, non creare PR.

# Report
Max 8 righe: PROMPT_ID, RESULT, DEPLOY, THREAD_ID_SOURCE, A_B_A, FAIL_CLOSED, TESTS, BLOCKER.
