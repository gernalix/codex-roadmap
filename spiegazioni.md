# Spiegazioni della roadmap

[[README|README]] · [[roadmap|Roadmap]]

Qui trovi, in parole semplici, **perché ogni task richiede ancora Codex e se conviene lanciarlo come Prompt normale oppure Goal**. Tutto ciò che era correggibile direttamente sul remoto è stato tolto dalla coda.

L'ordine minimizza dipendenze e lavoro duplicato: prima aggiorna la pipeline `codex-usage` che osserverà i run successivi; poi chiude il rischio PAT di Logseq che può cambiare i metadata di pubblicabilità; quindi esegue i due gate Fedora indipendenti; il refactor MegaVault precede il consolidamento CI globale, che resta ultimo così lavora sui repository nello stato finale.

|   # | Prompt | Spiegazioni | Livello ragionamento | Tipo prompt |
| --: | ------ | ----------- | -------------------- | ----------- |
| 1 | [[prompts/codex-usage-publisher-cycle-path-deploy]] | I fix remoti sono già implementati e testati: path cycle-aware, parser degli stati terminali con `FIXED` e analisi prompt continuation-safe. Va eseguito per primo perché rende più affidabile pubblicazione e analisi dei successivi run Codex. Codex serve solo per deploy Fedora, un singolo backfill/push del repo privato `codex-usage` e verifica dei casi `583214` e `742615`. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 2 | [[prompts/logseq-updates-pat-safety-closure]] | Il PAT è già rimosso dal tree corrente, ma resta nella history. Questo task viene prima della CI globale perché può aggiornare lo stato di pubblicabilità/visibility consumato dal consolidamento finale. Richiede ambiente Git autenticato locale per rewrite, gitleaks all-refs e verifica credential senza esporre il secret. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 3 | [[prompts/adb-device-keeper-canonicalize]] | Sorgente canonica, test, CI, deploy helper e rimozione WhatsApp sono già completati sul remoto. Resta solo Fedora reale: sync, deploy, user-systemd e un unico disconnect/reconnect Pixel 8a via Tailscale. È indipendente dai task 1-2 ma viene dopo la chiusura del rischio PAT. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 4 | [[prompts/fedora-runtime-validation]] | `847392` ha già verificato user-systemd e Telegram e i gap CI/deploy sono corretti sul remoto. Resta solo deploy live, sessione Chrome canonica e readback Kuma #39/#40 + inversione Storage. Nessuna nuova implementazione. **Prompt**, GPT-5.5/low + FAST. | low | Prompt |
| 5 | [[prompts/megavault-internal-capsule-boundaries]] | L'anti-pattern è ancora presente (`import *`, re-export via `globals()` e monkey-patching). Il refactor deve preservare il comportamento sul DB canonico. Viene subito prima del task CI globale così quest'ultimo valuta MegaVault nella struttura definitiva e non deve riaprire il repo dopo. **Prompt**, GPT-5.6 Sol/medium + STRICT. | medium | Prompt |
| 6 | [[prompts/retained-repositories-github-ci-completion]] | Consolidamento finale: usa l'handoff MegaVault aggiornato e completa GitHub Actions sui repo mantenuti, incluso il nuovo `adb-device-keeper`. Deve restare ultimo per evitare di configurare CI e poi modificare nuovamente gli stessi repository nei task precedenti. **Goal**, GPT-5.5/medium + STANDARD. | medium | Goal |
