#!/usr/bin/env python3
"""Retired entrypoint: Git integration belongs to github-autosync only."""
import json

REPOSITORY = 'gernalix/codex-roadmap'


class IntegrationError(RuntimeError):
    pass


def _retired(*args, **kwargs):
    raise IntegrationError('retired: use github-autosync/repo_single_writer.py')


queue = status = integrate = _retired


def main():
    print(json.dumps({'status': 'blocked', 'error': 'retired: use github-autosync/repo_single_writer.py'}))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
