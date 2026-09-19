PROMPT_ID=697834 | PARENT_PROMPT_ID=830867 | project_id=49 | model=GPT-5.6 Sol | reasoning=medium | MegaVault=STRICT

# Goal
Porta i veri timestamp/istanti persistiti di PersonalHub a INTEGER epoch milliseconds con una migrazione lossless, usando lo scanner esistente come gate corretto invece di migrare falsi positivi.

# Starting point
- repo: /home/daniele/projects/PersonalHub;
- Room schema corrente verificato: v15;
- HubTimestamp e tools/check_timestamp_contract.py esistono;
- lo scanner corrente è troppo largo: può classificare lat e metriche/durate *_ms come timestamp;
- non convertire date-only, coordinate, durate, reaction/inter-key metrics o altri numeri non-istante.

# Esecuzione
1. Correggi in modo mirato check_timestamp_contract.py affinché identifichi solo colonne che rappresentano istanti temporali. Aggiungi test minimi per falsi positivi noti.
2. Esegui lo scanner corretto sul latest schema e usa quell'output come lista di lavoro; niente grep globale alternativo salvo evidenza mancante.
3. Migra solo le vere colonne istante non-INTEGER a epoch ms. Preserva NULL, ordinamento e significato; parse fail-closed con test su formati legacy realmente presenti.
4. Aggiorna Room entities/DAO/query/formatting e schema export solo dove necessario. Una sola nuova versione DB rispetto alla base corrente.
5. Migration test dalla schema reale precedente + quick_check/FK + scanner zero violations + leaf compile/test; poi app compile. AVD solo se serve a dimostrare la migrazione reale.

# Acceptance
PASS con scanner corretto senza falsi positivi noti, zero violazioni reali, migrazione lossless testata dalla versione precedente, quick_check/FK PASS e nessuna semantica data/durata alterata. Niente refactor collaterali; stop dopo PASS.
