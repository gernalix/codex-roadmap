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
    if executor in ('chatgpt','rdc') and spec['activity'] in ('gui','semantic'):
        if not spec['project_url'] or not str(spec['project_url']).startswith('https://chatgpt.com/'):
            raise SchedulingError('chatgpt_project_url_required')
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
    candidates = conn.execute('''SELECT w.* FROM v_work_item_runnable w
      ORDER BY CASE
        WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p0') THEN 0
        WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p1') THEN 1
        WHEN EXISTS(SELECT 1 FROM work_item_tags t WHERE t.work_item_id=w.work_item_id AND t.tag='priority:p2') THEN 2
        ELSE 3 END,
        COALESCE(w.sort_order,2147483647),w.created_at,w.work_item_id''').fetchall()
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
