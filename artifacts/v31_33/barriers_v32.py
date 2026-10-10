#!/usr/bin/env python3
"""v32 extract tagged barrier nodes intersecting v16 local street graph.

Gate and bollard accessibility depends on mode, legal access, opening state.
Conservative candidate routing excludes unknown/restricted barrier nodes;
a dropped route is uncertainty, not proven impossible real-world travel.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import osmium
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
VEHICLE_OBSTACLES={"bollard","block","cycle_barrier","stile","kissing_gate",
                   "turnstile","fence","wall","chain","bar","swing_gate","lift_gate","gate"}
FOOT_OBSTACLES={"wall","fence","block","turnstile","stile","kissing_gate","gate",
                "swing_gate","lift_gate"}
def access(tags,mode):
    b=tags.get("barrier")
    if not b:return "NO_BARRIER_TAG"
    keys=("access","foot") if mode=="walk" else ("access","vehicle","motor_vehicle","motorcar")
    v={k:tags[k] for k in keys if k in tags}
    if any(x in ("private","no") for x in v.values()):return "EXPLICITLY_RESTRICTED"
    # If no explicit denial but one explicit allowance, still may need permit. Tag semantics simplified.
    if "yes" in v.values() or "designated" in v.values():
        return "TAGGED_ALLOWANCE_NOT_LEGAL_VERIFICATION"
    if b=="entrance":return "OPEN_ENTRANCE_TAGGED"
    if (mode=="walk" and b=="bollard"):return "WALK_IMPLIED_PASSABLE_UNVERIFIED"
    if b in (FOOT_OBSTACLES if mode=="walk" else VEHICLE_OBSTACLES):
        return "U_BARRIER_PASSABILITY"
    return "U_UNCLASSIFIED_BARRIER"
class BarrierNodes(osmium.SimpleHandler):
    def __init__(self,graph):
        super().__init__();self.graph_nodes=set(graph["nodes"]);self.records={}
        self.total_tagged=0
    def node(self,n):
        if not n.tags.get("barrier"):return
        self.total_tagged+=1
        key=str(n.id)
        if key not in self.graph_nodes:return
        t={str(x.k):str(x.v) for x in n.tags}
        self.records[key]={"osm_node":key,"barrier":t["barrier"],
              "access_tags":{k:v for k,v in t.items() if k in
                       ("access","foot","vehicle","motor_vehicle","motorcar")},
              "walk":access(t,"walk"),"drive":access(t,"drive"),
              "status":"R_OSM_TAGGED_NOT_REAL_OPEN_STATUS"}
def candidate_route(graph,source,target,mode,barriers):
    """A conservative distance-only shortest path excluding uncertain gates."""
    import heapq
    source,target=str(source),str(target)
    if source not in graph["nodes"] or target not in graph["nodes"]:
        raise KeyError("source/target node not in graph")
    blocked={id for id,item in barriers.items() if item[mode] in
             ("EXPLICITLY_RESTRICTED","U_BARRIER_PASSABILITY","U_UNCLASSIFIED_BARRIER")}
    if source in blocked or target in blocked:return None
    adj={}
    for a,b,m,w,way,highway in graph["edges"]:
        if m==mode and a not in blocked and b not in blocked:
            adj.setdefault(a,[]).append((b,float(w)))
    best={source:0.0};q=[(0.0,source)]
    while q:
        d,n=heapq.heappop(q)
        if d>best.get(n,float("inf"))+1e-9:continue
        if n==target:
            return {"status":"CANDIDATE_NOT_NAVIGATION","distance_m":round(d,2),
                    "potential_barrier_nodes_excluded":len(blocked)}
        for nxt,cost in adj.get(n,[]):
            nd=d+cost
            if nd<best.get(nxt,float("inf"))-1e-9:
                best[nxt]=nd;heapq.heappush(q,(nd,nxt))
    return None
def main():
    src=json.loads((ROOT/"data/manifest.json").read_text())
    info=next(x for x in src["datasets"] if x["id"]=="beijing_osm_2026_10_01")
    p=ROOT/info["dest"];sha=hashlib.sha256(p.read_bytes()).hexdigest()
    if sha!=info["sha256"]:raise ValueError("OSM mismatch")
    graph=json.loads((ROOT/"artifacts/v16/osm_graph_sample.json").read_text())
    if graph["source"]["sha256"]!=sha:raise ValueError("graph source mismatch")
    h=BarrierNodes(graph);h.apply_file(str(p))
    records={k:h.records[k] for k in sorted(h.records,key=int)}
    out=BASE/"osm_barrier_nodes.json"
    data={"schema":32,"snapshot":"2026-10-01","source_sha256":sha,
        "source_graph":"artifacts/v16/osm_graph_sample.json",
        "source_graph_sha256":hashlib.sha256((ROOT/"artifacts/v16/osm_graph_sample.json").read_bytes()).hexdigest(),
        "barriers":records,"legal_navigation_authorized":False,
        "license":"© OpenStreetMap contributors, ODbL 1.0"}
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report={"tagged_barrier_nodes_in_city_pbf":h.total_tagged,
         "on_local_road_graph":len(records),
         "uncertain_drive":sum(i["drive"].startswith("U_") for i in records.values()),
         "uncertain_walk":sum(i["walk"].startswith("U_") for i in records.values()),
         "bytes":out.stat().st_size,"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
         "source_sha256":sha,"output":out.relative_to(ROOT).as_posix(),
         "all_barriers_or_navigation_verified":False}
    (BASE/"barrier_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
