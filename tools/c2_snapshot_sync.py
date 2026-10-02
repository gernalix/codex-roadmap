#!/usr/bin/env python3
"""Retired snapshot transport: canonical C3 reads are local and direct."""


class SnapshotError(RuntimeError):
    pass


def sync(*args, **kwargs):
    raise SnapshotError("snapshot_transport_retired_use_canonical_c3_database")


def main():
    import json
    print(json.dumps({"status": "blocked", "reason": "snapshot_transport_retired"}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
