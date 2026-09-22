from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import apply_issue_mutation
import roadmap_db


class IssueMutationTests(unittest.TestCase):
    def _event(self, root: Path, *, number: int, key: str, document: dict) -> Path:
        event = {
            "issue": {
                "number": number,
                "title": f"[roadmap-mutation] {key}",
                "body": json.dumps(document),
            }
        }
        path = root / "event.json"
        path.write_text(json.dumps(event), encoding="utf-8")
        return path

    def test_register_materializes_prompt_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            prompt_text = "PROMPT_ID=123456\n# Goal\nTest"
            document = {
                "schema": "codex-roadmap.mutation.v1",
                "actor": "chatgpt",
                "operations": [
                    {
                        "op": "register",
                        "prompt_id": "123456",
                        "slug": "test-prompt",
                        "title": "Test prompt",
                        "current_path": "prompts/test-prompt.md",
                        "prompt_text": prompt_text,
                    }
                ],
            }
            out = apply_issue_mutation.apply_issue(
                repo, self._event(repo, number=12, key="register-123456", document=document)
            )
            self.assertFalse(out["idempotent"])
            self.assertEqual(
                prompt_text,
                (repo / "prompts/test-prompt.md").read_text(encoding="utf-8"),
            )
            conn = roadmap_db.connect(repo, writable=False)
            receipt = conn.execute(
                "SELECT request_key,issue_number FROM mutation_receipts"
            ).fetchone()
            self.assertEqual(("register-123456", 12), tuple(receipt))
            conn.close()

    def test_deferred_render_applies_mutation_without_regenerating_views(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            document = {
                "schema": "codex-roadmap.mutation.v1",
                "actor": "chatgpt",
                "operations": [
                    {
                        "op": "register",
                        "prompt_id": "123456",
                        "slug": "deferred-render",
                        "title": "Deferred render",
                        "current_path": "prompts/deferred-render.md",
                        "prompt_text": "PROMPT_ID=123456",
                    }
                ],
            }
            with patch.object(
                apply_issue_mutation, "reconcile_prompt_file_locations"
            ) as reconcile, patch.object(apply_issue_mutation, "render") as render:
                out = apply_issue_mutation.apply_issue(
                    repo,
                    self._event(
                        repo,
                        number=14,
                        key="register-deferred-123456",
                        document=document,
                    ),
                    render_views=False,
                )

            self.assertFalse(out["rendered_views"])
            self.assertTrue((repo / "prompts/deferred-render.md").is_file())
            reconcile.assert_not_called()
            render.assert_not_called()

    def test_same_payload_different_duplicate_issue_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "prompts").mkdir()
            document = {
                "schema": "codex-roadmap.mutation.v1",
                "actor": "chatgpt",
                "operations": [
                    {
                        "op": "register",
                        "prompt_id": "123456",
                        "slug": "test-prompt",
                        "title": "Test prompt",
                        "current_path": "prompts/test-prompt.md",
                        "prompt_text": "PROMPT_ID=123456",
                    }
                ],
            }
            first = self._event(repo, number=12, key="same-key", document=document)
            apply_issue_mutation.apply_issue(repo, first)
            duplicate = self._event(repo, number=13, key="same-key", document=document)
            out = apply_issue_mutation.apply_issue(repo, duplicate)
            self.assertTrue(out["idempotent"])
            conn = roadmap_db.connect(repo, writable=False)
            self.assertEqual(
                1,
                conn.execute(
                    "SELECT COUNT(*) FROM mutation_receipts WHERE request_key='same-key'"
                ).fetchone()[0],
            )
            conn.close()

    def test_same_key_different_payload_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base = {
                "schema": "codex-roadmap.mutation.v1",
                "actor": "chatgpt",
                "operations": [
                    {
                        "op": "register",
                        "prompt_id": "123456",
                        "slug": "test-prompt",
                        "title": "Test prompt",
                        "current_path": "prompts/test-prompt.md",
                        "prompt_text": "PROMPT_ID=123456",
                    }
                ],
            }
            apply_issue_mutation.apply_issue(
                repo, self._event(repo, number=12, key="same-key", document=base)
            )
            changed = json.loads(json.dumps(base))
            changed["operations"][0]["title"] = "Different"
            with self.assertRaises(apply_issue_mutation.IssueMutationError):
                apply_issue_mutation.apply_issue(
                    repo, self._event(repo, number=13, key="same-key", document=changed)
                )


if __name__ == "__main__":
    unittest.main()
