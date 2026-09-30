#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, datetime as dt, json, os, re, select, shutil, sqlite3, subprocess, sys, termios, time, tty
from pathlib import Path

THREAD="01a0e719-60ff-7b91-82db-1d7c55787c67"
WT=Path("/home/daniele/.local/share/c2-supervisor/worktrees/roadmap-batch-reconciliation-20260928")
CHECKPOINT=WT/"operations/task-state/ROADMAP-BATCH-RECONCILIATION-20260928.md"
CACHE=Path.home()/".cache/c2-roadmap-dashboard"
BARE=CACHE/"repo.git"; DB=CACHE/"roadmap.sqlite"; STAMP=CACHE/"updated_at"; STATE=CACHE/"state.json"
USAGE_DB=Path.home()/".local/share/codex-usage-monitor/codex_usage_monitor.db"
PROJECT_MAP=WT/"operations/task-state/ROADMAP-PROJECT-MAP-20260928.md"
PROGRESS_HISTORY=CACHE/"progress-history.json"
RPC_PIDFILE=Path.home()/".local/state/c2-roadmap-goal-watchdog/rpc-worker.pid"
WATCHDOG_STATE=Path.home()/".local/state/c2-roadmap-goal-watchdog/state.json"
SEMANTIC_STATE=Path.home()/".local/share/c2-master-watcher/state.json"
SEMANTIC_HEARTBEAT=Path.home()/".local/share/c2-master-watcher/heartbeat.json"
SESSION_ROOT=Path.home()/".codex/sessions"
REMOTE="https://github.com/gernalix/codex-roadmap.git"
TERMINAL={"completed","superseded","cancelled","failed","waived"}
ACTIVE={"pending","waiting","blocked","claimed","running","recovering"}
ANSI_BRIGHT_GREEN="\033[1;92m"
ANSI_RESET="\033[0m"

def sh(args,cwd=None,timeout=25):
    return subprocess.run(args,cwd=cwd,text=True,capture_output=True,timeout=timeout)

def refresh_cache(force=False):
    CACHE.mkdir(parents=True,exist_ok=True)
    age=10**9
    if STAMP.exists():
        try: age=time.time()-float(STAMP.read_text().strip())
        except: pass
    if not force and DB.exists() and age<60: return age,False
    if not BARE.exists():
        sh(["git","init","--bare",str(BARE)])
        sh(["git","-C",str(BARE),"remote","add","origin",REMOTE])
    f=sh(["git","-C",str(BARE),"fetch","--depth=1","origin","main"],timeout=40)
    if f.returncode: return age,False
    tmp=DB.with_suffix(".new")
    with tmp.open("wb") as out:
        p=subprocess.run(["git","-C",str(BARE),"show","FETCH_HEAD:roadmap.sqlite"],stdout=out,stderr=subprocess.DEVNULL)
    if p.returncode==0 and tmp.stat().st_size>0:
        tmp.replace(DB); STAMP.write_text(str(time.time()))
        return 0,True
    tmp.unlink(missing_ok=True); return age,False

def dbconn():
    c=sqlite3.connect(f"file:{DB}?mode=ro",uri=True); c.row_factory=sqlite3.Row; return c

