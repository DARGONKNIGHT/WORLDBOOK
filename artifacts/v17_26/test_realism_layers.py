#!/usr/bin/env python3
"""45 cross-domain invariants for v17-v26, no actual world clock changes."""
import json, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from realism_layers import *

TZ=timezone(timedelta(hours=8))
D=datetime(2026,10,9,9,0,tzinfo=TZ)
at=lambda m:(D+timedelta(minutes=m)).isoformat()
BASE=Path(__file__).resolve().parents[1]
OFFICIAL=(BASE/"v14/official_world_state_frozen_v13.json").read_bytes()

class Tests17Transit(unittest.TestCase):
    def setUp(self):
        self.t=TransitV17()
        self.t.add("T1","A","B",at(10),at(30))
        self.t.add("T2","B","C",at(40),at(60))
    def test_01_direct_not_actual_ticket(self):
        x=self.t.direct("A","B",at(0))
        self.assertEqual("S_FIXTURE",x[0]["grade"])
        self.assertEqual(1,len(x))
    def test_02_waits_for_transfer(self):
        self.assertEqual(1,len(self.t.via("A","B","C",at(0),5)))
        self.assertEqual([],self.t.via("A","B","C",at(0),15))
    def test_03_no_train_if_schedule_missing(self):
        self.assertEqual([],self.t.direct("A","D",at(0)))
    def test_04_bad_temporal_trip(self):
        with self.assertRaises(ValueError):self.t.add("T3","A","B",at(20),at(10))
    def test_05_no_retroactive_departure(self):
        self.assertEqual([],self.t.direct("A","B",at(11)))

class Tests18Places(unittest.TestCase):
    def setUp(self):
        self.p=PlacesV18()
        self.p.add("O1","school",40.1880155,116.7077492,"S_TEST","fixture:fictional-school","SCHOOL S fixture")
    def test_01_grounded_identity(self):
        self.assertEqual(1,len(self.p.query("school")))
    def test_02_unknown_open(self):
        self.assertEqual("U",self.p.get("O1")["open_status"])
    def test_03_duplicate_place(self):
        with self.assertRaises(ValueError):self.p.add("O1","hospital",40,116,"S_TEST","fixture")
    def test_04_invalid_coords(self):
        with self.assertRaises(ValueError):self.p.add("O2","hospital",120,200,"S_TEST","fixture")

class Tests19Housing(unittest.TestCase):
    def setUp(self):
        self.h=HousingV19({"tenant":300000,"owner":20000})
        self.h.lease("L1","tenant","owner","S_HOUSE_1",50000)
    def test_01_balanced_rent(self):
        before=sum(self.h.balances.values());self.h.pay("L1","2026-10")
        self.assertEqual(before,sum(self.h.balances.values()))
    def test_02_no_duplicate(self):
        self.h.pay("L1","2026-10")
        with self.assertRaises(ValueError):self.h.pay("L1","2026-10")
    def test_03_unknown_money(self):
        self.h.lease("L2","missing","owner","S_HOUSE_2",10000)
        with self.assertRaisesRegex(ValueError,"unknown account"):self.h.pay("L2","2026-10")
    def test_04_insufficient(self):
        h=HousingV19({"a":1,"b":0});h.lease("X","a","b","p",100)
        with self.assertRaises(ValueError):h.pay("X","2026-10")

class Tests20Commerce(unittest.TestCase):
    def setUp(self):
        self.c=CommerceV20({"S_WIDGET":4},{"buyer":20000,"seller":0})
        self.c.quote("Q1","seller","buyer","S_WIDGET",2,5000)
    def test_01_quote_is_not_sale(self):
        self.assertEqual(4,self.c.inventory["S_WIDGET"])
        self.assertEqual(20000,self.c.balances["buyer"])
    def test_02_fulfilment_transition(self):
        self.c.accept("Q1");self.c.dispatch("Q1");self.c.receive("Q1")
        self.assertEqual("received",self.c.orders["Q1"]["shipment"])
        self.assertEqual(2,self.c.inventory["S_WIDGET"])
    def test_03_payment_independent(self):
        self.c.accept("Q1");self.c.pay("Q1")
        self.assertEqual(10000,self.c.balances["buyer"])
        self.assertEqual("not_dispatched",self.c.orders["Q1"]["shipment"])
    def test_04_payment_once(self):
        self.c.accept("Q1");self.c.pay("Q1")
        with self.assertRaises(ValueError):self.c.pay("Q1")
    def test_05_stock_precondition(self):
        c=CommerceV20({},{"a":1,"b":2});c.quote("Q","a","b","widget",2,1);c.accept("Q")
        with self.assertRaises(ValueError):c.dispatch("Q")

class Tests21Employment(unittest.TestCase):
    def setUp(self):
        self.e=EmploymentV21({"company":100000})
        self.e.hire("E1","worker","company","S_SITE",30000)
    def test_01_unknown_tax_not_guessed(self):
        with self.assertRaises(ValueError):self.e.payroll("E1","2026-10")
    def test_02_report_gross_net(self):
        r=self.e.payroll("E1","2026-10",3000)
        self.assertEqual((30000,3000,27000),(r["gross"],r["withheld"],r["net"]))
    def test_03_payroll_once(self):
        self.e.payroll("E1","2026-10",0)
        with self.assertRaises(ValueError):self.e.payroll("E1","2026-10",0)
    def test_04_insufficient_employer(self):
        e=EmploymentV21({"company":1});e.hire("E","w","company","S",30000)
        with self.assertRaises(ValueError):e.payroll("E","2026-10",100)

