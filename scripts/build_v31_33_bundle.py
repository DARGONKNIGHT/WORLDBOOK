#!/usr/bin/env python3
"""Deterministic v31-v33 compact archive, original OSM already preserved."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
files=[
"artifacts/v31_33/areas_v31.py","artifacts/v31_33/barriers_v32.py",
"artifacts/v31_33/closure_v33.py","artifacts/v31_33/test_v31_33.py",
"artifacts/v31_33/osm_public_multipolygons.json",
"artifacts/v31_33/area_report.json","artifacts/v31_33/osm_barrier_nodes.json",
"artifacts/v31_33/barrier_report.json","artifacts/v31_33/milestone_v33.json",
"artifacts/v31_33/test_run_v31_33.txt",
"data/derived/manifest_v31_33.json","data/manifest.json",
]
files += [f"worldbook/v{i}.md" for i in range(31,34)]
files += [f"docs/decisions/2026-10-10-v{i}-{name}.md" for i,name in
          [(31,"multipolygon-public-facilities"),(32,"road-barriers"),(33,"source-gated-audit")]]
out=ROOT/"artifacts/earth_realism_v31_to_v33_bundle.zip"
with zipfile.ZipFile(out,"w") as z:
    for path in sorted(files):
        file=ROOT/path
        if not file.is_file():raise FileNotFoundError(path)
        info=zipfile.ZipInfo("earth_realism_v31_to_v33/"+path,date_time=(2026,10,9,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        z.writestr(info,file.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({"zip":out.relative_to(ROOT).as_posix(),"bytes":out.stat().st_size,
                  "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
                  "files":len(files)},ensure_ascii=False))
