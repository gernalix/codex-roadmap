"""Bounded technical Inbox reconciliation; never owns a work item or run."""
import hashlib
import json

import c2_issue_inbox


def plan(conn, *, batch_limit=25):
    if type(batch_limit) is not int or not 1 <= batch_limit <= 25:
        raise ValueError('inbox_batch_limit_invalid')
    rows = conn.execute("SELECT * FROM issue_inbox WHERE state='pending' ORDER BY observed_at_ms,issue_id LIMIT ?",
                        (batch_limit,)).fetchall()
    decisions = []
    for issue in rows:
        # Only an exact prior decision, in the same observation context and
        # still-active work, is safe without a fresh semantic judgment.
        targets = conn.execute("""SELECT DISTINCT old.promoted_work_item_id
            FROM issue_inbox old JOIN work_items w ON w.work_item_id=old.promoted_work_item_id
            WHERE old.state='promoted' AND old.description=?
              AND old.repo IS ? AND old.code_location IS ?
              AND old.origin_work_item_id IS ? AND old.observed_at_ms<=?
              AND w.status IN ('pending','running','waiting','blocked','needs_fix','unknown')""",
            (issue['description'], issue['repo'], issue['code_location'],
             issue['origin_work_item_id'], issue['observed_at_ms'])).fetchall()
        if len(targets) == 1:
            decisions.append({'issue_id': issue['issue_id'], 'work_item_ids': [targets[0][0]],
                              'reason': 'Exact prior observation decision; target remains active'})
    digest = hashlib.sha256(json.dumps(decisions, sort_keys=True).encode()).hexdigest()
    return {'decisions': decisions, 'digest': digest, 'scanned': len(rows)}


def apply(conn, *, expected_digest, batch_limit=25):
    c2_issue_inbox._transaction(conn)
    current = plan(conn, batch_limit=batch_limit)
    if current['digest'] != expected_digest:
        raise ValueError('inbox_batch_precondition_changed')
    if not current['decisions']:
        return {'changed': 0, 'pending': current['scanned']}
    result = c2_issue_inbox.reconcile_batch(conn, batch_id='technical-' + expected_digest,
        decisions=current['decisions'], triaged_by='c3-inbox-maintenance')
    return {'changed': len(result['decisions']), 'pending': current['scanned'] - len(result['decisions'])}


def run(conn, submit):
    current = plan(conn)
    # No-op scans create neither mutation receipt nor audit/technical task.
    if not current['decisions']:
        return {'changed': 0, 'pending': current['scanned']}
    submit('maintain_issue_inbox', {'expected_digest': current['digest'], 'batch_limit': 25},
           'c3-inbox-maintenance-' + current['digest'])
    return {'changed': len(current['decisions']), 'pending': current['scanned'] - len(current['decisions'])}
