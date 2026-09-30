#!/usr/bin/env python3
"""Use the existing native Inbox fallback after the ordinary worker gates."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home()/'.local/share/c2-supervisor/worktree/tools'))
import c2_worker
# This entrypoint is selected only for the canonical issue-triage tag.
c2_worker.lane_degraded = lambda: True
raise SystemExit(c2_worker.main())
