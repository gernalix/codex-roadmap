# C3 Control Web App

Open http://127.0.0.1:8767/ in the existing browser. The enabled user unit
`c3-web.service` runs the merged canonical implementation and builds its static
production assets at startup. `systemctl --user status c3-web.service` is the
operational readback; `/api/health` verifies the canonical source is readable.

The primary view shows canonical root batches with progress, state and priority.
Expand Details for tasks and operational controls. Unparented leaf tasks are
explicitly grouped as Independent tasks, a projection without a canonical batch
identity; no membership is inferred from names. Finished items are optional.

Pause, resume, stop, cancel, delete, priority and drag/keyboard move use the same
canonical API. A constrained move reports exact prerequisites. Cancel/delete
require confirmation of every affected canonical ID. Delete preserves history.
The UI refreshes after applied receipts and every ten seconds while visible.
Unknown executor ownership fails closed. Running execution metadata stays
protected. Source/writer failures remain visible; they never become optimistic
successes. GitHub runner latency and the active writer transaction can delay the
synchronous response; user intent commits independently of the ordinary drain.

Validation: 593 Python tests (host chat suspension isolated only in the test
harness), 5 Node frontend tests, production build, actual systemd process
pause/resume/stop, HTTP integration with the real mutation parser, and real
Chrome over production data. Live UI pause/resume generated canonical events;
the C3 batch was restored to pending/P0. Destructive confirmation was inspected
without deleting production data. Browser loading, empty/source-error recovery,
canonical detail data and clean console were verified. API prerequisite 425315
has its applied PASS receipt; implementation PRs #7740 and #7786 are merged.
