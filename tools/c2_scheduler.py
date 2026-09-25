"""Transactional C2 scheduling primitives, called by the canonical writer only.

No process is launched inside a transaction. A durable run key is delivered to
an idempotent executor; expiry alone never authorizes a duplicate execution.
"""
from __future__ import annotations

import json
import sqlite3
import time
import uuid


class SchedulingError(RuntimeError):
    pass


SCHEMA = '''
CREATE TABLE IF NOT EXISTS work_item_execution_specs (
 work_item_id TEXT PRIMARY KEY REFERENCES work_items(work_item_id),
 activity TEXT NOT NULL CHECK(activity IN ('coding','diagnostic','gui','native','semantic','external','human')),
 model TEXT, reasoning TEXT, worktree TEXT, goal_mode INTEGER NOT NULL DEFAULT 0,
 command_json TEXT, resources_json TEXT NOT NULL DEFAULT '[]',
 max_attempts INTEGER NOT NULL DEFAULT 3 CHECK(max_attempts BETWEEN 1 AND 10)
);
CREATE TABLE IF NOT EXISTS work_item_runs (
 run_id TEXT PRIMARY KEY, work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id),
 event_key TEXT NOT NULL, attempt INTEGER NOT NULL,
 executor TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('claimed','running','recovering','completed','failed')),
 lease_until REAL NOT NULL, worker_ref TEXT, checkpoint_commit TEXT,
 metadata_json TEXT NOT NULL, created_at REAL NOT NULL,
 UNIQUE(work_item_id,attempt)
);
CREATE UNIQUE INDEX IF NOT EXISTS work_item_one_active_run ON work_item_runs(work_item_id)
 WHERE state IN ('claimed','running','recovering');
CREATE TABLE IF NOT EXISTS work_item_resource_leases (
 resource TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES work_item_runs(run_id)
);
CREATE TABLE IF NOT EXISTS work_item_scheduler_events (
 event_key TEXT PRIMARY KEY, observed_at REAL NOT NULL, result_json TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS work_item_execution_spec_running_update
BEFORE UPDATE ON work_item_execution_specs
WHEN (SELECT status FROM work_items WHERE work_item_id=OLD.work_item_id)='running'
BEGIN SELECT RAISE(ABORT,'RUNNING_EXECUTION_METADATA_IMMUTABLE'); END;
CREATE TRIGGER IF NOT EXISTS work_item_execution_spec_running_delete
BEFORE DELETE ON work_item_execution_specs
WHEN (SELECT status FROM work_items WHERE work_item_id=OLD.work_item_id)='running'
BEGIN SELECT RAISE(ABORT,'RUNNING_EXECUTION_METADATA_IMMUTABLE'); END;
'''


def install_schema(conn):
    # executescript would commit the caller's transaction.
    statement = ''
    for line in SCHEMA.splitlines():
        statement += line + '\n'
        if sqlite3.complete_statement(statement):
            conn.execute(statement)
            statement = ''


def choose_executor(policy: str, activity: str) -> str | None:
    if activity == 'external':
        return None
    if activity == 'human' or policy == 'human':
        return 'human'
    if policy != 'auto':
        return policy
    return {'coding':'codex','diagnostic':'codex','gui':'rdc',
            'native':'rdc','semantic':'chatgpt'}[activity]


def _transaction(conn):
    if not conn.in_transaction:
        raise SchedulingError('canonical_writer_transaction_required')


def configure(conn, work_item_id, *, activity, model=None, reasoning=None,
              worktree=None, goal_mode=False, command=None, resources=(), max_attempts=3):
    _transaction(conn)
    item = conn.execute('SELECT * FROM work_items WHERE work_item_id=?', (work_item_id,)).fetchone()
    if not item or item['status'] != 'pending':
        raise SchedulingError('only_pending_items_can_be_configured')
    if activity == 'native' and (not command or not isinstance(command, list)
                                or not all(isinstance(x,str) and x for x in command)):
        raise SchedulingError('native_requires_deterministic_argv')
    if not all(isinstance(r,str) and r for r in resources):
        raise SchedulingError('invalid_resource')
    conn.execute('''INSERT INTO work_item_execution_specs VALUES(?,?,?,?,?,?,?,?,?)
        ON CONFLICT(work_item_id) DO UPDATE SET activity=excluded.activity,
        model=excluded.model,reasoning=excluded.reasoning,worktree=excluded.worktree,
        goal_mode=excluded.goal_mode,command_json=excluded.command_json,
        resources_json=excluded.resources_json,max_attempts=excluded.max_attempts''',
        (work_item_id, activity, model, reasoning, worktree, int(goal_mode),
         json.dumps(command) if command else None, json.dumps(sorted(set(resources))), max_attempts))


