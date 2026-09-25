#!/usr/bin/env python3
"""Execute one native C2 run with a durable receipt and a per-run process lock."""
from __future__ import annotations

import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import time

from c2_codex_executor import persist


class NativeExecutionError(RuntimeError):
    pass


def execute(*, run_id: str, metadata: dict, receipt: Path, timeout=3600):
    command=json.loads(metadata.get('command_json') or 'null')
    if metadata.get('activity')!='native' or not isinstance(command,list) or not command or not all(isinstance(v,str) and v for v in command):
        raise NativeExecutionError('deterministic_native_argv_required')
    cwd=metadata.get('worktree')
    if cwd is not None and not Path(cwd).is_dir():
        raise NativeExecutionError('execution_directory_missing')
    digest=hashlib.sha256(json.dumps(metadata,sort_keys=True).encode()).hexdigest()
    receipt.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with receipt.with_suffix('.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise NativeExecutionError('run_worker_already_active') from None
        if receipt.exists():
            existing=json.loads(receipt.read_text())
            if existing['run_id']!=run_id or existing['metadata_sha256']!=digest:
                raise NativeExecutionError('run_identity_conflict')
            # An interrupted process may have changed the world. Never infer
            # retry safety from an expired lease or missing exit status.
            return existing
        state={'run_id':run_id,'metadata_sha256':digest,'state':'executing','started_at':time.time()}
        persist(receipt,state)
        try:
            result=subprocess.run(command,cwd=cwd,stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=timeout,check=False)
        except (OSError,subprocess.TimeoutExpired) as exc:
            state.update(state='uncertain',error=type(exc).__name__)
        else:
            state.update(state='completed' if result.returncode==0 else 'failed',returncode=result.returncode)
        state['ended_at']=time.time()
        persist(receipt,state)
        return state
