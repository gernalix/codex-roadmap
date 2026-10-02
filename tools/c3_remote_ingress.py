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
    critical = key.startswith(('start-', 'terminal-', 'c2-executor-', 'c2-bind-'))
    try:
        document = json.loads(issue.get('body') or '{}')
        operations = document.get('operations', [])
        critical = critical or any(op.get('op') in (
            'c2_executor_started', 'c2_executor_result', 'c2_bind_executor',
            'c2_heartbeat_run', 'c2_schedule_run', 'c2_runtime_claim')
            or (op.get('op') == 'status' and op.get('status') in ('running','completed','blocked','failed','cancelled'))
            for op in operations)
    except (ValueError, AttributeError, TypeError):
        pass  # Invalid documents are rejected by the writer, not executed here.
    return (0 if critical else 1, issue['number'])


def drain(limit=100):
    if not 1 <= limit <= 100:
        raise ValueError('remote_batch_limit_invalid')
    endpoint = 'repos/' + DEFAULT_REMOTE_REPO + '/issues'
    rows = gh(endpoint + '?state=open&per_page=100')
    # Bound network discovery independently of applied mutation batch size.
    for page in (2, 3):
        if len(rows) < (page - 1) * 100:
            break
        rows.extend(gh(endpoint + '?state=open&per_page=100&page=' + str(page)))
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