def parse_checkpoint():
    text=CHECKPOINT.read_text(encoding="utf-8") if CHECKPOINT.exists() else ""
    batches={}; current=None
    for line in text.splitlines():
        m=re.match(r"## (\d\d)/([^ ]+) \((\d+)\)",line)
        if m:
            current=m.group(1); batches[current]={"name":m.group(2),"declared":int(m.group(3)),"ids":[]}; continue
        if current and line.startswith("## "): current=None
        if current:
            q=re.match(r"- `([^`]+)`",line)
            if q: batches[current]["ids"].append(q.group(1))
    survivors=[]
    block=re.search(r"## Canonical survivor order\n(.*?)(?=\n## )",text,re.S)
    if block: survivors=re.findall(r"^\d+\. `([^`]+)`",block.group(1),re.M)
    fresh=set(re.findall(r"^### Fresh semantic reconciliation: (\d\d)/",text,re.M))
    nexts=re.findall(r"^## Next action\n(.*?)(?=\n## |\n### |\Z)",text,re.M|re.S)
    next_action=re.sub(r"\s+"," ",nexts[-1].strip()) if nexts else ""
    focus=None
    for prefix in re.findall(r"`?((?:wi:|prompt:)?[0-9A-Za-z]+)…?`?",next_action):
        if prefix.startswith(("wi:","prompt:")):
            hits=[x for x in survivors if x.startswith(prefix)]
        else:
            hits=[x for x in survivors if x.split(":",1)[-1].startswith(prefix)]
        if len(hits)==1: focus=hits[0]; break
    focus_batch=None
    if focus:
        for n,b in batches.items():
            if focus in b["ids"]: focus_batch=n; break
    return text,batches,survivors,fresh,next_action,focus,focus_batch

def iso_ts(x):
    if x is None:return None
    try:return dt.datetime.fromisoformat(str(x).replace("Z","+00:00")).timestamp()
    except:return None

def issue_metrics(c,now,window):
    start=now-window
    rows=[dict(r) for r in c.execute("select observed_at_ms,created_at,triaged_at_ms,state from issue_inbox")]
    tri=[r for r in rows if r["triaged_at_ms"] and r["triaged_at_ms"]/1000>=start]
    d=[]
    ints=[]
    for r in rows:
        a=r["observed_at_ms"]/1000 if r["observed_at_ms"] else iso_ts(r["created_at"])
        if a is None: continue
        b=r["triaged_at_ms"]/1000 if r["triaged_at_ms"] else now
        if r["triaged_at_ms"] and r["triaged_at_ms"]/1000>=start: d.append(r["triaged_at_ms"]/1000-a)
        a=max(a,start); b=min(b,now)
        if b>a: ints.append((a,b))
    ints.sort(); merged=[]
    for a,b in ints:
        if not merged or a>merged[-1][1]: merged.append([a,b])
        else: merged[-1][1]=max(merged[-1][1],b)
    occupied=sum(b-a for a,b in merged)
    return {"processed":len(tri),"avg":sum(d)/len(d) if d else None,"empty":max(0,100*(1-occupied/window))}

def task_metrics(c,now,window):
    rec=[dict(r) for r in c.execute("select * from work_item_result_receipts where captured_at>=?",(now-window,))]
    cnt=collections.Counter(r["outcome"] for r in rec); durations=[]
    for r in rec:
        q=c.execute("select created_at from work_item_runs where run_id=?",(r["run_id"],)).fetchone()
        if not q: continue
        a=iso_ts(q[0])
        if a is None:
            try:a=float(q[0])
            except:continue
        if r["captured_at"]>=a:durations.append(r["captured_at"]-a)
    return {"n":len(rec),"outcomes":cnt,"avg":sum(durations)/len(durations) if durations else None,"avg_n":len(durations)}

def fmt_duration(sec):
    if sec is None:return "—"
    sec=max(0,int(sec))
    if sec<60:return f"{sec}s"
    if sec<3600:return f"{sec//60}m"
    return f"{sec//3600}h {(sec%3600)//60:02d}m"

def relative_age(sec):
    if sec is None:return "tempo sconosciuto"
    sec=max(0,int(sec))
    if sec<60:return "adesso" if sec<10 else f"{sec}s fa"
    minutes=sec//60
    if minutes<60:return f"{minutes} min fa"
    hours,rem=divmod(minutes,60)
    if hours<24:return f"{hours} h fa" if not rem else f"{hours} h {rem} min fa"
    days,remh=divmod(hours,24)
    return f"{days} g fa" if not remh else f"{days} g {remh} h fa"

def age_from_iso(value, now):
    ts=iso_ts(value) if value else None
    return relative_age(now-ts) if ts is not None else "tempo sconosciuto"

