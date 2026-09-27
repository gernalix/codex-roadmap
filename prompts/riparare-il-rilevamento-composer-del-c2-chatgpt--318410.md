PROMPT_ID=318410

Correggi SOLO il rilevamento del composer corrente nel C2 ChatGPT browser executor.

Obiettivo:
- sostituisci/estendi i selettori obsoleti (#prompt-textarea, textarea[data-testid*=prompt], contenteditable[data-lexical-editor=true]) con una strategia robusta sulla UI corrente;
- preserva fail-closed e anti-duplicazione;
- copri delivery iniziale e recovery phase=starting;
- niente cambiamenti a scheduling/semantica C2 non necessari.

Acceptance:
- test/regressione riproduce il vecchio failure composer-not-found e passa col fix;
- delivery iniziale e recovery starting restano fail-closed/idempotenti;
- test mirati PASS;
- commit+push del fix verificato; report finale conciso.
