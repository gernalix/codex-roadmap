PROMPT_ID=436865

Implementa SOLO la strategia project-wide minima e durevole per risolvere MissingTranslation in PersonalHub.

Obiettivo:
- identifica perché l'introduzione di values-it nel lavoro Alerts ha fatto emergere MissingTranslation su stringhe default preesistenti;
- scegli il fix più semplice e corretto per il progetto (traduzioni, locale policy/lint config, o combinazione strettamente necessaria);
- applicalo senza refactor UI/feature estranei;
- preserva il comportamento delle feature e il Play preflight.

Acceptance:
- il failure MissingTranslation riprodotto non si verifica più sui controlli mirati;
- la strategia è coerente a livello progetto e non introduce falsi silenzi su errori utili;
- touched-module compile/lint mirati PASS;
- commit+push del lavoro verificato; report finale conciso.
