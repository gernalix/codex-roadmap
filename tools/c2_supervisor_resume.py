#!/usr/bin/env python3
"""One-shot, bounded C2 supervisor recovery state machine."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import time

from c2_supervisor_lease import (
    DEFAULT_DB, LeaseError, acquire, connect, publish_runtime_identity,
    record_activity, retire_stalled, snapshot,
)
from submit_mutation import submit_document


DEFAULT_CANONICAL_DB = Path.home() / '.local/state/c2-supervisor/roadmap.sqlite3'
SUSPECTED_STALL_SECONDS = 40
FINAL_VERIFICATION_SECONDS = 90
STALE_TAKEOVER_SECONDS = 180


class ResumeError(RuntimeError):
    pass


def read_recovery_pointer(path: Path) -> dict:
    """Read and parse the durable pointer exactly once."""
    try:
        text = path.read_text(encoding='utf-8')
    except OSError as exc:
        raise ResumeError('recovery_pointer_unavailable') from exc
    state_line = next((line for line in text.splitlines()
                       if line.startswith('C2_RECOVERY_STATE=')), None)
    if state_line is None:
        raise ResumeError('recovery_pointer_contract_missing')
    try:
        state = json.loads(state_line.removeprefix('C2_RECOVERY_STATE='))
    except json.JSONDecodeError as exc:
        raise ResumeError('recovery_pointer_state_invalid') from exc
    required = {
        'previous_supervisor_id', 'previous_fencing_token', 'active_runs',
        'active_executors', 'preserve_resources', 'blocker',
    }
    if not isinstance(state, dict) or not required.issubset(state):
        raise ResumeError('recovery_pointer_state_incomplete')
    if (not isinstance(state['previous_supervisor_id'], str) or
            type(state['previous_fencing_token']) is not int or
            any(not isinstance(state[key], list)
                for key in ('active_runs', 'active_executors', 'preserve_resources'))):
        raise ResumeError('recovery_pointer_state_invalid')
    marker = '# Exact next action\n'
    if marker not in text:
        raise ResumeError('exact_next_action_missing')
    exact = text.split(marker, 1)[1].split('\n# ', 1)[0].strip()
    if not exact:
        raise ResumeError('exact_next_action_missing')
    return {'state': state, 'exact_next_action': exact, 'path': str(path)}


def read_canonical_state(path: Path) -> dict:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise ResumeError('canonical_snapshot_missing')
    with closing(sqlite3.connect(f'{resolved.as_uri()}?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        authority = db.execute(
            'SELECT supervisor_id,fencing_token,lease_expires_at,claimed_at,renewed_at '
            'FROM c2_supervisor_authority WHERE singleton=1'
        ).fetchone()
        runs = [dict(row) for row in db.execute('''SELECT run_id,work_item_id,executor,worker_ref
            FROM work_item_runs WHERE state IN ('claimed','running','recovering')
            ORDER BY run_id''')]
        resources = [str(row[0]) for row in db.execute('''SELECT resource
            FROM work_item_resource_leases ORDER BY resource''')]
    return {
        'authority': dict(authority) if authority else None,
        'active_runs': runs,
        'active_resources': resources,
    }


def _phase(age: float) -> str:
    if age >= STALE_TAKEOVER_SECONDS:
        return 'stalled'
    if age >= FINAL_VERIFICATION_SECONDS:
        return 'final_verification'
    if age >= SUSPECTED_STALL_SECONDS:
        return 'suspected_stall'
    return 'active'


def _same_authority(left: dict | None, right: dict | None) -> bool:
    return bool(left and right and
                left['supervisor_id'] == right['supervisor_id'] and
                int(left['fencing_token']) == int(right['fencing_token']))


def _submit_claim(row: dict, pointer: dict) -> dict:
    authority = {
        'supervisor_id': row['supervisor_id'],
        'fencing_token': int(row['fencing_token']),
        # The request key identifies this acquisition. Later local heartbeats
        # must not change the immutable claim document on replay.
        'lease_expires_at': float(row['acquired_at']) + STALE_TAKEOVER_SECONDS,
    }
    identity = pointer['path'] + ':' + row['supervisor_id'] + ':' + str(row['fencing_token'])
    key = 'c2-supervisor-resume-' + hashlib.sha256(identity.encode()).hexdigest()[:32]
    return submit_document({
        'schema': 'codex-roadmap.mutation.v1',
        'actor': 'c2-supervisor-resume',
        'operations': [{'op': 'c2_claim_supervisor',
                        'arguments': {'supervisor_authority': authority}}],
    }, request_key=key)


def _submit_renewal(row: dict, pointer: dict) -> dict:
    authority = {
        'supervisor_id': row['supervisor_id'],
        'fencing_token': int(row['fencing_token']),
        'lease_expires_at': float(row['lease_expires_at']),
    }
    identity = (pointer['path'] + ':' + row['supervisor_id'] + ':'
                + str(row['fencing_token']) + ':' + repr(authority['lease_expires_at']))
    key = 'c2-supervisor-renew-' + hashlib.sha256(identity.encode()).hexdigest()[:32]
    return submit_document({
        'schema': 'codex-roadmap.mutation.v1',
        'actor': 'c2-supervisor-resume',
        'operations': [{'op': 'c2_renew_supervisor',
                        'arguments': {'supervisor_authority': authority}}],
    }, request_key=key)


def resume(db, canonical: dict, pointer: dict, *, owner='c2-supervisor-resume',
           claim=_submit_claim, publish=publish_runtime_identity,
           now=None, supervisor_id=None) -> dict:
    now = time.time() if now is None else now
    local = snapshot(db)
    remote = canonical.get('authority')
    pstate = pointer['state']
    if pstate.get('blocker'):
        return {'outcome': 'BLOCKED', 'reason': 'pointer_blocker',
                'blocker': str(pstate['blocker'])}

    previous_token = int(pstate['previous_fencing_token'])
    previous_id = pstate['previous_supervisor_id']
    newest_token = max(previous_token,
                       int(local['fencing_token']) if local else 0,
                       int(remote['fencing_token']) if remote else 0)

    # A successor already authoritative is the terminal idempotent result.
    if remote and int(remote['fencing_token']) > previous_token and float(remote['lease_expires_at']) > now:
        if local and _same_authority(local, remote) and local['state'] == 'active' and local['lease_expires_at'] > now:
            age = now - max(float(local['last_heartbeat']), float(local['last_progress_at']))
            return {'outcome': 'ALREADY_ACTIVE', 'phase': _phase(age),
                    'supervisor_id': local['supervisor_id'],
                    'fencing_token': int(local['fencing_token'])}
        return {'outcome': 'ALREADY_ACTIVE', 'phase': 'canonical_successor',
                'supervisor_id': remote['supervisor_id'],
                'fencing_token': int(remote['fencing_token'])}

    if (local and remote and _same_authority(local, remote)
            and local['state'] == 'active' and local['lease_expires_at'] > now
            and now - float(local['last_progress_at']) < STALE_TAKEOVER_SECONDS
            and float(remote['lease_expires_at']) <= now):
        receipt = _submit_renewal(local, pointer)
        # Preserve the response shape consumed by Workflowy's preflight: it
        # waits for a queued submission and proceeds only after application.
        return {'outcome': 'RESUMED', 'phase': 'canonical_renewal',
                'supervisor_id': local['supervisor_id'],
                'fencing_token': int(local['fencing_token']),
                'exact_next_action': pointer['exact_next_action'],
                'claim': receipt}

    # Replays between local acquisition and canonical application reuse one identity.
    if (local and int(local['fencing_token']) > previous_token and
            local['state'] == 'active' and local['lease_expires_at'] > now):
        receipt = claim(local, pointer)
        return {'outcome': str(local['current_step']).upper()
                if local['current_step'] in ('resumed', 'stale_takeover') else 'RESUMED',
                'supervisor_id': local['supervisor_id'],
                'fencing_token': int(local['fencing_token']),
                'exact_next_action': pointer['exact_next_action'],
                'claim': receipt}

    local_previous = bool(local and local['supervisor_id'] == previous_id and
                          int(local['fencing_token']) == previous_token)
    remote_previous = bool(remote and remote['supervisor_id'] == previous_id and
                           int(remote['fencing_token']) == previous_token)
    active_lease = ((local_previous and local['state'] == 'active' and local['lease_expires_at'] > now) or
                    (remote_previous and float(remote['lease_expires_at']) > now))
    progress_values = []
    if local_previous:
        progress_values.append(float(local['last_progress_at']))
    if remote_previous:
        progress_values.append(float(remote['renewed_at']))
    age = now - max(progress_values) if progress_values else STALE_TAKEOVER_SECONDS
    phase = _phase(age)
    if active_lease and phase != 'stalled':
        return {'outcome': 'ALREADY_ACTIVE', 'phase': phase,
                'supervisor_id': previous_id, 'fencing_token': previous_token}

    if remote and float(remote['lease_expires_at']) > now and not remote_previous:
        return {'outcome': 'BLOCKED', 'reason': 'canonical_primary_lease_held',
                'blocker': remote['supervisor_id']}

    takeover = bool(local or remote)
    if local and local['state'] == 'active' and local['lease_expires_at'] > now:
        # A 180-second progress stall is takeover eligibility even if manual
        # heartbeats incorrectly extended the lease.
        if now - float(local['last_progress_at']) < STALE_TAKEOVER_SECONDS:
            return {'outcome': 'ALREADY_ACTIVE', 'phase': phase,
                    'supervisor_id': local['supervisor_id'],
                    'fencing_token': int(local['fencing_token'])}
        retire_stalled(db, stalled_after=STALE_TAKEOVER_SECONDS, now=now)

    row = acquire(db, owner=owner, pointer=pointer['path'], supervisor_id=supervisor_id,
                  ttl=STALE_TAKEOVER_SECONDS, now=now, minimum_token=newest_token)
    outcome = 'STALE_TAKEOVER' if takeover else 'RESUMED'
    row = record_activity(db, supervisor_id=row['supervisor_id'],
                          token=row['fencing_token'], operation='recovery:authority',
                          step=outcome.lower(), ttl=STALE_TAKEOVER_SECONDS, now=now)
    publish(row)
    receipt = claim(row, pointer)
    observed_runs = [str(run['run_id']) for run in canonical.get('active_runs', [])]
    preserved_runs = sorted(set(map(str, pstate['active_runs'])) | set(observed_runs))
    preserved_resources = sorted(set(map(str, pstate['preserve_resources'])) |
                                 set(map(str, canonical.get('active_resources', []))))
    return {'outcome': outcome, 'supervisor_id': row['supervisor_id'],
            'fencing_token': int(row['fencing_token']),
            'exact_next_action': pointer['exact_next_action'], 'claim': receipt,
            'preserve_resources': preserved_resources,
            'active_runs': preserved_runs,
            'active_executors': list(pstate['active_executors'])}


def main(argv=None) -> int:
    from c3_retirement import require_not_retired
    require_not_retired()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    parser.add_argument('--canonical-db', type=Path, default=DEFAULT_CANONICAL_DB)
    parser.add_argument('--pointer', type=Path)
    parser.add_argument('--owner', default='c2-supervisor-resume')
    args = parser.parse_args(argv)
    try:
        with connect(args.db) as db:
            local = snapshot(db)
            if not local and args.pointer is None:
                raise ResumeError('supervisor_lease_missing')
            pointer_path = (args.pointer or Path(local['recovery_pointer'])).expanduser()
            if not pointer_path.is_absolute():
                pointer_path = Path(__file__).resolve().parents[1] / pointer_path
            pointer = read_recovery_pointer(pointer_path.resolve())
            canonical = read_canonical_state(args.canonical_db)
            result = resume(db, canonical, pointer, owner=args.owner)
    except (OSError, sqlite3.Error, LeaseError, ResumeError, ValueError) as exc:
        result = {'outcome': 'BLOCKED', 'reason': str(exc)}
    print(json.dumps(result, sort_keys=True))
    return 2 if result['outcome'] == 'BLOCKED' else 0


if __name__ == '__main__':
    raise SystemExit(main())
