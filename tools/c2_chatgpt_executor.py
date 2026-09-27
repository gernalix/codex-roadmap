"""Launch a replaceable ChatGPT/RDC browser worker from canonical C2 identity."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from c2_codex_executor import persist
from c2_supervisor_source import require_supervisor_source

C2_GENERATION_SUSPECT_S=40
C2_MAX_RECOVERY_ATTEMPTS=3
LANE_STATE=Path.home()/'.local/state/chatgpt-rdc-supervisor/global.json'
KILL_SWITCH=Path.home()/'.config/c2/disable-chat-supervisor'


class ChatWorkerError(RuntimeError):
    pass


def lane_degraded(path: Path = LANE_STATE) -> bool:
    try:
        return json.loads(path.read_text()).get('chatgpt_lane',{}).get('state') in ('suspected','global_degraded')
    except (OSError,ValueError,TypeError):
        return False


def _supervisor_types():
    try:
        source=require_supervisor_source()
    except RuntimeError as exc:
        raise ChatWorkerError(str(exc)) from exc
    if str(source) not in sys.path:
        sys.path.insert(0,str(source))
    from chatgpt_rdc_supervisor.browser import ChatGPTBrowser, is_persisted_chat_url
    from chatgpt_rdc_supervisor.model import TaskConfig
    from chatgpt_rdc_supervisor.storage import Store
    return ChatGPTBrowser, is_persisted_chat_url, TaskConfig, Store


def _task_config(TaskConfig, *, work_item_id: str, db_path: Path,
                 chat_url: str, project_url: str):
    task=TaskConfig(task_id=work_item_id,
        state_file='c2-db:'+str(Path(db_path).resolve())+'#'+work_item_id,
        repo_root=str(Path(db_path).resolve().parent),
        chat_url=chat_url,project_url=project_url)
    thresholds=getattr(task,'thresholds',None)
    if thresholds is None:
        raise ChatWorkerError('supervisor_thresholds_unavailable')
    thresholds.generation_suspect_s=C2_GENERATION_SUSPECT_S
    thresholds.generation_verify_s=90
    thresholds.generation_stall_s=180
    thresholds.max_recovery_attempts=C2_MAX_RECOVERY_ATTEMPTS
    return task


def dispatch(*, run_id: str, work_item_id: str, metadata: dict, prompt: str,
             db_path: Path, receipt: Path, browser=None, store=None):
    if KILL_SWITCH.exists():
        return {'phase':'suspended','chat_url':None,'resubmitted':False}
    if lane_degraded():
        return {'phase':'suspended','chat_url':None,'resubmitted':False}
    if metadata.get('executor') not in ('chatgpt','rdc') or metadata.get('activity') not in ('gui','semantic'):
        raise ChatWorkerError('browser_executor_not_configured')
    project_url=metadata.get('project_url')
    if not project_url or not str(project_url).startswith('https://chatgpt.com/'):
        raise ChatWorkerError('exact_project_url_required')
    if not prompt or not work_item_id:
        raise ChatWorkerError('canonical_prompt_required')
    identity='TASK_ID='+work_item_id
    message=identity+'\n'+prompt
    if receipt.exists():
        state=json.loads(receipt.read_text())
        if state['run_id']!=run_id or state['work_item_id']!=work_item_id or state['project_url']!=project_url:
            raise ChatWorkerError('browser_run_identity_conflict')
        if state['phase']=='starting':
            ChatGPTBrowser, is_persisted_chat_url, TaskConfig, Store=_supervisor_types()
            owned=browser is None
            browser=browser or ChatGPTBrowser()
            store=store or Store()
            try:
                if owned:
                    browser.connect()
                matches=[]
                for context in getattr(getattr(browser,'browser',None),'contexts',[]):
                    for page in context.pages:
                        if not is_persisted_chat_url(page.url):
                            continue
                        own=page.locator('[data-message-author-role="user"]').filter(has_text=identity)
                        if own.count():
                            matches.append(page.url)
                if len(matches)==1:
                    task=_task_config(TaskConfig,work_item_id=work_item_id,
                        db_path=db_path,chat_url=matches[0],project_url=project_url)
                    store.save_task(task)
                    state.update(phase='started',chat_url=matches[0])
                    persist(receipt,state)
            finally:
                if owned:
                    browser.close()
        # A sent message without an acknowledged URL remains ambiguous;
        # never create another chat from the same run.
        return {'phase':state['phase'],'chat_url':state.get('chat_url'),'resubmitted':False}
    ChatGPTBrowser, is_persisted_chat_url, TaskConfig, Store=_supervisor_types()
    store=store or Store()
    load_task=getattr(store,'load_task',None)
    if load_task is not None:
        try:
            previous=load_task(work_item_id)
        except FileNotFoundError:
            previous=None
        if previous is not None and is_persisted_chat_url(previous.chat_url):
            if previous.project_url != project_url:
                raise ChatWorkerError('browser_work_item_project_conflict')
            state={'run_id':run_id,'work_item_id':work_item_id,'project_url':project_url,
                   'phase':'started','chat_url':previous.chat_url}
            persist(receipt,state)
            return {'phase':'started','chat_url':previous.chat_url,'resubmitted':False}
    state={'run_id':run_id,'work_item_id':work_item_id,'project_url':project_url,'phase':'starting'}
    persist(receipt,state)
    task=_task_config(TaskConfig,work_item_id=work_item_id,db_path=db_path,
        chat_url='',project_url=project_url)
    owned=browser is None
    browser=browser or ChatGPTBrowser()
    try:
        if owned:
            browser.connect()
        page,url,error=browser.new_chat(task,message)
        if error or not is_persisted_chat_url(url):
            raise ChatWorkerError('chat_launch_unconfirmed')
        task.chat_url=url
        store.save_task(task)
        state.update(phase='started',chat_url=url)
        persist(receipt,state)
        return {'phase':'started','chat_url':url,'resubmitted':False}
    finally:
        if owned:
            browser.close()
