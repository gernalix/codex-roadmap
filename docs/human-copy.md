# C2 human-facing copy

C2 keeps technical lifecycle data separate from presentation copy.

## Fields

### `human_title`
- Language: Italian.
- Purpose: instantly understandable to a non-programmer.
- Target length: 20–90 characters; hard maximum 120.
- One line; no trailing `...` or `…`.
- Prefer a concrete action/result: `Evita che…`, `Sistema…`, `Mostra…`, `Permetti…`.
- Omit IDs, function/class names, protocol jargon and internal acronyms unless essential to identify something the user already knows.
- Do not claim a cause or fix that is not supported by the source.

### `ai_title`
- Purpose: precise technical identity for AI/executors, search and deduplication.
- Target length: 30–160 characters; hard maximum 220.
- Preserve component names, relevant error names and technical distinctions.
- It may contain IDs only when identity would otherwise be ambiguous.
- It is not the default title shown to the user.

### `human_summary`
- Language: Italian.
- 1–3 short sentences.
- Target length: 60–300 characters; hard maximum 600.
- Explain what is wrong/change requested, the desired outcome, and why it matters when useful.
- No implementation dump, stack traces or raw IDs unless essential.
- Never invent missing facts.

## Ambiguous source fallback

If a safe human translation cannot be produced:
- `copy_status = needs_clarification`
- `human_title = "Chiarire: <area comprensibile>"`
- `ai_title` preserves the most precise source wording available.
- `human_summary` explicitly says which information is missing and why the task cannot be stated more specifically yet.

Do not hide ambiguity behind a confident simplified title.

## Presentation

Workflowy and other human UIs display `human_title` and `human_summary` first. `ai_title`, canonical IDs, technical objective, dependencies and executor metadata remain available in expanded technical details. Human titles are wrapped by the UI and are never shortened with ellipsis by C2.
