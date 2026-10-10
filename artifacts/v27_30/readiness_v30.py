#!/usr/bin/env python3
"""v30 machine-readable evidence gate; determines if new automatic layers
would create unjustified facts. It never asserts all possible future work done.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
REQUIRED={
 "raw_baseline":"data/manifest.json",
 "v16_local_graph":"data/derived/manifest.json",
 "v17_26_osm_nodes":"data/derived/manifest_v17_26.json",
 "formal_frozen":"artifacts/v14/official_world_state_frozen_v13.json",
}
BLOCKERS=[
 {"id":"B01","scope":"v2-v12 exact transcripts","status":"NEEDS_USER_EXPORT",
  "reason":"Original older chat text was not fully archived; summaries cannot prove verbatim fidelity."},
 {"id":"B02","scope":"Beijing GTFS historical schedule","status":"NEEDS_AUTHORIZED_DATED_DATA",
  "reason":"40 OSM transit points do not contain trips, service calendars, fare or operational status."},
 {"id":"B03","scope":"OSM polygon multipolygon and public transport geometry coverage",
  "status":"TECHNICALLY_EXPANDABLE","reason":"v27 closed ways added, but relation polygons and all building entrances remain unresolved."},
 {"id":"B04","scope":"Turn restrictions and navigable routes",
  "status":"TECHNICALLY_EXPANDABLE","reason":"v28 supports simple node-via records only. Local laws, barriers and conditional restrictions not proven."},
 {"id":"B05","scope":"Actual 31 synthetic NPC private accounts and schedules",
  "status":"REQUIRES_EXPLICIT_SIMULATION_STATE","reason":"No player created, no invented private facts allowed; cannot infer from census."},
 {"id":"B06","scope":"2026-10-09 published macroeconomic vintages",
  "status":"NEEDS_HISTORICAL_RELEASE_SNAPSHOT","reason":"World Bank values may have been revised or released after baseline."},
 {"id":"B07","scope":"Real schools, health facilities, provider capacity, law decisions",
  "status":"NEEDS_EVIDENCE_PERMISSION_AND_ELIGIBILITY",
  "reason":"OSM geometry cannot prove facilities are operating or accessible."}
]
def checks(base=BASE):
    missing=[f"{name}: {path}" for name,path in REQUIRED.items() if not(base/path).is_file()]
    if missing:raise ValueError("missing ground truth: "+str(missing))
    original=(base/REQUIRED["formal_frozen"]).read_bytes()
    state=json.loads(original)
    if state["game_started"] is not False or state["player_character"] is not None or state["game_clock_time"] is not None or state["actual_game_events"]!=[]:
        raise ValueError("Official game violated frozen-world conditions")
    if len(state["people"])!=31:raise ValueError("NPC count changed")
    raw=json.loads((base/REQUIRED["raw_baseline"]).read_text())
    ids={d["id"] for d in raw["datasets"]}
    if "beijing_osm_2026_10_01" not in ids:raise ValueError("missing OSM source")
    source=next(d for d in raw["datasets"] if d["id"]=="beijing_osm_2026_10_01")
    for x in ["manifest.json","manifest_v17_26.json"]:
        name=(base/"data/derived"/x)
        derived=json.loads(name.read_text())
        if derived["source"]["sha256"]!=source["sha256"]:
            raise ValueError("OSM data source lineage mismatch")
    return {"frozen_state_sha256":hashlib.sha256(original).hexdigest(),
            "blocked_new_R_personal_histories":True,
            "game_events_written":0,
            "blockers":BLOCKERS,
            "technical_scope_complete":False,
            "automatic_iteration_status":"STOP_WHEN_REMAINING_REQUESTED_WORK_REQUIRES_NEW_SOURCE_OR_AUTHORIZATION",
            "claims":"Not a complete Earth digital twin; partial reproducible sandbox"}
def main():
    report=checks()
    p=Path(__file__).resolve().parent/"readiness_report.json"
    p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"blockers":len(report["blockers"]),
                      "technical_scope_complete":False,
                      "official_game_events":report["game_events_written"]},ensure_ascii=False))
if __name__=="__main__":main()
