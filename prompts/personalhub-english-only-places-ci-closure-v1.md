PROMPT_ID=255970 | PARENT_PROMPT_ID=609279 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Dopo 521404 PASS, chiudi in un solo task English-only + diagnostica Places on-demand + CI mantenuta di PersonalHub. Non separare di nuovo UX e CI.

# Starting point
- repo: /home/daniele/projects/PersonalHub; usa main corrente dopo 521404;
- CODE_MAP: places.root / places.checkin;
- oggi HomeScreen mostra CheckInDiagnosticsPanel inline quando esistono tentativi;
- esistono ancora values-it in più moduli;
- i gate mantenuti sono quelli già definiti nel repo/GitHub Actions.

# Esecuzione
1. Sincronizza main una volta, preservando dirty work. Niente audit repo-wide.
2. Rendi l'inglese l'unica UI supportata per ora: rimuovi risorse/config di localizzazione italiana mantenute dal progetto; non toccare dati utente/test fixture dove l'italiano è contenuto semantico.
3. In Places non mostrare più la diagnostica inline: rendila accessibile solo da un controllo discreto on-demand. Mantieni filtri/copia/report già implementati.
4. Aggiorna solo test/stringhe direttamente coinvolti.
5. Esegui leaf test Places + compile app. Poi un solo smoke AVD necessario per lingua e diagnostica.
6. Push e verifica solo i workflow GitHub mantenuti sul commit finale. Se uno fallisce, correggi il failure concreto nello stesso task e riesegui solo il gate necessario; niente audit CI generale.

# Acceptance
PASS se UI mantenuta è English-only, diagnostica Places non occupa la home finché non richiesta, leaf+app+AVD PASS e i workflow mantenuti del commit finale sono verdi. Un solo bump versione se richiesto dalla policy corrente. Stop immediato dopo PASS.
