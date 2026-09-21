PROMPT_ID=482761 | PARENT_PROMPT_ID=206756 | project_id=23 | MODEL=GPT-5.6 Luna | reasoning=low | MegaVault=FAST
WORKDIR=/home/daniele/projects/codex-roadmap

# Goal
Sblocca SOLO l’esplorazione browser di 206756 e completa la classificazione della massima capacità nativa di export e-Boks: A=intera inbox/cartella, B=batch limitato/per pagina, C=solo singoli. Non implementare eboks-scraper e non fare audit di repo.

# Evidenza già verificata
- 206756 ha una execution BLOCKED; il fix-packet più recente dice `Manually load <path> unpacked, then ask me to resume`; il precedente chiedeva conferma per installare la stessa temporary local extension.
- Il parent è stato riconciliato canonicamente a BLOCKED prima di questo fix.
- Chrome↔Codex Switcher serve a focus/pairing della tab; non trattarlo come DOM inspector e non modificarlo.

# Esecuzione minima
1. Avvia SOLO 482761 con roadmap_start.py e riusa la stessa chat/sessione e-Boks di 206756.
2. NON chiedere conferme o click manuali. Hai autorizzazione a usare/caricare la temporary unpacked extension già preparata da 206756; ricreala solo se il path non esiste più.
3. Fai prima UN tentativo senza installazione usando solo il controllo/accessibility già disponibile per leggere i controlli visibili della tab. Se basta, non toccare estensioni.
4. Se non basta, carica autonomamente la temporary extension nella sessione Chrome esistente. Deve essere minimale e limitata a e-boks.dk e leggere solo DOM/label/state necessari. Vietati cookie, token, local/session storage, network interception e API private.
5. Se chrome://extensions non è automatizzabile, usa al massimo UN fallback locale sicuro già disponibile per ottenere la stessa lettura UI. Nessun retry identico. Non riavviare Chrome se rischia di perdere la sessione autenticata.
6. Verifica SOLO multi-select, select-all page/cartella/inbox, Save local copy/equivalente, formato output, paginazione/scroll e limiti UI. Al massimo un test bounded su 2–5 documenti non sensibili; mai export completo.
7. Se compare login scaduto, CAPTCHA, 429 o anti-bot, STOP fail-closed. Se hai caricato una temporary extension, disabilitala/rimuovila alla fine senza toccare Chrome↔Codex Switcher.
8. Finalizza 482761 e STOP immediato.

# Acceptance
PASS solo se A/B/C è dimostrato con percorso UI, granularità select-all, output format e limiti; nessun intervento manuale richiesto; nessun cookie/token/session data letto; test bounded <=5 documenti. Se resta solo una capacità runtime concretamente non automatizzabile, BLOCKED con una sola riga precisa e senza nuovi retry.

# Report
Massimo 9 righe: RESULT, BROWSER_CONTROL, MAX_EXPORT_SCOPE, SELECT_ALL_SCOPE, OUTPUT_FORMAT, BOUNDED_TEST, LIMITS, TEMP_EXTENSION, BLOCKER.
