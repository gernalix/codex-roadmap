from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from roadmap_render import _project_prompt_body


class PromptProjectionTests(unittest.TestCase):
    def test_missing_prompt_id_is_added_to_projection(self):
        self.assertEqual(
            "PROMPT_ID=123456\n\n# Goal\nRepair C2.\n",
            _project_prompt_body("123456", "# Goal\nRepair C2.\n"),
        )

    def test_existing_prompt_id_is_preserved(self):
        body = "PROMPT_ID=123456\n\n# Goal\nRepair C2.\n"
        self.assertEqual(body, _project_prompt_body("123456", body))


if __name__ == "__main__":
    unittest.main()
