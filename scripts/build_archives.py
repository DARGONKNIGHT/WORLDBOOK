#!/usr/bin/env python3
"""Build v13/v14 archival bundles and regenerable 30-day simulation results.

Requires Python 3.10+ standard library only.
Never changes the frozen official world state; sandbox fixtures are S-grade.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"


def create_bundle(version: int) -> tuple[Path, int, str]:
    src = ART / f"v{version}"
    out = ART / f"earth_realism_v{version}_bundle.zip"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for file in sorted(src.rglob("*")):
            if not file.is_file() or "__pycache__" in file.parts:
                continue
            zf.write(file, arcname=f"earth_realism_v{version}/{file.relative_to(src)}")
    data = out.read_bytes()
    return out, len(data), hashlib.sha256(data).hexdigest()


def main() -> None:
    v14 = ART / "v14"
    frozen = v14 / "official_world_state_frozen_v13.json"
    before = hashlib.sha256(frozen.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(v14 / "test_v14.py")], cwd=v14, check=True)
    subprocess.run([sys.executable, str(v14 / "scenario_v14.py")], cwd=v14, check=True)
    after = hashlib.sha256(frozen.read_bytes()).hexdigest()
    if before != after:
        raise RuntimeError("Frozen official v13 state was modified")
    result = {"frozen_state_sha256": after, "bundles": []}
    for version in (13, 14):
        p, size, digest = create_bundle(version)
        result["bundles"].append({"path": str(p.relative_to(ROOT)), "bytes": size, "sha256": digest})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
