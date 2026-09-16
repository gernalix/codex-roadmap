PROMPT_ID=615438 | project_id=15 | model=GPT-5.5 | reasoning=medium | MegaVault=FAST

# Goal

Elimina alla radice il ricorrente `user systemd: command exited with status 1` che rende `partial` i collector Fedora `minute`/`five_minute`, senza silenziare veri failure di servizi utente né fare discovery generale.

# Starting point autoritativo

- repo: `/home/daniele/projects/fedora-system-monitor`, MegaVault project `15`;
- durante `PROMPT_ID=673914` run reali `minute` e `five_minute` completavano con metriche valide ma `outcome=partial` e unico errore ricorrente `user systemd: command exited with status 1`;
- il collector gira come root via `fedora-system-monitor-collect@.service`; la configurazione servizi include almeno un'unità utente (`user:codex-session-archive.service`), quindi non basta ignorare `systemctl --user`;
- parti esclusivamente dal ramo servizi nei collector (`src/fedora_system_monitor/capsules/collectors/periodic.py` e collaboratori diretti) e dai test già relativi ai service collector.

Prompt autosufficiente: niente README/roadmap/MEMORY/MegaVault, inventory repo-wide o audit systemd globale.

# Esecuzione minima

1. Fotografia Git + `pull --ff-only` se pulito. Nessun commit intermedio.
2. Individua il comando esatto già usato dal collector per interrogare systemd utente leggendo solo il simbolo pertinente.
3. Riproduci **una sola volta** il comando nel contesto effettivo del service/root e **una sola volta** nel contesto utente `daniele`, con output/exit code limitati. Determina se manca user bus/runtime env, se l'unità è realmente assente/failed o se il comando è costruito male.
4. Applica il fix minimo che consenta al collector root di osservare correttamente i servizi utente configurati. Non trasformare indisponibilità reali in `ok` e non rimuovere l'unità dalla configurazione per far sparire l'errore.
5. Aggiungi/aggiorna solo i test del leaf servizi necessari a bloccare la regressione. Esegui una volta il test target; failure => una sola correzione basata sulla failure + riconferma.
6. Dopo test PASS: commit/push una volta e `sudo scripts/deploy-runtime.sh`.
7. Usa **un solo verifier bounded** sul timer reale e termina appena 3 run `minute` consecutivi risultano `ok` oppure `partial` per un motivo diverso e concretamente reale. L'errore `user systemd: command exited with status 1` non deve più comparire.

# Acceptance

PASS se la causa è identificata, i servizi utente restano realmente monitorati, test mirato PASS, runtime aggiornato e 3 run schedulati consecutivi non producono più il falso errore user-systemd.

# Non-goal

Niente fix storage/Kuma/Telegram, modifiche alle unità utente non necessarie, aggiornamenti di sistema, refactor collector o suite globale.

# Stop

Dopo PASS:
`python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 615438 --dry-run && python3 ~/projects/codex-roadmap/tools/roadmap_guard.py --repo ~/projects/codex-roadmap complete --prompt-id 615438`

Output massimo 5 righe: `RESULT`, `ROOT_CAUSE`, `FIX`, `THREE_RUNS`, `PUSH/BLOCKER`.
