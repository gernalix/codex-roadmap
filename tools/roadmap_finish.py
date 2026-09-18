#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from roadmap_result import RoadmapResultError, finish_result

def finish(repo: Path,prompt_id: str,*,dry_run: bool=False,confirm_executed: bool=False):
    payload=finish_result(repo,prompt_id,"PASS",dry_run=dry_run,confirm_executed=confirm_executed)
    return {**payload,"finish_mode":"sqlite"}

def build_parser():
    p=argparse.ArgumentParser(description="Compatibility wrapper: record PASS in roadmap.sqlite.")
    p.add_argument("--repo",default=".")
    p.add_argument("--prompt-id",required=True)
    p.add_argument("--dry-run",action="store_true")
    p.add_argument("--confirm-executed",action="store_true")
    return p

def main(argv=None):
    a=build_parser().parse_args(argv)
    try:
        payload=finish(Path(a.repo).expanduser(),a.prompt_id,dry_run=a.dry_run,confirm_executed=a.confirm_executed)
    except RoadmapResultError as e:
        print(json.dumps({"status":"blocked","error":str(e)},sort_keys=True)); return 2
    print(json.dumps(payload,sort_keys=True)); return 0

if __name__=="__main__":
    raise SystemExit(main())
