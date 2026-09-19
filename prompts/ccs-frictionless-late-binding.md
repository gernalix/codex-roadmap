PROMPT_ID=438216
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST
REPO=gernalix/chrome-codex-switcher

GOAL
Implementare late binding frictionless dei link Chrome e Codex per qualunque prompt dashboard, anche se il pairing iniziale è stato saltato.

ACCEPTANCE
- Pair missing links separato dal launch iniziale.
- Associa/Ricollega Chrome: auto-cattura se esiste un solo candidato sicuro; altrimenti capture mode e basta aprire la tab target.
- Associa/Ricollega Codex: tenta discovery automatica della sessione nativa tramite PROMPT_ID esatto; fallback a una sola azione Ctrl+Alt+L sulla chat target.
- Supporta anche Codex-first: binding parziale Codex e successivo Chrome completa il twin.
- Nessun guessing ambiguo o furto silenzioso di binding appartenenti ad altri prompt.
- API/extension backward compatible con /bind esistente.
- Test mirati + CI PASS.
