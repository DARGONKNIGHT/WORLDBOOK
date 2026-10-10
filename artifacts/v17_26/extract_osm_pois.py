#!/usr/bin/env python3
"""Extract actual, dated, node-tagged local OSM transit and civic POIs.

Not a transit timetable; excludes area/way-based features, does not infer
hours, admission eligibility, fare, service frequency, or verified operator.
"""
import hashlib,json
from pathlib import Path
import osmium

from realism_layers import PlacesV18

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
CENTER=(40.1880155,116.7077492)
RADIUS_M=2800
SOURCE_SHA="945a6b7967c10dbd40a6e5c59bcae771a9dd44112ee4e37e868e5c544b34762d"

def distance(lat,lon):
    from math import asin,cos,radians,sin,sqrt
    a=sin(radians((lat-CENTER[0])/2))**2+cos(radians(lat))*cos(radians(CENTER[0]))*sin(radians((lon-CENTER[1])/2))**2
    return 2*6371008.8*asin(min(1,sqrt(a)))

TRANSIT_RAIL={"station","halt","tram_stop","subway_entrance"}
CIVIC_AMENITY={"school","kindergarten","hospital","clinic","pharmacy",
               "bank","post_office","library","police","fire_station",
               "townhall","community_centre","doctors","dentist","parking"}
COMMERCE_SHOP={"supermarket","convenience","bakery","greengrocer","hardware","repair"}
class NodeInventory(osmium.SimpleHandler):
    def __init__(self):super().__init__();self.transit={};self.places={}
    def node(self,n):
        if not n.location.valid():return
        lat,lon=n.location.lat,n.location.lon
        if distance(lat,lon)>RADIUS_M:return
        tags=n.tags
        pt=tags.get("public_transport")
        railway=tags.get("railway")
        highway=tags.get("highway")
        tid=str(n.id)
        item={"osm_node_id":tid,"lat":round(lat,7),"lon":round(lon,7),
              "name":tags.get("name") or None,
              "grade":"R_OSM_NODE_CROWDSOURCED",
              "effective_snapshot":"2026-10-01",
              "opening_hours":"U","service_schedule":"U","service_capacity":"U"}
        if highway=="bus_stop" or pt in ("stop_position","platform") or railway in TRANSIT_RAIL:
            self.transit[tid]=dict(item,public_transport=pt or None,
                                   highway=highway if highway=="bus_stop" else None,
                                   railway=railway if railway in TRANSIT_RAIL else None)
        amen=tags.get("amenity");shop=tags.get("shop")
        if amen in CIVIC_AMENITY or shop in COMMERCE_SHOP:
            cat=amen if amen in CIVIC_AMENITY else "shop:"+shop
            self.places[tid]=dict(item,category=cat,
                                  operator_identity="U",
                                  address_precision="OSM_NODE_ONLY_NO_HOUSENUMBER")
def main():
    src=json.loads((ROOT/"data/manifest.json").read_text(encoding="utf-8"))
    original=next(x for x in src["datasets"] if x["id"]=="beijing_osm_2026_10_01")
    p=ROOT/original["dest"]
    must=hashlib.sha256(p.read_bytes()).hexdigest()
    if must!=SOURCE_SHA or must!=original["sha256"]:raise ValueError("OSM source corrupted")
    h=NodeInventory();h.apply_file(str(p))
    common={"source_id":"beijing_osm_2026_10_01","source_sha256":must,
             "source_date":"2026-10-01","radius_m":RADIUS_M,
             "center":{"place_name":"前礼务村","osm_node_id":"6410843713",
                       "lat":CENTER[0],"lon":CENTER[1]},
             "license":"© OpenStreetMap contributors, ODbL 1.0",
             "scope":"Node-based public tags only; excludes polygon/way features.",
             "verified_schedules":False,"official_service_eligibility_verified":False}
    results={}
    for label,rows in (("transit_nodes",h.transit),("civic_poi_nodes",h.places)):
        data=dict(common,kind=label,features=[rows[k] for k in sorted(rows,key=int)])
        target=BASE/f"osm_{label}.json"
        target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        results[label]={"count":len(rows),"path":target.relative_to(ROOT).as_posix(),
                        "sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
                        "bytes":target.stat().st_size}
    report={"grade":"R_OSM_DERIVED_NOT_AUTHORITATIVE","records":results,
            "transit_timetables":"U_NOT_INGESTED",
            "real_medical_education_legal_eligibility":"U",
            "source_sha256":must,"official_game_events_written":0}
    (BASE/"osm_poi_extract_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