class Tests22Services(unittest.TestCase):
    def setUp(self):
        self.s=ServicesV22();self.s.provider("school","education",1,"registrar")
        self.s.request("R1","school","child",{"documents":"S_TEST"})
    def test_01_approval_capacity(self):
        self.assertEqual("accepted",self.s.decide("R1","registrar",True))
        self.assertEqual(0,self.s.providers["school"]["capacity"])
    def test_02_waitlist(self):
        self.s.request("R2","school","child2",{"documents":"S"})
        self.s.decide("R1","registrar",True)
        self.assertEqual("waitlisted",self.s.decide("R2","registrar",True))
    def test_03_no_authority(self):
        with self.assertRaises(ValueError):self.s.decide("R1","visitor",True)
    def test_04_unknown_eligibility(self):
        self.s.request("R2","school","child2",None)
        with self.assertRaises(ValueError):self.s.decide("R2","registrar",True)
    def test_05_unknown_capacity(self):
        self.s.provider("hospital","medical",None,"doctor")
        self.s.request("R3","hospital","patient",{"id":"S"})
        self.assertEqual("awaiting_capacity",self.s.decide("R3","doctor",True))

class Tests23Admin(unittest.TestCase):
    def setUp(self):
        self.a=AdministrationV23();self.a.office("O",["clerk"],"S_RULE","2026-10-01")
    def test_01_filing_not_approval(self):
        self.a.file("F","O","applicant",at(0),{"paper":"S"})
        self.assertEqual("submitted",self.a.dockets["F"]["status"])
    def test_02_permission(self):
        self.a.file("F","O","applicant",at(0),{"paper":"S"})
        with self.assertRaises(ValueError):self.a.decide("F","stranger",True,"x")
    def test_03_effective_date(self):
        self.a.office("NEW",["clerk"],"S_NEW","2026-10-10")
        with self.assertRaises(ValueError):self.a.file("F","NEW","applicant",at(0),{})
    def test_04_reasoned_denial(self):
        self.a.file("F","O","applicant",at(0),{"paper":"S"})
        self.assertEqual("denied",self.a.decide("F","clerk",False,"S evidence insufficient"))

class Tests24Information(unittest.TestCase):
    def setUp(self):
        self.n=InformationV24()
        self.n.send("M","p1","p2","rumor",at(0),20)
    def test_01_latency(self):
        with self.assertRaises(ValueError):self.n.deliver("M",at(10))
        self.n.deliver("M",at(20))
    def test_02_receiver_only(self):
        self.n.deliver("M",at(20))
        with self.assertRaises(ValueError):self.n.read("M","p3",at(21))
    def test_03_no_omniscience(self):
        self.n.deliver("M",at(20));self.n.read("M","p2",at(20))
        self.assertNotIn("p3",self.n.knowledge)
    def test_04_rumor_not_fact(self):
        self.n.deliver("M",at(20));self.n.read("M","p2",at(20))
        self.assertEqual("S_UNVERIFIED",self.n.knowledge["p2"][0]["grade"])
    def test_05_not_delivered_auto_read(self):
        with self.assertRaises(ValueError):self.n.read("M","p2",at(30))

class Tests25Macro(unittest.TestCase):
    def setUp(self):
        self.m=MacroeconomyV25()
        self.m.record("GDP","CN","GDP","2025-12-31",at(30),100,"S_UNIT","S_DATABASE")
    def test_01_publication_barrier(self):
        self.assertIsNone(self.m.as_known("GDP",at(0)))
        self.assertEqual(100,self.m.as_known("GDP",at(31))["value"])
    def test_02_no_spontaneous_cash(self):
        result=self.m.expose("GDP","person",10,0.2,at(31))
        self.assertEqual("S_HYPOTHETICAL_NOT_SETTLED",result["grade"])
        self.assertFalse(hasattr(self.m,"balances"))
    def test_03_unknown_exposure(self):
        with self.assertRaises(ValueError):self.m.expose("GDP","person",None,None,at(31))
    def test_04_future_data_not_available(self):
        with self.assertRaises(ValueError):self.m.expose("GDP","person",1,1,at(0))

class Tests26Integrated(unittest.TestCase):
    def test_01_formal_state_frozen(self):
        i=IntegrationV26(OFFICIAL)
        r=i.summary(OFFICIAL)
        self.assertEqual(0,r["official_game_events_written"])
    def test_02_reject_non_s_grade(self):
        i=IntegrationV26(OFFICIAL)
        with self.assertRaises(ValueError):i.record("E","public",{},grade="R_REAL_PERSONAL_EVENT")
    def test_03_duplicate_id(self):
        i=IntegrationV26(OFFICIAL);i.record("e1","transit",{})
        with self.assertRaises(ValueError):i.record("e1","transit",{})
    def test_04_frozen_bytes(self):
        i=IntegrationV26(OFFICIAL)
        with self.assertRaises(ValueError):i.summary(OFFICIAL+b"corruption")
    def test_05_deterministic_digest(self):
        a=IntegrationV26(OFFICIAL);b=IntegrationV26(OFFICIAL)
        for w in (a,b):w.record("a","source",{"x":1})
        self.assertEqual(a.summary(OFFICIAL)["digest"],b.summary(OFFICIAL)["digest"])

if __name__=="__main__":
    unittest.main(verbosity=2)
