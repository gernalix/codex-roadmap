PROMPT_ID=404846 | PARENT_PROMPT_ID=962109 | project_id=49 | model=GPT-5.6 Terra | reasoning=medium | MegaVault=FAST
Codex Desktop project: Personal Hub

# Goal
Chiudi tutti i workflow GitHub Actions mantenuti di PersonalHub dopo il completamento di PROMPT_ID=609279. Questo prompt sostituisce 962109 perché la policy è cambiata: PersonalHub è temporaneamente English-only e NON vanno aggiunte/mantenute traduzioni italiane per soddisfare lint.

# Starting point
- workdir: /home/daniele/projects/PersonalHub;
- branch finale: main;
- 609279 deve essere completed/PASS prima di iniziare;
- usa i run GitHub più recenti non superseded come autorità;
- il vecchio 962109 citava:
  - FinanceCapsuleTest.versionThreeUpgradeKeepsExistingRowsAndCreatesOnlyEmptyFinanceTables;
  - :app:lintPlay MissingTranslation per module_salute/module_salute_subtitle in values-it;
  - Android instrumentation CI da verificare.
Queste informazioni sono solo starting point storico: non aggiungere stringhe italiane. Se 609279 ha eliminato quel failure, consideralo chiuso.

# Scope
- Porta a PASS solo i workflow mantenuti: Android unit CI, Android instrumentation CI, Play Store preflight, Architecture boundaries, Salute module.
- Parti dal primo failure reale del run più recente e correggi solo quel failure domain.
- Puoi modificare codice/test/build logic/workflow direttamente necessari.
- Per qualunque problema di localizzazione, preserva la policy English-only introdotta da 609279; non ricreare values-it e non aggiungere traduzioni italiane.
- Non disabilitare test, non creare baseline/soppressioni generiche solo per ottenere verde.
- Niente refactor, cleanup, upgrade dipendenze o feature non necessarie.
- Niente device fisici; se serve riprodurre instrumentation usa solo emulatore.

# Esecuzione token-efficient
1. Un solo preflight Git e sync non distruttivo di main.
2. Controlla i run più recenti; non reinvestigare failure già risolti.
3. Esegui test locali mirati solo quando servono a riprodurre/correggere un failure.
4. Nessun retry identico senza nuova evidenza.
5. Push per batch coerente; usa i nuovi run GitHub come acceptance finale.
6. Se un branch temporaneo è necessario, mergialo appena verde e cancellalo. Stato finale: solo main per questo lavoro.

# Acceptance
PASS solo quando, sul commit finale di main:
- Android unit CI = success;
- Android instrumentation CI = success;
- Play Store preflight = success;
- Architecture boundaries = success;
- Salute module = success;
- English-only resta rispettato e nessuna traduzione italiana è stata reintrodotta;
- git status locale pulito e main sincronizzato con origin/main.

Finalizza:
python3 ~/projects/codex-roadmap/tools/roadmap_finish.py --repo ~/projects/codex-roadmap --prompt-id 404846 --confirm-executed

BLOCKED/FAIL via roadmap_result. Output max 6 righe: RESULT, HEAD, UNIT, INSTRUMENTATION, PLAY_AND_OTHER_CI, BLOCKER.
