#!/usr/bin/env python3
"""Rebuild auditable v13/v14 archives and v14 test outputs, using Python stdlib.

Reproducible ZIP metadata; sandbox writes never modify official frozen state.
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
    with zipfile.ZipFile(out, "w") as zf:
        for file in sorted(src.rglob("*")):
            if not file.is_file() or "__pycache__" in file.parts:
                continue
            name = f"earth_realism_v{version}/{file.relative_to(src).as_posix()}"
            meta = zipfile.ZipInfo(name, date_time=(2026, 10, 9, 0, 0, 0))
            meta.compress_type = zipfile.ZIP_DEFLATED
            meta.external_attr = 0o100644 << 16
            zf.writestr(meta, file.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
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
        raise RuntimeError("Frozen official world state was modified")
    result = {"frozen_state_sha256": after, "bundles": []}
    for version in (13, 14):
        p, size, digest = create_bundle(version)
        result["bundles"].append({"path": str(p.relative_to(ROOT)), "bytes": size, "sha256": digest})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
