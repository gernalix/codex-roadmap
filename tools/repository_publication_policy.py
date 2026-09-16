#!/usr/bin/env python3
"""Deterministic policy helpers for repository publication audits.

This module deliberately separates secret scanning from path/workflow heuristics.
A filename keyword alone must not turn ordinary source code or documentation into
an automatic publication blocker.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Classification:
    severity: str
    reason: str

    @property
    def blocking(self) -> bool:
        return self.severity == "block"


IGNORE = Classification("ignore", "no_path_based_risk")

_ENV_RE = re.compile(r"^\.env(?:\..+)?$", re.IGNORECASE)
_ENV_PLACEHOLDER_RE = re.compile(
    r"^\.env(?:\.(?:example|sample|template|dist|defaults?))$", re.IGNORECASE
)
_RISKY_NAME_RE = re.compile(
    r"(?:^|[-_.])(?:auth|cookie|cookies|credential|credentials|secret|secrets|"
    r"session|sessions|token|tokens|webhook|webhooks|contact|contacts|message|"
    r"messages|export|backup)(?:[-_.]|$)",
    re.IGNORECASE,
)
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)

_BLOCKING_EXTENSIONS = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".dump",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
}

# These are code/docs/operational definitions. Their filenames can legitimately
# contain words such as "session", "token" or "secret" without containing data.
_SOURCE_OR_DOC_EXTENSIONS = {
    ".bat",
    ".c",
    ".cc",
    ".cpp",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".kt",
    ".kts",
    ".md",
    ".py",
    ".rb",
    ".rs",
    ".service",
    ".sh",
    ".timer",
    ".toml",
    ".ts",
    ".tsx",
}

_REVIEWABLE_DATA_EXTENSIONS = {
    ".7z",
    ".csv",
    ".gz",
    ".json",
    ".jsonl",
    ".log",
    ".tar",
    ".tgz",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
    ".zip",
}


def classify_path(path: str) -> Classification:
    """Classify a tracked path without reading or guessing its contents.

    `block` is reserved for path types intrinsically unsafe to publish without
    proof (real env files, databases, private keys/keystores, dumps). `review`
    means inspect content before publication. `ignore` means the path name alone
    is not evidence of sensitive content; secret scanners still apply.
    """

    normalized = path.replace("\\", "/").strip()
    name = PurePosixPath(normalized).name
    lower_name = name.lower()
    suffix = PurePosixPath(lower_name).suffix

    if _ENV_PLACEHOLDER_RE.match(lower_name):
        return Classification("ignore", "env_placeholder")
    if _ENV_RE.match(lower_name):
        return Classification("block", "environment_file")

    if suffix in _BLOCKING_EXTENSIONS:
        return Classification("block", f"sensitive_artifact_extension:{suffix}")

    if not _RISKY_NAME_RE.search(lower_name):
        return IGNORE

    if suffix in _SOURCE_OR_DOC_EXTENSIONS:
        return Classification("ignore", "keyword_in_source_or_document_name")

    if suffix in _REVIEWABLE_DATA_EXTENSIONS or not suffix:
        return Classification("review", "keyword_in_data_or_config_artifact_name")

    return Classification("review", "sensitive_keyword_requires_content_review")


def classify_action_ref(ref: str) -> Classification:
    """Classify a GitHub Actions `uses:` reference.

    GitHub-maintained `actions/*` tags are mutable, but they are not third-party
    actions and therefore are advisory rather than an automatic publication
    blocker. Third-party mutable refs require review; immutable 40-char SHAs are
    accepted by this path-level policy.
    """

    value = ref.strip().strip("'\"")
    if value.startswith("./"):
        return Classification("ignore", "local_action")
    if value.startswith("docker://"):
        return Classification("review", "mutable_or_external_container_action")

    if "@" not in value or "/" not in value.split("@", 1)[0]:
        return Classification("review", "unparseable_action_ref")

    action, revision = value.rsplit("@", 1)
    owner = action.split("/", 1)[0].lower()
    if _SHA40_RE.fullmatch(revision):
        return Classification("ignore", "immutable_sha_pin")
    if owner == "actions":
        return Classification("advisory", "github_official_action_mutable_ref")
    return Classification("review", "third_party_action_mutable_ref")


def audit_is_fresh(scanned_head_sha: str | None, current_head_sha: str | None) -> bool:
    """Return True only when a report proves that it scanned current HEAD."""

    if not scanned_head_sha or not current_head_sha:
        return False
    return scanned_head_sha.lower() == current_head_sha.lower()


def _emit(kind: str, values: list[str]) -> None:
    classifier = classify_path if kind == "path" else classify_action_ref
    payload = []
    for value in values:
        result = classifier(value)
        payload.append(
            {"value": value, **asdict(result), "blocking": result.blocking}
        )
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    path_parser = sub.add_parser("path")
    path_parser.add_argument("values", nargs="+")

    action_parser = sub.add_parser("action")
    action_parser.add_argument("values", nargs="+")

    freshness_parser = sub.add_parser("freshness")
    freshness_parser.add_argument("--scanned", required=True)
    freshness_parser.add_argument("--current", required=True)

    args = parser.parse_args()
    if args.command in {"path", "action"}:
        _emit(args.command, args.values)
        return 0

    print(
        json.dumps(
            {"fresh": audit_is_fresh(args.scanned, args.current)},
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
