from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))

import c2_prepare_codex as prep


class PrepareCodexTests(unittest.TestCase):
    def _spec(self, prompt_file: Path, *, evidence=None):
        return {
            "work_item_id":"wi:test",
            "prompt_file":prompt_file,
            "source":"test",
            "model":"GPT-5.6 Terra",
            "reasoning":"medium",
            "activity":"coding",
            "megavault_mode":"FAST",
            "resources":["repo:test"],
            "max_attempts":3,
            "readiness_evidence":list(evidence or []),
        }

    def _state(self, *, status="waiting", actionable=0, project_name="Example"):
        return {
            "item":{
                "work_item_id":"wi:test","status":status,"actionable":actionable,
                "executor_policy":"auto","repo":"gernalix/example",
                "project_id":"51","project_name":project_name,"prompt_id":None,
                "blocker":"exact execution context missing",
            },
            "tags":[],"active_runs":0,"execution_spec":None,
            "prompt":None,"prompt_body":None,
        }

    def test_one_command_prepares_waiting_item_without_dispatch_and_replays(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt_file=Path(tmp)/"prompt.md"
            prompt_text="# Goal\nImplement the bounded change.\n"
            prompt_file.write_text(prompt_text,encoding="utf-8")
            spec=self._spec(prompt_file,evidence=["Verified intake is ready."])
            state=self._state(project_name="PersonalHub")
            calls=[]

            def refresh(_):
                return copy.deepcopy(state)

            def submit(operation,arguments,phase):
                calls.append((operation,phase))
                if operation=="reconcile_item":
                    state["item"].update(status="pending",actionable=1,blocker=None)
                elif operation=="prepare_codex":
                    pid="123456"
                    state["item"].update(prompt_id=pid,executor_policy="codex")
                    state["prompt"]={
                        "prompt_id":pid,"model":spec["model"],
                        "reasoning":spec["reasoning"],"prompt_type":"Prompt",
                        "current_path":"prompts/test-123456.md",
                    }
                    state["prompt_body"]=prep._expected_prompt_body(pid,prompt_text)
                elif operation=="auto_configure":
                    execution=arguments["execution"]
                    state["execution_spec"]={
                        "work_item_id":"wi:test","activity":execution["activity"],
                        "model":execution["model"],"reasoning":execution["reasoning"],
                        "worktree":execution["worktree"],"project_url":None,
                        "goal_mode":0,"command_json":None,
                        "resources_json":json.dumps(sorted(execution["resources"])),
                        "max_attempts":execution["max_attempts"],
                    }
                else:
                    self.fail("unexpected operation "+operation)

            def allocate(_item,_prompt_id):
                return "/tmp/c2-test-worktree"

            result=prep.prepare(
                spec,authority={"fencing_token":1},refresh=refresh,
                submit_phase=submit,allocate_worktree=allocate,
                sandbox_roots=lambda _worktree:["/tmp/repo/.git"],
            )
            self.assertEqual("prepared",result["status"])
            self.assertFalse(result["dispatched"])
            self.assertEqual(["/tmp/repo/.git"],result["sandbox_writable_roots"])
            self.assertEqual(
                [("reconcile_item","ready"),("prepare_codex","prompt"),
                 ("auto_configure","execution")],calls)
            self.assertEqual("pending",state["item"]["status"])
            self.assertEqual(0,state["active_runs"])

            before=list(calls)
            replay=prep.prepare(
                spec,authority={"fencing_token":2},refresh=refresh,
                submit_phase=submit,allocate_worktree=allocate,
                sandbox_roots=lambda _worktree:["/tmp/repo/.git"],
            )
            self.assertEqual("prepared",replay["status"])
            self.assertEqual(before,calls)

    def test_waiting_item_without_readiness_evidence_stays_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt_file=Path(tmp)/"prompt.md"
            prompt_file.write_text("# Goal\nX\n",encoding="utf-8")
            spec=self._spec(prompt_file)
            state=self._state()
            original=copy.deepcopy(state)

            with self.assertRaisesRegex(prep.PrepareCodexError,"work_item_waiting:exact execution context missing"):
                prep.prepare(
                    spec,authority={"fencing_token":1},
                    refresh=lambda _wid: copy.deepcopy(state),
                    submit_phase=lambda *_args: self.fail("must not submit"),
                    allocate_worktree=lambda *_args: self.fail("must not allocate"),
                    sandbox_roots=lambda _worktree:[],
                )
            self.assertEqual(original,state)

    def test_existing_execution_spec_conflict_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt_file=Path(tmp)/"prompt.md"
            prompt_text="# Goal\nX\n"
            prompt_file.write_text(prompt_text,encoding="utf-8")
            spec=self._spec(prompt_file)
            state=self._state(status="pending",actionable=1)
            state["item"].update(prompt_id="123456",executor_policy="codex")
            state["prompt"]={
                "prompt_id":"123456","model":spec["model"],
                "reasoning":spec["reasoning"],"prompt_type":"Prompt",
                "current_path":"prompts/test-123456.md",
            }
            state["prompt_body"]=prep._expected_prompt_body("123456",prompt_text)
            state["execution_spec"]={
                "activity":"coding","model":spec["model"],
                "reasoning":spec["reasoning"],"worktree":"/tmp/other",
                "project_url":None,"goal_mode":0,"command_json":None,
                "resources_json":json.dumps(spec["resources"]),"max_attempts":3,
            }
            with self.assertRaisesRegex(prep.PrepareCodexError,"execution_spec_conflict:worktree"):
                prep.prepare(
                    spec,authority={"fencing_token":1},
                    refresh=lambda _wid: copy.deepcopy(state),
                    submit_phase=lambda *_args: self.fail("must not submit"),
                    allocate_worktree=lambda *_args:"/tmp/c2-test-worktree",
                    sandbox_roots=lambda _worktree:[],
                )

    def test_spec_requires_explicit_model_reasoning_and_activity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"prompt.md").write_text("# Goal\nX\n",encoding="utf-8")
            path=root/"spec.json"
            path.write_text(json.dumps({
                "work_item_id":"wi:test","prompt_file":"prompt.md","source":"test",
                "model":"GPT-5.6 Terra","activity":"coding",
            }),encoding="utf-8")
            with self.assertRaisesRegex(prep.PrepareCodexError,"reasoning_required"):
                prep.load_spec(path)

    def test_repo_slug_normalization_is_structural_not_title_based(self):
        self.assertEqual("gernalix/example",prep._repo_slug("https://github.com/gernalix/example.git"))
        self.assertEqual("gernalix/example",prep._repo_slug("git@github.com:gernalix/example.git"))


if __name__=="__main__":
    unittest.main()