def with_age(text, age):
    text=str(text or '').strip()
    return f"{text}  ·  {age}" if text else age

def usage_metrics(now):
    if not USAGE_DB.exists(): return None
    try:
        c=sqlite3.connect(f"file:{USAGE_DB}?mode=ro",uri=True); c.row_factory=sqlite3.Row
        rows=[dict(r) for r in c.execute("select acquired_at_utc,weekly_used_percent,weekly_remaining_percent from quota_snapshots where acquisition_status='ok' order by acquired_at_utc desc limit 400")]
        if not rows:return None
        latest=rows[0]; lt=iso_ts(latest["acquired_at_utc"]); target=(lt or now)-3600
        prior=min(rows,key=lambda r:abs((iso_ts(r["acquired_at_utc"]) or 0)-target))
        burn=float(latest["weekly_used_percent"])-float(prior["weekly_used_percent"])
        return {"remaining":latest["weekly_remaining_percent"],"used":latest["weekly_used_percent"],"burn1h":burn,"age":now-(lt or now)}
    except:return None

def load_state():
    try:return json.loads(STATE.read_text())
    except:return {"statuses":{},"events":[]}

def update_transitions(c,now,refreshed):
    st=load_state()
    if refreshed or not st.get("statuses"):
        cur={r["work_item_id"]:r["status"] for r in c.execute("select work_item_id,status from work_items")}
        prev=st.get("statuses",{})
        events=st.get("events",[])
        if prev:
            for k,v in cur.items():
                old=prev.get(k)
                if old and old!=v: events.append({"t":now,"from":old,"to":v,"id":k})
        st={"statuses":cur,"events":[e for e in events if e["t"]>=now-86400]}
        STATE.write_text(json.dumps(st))
    return [e for e in st.get("events",[]) if e["t"]>=now-300]

def granular_progress(c, batches, survivors, fresh):
    project_text=PROJECT_MAP.read_text(encoding='utf-8') if PROJECT_MAP.exists() else ''
    project_ids=set(re.findall(r'^\| `([^`]+)` \| `[^`]+` \|',project_text,re.M))
    root_batch={x:n for n,b in batches.items() for x in b['ids']}
    runnable={r[0] for r in c.execute('select work_item_id from v_work_item_runnable')}
    starts={r[0] for r in c.execute('select distinct work_item_id from work_item_executor_starts')}
    receipts={r[0] for r in c.execute('select distinct work_item_id from work_item_result_receipts')}
    checkpoints={r[0] for r in c.execute('select distinct work_item_id from work_item_checkpoints')}
    nodes={}; owner={}
    query='WITH RECURSIVE d(id) AS (SELECT ? UNION ALL SELECT w.work_item_id FROM d JOIN work_items w ON w.parent_id=d.id) SELECT id FROM d'
    for root in survivors:
        for rr in c.execute(query,(root,)):
            nodes[rr[0]]=1
            owner.setdefault(rr[0],root)
    score=0; total=0
    for wid in nodes:
        row=c.execute('select * from work_items where work_item_id=?',(wid,)).fetchone()
        if not row: continue
        root=owner[wid]; batch=root_batch.get(root)
        milestones=[
            bool(row['project_id'] or row['project_name'] or wid in project_ids or root in project_ids),
            bool(batch),
            bool(batch in fresh),
            row['status'] in TERMINAL|ACTIVE,
            row['status'] in TERMINAL|{'waiting','blocked'} or wid in runnable or wid in starts,
            row['status'] in TERMINAL or wid in checkpoints or wid in receipts or wid in starts or (row['status'] in ('waiting','blocked') and bool(row['blocker'])),
            row['status'] in TERMINAL or wid in receipts or wid in checkpoints,
            row['status'] in TERMINAL,
        ]
        score+=sum(milestones); total+=len(milestones)
    return score,total,len(nodes)

