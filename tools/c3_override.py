"""Canonical C3 user operations. Called only inside the roadmap single writer."""
from __future__ import annotations
import hashlib
import json
import sqlite3
from datetime import datetime, timezone

USER_ACTIONS = {'pause', 'resume', 'stop', 'force-priority', 'move'}
DESTRUCTIVE_ACTIONS = {'cancel', 'delete'}
TERMINAL = {'completed', 'cancelled', 'superseded', 'waived'}


def install_schema(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS c3_user_events (
        request_id TEXT PRIMARY KEY, work_item_id TEXT NOT NULL,
        action TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL)''')
    conn.execute('CREATE TABLE IF NOT EXISTS c3_user_order (work_item_id TEXT PRIMARY KEY REFERENCES work_items(work_item_id), rank INTEGER NOT NULL)')
    conn.execute('''CREATE TABLE IF NOT EXISTS c3_user_state (
        work_item_id TEXT PRIMARY KEY REFERENCES work_items(work_item_id),
        paused INTEGER NOT NULL DEFAULT 0, deleted INTEGER NOT NULL DEFAULT 0,
        previous_status TEXT)''')


def graph(conn):
    items = {r['work_item_id']: dict(r) for r in conn.execute('SELECT * FROM work_items')}
    edges = [(r[0], r[1]) for r in conn.execute(
        'SELECT work_item_id,depends_on_work_item_id FROM work_item_dependencies WHERE required=1')]
    return items, edges


def impact(conn, work_item_id):
    items, edges = graph(conn)
    if work_item_id not in items:
        raise ValueError('work_item_not_found')
    affected = {work_item_id}
    while True:
        new = affected | {i for i, p in edges if p in affected} | {
            i for i, row in items.items() if row['parent_id'] in affected}
        if new == affected:
            break
        affected = new
    return sorted(affected)


def precondition(conn, ids, action, work_item_id):
    """Include graph, lifecycle, order, tags and exact live runs in the preview fence."""
    items, edges = graph(conn)
    runs = [dict(r) for r in conn.execute("SELECT * FROM work_item_runs WHERE state IN ('claimed','running','recovering') ORDER BY run_id") if r['work_item_id'] in ids]
    scope = set(ids)
    if action == 'move':
        scope.update(i for i, r in items.items() if r['parent_id'] == items[work_item_id]['parent_id'])
    body = {'items': {i: items[i] for i in sorted(scope)},
            'edges': sorted((i, p) for i, p in edges if i in scope or p in scope), 'runs': runs,
            'tags': [tuple(r) for r in conn.execute('SELECT work_item_id,tag FROM work_item_tags ORDER BY work_item_id,tag') if r[0] in scope]}
    if conn.execute("SELECT 1 FROM sqlite_master WHERE name='c3_user_order'").fetchone():
        body['user_order'] = [tuple(r) for r in conn.execute('SELECT work_item_id,rank FROM c3_user_order ORDER BY work_item_id') if r[0] in scope]
    # Renewing a lease does not change control ownership.
    for run in runs:
        run.pop('lease_until', None)
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(), runs


def preview(conn, work_item_id, action):
    if action not in USER_ACTIONS | DESTRUCTIVE_ACTIONS:
        raise ValueError('invalid_user_action')
    ids = impact(conn, work_item_id)
    # Pause/stop operate on a batch's child tree too. Destructive actions also
    # cover downstream dependents; preview always exposes that full impact.
    if action not in DESTRUCTIVE_ACTIONS:
        items, _ = graph(conn)
        ids = [work_item_id]
        while True:
            children = [i for i, row in items.items() if row['parent_id'] in ids and i not in ids]
            if not children:
                break
            ids.extend(children)
        ids.sort()
    token, runs = precondition(conn, ids, action, work_item_id)
    return {'work_item_id': work_item_id, 'action': action, 'affected': ids,
            'downstream': [i for i in ids if i != work_item_id],
            'precondition': token, 'runs': runs,
            'requires_confirmation': action in DESTRUCTIVE_ACTIONS}


def order_key(conn):
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    user = dict(conn.execute('SELECT work_item_id,rank FROM c3_user_order')) if 'c3_user_order' in names else {}
    priorities = {}
    for wid, tag in conn.execute("SELECT work_item_id,tag FROM work_item_tags WHERE tag IN ('priority:p0','priority:p1','priority:p2')"):
        priorities[wid] = min(priorities.get(wid, 3), int(tag[-1]))
    return lambda item: (user.get(item['work_item_id'], 2147483647),
                         priorities.get(item['work_item_id'], 3),
                         item['sort_order'] if item['sort_order'] is not None else 2147483647,
                         item['work_item_id'])


def legal_move(conn, work_item_id, position):
    items, edges = graph(conn)
    parent = items[work_item_id]['parent_id']
    deleted = {r[0] for r in conn.execute('SELECT work_item_id FROM c3_user_state WHERE deleted=1')} if conn.execute("SELECT 1 FROM sqlite_master WHERE name='c3_user_state'").fetchone() else set()
    key = order_key(conn)
    ordered = sorted([i for i, r in items.items() if r['parent_id'] == parent and i not in deleted],
                     key=lambda i: key(items[i]))
    # Map dependencies on descendants to the displayed sibling's ancestor.
    def sibling(i):
        seen = set()
        while i in items and i not in seen:
            seen.add(i)
            if i in ordered:
                return i
            i = items[i]['parent_id']
        return None
    mapped = {(sibling(i), sibling(p), p) for i, p in edges}
    deps = {(i, p) for i, p, _ in mapped if i and p and i != p}
    rest = [i for i in ordered if i != work_item_id]
    if isinstance(position, bool) or not isinstance(position, int) or not 0 <= position <= len(rest):
        raise ValueError('invalid_move_position')
    # Stable topological sort first repairs any legacy semantic order.
    topo = []
    pending = rest[:]
    while pending:
        ready = next((i for i in pending if not any(a == i and b in pending for a, b in deps)), None)
        if ready is None:
            raise ValueError('dependency_cycle')
        topo.append(ready)
        pending.remove(ready)
    low = max([topo.index(p) + 1 for i, p in deps if i == work_item_id] or [0])
    high = min([topo.index(i) for i, p in deps if p == work_item_id] or [len(topo)])
    if low > high:
        raise ValueError('dependency_cycle')
    applied = min(max(position, low), high)
    topo.insert(applied, work_item_id)
    blockers = sorted({exact for i, p, exact in mapped if
                       (position < low and i == work_item_id and p) or
                       (position > high and p == work_item_id and i)})
    return {'ordered_ids': topo, 'requested_position': position,
            'applied_position': applied, 'blocking_prerequisites': blockers}


def apply(conn, mutation, actor):
    if not conn.in_transaction:
        raise ValueError('canonical_writer_transaction_required')
    install_schema(conn)
    args = dict(mutation.get('arguments') or {})
    request_id = args.get('request_id')
    if not isinstance(request_id, str) or not request_id or len(request_id) > 128:
        raise ValueError('user_request_id_required')
    if actor != 'c3-user-control' or args.get('intent') != 'explicit-user':
        raise ValueError('explicit_user_authority_required')
    old = conn.execute('SELECT result_json FROM c3_user_events WHERE request_id=?', (request_id,)).fetchone()
    if old:
        raise ValueError('duplicate_user_event_without_receipt')
    wid, action = args['work_item_id'], args['action']
    destructive = mutation['op'] == 'c3_destructive_override'
    if action not in (DESTRUCTIVE_ACTIONS if destructive else USER_ACTIONS):
        raise ValueError('wrong_override_class')
    plan = preview(conn, wid, action)
    if args.get('precondition') != plan['precondition']:
        raise ValueError('control_precondition_changed')
    if destructive and args.get('confirmed_affected') != plan['affected']:
        raise ValueError('explicit_dependency_confirmation_required')
    expected_effect = {'pause': 'paused', 'resume': 'resumed', 'stop': 'stopped',
                       'cancel': 'stopped', 'delete': 'stopped'}.get(action)
    if expected_effect:
        items, _ = graph(conn)
        controlled = {r['work_item_id'] for r in plan['runs']}
        if any(items[i]['status'] == 'running' and i not in controlled for i in plan['affected']):
            raise ValueError('uncontrolled_manual_executor')
        expected = sorted((r['run_id'], r['worker_ref'], expected_effect) for r in plan['runs'])
        actual = sorted((r.get('run_id'), r.get('worker_ref'), r.get('effect')) for r in args.get('executor_effects', []))
        if expected != actual:
            raise ValueError('executor_control_not_acknowledged')
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    result = {k: v for k, v in plan.items() if k != 'runs'}
    if action == 'move':
        result.update(legal_move(conn, wid, args.get('position')))
        if conn.execute('SELECT status FROM work_items WHERE work_item_id=?', (wid,)).fetchone()[0] == 'running':
            raise ValueError('running_item_order_immutable:' + wid)
        for rank, i in enumerate(result['ordered_ids']):
            # Store one complete legal projection; do not rewrite sort_order,
            # prompt metadata or the active run's execution spec.
            conn.execute('INSERT OR REPLACE INTO c3_user_order VALUES(?,?)', (i, rank))
    elif action == 'force-priority':
        if conn.execute('SELECT status FROM work_items WHERE work_item_id=?', (wid,)).fetchone()[0] == 'running':
            raise ValueError('running_item_priority_immutable')
        priority = args.get('priority')
        if priority not in ('p0', 'p1', 'p2'):
            raise ValueError('invalid_priority')
        conn.execute("DELETE FROM work_item_tags WHERE work_item_id=? AND tag LIKE 'priority:%'", (wid,))
        conn.execute('INSERT INTO work_item_tags VALUES(?,?)', (wid, 'priority:' + priority))
    else:
        for i in plan['affected']:
            row = conn.execute('SELECT status FROM work_items WHERE work_item_id=?', (i,)).fetchone()
            conn.execute('INSERT OR IGNORE INTO c3_user_state(work_item_id) VALUES(?)', (i,))
            if action == 'pause':
                if row['status'] in TERMINAL:
                    continue
                conn.execute('UPDATE c3_user_state SET paused=1 WHERE work_item_id=?', (i,))
                conn.execute("INSERT OR IGNORE INTO work_item_tags VALUES(?,'manual-prerequisite:c3-paused')", (i,))
            elif action == 'resume':
                conn.execute('UPDATE c3_user_state SET paused=0 WHERE work_item_id=?', (i,))
                conn.execute("DELETE FROM work_item_tags WHERE work_item_id=? AND tag='manual-prerequisite:c3-paused'", (i,))
                if row['status'] == 'blocked' and conn.execute('SELECT previous_status FROM c3_user_state WHERE work_item_id=?', (i,)).fetchone()[0]:
                    conn.execute("UPDATE work_items SET status='pending',blocker=NULL WHERE work_item_id=?", (i,))
                    conn.execute('UPDATE c3_user_state SET previous_status=NULL WHERE work_item_id=?', (i,))
            elif row['status'] not in TERMINAL:
                status = 'blocked' if action == 'stop' else 'cancelled'
                conn.execute('UPDATE c3_user_state SET previous_status=? WHERE work_item_id=?', (row['status'], i))
                if action == 'delete':
                    conn.execute('UPDATE c3_user_state SET deleted=1 WHERE work_item_id=?', (i,))
                prompt = conn.execute('SELECT prompt_id FROM work_items WHERE work_item_id=?', (i,)).fetchone()[0]
                if prompt:
                    import roadmap_db
                    roadmap_db.request_terminal(conn, prompt, status, actor='c3-user-control', note='user-override:' + request_id)
                conn.execute('UPDATE work_items SET status=?,blocker=?,updated_at=? WHERE work_item_id=?',
                             (status, 'Stopped by user' if action == 'stop' else None, now, i))
                # User stops are explicit interruption, never successful execution.
                conn.execute("UPDATE work_item_runs SET state='failed' WHERE work_item_id=? AND state IN ('claimed','running','recovering')", (i,))
                conn.execute("DELETE FROM work_item_resource_leases WHERE run_id IN (SELECT run_id FROM work_item_runs WHERE work_item_id=? AND state='failed')", (i,))
            elif action == 'delete':
                conn.execute('UPDATE c3_user_state SET deleted=1 WHERE work_item_id=?', (i,))
    result['request_id'] = request_id
    result['executor_effects'] = args.get('executor_effects', [])
    conn.execute('INSERT INTO c3_user_events VALUES(?,?,?,?,?)', (request_id, wid, action, json.dumps(result, sort_keys=True), now))
    return result