def execution_metadata(conn, item, spec, executor):
    result = dict(spec)
    result['executor'] = executor
    result['repo'] = item['repo']
    result['prompt_id'] = item['prompt_id']
    if executor == 'codex':
        if not item['prompt_id']:
            raise SchedulingError('codex_prompt_materialization_required')
        prompt = conn.execute('SELECT * FROM prompts WHERE prompt_id=?', (item['prompt_id'],)).fetchone()
        if not prompt or not prompt['model'] or not prompt['reasoning'] or not spec['worktree']:
            raise SchedulingError('codex_exact_metadata_missing')
        for key in ('model','reasoning'):
            if spec[key] != prompt[key]:
                raise SchedulingError('codex_metadata_mismatch:'+key)
        if bool(spec['goal_mode']) != (prompt['prompt_type'] == 'Goal'):
            raise SchedulingError('codex_metadata_mismatch:goal_mode')
    return result


def schedule(conn, *, event_key, now=None, max_parallel=3, lease_seconds=120):
    _transaction(conn)
    now=time.time() if now is None else now
    if not event_key or max_parallel < 1 or lease_seconds <= 0:
        raise SchedulingError('invalid_scheduler_event')
    prior = conn.execute('SELECT result_json FROM work_item_scheduler_events WHERE event_key=?', (event_key,)).fetchone()
    if prior:
        return json.loads(prior[0])
    # Every observed running item counts, including adopted legacy runs.
    active = conn.execute("SELECT COUNT(*) FROM work_items WHERE status='running'").fetchone()[0]
    results = []
    candidates = conn.execute('SELECT * FROM v_work_item_runnable').fetchall()
    for item in candidates:
        if active >= max_parallel:
            break
        # A parent owns an execution branch: never launch imported checklist
        # steps as independent workers underneath an active ancestor.
        ancestor = item['parent_id']
        seen = set()
        blocked = False
        while ancestor:
            if ancestor in seen:
                raise SchedulingError('hierarchy_cycle')
            seen.add(ancestor)
            row = conn.execute('SELECT parent_id,status FROM work_items WHERE work_item_id=?', (ancestor,)).fetchone()
            if row['status'] == 'running':
                blocked = True
                break
            ancestor = row['parent_id']
        if blocked:
            continue
        spec = conn.execute('SELECT * FROM work_item_execution_specs WHERE work_item_id=?', (item['work_item_id'],)).fetchone()
        if not spec:
            continue  # No guessed semantic classification or implicit launch.
        executor = choose_executor(item['executor_policy'], spec['activity'])
        if executor in (None, 'human'):
            continue
        resources = set(json.loads(spec['resources_json']))
        if item['repo']:
            # Default exclusive repo writer. Explicit isolated worktree resource
            # is permitted only when the spec supplies the actual worktree.
            resources.add('worktree:'+spec['worktree'] if spec['worktree'] else 'repo:'+item['repo'])
            peers = conn.execute("SELECT w.work_item_id,s.worktree FROM work_items w LEFT JOIN work_item_execution_specs s USING(work_item_id) WHERE w.repo=? AND w.status='running'", (item['repo'],)).fetchall()
            if any(not spec['worktree'] or not peer['worktree'] or spec['worktree']==peer['worktree'] for peer in peers):
                continue
        if any(conn.execute('SELECT 1 FROM work_item_resource_leases WHERE resource=?',(r,)).fetchone() for r in resources):
            continue
        attempt = 1 + conn.execute('SELECT COUNT(*) FROM work_item_runs WHERE work_item_id=?',(item['work_item_id'],)).fetchone()[0]
        if attempt > spec['max_attempts']:
            continue
        try:
            metadata = execution_metadata(conn, item, spec, executor)
        except SchedulingError as exc:
            results.append({'work_item_id':item['work_item_id'], 'blocked':str(exc)})
            continue
        run_id = uuid.uuid4().hex
        conn.execute('INSERT INTO work_item_runs VALUES(?,?,?,?,?,?,?,?,?,?,?)',
            (run_id,item['work_item_id'],event_key,attempt,executor,'claimed',now+lease_seconds,None,None,json.dumps(metadata,sort_keys=True),now))
        for resource in sorted(resources):
            conn.execute('INSERT INTO work_item_resource_leases VALUES(?,?)',(resource,run_id))
        if item['prompt_id']:
            import roadmap_db
            roadmap_db.set_status(conn, item['prompt_id'], 'running', actor='c2-scheduler')
        else:
            conn.execute("UPDATE work_items SET status='running' WHERE work_item_id=?",(item['work_item_id'],))
        results.append({'work_item_id':item['work_item_id'],'run_id':run_id,'executor':executor,'metadata':metadata})
        active += 1
    conn.execute('INSERT INTO work_item_scheduler_events VALUES(?,?,?)',(event_key,now,json.dumps(results,sort_keys=True)))
    return results


