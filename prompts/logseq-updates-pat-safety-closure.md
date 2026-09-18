PROMPT_ID=255325 | parent_prompt_id=518264 | project_id=23 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Chiudi fail-closed la bonifica PAT/history di `gernalix/logseq_updates` e poi rendi l'aggiornamento di Logseq su Fedora x86_64 completamente unattended: trova live l'ultima build GitHub Actions corretta, scarica l'artifact Linux x64, installa atomicamente l'AppImage e invia Telegram sia sul successo sia su ogni fallimento reale.

# Starting point autoritativo
- target attuale: Fedora Linux x86_64; Logseq è già installato localmente come AppImage con launcher `.desktop`;
- NON toccare graph, dati utente, configurazioni Logseq o `~/.logseq`;
- repo `gernalix/logseq_updates` PRIVATE;
- `main` e `master` puntano a `712741b38ca41d090c14084d1859f23d35e9c728`; `master` è ancora default; nessun altro branch;
- finding noto: `github-pat` nella history, path `logseq_updates.bat`, commit abbreviato `41ff0d119e3c`; tree corrente già privo del PAT hardcoded;
- il codice attuale è Windows-centric: `logseq_updates.py` v1.3.8 cerca `logseq-win64-builds`, estrae MSI e usa `os.startfile`; BAT/XML Task Scheduler sono legacy;
- `last_logseq_build.json` è runtime state tracciato nel repo e nel nuovo design va spostato fuori da Git;
- upstream: `logseq/logseq`; l'artifact Linux x64 storicamente corretto è `logseq-linux-x64-builds`, ma run URL, artifact ID e signed URL NON vanno hardcodati;
- checkout canonici: `/home/daniele/projects/logseq_updates`, `/home/daniele/projects/MegaVault`, `/home/daniele/projects/codex-roadmap`;
- output MegaVault modificabili SOLO per `logseq_updates`: `ai/repository-publication-audit.json`, `ai/repository-ci-handoff.json`, `ai/repository-public-private-matrix.md`;
- helper rewrite: `/home/daniele/projects/codex-roadmap/tools/ensure_git_filter_repo.py`.
Non rileggere README/roadmap/spiegazioni/MEMORY e non fare inventory generale.

# Safety
Mai stampare secret/fingerprint/raw finding/header/token/replace-map. Artefatti sensibili solo in `/tmp` protetto. Rewrite solo su mirror fresco. Repo PRIVATE finché history+credential non sono safe. Nessun source build Logseq. Non killare Logseq: su Linux sostituisci atomicamente l'AppImage; il processo aperto può continuare sul vecchio inode. Mai toccare graph o `~/.logseq`.

# Fase A — PAT/history
1. Verifica in un solo preflight che `origin/main` e `origin/master` siano ancora allo SHA noto e che non esistano altri branch. Imposta default `main` con auth GitHub esistente, verifica una volta e poi elimina `master`. Failure => BLOCKED.
2. Esegui UNA volta `ensure_git_filter_repo.py`; parsea solo il JSON. Crea mirror fresco in `/tmp`, UNA gitleaks full-history/all-refs `--redact`, conferma programmaticamente il finding senza stamparlo.
3. Se il valore target è verificabile in-memory senza output, fai al massimo UNA verifica read-only e registra solo `credential_state=active|inactive|unknown`; `active|unknown` non è safe.
4. Riscrivi SOLO il secret target, verifica UNA volta gitleaks all-refs pulito + main/tag preservati, force-pusha main riscritto e tag necessari. Non ricreare master.
5. Da mirror fresco post-push fai UNA scansione gitleaks finale e verifica default/solo branch `main`. Se credential non è `inactive` o history non è clean => BLOCKED, cleanup e STOP.

