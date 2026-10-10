#!/usr/bin/env python3
"""Build a deterministic ZIP of ten new layers, scripts, reports and source refs.

The 36MB Beijing OSM PBF remains in GitHub data/raw; ZIP includes derivations.
"""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=[
"artifacts/v17_26/realism_layers.py",
"artifacts/v17_26/test_realism_layers.py",
"artifacts/v17_26/scenario.py",
"artifacts/v17_26/extract_osm_pois.py",
"artifacts/v17_26/osm_transit_nodes.json",
"artifacts/v17_26/osm_civic_poi_nodes.json",
"artifacts/v17_26/osm_poi_extract_report.json",
"artifacts/v17_26/simulation_evidence.json",
"artifacts/v17_26/simulation_summary.json",
"data/derived/manifest_v17_26.json",
"data/manifest.json",
]
files += [f"worldbook/v{i}.md" for i in range(17,27)]
adr={17:"transit",18:"places",19:"housing",20:"commerce",21:"employment",
     22:"services",23:"administration",24:"information",25:"macroeconomy",26:"integration"}
files += [f"docs/decisions/2026-10-10-v{i}-{adr[i]}.md" for i in range(17,27)]
dest=ROOT/"artifacts/earth_realism_v17_to_v26_bundle.zip"
with zipfile.ZipFile(dest,"w") as z:
    for rel in sorted(files):
        p=ROOT/rel
        if not p.is_file():raise FileNotFoundError(rel)
        zi=zipfile.ZipInfo("earth_realism_v17_to_v26/"+rel,date_time=(2026,10,9,0,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        zi.external_attr=0o100644<<16
        z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({"path":dest.relative_to(ROOT).as_posix(),"files":len(files),"bytes":dest.stat().st_size,
   "sha256":hashlib.sha256(dest.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
