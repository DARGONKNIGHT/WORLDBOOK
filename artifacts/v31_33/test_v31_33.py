#!/usr/bin/env python3
"""v31-v33 source-tagged public areas, barriers and closed-game checks."""
import unittest,json
from pathlib import Path
from areas_v31 import permitted,representation
from barriers_v32 import access,candidate_route
class PublicAreas(unittest.TestCase):
    def test_allow_school(self):
        self.assertEqual("amenity:school",permitted({"amenity":"school"}))
    def test_exclude_private_residential(self):
        self.assertIsNone(permitted({"building":"residential"}))
    def test_representation_bbox(self):
        arr=[[(40.188,116.707),(40.188,116.708),(40.189,116.708),(40.188,116.707)]]
        x=representation("43","amenity:school",arr,"S_PLACE")
        self.assertEqual([40.188,116.707,40.189,116.708],x["bbox"])
        self.assertEqual("OUTER_VERTICES_ARITHMETIC_MEAN_NOT_CENTROID_ENTRANCE",
                         x["representative_grade"])
    def test_outside_skipped(self):
        self.assertIsNone(representation("2","amenity:school",[[(0,0),(1,1),(0,0),(1,1)]],None))
    def test_no_automatic_hours(self):
        x=representation("43","amenity:school",[[(40.188,116.707),(40.188,116.708),(40.189,116.708),(40.188,116.707)]],None)
        self.assertEqual("U",x["operating_status"])
class RoadBarriers(unittest.TestCase):
    def setUp(self):
        self.g={"nodes":{"1":[0,0],"2":[0,1],"3":[0,2]},
                "edges":[["1","2","drive",1,"W1","residential"],
                         ["2","3","drive",1,"W2","residential"],
                         ["1","2","walk",1,"W1","residential"],
                         ["2","3","walk",1,"W2","residential"]]}
    def test_bollard_no_automatic_car_clearance(self):
        self.assertEqual("U_BARRIER_PASSABILITY",access({"barrier":"bollard"},"drive"))
        self.assertEqual("WALK_IMPLIED_PASSABLE_UNVERIFIED",access({"barrier":"bollard"},"walk"))
    def test_private_gate_rejected(self):
        self.assertEqual("EXPLICITLY_RESTRICTED",access({"barrier":"gate","access":"private"},"drive"))
    def test_vehicle_synthetic_path_blocked(self):
        b={"2":{"walk":"WALK_IMPLIED_PASSABLE_UNVERIFIED","drive":"U_BARRIER_PASSABILITY"}}
        self.assertIsNone(candidate_route(self.g,"1","3","drive",b))
        self.assertEqual(2.0,candidate_route(self.g,"1","3","walk",b)["distance_m"])
    def test_unknown_gate_not_falsely_passable(self):
        self.assertEqual("U_BARRIER_PASSABILITY",access({"barrier":"gate"},"walk"))
    def test_open_entrance_differs_from_gate(self):
        self.assertEqual("OPEN_ENTRANCE_TAGGED",access({"barrier":"entrance"},"walk"))
    def test_no_source_node_not_applied(self):
        self.assertEqual(2.0,candidate_route(self.g,"1","3","drive",{})["distance_m"])
class ReleaseGate(unittest.TestCase):
    def test_frozen_report_when_generated(self):
        # The full integration report is created by GitHub Actions after real OSM.
        from closure_v33 import REQUIRED
        self.assertIn("artifacts/v14/official_world_state_frozen_v13.json",REQUIRED)
    def test_no_claim_full_world(self):
        from closure_v33 import readiness
        # This is only called after CI has populated the two real raw-source derivatives.
        x=readiness()
        self.assertFalse(x["official_history_written"])
        self.assertTrue(x["still_technically_expandable"])
if __name__=="__main__":unittest.main(verbosity=2)
