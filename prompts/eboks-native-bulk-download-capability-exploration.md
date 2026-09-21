PROMPT_ID=206756 | PROJECT=e-Boks exploration | project_id=23 | MODEL=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST

# Goal
Esplora SOLO la scheda Chrome e-Boks già aperta e autenticata e determina con evidenza quale export/download nativo massimo è disponibile: singolo documento, selezione multipla, intera pagina/cartella oppure intera inbox. Non implementare ancora lo scraper e non scaricare l'intera inbox.

# Starting point
- Chrome è già aperto con una tab e-Boks autenticata.
- Il side panel ufficiale ChatGPT mostra "Native transport disconnected": NON considerarlo un blocker automatico.
- Esistono meccanismi locali separati dal side panel, incluso chrome-codex-switcher e la possibilità di usare una piccola estensione MV3 locale/DevTools se strettamente necessario.
- Prompt successivo già in roadmap: 218695, bootstrap del repo eboks-scraper. Questo prompt deve produrre i fatti che 218695 userà per scegliere l'architettura.
- Nessuna automazione MitID, estrazione cookie/sessione, reverse engineering di API private o bypass CAPTCHA/rate-limit.

# Execution
1. Avvia con `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 206756`.
2. Usa la tab e-Boks esistente; non fare logout, non chiuderla e non rilanciare Chrome salvo necessità dimostrata.
3. Prova prima i meccanismi locali già installati per focalizzare/ispezionare la tab. Il side panel ChatGPT non è richiesto.
4. Se i meccanismi esistenti non permettono di leggere il DOM, usa il minimo fallback locale sicuro: una piccola estensione MV3 temporanea/content script limitata a e-boks.dk oppure DevTools sulla stessa tab. Non leggere/esportare cookie, token o credenziali.
5. Esplora la UI Inbox e i menu/checkbox relativi a selezione e download. Verifica separatamente:
   - selezione multipla di messaggi;
   - eventuale "select all" della pagina;
   - eventuale "select all" dell'intera cartella/inbox;
   - azione "Save local copy"/equivalente;
   - se l'output è uno ZIP, più PDF o altro;
   - se un messaggio con più allegati produce più PDF;
   - comportamento con paginazione/scroll;
   - limiti di quantità visibili o messaggi UI.
6. Fai al massimo UN test bounded su 2-5 documenti non sensibili quanto basta a confermare il comportamento. Non esportare tutta l'inbox.
7. Non analizzare endpoint di rete privati. Se compare CAPTCHA, 429/throttling, login scaduto o altro anti-bot, stop senza bypass.
8. Salva nel report solo metadati tecnici necessari (nomi dei controlli, quantità, tipo file, percorso UI); non riportare contenuti personali dei documenti.

# Acceptance
PASS solo se il report identifica con evidenza UNA delle capacità massime:
A) intera inbox/cartella in un'azione;
B) batch selezionabile con limite o per pagina;
C) solo singoli messaggi/documenti.
Indica inoltre formato output (PDF multipli/ZIP/altro), granularità "select all", eventuali limiti e il percorso UI esatto. Se il side panel ChatGPT non funziona ma l'ispezione riesce con un altro meccanismo, esplicitalo come PASS.

# Stop
Dopo aver classificato la capacità massima, finalizza e STOP. Nessuna implementazione del repo. Output max 9 righe:
PROMPT_ID
RESULT
BROWSER_CONTROL
MAX_EXPORT_SCOPE
SELECT_ALL_SCOPE
OUTPUT_FORMAT
BOUNDED_TEST
LIMITS
BLOCKER
