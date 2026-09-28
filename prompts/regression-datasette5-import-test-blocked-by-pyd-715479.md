PROMPT_ID=715479

Resolve only the Datasette5 regression that blocks the Phase C verification: the documented test/import environment reports pydantic-core 2.49.0 while the installed pydantic requires 2.46.5, preventing tests that import datasette.app.

Scope and stopping rules:
- Work only in the canonical gernalix/datasette5 task worktree allocated for this item.
- Reproduce the mismatch using the repository's current documented test environment; distinguish repo dependency/config drift from a stale local environment.
- Apply the smallest repository-owned fix needed. Do not modify shared/global Python packages unless repository policy explicitly requires it. Do not broadly upgrade dependencies or refactor unrelated code.
- Run only the minimal import/test gate proving datasette.app can import and the affected Phase C test can proceed.
- If the repository already encodes the correct environment and the failure is purely external/stale, make no artificial code change; record exact evidence and the minimal remediation.
- Commit and push any real repository change to the task branch. Stop immediately once the regression acceptance is proven.

Final response must contain:
RESULT=PASS|BLOCKED|FAIL|CANCELLED
C2_RESULT={"completed":[],"remaining":[],"evidence":[],"blocker":null,"next_action":null,"summary":"..."}
