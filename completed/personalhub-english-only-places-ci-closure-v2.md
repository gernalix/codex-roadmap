PROMPT_ID=477616 | PARENT_PROMPT_ID=255970 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STANDARD

# Goal
Chiudi in un solo task English-only + diagnostica Places on-demand + CI mantenuta di PersonalHub. Non separare di nuovo UX e CI.

# Dependency contract
roadmap_start è l'unica autorità sulla readiness: se il claim di 477616 viene accettato, NON ricontrollare né attendere PROMPT_ID predecessori citati nello storico.

# Starting point
- repo: /home/daniele/projects/PersonalHub; usa il main corrente al momento del claim;
- CODE_MAP: places.root / places.checkin;
- oggi HomeScreen mostra CheckInDiagnosticsPanel inline quando esistono tentativi;
- esistono ancora values-it in più moduli;
- i gate mantenuti sono quelli già definiti nel repo/GitHub Actions.

# Esecuzione autonoma
1. Sincronizza main una volta, preservando dirty work non sovrapposto. Niente audit repo-wide.
2. Rendi l'inglese l'unica UI supportata per ora: rimuovi/disattiva le risorse/config di localizzazione italiana mantenute dal progetto; non toccare dati utente/test fixture dove l'italiano è contenuto semantico.
3. In Places non mostrare più la diagnostica inline: rendila accessibile solo da un controllo discreto on-demand. Mantieni filtri/copia/report esistenti.
4. Aggiorna solo test/stringhe direttamente coinvolti.
5. Leaf test Places + compile app, poi un solo smoke AVD per lingua e diagnostica.
6. Push e verifica i workflow mantenuti sul commit finale. CI pending/in-progress non è BLOCKED: attendi/continua lavoro utile; su failure correggi il failure concreto nello stesso task e riesegui solo il gate necessario.
7. Un solo bump versione se richiesto dalla policy corrente.

# Recovery / acceptance
Failure locali correggibili, lock orfani, helper difettosi, CI pending o remote advance non sono terminali: recupera e continua. BLOCKED solo per blocker esterno/safety non risolvibile.
PASS se UI mantenuta è English-only, diagnostica Places è on-demand, leaf+app+AVD PASS e required workflow finali sono verdi. Stop immediato dopo PASS.
Prima riga output: PROMPT_ID=477616
Seconda riga: RESULT=PASS|BLOCKED|FAIL
