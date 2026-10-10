#!/usr/bin/env python3
"""v31 genuine OSM multipolygon public facilities, not merely closed way tags.

Pyosmium assembles areas with a two-pass read. Restrict to relation-based
multipolygons with safe public-service tags; does not index private residences
and does NOT claim true centroid, entrance or operating status.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
import osmium
ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
CENTER=(40.1880155,116.7077492);RADIUS=2800
SAFE_AMENITY={"school","kindergarten","hospital","clinic","library","post_office",
              "community_centre","marketplace","bus_station","townhall"}
SAFE_SHOPS={"supermarket","convenience","books"}
def permitted(tags):
    if tags.get("amenity") in SAFE_AMENITY:return "amenity:"+tags["amenity"]
    if tags.get("shop") in SAFE_SHOPS:return "shop:"+tags["shop"]
    if tags.get("public_transport") in ("station","platform"):return "public_transport:"+tags["public_transport"]
    return None
def meters(lat,lon):
    a=math.sin(math.radians((lat-CENTER[0])/2))**2
    a+=math.cos(math.radians(lat))*math.cos(math.radians(CENTER[0]))*math.sin(math.radians((lon-CENTER[1])/2))**2
    return 2*6371008.8*math.asin(min(1,math.sqrt(a)))
def representation(relation_id,kind,rings,name):
    pts=[p for ring in rings for p in ring]
    if not pts or min(meters(*x) for x in pts)>RADIUS:return None
    return {"type":"multipolygon_relation","osm_relation_id":str(relation_id),
      "kind":kind,"name":name,"outer_ring_count":len(rings),
      "outer_vertex_count":len(pts),
      "bbox":[round(min(a for a,b in pts),7),round(min(b for a,b in pts),7),
              round(max(a for a,b in pts),7),round(max(b for a,b in pts),7)],
      "representative_lat":round(sum(a for a,b in pts)/len(pts),7),
      "representative_lon":round(sum(b for a,b in pts)/len(pts),7),
      "representative_grade":"OUTER_VERTICES_ARITHMETIC_MEAN_NOT_CENTROID_ENTRANCE",
      "holes_disclosed":False,"operating_status":"U","service_eligibility":"U",
      "grade":"R_OSM_CROWDSOURCED"}
class Areas(osmium.SimpleHandler):
    def __init__(self):
        super().__init__();self.rows={};self.candidates=0;self.omitted=0
    def area(self,polygon):
        if polygon.from_way():return  # v27 already covers closed-way footprints
        tags={str(t.k):str(t.v) for t in polygon.tags}
        kind=permitted(tags)
        if not kind:return
        self.candidates+=1
        rings=[]
        for ring in polygon.outer_rings():
            coords=[(float(n.lat),float(n.lon)) for n in ring if n.location.valid()]
            if len(coords)>=4:rings.append(coords)
        if not rings:
            self.omitted+=1;return
        row=representation(polygon.orig_id(),kind,rings,tags.get("name"))
        if row:self.rows[row["osm_relation_id"]]=row
def main():
    manifest=json.loads((ROOT/"data/manifest.json").read_text())
    info=next(d for d in manifest["datasets"] if d["id"]=="beijing_osm_2026_10_01")
    p=ROOT/info["dest"];sha=hashlib.sha256(p.read_bytes()).hexdigest()
    if sha!=info["sha256"]:raise ValueError("PBF mismatch")
    handler=Areas()
    handler.apply_file(str(p),locations=True,idx="flex_mem")
    items=[handler.rows[k] for k in sorted(handler.rows,key=int)]
    output={"schema":31,"source_sha256":sha,"snapshot":"2026-10-01",
       "center":{"name":"前礼务村","osm_node":"6410843713"},
       "radius_m":RADIUS,"features":items,
       "area_based":True,"private_residences_included":False,
       "not_included":["way-shaped facilities from v27","incomplete polygons",
         "non-service areas","entrances","inner ring topology","actual providers"],
       "attribution":"© OpenStreetMap contributors; ODbL 1.0"}
    target=BASE/"osm_public_multipolygons.json"
    target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report={"source_sha256":sha,"count":len(items),
       "candidate_multipolygons_in_whole_pbf":handler.candidates,
       "malformed_or_missing_outer_rings":handler.omitted,
       "bytes":target.stat().st_size,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
       "output":target.relative_to(ROOT).as_posix(),
       "all_areas_complete":False}
    (BASE/"area_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
