"""C2 operations inside the existing serialized roadmap mutation writer."""
from __future__ import annotations

import c2_intake
import c2_scheduler


def apply(conn, mutation):
    if conn.execute("SELECT type FROM sqlite_master WHERE name='prompts'").fetchone()[0] != 'view':
        raise ValueError('c2_writer_cutover_required')
    if not conn.in_transaction:
        conn.execute('BEGIN IMMEDIATE')
    c2_scheduler.install_schema(conn)
    action = mutation['op'].removeprefix('c2_')
    arguments = dict(mutation.get('arguments') or {})
    operations = {
        'intake': c2_intake.add_work_item,
        'prepare_codex': c2_intake.prepare_codex,
        'configure': c2_scheduler.configure,
        'schedule': c2_scheduler.schedule,
        'acknowledge': c2_scheduler.acknowledge,
        'checkpoint': c2_scheduler.checkpoint,
        'recover': c2_scheduler.recover,
        'complete': c2_scheduler.complete,
        'reconcile_run': c2_scheduler.reconcile_terminal_run,
        'milestone': c2_scheduler.enqueue_milestone,
        'claim_milestone': c2_scheduler.claim_milestone,
        'mark_milestone': c2_scheduler.mark_milestone,
    }
    if action not in operations:
        raise ValueError('unknown_c2_operation:'+action)
    return operations[action](conn, **arguments)
