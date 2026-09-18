from pathlib import Path
import re
import sqlite3
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROADMAP_RE = re.compile(r"^\s*(\d+)\.\s+\[\[prompts/([^|\]]+)(?:\|[^\]]+)?\]\]\s*$")
PROMPT_LINK_RE = re.compile(r"^\[\[prompts/([^|\]]+)(?:\|[^\]]+)?\]\]$")
PROMPT_ID_RE = re.compile(r"\bPROMPT_ID=(\d{6})\b")
REASONING_RE = re.compile(r"\breasoning=([a-z_]+)\b", re.IGNORECASE)


class RepositoryConsistencyTests(unittest.TestCase):
    def _db_pending(self):
        conn = sqlite3.connect(ROOT / "roadmap.sqlite")
        conn.row_factory = sqlite3.Row
        try:
            return list(
                conn.execute(
                    """
                    SELECT prompt_id,slug,reasoning,prompt_type
                    FROM prompts
                    WHERE status IN ('pending','running')
                    ORDER BY
                      CASE WHEN status='pending' THEN 0 WHEN status='running' THEN 1 ELSE 2 END,
                      COALESCE(queue_position,2147483647), created_at, prompt_id
                    """
                )
            )
        finally:
            conn.close()

    def _roadmap(self):
        rows = []
        for line in (ROOT / "roadmap.md").read_text(encoding="utf-8").splitlines():
            if match := ROADMAP_RE.match(line):
                rows.append((int(match.group(1)), match.group(2)))
        return rows

    def _explanations(self):
        lines = (ROOT / "spiegazioni.md").read_text(encoding="utf-8").splitlines()
        header = next(line for line in lines if line.startswith("| # |"))
        names = [cell.strip() for cell in header.strip("|").split("|")]
        indexes = {name: idx for idx, name in enumerate(names)}
        required = {"#", "Prompt", "PROMPT_ID", "Reasoning", "Tipo prompt"}
        self.assertTrue(required.issubset(indexes), indexes)

        rows = []
        for line in lines:
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) != len(names) or not cells[indexes["#"]].isdigit():
                continue
            link = PROMPT_LINK_RE.match(cells[indexes["Prompt"]])
            self.assertIsNotNone(link, line)
            rows.append(
                (
                    int(cells[indexes["#"]]),
                    link.group(1),
                    cells[indexes["PROMPT_ID"]],
                    cells[indexes["Reasoning"]].lower(),
                    cells[indexes["Tipo prompt"]],
                )
            )
        return rows

    def test_pending_inventory_is_one_to_one_and_ordered(self):
        db_rows = self._db_pending()
        roadmap = self._roadmap()
        explanations = self._explanations()

        expected_slugs = [row["slug"] for row in db_rows]
        self.assertEqual([n for n, _ in roadmap], list(range(1, len(roadmap) + 1)))
        self.assertEqual([n for n, *_ in explanations], list(range(1, len(explanations) + 1)))
        self.assertEqual(expected_slugs, [name for _, name in roadmap])
        self.assertEqual(expected_slugs, [name for _, name, *_ in explanations])

        prompt_files = {path.stem for path in (ROOT / "prompts").glob("*.md")}
        self.assertEqual(set(expected_slugs), prompt_files)

    def test_explanation_intro_has_no_numbered_task_narrative(self):
        text = (ROOT / "spiegazioni.md").read_text(encoding="utf-8")
        intro = text.split("| # |", 1)[0]
        self.assertNotRegex(intro, re.compile(r"\btask\s+\d+\b", re.IGNORECASE))

    def test_pending_prompt_metadata_is_canonical(self):
        db_rows = {row["slug"]: row for row in self._db_pending()}
        explanations = {
            name: (prompt_id, reasoning, prompt_type)
            for _, name, prompt_id, reasoning, prompt_type in self._explanations()
        }
        prompt_ids = []
        for _, name in self._roadmap():
            text = (ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8")
            prompt_id = PROMPT_ID_RE.search(text)
            reasoning = REASONING_RE.search(text)
            self.assertIsNotNone(prompt_id, name)
            self.assertIsNotNone(reasoning, name)

            db_row = db_rows[name]
            exp_id, exp_reasoning, exp_type = explanations[name]
            self.assertEqual(prompt_id.group(1), db_row["prompt_id"], name)
            self.assertEqual(prompt_id.group(1), exp_id, name)
            self.assertEqual(reasoning.group(1).lower(), (db_row["reasoning"] or "").lower(), name)
            self.assertEqual(reasoning.group(1).lower(), exp_reasoning, name)
            self.assertEqual(db_row["prompt_type"], exp_type, name)
            self.assertNotRegex(text, r"(?i)<\s*genera[^>]*>|\bPROMPT_ID\s*=\s*(?:TODO|TBD)\b")
            prompt_ids.append(prompt_id.group(1))

        self.assertEqual(len(prompt_ids), len(set(prompt_ids)))


if __name__ == "__main__":
    unittest.main()
