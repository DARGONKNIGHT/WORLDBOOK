#!/usr/bin/env python3
"""v33 release/readiness report for finite evidence-based worldbook milestone.

Source-gated stop does NOT mean that no engineering or facts can ever be added.
It means *this automatic batch* cannot responsibly complete real historical
GTFS, resident info, administrative decisions or old transcript recovery.
"""
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
REQUIRED=[
 "data/manifest.json","data/derived/manifest.json",
 "data/derived/manifest_v17_26.json","data/derived/manifest_v27_30.json",
 "artifacts/v27_30/osm_public_way_features.json",
 "artifacts/v27_30/turn_restrictions_local.json",
 "artifacts/v31_33/osm_public_multipolygons.json",
 "artifacts/v31_33/osm_barrier_nodes.json",
 "artifacts/v14/official_world_state_frozen_v13.json"
]
def verify_bytes(path,sha,size):
    p=BASE/path
    if not p.is_file() or p.stat().st_size!=size:
        raise ValueError("missing/size mismatch: "+path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
        raise ValueError("SHA256 mismatch: "+path)
def readiness():
    missing=[x for x in REQUIRED if not(BASE/x).is_file()]
    if missing:raise ValueError("missing canonical evidence: "+str(missing))
    raw=json.loads((BASE/"data/manifest.json").read_text())
    osm=next(x for x in raw["datasets"] if x["id"]=="beijing_osm_2026_10_01")
    verify_bytes(osm["dest"],osm["sha256"],osm["bytes"])
    prior=json.loads((BASE/"data/derived/manifest_v27_30.json").read_text())
    if prior["source_sha256"]!=osm["sha256"]:raise ValueError("bad prior provenance")
    reports={
       "multipolygons":json.loads((OUT/"area_report.json").read_text()),
       "barriers":json.loads((OUT/"barrier_report.json").read_text())
    }
    for r in reports.values():
        if r["source_sha256"]!=osm["sha256"]:raise ValueError("different source date")
        verify_bytes(r["output"],r["sha256"],r["bytes"])
    official=(BASE/"artifacts/v14/official_world_state_frozen_v13.json").read_bytes()
    state=json.loads(official)
    if state["player_character"] is not None or state["game_started"] or state["actual_game_events"] or state["game_clock_time"] is not None:
        raise ValueError("official state unexpectedly advanced")
    if len(state["people"])!=31:raise ValueError("NPC count mismatch")
    return {"status":"SOURCE_GATED_MILESTONE_V33_NOT_COMPLETE_EARTH",
       "source_osm_sha256":osm["sha256"],
       "official_frozen_sha256":hashlib.sha256(official).hexdigest(),
       "official_history_written":0,
       "multipolygon_relation_count":reports["multipolygons"]["count"],
       "barrier_graph_node_count":reports["barriers"]["on_local_road_graph"],
       "open_dependency_ids":["B01","B02","B03","B04","B05","B06","B07"],
       "still_technically_expandable":True,
       "human_data_source_needed":True,
       "next_layer_requires_new_ground_truth_or_distinct_engineering_scope":True,
       "statement":"Pause unbounded auto-expansion at an honest data/verification gate; not proof no further possible layer."}
def main():
    data=readiness()
    file=OUT/"milestone_v33.json"
    file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
