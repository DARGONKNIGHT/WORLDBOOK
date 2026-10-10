#!/usr/bin/env python3
"""Validate frozen official world and SHA256 of all ingested data files."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in ("AGENTS.md","docs/WORLDBOOK_MASTER.md","docs/FULL_DATA_GAP_REGISTER.md",
          "docs/NPC_ROSTER.md","data/README.md","scripts/ingest_open_data.py"):
    assert (ROOT/p).is_file(),f"Missing required {p}"
for v in range(2,13):
    assert (ROOT/f"worldbook/v{v:02}.md").is_file(),f"Missing v{v}"
frozen=json.loads((ROOT/"artifacts/v13/world_state_v13.json").read_text(encoding="utf-8"))
assert frozen.get("player_character") is None
assert frozen.get("game_started") is False
manifest=ROOT/"data/manifest.json"
if manifest.exists():
    docs=json.loads(manifest.read_text(encoding="utf-8"))["datasets"]
    ids=set()
    for d in docs:
        assert d["id"] not in ids, "duplicate dataset id"
        ids.add(d["id"])
        assert d["status"]=="INGESTED_VERIFIED_BYTES"
        p=ROOT/d["dest"]
        assert p.is_file(),f"Missing data bytes: {p}"
        assert p.stat().st_size==d["bytes"],f"Size mismatch: {p}"
        assert hashlib.sha256(p.read_bytes()).hexdigest()==d["sha256"],f"Hash mismatch: {p}"
    print(f"Verified {len(docs)} ingested source data files")
else:
    print("No actual data manifest yet; all indexed resources remain INDEX_ONLY")

# Derived data is a real GitHub artifact, not a source URL.
derived_manifest=ROOT/"data/derived/manifest.json"
if derived_manifest.exists():
    item=json.loads(derived_manifest.read_text(encoding="utf-8"))
    assert item["status"]=="COMMITTED_WITH_SHA256"
    source_record=next(d for d in docs if d["id"]==item["source"]["id"])
    assert source_record["sha256"]==item["source"]["sha256"]
    file_info=item["derived"]
    location=ROOT/file_info["path"]
    assert location.is_file(),f"Missing derived bytes: {location}"
    assert location.stat().st_size==file_info["bytes"],f"Derived size mismatch: {location}"
    assert hashlib.sha256(location.read_bytes()).hexdigest()==file_info["sha256"],f"Derived hash mismatch: {location}"
    graph=json.loads(location.read_text(encoding="utf-8"))
    assert graph["source"]["sha256"]==source_record["sha256"]
    assert graph["anchor"]["osm_node"]==item["anchor"]["node_id"]
    assert len(graph["nodes"])==item["nodes"]
    assert sum(edge[2]=="walk" for edge in graph["edges"])==item["edges"]["walk"]
    assert sum(edge[2]=="drive" for edge in graph["edges"])==item["edges"]["drive"]
    assert not frozen["actual_game_events"],"Official game events unexpectedly modified"
    print("Verified OSM-derived graph geometry, counts, source lineage and SHA256")
print("Frozen world and source-of-truth checks passed")
