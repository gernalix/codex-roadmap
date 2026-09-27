#!/usr/bin/env python3
"""Submit Workflowy manual ordering through the fenced C2 control path."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import c2_control
from c2_supervisor_lease import RUNTIME_ENV


class WorkflowyOrderError(RuntimeError):
    pass


def load_runtime_identity(path: Path = RUNTIME_ENV) -> tuple[str, int]:
    path = Path(path).expanduser()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise WorkflowyOrderError("supervisor_runtime_env_missing") from exc
    values: dict[str, str] = {}
    allowed = {"C2_SUPERVISOR_ID", "C2_FENCING_TOKEN"}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise WorkflowyOrderError("invalid_supervisor_runtime_env")
        key, value = line.split("=", 1)
        if key not in allowed or key in values or not value:
            raise WorkflowyOrderError("invalid_supervisor_runtime_env")
        values[key] = value
    supervisor_id = values.get("C2_SUPERVISOR_ID", "")
    token = values.get("C2_FENCING_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_.:-]+", supervisor_id):
        raise WorkflowyOrderError("invalid_supervisor_id")
    if not re.fullmatch(r"[1-9][0-9]*", token):
        raise WorkflowyOrderError("invalid_fencing_token")
    return supervisor_id, int(token)


def request_key(action: str, scope: str, ids: list[str],
                source_modified_at: str | None = None) -> str:
    stable = {
        "action": action,
        "scope": scope,
        "ids": ids if action == "set" else sorted(ids),
        "source_modified_at": source_modified_at,
    }
    encoded = json.dumps(
        stable, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "c2-workflowy-order-" + hashlib.sha256(encoded).hexdigest()[:32]


def main(argv=None, *, runtime_env: Path = RUNTIME_ENV) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    setter = sub.add_parser("set")
    setter.add_argument("--scope", choices=("inbox", "roadmap"), required=True)
    setter.add_argument("--source-modified-at", required=True)
    setter.add_argument("ids", nargs="*")
    clearer = sub.add_parser("clear")
    clearer.add_argument("--scope", choices=("inbox", "roadmap"), required=True)
    clearer.add_argument(
        "--source-modified-at",
        required=True,
        help="stable modifiedAt/action identity of this Workflowy reset event",
    )
    clearer.add_argument("ids", nargs="*")
    args = parser.parse_args(argv)

    if len(set(args.ids)) != len(args.ids):
        raise WorkflowyOrderError("duplicate_entity_id")
    supervisor_id, fencing_token = load_runtime_identity(runtime_env)
    if args.action == "set":
        if not args.source_modified_at:
            raise WorkflowyOrderError("source_modified_at_required")
        operation = "set_manual_order"
        arguments = {
            "scope": args.scope,
            "ordered_ids": args.ids,
            "source": "workflowy",
            "source_modified_at": args.source_modified_at,
        }
    else:
        if not args.source_modified_at:
            raise WorkflowyOrderError("source_modified_at_required")
        if args.source_modified_at != args.source_modified_at.strip():
            raise WorkflowyOrderError("invalid_source_modified_at")
        operation = "clear_manual_order"
        arguments = {"scope": args.scope}
        if args.ids:
            arguments["ids"] = sorted(args.ids)
    key = request_key(
        args.action, args.scope, args.ids, args.source_modified_at
    )
    result = c2_control.submit_control(
        operation=operation,
        arguments=arguments,
        request_key=key,
        supervisor_id=supervisor_id,
        fencing_token=fencing_token,
        actor="c2-workflowy-order",
    )
    print(json.dumps({"status": "queued", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
