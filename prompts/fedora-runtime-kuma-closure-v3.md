PROMPT_ID=542078 | PARENT_PROMPT_ID=526713 | project_id=15 | model=GPT-5.6 Luna | reasoning=low | MegaVault=FAST

# Goal
Chiudi soltanto il gate Kuma del monitor Fedora dopo che l'utente ha rifatto login nel profilo Chrome canonico. Non ripetere deploy/test già conclusi.

# Starting point
- repo: /home/daniele/projects/fedora-system-monitor;
- baseline 46235552ee292c96f6e4b00de39db2e520493b32 deve essere antenata; CI già green;
- profilo ammesso: /home/daniele/.var/app/com.google.Chrome/config/google-chrome;
- attesi: monitor #39=180/60; #40=480/180, upside_down=1; config locale inverted_categories=["storage"].

# Esecuzione
1. Sync non distruttivo e verifica solo che la baseline sia antenata; niente redeploy.
2. Una sola esecuzione bounded di fedora-system-monitor kuma-configure col profilo Chrome canonico.
3. Se login ancora stale/rifiutato => BLOCKED immediato; nessun altro profilo/token/retry identico.
4. Se riesce, un readback autenticato limitato a #39/#40 e una lettura mirata della config locale.
5. Correggi solo mismatch tecnico concreto nello stesso dominio e verifica una volta.

# Acceptance
PASS con checkout sync, kuma-configure exit 0, #39/#40 esatti e storage inversion preservata. Niente suite test/CI/deploy/README/MegaVault. Stop dopo PASS.
