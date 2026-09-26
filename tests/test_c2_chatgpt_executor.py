from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from c2_chatgpt_executor import dispatch

class FakeTaskConfig:
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)
        self.thresholds=SimpleNamespace(generation_stall_s=600,max_recovery_attempts=9)

def fake_supervisor_types():
    return FakeBrowser,lambda url:url.startswith('https://chatgpt.com/c/'),FakeTaskConfig,FakeStore

class FakeBrowser:
    def __init__(self):self.calls=[]
    def new_chat(self,task,message):
        self.calls.append((task,message))
        return None,'https://chatgpt.com/c/fixture',None
class FakeStore:
    def __init__(self):self.tasks=[]
    def save_task(self,task):self.tasks.append(task)

class BrowserExecutorTests(unittest.TestCase):
    def setUp(self):
        self.supervisor_patch=patch('c2_chatgpt_executor._supervisor_types',fake_supervisor_types)
        self.supervisor_patch.start()
        self.addCleanup(self.supervisor_patch.stop)
    def test_new_chat_uses_work_item_identity_and_replays_without_resend(self):
        with tempfile.TemporaryDirectory() as tmp:
            browser=FakeBrowser();store=FakeStore()
            data={'executor':'rdc','activity':'gui','project_url':'https://chatgpt.com/g/g-p-project'}
            receipt=Path(tmp)/'receipt.json';db=Path(tmp)/'roadmap.sqlite'
            for _ in range(2):
                result=dispatch(run_id='one',work_item_id='wi:fixture',metadata=data,
                    prompt='Use the GUI',db_path=db,receipt=receipt,browser=browser,store=store)
                self.assertEqual('started',result['phase'])
            self.assertEqual(1,len(browser.calls))
            self.assertEqual('TASK_ID=wi:fixture\nUse the GUI',browser.calls[0][1])
            self.assertEqual(1,len(store.tasks))
            self.assertTrue(store.tasks[0].state_file.startswith('c2-db:'))
            self.assertEqual(40,store.tasks[0].thresholds.generation_stall_s)
            self.assertEqual(3,store.tasks[0].thresholds.max_recovery_attempts)
    def test_ambiguous_start_does_not_send_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            class Broken(FakeBrowser):
                def new_chat(self,task,message):
                    self.calls.append((task,message));raise TimeoutError('lost URL')
            browser=Broken();metadata={'executor':'chatgpt','activity':'semantic',
                'project_url':'https://chatgpt.com/g/g-p-project'}
            receipt=Path(tmp)/'r.json'
            with self.assertRaises(TimeoutError):
                dispatch(run_id='one',work_item_id='wi:fixture',metadata=metadata,
                    prompt='Decide',db_path=Path(tmp)/'db',receipt=receipt,
                    browser=browser,store=FakeStore())
            result=dispatch(run_id='one',work_item_id='wi:fixture',metadata=metadata,
                    prompt='Decide',db_path=Path(tmp)/'db',receipt=receipt,
                    browser=browser,store=FakeStore())
            self.assertEqual('starting',result['phase'])
            self.assertEqual(1,len(browser.calls))

    def test_restart_rebinds_one_open_chat_without_new_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            class Match:
                def filter(self,**kwargs):
                    return self
                def count(self):
                    return 1
            class Page:
                url='https://chatgpt.com/c/fixture'
                def locator(self,*args):
                    return Match()
            class Context:
                pages=[Page()]
            browser=FakeBrowser()
            browser.browser=type('Browser',(),{'contexts':[Context()]})()
            metadata={'executor':'chatgpt','activity':'semantic',
                'project_url':'https://chatgpt.com/g/g-p-project'}
            receipt=Path(tmp)/'r.json'
            receipt.write_text(__import__('json').dumps({'run_id':'one',
                'work_item_id':'wi:fixture','project_url':metadata['project_url'],
                'phase':'starting'}))
            store=FakeStore()
            result=dispatch(run_id='one',work_item_id='wi:fixture',metadata=metadata,
                prompt='Decide',db_path=Path(tmp)/'db',receipt=receipt,
                browser=browser,store=store)
            self.assertEqual('started',result['phase'])
            self.assertEqual(0,len(browser.calls))
            self.assertEqual(1,len(store.tasks))
            self.assertEqual(40,store.tasks[0].thresholds.generation_stall_s)
