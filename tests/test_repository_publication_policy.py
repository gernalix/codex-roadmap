from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from repository_publication_policy import (  # noqa: E402
    audit_is_fresh,
    classify_action_ref,
    classify_path,
)


class RepositoryPublicationPolicyTests(unittest.TestCase):
    def test_source_and_document_keywords_are_not_path_blockers(self):
        paths = [
            "completed/codex-per-prompt-token-attribution-local-validation.md",
            "scripts/secret_scan.sh",
            "systemd/codex-session-archive.service",
            "contracts/database/src/main/java/com/wordpulse/app/data/SessionSummaryRow.kt",
            "feature/supercontacts/src/main/assets/countries-v1.csv",
            ".codex/CODE_MAP.tsv",
        ]
        self.assertTrue(all(classify_path(path).severity == "ignore" for path in paths))

    def test_intrinsically_sensitive_artifacts_block(self):
        for path in ("salute.db", ".env", "keys/id_rsa.key"):
            with self.subTest(path=path):
                self.assertEqual(classify_path(path).severity, "block")

    def test_env_placeholder_does_not_block(self):
        self.assertEqual(classify_path(".env.example").severity, "ignore")

    def test_data_artifacts_with_sensitive_names_require_review(self):
        for path in ("cookies.json", "session-export.zip"):
            with self.subTest(path=path):
                self.assertEqual(classify_path(path).severity, "review")

    def test_official_github_actions_are_advisory_not_third_party(self):
        self.assertEqual(classify_action_ref("actions/checkout@v4").severity, "advisory")
        self.assertEqual(classify_action_ref("actions/setup-python@v5").severity, "advisory")

    def test_third_party_mutable_action_requires_review(self):
        self.assertEqual(classify_action_ref("somecorp/action@v1").severity, "review")

    def test_sha_pinned_and_local_actions_do_not_require_review(self):
        pinned = "somecorp/action@" + "a" * 40
        self.assertEqual(classify_action_ref(pinned).severity, "ignore")
        self.assertEqual(classify_action_ref("./.github/actions/local").severity, "ignore")

    def test_audit_freshness_requires_exact_recorded_head(self):
        sha = "a" * 40
        self.assertTrue(audit_is_fresh(sha, sha.upper()))
        self.assertFalse(audit_is_fresh(sha, "b" * 40))
        self.assertFalse(audit_is_fresh(None, sha))
        self.assertFalse(audit_is_fresh(sha, None))


if __name__ == "__main__":
    unittest.main()
