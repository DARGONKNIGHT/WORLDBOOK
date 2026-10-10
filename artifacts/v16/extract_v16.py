#!/usr/bin/env python3
"""Extract a small, actual OSM road topology from a verified Beijing PBF.

Requires pyosmium only at ingestion time: pip install osmium==4.3.1.
Reads source bytes from GitHub's own data/raw, checks manifest SHA256,
and does not infer a real NPC's home/work location.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
import sys
import osmium
from network_v16 import haversine,permitted,directions,validate_graph,demo_pair
ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
MANIFEST=ROOT/"data/manifest.json"
ANCHORS=("前礼务村","前礼务","北小营镇","北小营","顺义","北京")
RADIUS_M=2800

class FindAnchors(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.found=[]
    def node(self,n):
        tag=n.tags.get("name","")
        names=(tag,n.tags.get("name:zh",""),n.tags.get("official_name",""))
        if not any(a in names for a in ANCHORS):return
        if n.tags.get("place") not in ("village","hamlet","town","suburb","city",
                                     "neighbourhood","quarter","locality"):return
        if not n.location.valid():return
        label=next((a for a in ANCHORS if a in names),None)
        if label is not None:
            self.found.append({"target":label,"osm_node":str(n.id),
                               "name":tag,"lat":round(n.location.lat,7),
                               "lon":round(n.location.lon,7)})

class ExtractRoads(osmium.SimpleHandler):
    def __init__(self,lat,lon):
        super().__init__()
        self.lat=lat;self.lon=lon
        self.nodes={}
        self.edges=[]
        self.ways_seen=0
        self.excluded_border_segments=0
    def way(self,w):
        hw=w.tags.get("highway")
        if not hw or len(w.nodes)<2:return
        tags={str(t.k):str(t.v) for t in w.tags}
        modes=[m for m in ("walk","drive") if permitted(tags,m)]
        if not modes:return
        self.ways_seen+=1
        nodes=list(w.nodes)
        for a,b in zip(nodes,nodes[1:]):
            if not a.location.valid() or not b.location.valid():continue
            a_lat,a_lon=float(a.location.lat),float(a.location.lon)
            b_lat,b_lon=float(b.location.lat),float(b.location.lon)
            if max(haversine(self.lat,self.lon,a_lat,a_lon),
                   haversine(self.lat,self.lon,b_lat,b_lon))>RADIUS_M:
                self.excluded_border_segments+=1
                continue
            dist=round(haversine(a_lat,a_lon,b_lat,b_lon),2)
            if dist<0.01:continue
            self.nodes[str(a.ref)]=[round(a_lat,7),round(a_lon,7)]
            self.nodes[str(b.ref)]=[round(b_lat,7),round(b_lon,7)]
            for m in modes:
                for direction in directions(tags,m):
                    src,dst=(str(a.ref),str(b.ref)) if direction==1 else (str(b.ref),str(a.ref))
                    self.edges.append([src,dst,m,dist,str(w.id),hw])

def main():
    state=json.loads(MANIFEST.read_text(encoding="utf-8"))
    row=next(x for x in state["datasets"] if x["id"]=="beijing_osm_2026_10_01")
    p=ROOT/row["dest"]
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    if sha!=row["sha256"] or p.stat().st_size!=row["bytes"]:
        raise ValueError("OSM bytes invalid against GitHub manifest")
    names=FindAnchors()
    names.apply_file(str(p),locations=False)
    anchors=sorted(names.found,key=lambda x:(ANCHORS.index(x["target"]),int(x["osm_node"])))
    if anchors:
        a=anchors[0]
        anchor={"name":a["name"],"target":a["target"],"lat":a["lat"],"lon":a["lon"],
                "osm_node":a["osm_node"],"grade":"R_OSM_PLACE_NODE"}
    else:
        # Does NOT masquerade as the village. The graph remains a test subset only.
        anchor={"name":"北京市区近似测试中心（不是前礼务村）","target":"FALLBACK_TEST_ONLY",
                "lat":39.9042,"lon":116.4074,"osm_node":None,
                "grade":"S_APPROX_FALLBACK"}
    handler=ExtractRoads(anchor["lat"],anchor["lon"])
    handler.apply_file(str(p),locations=True,idx="flex_mem")
    graph={
      "schema_version":16,
      "source":{"id":row["id"],"url":row["url"],"sha256":sha,
                "licence":"© OpenStreetMap contributors, ODbL 1.0",
                "reference_period":"2026-10-01","game_cutoff":"2026-10-09"},
      "anchor":anchor,"radius_m":RADIUS_M,
      "status":"OSM_EXTRACT_UNVALIDATED_FOR_LIVE_ROUTING",
      "nodes":dict(sorted(handler.nodes.items(),key=lambda x:int(x[0]))),
      "edges":sorted(handler.edges,key=lambda x:(int(x[0]),int(x[1]),x[2],int(x[4]))),
      "metadata":{"ways_seen":handler.ways_seen,
                  "border_segments_dropped":handler.excluded_border_segments,
                  "notes":"OSM way-node geometry, mode tags and oneway only. No turn restrictions, barrier checks or live travel time."}
    }
    audit=validate_graph(graph)
    if audit["nodes"]<20 or not audit["walk_edges"] or not audit["drive_edges"]:
        raise RuntimeError("Insufficient connected real OSM ways in target area")
    outfile=BASE/"osm_graph_sample.json"
    outfile.write_text(json.dumps(graph,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    samples={m:demo_pair(graph,m) for m in ("walk","drive")}
    if any(v is None for v in samples.values()):
        raise RuntimeError("No positive-length route example for one transport mode")
    summary={"test_only":True,"anchor":anchor,"sample_radius_m":RADIUS_M,
             "graph":audit,"mode_examples":samples,
             "graph_json_bytes":outfile.stat().st_size,
             "graph_json_sha256":hashlib.sha256(outfile.read_bytes()).hexdigest(),
             "source_verified_sha256":sha,
             "unmodeled":["turn restrictions","barrier nodes","conditional restrictions",
                          "junction design","traffic","closures","real travel-time"],
             "official_game_events_written":0}
    (BASE/"osm_graph_report.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="mode_examples"},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
