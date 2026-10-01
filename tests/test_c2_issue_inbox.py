from contextlib import closing
from pathlib import Path
import sys
import io
import json
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import c2_intake
import c2_issue_inbox
import c2_scheduler
import c2_issue_capture
import c2_issue_manage
import c2_runtime
import c2_supervisor_authority
import roadmap_db
from test_c2_intake import C2IntakeTests


class IssueInboxTests(unittest.TestCase):
    def make_conn(self, root: Path):
        path = C2IntakeTests().make_cutover_db(root)
        conn = c2_intake._connect(path)
        c2_scheduler.install_schema(conn)
        return path, conn

    def test_batch_many_to_one_split_discard_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                issues = [c2_issue_inbox.capture(conn, description=f'Observation {n}')['issue_id']
                          for n in range(4)]
                existing = c2_intake.add_work_item(conn, title='Existing')['work_item_id']
                before_items = conn.execute('SELECT COUNT(*) FROM work_items').fetchone()[0]
                args = dict(batch_id='semantic-1', triaged_by='test',
                    new_items=[{'alias':'second', 'title':'Second decision'}],
                    decisions=[
                        {'issue_id':issues[0], 'reason':'same work', 'work_item_ids':[existing]},
                        {'issue_id':issues[1], 'reason':'same work', 'work_item_ids':[existing]},
                        {'issue_id':issues[2], 'reason':'two scopes', 'work_item_ids':[existing,'@second']},
                        {'issue_id':issues[3], 'reason':'no work', 'work_item_ids':[]}])
                result = c2_issue_inbox.reconcile_batch(conn, **args)
                self.assertEqual(result, c2_issue_inbox.reconcile_batch(conn, **args))
                self.assertEqual(before_items + 1, conn.execute('SELECT COUNT(*) FROM work_items').fetchone()[0])
                self.assertEqual(4, conn.execute('SELECT COUNT(*) FROM issue_work_item_links WHERE role="decision"').fetchone()[0])
                self.assertEqual(['promoted'] * 3 + ['discarded'],
                    [conn.execute('SELECT state FROM issue_inbox WHERE issue_id=?',(i,)).fetchone()[0] for i in issues])
                with self.assertRaisesRegex(c2_issue_inbox.IssueInboxError, 'batch_id_conflict'):
                    c2_issue_inbox.reconcile_batch(conn, **{**args, 'triaged_by':'other'})
            finally:
                conn.close()

    def test_legacy_scalar_links_are_migrated_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                item = c2_intake.add_work_item(conn, title='Old decision')['work_item_id']
                issue = c2_issue_inbox.capture(conn, description='Old observation')['issue_id']
                conn.execute('UPDATE issue_inbox SET state="promoted",promoted_work_item_id=? WHERE issue_id=?',(item,issue))
                conn.execute('DROP TABLE issue_work_item_links')
                c2_issue_inbox.install_schema(conn)
                c2_issue_inbox.install_schema(conn)
                self.assertEqual([(issue,item,'decision')], [tuple(row) for row in conn.execute(
                    'SELECT issue_id,work_item_id,role FROM issue_work_item_links')])
                self.assertEqual([], conn.execute('PRAGMA foreign_key_check').fetchall())
            finally:
                conn.close()

    def test_batch_requires_fenced_writer_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                issue = c2_issue_inbox.capture(conn, description='Writer batch')['issue_id']
                arguments = {'batch_id':'writer-batch', 'triaged_by':'test',
                    'decisions':[{'issue_id':issue, 'reason':'no work', 'work_item_ids':[]}]}
                with self.assertRaisesRegex(Exception, 'supervisor_authority_required'):
                    roadmap_db.apply_mutation(conn, {'op':'c2_reconcile_issue_batch',
                                                      'arguments':arguments})
                authority = {'supervisor_id':'test-supervisor', 'fencing_token':1,
                             'lease_expires_at':time.time()+120}
                roadmap_db.apply_mutation(conn, {'op':'c2_claim_supervisor',
                    'arguments':{'supervisor_authority':authority}})
                roadmap_db.apply_mutation(conn, {'op':'c2_reconcile_issue_batch',
                    'arguments':{**arguments, 'supervisor_authority':authority}})
                self.assertEqual(1, conn.execute('SELECT COUNT(*) FROM issue_reconciliation_batches').fetchone()[0])
                self.assertEqual('discarded', conn.execute(
                    'SELECT state FROM issue_inbox WHERE issue_id=?',(issue,)).fetchone()[0])
            finally:
                conn.close()

    def test_pending_edit_and_void_are_audited_and_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                issue_id = c2_issue_inbox.capture(conn, description="Old", repo="old/repo")["issue_id"]
                edit_id = "a" * 32
                args = dict(issue_id=issue_id, mutation_id=edit_id, actor="operator",
                            reason="Correct typo", changes={"description": "New\ntext", "repo": None})
                first = c2_issue_inbox.edit(conn, **args)
                self.assertEqual("New\ntext", first["description"])
                self.assertIsNone(first["repo"])
                self.assertEqual(first, c2_issue_inbox.edit(conn, **args))
                self.assertEqual(1, conn.execute("SELECT COUNT(*) FROM issue_inbox_revisions").fetchone()[0])
                history = conn.execute("SELECT before_json,after_json FROM issue_inbox_revisions").fetchone()
                self.assertEqual("Old", json.loads(history[0])["description"])
                self.assertEqual("New\ntext", json.loads(history[1])["description"])
                with self.assertRaisesRegex(c2_issue_inbox.IssueInboxError, "mutation_id_conflict"):
                    c2_issue_inbox.edit(conn, **{**args, "reason": "Different"})
                with self.assertRaisesRegex(c2_issue_inbox.IssueInboxError, "invalid_edit_fields"):
                    c2_issue_inbox.edit(conn, **{**args, "mutation_id": "b" * 32,
                                                 "changes": {"origin_run_id": None}})
                void_args = dict(issue_id=issue_id, mutation_id="c" * 32,
                                 actor="operator", reason="Accidental capture")
                voided = c2_issue_inbox.void(conn, **void_args)
                self.assertEqual("voided", voided["state"])
                self.assertEqual(voided, c2_issue_inbox.void(conn, **void_args))
                self.assertEqual([], c2_issue_inbox.pending_issues(conn))
                self.assertEqual(2, conn.execute("SELECT COUNT(*) FROM issue_inbox_revisions").fetchone()[0])
                with self.assertRaisesRegex(c2_issue_inbox.IssueInboxError, "issue_already_triaged"):
                    c2_issue_inbox.edit(conn, **{**args, "mutation_id": "d" * 32})
                with self.assertRaisesRegex(c2_issue_inbox.IssueInboxError, "issue_already_triaged"):
                    c2_issue_inbox.discard(conn, issue_id=issue_id, reason="x", triaged_by="test")
            finally:
                conn.close()

    def test_triaged_rows_cannot_be_edited_or_voided(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                issue_id = c2_issue_inbox.capture(conn, description="Real")["issue_id"]
                c2_issue_inbox.discard(conn, issue_id=issue_id, reason="Handled", triaged_by="test")
                with self.assertRaisesRegex(c2_issue_inbox.IssueInboxError, "issue_already_triaged"):
                    c2_issue_inbox.void(conn, issue_id=issue_id, mutation_id="e" * 32,
                                        actor="operator", reason="Late correction")
                self.assertEqual(0, conn.execute("SELECT COUNT(*) FROM issue_inbox_revisions").fetchone()[0])
            finally:
                conn.close()

    def test_legacy_state_constraint_migrates_without_losing_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                issue_id = c2_issue_inbox.capture(conn, description="Legacy")["issue_id"]
                conn.execute("DROP VIEW v_issue_inbox_pending_ordered")
                conn.execute("DROP TABLE issue_inbox_revisions")
                conn.execute("CREATE TABLE legacy AS SELECT * FROM issue_inbox")
                conn.execute("DROP TABLE issue_inbox")
                old = c2_issue_inbox.SCHEMA.split("CREATE INDEX")[0].split("CREATE TABLE IF NOT EXISTS issue_inbox_revisions")[0]
                old = old.replace("'discarded','voided'", "'discarded'")
                conn.execute(old.replace("CREATE TABLE IF NOT EXISTS", "CREATE TABLE"))
                conn.execute("INSERT INTO issue_inbox SELECT * FROM legacy")
                conn.execute("DROP TABLE legacy")
                c2_issue_inbox.install_schema(conn)
                self.assertEqual("Legacy", conn.execute("SELECT description FROM issue_inbox WHERE issue_id=?", (issue_id,)).fetchone()[0])
                self.assertEqual("voided", c2_issue_inbox.void(conn, issue_id=issue_id,
                    mutation_id="f" * 32, actor="operator", reason="Invalid")["state"])
                self.assertEqual([], conn.execute("PRAGMA foreign_key_check").fetchall())
            finally:
                conn.close()

    def test_capture_is_append_only_and_requires_no_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                first = c2_issue_inbox.capture(
                    conn, description="Same observation", observed_at_ms=1000
                )
                second = c2_issue_inbox.capture(
                    conn, description="Same observation", observed_at_ms=1001
                )
                self.assertNotEqual(first["issue_id"], second["issue_id"])
                self.assertEqual(2, conn.execute(
                    "SELECT COUNT(*) FROM issue_inbox"
                ).fetchone()[0])
            finally:
                conn.close()

    def test_capture_preserves_exact_multiline_description_without_execution_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                body = "  First line\nsecond line\n"
                row = c2_issue_inbox.capture(conn, description=body)
                self.assertEqual(body, row["description"])
                self.assertIsNone(row["origin_run_id"])
                self.assertIsNone(row["origin_work_item_id"])
            finally:
                conn.close()

    def test_pending_readback_uses_observed_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                first = c2_issue_inbox.capture(
                    conn, description="First", observed_at_ms=1000
                )["issue_id"]
                second = c2_issue_inbox.capture(
                    conn, description="Second", observed_at_ms=2000
                )["issue_id"]
                third = c2_issue_inbox.capture(
                    conn, description="Third", observed_at_ms=3000
                )["issue_id"]
                rows = c2_issue_inbox.pending_issues(conn)
                self.assertEqual([first, second, third], [row["issue_id"] for row in rows])
            finally:
                conn.close()

    def test_task_id_resolves_bound_chat_without_executor_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                item = c2_intake.add_work_item(
                    conn,
                    title="Semantic source",
                    objective="Do source task",
                    acceptance=["done"],
                    execution={
                        "activity": "semantic",
                        "project_url": "https://chatgpt.com/g/g-p-test/project",
                    },
                )
                run = c2_scheduler.schedule(conn, event_key="bind", now=10)[0]
                c2_scheduler.acknowledge(
                    conn,
                    run["run_id"],
                    worker_ref="c2-run:" + run["run_id"],
                    metadata=run["metadata"],
                    now=11,
                )
                c2_scheduler.bind_executor(
                    conn,
                    run["run_id"],
                    executor_ref="https://chatgpt.com/c/test-chat",
                    chat_url="https://chatgpt.com/c/test-chat",
                    now=12,
                )
                issue = c2_issue_inbox.capture(
                    conn,
                    description="Observed while working",
                    task_id=item["work_item_id"],
                    observed_at_ms=13000,
                )
                self.assertEqual(item["work_item_id"], issue["origin_work_item_id"])
                self.assertEqual(run["run_id"], issue["origin_run_id"])
                self.assertEqual("https://chatgpt.com/c/test-chat", issue["chat_url"])
                self.assertEqual("https://chatgpt.com/c/test-chat", issue["executor_ref"])
            finally:
                conn.close()

    def test_completed_match_cannot_be_discarded_and_reopens_as_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                fixed = c2_intake.add_work_item(
                    conn, title="Previously fixed", repo="repo", sort_order=7
                )
                conn.execute(
                    "UPDATE work_items SET status='completed' WHERE work_item_id=?",
                    (fixed["work_item_id"],),
                )
                issue = c2_issue_inbox.capture(
                    conn,
                    description="The fixed bug happened again",
                    task_id=fixed["work_item_id"],
                    observed_at_ms=2000,
                )
                with self.assertRaisesRegex(
                    c2_issue_inbox.IssueInboxError,
                    "requires_regression",
                ):
                    c2_issue_inbox.discard(
                        conn,
                        issue_id=issue["issue_id"],
                        matched_work_item_id=fixed["work_item_id"],
                        reason="already fixed",
                        triaged_by="test",
                    )

                result = c2_issue_inbox.promote(
                    conn,
                    issue_id=issue["issue_id"],
                    matched_work_item_id=fixed["work_item_id"],
                    reason="fresh reproduction",
                    triaged_by="test",
                )
                self.assertTrue(result["regression"])
                self.assertNotEqual(
                    fixed["work_item_id"], result["promoted_work_item_id"]
                )
                reopened = conn.execute(
                    "SELECT status,repo,sort_order FROM work_items WHERE work_item_id=?",
                    (result["promoted_work_item_id"],),
                ).fetchone()
                self.assertEqual(("pending", "repo", 7), tuple(reopened))
                relation = conn.execute(
                    """SELECT relation_type FROM work_item_relations
                       WHERE from_work_item_id=? AND to_work_item_id=?""",
                    (result["promoted_work_item_id"], fixed["work_item_id"]),
                ).fetchone()
                self.assertEqual("regression_of", relation[0])
                self.assertEqual(
                    "promoted",
                    conn.execute(
                        "SELECT state FROM issue_inbox WHERE issue_id=?",
                        (issue["issue_id"],),
                    ).fetchone()[0],
                )
            finally:
                conn.close()

    def test_active_duplicate_is_promoted_into_existing_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                active = c2_intake.add_work_item(conn, title="Existing active")
                issue = c2_issue_inbox.capture(
                    conn, description="Same active problem", observed_at_ms=3000
                )
                before = conn.execute("SELECT COUNT(*) FROM work_items").fetchone()[0]
                result = c2_issue_inbox.promote(
                    conn,
                    issue_id=issue["issue_id"],
                    matched_work_item_id=active["work_item_id"],
                    reason="duplicate observation of relevant active work",
                    triaged_by="test",
                )
                after = conn.execute("SELECT COUNT(*) FROM work_items").fetchone()[0]
                self.assertEqual(before, after)
                self.assertEqual(active["work_item_id"], result["promoted_work_item_id"])
                self.assertEqual(1, conn.execute(
                    """SELECT COUNT(*) FROM work_item_evidence
                       WHERE work_item_id=? AND evidence_kind='issue_inbox'""",
                    (active["work_item_id"],),
                ).fetchone()[0])
            finally:
                conn.close()

    def test_capture_is_unfenced_but_triage_requires_supervisor(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                roadmap_db.apply_mutation(
                    conn,
                    {
                        "op": "c2_capture_issue",
                        "arguments": {
                            "description": "Cheap capture",
                            "observed_at_ms": 4000,
                        },
                    },
                )
                issue_id = conn.execute(
                    "SELECT issue_id FROM issue_inbox"
                ).fetchone()[0]
                with self.assertRaisesRegex(Exception, "supervisor_authority_required"):
                    roadmap_db.apply_mutation(
                        conn,
                        {
                            "op": "c2_discard_issue",
                            "arguments": {
                                "issue_id": issue_id,
                                "reason": "irrelevant",
                                "triaged_by": "test",
                            },
                        },
                    )

                authority = {
                    "supervisor_id": "test-supervisor",
                    "fencing_token": 1,
                    "lease_expires_at": time.time() + 120,
                }
                roadmap_db.apply_mutation(
                    conn,
                    {
                        "op": "c2_claim_supervisor",
                        "arguments": {"supervisor_authority": authority},
                    },
                )
                roadmap_db.apply_mutation(
                    conn,
                    {
                        "op": "c2_discard_issue",
                        "arguments": {
                            "issue_id": issue_id,
                            "reason": "irrelevant",
                            "triaged_by": "test-supervisor",
                            "supervisor_authority": authority,
                        },
                    },
                )
                self.assertEqual(
                    "discarded",
                    conn.execute(
                        "SELECT state FROM issue_inbox WHERE issue_id=?",
                        (issue_id,),
                    ).fetchone()[0],
                )
            finally:
                conn.close()

    def test_edit_requires_fenced_writer_and_cli_submits_one_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute("BEGIN IMMEDIATE")
                issue_id = c2_issue_inbox.capture(conn, description="Before")["issue_id"]
                args = {"issue_id": issue_id, "mutation_id": "1" * 32,
                        "actor": "operator", "reason": "Correction",
                        "changes": {"description": "After"}}
                with self.assertRaisesRegex(Exception, "supervisor_authority_required"):
                    roadmap_db.apply_mutation(conn, {"op": "c2_edit_issue", "arguments": args})
                authority = {"supervisor_id": "test-supervisor", "fencing_token": 1,
                             "lease_expires_at": time.time() + 120}
                roadmap_db.apply_mutation(conn, {"op": "c2_claim_supervisor",
                    "arguments": {"supervisor_authority": authority}})
                roadmap_db.apply_mutation(conn, {"op": "c2_edit_issue",
                    "arguments": {**args, "supervisor_authority": authority}})
                self.assertEqual("After", conn.execute("SELECT description FROM issue_inbox").fetchone()[0])
            finally:
                conn.close()
        with tempfile.TemporaryDirectory() as tmp:
            changes_file = Path(tmp) / "changes.json"
            changes_file.write_text('{"description":"Corrected"}', encoding="utf-8")
            with patch.object(c2_issue_manage, "load_runtime_identity", return_value=("supervisor", 4)), \
                 patch.object(c2_issue_manage.c2_control, "submit_control", return_value={"status": "queued"}) as submit:
                self.assertEqual(0, c2_issue_manage.main([
                    "edit", "issue:" + "2" * 32, "--actor", "operator",
                    "--reason", "Correction", "--mutation-id", "3" * 32,
                    "--changes-json", str(changes_file)]))
                self.assertEqual("edit_issue", submit.call_args.kwargs["operation"])
                self.assertEqual({"description": "Corrected"},
                                 submit.call_args.kwargs["arguments"]["changes"])

    def test_capture_cli_uses_only_description_and_run_environment(self):
        submitted = []
        with patch.dict('os.environ', {'C2_TASK_ID': 'wi:known', 'C2_RUN_ID': 'run-known'}, clear=True), \
             patch('sys.argv', ['c2_issue_capture.py', 'Incidental failure']), \
             patch.object(c2_issue_capture, 'submit_document',
                          side_effect=lambda doc, **kw: submitted.append((doc, kw)) or {'status': 'queued'}):
            self.assertEqual(0, c2_issue_capture.main())
        args = submitted[0][0]['operations'][0]['arguments']
        self.assertEqual('Incidental failure', args['description'])
        self.assertEqual('wi:known', args['task_id'])
        self.assertEqual('run-known', args['run_id'])
        self.assertNotIn('repo', args)
        self.assertNotIn('code_location', args)

    def test_capture_cli_native_sources_and_idempotent_identity(self):
        body = "  Long text\nwith punctuation: $ ` \\ \n"
        submitted = []
        def record(doc, **kwargs):
            submitted.append((doc, kwargs))
            return {'status': 'queued'}
        with tempfile.TemporaryDirectory() as tmp, \
             patch.dict('os.environ', {}, clear=True), \
             patch.object(c2_issue_capture, 'submit_document', side_effect=record), \
             patch('sys.stdout', new_callable=io.StringIO):
            source = Path(tmp) / 'issue.txt'
            source.write_text(body)
            with patch('sys.argv', ['capture', '--file', str(source)]):
                self.assertEqual(0, c2_issue_capture.main())
            with patch('sys.argv', ['capture', '--stdin']), \
                 patch('sys.stdin', io.StringIO(body)):
                self.assertEqual(0, c2_issue_capture.main())
            identity = 'issue:' + 'a' * 32
            payload = json.dumps({'issue_id': identity, 'description': body, 'repo': 'example/repo'})
            for _ in range(2):
                with patch('sys.argv', ['capture', '--json', payload]):
                    self.assertEqual(0, c2_issue_capture.main())
        self.assertEqual([body] * 4,
                         [item[0]['operations'][0]['arguments']['description'] for item in submitted])
        self.assertNotEqual(submitted[0][1]['request_key'], submitted[1][1]['request_key'])
        self.assertEqual(submitted[2][1]['request_key'], submitted[3][1]['request_key'])
        self.assertTrue(submitted[2][1]['lookup_existing'])
        self.assertEqual('example/repo', submitted[2][0]['operations'][0]['arguments']['repo'])

    def test_manual_start_receipt_resolves_executor_without_run_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                item = c2_intake.add_work_item(conn, title='Manual source')
                c2_scheduler.executor_started(conn, work_item_id=item['work_item_id'],
                    executor='codex', executor_ref='thread-manual',
                    chat_url='codex://threads/thread-manual', now=2)
                issue = c2_issue_inbox.capture(conn, description='Manual incidental',
                    task_id=item['work_item_id'])
                self.assertEqual('codex', issue['executor'])
                self.assertEqual('thread-manual', issue['executor_ref'])
                self.assertEqual('codex://threads/thread-manual', issue['chat_url'])
                self.assertIsNone(issue['origin_run_id'])
            finally:
                conn.close()

    def test_codex_binding_is_idempotent_and_conflicts_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                item = c2_intake.add_work_item(conn, title='Codex source')
                conn.execute('''INSERT INTO work_item_runs
                  (run_id,work_item_id,event_key,attempt,executor,state,lease_until,
                   worker_ref,checkpoint_commit,metadata_json,created_at)
                  VALUES(?,?,?,1,'codex','running',1000,NULL,NULL,'{}',1)''',
                  ('run-codex', item['work_item_id'], 'test'))
                issue = c2_issue_inbox.capture(conn, description='Found in thread', run_id='run-codex')
                self.assertIsNone(issue['chat_url'])
                first = c2_scheduler.bind_executor(conn, 'run-codex',
                    executor_ref='thread-123', chat_url='codex://threads/thread-123', now=2)
                self.assertEqual(first, c2_scheduler.bind_executor(conn, 'run-codex',
                    executor_ref='thread-123', chat_url='codex://threads/thread-123', now=3))
                self.assertEqual('codex://threads/thread-123', conn.execute(
                    'SELECT chat_url FROM issue_inbox WHERE issue_id=?', (issue['issue_id'],)).fetchone()[0])
                with self.assertRaisesRegex(c2_scheduler.SchedulingError, 'executor_binding_conflict'):
                    c2_scheduler.bind_executor(conn, 'run-codex', executor_ref='other',
                                               chat_url='codex://threads/other')
            finally:
                conn.close()

    def test_recursive_triage_cannot_create_work_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                issue = c2_issue_inbox.capture(conn, description='Needs decision')
                before = conn.total_changes
                with self.assertRaisesRegex(c2_issue_inbox.IssueInboxError, 'retired_recursive'):
                    c2_issue_inbox.ensure_triage(conn, project_url='anything')
                self.assertEqual(before, conn.total_changes)
                self.assertEqual('pending', conn.execute(
                    'SELECT state FROM issue_inbox WHERE issue_id=?', (issue['issue_id'],)).fetchone()[0])
            finally:
                conn.close()

    def test_runtime_does_not_create_triage_item_or_gate_scheduling(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, conn = self.make_conn(Path(tmp))
            try:
                conn.execute('BEGIN IMMEDIATE')
                c2_issue_inbox.capture(conn, description='Needs triage')
                calls = []
                normal = c2_intake.add_work_item(conn, title='Independent', repo='independent')
                c2_scheduler.configure(conn, normal['work_item_id'], activity='native', command=['true'])
                with patch.object(c2_runtime, 'automatic_candidates', return_value=['candidate']):
                    c2_runtime.advance(conn, submit=lambda *args: calls.append(args), launch=lambda _: None,
                        triage_project_url='https://chatgpt.com/g/g-p-test/project')
                self.assertNotIn('ensure_issue_triage', [call[0] for call in calls])
                self.assertIn('schedule', [call[0] for call in calls])
                self.assertIn('reconcile_blocked_safety_net', [call[0] for call in calls])
                self.assertEqual(0, conn.execute("SELECT COUNT(*) FROM work_item_tags WHERE tag='c2:issue-triage'").fetchone()[0])
            finally:
                conn.close()




if __name__ == "__main__":
    unittest.main()
