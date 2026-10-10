#!/usr/bin/env python3
"""Reproducible v16 source/results ZIP; original 36MB Beijing PBF stays in GitHub data/raw."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=[
 "artifacts/v16/network_v16.py","artifacts/v16/extract_v16.py",
 "artifacts/v16/scenario_v16.py","artifacts/v16/test_v16.py",
 "artifacts/v16/worldbook_protocol_v16.md","artifacts/v16/osm_graph_sample.json",
 "artifacts/v16/osm_graph_report.json","artifacts/v16/route_sandbox_journal.json",
 "artifacts/v16/route_sandbox_report.json",
 "artifacts/v14/engine_v14.py","artifacts/v14/official_world_state_frozen_v13.json",
 "docs/decisions/2026-10-10-v16-osm-network.md","worldbook/v16.md",
 "data/manifest.json"
]
def main():
    dest=ROOT/"artifacts/earth_realism_v16_bundle.zip"
    with zipfile.ZipFile(dest,"w") as z:
        for rel in sorted(FILES):
            p=ROOT/rel
            if not p.is_file():raise FileNotFoundError(rel)
            info=zipfile.ZipInfo("earth_realism_v16/"+rel,date_time=(2026,10,9,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(json.dumps({"bundle":str(dest.relative_to(ROOT)),
                      "bytes":dest.stat().st_size,
                      "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
                      "osm_original":"data/raw/osm/beijing-2026-10-01.osm.pbf (in GitHub separately)"},
                      ensure_ascii=False,indent=2))
if __name__=="__main__":main()
