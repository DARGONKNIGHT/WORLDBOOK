#!/usr/bin/env python3
"""v27 OSM PUBLIC feature coverage beyond node-only inventories.

Read actual GitHub-pinned Beijing PBF; one derived record per OSM way.
Way centroid is an arithmetic representative point, NOT the entrance or exact
polygon centroid. Multipolygon relations and private residential features
are out of scope. Retains full source way ID, tags category, approximate bbox.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
import osmium

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
SRC_SHA="945a6b7967c10dbd40a6e5c59bcae771a9dd44112ee4e37e868e5c544b34762d"
CENTER=(40.1880155,116.7077492)
RADIUS=2800
SAFE_AMENITIES={"school","kindergarten","hospital","clinic","doctors","pharmacy",
  "library","police","fire_station","townhall","community_centre","post_office",
  "bank","marketplace","bus_station","parking","college","university"}
SAFE_SHOPS={"supermarket","convenience","bakery","greengrocer","hardware","books","car_repair"}
SAFE_RAIL={"station","tram_stop","halt"}
SAFE_PT={"platform","station"}
def distance(lat,lon):
    a=math.sin(math.radians((lat-CENTER[0])/2))**2
    a+=math.cos(math.radians(lat))*math.cos(math.radians(CENTER[0]))*math.sin(math.radians((lon-CENTER[1])/2))**2
    return 2*6371008.8*math.asin(min(1,math.sqrt(a)))
def category(tags):
    if tags.get("amenity") in SAFE_AMENITIES:return "amenity:"+tags["amenity"]
    if tags.get("shop") in SAFE_SHOPS:return "shop:"+tags["shop"]
    if tags.get("public_transport") in SAFE_PT:return "public_transport:"+tags["public_transport"]
    if tags.get("railway") in SAFE_RAIL:return "railway:"+tags["railway"]
    return None
def summarize_way(id,coords,tags):
    kind=category(tags)
    if not kind or len(coords)<2:return None
    # Each source object is preserved as one feature, not each polygon vertex.
    if min(distance(lat,lon) for lat,lon in coords)>RADIUS:return None
    lats=[x[0] for x in coords];lons=[x[1] for x in coords]
    closed=(coords[0]==coords[-1] and len(coords)>=4)
    return {"osm_type":"way","osm_id":str(id),"category":kind,
      "name":tags.get("name"),"geometry_type":"closed_way" if closed else "linear_way",
      "representative_lat":round(sum(lats)/len(lats),7),
      "representative_lon":round(sum(lons)/len(lons),7),
      "bbox":[round(min(lats),7),round(min(lons),7),
              round(max(lats),7),round(max(lons),7)],
      "geometry_quality":"VERTEX_MEAN_NOT_ENTRANCE_OR_TRUE_CENTROID",
      "operation_hours":"U","current_operator":"U","legal_eligibility":"U",
      "grade":"R_OSM_CROWDSOURCED_NOT_VERIFIED_OFFICIAL"}
class Ways(osmium.SimpleHandler):
    def __init__(self):super().__init__();self.rows={}
    def way(self,way):
        tags={str(t.k):str(t.v) for t in way.tags}
        if not category(tags):return
        coords=[(n.location.lat,n.location.lon) for n in way.nodes if n.location.valid()]
        if len(coords)!=len(way.nodes):return
        item=summarize_way(way.id,coords,tags)
        if item:self.rows[item["osm_id"]]=item
def main():
    state=json.loads((ROOT/"data/manifest.json").read_text())
    src=next(x for x in state["datasets"] if x["id"]=="beijing_osm_2026_10_01")
    f=ROOT/src["dest"]
    rawhash=hashlib.sha256(f.read_bytes()).hexdigest()
    if rawhash!=SRC_SHA or src["sha256"]!=rawhash:raise ValueError("source checksum mismatch")
    finder=Ways();finder.apply_file(str(f),locations=True)
    rows=[finder.rows[k] for k in sorted(finder.rows,key=int)]
    dataset={"schema":27,"source_sha256":rawhash,"snapshot":"2026-10-01",
      "center":{"name":"前礼务村","osm_node_id":"6410843713",
                "lat":CENTER[0],"lon":CENTER[1]},
      "radius_m":RADIUS,"osm_object_type":"way","features":rows,
      "excluded":["multipolygon relations","private residential houses","detailed parcel title",
                  "service hours","precise legal eligibility","entrance positions"],
      "attribution":"© OpenStreetMap contributors; ODbL 1.0"}
    out=BASE/"osm_public_way_features.json"
    out.write_text(json.dumps(dataset,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    proof={"source_sha256":rawhash,"count":len(rows),
           "closed_way_count":sum(x["geometry_type"]=="closed_way" for x in rows),
           "linear_way_count":sum(x["geometry_type"]=="linear_way" for x in rows),
           "output":out.relative_to(ROOT).as_posix(),"bytes":out.stat().st_size,
           "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
           "multipolygon_relations_indexed":False,"real_service_hours_verified":False}
    (BASE/"way_features_report.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(proof,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
