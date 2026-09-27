#!/usr/bin/env python3
"""Submit audited pending Inbox edits or voids through the fenced C2 writer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import uuid

import c2_control
from c2_workflowy_order import load_runtime_identity


ALLOWED = {"description", "repo", "code_location", "executor_ref", "chat_url"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("edit", "void"))
    parser.add_argument("issue_id")
    parser.add_argument("--actor", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--mutation-id", help="Stable 32 lowercase hex ID for retries")
    parser.add_argument("--changes-json", type=Path, help="UTF-8 JSON object for edit fields")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"issue:[0-9a-f]{32}", args.issue_id):
        parser.error("invalid issue ID")
    mutation_id = args.mutation_id or uuid.uuid4().hex
    if not re.fullmatch(r"[0-9a-f]{32}", mutation_id):
        parser.error("invalid mutation ID")
    if args.action == "edit":
        if not args.changes_json:
            parser.error("edit requires --changes-json")
        changes = json.loads(args.changes_json.read_text(encoding="utf-8"))
        if not isinstance(changes, dict) or not changes or set(changes) - ALLOWED:
            parser.error("invalid edit fields")
    else:
        if args.changes_json:
            parser.error("void does not accept changes")
        changes = None
    supervisor_id, fencing_token = load_runtime_identity()
    arguments = {"issue_id": args.issue_id, "mutation_id": mutation_id,
                 "actor": args.actor, "reason": args.reason}
    if changes is not None:
        arguments["changes"] = changes
    result = c2_control.submit_control(
        operation=args.action + "_issue", arguments=arguments,
        request_key="c2-issue-" + args.action + "-" + mutation_id,
        supervisor_id=supervisor_id, fencing_token=fencing_token,
        actor="c2-issue-manage")
    print(json.dumps({"mutation_id": mutation_id, **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
