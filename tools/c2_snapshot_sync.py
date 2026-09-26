#!/usr/bin/env python3
"""Refresh a read-only C2 roadmap snapshot from the canonical remote main blob."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile


DEFAULT_REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path.home() / '.local/state/c2-supervisor/roadmap.sqlite3'


class SnapshotError(RuntimeError):
    pass


def _git(repo, *args, stdout=None):
    result = subprocess.run(['git', '-C', str(repo), '-c', 'maintenance.auto=false',
                             '-c', 'gc.auto=0', *args], stdout=stdout or subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise SnapshotError('git_snapshot_source_failed:' + args[0])
    return result.stdout


def _validate(path):
    db = sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True)
    try:
        if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise SnapshotError('snapshot_integrity_failed')
        if not db.execute("SELECT 1 FROM meta WHERE key='work_items_cutover_version'").fetchone():
            raise SnapshotError('snapshot_c2_cutover_missing')
    finally:
        db.close()


def _preserve_active(previous, incoming):
    if not previous.exists():
        return
    old = sqlite3.connect(f'{previous.resolve().as_uri()}?mode=ro', uri=True)
    new = sqlite3.connect(f'{incoming.resolve().as_uri()}?mode=ro', uri=True)
    try:
        for (run_id,) in old.execute("SELECT run_id FROM work_item_runs WHERE state IN ('claimed','running','recovering')"):
            row = new.execute('SELECT state FROM work_item_runs WHERE run_id=?', (run_id,)).fetchone()
            if not row:
                raise SnapshotError('active_run_missing_from_remote')
    finally:
        old.close()
        new.close()


def sync(repo=DEFAULT_REPO, output=DEFAULT_OUTPUT):
    repo, output = Path(repo), Path(output)
    refs = _git(repo, 'ls-remote', 'origin', 'refs/heads/main').decode().split()
    if len(refs) != 2 or refs[1] != 'refs/heads/main':
        raise SnapshotError('remote_main_missing')
    remote = refs[0]
    if not re.fullmatch(r'[0-9a-f]{40}', remote):
        raise SnapshotError('invalid_remote_main')
    manifest = output.with_suffix(output.suffix + '.json')
    if output.exists() and manifest.exists():
        try:
            if json.loads(manifest.read_text()).get('source_commit') == remote:
                _validate(output)
                return {'state': 'current', 'source_commit': remote}
        except (OSError, ValueError, sqlite3.DatabaseError):
            pass
    _git(repo, 'fetch', '--no-write-fetch-head', '--quiet', 'origin', remote)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=output.parent, prefix='roadmap-', suffix='.sqlite3')
    try:
        with os.fdopen(fd, 'wb') as stream:
            _git(repo, 'show', remote + ':roadmap.sqlite', stdout=stream)
            stream.flush()
            os.fsync(stream.fileno())
        candidate = Path(temporary)
        _validate(candidate)
        _preserve_active(output, candidate)
        os.replace(candidate, output)
        manifest.write_text(json.dumps({'source_commit': remote}, sort_keys=True) + '\n')
        return {'state': 'updated', 'source_commit': remote}
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = sync(args.repo, args.output)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
