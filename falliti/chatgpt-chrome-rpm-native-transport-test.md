PROMPT_ID=628541 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST

# Goal
Verifica sul Fedora reale se l'errore del pannello laterale ChatGPT in Chrome `Native transport disconnected` dipende dall'uso di Chrome Flatpak, testando Google Chrome RPM nativo in parallelo. Non rimuovere né alterare il Chrome Flatpak o il suo profilo.

# Contesto già noto
- ChatGPT Desktop mostrato dall'utente: versione 26.915.31945, release 2026-09-18.
- Nel pannello laterale Chrome l'estensione ChatGPT mostra: `The Chrome side panel could not connect to the ChatGPT desktop app` / `Native transport disconnected`.
- NON assumere che il Chrome attivo sia Flatpak: verificalo prima.
- Obiettivo principale = prova A/B Flatpak vs RPM, non audit generale del desktop.

# Esecuzione minima
1. Acquisisci il claim canonico:
   `python3 ~/projects/codex-roadmap/tools/roadmap_start.py --repo ~/projects/codex-roadmap --prompt-id 628541`
   Se non diventa `running`, fermati.
2. Determina una sola volta come è installato il Chrome realmente in uso: controlla `flatpak info com.google.Chrome`, `rpm -q google-chrome-stable`, il path dell'eseguibile del processo Chrome attivo e il launcher. Riporta il risultato; niente scansioni generali.
3. Se `google-chrome-stable` RPM nativo non è installato, scarica esclusivamente l'RPM stable x86_64 ufficiale Google da `https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm` in `/tmp` e installalo con DNF. Non rimuovere il Flatpak. Non usare repo/package non ufficiali. Se serve sudo e non è disponibile in questa sessione, termina BLOCKED indicando l'unico comando esatto che l'utente deve autorizzare; niente workaround.
4. Verifica `rpm -q google-chrome-stable` e `command -v google-chrome-stable`; avvia esplicitamente `/usr/bin/google-chrome-stable`. Non cambiare browser predefinito, non copiare profili/cookie/password/bookmark tra Flatpak e RPM e non cancellare dati.
5. Con ChatGPT Desktop in esecuzione, prova l'estensione ChatGPT nel Chrome RPM. Se nel profilo RPM l'estensione manca, usa solo il percorso ufficiale ChatGPT/Chrome per installarla o abilitarla. Se Chrome richiede una conferma UI che non puoi eseguire, termina BLOCKED con una sola azione manuale precisa; non copiare a mano directory di estensioni.
6. Se il bridge funziona nel Chrome RPM, considera dimostrato che il percorso RPM risolve il problema osservato e lascia entrambe le installazioni intatte. Se è sicuro e immediato, conferma una sola volta che il vecchio Chrome/Flatpak mantiene il failure, senza modificare nulla.
7. Se anche l'RPM mostra `Native transport disconnected`, diagnostica SOLO il native messaging bridge pertinente: manifest `NativeMessagingHosts`, executable target, permessi/path e log direttamente correlati. Applica solo un fix locale minimo e reversibile se la causa è evidente; poi ritesta una volta. Non reinstallare ChatGPT, non migrare profili, non fare cleanup o audit di GNOME/Chrome/Fedora.
8. Non modificare repository Git: questo è un task di validazione/runtime locale.

# Acceptance
PASS solo se:
- è documentato se il Chrome iniziale era Flatpak, RPM o entrambi;
- Chrome RPM nativo è installato/disponibile e viene avviato tramite `/usr/bin/google-chrome-stable`;
- il Chrome Flatpak e il suo profilo restano intatti;
- l'estensione ChatGPT nel Chrome RPM stabilisce realmente il collegamento con ChatGPT Desktop e non mostra più `Native transport disconnected`;
- viene riportata la causa osservata in termini fattuali, senza inferenze non verificate.

Se serve un click/conferma/password non eseguibile da Codex, usa BLOCKED invece di simulare PASS.

# Stop
Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_result.py --repo ~/projects/codex-roadmap --prompt-id 628541 --result PASS --confirm-executed`

Dopo BLOCKED/FAIL usa lo stesso finalizzatore con l'esito reale. Output finale massimo 7 righe: RESULT, INITIAL_CHROME, RPM, CHATGPT_DESKTOP, NATIVE_BRIDGE, ROOT_CAUSE, NEXT_ACTION.
