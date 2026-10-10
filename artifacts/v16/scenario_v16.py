#!/usr/bin/env python3
"""v16 road-constrained travel test; a selected OSM edge, not a real person's trip."""
from __future__ import annotations
import hashlib,json,math,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from network_v16 import demo_pair,load_graph,shortest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"v14"))
from engine_v14 import SandboxEngine
BASE=Path(__file__).resolve().parent
FROZEN=BASE.parent/"v14"/"official_world_state_frozen_v13.json"
ANCHOR=datetime(2026,10,9,9,0,tzinfo=timezone(timedelta(hours=8)))

def sandbox_run(graph=None):
    if graph is None:graph=load_graph(BASE/"osm_graph_sample.json")
    route=demo_pair(graph,"drive")
    if not route or route["distance_m"]<=0:raise RuntimeError("No OSM drive route")
    origin="osm_node:"+route["origin_node"]
    destination="osm_node:"+route["destination_node"]
    # The geometric path is sourced in OSM. Both speed and extra time are explicitly S.
    minutes=max(2,math.ceil(route["illustrative_minutes"])+2)
    engine=SandboxEngine(ANCHOR,["P014"],{},{"P014":origin})
    engine.schedule("v16-route-travel",ANCHOR,"travel","P014",
                    origin=origin,destination=destination,minutes=minutes)
    engine.schedule("v16-premature-arrival-activity",ANCHOR+timedelta(minutes=1),
                    "activity","P014",minutes=1,location=destination)
    engine.schedule("v16-post-arrival-activity",ANCHOR+timedelta(minutes=minutes+1),
                    "activity","P014",minutes=5,location=destination)
    engine.run(ANCHOR+timedelta(minutes=minutes+7))
    assert not engine.audit(),engine.audit()
    status={e["event_id"]:e["status"] for e in engine.journal}
    assert status["v16-route-travel"]=="completed"
    assert status["v16-premature-arrival-activity"]=="rejected"
    assert status["v16-route-travel:arrive"]=="completed"
    assert status["v16-post-arrival-activity"]=="completed"
    return {"route":route,"assumed_travel_minutes":minutes,
            "arrival_time":(ANCHOR+timedelta(minutes=minutes)).isoformat(),
            "journal":engine.journal,"final_state":engine.state,
            "status":status,"audit":engine.audit()}

def generate():
    original=FROZEN.read_bytes()
    before=json.loads(original)
    assert before["game_started"] is False
    assert before["game_clock_time"] is None and before["player_character"] is None
    assert before["actual_game_events"]==[]
    result=sandbox_run()
    assert FROZEN.read_bytes()==original
    report={
      "test_only":True,"model":"v16",
      "source":"verified graph extracted from Beijing OSM 2026-10-01",
      "road_geometry_reality_grade":"R_OSM_DERIVED_WITH_UNKNOWN_COMPLETENESS",
      "travel_duration_grade":"S_UNCALIBRATED",
      "graph_sha256":hashlib.sha256((BASE/"osm_graph_sample.json").read_bytes()).hexdigest(),
      "route":result["route"],"assumed_travel_minutes":result["assumed_travel_minutes"],
      "sandbox_arrival":result["arrival_time"],
      "event_statuses":result["status"],
      "audit_violations":result["audit"],
      "official_world_sha256":hashlib.sha256(original).hexdigest(),
      "official_game_events_written":0,
      "caveats":"single OSM segment in an illustrative sandbox; no real NPC home, employment, traffic or turn rules"
    }
    (BASE/"route_sandbox_journal.json").write_text(
        json.dumps(result["journal"],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (BASE/"route_sandbox_report.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report
if __name__=="__main__":generate()
