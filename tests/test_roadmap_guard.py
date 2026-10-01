from pathlib import Path
import tempfile
import unittest
import roadmap_guard as guard


class RoadmapGuardTests(unittest.TestCase):
    def test_retired_reader_and_writers_fail_without_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for operation in (guard.first_prompt, guard.complete, guard.reconcile):
                with self.assertRaisesRegex(guard.RoadmapError, "markdown_control_retired"):
                    operation(root, "123456")
            self.assertEqual(list(root.iterdir()), [])
            self.assertEqual(2, guard.main(["complete", "--prompt-id", "123456"]))
