#!/usr/bin/env python3
"""Prepare one verified C2 intake for Codex without dispatching it."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import time
from typing import Any, Callable

from c3_storage import CANONICAL_DB
from c2_codex_sandbox import git_metadata_writable_roots, SandboxPathError
from c2_supervisor_lease import DEFAULT_DB as SUPERVISOR_DB, connect as connect_supervisor, _require as require_supervisor, snapshot as supervisor_snapshot, record_activity
from roadmap_start import _wait_issue_applied, RoadmapStartError
from submit_mutation import submit_document, MutationSubmitError

DEFAULT_REPOSITORY = "gernalix/codex-roadmap"
DEFAULT_REPO = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = CANONICAL_DB
REPO_SINGLE_WRITER = Path.home()/"projects/github-autosync/repo_single_writer.py"


class PrepareCodexError(RuntimeError):
    pass


def _required_text(value: object, name: str) -> str:
    text=str(value or "").strip()
    if not text:
        raise PrepareCodexError(name+"_required")
    return text
def load_spec(path: Path) -> dict[str, Any]:
    path=Path(path).expanduser().resolve()
    try:
        raw=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        raise PrepareCodexError("invalid_spec_file") from exc
    if not isinstance(raw,dict):
        raise PrepareCodexError("spec_must_be_object")
    allowed={"work_item_id","prompt_file","source","model","reasoning","activity",
             "megavault_mode","parent_prompt_id","resources","max_attempts",
             "readiness_evidence"}
    unknown=set(raw)-allowed
    if unknown:
        raise PrepareCodexError("unknown_spec_fields:"+",".join(sorted(unknown)))
    spec=dict(raw)
    for key in ("work_item_id","prompt_file","source","model","reasoning","activity"):
        spec[key]=_required_text(spec.get(key),key)
    if spec["activity"] not in ("coding","diagnostic"):
        raise PrepareCodexError("activity_must_be_coding_or_diagnostic")
    prompt_file=Path(spec["prompt_file"]).expanduser()
    if not prompt_file.is_absolute():
        prompt_file=(path.parent/prompt_file).resolve()
    if not prompt_file.is_file():
        raise PrepareCodexError("prompt_file_missing")
    spec["prompt_file"]=prompt_file
    mode=spec.get("megavault_mode")
    if mode is not None and str(mode) not in ("FAST","STANDARD","STRICT"):
        raise PrepareCodexError("invalid_megavault_mode")
    parent=spec.get("parent_prompt_id")
    if parent is not None and (type(parent) is not int or not re.fullmatch(r"\d{6}",str(parent))):
        raise PrepareCodexError("invalid_parent_prompt_id")
    resources=spec.get("resources",[])
    if not isinstance(resources,list) or any(not isinstance(v,str) or not v.strip() for v in resources):
        raise PrepareCodexError("resources_must_be_nonempty_strings")
    spec["resources"]=sorted(set(v.strip() for v in resources))
    attempts=spec.get("max_attempts",3)
    if type(attempts) is not int or attempts < 1:
        raise PrepareCodexError("invalid_max_attempts")
    spec["max_attempts"]=attempts
    evidence=spec.get("readiness_evidence",[])
    if not isinstance(evidence,list) or any(not isinstance(v,str) or not v.strip() for v in evidence):
        raise PrepareCodexError("readiness_evidence_must_be_strings")
    spec["readiness_evidence"]=[v.strip() for v in evidence]
    return spec


def _open_snapshot(path: Path=DEFAULT_SNAPSHOT) -> sqlite3.Connection:
    path=Path(path).expanduser().resolve()
    if not path.is_file():
        raise PrepareCodexError("roadmap_snapshot_missing")
    conn=sqlite3.connect(f"{path.as_uri()}?mode=ro",uri=True)
    conn.row_factory=sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _state(conn: sqlite3.Connection, work_item_id: str) -> dict[str, Any]:
    item=conn.execute("SELECT * FROM work_items WHERE work_item_id=?",(work_item_id,)).fetchone()
    if not item:
        raise PrepareCodexError("work_item_not_found:"+work_item_id)
    result={"item":dict(item)}
    result["tags"]=[str(r[0]) for r in conn.execute(
        "SELECT tag FROM work_item_tags WHERE work_item_id=? ORDER BY tag",(work_item_id,))]
    result["active_runs"]=int(conn.execute("""SELECT COUNT(*) FROM work_item_runs
        WHERE work_item_id=? AND state IN ('claimed','running','recovering')""",
        (work_item_id,)).fetchone()[0])
    result["execution_spec"]=None
    spec=conn.execute("SELECT * FROM work_item_execution_specs WHERE work_item_id=?",(work_item_id,)).fetchone()
    if spec:
        result["execution_spec"]=dict(spec)
    result["prompt"]=None
    result["prompt_body"]=None
    prompt_id=item["prompt_id"]
    if prompt_id:
        prompt=conn.execute("""SELECT prompt_id,model,reasoning,prompt_type,current_path
            FROM prompts WHERE prompt_id=?""",(prompt_id,)).fetchone()
        if prompt:
            result["prompt"]=dict(prompt)
        body=conn.execute("""SELECT body FROM prompt_materializations
            WHERE prompt_id=? ORDER BY created_at DESC LIMIT 1""",(prompt_id,)).fetchone()
        if body:
            result["prompt_body"]=str(body[0])
    return result
def _refresh_state(work_item_id: str) -> dict[str, Any]:
    with closing(_open_snapshot()) as conn:
        return _state(conn,work_item_id)


def _current_authority(activity: str | None=None) -> dict[str, Any]:
    with closing(connect_supervisor(SUPERVISOR_DB)) as db:
        row=supervisor_snapshot(db)
        if not row:
            raise PrepareCodexError("supervisor_lease_missing")
        try:
            row=require_supervisor(db,row["supervisor_id"],int(row["fencing_token"]),time.time())
            if activity:
                row=record_activity(db,supervisor_id=row["supervisor_id"],
                                    token=int(row["fencing_token"]),operation=activity)
        except Exception as exc:
            raise PrepareCodexError("supervisor_lease_not_active") from exc
        return {
            "supervisor_id":str(row["supervisor_id"]),
            "fencing_token":int(row["fencing_token"]),
            "lease_expires_at":float(row["lease_expires_at"]),
        }


def _request_key(phase: str, work_item_id: str, arguments: dict[str, Any],
                 authority: dict[str, Any]) -> str:
    stable={"phase":phase,"work_item_id":work_item_id,"arguments":arguments,
            "fencing_token":authority["fencing_token"],
            "lease_expires_at":authority["lease_expires_at"]}
    digest=hashlib.sha256(json.dumps(stable,sort_keys=True,ensure_ascii=False,
        default=str,separators=(",",":")).encode()).hexdigest()[:28]
    return "c2-prepare-codex-"+phase+"-"+digest


def _submit_phase(operation: str, arguments: dict[str, Any], phase: str,
                  work_item_id: str, authority: dict[str, Any], timeout: float) -> dict[str,str]:
    current=_current_authority("prepare:"+phase)
    if (current["supervisor_id"]!=authority["supervisor_id"] or
            current["fencing_token"]!=authority["fencing_token"]):
        raise PrepareCodexError("supervisor_authority_changed")
    authority=dict(current)
    payload=dict(arguments)
    payload["supervisor_authority"]=dict(authority)
    key=_request_key(phase,work_item_id,arguments,authority)
    result=submit_document({
        "schema":"codex-roadmap.mutation.v1",
        "actor":"c2-prepare-codex",
        "operations":[
            {"op":"c2_renew_supervisor","arguments":{
                "supervisor_authority":dict(authority),
            }},
            {"op":"c2_"+operation,"arguments":payload},
        ],
    },request_key=key)
    _wait_issue_applied(DEFAULT_REPOSITORY,result["issue_number"],timeout)
    return result
def _expected_prompt_body(prompt_id: str, text: str) -> str:
    match=re.search(r"(?m)^PROMPT_ID\s*[:=]\s*(\d{6})\s*$",text)
    if match:
        if match.group(1)!=prompt_id:
            raise PrepareCodexError("prompt_text_prompt_id_mismatch")
        return text
    return f"PROMPT_ID={prompt_id}\n\n{text.lstrip()}"


def _validate_prompt_state(state: dict[str, Any], spec: dict[str, Any],
                           prompt_text: str) -> str:
    item=state["item"]
    prompt_id=str(item.get("prompt_id") or "")
    prompt=state.get("prompt")
    if not prompt_id or not prompt:
        raise PrepareCodexError("prompt_materialization_missing")
    if str(item.get("executor_policy"))!="codex":
        raise PrepareCodexError("prepared_item_not_codex")
    if str(prompt.get("model") or "")!=spec["model"]:
        raise PrepareCodexError("prepared_model_conflict")
    if str(prompt.get("reasoning") or "")!=spec["reasoning"]:
        raise PrepareCodexError("prepared_reasoning_conflict")
    if state.get("prompt_body")!=_expected_prompt_body(prompt_id,prompt_text):
        raise PrepareCodexError("prepared_prompt_body_conflict")
    return prompt_id


def _repo_slug(value: str) -> str:
    text=str(value or "").strip()
    path=Path(text).expanduser()
    if text.startswith("/") and path.exists():
        proc=subprocess.run(["git","-C",str(path),"remote","get-url","origin"],
            text=True,capture_output=True,check=False)
        if proc.returncode:
            raise PrepareCodexError("repo_origin_unavailable")
        text=proc.stdout.strip()
    if text.startswith("git@github.com:"):
        text=text.removeprefix("git@github.com:")
    elif "github.com/" in text:
        text=text.split("github.com/",1)[1]
    text=text.removesuffix(".git").strip("/")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",text):
        raise PrepareCodexError("canonical_repo_slug_required")
    return text


def _run_checked(command: list[str], error: str) -> str:
    proc=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if proc.returncode:
        raise PrepareCodexError(error+":"+(proc.stderr.strip() or proc.stdout.strip() or str(proc.returncode)))
    return proc.stdout.strip()


def _external_worktree(item: dict[str, Any], prompt_id: str) -> str:
    if not REPO_SINGLE_WRITER.is_file():
        raise PrepareCodexError("repo_single_writer_missing")
    slug=_repo_slug(str(item.get("repo") or ""))
    command=["python3",str(REPO_SINGLE_WRITER),"start-roadmap",
             "--repo-slug",slug,"--task-id",prompt_id,"--actor","c2-prepare"]
    project_id=str(item.get("project_id") or "").strip()
    if project_id:
        command.extend(["--project-id",project_id])
    output=_run_checked(command,"repo_single_writer_start_failed")
    worktree=output.splitlines()[-1].strip() if output else ""
    if not worktree:
        raise PrepareCodexError("repo_single_writer_worktree_missing")
    return worktree
def _allocate_worktree(item: dict[str, Any], prompt_id: str) -> str:
    return _external_worktree(item,prompt_id)


def _validate_execution_state(state: dict[str, Any], spec: dict[str, Any],
                              worktree: str) -> None:
    item=state["item"]
    current=state.get("execution_spec")
    if not current:
        raise PrepareCodexError("execution_spec_missing")
    expected={
        "activity":spec["activity"],
        "model":spec["model"],
        "reasoning":spec["reasoning"],
        "worktree":str(Path(worktree).expanduser().resolve()),
        "project_url":None,
        "command_json":None,
        "resources_json":json.dumps(sorted(set(spec["resources"]))),
        "max_attempts":spec["max_attempts"],
    }
    for key,value in expected.items():
        actual=current.get(key)
        if key=="worktree" and actual is not None:
            actual=str(Path(str(actual)).expanduser().resolve())
        if actual!=value:
            raise PrepareCodexError("execution_spec_conflict:"+key)
    prompt=state.get("prompt") or {}
    expected_goal=1 if prompt.get("prompt_type")=="Goal" else 0
    if int(current.get("goal_mode") or 0)!=expected_goal:
        raise PrepareCodexError("execution_spec_conflict:goal_mode")
    if item.get("status")!="pending":
        raise PrepareCodexError("preparation_dispatched_unexpectedly")
    if state.get("active_runs"):
        raise PrepareCodexError("preparation_created_active_run")


def prepare(spec: dict[str, Any], *, timeout: float=120.0,
            refresh: Callable[[str],dict[str,Any]]|None=None,
            submit_phase: Callable[[str,dict[str,Any],str],Any]|None=None,
            allocate_worktree: Callable[[dict[str,Any],str],str]|None=None,
            sandbox_roots: Callable[[str],list[str]]|None=None,
            authority: dict[str,Any]|None=None) -> dict[str,Any]:
    refresh=refresh or _refresh_state
    authority=authority or _current_authority()
    wid=spec["work_item_id"]
    if submit_phase is None:
        submit_phase=lambda operation,arguments,phase: _submit_phase(
            operation,arguments,phase,wid,authority,timeout)
    allocate_worktree=allocate_worktree or _allocate_worktree
    sandbox_roots=sandbox_roots or git_metadata_writable_roots
    state=refresh(wid)
    if state["active_runs"]:
        raise PrepareCodexError("active_run_conflict")
    status=str(state["item"].get("status") or "")
    if status in ("waiting","blocked"):
        evidence=spec.get("readiness_evidence") or []
        if not evidence:
            blocker=str(state["item"].get("blocker") or "readiness_evidence_required")
            raise PrepareCodexError("work_item_waiting:"+blocker)
        submit_phase("reconcile_item",{
            "work_item_id":wid,"classification":"CURRENT_READY","status":"pending",
            "evidence":list(evidence),"fields":{
                "actionable":1,"blocker":None,
                "current_action":"Codex preparation requested from explicit structured input.",
                "next_action":"Materialize prompt, allocate isolated worktree and configure exact execution spec; do not dispatch.",
            },"include_descendants":False,
        },"ready")
        state=refresh(wid)
        status=str(state["item"].get("status") or "")
    if status!="pending" or not int(state["item"].get("actionable") or 0):
        raise PrepareCodexError("work_item_not_ready_for_preparation:"+status)
    prompt_text=Path(spec["prompt_file"]).read_text(encoding="utf-8")
    if not state["item"].get("prompt_id"):
        arguments={
            "work_item_id":wid,"prompt_text":prompt_text,"source":spec["source"],
            "model":spec["model"],"reasoning":spec["reasoning"],
        }
        if spec.get("megavault_mode") is not None:
            arguments["megavault_mode"]=spec["megavault_mode"]
        if spec.get("parent_prompt_id") is not None:
            arguments["parent_prompt_id"]=spec["parent_prompt_id"]
        submit_phase("prepare_codex",arguments,"prompt")
        state=refresh(wid)
    prompt_id=_validate_prompt_state(state,spec,prompt_text)
    worktree=allocate_worktree(state["item"],prompt_id)
    try:
        sandbox_writable_roots=sandbox_roots(worktree)
    except SandboxPathError as exc:
        raise PrepareCodexError(str(exc)) from exc
    execution={
        "activity":spec["activity"],"worktree":worktree,
        "model":spec["model"],"reasoning":spec["reasoning"],
        "resources":list(spec["resources"]),"max_attempts":spec["max_attempts"],
    }
    if state.get("execution_spec"):
        _validate_execution_state(state,spec,worktree)
    else:
        submit_phase("auto_configure",{"work_item_id":wid,"execution":execution},"execution")
        state=refresh(wid)
        _validate_execution_state(state,spec,worktree)
    return {
        "status":"prepared","work_item_id":wid,"prompt_id":prompt_id,
        "worktree":worktree,"activity":spec["activity"],
        "sandbox_writable_roots":sandbox_writable_roots,
        "model":spec["model"],"reasoning":spec["reasoning"],
        "dispatched":False,
    }
def build_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec",type=Path,required=True,
        help="JSON with explicit work_item_id, prompt_file, source, model, reasoning and activity")
    parser.add_argument("--timeout",type=float,default=120.0)
    return parser


def main(argv: list[str]|None=None) -> int:
    args=build_parser().parse_args(argv)
    try:
        spec=load_spec(args.spec)
        result=prepare(spec,timeout=args.timeout)
    except (PrepareCodexError,MutationSubmitError,RoadmapStartError,OSError,
            sqlite3.Error,ValueError) as exc:
        print(json.dumps({"status":"blocked","error":str(exc)},sort_keys=True))
        return 2
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
