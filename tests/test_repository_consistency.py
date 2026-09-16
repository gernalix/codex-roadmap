from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROADMAP_RE = re.compile(r"^\s*(\d+)\.\s+\[\[prompts/([^|\]]+)(?:\|[^\]]+)?\]\]\s*$")
EXPLANATION_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*\[\[prompts/([^\]]+)\]\]\s*\|.*\|\s*"
    r"(low|medium|high|extra_high)\s*\|\s*(Prompt|Goal)\s*\|\s*$",
    re.IGNORECASE,
)
PROMPT_ID_RE = re.compile(r"\bPROMPT_ID=(\d{6})\b")
REASONING_RE = re.compile(r"\breasoning=([a-z_]+)\b", re.IGNORECASE)


class RepositoryConsistencyTests(unittest.TestCase):
    def _roadmap(self):
        rows = []
        for line in (ROOT / "roadmap.md").read_text(encoding="utf-8").splitlines():
            if match := ROADMAP_RE.match(line):
                rows.append((int(match.group(1)), match.group(2)))
        return rows

    def _explanations(self):
        rows = []
        for line in (ROOT / "spiegazioni.md").read_text(encoding="utf-8").splitlines():
            if match := EXPLANATION_RE.match(line):
                rows.append(
                    (int(match.group(1)), match.group(2), match.group(3).lower(), match.group(4))
                )
        return rows

    def test_pending_inventory_is_one_to_one_and_ordered(self):
        roadmap = self._roadmap()
        explanations = self._explanations()
        self.assertEqual([n for n, _ in roadmap], list(range(1, len(roadmap) + 1)))
        self.assertEqual([n for n, *_ in explanations], list(range(1, len(explanations) + 1)))
        self.assertEqual([name for _, name in roadmap], [name for _, name, *_ in explanations])
        prompt_files = {path.stem for path in (ROOT / "prompts").glob("*.md")}
        self.assertEqual(set(name for _, name in roadmap), prompt_files)

    def test_pending_prompt_metadata_is_canonical(self):
        explanations = {name: reasoning for _, name, reasoning, _ in self._explanations()}
        prompt_ids = []
        for _, name in self._roadmap():
            text = (ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8")
            prompt_id = PROMPT_ID_RE.search(text)
            reasoning = REASONING_RE.search(text)
            self.assertIsNotNone(prompt_id, name)
            self.assertIsNotNone(reasoning, name)
            self.assertEqual(reasoning.group(1).lower(), explanations[name], name)
            self.assertNotRegex(text, r"(?i)<\s*genera[^>]*>|\bPROMPT_ID\s*=\s*(?:TODO|TBD)\b")
            prompt_ids.append(prompt_id.group(1))
        self.assertEqual(len(prompt_ids), len(set(prompt_ids)))


if __name__ == "__main__":
    unittest.main()