def progress_delta(now,score,total):
    try: hist=json.loads(PROGRESS_HISTORY.read_text())
    except: hist=[]
    hist=[x for x in hist if x.get('t',0)>=now-86400]
    hist.append({'t':now,'score':score,'total':total})
    compact=[]
    for x in hist:
        if not compact or x['t']-compact[-1]['t']>=20 or x is hist[-1]:
            compact.append(x)
        else:
            compact[-1]=x
    PROGRESS_HISTORY.write_text(json.dumps(compact[-500:]))
    target=now-300
    prior=min(compact,key=lambda x:abs(x['t']-target)) if compact else {'score':score}
    return score-int(prior.get('score',score))

def progress_bar(done,total,width=20):
    if total <= 0: return '░'*width
    filled=max(0,min(width,round(width*done/total)))
    return '█'*filled+'░'*(width-filled)

def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid,0)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False

def goal_runtime(now: float) -> dict:
    rpc_pid=None; rpc_alive=False
    try:
        rpc_pid=int(RPC_PIDFILE.read_text().strip())
        rpc_alive=_pid_alive(rpc_pid)
    except Exception:
        pass
    proc=sh(['ps','-eo','pid=,args=']).stdout
    cli_alive=any('codex exec resume' in line and THREAD in line for line in proc.splitlines())
    helper_alive=any(('/home/daniele/.local/bin/c2-master-goal-start' in line or '/home/daniele/.local/bin/c2-steer-main-goal' in line) and 'python' in line for line in proc.splitlines())
    env=os.environ.copy(); uid=os.getuid(); env.setdefault('XDG_RUNTIME_DIR',f'/run/user/{uid}'); env.setdefault('DBUS_SESSION_BUS_ADDRESS',f'unix:path=/run/user/{uid}/bus')
    try:
        service_alive=subprocess.run(['systemctl','--user','is-active','c2-master-goal.service'],text=True,capture_output=True,env=env,timeout=2).stdout.strip()=='active'
    except Exception:
        service_alive=False
    worker_alive=rpc_alive or cli_alive or helper_alive or service_alive
    newest=None
    if SESSION_ROOT.exists():
        for path in SESSION_ROOT.glob(f'**/rollout-*{THREAD}.jsonl'):
            try:
                mt=path.stat().st_mtime
                if newest is None or mt>newest: newest=mt
            except OSError:
                pass
    event_age=(now-newest) if newest is not None else None
    return {'worker_alive':worker_alive,'rpc_alive':rpc_alive,'rpc_pid':rpc_pid,
            'cli_alive':cli_alive,'helper_alive':helper_alive,'service_alive':service_alive,'event_age':event_age}

def watchdog_state(now: float) -> dict:
    try:
        state=json.loads(WATCHDOG_STATE.read_text())
        state['age']=max(0.0, now-float(state.get('observed_at') or 0))
        if state['age']>180:
            state['stale']=True
        return state
    except Exception:
        return {'mode':None,'goal_status':None,'age':None,'stale':True}

def semantic_state(now: float) -> dict | None:
    try:
        sem=json.loads(SEMANTIC_STATE.read_text())
        hb=json.loads(SEMANTIC_HEARTBEAT.read_text())
        hb_ts=hb.get("checked_at") or hb.get("observed_at") or hb.get("last_analysis") or 0
        hb_age=max(0.0, now-float(hb_ts))
        sem["heartbeat_age"]=hb_age
        sem["analysis_age"]=max(0.0, now-float(sem.get("analyzed_at") or 0))
        if hb_age>60:
            return None
        return sem
    except Exception:
        return None

def active_survivor_focus(c, survivors):
    survivor_set=set(survivors)
    rows=c.execute("""SELECT w.work_item_id,w.title,w.status,w.current_action,w.next_action,w.updated_at,r.state,r.lease_until
        FROM work_item_runs r JOIN work_items w ON w.work_item_id=r.work_item_id
        WHERE r.state IN ('claimed','running','recovering')
        ORDER BY r.created_at DESC""").fetchall()
    for row in rows:
        if row['work_item_id'] in survivor_set and row['status'] not in TERMINAL:
            return row
    return None

