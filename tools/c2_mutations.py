"""C2 operations inside the existing serialized roadmap mutation writer."""
from __future__ import annotations

import c2_intake
import c2_scheduler
import c2_cutover_writer
import c2_supervisor_authority
import c2_terminal_state_reimport


SUPERVISOR_OPERATIONS = frozenset({
    'intake', 'prepare_codex', 'configure', 'auto_configure', 'schedule', 'acknowledge',
    'recover', 'reconcile_run', 'milestone', 'claim_milestone',
    'mark_milestone', 'verify_work_item',
    'reimport_terminal_state',
})


def apply(conn, mutation):
    if conn.execute("SELECT type FROM sqlite_master WHERE name='prompts'").fetchone()[0] != 'view':
        raise ValueError('c2_writer_cutover_required')
    if not conn.in_transaction:
        conn.execute('BEGIN IMMEDIATE')
    c2_scheduler.install_schema(conn)
    c2_supervisor_authority.install_schema(conn)
    action = mutation['op'].removeprefix('c2_')
    arguments = dict(mutation.get('arguments') or {})
    authority = arguments.pop('supervisor_authority', None)
    if action == 'claim_supervisor':
        return c2_supervisor_authority.claim(conn, authority)
    if action == 'renew_supervisor':
        return c2_supervisor_authority.renew(conn, authority)
    if action == 'retire_supervisor':
        return c2_supervisor_authority.retire(conn, authority)
    if action in SUPERVISOR_OPERATIONS:
        c2_supervisor_authority.require(conn, authority)
    operations = {
        'cutover': c2_cutover_writer.confirm,
        'intake': c2_intake.add_work_item,
        'prepare_codex': c2_intake.prepare_codex,
        'configure': c2_scheduler.configure,
        'auto_configure': c2_scheduler.configure_auto,
        'schedule': c2_scheduler.schedule,
        'acknowledge': c2_scheduler.acknowledge,
        'checkpoint': c2_scheduler.checkpoint,
        'record_checkpoint': c2_scheduler.record_checkpoint,
        'recover': c2_scheduler.recover,
        'quarantine_browser': c2_scheduler.quarantine_browser_run,
        'finish_work_item': c2_scheduler.finish_browser_work_item,
        'complete_verified': c2_scheduler.complete_verified,
        'verify_work_item': c2_scheduler.verify_work_item,
        'complete': c2_scheduler.complete,
        'reconcile_run': c2_scheduler.reconcile_terminal_run,
        'milestone': c2_scheduler.enqueue_milestone,
        'claim_milestone': c2_scheduler.claim_milestone,
        'mark_milestone': c2_scheduler.mark_milestone,
        'reimport_terminal_state': c2_terminal_state_reimport.apply,
    }
    if action not in operations:
        raise ValueError('unknown_c2_operation:'+action)
    return operations[action](conn, **arguments)
