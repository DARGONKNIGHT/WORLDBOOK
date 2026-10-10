#!/usr/bin/env python3
"""v15 regression checks, entirely S-grade and frozen-world safe."""
import hashlib
import json
import unittest
from datetime import timedelta
from scenario_v15 import ANCHOR, FROZEN, at, build, option, run_case

class PlanningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=FROZEN.read_bytes()
        cls.case=run_case()
        cls.out={d["candidate_id"]:d for d in cls.case.decisions}
        cls.journal={x["event_id"]:x for x in cls.case.events.journal}

    @classmethod
    def tearDownClass(cls):
        assert FROZEN.read_bytes()==cls.raw

    def test_01_official_frozen(self):
        obj=json.loads(self.raw)
        self.assertIsNone(obj["player_character"])
        self.assertIsNone(obj["game_clock_time"])
        self.assertEqual([],obj["actual_game_events"])
        self.assertEqual(31,len(obj["people"]))
        self.assertTrue(obj["geography"]["observation_only"])

    def test_02_inventory_trigger_without_purchase(self):
        self.assertEqual("scheduled",self.out["store_stocktake"]["choice"])
        self.assertEqual("scheduled",self.out["shop_repair_question"]["choice"])
        self.assertEqual([],self.case.events.state["transactions"])

    def test_03_overlap_declined_before_scheduling(self):
        self.assertEqual("reservation_conflict",self.out["store_break_conflict"]["reason"])
        self.assertNotIn("V15:store_break_conflict",self.journal)

    def test_04_knowledge_delay_family(self):
        self.assertEqual("missing_knowledge",self.out["premature_family_reply"]["reason"])
        self.assertEqual("scheduled",self.out["family_ack_after_delivery"]["choice"])
        self.assertLess(self.journal["V15:technician_shift_notice:deliver"]["at"],
                        self.journal["V15:family_ack_after_delivery"]["at"])
        self.assertIn("test_shift_notice",self.case.events.state["knowledge"]["P006"])
        self.assertNotIn("test_shift_notice",self.case.events.state["knowledge"]["P011"])

    def test_05_knowledge_delay_repair(self):
        self.assertEqual("missing_knowledge",self.out["premature_quote"]["reason"])
        self.assertEqual("scheduled",self.out["quote_after_delivery"]["choice"])
        self.assertEqual("missing_knowledge",self.out["too_early_quote_review"]["reason"])
        self.assertEqual("scheduled",self.out["quote_review_after_receipt"]["choice"])
        self.assertNotIn("test_repair_question",self.case.events.state["knowledge"]["P005"])

    def test_06_unknown_money_not_zero(self):
        self.assertEqual("balance_unknown",self.out["cash_unknown_course"]["reason"])

    def test_07_cost_guard(self):
        self.assertEqual("insufficient_sandbox_balance",self.out["excess_cost"]["reason"])

    def test_08_unauthorized_payment_not_proposed(self):
        self.assertEqual("unsupported_action_requires_separate_approval",
                         self.out["no_unauthorized_purchase"]["reason"])
        self.assertEqual(0,len(self.case.events.state["ledger"]))

    def test_09_unconfirmed_calendar_not_assumed(self):
        self.assertEqual("calendar_unconfirmed",self.out["unconfirmed_saturday_school"]["reason"])

    def test_10_low_value_can_choose_no_action(self):
        self.assertEqual("low_priority_no_action",self.out["low_value_no_action"]["reason"])

    def test_11_budgets_not_mutated(self):
        self.assertEqual(self.case.events.initial_state["balances_cents"],
                         self.case.events.state["balances_cents"])

    def test_12_event_log_replay_and_hash(self):
        self.assertEqual([],self.case.audit())
        self.assertEqual(64,len(self.case.events.journal[-1]["hash"]))

    def test_13_determinism(self):
        again=run_case()
        self.assertEqual(self.case.decisions,again.decisions)
        self.assertEqual(self.case.events.journal,again.events.journal)

    def test_14_duplicate_decision_rejected(self):
        p=build()
        x=option("once","P005",10,minutes=5,location="S_TEST_FACTORY")
        p.decide(ANCHOR,[x])
        with self.assertRaises(ValueError):
            p.decide(ANCHOR,[x])

    def test_15_required_skill(self):
        p=build()
        x=option("unauthorized_skill","P005",10,minutes=5,location="S_TEST_FACTORY",
                 required_skill="doctor")
        self.assertEqual("required_skill_missing",p.decide(ANCHOR,[x])[0]["reason"])

    def test_16_absent_profile_no_forced_life(self):
        p=build()
        x=option("no_assumed_daily_life","P031",10,minutes=5,location="S_TEST_WORKSHOP")
        self.assertEqual("unknown_or_unmodelled_actor",p.decide(ANCHOR,[x])[0]["reason"])

    def test_17_no_regression_in_time(self):
        p=build()
        p.events.run(ANCHOR+timedelta(hours=1))
        with self.assertRaises(ValueError):
            p.decide(ANCHOR,[])

    def test_18_no_arbitrary_new_actor(self):
        p=build()
        x=option("nonexistent","P999",10,minutes=5,location="S_TEST_FACTORY")
        self.assertEqual("unknown_or_unmodelled_actor",p.decide(ANCHOR,[x])[0]["reason"])

if __name__=="__main__":
    unittest.main(verbosity=2)
