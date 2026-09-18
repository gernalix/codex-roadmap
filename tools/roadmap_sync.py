#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

MAX_RETRIES=3

class SyncError(RuntimeError): pass

def run(repo: Path,*args:str,check:bool=True):
    p=subprocess.run(["git","-C",str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and p.returncode:
        raise SyncError(f"git_{args[0]}_failed:{p.stderr.strip()}")
    return p

def sync(repo: Path, source: Path) -> dict[str,object]:
    repo=Path(repo).resolve(); source=Path(source).resolve()
    for attempt in range(MAX_RETRIES+1):
        run(repo,"fetch","--quiet","origin","main")
        parent=Path(tempfile.mkdtemp(prefix="codex-roadmap-sync-"))
        wt=parent/"worktree"
        try:
            run(repo,"worktree","add","--detach",str(wt),"origin/main")
            cmd=["python3",str(wt/"tools"/"import_codex_usage.py"),"--repo",str(wt),"--source",str(source)]
            p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if p.returncode:
                raise SyncError(f"import_failed:{p.stderr.strip()}")
            status=run(wt,"status","--porcelain","--untracked-files=all").stdout.splitlines()
            if not status:
                return {"status":"noop","attempt":attempt,"import":json.loads(p.stdout or "{}")}
            allowed_prefixes=("roadmap.sqlite","roadmap.md","spiegazioni.md","prompt-registry.md","obsidian/","prompts/","completed/","falliti/")
            changed=[line[3:] for line in status if len(line)>=4]
            bad=[x for x in changed if not any(x==a or x.startswith(a) for a in allowed_prefixes)]
            if bad:
                raise SyncError("unexpected_changes:"+",".join(sorted(bad)))
            run(wt,"add","-A","roadmap.sqlite","roadmap.md","spiegazioni.md","prompt-registry.md","obsidian","prompts","completed","falliti")
            run(wt,"commit","-m","Sync roadmap execution metadata")
            sha=run(wt,"rev-parse","HEAD").stdout.strip()
            push=run(wt,"push","origin","HEAD:main",check=False)
            if push.returncode==0:
                return {"status":"updated","attempt":attempt,"commit":sha,"import":json.loads(p.stdout or "{}")}
            msg=(push.stderr or "").lower()
            if attempt<MAX_RETRIES and ("fetch first" in msg or "non-fast-forward" in msg):
                continue
            raise SyncError(f"push_failed:{push.stderr.strip()}")
        finally:
            if wt.exists():
                run(repo,"worktree","remove","--force",str(wt),check=False)
            shutil.rmtree(parent,ignore_errors=True)
    raise SyncError("retry_exhausted")

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default=".")
    p.add_argument("--source",required=True)
    a=p.parse_args(argv)
    try:
        result=sync(Path(a.repo).expanduser(),Path(a.source).expanduser())
    except SyncError as e:
        print(json.dumps({"status":"blocked","error":str(e)},sort_keys=True)); return 2
    print(json.dumps(result,sort_keys=True)); return 0

if __name__=="__main__":
    raise SystemExit(main())