def human_focus(focus, title, next_action):
    fid=str(focus or '')
    low=(str(title or '')+' '+str(next_action or '')).lower()
    if 'b45503242' in fid or 'discendenti task-state' in low:
        return (
            'Pulizia dei vecchi task C2 rimasti attivi per errore',
            'Sta creando il meccanismo che permette di archiviare in sicurezza vecchi sotto-task duplicati o obsoleti, senza toccare quelli ancora validi.',
            'Poi potrà chiudere quei residui, sistemare la vecchia Fase C e proseguire con la Fase D.'
        )
    if 'phase d' in low or 'fedora' in low and 'oracle' in low and 'datasette' in low:
        return ('Fase D: portare automaticamente i dati da Fedora a Oracle e Datasette',
                'Sta costruendo il passaggio che raccoglie i dati dal PC Fedora, li invia a Oracle e li rende consultabili in Datasette.',
                'Poi passerà alla Fase E: rendere Datasette più semplice e immediato da usare.')
    if 'personalhub' in low:
        return ('PersonalHub', 'Sta lavorando sul prossimo blocco PersonalHub già riconciliato.',
                'Continuerà con il successivo task PH valido, senza riaprire duplicati già chiusi.')
    if title:
        return (str(title), 'Sta lavorando sull’attività attualmente prioritaria della roadmap.',
                'Quando questa sarà chiusa o parcheggiata, passerà automaticamente alla successiva.')
    return ('Roadmap C2', 'Sta proseguendo il lavoro già pianificato.',
            'Passerà automaticamente al prossimo blocco utile.')

