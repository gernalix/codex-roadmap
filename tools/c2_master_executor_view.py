#!/usr/bin/env python3
import glob, json, os, sqlite3, subprocess, sys, time
from pathlib import Path

THREAD='01a0e719-60ff-7b91-82db-1d7c55787c67'
DB=Path.home()/'.local/state/c2-supervisor/roadmap.sqlite3'
DISABLE='\x1b[?1000l\x1b[?1002l\x1b[?1003l\x1b[?1006l\x1b[?1015l\x1b[?2004l'


def find_path():
    ps=glob.glob('/home/daniele/.codex/sessions/**/rollout-*'+THREAD+'.jsonl',recursive=True)
    return max(ps,key=os.path.getmtime) if ps else None


def service_active(name):
    try:
        env=os.environ.copy(); uid=os.getuid()
        env.setdefault('XDG_RUNTIME_DIR',f'/run/user/{uid}')
        env.setdefault('DBUS_SESSION_BUS_ADDRESS',f'unix:path=/run/user/{uid}/bus')
        r=subprocess.run(['systemctl','--user','is-active',name],text=True,capture_output=True,env=env,timeout=2)
        return r.stdout.strip()=='active'
    except Exception:
        return False


def delegated_state():
    out={'inbox':None,'run_id':None,'state':None,'lease_left':None,'worker_alive':False,'last_triaged_age':None}
    try:
        c=sqlite3.connect(f'file:{DB}?mode=ro',uri=True); c.row_factory=sqlite3.Row
        out['inbox']=c.execute('select count(*) from v_issue_inbox_pending_ordered').fetchone()[0]
        row=c.execute("""select r.run_id,r.state,r.lease_until from work_item_runs r
            join work_items w using(work_item_id) join work_item_tags t using(work_item_id)
            where t.tag='c2:issue-triage' and w.status='running'
              and r.state in ('claimed','running','recovering')
            order by r.created_at desc limit 1""").fetchone()
        if row:
            out.update(run_id=row['run_id'],state=row['state'],lease_left=float(row['lease_until'] or 0)-time.time())
        last=c.execute('select max(triaged_at_ms) from issue_inbox where triaged_at_ms is not null').fetchone()[0]
        if last: out['last_triaged_age']=max(0,time.time()-float(last)/1000)
        c.close()
    except Exception:
        pass
    if out['run_id']:
        try:
            ps=subprocess.run(['ps','-eo','args='],text=True,capture_output=True,timeout=2).stdout
            out['worker_alive']=f'c2_worker.py --run-id {out["run_id"]}' in ps
        except Exception:
            pass
    return out


def last_master_messages(limit=3):
    path=find_path()
    if not path: return []
    rows=[]
    try:
        for line in open(path,encoding='utf-8',errors='ignore').read().splitlines()[-1800:]:
            try:o=json.loads(line)
            except Exception:continue
            p=o.get('payload') or {}
            if o.get('type')=='response_item' and p.get('type')=='message' and p.get('role')=='assistant':
                txt=' '.join(x.get('text','') for x in p.get('content',[]) if x.get('type')=='output_text').strip()
                if txt:
                    ts=o.get('timestamp',''); hh=ts[11:19] if len(ts)>=19 else ts
                    rows.append((hh,txt))
    except Exception:
        return []
    return rows[-limit:]


def fmt_age(v):
    if v is None:return '—'
    if v<60:return f'{int(v)}s'
    return f'{int(v//60)}m {int(v%60)}s'

sys.stdout.write(DISABLE)
try:
    while True:
        d=delegated_state()
        master=service_active('c2-master-goal.service')
        sys.stdout.write(DISABLE+'\x1b[2J\x1b[H')
        print('C2 CODEX EXECUTOR — LIVE')
        print('='*80)
        if d['worker_alive']:
            print('STATO: LAVORO DELEGATO IN CORSO')
            print('Master Goal: PAUSED/IDLE per design   Worker triage: ATTIVO')
        elif master:
            print('STATO: MASTER GOAL IN ESECUZIONE')
            print('Master Goal: ATTIVO   Worker triage: non rilevato')
        else:
            print('STATO: NESSUN EXECUTOR ATTIVO')
            print('Master Goal: INATTIVO   Worker triage: non rilevato')
        print()
        print(f'Inbox pendente: {d["inbox"] if d["inbox"] is not None else "—"}')
        if d['run_id']:
            lease='scaduta' if d['lease_left'] is not None and d['lease_left']<0 else f'{int(d["lease_left"] or 0)}s'
            print(f'Run triage: {d["state"]}   lease: {lease}   ultimo triage: {fmt_age(d["last_triaged_age"])} fa')
            print(f'Run ID: {d["run_id"]}')
        print()
        print('ULTIMI MESSAGGI DEL MASTER GOAL')
        print('-'*80)
        msgs=last_master_messages(3)
        if not msgs:
            print('Nessun messaggio disponibile.')
        for hh,txt in msgs:
            one=' '.join(txt.split())
            if len(one)>900: one=one[:897]+'...'
            print(f'[{hh}] {one}')
            print()
        print('Questa vista è read-only. Se il Master è paused ma il worker è attivo, C2 sta lavorando normalmente.')
        sys.stdout.flush()
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write(DISABLE); sys.stdout.flush()
