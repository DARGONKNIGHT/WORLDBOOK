#!/usr/bin/env python3
"""v28 OSM node-via restrictions and turn-aware graph search.

ONLY straightforward single from-way/via-node/to-way relations, no exceptions
or conditional restriction; do NOT use as legal navigation. Via-way, mode
exceptions, barrier restrictions, and incomplete relations are documented.
"""
from __future__ import annotations
import hashlib,heapq,json
from pathlib import Path
import osmium

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
SOURCE_SHA="945a6b7967c10dbd40a6e5c59bcae771a9dd44112ee4e37e868e5c544b34762d"
TYPES={"no_left_turn","no_right_turn","no_straight_on","no_u_turn",
       "only_left_turn","only_right_turn","only_straight_on","only_u_turn"}
def normalized_relation(relation_id,tags,members,graph_nodes):
    if tags.get("type")!="restriction":return None,"not_restriction"
    if tags.get("restriction") not in TYPES:return None,"unknown_type"
    if "except" in tags or any(k.endswith(":conditional") or k.startswith("restriction:") for k in tags):
        return None,"exception_or_conditional_unsupported"
    byrole={"from":[],"via":[],"to":[]}
    for kind,ref,role in members:
        if role in byrole:byrole[role].append((kind,str(ref)))
    if len(byrole["from"])!=1 or len(byrole["via"])!=1 or len(byrole["to"])!=1:
        return None,"multi_member_unsupported"
    a,v,b=byrole["from"][0],byrole["via"][0],byrole["to"][0]
    if a[0]!="w" or v[0]!="n" or b[0]!="w":
        return None,"via_way_or_invalid_member"
    if v[1] not in graph_nodes:return None,"outside_local_graph"
    return {"relation_id":str(relation_id),"from_way":a[1],"via_node":v[1],
            "to_way":b[1],"restriction":tags["restriction"],
            "grade":"R_OSM_RELATION_NOT_LEGAL_VERIFICATION"},None
class Relations(osmium.SimpleHandler):
    def __init__(self,graph_nodes):
        super().__init__();self.nodes=graph_nodes;self.rows={};self.counts={}
    def relation(self,rel):
        if rel.tags.get("type")!="restriction":return
        t={str(x.k):str(x.v) for x in rel.tags}
        members=[(str(m.type),str(m.ref),str(m.role)) for m in rel.members]
        row,why=normalized_relation(rel.id,t,members,self.nodes)
        if row:self.rows[row["relation_id"]]=row
        else:self.counts[why]=self.counts.get(why,0)+1
def turn_allowed(previous_way,via,next_way,rules):
    if previous_way is None:return True
    for rule in rules:
        if rule["via_node"]!=str(via) or rule["from_way"]!=str(previous_way):
            continue
        only=rule["restriction"].startswith("only_")
        if only and rule["to_way"]!=str(next_way):return False
        if not only and rule["to_way"]==str(next_way):return False
    return True
def route_turn_aware(graph,origin,destination,restrictions):
    nodes=graph["nodes"];origin=str(origin);destination=str(destination)
    if origin not in nodes or destination not in nodes:raise KeyError("unknown OSM node")
    if origin==destination:return {"distance_m":0.0,"node_ids":[origin],"way_ids":[]}
    adjacency={}
    for a,b,mode,dist,way,hw in graph["edges"]:
        if mode=="drive":adjacency.setdefault(str(a),[]).append((str(b),float(dist),str(way)))
    for entries in adjacency.values():entries.sort()
    initial=(origin,None);best={initial:0.0};prev={};queue=[(0.0,origin,"")]
    terminal=None
    while queue:
        d,node,way=heapq.heappop(queue)
        state=(node,way or None)
        if d>best.get(state,float("inf"))+1e-9:continue
        if node==destination:terminal=state;break
        for nxt,cost,nway in adjacency.get(node,[]):
            if not turn_allowed(state[1],node,nway,restrictions):continue
            key=(nxt,nway);cand=d+cost
            if cand<best.get(key,float("inf"))-1e-9:
                best[key]=cand;prev[key]=state;heapq.heappush(queue,(cand,nxt,nway))
    if terminal is None:return None
    states=[terminal]
    while states[-1]!=initial:states.append(prev[states[-1]])
    states.reverse()
    return {"distance_m":round(best[terminal],2),
            "node_ids":[s[0] for s in states],
            "way_ids":[s[1] for s in states[1:]],
            "status":"UNVERIFIED_CANDIDATE_ONLY",
            "excluded":["via-way restrictions","except tag","conditional rules",
                        "implicit local laws","barrier nodes","live traffic","real ETA"]}
def main():
    manifest=json.loads((ROOT/"data/manifest.json").read_text())
    src=next(d for d in manifest["datasets"] if d["id"]=="beijing_osm_2026_10_01")
    f=ROOT/src["dest"];sha=hashlib.sha256(f.read_bytes()).hexdigest()
    if sha!=src["sha256"] or sha!=SOURCE_SHA:raise ValueError("OSM source mismatch")
    graph=json.loads((ROOT/"artifacts/v16/osm_graph_sample.json").read_text())
    if graph["source"]["sha256"]!=sha:raise ValueError("graph source mismatch")
    obj=Relations(set(graph["nodes"]))
    obj.apply_file(str(f),locations=False)
    records=[obj.rows[k] for k in sorted(obj.rows,key=int)]
    data={"schema":28,"source_sha256":sha,"road_graph_sha256":hashlib.sha256(
       (ROOT/"artifacts/v16/osm_graph_sample.json").read_bytes()).hexdigest(),
      "snapshot":"2026-10-01","subset":"OSM node-via restrictions only",
      "restrictions":records,"excluded_reason_counts":obj.counts,
      "legal_navigation_authorized":False,
      "attribution":"© OpenStreetMap contributors; ODbL 1.0"}
    out=BASE/"turn_restrictions_local.json"
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    audit={"total_supported_relation_records":len(records),
           "source_sha256":sha,"counts_excluded":obj.counts,
           "bytes":out.stat().st_size,"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
           "graph_road_segments_complete":False,
           "real_navigation_safe":False}
    (BASE/"turn_restrictions_report.json").write_text(
        json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(audit,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
