#!/usr/bin/env python3
"""v16 unit and actual OSM-derived graph integration checks."""
from __future__ import annotations
import hashlib,json,sys,unittest
from datetime import timedelta
from pathlib import Path
from network_v16 import permitted,directions,haversine,shortest,nearest_node,validate_graph,load_graph,demo_pair
from scenario_v16 import sandbox_run,BASE,FROZEN,ANCHOR
class RoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=FROZEN.read_bytes()
        cls.graph=load_graph(BASE/"osm_graph_sample.json")
    @classmethod
    def tearDownClass(cls):
        assert FROZEN.read_bytes()==cls.original
    def fixture(self):
        return {"schema_version":16,
                "source":{"sha256":"synthetic_SHA_01","game_cutoff":"2026-10-09"},
                "anchor":{"grade":"S_APPROX_FALLBACK"},
                "nodes":{"1":[40.0,116.0],"2":[40.0,116.001],
                         "3":[40.0,116.002],"4":[40.01,116.01]},
                "edges":[["1","2","drive",85,"way1","residential"],
                         ["2","3","drive",85,"way2","residential"],
                         ["1","2","walk",85,"way1","residential"],
                         ["2","1","walk",85,"way1","residential"],
                         ["2","3","walk",85,"way2","residential"],
                         ["3","2","walk",85,"way2","residential"]]}

    def test_01_real_checksum_reference(self):
        self.assertEqual("945a6b7967c10dbd40a6e5c59bcae771a9dd44112ee4e37e868e5c544b34762d",
                         self.graph["source"]["sha256"])
    def test_02_real_graph_nonempty(self):
        d=validate_graph(self.graph)
        self.assertGreater(d["nodes"],20)
        self.assertGreater(d["walk_edges"],0)
        self.assertGreater(d["drive_edges"],0)
    def test_03_walk_route_from_actual_data(self):
        r=demo_pair(self.graph,"walk")
        self.assertIsNotNone(r)
        self.assertGreater(r["distance_m"],0)
        self.assertEqual("S_UNCALIBRATED",r["travel_time_grade"])
    def test_04_drive_route_from_actual_data(self):
        r=demo_pair(self.graph,"drive")
        self.assertIsNotNone(r)
        self.assertEqual("R_DERIVED_FROM_OSM_GEOMETRY",r["distance_grade"])
    def test_05_private_way_denied(self):
        self.assertFalse(permitted({"highway":"residential","access":"private"},"drive"))
        self.assertFalse(permitted({"highway":"service","access":"private"},"walk"))
    def test_06_explicit_walk_exception(self):
        self.assertTrue(permitted({"highway":"service","access":"no","foot":"yes"},"walk"))
    def test_07_motor_on_footway_denied(self):
        self.assertFalse(permitted({"highway":"footway","access":"yes"},"drive"))
        self.assertTrue(permitted({"highway":"footway"},"walk"))
    def test_08_unknown_conditional_denied(self):
        self.assertFalse(permitted({"highway":"residential","access:conditional":"no @ (Mo-Fr)"},"drive"))
    def test_09_drive_oneway(self):
        self.assertEqual((1,),directions({"highway":"residential","oneway":"yes"},"drive"))
        self.assertEqual((-1,),directions({"highway":"residential","oneway":"-1"},"drive"))
        self.assertEqual((1,-1),directions({"highway":"residential","oneway":"no"},"drive"))
    def test_10_pedestrian_not_generic_vehicle_oneway(self):
        self.assertEqual((1,-1),directions({"highway":"residential","oneway":"yes"},"walk"))
        self.assertEqual((1,),directions({"highway":"footway","oneway:foot":"yes"},"walk"))
    def test_11_real_dijkstra_respects_direction(self):
        g=self.fixture()
        self.assertEqual(170,shortest(g,"1","3","drive")["distance_m"])
        self.assertIsNone(shortest(g,"3","1","drive"))
        self.assertEqual(170,shortest(g,"3","1","walk")["distance_m"])
    def test_12_no_teleport_disconnected(self):
        self.assertIsNone(shortest(self.fixture(),"1","4","walk"))
    def test_13_nearest_snap_bound(self):
        g=self.fixture()
        self.assertIsNone(nearest_node(g,0,0,max_distance_m=150))
        self.assertEqual("1",nearest_node(g,40.0,116.0,max_distance_m=150)["node"])
    def test_14_positive_distance(self):
        self.assertGreater(haversine(40,116,40.0001,116),10)
    def test_15_real_transport_integration(self):
        result=sandbox_run(self.graph)
        self.assertEqual("completed",result["status"]["v16-route-travel"])
        self.assertEqual("rejected",result["status"]["v16-premature-arrival-activity"])
        self.assertEqual("completed",result["status"]["v16-post-arrival-activity"])
        self.assertEqual([],result["audit"])
    def test_16_game_world_frozen(self):
        self.assertEqual(self.original,FROZEN.read_bytes())
        obj=json.loads(self.original)
        self.assertIsNone(obj["player_character"])
        self.assertIsNone(obj["game_clock_time"])
        self.assertEqual([],obj["actual_game_events"])
    def test_17_no_real_travel_eta(self):
        r=demo_pair(self.graph,"drive")
        self.assertIn("traffic",r["excluded"])
        self.assertEqual("S_UNCALIBRATED",r["travel_time_grade"])
    def test_18_osm_anchor_distinct_from_player(self):
        self.assertNotIn("player_home",self.graph)
        self.assertIn(self.graph["anchor"]["grade"],("R_OSM_PLACE_NODE","S_APPROX_FALLBACK"))
if __name__=="__main__":unittest.main(verbosity=2)