def render(force_refresh=False):
    now=time.time(); age,refreshed=refresh_cache(force_refresh)
    if not DB.exists(): return 'C2 — STATO ROADMAP\n\nImpossibile leggere lo stato canonico.'
    text,batches,survivors,fresh,next_action,focus,focus_batch=parse_checkpoint()
    c=dbconn()
    statuses={r['work_item_id']:r['status'] for r in c.execute('select work_item_id,status from work_items')}
    runnable={r[0] for r in c.execute('select work_item_id from v_work_item_runnable')}
    surv=[x for x in survivors if x in statuses]
    terminal=[x for x in surv if statuses[x] in TERMINAL]
    waiting=[x for x in surv if statuses[x] in ('blocked','waiting') or (statuses[x]=='pending' and x not in runnable)]
    ready=[x for x in surv if x in runnable]
    other=[x for x in surv if x not in set(terminal+waiting+ready)]
    granular_done,granular_total,granular_nodes=granular_progress(c,batches,survivors,fresh)
    granular_delta=progress_delta(now,granular_done,granular_total)
    t1=task_metrics(c,now,3600)
    usage=usage_metrics(now)

    runtime=goal_runtime(now)
    worker_alive=runtime['worker_alive']
    env=os.environ.copy(); uid=os.getuid(); env['XDG_RUNTIME_DIR']=f'/run/user/{uid}'; env['DBUS_SESSION_BUS_ADDRESS']=f'unix:path=/run/user/{uid}/bus'
    try:
        watchdog=subprocess.run(['systemctl','--user','is-active','c2-roadmap-goal-watchdog.service'],text=True,capture_output=True,env=env).stdout.strip()=='active'
    except: watchdog=False
    wd=watchdog_state(now)
    wd_mode=None if wd.get('stale') else wd.get('mode')
    goal_status=None if wd.get('stale') else wd.get('goal_status')

    rec_batches=sum(1 for x in [f'{i:02d}' for i in range(13)] if x in fresh)
    sem=semantic_state(now)
    sem_status=sem.get('status') if sem else None
    semantic_wait=sem_status in ('waiting_external','globally_quiescent')
    active_focus=active_survivor_focus(c,surv)
    if sem:
        now_title=sem.get('headline') or 'Stato C2'
        now_desc=with_age(sem.get('current') or 'Il watcher AI non ha fornito una descrizione.', relative_age(sem.get('analysis_age')))
        after_desc=sem.get('next') or 'Attendere il prossimo cambiamento di stato.'
        semantic_intervention=(sem.get('intervention') or '').strip() or 'No.'
    else:
        conditional_wait = watchdog and wd_mode in ('conditional_complete','waiting_gate') and not worker_alive
        if active_focus is not None:
            focus=active_focus['work_item_id']
            title=active_focus['title']
            action=active_focus['current_action'] or active_focus['next_action'] or next_action
            now_title,now_desc,after_desc=human_focus(focus,title,action)
            now_desc=with_age(now_desc, age_from_iso(active_focus['updated_at'],now))
        elif conditional_wait:
            now_title='Nessuna attività eseguibile al momento'
            now_desc='Il Goal è correttamente in attesa di un gate canonico.'
            after_desc='Il watchdog riattiverà automaticamente la stessa thread quando il gate cambia.'
        elif worker_alive:
            now_title='Riconciliazione e avanzamento della roadmap'
            now_desc='Il Goal principale è attivo.'
            after_desc='Proseguirà con il prossimo task sicuro.'
        else:
            now_title='Nessuna attività esecutiva in corso'
            now_desc='Non risulta un worker del Goal attivo in questo momento.'
            after_desc='Il watchdog proverà a recuperare il Goal se esiste ancora lavoro eseguibile.'
        semantic_intervention=None

    event_age=runtime['event_age']
    recent=event_age is not None and event_age <= 120
    ok=worker_alive and watchdog and recent
    healthy_wait=semantic_wait if sem else (watchdog and wd_mode in ('conditional_complete','waiting_gate') and not worker_alive)
    if sem:
        status_word={
            'working':'🟢 STA LAVORANDO NORMALMENTE',
            'recovering':'🟡 RECUPERO AUTOMATICO IN CORSO',
            'waiting_external':'🔵 IN ATTESA DI UN GATE ESTERNO',
            'globally_quiescent':'✅ QUIESCENZA GLOBALE RAGGIUNTA',
            'stalled':'🔴 STALLO RILEVATO',
            'needs_user':'🟠 SERVE IL TUO INTERVENTO',
            'degraded':'🟡 STATO DEGRADATO',
            'stopped':'🔴 GOAL ARRESTATO',
        }.get(sem_status,'🟡 STATO WATCHER NON RICONOSCIUTO')
    elif ok:
        status_word='🟢 STA LAVORANDO NORMALMENTE'
    elif healthy_wait:
        status_word='🔵 GOAL IN ATTESA DI UN GATE CANONICO'
    elif worker_alive and watchdog:
        status_word='🔵 WORKER ATTIVO, IN ATTESA DI UN NUOVO EVENTO'
    elif watchdog:
        status_word='🟡 LAVORO FERMO, RECUPERO AUTOMATICO ATTIVO'
    else:
        status_word='🔴 RICHIEDE CONTROLLO'
    done_pct=round(100*len(terminal)/len(surv)) if surv else 0
    raw_ready=len(ready)
    if healthy_wait:
        effective_ready=0
        effective_waiting=len(surv)-len(terminal)
        effective_other=0
    else:
        effective_ready=len(ready)
        effective_waiting=len(waiting)
        effective_other=len(other)
    batch_pct=round(100*rec_batches/13)
    pass_n=int(t1['outcomes'].get('PASS',0)); fail_n=t1['n']-pass_n

    lines=['C2 — STATO ROADMAP','='*64,'',status_word]
    if usage:
        quota=f"Consumo Codex ultima ora: ~{usage['burn1h']:+.0f} punti"
        if usage['remaining']<=10: quota+='  ⚠️ quota quasi esaurita'
        lines.append(quota)
    granular_pct=round(100*granular_done/granular_total,1) if granular_total else 0
    delta_text=f"  (+{granular_delta} negli ultimi 5 min)" if granular_delta>0 else ''
    lines += ['', 'PROGRESSO',
              f"Avanzamento operativo {progress_bar(granular_done,granular_total)}  {granular_done}/{granular_total} passi ({granular_pct:.1f}%){delta_text}",
              f"Attività completate: {len(terminal)}/{len(surv)}",
              '',
              f"Questa è l’unica percentuale mostrata perché è la più sensibile: segue {granular_nodes} task e sotto-task attraverso più tappe verificabili, quindi può muoversi anche prima che un'intera attività sia chiusa.",
              f"Restano {len(surv)-len(terminal)} attività reali: {effective_ready} eseguibili ora, {effective_waiting} condizionali/in attesa e {effective_other} già in corso o in aggiornamento.",
              'Le attività che aspettano qualcosa non sono necessariamente problemi: molte dipendono da un login, un dispositivo collegato, controlli automatici esterni o condizioni future.',
              '', 'COSA STA FACENDO ADESSO',
              now_title,
              now_desc,
              '', 'DOPO',
              after_desc,
              '', 'VELOCITÀ RECENTE']
    if t1['n']:
        extra = '' if fail_n == 0 else (f'; 1 si è fermata senza chiudersi positivamente.' if fail_n == 1 else f'; {fail_n} si sono fermate senza chiudersi positivamente.')
        lines.append(f"Nell’ultima ora sono state chiuse {t1['n']} attività: {pass_n} con esito positivo" + extra + ('.' if fail_n == 0 else ''))
    else:
        lines.append('Nell’ultima ora non risultano nuove attività chiuse.')
    if sem:
        intervention=semantic_intervention
    elif healthy_wait:
        intervention='Non per il sistema: il Goal è correttamente in attesa. Alcuni gate esterni possono comunque richiedere un’azione manuale.'
    elif worker_alive and watchdog:
        intervention='No. Il lavoro corrente può continuare da solo.'
    else:
        intervention='Possibile: il sistema non risulta completamente operativo.'
    lines += ['', 'SERVE IL TUO INTERVENTO?',
              intervention,
              '', 'INFO',
              '• “13/13 gruppi analizzati” significa che ogni gruppo è stato ripulito da duplicati, vecchi task e falsi blocker. Non significa che tutto sia già implementato.',
              '• Le 56 attività sono la roadmap reale rimasta dopo aver escluso gran parte della burocrazia, dei duplicati e dei residui legacy.',
              f"• Dati della roadmap aggiornati circa {int(age)} secondi fa. La UI si aggiorna ogni 2 secondi; il watchdog è deterministico e non effettua chiamate periodiche a modelli AI.",
              f"• Ultimo evento del Goal: {fmt_duration(event_age)} fa; worker RPC/CLI rilevato: {'sì' if worker_alive else 'no'}."]
    if healthy_wait and raw_ready:
        lines.append(f"• Il DB marca {raw_ready} item tecnicamente runnable, ma l’ultima riconciliazione del Goal li considera condizionali/non-dispatchabili: eseguibili ora = 0.")
    if wd_mode:
        lines.append(f"• Stato watchdog: {wd_mode}; stato Goal: {goal_status or 'sconosciuto'}.")
    if sem:
        lines.append(f"• Watchdog deterministico · stato {fmt_duration(sem.get('analysis_age'))} fa · heartbeat {fmt_duration(sem.get('heartbeat_age'))} fa · confidenza {sem.get('confidence','—')}.")
        for why in (sem.get('why') or [])[:3]:
            lines.append('• Watchdog: '+str(why))
        discoveries=sem.get('discoveries') or []
        if discoveries:
            material=sum(1 for d in discoveries if d.get('material') and d.get('confidence')=='high')
            lines.append(f"• Discovery AI nell’ultimo evento: {len(discoveries)}; eleggibili per Inbox: {material}.")
    else:
        lines.append('• Watchdog deterministico non disponibile: dashboard in fallback locale.')
    return '\n'.join(lines)


