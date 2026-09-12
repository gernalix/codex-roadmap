[[roadmap|Roadmap]] · [[spiegazioni|Spiegazioni]]

`PROMPT_ID=618472 | project_id=49 | model=GPT-5.5 | reasoning=medium | MegaVault=STANDARD`

> Esecuzione diretta. Non eseguire `roadmap_guard.py select` e non rileggere roadmap/README/spiegazioni. Questo task contiene solo lavoro che richiede ambiente locale/VM/segreti o verifica Gradle reale.

# Goal
Eliminare i colli di bottiglia di rilascio PersonalHub prima della campagna successiva: Telegram Local Bot API sulla VM Oracle, `telegram_notify` condiviso con endpoint configurabile, serializzazione reale dei task PersonalHub e verifica locale dei recenti fix del Registro. **Nessun bump versione, nessun final APK PersonalHub in questo task.**

# Fatti già verificati
- `vm_oracle` è il repository proprietario dell'infrastruttura; non creare un repo separato.
- Prima di lavorare sulla VM, **pullare `gernalix/vm_oracle`** e partire dal remoto corrente.
- MegaVault contiene `ai/personalhub-efficiency-recommendations.md`; usalo come decision record, senza rileggere altri documenti se non necessari.
- Telegram documenta per il Local Bot API in `--local`: upload fino a 2000 MB. Il passaggio cloud→local richiede `logOut` del bot.
- Il cloud Bot API da 50 MB ha causato rebuild debug→release→arm64→re-sign non desiderati. Dopo questo task il trasporto, non l'APK, deve risolvere la dimensione.
- PersonalHub `main` contiene già i fix Registro: payload completi solo per eventi reversibili, stale Undo persistito `CONFLICT`, app-version reale per gli update membri episodio e nuovi test regressione.

# A — Telegram Local Bot API sulla VM
1. Pull canonico `vm_oracle`; nessun lavoro su checkout stale.
2. Individua la sorgente/deployment canonica del package condiviso `telegram_notify` installato in `/usr/local/lib/python3.14/site-packages/telegram_notify`. Cerca solo nei repository/metadata direttamente pertinenti. Se non esiste sorgente tracciata, rendi `vm_oracle` la sorgente di deployment; **non creare un nuovo repository**.
3. Installa il server ufficiale `tdlib/telegram-bot-api` in modalità local con versione/pin riproducibile. Evita immagini third-party `latest`; preferisci sorgente/release ufficiale o artefatto pin verificabile.
4. Mantieni `api_id`, `api_hash`, bot token e destinazione fuori Git. Non stampare valori sensibili.
5. Usa il bind più ristretto compatibile con `telegram_notify`; niente endpoint pubblico non necessario.
6. Esegui la transizione ufficiale `logOut` cloud→local una sola volta quando necessario e verifica `getMe`/send.
7. Estendi `telegram_notify` con base URL configurabile, mantenendo compatibilità con gli attuali caller testo/documento e la destinazione condivisa esistente.
8. Acceptance trasporto: invio testo normale + file temporaneo >50 MB tramite endpoint locale; verifica API success, poi cancella il file. Non usare un APK PH come test.
9. Aggiungi health check/service docs minime in `vm_oracle` e aggiorna MegaVault operational metadata solo se le convenzioni correnti lo richiedono.

# B — serializzazione PersonalHub
Implementa il meccanismo locale minimo che impedisca a due task PersonalHub di entrare contemporaneamente in fase implementazione/QA/release. Deve avere:
- acquire atomico con `PROMPT_ID`/timestamp non sensibili;
- secondo acquire concorrente => BLOCKED chiaro, non attesa/polling;
- release esplicita su PASS/BLOCKED/FAIL;
- recupero sicuro di lock stale dimostrabile senza cancellare un lock vivo;
- integrazione/documentazione nel bootstrap operativo PersonalHub, non un daemon pesante.

Non creare un sistema distribuito o lock Git remoto se un lease locale affidabile basta per le sessioni Codex sulla stessa Fedora.

# C — verifica locale fix Registro già pushati
Sul PersonalHub remoto corrente esegui solo:
- compile `:core:database` + `:core:hub-context`;
- `HubActivityRegisterTest` e i test hub-context direttamente coinvolti dal costruttore/runtime;
- se un test/compile fallisce, fix minimo e push; niente nuova QA manuale del Registro se i test automatici provano il caso.

Verifica in particolare che `HubContextRepository` compili con `appVersion` iniettato e che non siano rimaste modifiche cosmetiche involontarie nel diff. Nessun bump `version.txt`.

# D — attivazione delle regole
Solo dopo A+B+C PASS, aggiorna il bootstrap PersonalHub remoto in MegaVault in modo coerente con il decision record:
- final artifact predefinito = signed debug `<version>.apk`, salvo requisito release esplicito;
- mai minify/split/post-process/re-sign solo per limiti Telegram;
- final artifact immutabile tra test, Pixel e Telegram;
- endpoint locale `telegram_notify` come trasporto condiviso;
- serializzazione task obbligatoria;
- fallimento delivery = BLOCKED, non rebuild alternativo.

# Stop
PASS solo se Local Bot API è realmente operativo sulla VM, `telegram_notify` invia >50 MB, lock concorrente è provato, test locali Registro passano e bootstrap remoto è aggiornato. Nessun APK finale, nessun Pixel main install.

Su PASS completa solo questo prompt:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 618472 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 618472`

`push_verified=git_push_exit_0` è terminale: niente status/fetch/rev-parse successivi sulla roadmap.

Output massimo 8 righe: RESULT, Local Bot API, >50MB test, notifier source/deploy, PH lock, Registro local tests, repo/SHA pushati, blocker.
