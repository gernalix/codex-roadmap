#!/usr/bin/env python3
"""Retired Markdown lifecycle helper. C3 DB/API and start/finish own execution."""
import json


class RoadmapError(RuntimeError):
    pass


def first_prompt(*args, **kwargs):
    raise RoadmapError("markdown_control_retired_use_c3_database")


def complete(*args, **kwargs):
    raise RoadmapError("markdown_control_retired_use_roadmap_finish")


def reconcile(*args, **kwargs):
    raise RoadmapError("markdown_control_retired_use_c3_writer")


def main(argv=None):
    print(json.dumps({"status": "blocked", "error": "markdown_control_retired"}))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
