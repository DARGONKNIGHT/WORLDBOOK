#!/usr/bin/env python3
"""v16 deterministic graph router on OSM-derived edges. NOT navigation advice.

No remote lookups, private location data, turn restrictions, traffic, barriers,
temporary closures or real travel-time predictions. All time estimates are S.
"""
from __future__ import annotations
import heapq
import json
import math
from pathlib import Path

WALK_SPEED_KMH=4.5
DRIVE_SPEED_KMH=25.0   # strictly assumed demonstration speed, never real ETA

NO={"no","private","customers","delivery","agricultural","forestry"}
YES={"yes","designated","permissive","official"}
FOOT_HIGHWAYS={"footway","pedestrian","path","steps","living_street","residential",
               "service","unclassified","tertiary","track"}
DRIVE_HIGHWAYS={"motorway","motorway_link","trunk","trunk_link","primary","primary_link",
                "secondary","secondary_link","tertiary","tertiary_link",
                "unclassified","residential","living_street","service"}

def permitted(tags,mode):
    hw=tags.get("highway")
    if not hw or mode not in ("walk","drive"):
        return False
    if any(k.endswith(":conditional") for k in tags if k.startswith(
            ("access","vehicle","motor_vehicle","motorcar","foot","oneway"))):
        return False # unknown temporal eligibility -> conservative omit
    if mode=="walk":
        decision=hw in FOOT_HIGHWAYS
        # Motorway/trunk and faster primary/secondary only if explicit foot=yes
        for key in ("access","foot"):
            value=tags.get(key)
            if value in NO: decision=False
            elif key=="foot" and value in YES: decision=hw not in {"motorway","motorway_link"}
        return decision
    decision=hw in DRIVE_HIGHWAYS
    for key in ("access","vehicle","motor_vehicle","motorcar"):
        value=tags.get(key)
        if value in NO: decision=False
        elif value in YES: decision=True
    # Still prohibit driving designated pedestrian and footways even if access=yes
    if hw in {"footway","pedestrian","steps","cycleway","path"}:
        return False
    return decision

def directions(tags,mode):
    if mode=="walk":
        one=tags.get("oneway:foot","no")
    else:
        one=tags.get("oneway", "yes" if tags.get("junction")=="roundabout" or
                     tags.get("highway") in ("motorway","motorway_link") else "no")
    if one in ("yes","true","1"): return (1,)
    if one=="-1": return (-1,)
    if one in ("no","false","0"): return (1,-1)
    return () # unknown direction -> avoid unsafe assumption

def haversine(lat1,lon1,lat2,lon2):
    r=6371008.8
    a=math.sin(math.radians(lat2-lat1)/2)**2
    a+=math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 2*r*math.asin(min(1,math.sqrt(a)))

def graph_index(graph,mode):
    adjacency={}
    for src,dst,m,length,way,highway in graph["edges"]:
        if m==mode:
            adjacency.setdefault(str(src),[]).append((str(dst),float(length),str(way),highway))
    for arr in adjacency.values():
        arr.sort(key=lambda x:(x[0],x[2]))
    return adjacency

def shortest(graph,source,target,mode):
    """Source/target are OSM node IDs. No implicit snapping or forced connectedness."""
    source,target=str(source),str(target)
    if mode not in ("walk","drive"): raise ValueError("unsupported mode")
    nodes=graph["nodes"]
    if source not in nodes or target not in nodes:
        raise KeyError("unknown OSM node id")
    adj=graph_index(graph,mode)
    d={source:0.0}
    parent={}
    q=[(0.0,source)]
    while q:
        dist,node=heapq.heappop(q)
        if dist > d[node]+1e-8: continue
        if node==target: break
        for nex,weight,way,hw in adj.get(node,[]):
            candidate=dist+weight
            if candidate < d.get(nex,float("inf"))-1e-8:
                d[nex]=candidate
                parent[nex]=(node,way)
                heapq.heappush(q,(candidate,nex))
    if target not in d: return None
    chain=[target]
    ways=[]
    while chain[-1]!=source:
        pred,way=parent[chain[-1]]
        chain.append(pred); ways.append(way)
    chain.reverse();ways.reverse()
    meters=round(d[target],2)
    speed=WALK_SPEED_KMH if mode=="walk" else DRIVE_SPEED_KMH
    return {"status":"candidate_only","mode":mode,"origin_node":source,
            "destination_node":target,"node_ids":chain,"way_ids":ways,
            "distance_m":meters,
            "illustrative_minutes":round(meters/1000/speed*60,2),
            "illustrative_speed_kmh":speed,
            "travel_time_grade":"S_UNCALIBRATED",
            "distance_grade":"R_DERIVED_FROM_OSM_GEOMETRY",
            "excluded":"turn restrictions, conditional tags, barriers, closures, traffic, local laws, crossings",
            "source_dataset_sha256":graph["source"]["sha256"]}

def nearest_node(graph,lat,lon,max_distance_m=150):
    if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)):
        raise ValueError("coordinates required")
    candidates=((haversine(lat,lon,p[0],p[1]),n) for n,p in graph["nodes"].items())
    best=min(candidates,default=(float("inf"),None))
    return {"node":best[1],"distance_m":round(best[0],2)} if best[0]<=max_distance_m else None

def validate_graph(graph):
    assert graph["schema_version"]==16
    assert graph["source"]["sha256"] and graph["source"]["game_cutoff"]=="2026-10-09"
    assert graph["anchor"]["grade"] in ("R_OSM_PLACE_NODE","S_APPROX_FALLBACK")
    for src,dst,mode,meters,wid,hw in graph["edges"]:
        assert str(src) in graph["nodes"] and str(dst) in graph["nodes"]
        assert mode in ("walk","drive") and type(meters) in (int,float) and meters>0
    return {"nodes":len(graph["nodes"]),"directed_edges":len(graph["edges"]),
            "walk_edges":sum(x[2]=="walk" for x in graph["edges"]),
            "drive_edges":sum(x[2]=="drive" for x in graph["edges"])}

def load_graph(path):
    graph=json.loads(Path(path).read_text(encoding="utf-8"))
    validate_graph(graph)
    return graph

def demo_pair(graph,mode):
    """Choose a reproducible, small connected OSM-sourced route (not invented places)."""
    adj=graph_index(graph,mode)
    for src in sorted(adj):
        rows=adj[src]
        if rows:
            # A real connected segment, not necessarily a meaningful origin/destination.
            dst=max(rows,key=lambda v:(v[1],v[0]))[0]
            if dst!=src:
                out=shortest(graph,src,dst,mode)
                if out and out["distance_m"]>0:
                    return out
    return None
