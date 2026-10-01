#!/usr/bin/env python3
"""Bounded remote inbox transport; SQLite writes remain in the local service."""
import json
import subprocess

from c3_local_writer import submit_local
from submit_mutation import ISSUE_PREFIX, DEFAULT_REMOTE_REPO


def gh(*arguments):
    result = subprocess.run(['gh', 'api', *arguments], capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise RuntimeError('remote_ingress_unavailable')
    return json.loads(result.stdout)


def priority(issue):
    key = issue['title'][len(ISSUE_PREFIX):]
    prefixes = ('c3-user-', 'start-', 'terminal-', 'c2-executor-', 'c2-bind-')
    return (next((i for i, prefix in enumerate(prefixes) if key.startswith(prefix)), len(prefixes)), issue['number'])


def drain(limit=100):
    endpoint = 'repos/' + DEFAULT_REMOTE_REPO + '/issues'
    rows = gh(endpoint + '?state=open&per_page=100')
    rows = sorted((r for r in rows if not r.get('pull_request') and r.get('title', '').startswith(ISSUE_PREFIX)), key=priority)
    counts = {'applied': 0, 'rejected': 0}
    for issue in rows[:limit]:
        key = issue['title'][len(ISSUE_PREFIX):].strip()
        try:
            document = json.loads(issue.get('body') or '')
            submit_local(document, request_key=key, issue_number=issue['number'])
        except (ValueError, KeyError, TypeError):
            # Invalid requests fail closed. Socket/network failures leave the
            # issue open for delivery when the service becomes available.
            reason = 'not_planned'
            counts['rejected'] += 1
        else:
            reason = 'completed'
            counts['applied'] += 1
        gh('--method', 'PATCH', endpoint + '/' + str(issue['number']), '-f', 'state=closed', '-f', 'state_reason=' + reason)
    return counts


if __name__ == '__main__':
    print(json.dumps(drain(), sort_keys=True))
