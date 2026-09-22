PROMPT_ID=613102
PARENT_PROMPT_ID=624831
PROJECT_ID=49
MODEL=GPT-5.6 Terra
REASONING=medium
MEGAVAULT_MODE=STANDARD

## Goal
Portare a PASS il lavoro fallito di 624831: PersonalHub deve avere un solo motore foto globale condiviso da People, Places e Soldi, senza pipeline legacy parallela in People.

## Starting point
Riutilizzare il lavoro già verificato di 624831: shared thumbnail/grid in :core:ui, integrazioni Soldi/Places, photo_uri Places e migration 18→19, Soldi lifecycle/search/gallery. Il gap è la pipeline People legacy e la prova UI Soldi Search/photos-only.

## Scope
Rimuovere picker/import/crop/bitmap/cache/path handling People duplicati; mantenere solo associazione Person ID, label e navigazione. Preservare senza conversione distruttiva tutte le foto People BLOB esistenti dietro l'astrazione globale. Rafforzare il contract/architecture test affinché People, Places e Soldi consumino la stessa capability. Verificare regressioni People mirate e il percorso reale Soldi Search → camera → photos-only su emulatore. Correggere soltanto failure in-scope.

## Safety
Nessun reset DB/device, nessuna perdita o duplicazione inutile di foto, nessun refactor estraneo. Square preview solo presentazione non distruttiva. Usare l'image loader esistente.

## Acceptance
People non possiede più un motore foto equivalente; vecchie e nuove foto People funzionano con persistenza/replace/remove e owner stabile; anti-duplication guard PASS; compile/test mirati People/shared/Soldi/Places PASS; Search e photos-only Soldi provati realmente su emulatore; commit, push, CI, integrazione e roadmap PASS completati. Il 624831 resta storicamente FAIL ed è collegato come corretto da questo prompt.
