PROMPT_ID=485236
PROJECT=Facilitatori di prompt
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT=FAST

GOAL
Aggiungi a chrome-codex-switcher un late-binding flow non distruttivo per completare in seguito i link Chrome e Codex di un PROMPT_ID.

UX
- un'azione dashboard 🔗 Collega avvia il recovery flow;
- se manca Chrome, cattura automaticamente la prossima tab chatgpt.com/c/* o chatgpt.com/g/* che l'utente attiva;
- dopo la cattura Chrome, se manca Codex arma il PROMPT_ID e chiede solo di aprire la chat Codex corretta e premere Ctrl+Alt+L;
- se Chrome è già associato, salta direttamente al passo Codex;
- se Codex è già associato, la cattura Chrome completa il binding senza chiedere altro;
- non sovrascrivere un binding già completo e non indovinare tab/thread ambigui;
- il capture mode scade automaticamente ed è persistente abbastanza da sopravvivere al cambio tab.

ACCEPTANCE
- prompt senza link: click 🔗 Collega → attiva tab ChatGPT corretta → Ctrl+Alt+L nella chat Codex corretta → binding completo;
- prompt parziale: vengono richiesti solo i lati mancanti;
- nessun overwrite silenzioso di binding completo;
- stato/istruzioni chiare via flash nella UI;
- test/syntax/CI PASS.