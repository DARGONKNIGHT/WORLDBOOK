#!/usr/bin/env python3
"""Deterministic v27-v30 compact artifact. PBF already in GitHub data/raw."""
from pathlib import Path
import hashlib,zipfile,json
ROOT=Path(__file__).resolve().parents[1]
files=[f"worldbook/v{i}.md" for i in range(27,31)]
files += [f"artifacts/v27_30/{n}" for n in [
 "ways_v27.py","turns_v28.py","calendar_v29.py","readiness_v30.py","test_v27_30.py",
 "osm_public_way_features.json","way_features_report.json",
 "turn_restrictions_local.json","turn_restrictions_report.json",
 "readiness_report.json","test_run_v27_30.txt"]]
files += [f"docs/decisions/2026-10-10-v{i}-{slug}.md" for i,slug in [
 (27,"osm-public-ways"),(28,"turn-restrictions"),(29,"gtfs-calendar"),(30,"evidence-readiness")]]
files += ["data/manifest.json","data/derived/manifest_v27_30.json"]
out=ROOT/"artifacts/earth_realism_v27_to_v30_bundle.zip"
with zipfile.ZipFile(out,"w") as archive:
    for rel in sorted(files):
        file=ROOT/rel
        if not file.is_file():raise FileNotFoundError(rel)
        info=zipfile.ZipInfo("earth_realism_v27_to_v30/"+rel,date_time=(2026,10,9,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        archive.writestr(info,file.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({"zip":out.relative_to(ROOT).as_posix(),"files":len(files),
                  "bytes":out.stat().st_size,
                  "sha256":hashlib.sha256(out.read_bytes()).hexdigest()}))
