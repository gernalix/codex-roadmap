#!/usr/bin/env python3
"""Native runtime recovery; retain canonical fencing and run identities."""
import json, sys, time, sqlite3, subprocess
from pathlib import Path
ROOT = Path.home()/'.local/share/c2-supervisor/worktree/tools'
sys.path.insert(0, str(ROOT))
import c2_runtime as runtime
from c2_supervisor_lease import connect, snapshot, DEFAULT_DB, record_activity, publish_runtime_identity
from c2_supervisor_resume import read_recovery_pointer, read_canonical_state, resume
DB = Path.home()/'.local/state/c2-supervisor/roadmap.sqlite3'
with connect(DEFAULT_DB) as lease:
    row = snapshot(lease)
    if not row:
        raise RuntimeError('supervisor_lease_missing')
    if row['state'] != 'active' or row['lease_expires_at'] <= time.time():
        pointer = read_recovery_pointer(Path(row['recovery_pointer']))
        result = resume(lease, read_canonical_state(DB), pointer)
        print(json.dumps(result), flush=True)
        if result['outcome'] == 'BLOCKED':
            raise RuntimeError(result['reason'])
        row = snapshot(lease)
    row = record_activity(lease, supervisor_id=row['supervisor_id'], token=row['fencing_token'], operation='runtime:native-tick', ttl=600)
    publish_runtime_identity(row)
original_launch = runtime._launch_worker
def launch(run_id, db_path):
    with sqlite3.connect('file:'+str(db_path)+'?mode=ro', uri=True) as db:
        triage = db.execute("SELECT 1 FROM work_item_runs r JOIN work_item_tags t USING(work_item_id) WHERE r.run_id=? AND t.tag='c2:issue-triage'", (run_id,)).fetchone()
    if not triage:
        return original_launch(run_id, db_path)
    if runtime._worker_unit_active(run_id):
        return
    command = ['systemd-run','--user','--collect','--unit=c2-run-'+run_id,sys.executable,str(Path(__file__).with_name('triage.py')),'--run-id',run_id,'--db',str(db_path)]
    result = subprocess.run(command, capture_output=True, text=True, env=runtime._user_systemd_environment())
    if result.returncode and not runtime._worker_unit_active(run_id):
        raise RuntimeError('native_triage_launch_failed:'+result.stderr)
runtime._launch_worker = launch
sys.argv = [str(ROOT/'c2_runtime.py'), '--db',str(DB),'--supervisor-id',row['supervisor_id'],'--fencing-token',str(row['fencing_token'])]
raise SystemExit(runtime.main())
