PROMPT_ID=416826 | PARENT_PROMPT_ID=315972 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Completa l'integrazione utente di Salute sopra il modello canonico già mergiato: UI minima utile, Home/Hub/Context/Temporal Search e proiezione Obsidian health già prevista dai documenti. Non ridisegnare il modello dati.

# Precondizione
Esegui dopo 790233 PASS; stessa chat Codex è preferibile perché è una continuazione diretta, ma crea un nuovo branch dedicato dal main corrente.

# Esecuzione minima
1. Usa CODE_MAP `health.root|timeline|workflow` e documenti health; apri solo file consumer pertinenti.
2. Implementa/chiudi UI Salute per timeline, sample/measurements, note/snapshot AI e turnaround con i dati canonici; nessun DB parallelo.
3. Integra Salute nelle superfici globali PH tramite API/hub boundary, senza import feature-to-feature. Context e relazioni temporali devono riusare motori canonici, non duplicare inferenze.
4. Completa la proiezione Obsidian health one-way secondo il contratto esistente; niente import Obsidian→PH.
5. Test host mirati + architecture gate. Bump `version.txt` una volta rispetto al base.
6. Push/PR; solo dopo branch PASS acquisisci lease, review semantica latest main e QA `Pixel_8a` su Home→Salute, timeline/detail, Hub/Search e projection path. Merge/delete branch e rilascia lease. Nessuna release/Pixel fisico.

# Acceptance / stop
PASS con UI/integrations/projection funzionanti, nessun secondo datastore o boundary violation, host+AVD PASS e un solo bump. Finalizza PROMPT_ID 416826. Output max 8 righe.
