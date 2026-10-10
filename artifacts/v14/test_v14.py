#!/usr/bin/env python3
"""Deterministic unit tests for actual invariants, not claims of realism."""
import json
import hashlib
import unittest
from datetime import timedelta
from pathlib import Path
from scenario_v14 import build_fixture, ANCHOR, FROZEN
from engine_v14 import SandboxEngine


class SandboxTests(unittest.TestCase):
    def setUp(self):
        self.raw=FROZEN.read_bytes()
        self.official=json.loads(self.raw)

    def test_canonical_frozen(self):
        self.assertIsNone(self.official['player_character'])
        self.assertIsNone(self.official['game_clock_time'])
        self.assertFalse(self.official['game_started'])
        self.assertEqual([],self.official['actual_game_events'])
        self.assertTrue(self.official['geography']['observation_only'])

    def test_31_npcs_and_no_known_bank_amounts(self):
        people=self.official['people']
        self.assertEqual(31,len(people))
        self.assertEqual(15,sum(p['tier']=='core' for p in people))
        self.assertEqual(16,sum(p['tier']=='candidate' for p in people))
        self.assertTrue(all(p['cash_balance_cny'] is None for p in people))

    def test_30_day_run_does_not_mutate_canonical(self):
        build_fixture().run(ANCHOR+timedelta(days=30))
        self.assertEqual(self.raw,FROZEN.read_bytes())

    def test_balanced_internal_money_and_no_negative_accounts(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        self.assertEqual([],e.audit())
        self.assertEqual(sum(e.initial_state['balances_cents'].values()),sum(e.state['balances_cents'].values()))
        self.assertTrue(all(n>=0 for n in e.state['balances_cents'].values()))
        self.assertEqual(3,len(e.state['transactions']))

    def test_rejected_overdraw_and_duplicate(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        bad={v['event_id']:v for v in e.journal if v['status']=='rejected'}
        self.assertIn('DUPLICATE-PAYMENT',bad)
        self.assertIn('OVERDRAW',bad)
        self.assertNotIn('TX-OVERDRAW',e.state['transactions'])

    def test_no_instant_travel_or_overlapping_tasks(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        bad={v['event_id'] for v in e.journal if v['status']=='rejected'}
        self.assertIn('ACTIVITY-CONFLICT',bad)
        self.assertIn('IN-TRANSIT-ACTIVITY',bad)
        self.assertIn('WRONG-LOCATION',bad)
        self.assertEqual('TEST_SITE_A',e.state['locations']['P014'])
        self.assertNotIn('P014',e.state['transit'])

    def test_message_delivered_only_after_delay_and_to_intended_actor(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        msg={x['event_id']:x for x in e.journal}
        sent=msg['FAMILY-SHIFT-NOTE']
        delivered=msg['FAMILY-SHIFT-NOTE:deliver']
        self.assertGreater(delivered['at'],sent['at'])
        self.assertIn('shift_notice',e.state['knowledge']['P006'])
        self.assertNotIn('shift_notice',e.state['knowledge']['P003'])
        self.assertIn('shift_notice_ack',e.state['knowledge']['P005'])

    def test_narrow_policy_reply_only_after_delivery(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        msg={x['event_id']:x for x in e.journal}
        self.assertLess(msg['FAMILY-SHIFT-NOTE:deliver']['at'],msg['FAMILY-SHIFT-NOTE:deliver:policy_reply']['at'])

    def test_permission_denial(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        m={x['event_id']:x for x in e.journal}
        self.assertEqual('rejected',m['UNAUTHORIZED-APPROVAL']['status'])
        self.assertEqual('completed',m['AUTHORIZED-APPROVAL']['status'])
        self.assertEqual(1,len(e.state['approved']))

    def test_replay_and_hash_chain(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        self.assertEqual([],e.audit())
        self.assertEqual(64,len(e.journal[-1]['hash']))

    def test_determinism(self):
        a=build_fixture().run(ANCHOR+timedelta(days=30))
        b=build_fixture().run(ANCHOR+timedelta(days=30))
        self.assertEqual(a.report(),b.report())
        self.assertEqual(a.journal,b.journal)

    def test_simulation_has_no_player(self):
        e=build_fixture().run(ANCHOR+timedelta(days=30))
        self.assertNotIn('player_character',e.state)
        self.assertEqual(self.official['player_character'],None)

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            SandboxEngine('2026-10-09T09:00:00',['P001'],{},{} )

    def test_duplicate_schedule_id_rejected(self):
        e=SandboxEngine(ANCHOR,['P001'],{}, {})
        e.schedule('X',ANCHOR,'routine_check','P001')
        with self.assertRaises(ValueError):e.schedule('X',ANCHOR,'routine_check','P001')


if __name__=='__main__':
    unittest.main(verbosity=2)
