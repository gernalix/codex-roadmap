from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))

from c2_supervisor_lease import acquire, connect, record_activity, snapshot
from c2_supervisor_resume import _submit_claim, _submit_renewal, read_recovery_pointer, resume


def pointer(previous_id='old', previous_token=1, blocker=None):
    return {
        'path':'/tmp/recovery.md',
        'exact_next_action':'Run the one bounded scheduler cycle.',
        'state':{
            'previous_supervisor_id':previous_id,
            'previous_fencing_token':previous_token,
            'active_runs':['run-ph'],
            'active_executors':['worker-ph'],
            'preserve_resources':['device:pixel'],
            'blocker':blocker,
        },
    }


class SupervisorResumeTests(unittest.TestCase):
    def _claim(self, calls):
        return lambda row,_pointer: (calls.append((row['supervisor_id'],row['fencing_token'])) or
                                    {'issue_number':'fixture'})

    def test_recovery_pointer_is_read_once_and_returns_exact_action(self):
        text=('C2_RECOVERY_STATE={"previous_supervisor_id":"old",'
              '"previous_fencing_token":1,"active_runs":[],"active_executors":[],'
              '"preserve_resources":[],"blocker":null}\n'
              '# Exact next action\nRun the bounded action.\n')
        with patch.object(Path,'read_text',return_value=text) as read:
            result=read_recovery_pointer(Path('/tmp/recovery.md'))
        read.assert_called_once_with(encoding='utf-8')
        self.assertEqual('Run the bounded action.',result['exact_next_action'])

    def test_clean_resume_acquires_once_and_returns_exact_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            with connect(Path(tmp)/'lease.sqlite3') as db:
                result=resume(db,{'authority':None},pointer(previous_token=5),now=200,
                    supervisor_id='new',claim=self._claim(calls),publish=lambda _row:None)
                self.assertEqual('RESUMED',result['outcome'])
                self.assertEqual(6,result['fencing_token'])
                self.assertEqual('Run the one bounded scheduler cycle.',result['exact_next_action'])
                replay=resume(db,{'authority':None},pointer(previous_token=5),now=201,
                    claim=self._claim(calls),publish=lambda _row:None)
                self.assertEqual('RESUMED',replay['outcome'])
                self.assertEqual([('new',6),('new',6)],calls)

    def test_claim_replay_keeps_acquisition_expiry_after_local_renewal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with connect(Path(tmp)/'lease.sqlite3') as db:
                row = acquire(db, owner='one', pointer='/tmp/recovery.md',
                              supervisor_id='new', now=100, ttl=180)
                with patch('c2_supervisor_resume.submit_document',
                           return_value={'submission': 'pending'}) as submit:
                    _submit_claim(row, pointer())
                    renewed = record_activity(db, supervisor_id='new', token=1,
                                              operation='control:test', now=150)
                    _submit_claim(renewed, pointer())
                first, second = submit.call_args_list
                self.assertEqual(first.args[0], second.args[0])
                self.assertEqual(first.kwargs['request_key'], second.kwargs['request_key'])
                self.assertEqual(280, first.args[0]['operations'][0]['arguments']
                                 ['supervisor_authority']['lease_expires_at'])

    def test_expired_canonical_same_fence_submits_renewal_not_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            with connect(Path(tmp)/'lease.sqlite3') as db:
                acquire(db, owner='one', pointer='/tmp/recovery.md',
                        supervisor_id='new', minimum_token=1, now=100, ttl=180)
                local = record_activity(db, supervisor_id='new', token=2,
                                        operation='control:test', now=220)
                canonical = {'authority': {
                    'supervisor_id': 'new', 'fencing_token': 2,
                    'lease_expires_at': 200, 'renewed_at': 100,
                }}
                with patch('c2_supervisor_resume.submit_document',
                           return_value={'submission': 'pending'}) as submit:
                    result = resume(db, canonical, pointer(), now=250)
                self.assertEqual('RESUMED', result['outcome'])
                self.assertEqual('canonical_renewal', result['phase'])
                self.assertEqual({'submission': 'pending'}, result['claim'])
                self.assertEqual(2, snapshot(db)['fencing_token'])
                self.assertEqual('c2_renew_supervisor',
                                 submit.call_args.args[0]['operations'][0]['op'])
                self.assertEqual(local['lease_expires_at'],
                                 submit.call_args.args[0]['operations'][0]['arguments']
                                 ['supervisor_authority']['lease_expires_at'])

    def test_renewal_request_key_tracks_expiry_without_reusing_claim_key(self):
        row = {'supervisor_id': 'new', 'fencing_token': 2,
               'acquired_at': 100, 'lease_expires_at': 330}
        with patch('c2_supervisor_resume.submit_document',
                   return_value={'submission': 'pending'}) as submit:
            _submit_renewal(row, pointer())
            first = submit.call_args
            _submit_renewal(dict(row), pointer())
            second = submit.call_args
            _submit_renewal({**row, 'lease_expires_at': 390}, pointer())
            third = submit.call_args
        self.assertEqual(first.args[0], second.args[0])
        self.assertEqual(first.kwargs['request_key'], second.kwargs['request_key'])
        self.assertNotEqual(first.kwargs['request_key'], third.kwargs['request_key'])

    def test_live_successor_is_already_active_without_duplicate_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            with connect(Path(tmp)/'lease.sqlite3') as db:
                acquire(db,owner='successor',pointer='/tmp/recovery.md',
                        supervisor_id='new',minimum_token=1,now=100,ttl=180)
                canonical={'authority':{'supervisor_id':'new','fencing_token':2,
                    'lease_expires_at':280,'claimed_at':100,'renewed_at':100}}
                result=resume(db,canonical,pointer(),now=110,
                    claim=self._claim(calls),publish=lambda _row:None)
                self.assertEqual('ALREADY_ACTIVE',result['outcome'])
                self.assertEqual([],calls)

    def test_stale_authority_takes_over_at_180_seconds_and_preserves_resources(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            with connect(Path(tmp)/'lease.sqlite3') as db:
                acquire(db,owner='old',pointer='/tmp/recovery.md',
                        supervisor_id='old',now=0,ttl=1000)
                canonical={'authority':{'supervisor_id':'old','fencing_token':1,
                    'lease_expires_at':100,'claimed_at':0,'renewed_at':0},
                    'active_runs':[{'run_id':'run-c2'}],
                    'active_resources':['repo:external']}
                result=resume(db,canonical,pointer(),now=180,supervisor_id='new',
                    claim=self._claim(calls),publish=lambda _row:None)
                self.assertEqual('STALE_TAKEOVER',result['outcome'])
                self.assertEqual(['device:pixel','repo:external'],result['preserve_resources'])
                self.assertEqual(['run-c2','run-ph'],result['active_runs'])
                self.assertEqual([('new',2)],calls)

    def test_pre_takeover_thresholds_do_not_create_successor(self):
        with tempfile.TemporaryDirectory() as tmp:
            with connect(Path(tmp)/'lease.sqlite3') as db:
                acquire(db,owner='old',pointer='/tmp/recovery.md',
                        supervisor_id='old',now=0,ttl=1000)
                canonical={'authority':{'supervisor_id':'old','fencing_token':1,
                    'lease_expires_at':1000,'claimed_at':0,'renewed_at':0}}
                self.assertEqual('suspected_stall',resume(
                    db,canonical,pointer(),now=40,claim=lambda *_:self.fail('claim'),
                    publish=lambda _row:None)['phase'])
                self.assertEqual('final_verification',resume(
                    db,canonical,pointer(),now=90,claim=lambda *_:self.fail('claim'),
                    publish=lambda _row:None)['phase'])

    def test_pointer_blocker_is_the_only_blocked_fast_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            with connect(Path(tmp)/'lease.sqlite3') as db:
                result=resume(db,{'authority':None},pointer(blocker='login required'),now=1,
                    claim=lambda *_:self.fail('claim'),publish=lambda _row:None)
                self.assertEqual({'outcome':'BLOCKED','reason':'pointer_blocker',
                                  'blocker':'login required'},result)


if __name__=='__main__':
    unittest.main()
