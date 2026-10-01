"""Locations of C3's local authority, separate from Git audit replicas."""
from pathlib import Path
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone

REPO = Path.home() / 'projects/codex-roadmap'
CANONICAL_DB = Path.home() / '.local/state/c3-control/roadmap.sqlite'


def local_enabled():
    transport = os.environ.get('C3_MUTATION_TRANSPORT')
    if transport:
        return transport == 'local'
    return CANONICAL_DB.is_file()


def database(repo=REPO):
    repo = Path(repo).resolve()
    if repo == REPO.resolve() and CANONICAL_DB.is_file():
        return CANONICAL_DB
    return repo / 'roadmap.sqlite'


def verified_backup(source, directory):
    """Coherent SQLite backup and digest; never copy a live database file."""
    source, directory = Path(source), Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    target = directory / (source.stem + '-' + stamp + '.sqlite')
    with sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True) as incoming:
        with sqlite3.connect(target) as outgoing:
            incoming.backup(outgoing)
            if outgoing.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('backup_integrity_failed')
    os.chmod(target, 0o600)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    manifest = {'source': str(source.resolve()), 'backup': str(target), 'sha256': digest, 'integrity_check': 'ok'}
    target.with_suffix('.json').write_text(json.dumps(manifest, sort_keys=True) + '\n')
    return manifest


def initialize_local():
    if CANONICAL_DB.exists():
        raise ValueError('local_database_already_exists')
    backup = verified_backup(REPO / 'roadmap.sqlite', CANONICAL_DB.parent / 'backups')
    incoming = CANONICAL_DB.with_suffix('.incoming')
    if incoming.exists():
        raise ValueError('interrupted_cutover_requires_review')
    with sqlite3.connect(Path(backup['backup']).resolve().as_uri() + '?mode=ro', uri=True) as source:
        with sqlite3.connect(incoming) as target:
            source.backup(target)
            if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('local_database_integrity_failed')
    os.chmod(incoming, 0o600)
    os.replace(incoming, CANONICAL_DB)
    return backup


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initialize-local', action='store_true', required=True)
    parser.parse_args()
    print(json.dumps(initialize_local(), sort_keys=True))
