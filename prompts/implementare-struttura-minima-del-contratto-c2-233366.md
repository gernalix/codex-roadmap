PROMPT_ID=233366

# Goal
Creare C2_EXECUTOR_CONTRACT.md con soli blocchi normativi brevi: 0 Scope+precedenza; 1 READ/source of truth; 2 WRITE/single writer; 3 CLAIM+EXECUTE/worktree+resource ownership; 4 CHECKPOINT+RECOVER; 5 DISCOVERIES/bug-bottleneck intake; 6 FINISH+stop conditions; 7 INVARIANTS/ID+metadata; chiusura con micro-tabella 'need -> action'. Niente rationale narrativo.

# Canonical starting point
- C2 work item: wi:fee4d11db6b34cf8808e78bb760af63c
- Repository: gernalix/codex-roadmap
- The work item scope and acceptance below are authoritative. Inspect only files needed to satisfy them.
- Use the assigned isolated worktree and the repository single-writer/integration path. Do not edit canonical branches directly.
- Do not broaden scope into unrelated cleanup, refactors or audits.

# First bounded action
Implement the compact canonical contract and replace duplicated common rules in existing docs with references.

# Acceptance
- Le 8 sezioni esistono nell'ordine definito.
- Ogni regola normativa usa forma imperativa compatta e univoca.
- Il testo base è executor-agnostic; dettagli Codex/UI restano fuori dal contratto comune.
- La micro-tabella copre leggere stato, mutare C2, iniziare, checkpoint, registrare scoperta e terminare.
- Zero duplicazioni interne.

# Execution rules
- Fix only failures necessary for this goal; preserve unrelated local/runtime state.
- Use targeted tests first and widen only if evidence requires it.
- On incidental C2 bugs/bottlenecks, capture only the description to the C2 Inbox and continue.
- Stop immediately when acceptance is verified; do not wait on CI/merge in a model turn.
