#!/usr/bin/env python3
"""Acquire fixed historical source bytes; never backfill game's event history."""
import argparse, datetime as dt, hashlib, json, time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
OSM_URL="https://download.geofabrik.de/asia/china/beijing-260924.osm.pbf"
INDICATORS={
  "SP.POP.TOTL":"population",
  "NY.GDP.MKTP.CD":"GDP current USD",
  "FP.CPI.TOTL.ZG":"annual consumer price inflation %",
  "SL.UEM.TOTL.ZS":"unemployment modeled ILO estimate %",
}
def download(url,path,max_size):
    path.parent.mkdir(parents=True,exist_ok=True)
    for attempt in range(3):
        try:
            req=Request(url,headers={"User-Agent":"EarthRealismWorldbook/1.0 public-source archive"})
            with urlopen(req,timeout=160) as res, open(str(path)+".tmp","wb") as f:
                n=0; sha=hashlib.sha256()
                while True:
                    b=res.read(1024*1024)
                    if not b: break
                    n+=len(b)
                    if n>max_size: raise ValueError("Download exceeds max size")
                    f.write(b); sha.update(b)
            Path(str(path)+".tmp").replace(path)
            return n,sha.hexdigest()
        except Exception:
            Path(str(path)+".tmp").unlink(missing_ok=True)
            if attempt==2: raise
            time.sleep(2*(attempt+1))
def make_record(id,url,path,n,sha,license_note,effective,extra=None):
    rec={"id":id,"status":"INGESTED_VERIFIED_BYTES","url":url,
         "dest":path.relative_to(ROOT).as_posix(),"bytes":n,"sha256":sha,
         "acquired_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
         "effective_period":effective,"game_baseline":"2026-10-09",
         "license_note":license_note}
    if extra: rec.update(extra)
    return rec
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--osm",action="store_true")
    ap.add_argument("--wdi",action="store_true")
    args=ap.parse_args()
    if not (args.osm or args.wdi): ap.error("use --osm and/or --wdi")
    manifest=ROOT/"data/manifest.json"
    state=json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {"schema_version":1,"datasets":[]}
    by_id={item["id"]:item for item in state["datasets"]}
    if args.osm:
        p=ROOT/"data/raw/osm/beijing-2026-09-24.osm.pbf"
        n,sha=download(OSM_URL,p,80*1024*1024)
        if n<10*1024*1024 or b"OSMHeader" not in p.read_bytes()[:4096]:
            raise ValueError("Invalid Beijing OSM PBF")
        id="beijing_osm_2026_09_24"
        by_id[id]=make_record(id,OSM_URL,p,n,sha,
          "© OpenStreetMap contributors; ODbL 1.0; extract: Geofabrik GmbH","2026-09-24")
    if args.wdi:
        for ind,description in INDICATORS.items():
            url=f"https://api.worldbank.org/v2/country/CHN/indicator/{ind}?format=json&date=2020%3A2025&per_page=100"
            p=ROOT/f"data/raw/worldbank/CHN_{ind.replace('.','_')}_2020-2025.json"
            n,sha=download(url,p,4*1024*1024)
            rows=json.loads(p.read_text(encoding="utf-8"))
            if not(isinstance(rows,list) and len(rows)==2 and isinstance(rows[1],list)):
                raise ValueError("Unexpected World Bank JSON response: "+ind)
            if any(not("2020"<=str(r.get("date",""))<="2025") for r in rows[1]):
                raise ValueError("Unexpected data period")
            id="wdi_CHN_"+ind
            by_id[id]=make_record(id,url,p,n,sha,
              "World Bank open-data terms; source attribution required","2020-2025 reference years",
              {"indicator":ind,"description":description,"publication_as_of_2026_10_09":"UNVERIFIED_DO_NOT_BACKFILL"})
    state["datasets"]=sorted(by_id.values(),key=lambda d:d["id"])
    state["schema_version"]=1
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Recorded {len(state['datasets'])} downloaded data files; validate SHA256 before use.")
if __name__=="__main__": main()