def _progress_pct(output: str) -> float | None:
    match=re.search(r"Avanzamento operativo .*?\((\d+(?:\.\d+)?)%\)",output)
    return float(match.group(1)) if match else None

def _with_visit_delta(output: str, delta: float | None) -> str:
    if delta is None or abs(delta) < 0.05:
        return output
    sign='+' if delta>0 else ''
    label=f"  {ANSI_BRIGHT_GREEN}({sign}{delta:.1f}% mentre eri fuori focus){ANSI_RESET}"
    return re.sub(
        r"(Avanzamento operativo .*?\(\d+(?:\.\d+)?%\))",
        lambda m:m.group(1)+label,
        output,
        count=1,
    )

def _focus_reporting_start() -> dict | None:
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None
    fd=sys.stdin.fileno()
    try:
        old=termios.tcgetattr(fd)
        tty.setcbreak(fd)
        sys.stdout.write("\033[?1004h")
        sys.stdout.flush()
        return {"fd":fd,"old":old,"buffer":""}
    except Exception:
        return None

def _focus_reporting_stop(state: dict | None) -> None:
    if not state:
        return
    try:
        sys.stdout.write("\033[?1004l")
        sys.stdout.flush()
    finally:
        try: termios.tcsetattr(state["fd"],termios.TCSADRAIN,state["old"])
        except Exception: pass

