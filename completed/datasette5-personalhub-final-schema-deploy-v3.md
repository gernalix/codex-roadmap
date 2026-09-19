PROMPT_ID=489818 | PARENT_PROMPT_ID=904631 | project_id=10 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=STRICT

# Goal
Aggiorna la proiezione PersonalHub di datasette5 allo schema canonico finale (incluso Health) e distribuiscila sulla VM Oracle in modalità read-only sicura.

# Starting point
- repo locale datasette5: /home/daniele/projects/datasette5;
- main remoto verificato e CI green a e69fe799f9535c160f7df2bb5ca03267d1f55b65; accetta avanzamenti compatibili, non richiedere exact-head;
- projection/labels/tests esistono già: scripts/personalhub_projection.py, personalhub_labels.py, prepare_personalhub_replica.py, deploy/personalhub_schema.sql;
- non modificare l'app Android salvo che emerga un contratto realmente incompatibile.

# Esecuzione
1. Sincronizza main e usa i test esistenti come starting point; niente redesign.
2. Aggiorna projection/schema/label/FK/backlink solo per riflettere lo schema PH risultante da 462279, includendo Health e mantenendo le relazioni già supportate.
3. Esegui i test datasette5 mirati + CI locale pertinente.
4. Distribuisci sulla VM Oracle usando config/segreti canonici senza stamparli. Verifica replica/proiezione, Datasette start/restart e accesso HTTPS.
5. Verifica dall'esterno read-only: niente write endpoint utile, niente token esposti, relazioni/FK/backlink e Health navigabili.

# Acceptance
PASS con projection aggiornata, test PASS, servizio Oracle operativo e accesso read-only verificato sullo schema finale. Niente feature extra; stop dopo PASS.
