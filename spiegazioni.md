# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task vale la pena di essere fatto e cosa migliorerà concretamente**. I dettagli tecnici restano nei singoli prompt.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/personalhub-checkin-diagnostics-acceptance-closure]] | **Perché è importante:** l'audit di `893806` ha scoperto che il PASS era troppo ottimistico: mancano ancora i filtri outcome/luogo e i dettagli candidate richiesti, e la FK `ON DELETE CASCADE` può cancellare evidenza diagnostica storica quando un luogo viene eliminato. Il task chiude esattamente questi requisiti con migration Room 14→15 e una sola sessione emulator. | medium | Prompt |
| 2 | [[prompts/fedora-kuma-inversion-preservation-runtime-validation]] | **Perché è importante:** `936251` ha confermato il fix `upside_down` e distribuito il runtime, ma si è bloccato perché la CLI recuperava una sessione Chrome rifiutata da Kuma. Il codice remoto ora legge anche il WAL LevelDB `*.log`, dove può trovarsi il JWT più recente. Resta solo la prova sul Fedora/Kuma reali; il task elimina esplorazione Oracle/browser inutile e non aspetta più tre cicli da ~24 minuti complessivi, non pertinenti a questo difetto. | low | Prompt |
| 3 | [[prompts/fedora-filesystem-telegram-typeerror-runtime-fix]] | **Perché è importante:** durante `673914` la notifica Telegram per variazioni di spazio ha fallito con `TypeError`. Solo il runtime Fedora può mostrare la firma effettiva del modulo `telegram_notify` installato; il task corregge esattamente quel mismatch e prova una notifica reale. | low | Prompt |
| 4 | [[prompts/fedora-user-systemd-partial-collector-fix]] | **Perché è importante:** i collector `minute`/`five_minute` risultano `partial` per un errore ricorrente nell'interrogazione dei servizi systemd utente. Il task corregge il contesto root/user senza smettere di monitorare le unità utente reali. | medium | Prompt |
| 5 | [[prompts/personalhub-random-timer-background-deadline]] | **Perché è importante:** il Random Timer deve completarsi e notificare anche con app non aperta. Riusa lo scheduler Android esistente e conclude la campagna con un solo build, un solo APK Pixel-tested e lo stesso identico artefatto consegnato. | medium | Goal |
| 6 | [[prompts/personalhub-release-apk-minification]] | **Perché è importante:** la build `release` ha già R8 e resource shrinking; il task misura il guadagno reale, testa esattamente quell'APK sul Pixel e lo rende l'artefatto di consegna canonico senza rebuild inutili. | low | Goal |