# Fase B — updater Fedora autonomo
6. Preflight locale mirato: conferma Fedora x86_64 e ricava il path AppImage corrente dalla `Exec=` del launcher Logseq attivo; niente search globale. Ambiguità => BLOCKED.
7. Refactor minimo di `logseq_updates.py`:
   - scopri live e in modo bounded il workflow desktop corrente di `logseq/logseq` e la sua ultima run `completed/success`;
   - lista SOLO gli artifact di quella run; preferisci match esatto `logseq-linux-x64-builds`, fallback solo a un unico candidato inequivocabile Linux+x64; 0 o >1 => FAIL;
   - non hardcodare run/artifact/download URL; salva solo provenance stabile (run id/number, html_url, artifact id/name, SHA256 locale);
   - usa auth GitHub già presente sul Fedora host senza persistire/stampare secret;
   - scarica ZIP in temp, valida ZIP/path traversal, estrai esattamente una AppImage, SHA256, chmod executable;
   - installa sul path canonico stabile usando sibling temp + fsync + rename atomico; conserva il precedente solo fino al verify;
   - verifica il file reale con un probe AppImage non-GUI affidabile e che il launcher punti al path canonico; failure => rollback automatico + FAIL;
   - se serve, normalizza una sola volta solo `Exec=` al path stabile; preserva il resto del launcher;
   - non chiudere Logseq già aperto e non toccarne i dati.
8. Sposta stato in `~/.local/state/logseq-updater/state.json` con write atomico. Una build è “installed” SOLO dopo replace+verify. Failure resta ritentabile.
9. Telegram è contrattuale:
   - “nessuna build nuova” = no-op silenzioso;
   - ogni errore lookup/download/extract/install/verify => `Logseq update: FAIL` con stage, run/link se noto e testo sanificato;
   - install riuscita+verificata => `Logseq update: SUCCESS` con run/build;
   - se install riesce ma SUCCESS Telegram fallisce, non reinstallare: salva `notification_pending` e ritenta solo la notifica al run successivo;
   - notifier assente/config invalida è failure, mai silenzioso.
10. Solo dopo nuovo flusso verificato rimuovi dal tree il legacy Windows (BAT, XML, MSI/`os.startfile`) e `last_logseq_build.json` tracciato.
11. Test mirati senza framework superflui: latest-run/artifact; ambiguità fail-closed; zip safety; state post-verify; rollback; SUCCESS/FAIL notifier; retry `notification_pending`; no-op senza notifica.
12. Installa `systemd --user` service+timer: nessuna shell interattiva, `Persistent=true`, cadenza circa oraria, no polling interno; riusa lingering già presente e abilitalo solo se necessario.
13. Gate economici prima. Poi UN live E2E: lookup latest successful, download artifact Linux x64, replace/install latest AppImage (consenti un singolo `--reinstall-latest` solo per validare lo stesso build), verify file+launcher, reale Telegram SUCCESS, timer enabled/active e una service invocation exit 0. Il path FAIL va provato con mock/fault injection senza falso allarme Telegram reale.
14. Se un gate live fallisce, correggi solo quel failure domain e rilancia il leaf gate. Niente audit aggiuntivi.

# MegaVault + publish
15. Con history pulita e credential inactive, aggiorna SOLO le tre entry MegaVault indicate con default branch, gitleaks e decisione di pubblicabilità coerente; parse JSON + `git diff --check`; un solo commit/push MegaVault.
16. Riconcilia il checkout canonico `logseq_updates`, committa/pusha il nuovo updater su `main`; sul remoto deve restare solo `main`. Poi helper rewrite `--cleanup` una sola volta e rimuovi temp.

# Acceptance
PASS solo se: PAT mai esposto; history gitleaks-clean; credential inactive; solo/default main; latest build risolta live senza URL/ID hardcodati; artifact Linux x64 reale scaricato; AppImage installata atomicamente e verificata senza toccare graph/config; rollback/state retriable testati; runtime state fuori repo; legacy Windows rimosso; systemd timer enabled/active; success update produce Telegram SUCCESS post-verify; failure path tenta Telegram FAIL; MegaVault coerente.

# Non-goal
Niente source build, upgrade altri software, CI generale, audit altri repo, secondo scanner, refactor cosmetici, Uptime Kuma, modifica graph/config Logseq o cleanup non correlato.

# Stop
Dopo PASS esegui una sola volta:
`python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 255325 --confirm-executed`
Se BLOCKED/FAIL non finalizzare. Output finale max 9 righe: RESULT, BRANCHES, HISTORY, CREDENTIAL_STATE, UPSTREAM_BUILD, INSTALL, SYSTEMD, TELEGRAM, BLOCKER.