def _focus_events(state: dict) -> list[bool]:
    try:
        data=os.read(state["fd"],1024).decode("utf-8","ignore")
    except Exception:
        return []
    buf=state.get("buffer","")+data
    events=[]
    while True:
        found=[(buf.find("\033[I"),True),(buf.find("\033[O"),False)]
        found=[item for item in found if item[0]>=0]
        if not found:
            state["buffer"]=buf[-2:]
            break
        idx,focused=min(found,key=lambda item:item[0])
        events.append(focused)
        buf=buf[idx+3:]
    return events

def _live_screen_enter():
    # Keep a live dashboard out of the terminal's normal scrollback.  The
    # alternate screen is exactly what full-screen terminal UIs use for this.
    sys.stdout.write("\033[?1049h\033[3J\033[2J\033[H")
    sys.stdout.flush()


def _live_screen_exit():
    sys.stdout.write("\033[?1049l")
    sys.stdout.flush()


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--live",action="store_true"); ap.add_argument("--interval",type=float,default=2); ap.add_argument("--refresh",action="store_true"); a=ap.parse_args()
    if not a.live:
        print(render(a.refresh)); return
    _live_screen_enter()
    first=True
    focus=_focus_reporting_start()
    away_baseline=None
    visit_delta=None
    last_pct=None
    try:
        while True:
            raw=render(a.refresh and first); first=False
            last_pct=_progress_pct(raw)
            out=_with_visit_delta(raw,visit_delta)
            sys.stdout.write("\033[2J\033[H"+out+"\n"); sys.stdout.flush()
            deadline=time.monotonic()+max(1,a.interval)
            while True:
                remaining=deadline-time.monotonic()
                if remaining<=0:
                    break
                if not focus:
                    time.sleep(remaining)
                    break
                readable,_,_=select.select([focus["fd"]],[],[],remaining)
                if not readable:
                    break
                for focused in _focus_events(focus):
                    if not focused:
                        away_baseline=last_pct
                        visit_delta=None
                    else:
                        # Force one canonical refresh exactly when the user comes back.
                        fresh=render(True)
                        current=_progress_pct(fresh)
                        if away_baseline is not None and current is not None:
                            visit_delta=current-away_baseline
                        else:
                            visit_delta=None
                        last_pct=current
                        shown=_with_visit_delta(fresh,visit_delta)
                        sys.stdout.write("\033[2J\033[H"+shown+"\n"); sys.stdout.flush()
                        deadline=time.monotonic()+max(1,a.interval)
    except KeyboardInterrupt:
        pass
    finally:
        _focus_reporting_stop(focus)
        _live_screen_exit()

if __name__=="__main__": main()
