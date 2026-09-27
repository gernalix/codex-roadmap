import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import c2_human_copy
import c2_issue_inbox
import c2_intake
from test_c2_intake import C2IntakeTests


class HumanCopyTests(unittest.TestCase):
    def make_conn(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = C2IntakeTests().make_cutover_db(Path(tmp.name))
        conn = c2_intake._connect(path)
        c2_issue_inbox.install_schema(conn)
        conn.commit()
        return conn

    def test_copy_is_presentation_only_and_validated(self):
        conn = self.make_conn()
        conn.execute("BEGIN IMMEDIATE")
        item = c2_intake.add_work_item(
            conn, title="Fix request-key conflict after supervisor lease renewal",
            objective="Preserve fencing and make recovery idempotent.",
        )
        result = c2_human_copy.set_copy(
            conn,
            entity_kind="work_item",
            entity_id=item["work_item_id"],
            human_title="Evita che il rinnovo del supervisore blocchi la C2",
            ai_title="Fix supervisor resume request-key conflict after lease renewal",
            human_summary="Il rinnovo può riusare un identificatore già usato. La C2 deve recuperare senza fermare i sync.",
        )
        row = conn.execute(
            "SELECT title,status FROM work_items WHERE work_item_id=?",
            (item["work_item_id"],),
        ).fetchone()
        self.assertEqual(
            ("Fix request-key conflict after supervisor lease renewal", "pending"),
            tuple(row),
        )
        self.assertEqual("complete", result["copy_status"])
        with self.assertRaisesRegex(c2_human_copy.HumanCopyError, "must_not_be_truncated"):
            c2_human_copy.set_copy(
                conn,
                entity_kind="work_item",
                entity_id=item["work_item_id"],
                human_title="Titolo troncato…",
                ai_title="Technical",
                human_summary="Summary",
            )

    def test_promote_inherits_human_copy_to_issue_and_work_item(self):
        conn = self.make_conn()
        conn.execute("BEGIN IMMEDIATE")
        issue = c2_issue_inbox.capture(
            conn,
            description="c2_supervisor_resume reuses a request key with changed lease expiry",
            observed_at_ms=1000,
        )
        result = c2_issue_inbox.promote(
            conn,
            issue_id=issue["issue_id"],
            reason="actionable",
            triaged_by="test",
            title="Fix supervisor request-key conflict",
            human_title="Evita che il rinnovo del supervisore blocchi la C2",
            ai_title="Fix c2_supervisor_resume request-key idempotency after lease renewal",
            human_summary="Il rinnovo può riusare una chiave con dati diversi. Il recupero deve restare idempotente.",
        )
        rows = conn.execute(
            "SELECT entity_kind,human_title,copy_status FROM c2_human_copy ORDER BY entity_kind"
        ).fetchall()
        self.assertEqual(["issue", "work_item"], [row["entity_kind"] for row in rows])
        self.assertTrue(all(row["copy_status"] == "complete" for row in rows))
        self.assertEqual(
            result["promoted_work_item_id"],
            conn.execute(
                "SELECT entity_id FROM c2_human_copy WHERE entity_kind='work_item'"
            ).fetchone()[0],
        )

    def test_ambiguous_copy_uses_explicit_status(self):
        conn = self.make_conn()
        conn.execute("BEGIN IMMEDIATE")
        issue = c2_issue_inbox.capture(
            conn, description="Something is wrong with sync", observed_at_ms=1000
        )
        c2_human_copy.set_copy(
            conn,
            entity_kind="issue",
            entity_id=issue["issue_id"],
            human_title="Chiarire: problema di sincronizzazione",
            ai_title="Unspecified sync problem",
            human_summary="La segnalazione non indica quale sync fallisce né in quale condizione. Servono questi dettagli prima di definire il fix.",
            copy_status="needs_clarification",
        )
        self.assertEqual(
            "needs_clarification",
            conn.execute(
                "SELECT copy_status FROM c2_human_copy WHERE entity_kind='issue'"
            ).fetchone()[0],
        )


if __name__ == "__main__":
    unittest.main()
