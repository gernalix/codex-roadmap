#!/usr/bin/env python3
import json,os,subprocess,sys,time
from pathlib import Path

ROOT=Path('/home/daniele/.local/share/c2-master-watcher')
STATE=ROOT/'state.json'
HEARTBEAT=ROOT/'heartbeat.json'
ALERT=ROOT/'attention-alert.json'
DISABLE='\x1b[?1000l\x1b[?1002l\x1b[?1003l\x1b[?1006l\x1b[?1015l\x1b[?2004l'

def load(p,default):
    try:return json.loads(p.read_text())
    except Exception:return default

def service(name):
    try:
        r=subprocess.run(['systemctl','--user','is-active',name],text=True,capture_output=True,timeout=2)
        return r.stdout.strip() or 'unknown'
    except Exception:return 'unknown'

try:
    while True:
        s=load(STATE,{})
        h=load(HEARTBEAT,{})
        a=load(ALERT,{})
        sys.stdout.write(DISABLE+'\x1b[2J\x1b[H')
        print('C2 MASTER WATCHDOG — DETERMINISTICO / LIVE READ ONLY')
        print('='*80)
        print('Nessun modello AI periodico: fatti locali → recovery meccanica → notifica solo se serve')
        print()
        print('STATUS:',s.get('status','—'),'  PHASE:',s.get('phase','—'),
              '  SOURCE:',s.get('decision_source','—'),
              '  CONFIDENCE:',s.get('confidence','—'))
        print('MASTER GOAL SERVICE:',service('c2-master-goal.service'),
              '  WATCHER TIMER:',service('c2-master-watcher.timer'))
        print('HEARTBEAT:',time.strftime('%H:%M:%S',time.localtime(h.get('checked_at',0))) if h.get('checked_at') else '—',
              '  ANALYZED:',h.get('analyzed','—'),
              '  MASTER WORKER:',h.get('master_worker_alive','—'))
        print('NOTIFICHE: Telegram + Fedora',
              '  ALLARME ATTIVO:', 'SÌ' if a.get('active') else 'no',
              '  trigger: needs_user → recovery quando il Goal riparte')
        print()
        print('COSA VEDE')
        print(s.get('headline','—'))
        print(s.get('current','—'))
        print()
        print('DOPO')
        print(s.get('next','—'))
        print()
        print('INTERVENTO')
        print(s.get('intervention') or 'No.')
        print()
        print('WHY')
        for x in (s.get('why') or [])[:5]:
            print('•',x)
        print()
        print('WAKE GOAL:',s.get('should_wake_goal','—'),
              '  WAKE RESULT:',s.get('wake_result','—'))
        print()
        print('Aggiornamento UI ogni 2s; il watchdog non chiama Luna, Sol o altri modelli.')
        sys.stdout.flush()
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    sys.stdout.write(DISABLE); sys.stdout.flush()
