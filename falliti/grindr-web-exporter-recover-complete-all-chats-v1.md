PROMPT_ID=285894 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD
WORKDIR=/home/daniele/projects

# Goal
Recupera il vecchio progetto locale `grindr-web-exporter` dal backup T7 se esiste; se non esiste, ricostruiscilo dalle fonti storiche già note. Poi rendilo capace di esportare automaticamente TUTTE le chat Grindr Web: enumerazione completa delle conversazioni, per ogni chat scroll fino al primo messaggio, scraping ordinato top→bottom fino al più recente, checkpoint/resume e deduplica. Mantieni il progetto locale/privato; non creare un remote pubblico.

# Stato iniziale autoritativo
- Il Samsung T7 è fisicamente connesso ma NON montato.
- Identità T7 canonica: `/dev/disk/by-id/usb-Samsung_PSSD_T7_Shield_S6YGNS0Y903440H-0:0-part1`, UUID `4c75ac03-4c73-43f8-afd9-f90db49a74fc`, mountpoint `/mnt/T7_BACKUP`, Restic repo `/mnt/T7_BACKUP/restic-fedora`.
- Backup tooling: `~/projects/fedora-t7-backup`; runtime `/usr/local/libexec/t7-restic-backup`. Riusa il credential boundary systemd esistente; non leggere/stampare/copiare password o token.
- Vecchio root: `/home/daniele/codex-workspace/grindr-web-exporter`; prompt storico `739418`; era Python+Playwright, SQLite WAL, CLI `scan-chats|export-one|export-all|resume|export-html|export-json|status`, con tabelle chats/messages/media/dom_snapshots/progress_checkpoints/export_runs e deduplica.
- Fonte storica MegaVault: commit `6c6d917ed24b25595903bef2d0339ffb2327005d`, file `ai/projects/grindr-web-exporter.md`.
- Già verificato senza risultati: ZIP repo ritirati, vecchi bundle MegaVault e normali path di progetto. NON ripetere queste ricerche.
- Artefatti locali rimasti: `/home/daniele/Documents/ChatGPT/Scraping/GRINDR_EXPORT_MINIPROMPT.md` e `/home/daniele/Documents/ChatGPT/Scraping/grindr_dom_archive.py`. Parti da questi file e riusa il parser già validato invece di riscriverlo senza motivo.
- Python: ambiente globale; venv/virtualenv/poetry/uv vietati.

# Esecuzione
1. Esegui `roadmap_start` per 285894.
2. Verifica l'identità del T7 prima del mount. Montalo su `/mnt/T7_BACKUP` in modalità read-only quando compatibile con Restic; nessun format/fsck/scrittura al backup. Per letture Restic usa il meccanismo più sicuro disponibile (es. no-lock/read-only) e il credential boundary esistente. Se il comando diretto non eredita `CREDENTIALS_DIRECTORY`, usa l'unit/systemd tooling esistente o un equivalente minimo che riusi la stessa credenziale: NON creare un file password ad hoc.
3. Cerca in TUTTI gli snapshot Restic, in modo mirato, il path storico `/home/daniele/codex-workspace/grindr-web-exporter` e riferimenti `grindr-web-exporter|739418`. Non fare restore massivi. Se trovi più versioni, scegli la più recente completa prima della rimozione e documenta snapshot+timestamp.
4. Se trovato, ripristina il progetto in una directory di staging senza sovrascrivere nulla e preserva `.git`/history se presenti. Se non trovato, NON bloccare: ricostruisci il progetto minimo usando MegaVault storico + `GRINDR_EXPORT_MINIPROMPT.md` + `grindr_dom_archive.py`.
5. Materializza il progetto operativo in `/home/daniele/projects/grindr-web-exporter`. Preserva una copia read-only/staging dell'eventuale restore originale finché il nuovo progetto è verificato. Riusa la vecchia identità MegaVault se esiste; non creare un project_id duplicato.
6. Implementa il flusso automatico:
   - scansiona/scrolla la lista chat fino a convergenza e raccoglie tutte le conversazioni senza duplicati;
   - apre una chat e risale fino al vero inizio usando convergenza (limite superiore + nessun nuovo messaggio/load per cicli consecutivi), non un numero fisso di scroll;
   - dal top scende con finestre sovrapposte, aspetta lazy-loading/mutation, estrae e deduplica i messaggi visibili e salva checkpoint persistenti;
   - termina solo al vero fondo (near-bottom + nessun nuovo messaggio per cicli consecutivi), quindi passa alla chat successiva;
   - gestisce DOM virtualizzato senza assumere che tutta la cronologia sia contemporaneamente nel DOM;
   - `resume` riparte dalla chat/posizione sicura dopo crash/restart senza duplicare dati;
   - conserva ordine, timestamp/direzione/tipo/reply quando disponibili e gli output esistenti SQLite/JSON/HTML; preserva gli output aggiuntivi del parser corrente se già funzionanti.
7. Preferisci Chrome/Chromium perché il parser più recente è stato validato lì. Riusa una sessione Grindr già autenticata se controllabile senza esportare credenziali. Se serve login manuale, implementa prima tutto ciò che è possibile e termina BLOCKED solo quando il login è l'unico blocker reale; niente bypass anti-bot o protezioni.
8. Aggiungi test mirati per: enumerazione sidebar con lazy-load, rilevazione top/bottom, DOM virtualizzato/overlap, deduplica, resume/checkpoint e ordinamento. Usa fixture DOM sanificate, senza messaggi reali in Git.
9. Se esiste una sessione autenticata, esegui un smoke test reale su almeno una chat lunga dimostrando top→bottom e poi una scansione `export-all` limitata alla discovery delle chat; non è necessario attendere ore per esportare l'intero account nel gate di test. Nessun contenuto reale deve finire in Git/log/report.
10. Aggiorna documentazione tecnica minima e MegaVault con path/stato corrente del progetto. Commit locale del progetto recuperato/ricostruito; nessun remote nuovo salvo che ne esista già uno canonico e privato.

# Acceptance
PASS solo se: ricerca Restic completata; progetto recuperato o ricostruito; `export-all` può autonomamente enumerare tutte le chat e percorrere ogni conversazione top→bottom con convergenza, deduplica e resume; test mirati PASS; dati/credenziali/contenuto Grindr non sono committati; identità MegaVault non è duplicata. Se manca solo l'autenticazione reale dopo implementazione+test, BLOCKED con un'unica azione manuale precisa richiesta.

# Non-goal
Niente refactor generale, nuova dashboard, nuovo servizio sempre-on, pubblicazione del repo, bypass di protezioni Grindr o modifica del backup Restic.

# Report
Massimo 8 righe: RESULT, T7_MOUNT, RESTIC_RECOVERY, PROJECT_PATH, IMPLEMENTATION, TESTS, REAL_VALIDATION, BLOCKER.
