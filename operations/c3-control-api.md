PROMPT_ID=425315

C3 user control API

`python3 tools/c3_api.py` binds only 127.0.0.1:8767. `GET /api/state` returns the canonical origin/main snapshot, progress, tags, state and user events. `POST /api/preview` accepts work_item_id/action and returns exact dependency/hierarchy impact and a precondition. `POST /api/override` requires that precondition, a unique request_id and, for cancel/delete, confirmed_affected matching the preview exactly. POST requires the exact loopback Host, matching Origin and X-C3-Intent: explicit-user.

Actions: pause, resume, stop, cancel, delete, force-priority (priority p0/p1/p2), move (zero-based sibling position). Delete is a history-preserving canonical tombstone. Pause gates dispatch through a canonical prerequisite tag and signals/verifies owned process cgroups. Stop/cancel release leases only after verified executor stop. Unknown/manual executor control fails closed.

The existing GitHub mutation writer remains the sole canonical writer, under its existing concurrency group. c3-user requests are handled first and committed individually, without the ordinary autonomous batch. The HTTP request returns success only after applied Issue, receipt and canonical event readback. It may take GitHub runner latency; timeout is an error, never an optimistic UI success. An already-running writer transaction still serializes correctly.

Process effects and remote Git cannot form a distributed ACID transaction. The protocol fails closed: pause/stop happens before mutation; failure leaves those executors safely interrupted and requires refreshed canonical evidence. Failed resume is re-paused. Explicit interruption never reports executor PASS. Retried completed request IDs read back the existing event without repeating effects.

Task bodies, model/reasoning and history remain canonical. Running-item order and uncontrolled manual execution are protected. Ordinary autonomous mutation authority and retired C2 daemons are unchanged.
