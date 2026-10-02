"""Transactional C2 scheduling primitives, called by the canonical writer only.

No process is launched inside a transaction. A durable run key is delivered to
an idempotent executor; expiry alone never authorizes a duplicate execution.
"""
from __future__ import annotations

import json
import hashlib
import sqlite3
import time
import uuid

DEFAULT_PARALLEL_CAP = 12
HARD_PARALLEL_CAP = 16


class SchedulingError(RuntimeError):
    pass


SCHEMA = '''
CREATE TABLE IF NOT EXISTS work_item_execution_specs (
 work_item_id TEXT PRIMARY KEY REFERENCES work_items(work_item_id),
 activity TEXT NOT NULL CHECK(activity IN ('coding','diagnostic','gui','native','semantic','external','human')),
 model TEXT, reasoning TEXT, worktree TEXT, project_url TEXT,
 goal_mode INTEGER NOT NULL DEFAULT 0,
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
CREATE TABLE IF NOT EXISTS c2_execution_override (
 singleton INTEGER PRIMARY KEY CHECK(singleton=1),
 mode TEXT NOT NULL CHECK(mode='drain_first'),
 selector TEXT NOT NULL CHECK(selector IN ('project','repo','tag')),
 value TEXT NOT NULL CHECK(length(value)>0),
 updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS work_item_executor_bindings (
 run_id TEXT PRIMARY KEY REFERENCES work_item_runs(run_id) ON DELETE CASCADE,
 work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
 executor TEXT NOT NULL,
 executor_ref TEXT NOT NULL,
 chat_url TEXT NOT NULL,
 bound_at REAL NOT NULL,
 UNIQUE(executor, executor_ref)
);
CREATE INDEX IF NOT EXISTS idx_work_item_executor_bindings_item
 ON work_item_executor_bindings(work_item_id,bound_at);
CREATE TABLE IF NOT EXISTS work_item_executor_starts (
 receipt_id TEXT PRIMARY KEY,
 work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
 run_id TEXT REFERENCES work_item_runs(run_id) ON DELETE SET NULL,
 prompt_id TEXT,
 executor TEXT NOT NULL,
 executor_ref TEXT,
 chat_url TEXT,
 started_at REAL NOT NULL,
 UNIQUE(run_id)
);
CREATE INDEX IF NOT EXISTS idx_work_item_executor_starts_item
 ON work_item_executor_starts(work_item_id,started_at);
CREATE VIEW IF NOT EXISTS v_work_item_execution_liveness AS
SELECT w.work_item_id,
       w.status AS lifecycle_status,
       r.run_id AS live_run_id,
       r.state AS live_run_state,
       CASE
         WHEN r.run_id IS NOT NULL THEN r.state
         WHEN w.status='running' AND EXISTS(
           SELECT 1 FROM work_item_tags t
           WHERE t.work_item_id=w.work_item_id
             AND t.tag='c2:status-only-supervisor'
         ) THEN 'supervising'
         WHEN w.status='running' THEN 'stale_running'
         ELSE 'inactive'
       END AS execution_state,
       CASE WHEN r.run_id IS NOT NULL THEN 1 ELSE 0 END AS has_live_executor,
       CASE WHEN w.status='running' AND r.run_id IS NULL AND EXISTS(
         SELECT 1 FROM work_item_tags t
         WHERE t.work_item_id=w.work_item_id
           AND t.tag='c2:status-only-supervisor'
       ) THEN 1 ELSE 0 END AS is_status_only_supervisor
FROM work_items w
LEFT JOIN work_item_runs r
  ON r.work_item_id=w.work_item_id
 AND r.state IN ('claimed','running','recovering');
DROP VIEW IF EXISTS v_work_item_runnable;
CREATE VIEW v_work_item_runnable AS
SELECT w.*
FROM work_items w
WHERE w.status='pending'
  AND w.actionable=1
  AND w.executor_policy<>'human'
  AND NOT EXISTS (
    SELECT 1
    FROM work_item_dependencies d
    JOIN work_items dep ON dep.work_item_id=d.depends_on_work_item_id
    WHERE d.work_item_id=w.work_item_id
      AND d.required=1
      AND dep.status NOT IN ('completed','waived','cancelled','superseded')
  )
  AND NOT EXISTS (
    SELECT 1 FROM work_item_tags t
    WHERE t.work_item_id=w.work_item_id
      AND t.tag LIKE 'manual-prerequisite:%'
  )
  AND NOT EXISTS (
    WITH RECURSIVE ancestors(id) AS (
      SELECT w.parent_id
      UNION ALL
      SELECT p.parent_id FROM work_items p
      JOIN ancestors a ON p.work_item_id=a.id
      WHERE p.parent_id IS NOT NULL
    )
    SELECT 1 FROM ancestors a
    JOIN work_item_runs r ON r.work_item_id=a.id
    WHERE r.state IN ('claimed','running','recovering')
  )
ORDER BY COALESCE(w.sort_order,2147483647), w.created_at, w.work_item_id;
CREATE TABLE IF NOT EXISTS work_item_result_receipts (
 receipt_id TEXT PRIMARY KEY,
 work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
 run_id TEXT REFERENCES work_item_runs(run_id) ON DELETE SET NULL,
 prompt_id TEXT,
 outcome TEXT NOT NULL CHECK(outcome IN ('PASS','BLOCKED','FAIL','CANCELLED')),
 summary TEXT, completed_json TEXT NOT NULL, remaining_json TEXT NOT NULL,
 evidence_json TEXT NOT NULL, blocker TEXT, next_action TEXT,
 strict_contract INTEGER NOT NULL DEFAULT 0 CHECK(strict_contract IN (0,1)),
 payload_sha256 TEXT NOT NULL, captured_at REAL NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS work_item_result_receipts_run
 ON work_item_result_receipts(run_id) WHERE run_id IS NOT NULL;
CREATE TABLE IF NOT EXISTS work_item_scheduler_events (
 event_key TEXT PRIMARY KEY, observed_at REAL NOT NULL, result_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS c2_notification_outbox (
 event_key TEXT PRIMARY KEY,
 work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id),
 title TEXT NOT NULL, message TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('pending','sending','sent','uncertain')),
 created_at REAL NOT NULL, sent_at REAL, error TEXT
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
    import c3_override
    c3_override.install_schema(conn)


def choose_executor(policy: str, activity: str) -> str | None:
    if activity == 'external':
        return None
    if activity == 'human' or policy == 'human':
        return 'human'
    if policy != 'auto':
        return policy
    return {'coding':'codex','diagnostic':'codex','gui':'rdc',
            'native':'rdc','semantic':'chatgpt'}[activity]


def symphony_selected(policy, activity, repo, route):
    return bool(route and route.get('mode') in ('canary','production')
                and activity=='coding' and policy in ('auto','codex')
                and repo in route.get('source_repos',()))


def routed_executor(policy, activity, repo, route):
    if route and route.get('mode')=='invalid' and activity=='coding' and policy in ('auto','codex'):
        return 'symphony-unhealthy'
    if symphony_selected(policy,activity,repo,route):
        return 'symphony' if route.get('healthy') else 'symphony-unhealthy'
    selected = choose_executor(policy,activity)
    if route and route.get('no_legacy_codex') and selected == 'codex':
        return 'symphony-unhealthy'
    return selected


def _transaction(conn):
    if not conn.in_transaction:
        raise SchedulingError('canonical_writer_transaction_required')


def read_override(conn):
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='c2_execution_override'").fetchone():
        return None
    row = conn.execute('SELECT mode,selector,value,updated_at FROM c2_execution_override WHERE singleton=1').fetchone()
    return dict(row) if row else None


def set_override(conn, *, selector, value, mode='drain_first', now=None):
    _transaction(conn)
    if mode != 'drain_first' or selector not in ('project','repo','tag') or not isinstance(value,str) or not value.strip() or value != value.strip():
        raise SchedulingError('invalid_execution_override')
    conn.execute('''INSERT INTO c2_execution_override VALUES(1,?,?,?,?)
      ON CONFLICT(singleton) DO UPDATE SET mode=excluded.mode,selector=excluded.selector,
      value=excluded.value,updated_at=excluded.updated_at
      WHERE c2_execution_override.mode!=excluded.mode OR
            c2_execution_override.selector!=excluded.selector OR
            c2_execution_override.value!=excluded.value''',
      (mode,selector,value,time.time() if now is None else now))
    return read_override(conn)


def clear_override(conn):
    _transaction(conn)
    conn.execute('DELETE FROM c2_execution_override WHERE singleton=1')
    return None


def override_matches(conn, item, override):
    selector, value = override['selector'], override['value']
    if selector == 'project':
        return item['project_name'] == value or item['project_id'] == value
    if selector == 'repo':
        return item['repo'] == value
    return bool(conn.execute('SELECT 1 FROM work_item_tags WHERE work_item_id=? AND tag=?',
                             (item['work_item_id'],value)).fetchone())


def configure(conn, work_item_id, *, activity, model=None, reasoning=None,
              worktree=None, project_url=None, goal_mode=False, command=None,
              resources=(), max_attempts=3):
    _transaction(conn)
    item = conn.execute('SELECT * FROM work_items WHERE work_item_id=?', (work_item_id,)).fetchone()
    if not item or item['status'] != 'pending':
        raise SchedulingError('only_pending_items_can_be_configured')
    if activity == 'native' and (not command or not isinstance(command, list)
                                or not all(isinstance(x,str) and x for x in command)):
        raise SchedulingError('native_requires_deterministic_argv')
    if not all(isinstance(r,str) and r for r in resources):
        raise SchedulingError('invalid_resource')
    conn.execute('''INSERT INTO work_item_execution_specs VALUES(?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(work_item_id) DO UPDATE SET activity=excluded.activity,
        model=excluded.model,reasoning=excluded.reasoning,worktree=excluded.worktree,
        project_url=excluded.project_url,
        goal_mode=excluded.goal_mode,command_json=excluded.command_json,
        resources_json=excluded.resources_json,max_attempts=excluded.max_attempts''',
        (work_item_id, activity, model, reasoning, worktree, project_url, int(goal_mode),
         json.dumps(command) if command else None, json.dumps(sorted(set(resources))), max_attempts))


def configure_auto(conn, work_item_id, *, execution=None):
    """Create an auto-policy spec only from unambiguous structured input.

    Missing input is a normal waiting state. It must never be filled by guessing
    from a title, next action, repository name, or imported task-state text.
    """
    _transaction(conn)
    item = conn.execute('SELECT * FROM work_items WHERE work_item_id=?', (work_item_id,)).fetchone()
    if (not item or item['status'] != 'pending' or
            item['executor_policy'] not in ('auto','codex') or
            (item['executor_policy']=='codex' and not item['prompt_id'])):
        raise SchedulingError('auto_spec_requires_pending_auto_or_materialized_codex_item')
    if conn.execute('SELECT 1 FROM work_item_execution_specs WHERE work_item_id=?',
                    (work_item_id,)).fetchone():
        return {'state':'ready'}
    if execution is None:
        return {'state':'waiting','reason':'execution_context_missing'}
    if not isinstance(execution, dict):
        raise SchedulingError('execution_context_must_be_object')
    permitted = {'activity','command','worktree','project_url','model','reasoning',
                 'resources','max_attempts'}
    unknown = set(execution) - permitted
    if unknown:
        raise SchedulingError('unknown_execution_context_fields:'+','.join(sorted(unknown)))
    activity = execution.get('activity')
    if activity is None:
        # A command means native execution; a materialized prompt with an
        # isolated worktree means Codex. Browser routing needs an explicit
        # activity because GUI and semantic work have different executors.
        if execution.get('command') is not None:
            activity = 'native'
        elif item['prompt_id'] and execution.get('worktree'):
            activity = 'coding'
    if activity not in ('coding','diagnostic','gui','native','semantic'):
        return {'state':'waiting','reason':'activity_missing'}
    if item['executor_policy']=='codex' and activity not in ('coding','diagnostic'):
        raise SchedulingError('codex_activity_required')
    if activity != 'native' and execution.get('command') is not None:
        raise SchedulingError('execution_context_activity_conflict')
    if activity not in ('gui','semantic') and execution.get('project_url') is not None:
        raise SchedulingError('execution_context_activity_conflict')
    prompt = None
    if activity == 'native':
        command = execution.get('command')
        if not isinstance(command,list) or not command or not all(isinstance(v,str) and v for v in command):
            return {'state':'waiting','reason':'native_command_missing'}
        if item['repo'] and not execution.get('worktree'):
            return {'state':'waiting','reason':'execution_worktree_missing'}
    elif activity in ('coding','diagnostic'):
        if not item['prompt_id']:
            return {'state':'waiting','reason':'codex_prompt_materialization_required'}
        if not execution.get('worktree'):
            return {'state':'waiting','reason':'execution_worktree_missing'}
        prompt = conn.execute('SELECT model,reasoning,prompt_type FROM prompts WHERE prompt_id=?',
                              (item['prompt_id'],)).fetchone()
        if not prompt or not prompt['model'] or not prompt['reasoning']:
            return {'state':'waiting','reason':'codex_exact_metadata_missing'}
        if execution.get('model') not in (None,prompt['model']) or execution.get('reasoning') not in (None,prompt['reasoning']):
            raise SchedulingError('codex_metadata_mismatch')
    else:
        url = execution.get('project_url')
        if not isinstance(url,str) or not url.startswith('https://chatgpt.com/'):
            return {'state':'waiting','reason':'chatgpt_project_url_missing'}
        if not item['objective'] or not json.loads(item['acceptance_json'] or '[]'):
            return {'state':'waiting','reason':'browser_objective_or_acceptance_missing'}
    if execution.get('resources') is not None and not isinstance(execution['resources'],list):
        raise SchedulingError('invalid_resources')
    configure(conn,work_item_id,activity=activity,
              model=prompt['model'] if activity in ('coding','diagnostic') else None,
              reasoning=prompt['reasoning'] if activity in ('coding','diagnostic') else None,
              worktree=execution.get('worktree'),project_url=execution.get('project_url'),
              goal_mode=bool(prompt['prompt_type']=='Goal') if activity in ('coding','diagnostic') else False,
              command=execution.get('command'),resources=execution.get('resources') or (),
              max_attempts=execution.get('max_attempts',3))
    return {'state':'ready'}


def execution_metadata(conn, item, spec, executor):
    result = dict(spec)
    result['executor'] = executor
    result['repo'] = item['repo']
    result['prompt_id'] = item['prompt_id']
    if executor in ('codex','symphony'):
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
        if executor=='symphony':
            from c3_symphony_bridge import BridgeError, resolve_model, resolve_reasoning
            try:
                result['model_id']=resolve_model(spec['model'])
                result['reasoning_effort']=resolve_reasoning(spec['reasoning'])
            except BridgeError as exc:
                raise SchedulingError('symphony_exact_metadata_invalid') from exc
    if executor in ('chatgpt','rdc') and spec['activity'] in ('gui','semantic'):
        if not spec['project_url'] or not str(spec['project_url']).startswith('https://chatgpt.com/'):
            raise SchedulingError('chatgpt_project_url_required')
    return result


def _repo_writer_worktrees(conn, repo, work_item_id):
    """Return same-repo worktrees that represent actual writer ownership."""
    return conn.execute('''SELECT s.worktree FROM work_items w
      LEFT JOIN work_item_execution_specs s USING(work_item_id)
      JOIN v_work_item_execution_liveness live USING(work_item_id)
      WHERE w.repo=? AND w.work_item_id<>? AND live.has_live_executor=1''',
      (repo,work_item_id)).fetchall()


def _repo_writer_conflict(conn, item, spec):
    peers = _repo_writer_worktrees(conn,item['repo'],item['work_item_id'])
    return any(not spec['worktree'] or not peer['worktree']
               or spec['worktree']==peer['worktree'] for peer in peers)


def dispatchable(conn, item, coding_route=None):
    """Whether an item could acquire a new C2 run with current shared locks."""
    ancestor = item['parent_id']
    seen = set()
    while ancestor:
        if ancestor in seen:
            raise SchedulingError('hierarchy_cycle')
        seen.add(ancestor)
        row = conn.execute('''SELECT w.parent_id,live.has_live_executor
          FROM work_items w JOIN v_work_item_execution_liveness live USING(work_item_id)
          WHERE w.work_item_id=?''', (ancestor,)).fetchone()
        if row['has_live_executor']:
            return False
        ancestor = row['parent_id']
    spec = conn.execute('SELECT * FROM work_item_execution_specs WHERE work_item_id=?',
                        (item['work_item_id'],)).fetchone()
    if not spec:
        return False
    executor = routed_executor(item['executor_policy'],spec['activity'],item['repo'],coding_route)
    if executor in (None, 'human', 'symphony-unhealthy'):
        return False
    resources = set(json.loads(spec['resources_json']))
    if executor=='symphony':
        resources.add('symphony:backend')
    if item['repo']:
        resources.add('worktree:'+spec['worktree'] if spec['worktree'] else 'repo:'+item['repo'])
        if _repo_writer_conflict(conn,item,spec):
            return False
    if any(conn.execute('SELECT 1 FROM work_item_resource_leases WHERE resource=?',(r,)).fetchone() for r in resources):
        return False
    attempt = 1 + conn.execute('SELECT COUNT(*) FROM work_item_runs WHERE work_item_id=?',
                               (item['work_item_id'],)).fetchone()[0]
    if attempt > spec['max_attempts']:
        return False
    try:
        execution_metadata(conn, item, spec, executor)
    except SchedulingError:
        return False
    return True


def inbox_drain_state(conn):
    """Report whether Inbox triage is pending/reconciling for observability."""
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='issue_inbox'").fetchone():
        return None
    if conn.execute("SELECT 1 FROM issue_inbox WHERE state='pending' LIMIT 1").fetchone():
        return 'pending'
    triage = conn.execute("""SELECT w.status FROM work_items w
        JOIN work_item_tags t USING(work_item_id)
        WHERE t.tag='c2:issue-triage'
        ORDER BY w.created_at DESC,w.work_item_id DESC LIMIT 1""").fetchone()
    if triage and triage['status'] not in ('completed','failed','cancelled','superseded','waived'):
        return 'reconciling'
    return None


def inbox_gate_exempt(conn, item):
    return bool(conn.execute("""SELECT 1 FROM work_item_tags
        WHERE work_item_id=? AND tag IN ('c2:issue-triage','priority:p0') LIMIT 1""",
        (item['work_item_id'],)).fetchone())


def schedule(conn, *, event_key, now=None, max_parallel=DEFAULT_PARALLEL_CAP, lease_seconds=120,
             chatgpt_lane_degraded=False, coding_route=None):
    _transaction(conn)
    now=time.time() if now is None else now
    if not event_key or lease_seconds <= 0:
        raise SchedulingError('invalid_scheduler_event')
    if not 1 <= max_parallel <= HARD_PARALLEL_CAP:
        raise SchedulingError('parallel_cap_out_of_range')
    if coding_route is not None:
        if (not isinstance(coding_route,dict)
                or coding_route.get('mode') not in ('legacy','canary','production','invalid')
                or not isinstance(coding_route.get('healthy'),bool)
                or not isinstance(coding_route.get('source_repos'),list)):
            raise SchedulingError('invalid_coding_route')
        if coding_route['mode']=='production' and coding_route.get('tracker_repo')=='gernalix/symphony-canary':
            raise SchedulingError('production_tracker_is_canary')
        if coding_route['mode'] in ('canary','production') and (
                not coding_route.get('tracker_repo') or not coding_route['source_repos']):
            raise SchedulingError('tracker_or_source_allowlist_required')
    prior = conn.execute('SELECT result_json FROM work_item_scheduler_events WHERE event_key=?', (event_key,)).fetchone()
    if prior:
        return json.loads(prior[0])
    active = conn.execute('''SELECT COUNT(*) FROM v_work_item_execution_liveness
      WHERE has_live_executor=1''').fetchone()[0]
    results = []
    import c3_override
    c3_override.install_schema(conn)
    candidates = conn.execute('''SELECT w.*
      FROM v_work_item_runnable w
      LEFT JOIN c3_user_order u ON u.work_item_id=w.work_item_id
      ORDER BY CASE WHEN u.rank IS NULL THEN 1 ELSE 0 END,
        u.rank,
        CASE
        WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p0') THEN 0
        WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p1') THEN 1
        WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p2') THEN 2
        ELSE 3 END,
        COALESCE(w.sort_order,2147483647),w.created_at,w.work_item_id''').fetchall()
    # Inbox triage has its own P0 ordering and exclusive resource lease. Do not
    # globally filter unrelated candidates while a long drain is in progress.
    override = read_override(conn)
    scoped = []
    if override:
        for item in candidates:
            if not override_matches(conn,item,override):
                continue
            if dispatchable(conn,item,coding_route):
                scoped.append(item)
    if scoped:
        candidates = scoped
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
            row = conn.execute('''SELECT w.parent_id,live.has_live_executor
              FROM work_items w JOIN v_work_item_execution_liveness live USING(work_item_id)
              WHERE w.work_item_id=?''', (ancestor,)).fetchone()
            if row['has_live_executor']:
                blocked = True
                break
            ancestor = row['parent_id']
        if blocked:
            continue
        spec = conn.execute('SELECT * FROM work_item_execution_specs WHERE work_item_id=?', (item['work_item_id'],)).fetchone()
        if not spec:
            continue  # No guessed semantic classification or implicit launch.
        executor = routed_executor(item['executor_policy'],spec['activity'],item['repo'],coding_route)
        if executor in (None, 'human', 'symphony-unhealthy'):
            continue
        if chatgpt_lane_degraded and spec['activity'] in ('gui','semantic'):
            continue
        resources = set(json.loads(spec['resources_json']))
        if executor=='symphony':
            resources.add('symphony:backend')
        if item['repo']:
            # Default exclusive repo writer. Explicit isolated worktree resource
            # is permitted only when the spec supplies the actual worktree.
            resources.add('worktree:'+spec['worktree'] if spec['worktree'] else 'repo:'+item['repo'])
            if _repo_writer_conflict(conn,item,spec):
                continue
        if any(conn.execute('SELECT 1 FROM work_item_resource_leases WHERE resource=?',(r,)).fetchone() for r in resources):
            continue
        attempt = 1 + conn.execute('SELECT COUNT(*) FROM work_item_runs WHERE work_item_id=?',(item['work_item_id'],)).fetchone()[0]
        if attempt > spec['max_attempts']:
            continue
        try:
            metadata = execution_metadata(conn, item, spec, executor)
            if executor=='symphony':
                metadata['symphony_route']={
                    'mode':coding_route['mode'],
                    'tracker_repo':coding_route['tracker_repo'],
                    'source_repos':coding_route['source_repos'],
                }
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


def bind_executor(conn, run_id, *, executor_ref, chat_url, now=None):
    """Bind an active C2 run to its concrete ChatGPT/Codex conversation."""
    _transaction(conn)
    install_schema(conn)
    now=time.time() if now is None else now
    run=conn.execute('SELECT * FROM work_item_runs WHERE run_id=?',(run_id,)).fetchone()
    if not run:
        raise SchedulingError('run_not_found')
    executor_ref=str(executor_ref or '').strip()
    chat_url=str(chat_url or '').strip()
    if not executor_ref or not chat_url:
        raise SchedulingError('executor_binding_identity_required')
    executor=str(run['executor'])
    item_status=conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(run['work_item_id'],)).fetchone()[0]
    if executor=='codex':
        expected='codex://threads/'+executor_ref
        if chat_url != expected:
            raise SchedulingError('codex_deep_link_mismatch')
    elif executor in ('chatgpt','rdc'):
        if not chat_url.startswith('https://chatgpt.com/'):
            raise SchedulingError('chatgpt_chat_url_required')
    else:
        raise SchedulingError('executor_binding_unsupported:'+executor)
    prior=conn.execute('SELECT * FROM work_item_executor_bindings WHERE run_id=?',(run_id,)).fetchone()
    if prior:
        if (str(prior['executor'])!=executor or str(prior['executor_ref'])!=executor_ref
                or str(prior['chat_url'])!=chat_url
                or str(prior['work_item_id'])!=str(run['work_item_id'])):
            raise SchedulingError('executor_binding_conflict')
        if run['state'] in ('running','recovering') and item_status=='running':
            executor_started(conn,run_id=run_id,executor_ref=executor_ref,chat_url=chat_url,now=now)
        return dict(prior)
    if run['state'] not in ('claimed','running','recovering'):
        raise SchedulingError('run_not_active')
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='issue_inbox'").fetchone():
        conflict=conn.execute('''SELECT 1 FROM issue_inbox WHERE origin_run_id=?
          AND ((chat_url IS NOT NULL AND chat_url<>?) OR
               (executor_ref IS NOT NULL AND executor_ref<>?)) LIMIT 1''',
          (run_id,chat_url,executor_ref)).fetchone()
        if conflict:
            raise SchedulingError('executor_binding_conflict')
    try:
        conn.execute('''INSERT INTO work_item_executor_bindings(
          run_id,work_item_id,executor,executor_ref,chat_url,bound_at
        ) VALUES(?,?,?,?,?,?)''',
        (run_id,run['work_item_id'],executor,executor_ref,chat_url,now))
    except sqlite3.IntegrityError as exc:
        raise SchedulingError('executor_binding_conflict') from exc
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='issue_inbox'").fetchone():
        conn.execute('''UPDATE issue_inbox SET executor=?,executor_ref=?,chat_url=?
          WHERE origin_run_id=? AND chat_url IS NULL''',
          (executor,executor_ref,chat_url,run_id))
    if run['state'] in ('running','recovering') and item_status=='running':
        executor_started(conn,run_id=run_id,executor_ref=executor_ref,chat_url=chat_url,now=now)
    return dict(conn.execute('SELECT * FROM work_item_executor_bindings WHERE run_id=?',(run_id,)).fetchone())


def executor_started(conn, *, run_id=None, work_item_id=None, prompt_id=None,
                     executor=None, executor_ref=None, chat_url=None, now=None):
    """Record that an executor has actually begun handling an already-running C2 item."""
    _transaction(conn)
    install_schema(conn)
    now=time.time() if now is None else now
    run=None
    if run_id:
        run=conn.execute('SELECT * FROM work_item_runs WHERE run_id=?',(run_id,)).fetchone()
        if not run:
            raise SchedulingError('executor_start_run_not_found')
        if run['state'] not in ('running','recovering'):
            raise SchedulingError('executor_start_run_not_active')
        if work_item_id and work_item_id!=run['work_item_id']:
            raise SchedulingError('executor_start_work_item_mismatch')
        work_item_id=run['work_item_id']
        if executor and executor!=run['executor']:
            raise SchedulingError('executor_start_executor_mismatch')
        executor=run['executor']
    if prompt_id and not work_item_id:
        row=conn.execute('SELECT work_item_id FROM work_items WHERE prompt_id=?',(prompt_id,)).fetchone()
        if not row:
            raise SchedulingError('executor_start_prompt_not_found')
        work_item_id=row['work_item_id']
    if not work_item_id:
        raise SchedulingError('executor_start_identity_required')
    item=conn.execute('SELECT status,prompt_id FROM work_items WHERE work_item_id=?',(work_item_id,)).fetchone()
    if not item:
        raise SchedulingError('executor_start_work_item_not_found')
    if item['status']=='pending' and run is None:
        if item['prompt_id']:
            raise SchedulingError('executor_start_prompt_requires_roadmap_start')
        runnable=conn.execute('SELECT 1 FROM v_work_item_runnable WHERE work_item_id=?',(work_item_id,)).fetchone()
        if not runnable:
            raise SchedulingError('executor_start_work_item_not_runnable')
        pending=conn.execute('''SELECT w.work_item_id,w.repo,s.worktree
          FROM work_items w LEFT JOIN work_item_execution_specs s USING(work_item_id)
          WHERE w.work_item_id=?''',(work_item_id,)).fetchone()
        if pending['repo'] and _repo_writer_conflict(conn,pending,pending):
            raise SchedulingError('executor_start_repo_conflict')
        conn.execute("UPDATE work_items SET status='running',current_action='Executor started',blocker=NULL WHERE work_item_id=?",
                     (work_item_id,))
        item=conn.execute('SELECT status,prompt_id FROM work_items WHERE work_item_id=?',(work_item_id,)).fetchone()
    if item['status']!='running':
        raise SchedulingError('executor_start_requires_running_item')
    if prompt_id and item['prompt_id']!=prompt_id:
        raise SchedulingError('executor_start_prompt_mismatch')
    prompt_id=item['prompt_id']
    executor=str(executor or '').strip()
    if not executor:
        raise SchedulingError('executor_start_executor_required')
    executor_ref=str(executor_ref or '').strip() or None
    chat_url=str(chat_url or '').strip() or None
    receipt_id='run:'+str(run_id) if run_id else 'work-item:'+work_item_id+':'+executor
    existing=conn.execute('SELECT * FROM work_item_executor_starts WHERE receipt_id=?',(receipt_id,)).fetchone()
    if existing:
        if (existing['work_item_id']!=work_item_id or existing['prompt_id']!=prompt_id
                or existing['executor']!=executor):
            raise SchedulingError('executor_start_receipt_conflict')
        updates=[]; values=[]
        for field,value in (('executor_ref',executor_ref),('chat_url',chat_url)):
            prior=existing[field]
            if prior and value and prior!=value:
                raise SchedulingError('executor_start_binding_conflict')
            if not prior and value:
                updates.append(field+'=?'); values.append(value)
        if updates:
            conn.execute('UPDATE work_item_executor_starts SET '+','.join(updates)+' WHERE receipt_id=?',
                         (*values,receipt_id))
        return dict(conn.execute('SELECT * FROM work_item_executor_starts WHERE receipt_id=?',
                                 (receipt_id,)).fetchone())
    conn.execute("""INSERT INTO work_item_executor_starts(
      receipt_id,work_item_id,run_id,prompt_id,executor,executor_ref,chat_url,started_at
      ) VALUES(?,?,?,?,?,?,?,?)""",
      (receipt_id,work_item_id,run_id,prompt_id,executor,executor_ref,chat_url,now))
    return dict(conn.execute('SELECT * FROM work_item_executor_starts WHERE receipt_id=?',
                             (receipt_id,)).fetchone())


def checkpoint(conn, run_id, commit):
    _transaction(conn)
    if not isinstance(commit,str) or len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise SchedulingError('invalid_checkpoint_commit')
    result=conn.execute("UPDATE work_item_runs SET checkpoint_commit=? WHERE run_id=? AND state IN ('claimed','running','recovering')",(commit,run_id))
    if not result.rowcount:
        raise SchedulingError('run_not_active')


def record_checkpoint(conn, work_item_id, *, current_step, next_action,
                      completed=(), remaining=(), evidence=(), blocker=None,
                      objective=None, source_commit=None):
    _transaction(conn)
    row=conn.execute('SELECT status FROM work_items WHERE work_item_id=?',(work_item_id,)).fetchone()
    if not row or row['status'] not in ('pending','running','waiting','blocked'):
        raise SchedulingError('checkpoint_work_item_not_active')
    if not isinstance(completed,(list,tuple)) or not isinstance(remaining,(list,tuple)) or not isinstance(evidence,(list,tuple)):
        raise SchedulingError('checkpoint_lists_required')
    if not str(next_action).strip():
        raise SchedulingError('checkpoint_next_action_required')
    body={'work_item_id':work_item_id,'current_step':current_step,'next_action':next_action,
          'completed':list(completed),'remaining':list(remaining),'evidence':list(evidence),
          'blocker':blocker,'objective':objective,'source_commit':source_commit}
    digest=hashlib.sha256(json.dumps(body,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    conn.execute('''INSERT OR IGNORE INTO work_item_checkpoints
      (work_item_id,source_file,source_commit,source_sha256,objective,
       current_step,next_action,blocker,completed_json,remaining_json,
       evidence_json,captured_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
      (work_item_id,'c2-writer',source_commit,digest,objective,current_step,next_action,
       blocker,json.dumps(list(completed)),json.dumps(list(remaining)),
       json.dumps(list(evidence)),time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    conn.execute('''UPDATE work_items SET current_action=?,next_action=?,blocker=?
      WHERE work_item_id=?''',(current_step,next_action,blocker,work_item_id))
    return digest



RESULT_STATUS = {'PASS':'completed','BLOCKED':'blocked','FAIL':'failed','CANCELLED':'cancelled'}

def executor_result(conn, *, outcome, work_item_id=None, prompt_id=None, run_id=None,
                    summary=None, completed=(), remaining=(), evidence=(), blocker=None,
                    next_action=None, strict_contract=False):
    """Record one idempotent executor receipt; prompt lifecycle is finalized by c2_mutations."""
    _transaction(conn)
    if outcome not in RESULT_STATUS:
        raise SchedulingError('invalid_executor_outcome')
    for name,value in (('completed',completed),('remaining',remaining),('evidence',evidence)):
        if not isinstance(value,(list,tuple)):
            raise SchedulingError('executor_result_'+name+'_list_required')
    run=None
    if run_id:
        run=conn.execute('SELECT * FROM work_item_runs WHERE run_id=?',(run_id,)).fetchone()
        if not run:
            raise SchedulingError('executor_result_run_not_found')
        if work_item_id and work_item_id!=run['work_item_id']:
            raise SchedulingError('executor_result_work_item_mismatch')
        work_item_id=run['work_item_id']
    if prompt_id and not work_item_id:
        row=conn.execute('SELECT work_item_id FROM work_items WHERE prompt_id=?',(prompt_id,)).fetchone()
        if not row:
            raise SchedulingError('executor_result_prompt_not_found')
        work_item_id=row['work_item_id']
    if not work_item_id:
        raise SchedulingError('executor_result_identity_required')
    item=conn.execute('SELECT * FROM work_items WHERE work_item_id=?',(work_item_id,)).fetchone()
    if not item:
        raise SchedulingError('executor_result_work_item_not_found')
    if prompt_id and item['prompt_id']!=prompt_id:
        raise SchedulingError('executor_result_prompt_mismatch')
    prompt_id=item['prompt_id']
    if run is None:
        latest_run=conn.execute("""SELECT * FROM work_item_runs WHERE work_item_id=?
          ORDER BY created_at DESC LIMIT 1""",(work_item_id,)).fetchone()
        manual_start=conn.execute("""SELECT started_at FROM work_item_executor_starts
          WHERE work_item_id=? AND run_id IS NULL
          ORDER BY started_at DESC LIMIT 1""",(work_item_id,)).fetchone()
        # A fenced manual takeover after a failed scheduled run owns the next
        # result. Keep the old run failed and record a runless receipt.
        if latest_run and not (manual_start and manual_start['started_at'] > latest_run['created_at']):
            run=latest_run
            run_id=run['run_id']
    completed=[str(v).strip() for v in completed if str(v).strip()]
    remaining=[str(v).strip() for v in remaining if str(v).strip()]
    evidence=[str(v).strip() for v in evidence if str(v).strip()]
    blocker=str(blocker).strip() if blocker is not None and str(blocker).strip() else None
    next_action=str(next_action).strip() if next_action is not None and str(next_action).strip() else None
    summary=str(summary).strip() if summary is not None and str(summary).strip() else None
    if outcome=='PASS':
        if remaining or blocker:
            raise SchedulingError('pass_requires_no_remaining_or_blocker')
        if not evidence:
            raise SchedulingError('completion_evidence_required')
        if strict_contract:
            acceptance=set(json.loads(item['acceptance_json'] or '[]'))
            if acceptance and not acceptance.issubset(set(completed)):
                raise SchedulingError('acceptance_criteria_not_verified')
    elif outcome in ('BLOCKED','FAIL') and strict_contract:
        if not blocker:
            raise SchedulingError(outcome.lower()+'_requires_blocker')
        if outcome=='BLOCKED' and not next_action:
            raise SchedulingError('blocked_requires_next_action')
    payload={'outcome':outcome,'work_item_id':work_item_id,'run_id':run_id,
             'prompt_id':prompt_id,'summary':summary,'completed':completed,
             'remaining':remaining,'evidence':evidence,'blocker':blocker,
             'next_action':next_action,'strict_contract':bool(strict_contract)}
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    # A scheduled run has one immutable result.  Manual/non-prompt work has no
    # run identity, so retain every lifecycle-admitted result as its own
    # immutable receipt instead of conflating different submissions.
    receipt_id=('run:'+str(run_id) if run_id else
                ('prompt:'+str(prompt_id) if prompt_id else
                 'work-item:'+work_item_id+':'+digest[:32]))
    existing=conn.execute('SELECT payload_sha256,outcome FROM work_item_result_receipts WHERE receipt_id=?',
                          (receipt_id,)).fetchone()
    if existing:
        if existing['payload_sha256']!=digest or existing['outcome']!=outcome:
            raise SchedulingError('executor_result_receipt_conflict')
        return {'receipt_id':receipt_id,'work_item_id':work_item_id,'run_id':run_id,
                'prompt_id':prompt_id,'outcome':outcome,'target_status':RESULT_STATUS[outcome],
                'idempotent':True}
    if outcome=='PASS':
        missing=conn.execute('''WITH RECURSIVE children(id) AS (
          SELECT work_item_id FROM work_items WHERE parent_id=?
          UNION SELECT w.work_item_id FROM work_items w JOIN children c ON w.parent_id=c.id)
          SELECT 1 FROM children c JOIN work_items w ON w.work_item_id=c.id
          WHERE w.required=1 AND w.status NOT IN ('completed','waived') LIMIT 1''',
          (work_item_id,)).fetchone()
        if missing:
            raise SchedulingError('required_children_incomplete')
    if not prompt_id:
        target=RESULT_STATUS[outcome]
        if run:
            run_target='completed' if outcome=='PASS' else 'failed'
            if run['state'] not in (run_target,'running','recovering','claimed'):
                raise SchedulingError('executor_result_run_state_conflict')
            conn.execute('UPDATE work_item_runs SET state=? WHERE run_id=?',(run_target,run_id))
            conn.execute('DELETE FROM work_item_resource_leases WHERE run_id=?',(run_id,))
        if item['status'] not in (target,'pending','running','waiting','blocked'):
            raise SchedulingError('executor_result_item_state_conflict')
    conn.execute("""INSERT INTO work_item_result_receipts(
      receipt_id,work_item_id,run_id,prompt_id,outcome,summary,completed_json,remaining_json,
      evidence_json,blocker,next_action,strict_contract,payload_sha256,captured_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
      (receipt_id,work_item_id,run_id,prompt_id,outcome,summary,json.dumps(completed),
       json.dumps(remaining),json.dumps(evidence),blocker,next_action,int(bool(strict_contract)),
       digest,time.time()))
    for fact in evidence:
        conn.execute("""INSERT OR IGNORE INTO work_item_evidence
          (work_item_id,evidence_kind,label,uri,value_json,created_at)
          VALUES(?,'executor_result',?,NULL,?,?)""",
          (work_item_id,fact[:120],json.dumps(fact,ensure_ascii=False),
           time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    if item['status'] in ('pending','running','waiting','blocked'):
        conn.execute("""UPDATE work_items SET current_action=?,next_action=?,blocker=?
          WHERE work_item_id=?""",(summary or ('Completed' if outcome=='PASS' else outcome),
                                  next_action,blocker,work_item_id))
    if not prompt_id:
        conn.execute('UPDATE work_items SET status=?,blocker=? WHERE work_item_id=?',
                     (target,blocker,work_item_id))
        if outcome=='PASS':
            enqueue_milestone(conn,work_item_id)
    return {'receipt_id':receipt_id,'work_item_id':work_item_id,'run_id':run_id,
            'prompt_id':prompt_id,'outcome':outcome,'target_status':RESULT_STATUS[outcome],
            'idempotent':False}


def release_unstarted_symphony_run(conn, *, run_id, reason):
    """Release a Symphony claim only before any external executor identity exists."""
    _transaction(conn)
    reason=str(reason or '').strip()
    if not reason:
        raise SchedulingError('release_reason_required')
    row=conn.execute("""SELECT r.*,w.status AS item_status FROM work_item_runs r
        JOIN work_items w USING(work_item_id) WHERE r.run_id=?""",(run_id,)).fetchone()
    if not row or row['executor']!='symphony':
        raise SchedulingError('unstarted_symphony_run_required')
    if row['state'] not in ('claimed','running','recovering') or row['item_status']!='running':
        raise SchedulingError('unstarted_symphony_run_not_active')
    binding=conn.execute("SELECT 1 FROM work_item_executor_bindings WHERE run_id=? LIMIT 1",
                         (run_id,)).fetchone()
    start=conn.execute("""SELECT executor_ref,chat_url FROM work_item_executor_starts
        WHERE run_id=? ORDER BY started_at DESC LIMIT 1""",(run_id,)).fetchone()
    result=conn.execute("SELECT 1 FROM work_item_result_receipts WHERE run_id=? LIMIT 1",
                        (run_id,)).fetchone()
    if binding or result or (start and (start['executor_ref'] or start['chat_url'])):
        raise SchedulingError('symphony_run_already_dispatched')
    conn.execute("UPDATE work_item_runs SET state='failed' WHERE run_id=?",(run_id,))
    conn.execute("DELETE FROM work_item_resource_leases WHERE run_id=?",(run_id,))
    conn.execute("""UPDATE work_items SET status='pending',blocker=NULL,
        current_action=?,next_action=NULL WHERE work_item_id=?""",
        ('Pre-dispatch Symphony claim released: '+reason[:220],row['work_item_id']))
    return {'run_id':run_id,'work_item_id':row['work_item_id'],'state':'released'}


def recover(conn, *, now=None):
    _transaction(conn)
    now=time.time() if now is None else now
    rows = conn.execute("SELECT * FROM work_item_runs WHERE state IN ('claimed','running') AND lease_until<=?",(now,)).fetchall()
    for row in rows:
        conn.execute("UPDATE work_item_runs SET state='recovering' WHERE run_id=?",(row['run_id'],))
    # Preserve the same run identity and locks; executor must inspect its durable
    # worker receipt before resume. A lost acknowledgement is not a failed run.
    return [dict(r) for r in conn.execute("SELECT * FROM work_item_runs WHERE state='recovering'")]


def quarantine_browser_run(conn, run_id, *, reason):
    _transaction(conn)
    row=conn.execute('''SELECT r.state,r.executor,w.prompt_id,w.status
      FROM work_item_runs r JOIN work_items w USING(work_item_id)
      WHERE r.run_id=?''',(run_id,)).fetchone()
    if not row or row['executor'] not in ('rdc','chatgpt') or row['prompt_id']:
        raise SchedulingError('nonprompt_browser_run_required')
    if row['state']=='failed' and row['status']=='blocked':
        return
    if row['state'] not in ('claimed','running','recovering') or row['status']!='running':
        raise SchedulingError('run_not_active')
    conn.execute("UPDATE work_item_runs SET state='failed' WHERE run_id=?",(run_id,))
    conn.execute('DELETE FROM work_item_resource_leases WHERE run_id=?',(run_id,))
    conn.execute('''UPDATE work_items SET status='blocked',blocker=?
      WHERE work_item_id=(SELECT work_item_id FROM work_item_runs WHERE run_id=?)''',
      (str(reason)[:300],run_id))


def finish_browser_work_item(conn, work_item_id, *, evidence):
    _transaction(conn)
    row=conn.execute('''SELECT r.run_id,r.executor,r.state,w.prompt_id,w.status
      FROM work_items w JOIN work_item_runs r USING(work_item_id)
      WHERE w.work_item_id=? ORDER BY r.created_at DESC LIMIT 1''',(work_item_id,)).fetchone()
    if not row or row['executor'] not in ('rdc','chatgpt') or row['prompt_id']:
        raise SchedulingError('nonprompt_browser_run_required')
    if row['state']=='completed' and row['status']=='completed':
        return
    if row['state'] not in ('running','recovering') or row['status']!='running':
        raise SchedulingError('run_not_active')
    if conn.execute("SELECT 1 FROM work_item_tags WHERE work_item_id=? AND tag='c2:issue-triage'", (work_item_id,)).fetchone():
        if conn.execute("SELECT 1 FROM issue_inbox WHERE state='pending' LIMIT 1").fetchone():
            raise SchedulingError('issue_triage_pending_rows')
    cp=conn.execute('''SELECT remaining_json,blocker,evidence_json
      FROM work_item_checkpoints WHERE work_item_id=? AND source_file='c2-writer'
      ORDER BY checkpoint_id DESC LIMIT 1''',(work_item_id,)).fetchone()
    if not cp or json.loads(cp['remaining_json'] or '[]') or cp['blocker']:
        raise SchedulingError('acceptance_checkpoint_incomplete')
    if not isinstance(evidence,list) or not evidence or not all(str(v).strip() for v in evidence):
        raise SchedulingError('completion_evidence_required')
    missing=conn.execute('''WITH RECURSIVE children(id) AS (
      SELECT work_item_id FROM work_items WHERE parent_id=?
      UNION SELECT w.work_item_id FROM work_items w JOIN children c ON w.parent_id=c.id)
      SELECT 1 FROM children c JOIN work_items w ON w.work_item_id=c.id
      WHERE w.required=1 AND w.status NOT IN ('completed','waived') LIMIT 1''',(work_item_id,)).fetchone()
    if missing:
        raise SchedulingError('required_children_incomplete')
    conn.execute("UPDATE work_item_runs SET state='completed' WHERE run_id=?",(row['run_id'],))
    conn.execute('DELETE FROM work_item_resource_leases WHERE run_id=?',(row['run_id'],))
    conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?",(work_item_id,))
    for fact in evidence:
        payload=json.dumps(str(fact),ensure_ascii=False)
        conn.execute('''INSERT OR IGNORE INTO work_item_evidence
           (work_item_id,evidence_kind,label,uri,value_json,created_at)
           VALUES(?,'completion',?,NULL,?,?)''',
           (work_item_id,str(fact)[:120],payload,time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    enqueue_milestone(conn,work_item_id)


def verify_work_item(conn, work_item_id, *, evidence):
    """Close a non-prompt item only after its full acceptance is checkpointed."""
    _transaction(conn)
    item=conn.execute('SELECT * FROM work_items WHERE work_item_id=?',(work_item_id,)).fetchone()
    if not item or item['status']!='pending' or item['prompt_id']:
        raise SchedulingError('pending_nonprompt_item_required')
    if conn.execute('SELECT 1 FROM work_item_runs WHERE work_item_id=?',(work_item_id,)).fetchone():
        raise SchedulingError('work_item_has_execution_run')
    checkpoint=conn.execute('''SELECT completed_json,remaining_json,blocker FROM work_item_checkpoints
      WHERE work_item_id=? AND source_file='c2-writer' ORDER BY checkpoint_id DESC LIMIT 1''',
      (work_item_id,)).fetchone()
    if not checkpoint or json.loads(checkpoint['remaining_json'] or '[]') or checkpoint['blocker']:
        raise SchedulingError('acceptance_checkpoint_incomplete')
    completed=set(json.loads(checkpoint['completed_json'] or '[]'))
    acceptance=set(json.loads(item['acceptance_json'] or '[]'))
    if not acceptance or not acceptance.issubset(completed):
        raise SchedulingError('acceptance_criteria_not_verified')
    if not isinstance(evidence,list) or not evidence or not all(isinstance(v,str) and v.strip() for v in evidence):
        raise SchedulingError('completion_evidence_required')
    missing=conn.execute('''WITH RECURSIVE children(id) AS (
      SELECT work_item_id FROM work_items WHERE parent_id=?
      UNION SELECT w.work_item_id FROM work_items w JOIN children c ON w.parent_id=c.id)
      SELECT 1 FROM children c JOIN work_items w ON w.work_item_id=c.id
      WHERE w.required=1 AND w.status NOT IN ('completed','waived') LIMIT 1''',(work_item_id,)).fetchone()
    if missing:
        raise SchedulingError('required_children_incomplete')
    conn.execute("UPDATE work_items SET status='completed' WHERE work_item_id=?",(work_item_id,))
    for fact in evidence:
        conn.execute('''INSERT OR IGNORE INTO work_item_evidence
          (work_item_id,evidence_kind,label,uri,value_json,created_at)
          VALUES(?,'completion',?,NULL,?,?)''',
          (work_item_id,fact[:120],json.dumps(fact,ensure_ascii=False),
           time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    enqueue_milestone(conn,work_item_id)


def complete_verified(conn, work_item_id, *, source_commit, evidence):
    """Close work completed outside C2 scheduling only after its writer checkpoint is clear."""
    _transaction(conn)
    item=conn.execute('SELECT status,prompt_id FROM work_items WHERE work_item_id=?',
        (work_item_id,)).fetchone()
    if not item or item['prompt_id'] or item['status'] not in ('pending','completed'):
        raise SchedulingError('nonprompt_pending_work_item_required')
    if item['status']=='completed':
        return
    if not isinstance(evidence,list) or not evidence or not all(str(v).strip() for v in evidence):
        raise SchedulingError('completion_evidence_required')
    if conn.execute('''SELECT 1 FROM work_item_runs WHERE work_item_id=?
      AND state IN ('claimed','running','recovering')''',(work_item_id,)).fetchone():
        raise SchedulingError('active_run_requires_normal_completion')
    cp=conn.execute('''SELECT source_commit,remaining_json,blocker,evidence_json
      FROM work_item_checkpoints WHERE work_item_id=? AND source_file='c2-writer'
      ORDER BY checkpoint_id DESC LIMIT 1''',(work_item_id,)).fetchone()
    if (not cp or cp['source_commit']!=source_commit or
        json.loads(cp['remaining_json'] or '[]') or cp['blocker'] or
        not json.loads(cp['evidence_json'] or '[]')):
        raise SchedulingError('acceptance_checkpoint_incomplete')
    missing=conn.execute('''WITH RECURSIVE children(id) AS (
      SELECT work_item_id FROM work_items WHERE parent_id=?
      UNION SELECT w.work_item_id FROM work_items w JOIN children c ON w.parent_id=c.id)
      SELECT 1 FROM children c JOIN work_items w ON w.work_item_id=c.id
      WHERE w.required=1 AND w.status NOT IN ('completed','waived') LIMIT 1''',
      (work_item_id,)).fetchone()
    if missing:
        raise SchedulingError('required_children_incomplete')
    conn.execute("UPDATE work_items SET status='completed',blocker=NULL WHERE work_item_id=?",
        (work_item_id,))
    for fact in evidence:
        conn.execute('''INSERT OR IGNORE INTO work_item_evidence
           (work_item_id,evidence_kind,label,uri,value_json,created_at)
           VALUES(?,'completion',?,NULL,?,?)''',
           (work_item_id,str(fact)[:120],json.dumps(str(fact),ensure_ascii=False),
            time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
    enqueue_milestone(conn,work_item_id)


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
    if succeeded:
        enqueue_milestone(conn,run['work_item_id'])


def reconcile_terminal_run(conn, run_id):
    """Release a coding run only after the canonical terminal writer has acted."""
    _transaction(conn)
    row=conn.execute('''SELECT r.state,r.executor,w.status AS item_status
      FROM work_item_runs r JOIN work_items w USING(work_item_id)
      WHERE r.run_id=?''',(run_id,)).fetchone()
    if not row or row['executor'] not in ('codex','symphony'):
        raise SchedulingError('coding_run_required')
    if row['item_status'] not in ('completed','failed','blocked','cancelled'):
        raise SchedulingError('canonical_terminal_state_required')
    target='completed' if row['item_status']=='completed' else 'failed'
    if row['state']==target:
        return
    if row['state'] not in ('claimed','running','recovering'):
        raise SchedulingError('run_not_active')
    conn.execute('UPDATE work_item_runs SET state=? WHERE run_id=?',(target,run_id))
    conn.execute('DELETE FROM work_item_resource_leases WHERE run_id=?',(run_id,))
    if target=='completed':
        work_item_id=conn.execute('SELECT work_item_id FROM work_item_runs WHERE run_id=?',(run_id,)).fetchone()[0]
        enqueue_milestone(conn,work_item_id)


def enqueue_milestone(conn, work_item_id):
    _transaction(conn)
    item=conn.execute('''SELECT w.work_item_id,w.title,w.kind,w.status,w.parent_id,
       parent.next_action AS parent_next_action
       FROM work_items w LEFT JOIN work_items parent ON parent.work_item_id=w.parent_id
       WHERE w.work_item_id=?''',(work_item_id,)).fetchone()
    if not item or item['status']!='completed':
        raise SchedulingError('completed_work_item_required')
    tagged=conn.execute("SELECT 1 FROM work_item_tags WHERE work_item_id=? AND tag='milestone'",(work_item_id,)).fetchone()
    if item['kind'] not in ('goal','phase','gate') and not tagged:
        return False
    title='Checklist 2.0'
    label=(str(item['title']).splitlines() or [''])[0][:120]
    next_action=(str(item['parent_next_action'] or '').splitlines() or [''])[0][:160]
    message='Completato: '+label+'.'
    if next_action:
        message+=' Prossimo passo: '+next_action+'.'
    conn.execute('''INSERT OR IGNORE INTO c2_notification_outbox
       (event_key,work_item_id,title,message,state,created_at)
       VALUES(?,?,?,?,?,?)''',
       ('work-item:'+work_item_id+':completed',work_item_id,title,message,'pending',time.time()))
    return True


def claim_milestone(conn, event_key):
    _transaction(conn)
    row=conn.execute('SELECT * FROM c2_notification_outbox WHERE event_key=?',(event_key,)).fetchone()
    if not row:
        raise SchedulingError('milestone_not_found')
    if row['state']=='pending':
        conn.execute("UPDATE c2_notification_outbox SET state='sending' WHERE event_key=?",(event_key,))
    return dict(conn.execute('SELECT * FROM c2_notification_outbox WHERE event_key=?',(event_key,)).fetchone())


def mark_milestone(conn, event_key, *, sent, error=None):
    _transaction(conn)
    row=conn.execute('SELECT state FROM c2_notification_outbox WHERE event_key=?',(event_key,)).fetchone()
    if not row or row['state'] not in ('sending','sent','uncertain'):
        raise SchedulingError('milestone_not_claimed')
    if row['state'] in ('sent','uncertain'):
        return
    conn.execute('''UPDATE c2_notification_outbox
      SET state=?,sent_at=?,error=? WHERE event_key=?''',
      ('sent' if sent else 'uncertain',time.time() if sent else None,
       None if sent else str(error or 'delivery_unconfirmed')[:200],event_key))
