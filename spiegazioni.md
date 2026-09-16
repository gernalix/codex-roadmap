# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task vale la pena di essere fatto e cosa migliorerà concretamente**. I dettagli tecnici restano nei singoli prompt.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/fedora-kuma-inversion-preservation-runtime-validation]] | **Perché è importante:** il fix di `673914` dipende da `upside_down=1` su Fedora Storage. Il codice remoto ora preserva quel flag invece di azzerarlo durante `kuma-configure`; resta solo da provarlo sul runtime/Kuma reali e verificare tre cicli schedulati senza falsi heartbeat mancanti. | medium | Goal |
| 2 | [[prompts/fedora-filesystem-telegram-typeerror-runtime-fix]] | **Perché è importante:** durante `673914` la notifica Telegram per variazioni di spazio ha fallito con `TypeError`. Solo il runtime Fedora può mostrare la firma effettiva del modulo `telegram_notify` installato; il task corregge esattamente quel mismatch e prova una notifica reale. | low | Goal |
| 3 | [[prompts/fedora-user-systemd-partial-collector-fix]] | **Perché è importante:** i collector `minute`/`five_minute` risultano `partial` per un errore ricorrente nell'interrogazione dei servizi systemd utente. Il task corregge il contesto root/user senza smettere di monitorare le unità utente reali. | medium | Goal |
| 4 | [[prompts/personalhub-places-checkin-attempt-journal]] | **Perché è importante:** quando un check-in fallisce oggi manca la prova di cosa sia successo. Il task registra ogni tentativo e le candidate utili al debugging senza creare visite false. Nella stessa unica sessione emulator chiude anche il piccolo debito UI Hub/episodi con un test dedicato emulator-safe. GPT-5.5 Medium + STRICT basta perché schema e lifecycle sono già pre-localizzati. | medium | Goal |
| 5 | [[prompts/personalhub-random-timer-background-deadline]] | **Perché è importante:** il Random Timer deve completarsi e notificare anche con app non aperta. Riusa lo scheduler Android esistente e conclude la campagna con un solo build, un solo APK Pixel-tested e lo stesso identico artefatto consegnato. | medium | Goal |
| 6 | [[prompts/repository-publication-secret-audit]] | **Perché è importante:** prima di cambiare visibility bisogna controllare history, tree e workflow senza esporre secret nei log. Lo scan è batch/deterministico, quindi GPT-5.5 Medium è sufficiente; il task produce anche un handoff per la CI, ma la modifica dei workflow GitHub verrà fatta direttamente in chat e non consumerà quota Codex. | medium | Goal |
| 7 | [[prompts/personalhub-release-apk-minification]] | **Perché è importante:** la build `release` ha già R8 e resource shrinking; il task misura il guadagno reale, testa esattamente quell'APK sul Pixel e lo rende l'artefatto di consegna canonico senza rebuild inutili. | low | Goal |
