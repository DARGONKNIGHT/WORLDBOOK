#!/usr/bin/env python3
"""v27-v30 geometry / turn / calendar / evidence guards (S fixtures only)."""
import sys,unittest,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
from ways_v27 import category,summarize_way
from turns_v28 import normalized_relation,turn_allowed,route_turn_aware
from calendar_v29 import CalendarV29,gtfs_seconds
from readiness_v30 import checks
class WaysTests(unittest.TestCase):
    def test_public_school_allowed(self):
        self.assertEqual("amenity:school",category({"amenity":"school"}))
    def test_private_house_excluded(self):
        self.assertIsNone(category({"building":"residential","addr:housenumber":"123"}))
    def test_mean_not_entrance(self):
        coords=[(40.188,116.707),(40.189,116.707),(40.189,116.708),(40.188,116.707)]
        x=summarize_way(1,coords,{"amenity":"school"})
        self.assertEqual("VERTEX_MEAN_NOT_ENTRANCE_OR_TRUE_CENTROID",x["geometry_quality"])
    def test_outside_excluded(self):
        self.assertIsNone(summarize_way(1,[(0,0),(0.1,0.1)],{"amenity":"school"}))
    def test_linear_feature(self):
        x=summarize_way(3,[(40.188,116.707),(40.189,116.707)],{"railway":"station"})
        self.assertEqual("linear_way",x["geometry_type"])
class TurnsTests(unittest.TestCase):
    def fixture(self):
        return {"nodes":{"1":[0,0],"2":[0,1],"3":[0,2],"4":[1,1]},
                "edges":[["1","2","drive",1,"A","residential"],
                         ["2","3","drive",1,"B","residential"],
                         ["2","4","drive",2,"C","residential"],
                         ["4","3","drive",2,"D","residential"]]}
    def test_node_relation(self):
        rel,err=normalized_relation("1",{"type":"restriction","restriction":"no_left_turn"},
          [("w",1,"from"),("n",2,"via"),("w",2,"to")],{"1","2","3"})
        self.assertIsNone(err);self.assertEqual("2",rel["via_node"])
    def test_via_way_unsupported(self):
        rel,err=normalized_relation("1",{"type":"restriction","restriction":"no_left_turn"},
          [("w",1,"from"),("w",2,"via"),("w",3,"to")],{"1","2","3"})
        self.assertIsNone(rel);self.assertEqual("via_way_or_invalid_member",err)
    def test_restriction_conditional_excluded(self):
        rel,err=normalized_relation("1",{"type":"restriction","restriction":"no_left_turn",
          "restriction:conditional":"yes @ Mo-Fr"},[("w",1,"from"),("n",2,"via"),("w",3,"to")],{"2"})
        self.assertIsNone(rel)
    def test_only_turn_allows_one(self):
        rules=[{"from_way":"A","via_node":"2","to_way":"B","restriction":"only_right_turn"}]
        self.assertTrue(turn_allowed("A","2","B",rules))
        self.assertFalse(turn_allowed("A","2","C",rules))
    def test_no_turn_detours(self):
        g=self.fixture();rules=[{"from_way":"A","via_node":"2","to_way":"B","restriction":"no_left_turn"}]
        a=route_turn_aware(g,1,3,rules)
        self.assertEqual(["1","2","4","3"],a["node_ids"])
    def test_no_route_not_teleport(self):
        self.assertIsNone(route_turn_aware(self.fixture(),3,1,[]))
class CalendarTests(unittest.TestCase):
    def setUp(self):
        self.c=CalendarV29()
        self.c.add_service("S_WEEKDAY","2026-10-01","2026-10-31",list(range(5)))
    def test_25_hour_after_midnight(self):
        self.assertEqual(25*3600+10*60,gtfs_seconds("25:10:00"))
    def test_bad_minutes(self):
        with self.assertRaises(ValueError):gtfs_seconds("24:99:00")
    def test_weekend_cancelled(self):
        self.assertFalse(self.c.service_active("S_WEEKDAY","2026-10-10"))
    def test_calendar_exception_add(self):
        self.c.exception("S_WEEKDAY","2026-10-10","add")
        self.assertTrue(self.c.service_active("S_WEEKDAY","2026-10-10"))
    def test_unknown_is_not_no_service(self):
        self.assertIsNone(self.c.service_active("MISSING","2026-10-09"))
    def test_gtfs_day_roundtrip(self):
        self.c.exception("S_WEEKDAY","2026-10-10","add")
        x=self.c.departure("S_WEEKDAY","2026-10-10","25:10:00")
        self.assertEqual("2026-10-11T01:10:00+08:00",x["local_departure"])
    def test_real_schedule_needs_source(self):
        with self.assertRaises(ValueError):
            self.c.add_service("fake_real","2026-10-01","2026-10-10",[0],"R_VERIFIED_SCHEDULE")
    def test_exception_only_feed(self):
        self.c.exception("NO_WEEKLY_CALENDAR","2026-10-10","add")
        result=self.c.departure("NO_WEEKLY_CALENDAR","2026-10-10","09:15:00")
        self.assertEqual("S_FIXTURE_EXCEPTION_ONLY",result["grade"])
class ReadinessTests(unittest.TestCase):
    def test_frozen_world(self):
        d=checks()
        self.assertEqual(0,d["game_events_written"])
        self.assertEqual(64,len(d["frozen_state_sha256"]))
    def test_incomplete_real_inputs(self):
        d=checks();self.assertGreaterEqual(len(d["blockers"]),5)
        self.assertFalse(d["technical_scope_complete"])
    def test_no_pretend_full_twin(self):
        d=checks();self.assertIn("partial",d["claims"].lower())
if __name__=="__main__":unittest.main(verbosity=2)