def acknowledge(conn, run_id, *, worker_ref, metadata, now=None, lease_seconds=120):
    _transaction(conn)
    now=time.time() if now is None else now
    run = conn.execute('SELECT * FROM work_item_runs WHERE run_id=?',(run_id,)).fetchone()
    if not run or run['state'] not in ('claimed','running','recovering'):
        raise SchedulingError('run_not_active')
    if not worker_ref or metadata != json.loads(run['metadata_json']):
        raise SchedulingError('executor_metadata_mismatch')
    if run['worker_ref'] and worker_ref != run['worker_ref']:
        raise SchedulingError('worker_identity_mismatch')
    conn.execute("UPDATE work_item_runs SET state='running',worker_ref=?,lease_until=? WHERE run_id=?",(worker_ref,now+lease_seconds,run_id))


def checkpoint(conn, run_id, commit):
    _transaction(conn)
    if not isinstance(commit,str) or len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise SchedulingError('invalid_checkpoint_commit')
    result=conn.execute("UPDATE work_item_runs SET checkpoint_commit=? WHERE run_id=? AND state IN ('claimed','running','recovering')",(commit,run_id))
    if not result.rowcount:
        raise SchedulingError('run_not_active')


def recover(conn, *, now=None):
    _transaction(conn)
    now=time.time() if now is None else now
    rows = conn.execute("SELECT * FROM work_item_runs WHERE state IN ('claimed','running') AND lease_until<=?",(now,)).fetchall()
    for row in rows:
        conn.execute("UPDATE work_item_runs SET state='recovering' WHERE run_id=?",(row['run_id'],))
    # Preserve the same run identity and locks; executor must inspect its durable
    # worker receipt before resume. A lost acknowledgement is not a failed run.
    return [dict(r) for r in conn.execute("SELECT * FROM work_item_runs WHERE state='recovering'")]


def complete(conn, run_id, *, succeeded, worker_ref):
    _transaction(conn)
    run=conn.execute('SELECT * FROM work_item_runs WHERE run_id=?',(run_id,)).fetchone()
    if not run or run['worker_ref'] != worker_ref or not worker_ref:
        raise SchedulingError('worker_identity_mismatch')
    target='completed' if succeeded else 'failed'
    if run['state'] == target:
        return
    if run['state'] not in ('running','recovering'):
        raise SchedulingError('run_not_active')
    if succeeded:
        missing=conn.execute('''WITH RECURSIVE children(id) AS (
          SELECT work_item_id FROM work_items WHERE parent_id=?
          UNION SELECT w.work_item_id FROM work_items w JOIN children c ON w.parent_id=c.id)
          SELECT 1 FROM children c JOIN work_items w ON w.work_item_id=c.id
          WHERE w.required=1 AND w.status NOT IN ('completed','waived') LIMIT 1''',(run['work_item_id'],)).fetchone()
        if missing:
            raise SchedulingError('required_children_incomplete')
    item = conn.execute('SELECT prompt_id,status FROM work_items WHERE work_item_id=?', (run['work_item_id'],)).fetchone()
    if item['prompt_id'] and item['status'] != target:
        raise SchedulingError('prompt_terminal_requires_roadmap_finish')
    conn.execute('UPDATE work_item_runs SET state=? WHERE run_id=?',(target,run_id))
    conn.execute('DELETE FROM work_item_resource_leases WHERE run_id=?',(run_id,))
    conn.execute('UPDATE work_items SET status=? WHERE work_item_id=?',(target,run['work_item_id']))


def reconcile_terminal_run(conn, run_id):
    """Release a Codex run only after the canonical terminal writer has acted."""
    _transaction(conn)
    row=conn.execute('''SELECT r.state,r.executor,w.status AS item_status
      FROM work_item_runs r JOIN work_items w USING(work_item_id)
      WHERE r.run_id=?''',(run_id,)).fetchone()
    if not row or row['executor']!='codex':
        raise SchedulingError('codex_run_required')
    if row['item_status'] not in ('completed','failed','blocked','cancelled'):
        raise SchedulingError('canonical_terminal_state_required')
    target='completed' if row['item_status']=='completed' else 'failed'
    if row['state']==target:
        return
    if row['state'] not in ('claimed','running','recovering'):
        raise SchedulingError('run_not_active')
    conn.execute('UPDATE work_item_runs SET state=? WHERE run_id=?',(target,run_id))
    conn.execute('DELETE FROM work_item_resource_leases WHERE run_id=?',(run_id,))
