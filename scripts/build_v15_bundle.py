#!/usr/bin/env python3
"""Build self-contained v15 sandbox bundle with deterministic ZIP metadata."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
include=[
  "artifacts/v14/engine_v14.py",
  "artifacts/v14/official_world_state_frozen_v13.json",
  "artifacts/v15/planner_v15.py",
  "artifacts/v15/scenario_v15.py",
  "artifacts/v15/test_v15.py",
  "artifacts/v15/worldbook_protocol_v15.md",
  "artifacts/v15/sandbox_v15_decisions.json",
  "artifacts/v15/sandbox_v15_journal.json",
  "artifacts/v15/sandbox_v15_summary.json",
  "worldbook/v15.md",
  "docs/decisions/2026-10-10-v15-limited-agent-scheduling.md"
]
def main():
    out=ROOT/"artifacts/earth_realism_v15_bundle.zip"
    with zipfile.ZipFile(out,"w") as zipfile_out:
        for rel in sorted(include):
            p=ROOT/rel
            assert p.is_file(),f"missing bundle item: {rel}"
            meta=zipfile.ZipInfo("earth_realism_v15/"+rel,date_time=(2026,10,9,0,0,0))
            meta.compress_type=zipfile.ZIP_DEFLATED
            meta.external_attr=0o100644<<16
            zipfile_out.writestr(meta,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(json.dumps({"bundle":str(out.relative_to(ROOT)),"bytes":out.stat().st_size,
          "sha256":hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
if __name__=="__main__":main()
