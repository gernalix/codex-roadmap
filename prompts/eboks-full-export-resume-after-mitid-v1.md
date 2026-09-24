PROMPT_ID=582946
PARENT_PROMPT_ID=738242
ROADMAP_PROJECT=e-Boks exploration
MEGAVAULT=FAST

# Goal
Riprendi e completa l'export e-Boks già avviato da 738242 DOPO che l'utente ha completato il login MitID nella finestra e-Boks già aperta.

# Stato già verificato
- Il solo blocker attuale è logout/sessione e-Boks terminata.
- L'ultimo fix-packet dice: "e-Boks è confermato in logout; il login MitID aperto richiede azione manuale."
- Riusa l'output e il progress.json già esistenti; non ricominciare da zero.
- Nessuna probe/API privata: solo Browser Use e UI ufficiale e-Boks.

# Esecuzione
1. Claim 582946 e continua nella stessa chat/sessione di 738242.
2. Verifica una sola volta che la sessione e-Boks sia autenticata. Se non lo è, BLOCKED immediato con LOGIN_MITID_REQUIRED; nessun retry.
3. Leggi progress.json e riparti dal primo batch/sezione non confermato. Non riscaricare batch già registrati.
4. Completa Posta pubblica e Posta dalle aziende fino a esaurimento reale della paginazione.
5. Mantieni le regole già verificate di 738242: batch <=15, firma stabile per riga, zero azioni distruttive, zero file preesistenti spostati, zero .crdownload finali.
6. Non estrarre testo dai PDF in questo task.
7. Test/verifica solo la completezza dell'export; niente audit o refactor.

# Stop
PASS appena entrambe le sezioni sono complete e progress.json è coerente. Output max 7 righe: PROMPT_ID, RESULT, OUTPUT_DIR, POSTA_PUBBLICA, POSTA_AZIENDE, BATCHES, BLOCKER.