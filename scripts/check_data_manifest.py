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
# v17-v26: the actual data bytes and node-count claims must match the registry.
new_manifest=ROOT/"data/derived/manifest_v17_26.json"
if new_manifest.exists():
    cache=json.loads(new_manifest.read_text(encoding="utf-8"))
    assert cache["source"]["sha256"]==next(x["sha256"] for x in docs if x["id"]==cache["source"]["id"])
    assert cache["source"]["path"]==next(x["dest"] for x in docs if x["id"]==cache["source"]["id"])
    assert cache["timetables"]=="U_NOT_INGESTED" and cache["hours_and_capacities"]=="U_NOT_INGESTED"
    for category,rec in cache["outputs"].items():
        target=ROOT/rec["path"]
        assert target.is_file(),f"Missing OSM node snapshot {target}"
        raw=target.read_bytes()
        assert len(raw)==rec["bytes"] and hashlib.sha256(raw).hexdigest()==rec["sha256"]
        data=json.loads(raw)
        assert data["source_sha256"]==cache["source"]["sha256"]
        assert data["source_date"]=="2026-10-01"
        assert len(data["features"])==rec["count"],"OSM node feature count mismatch"
        assert all(z["grade"]=="R_OSM_NODE_CROWDSOURCED" and z["opening_hours"]=="U" for z in data["features"])
    proof=json.loads((ROOT/"artifacts/v17_26/simulation_summary.json").read_text(encoding="utf-8"))
    assert proof["versions_completed"]==list(range(17,27))
    assert proof["official_game_events_written"]==0 and not proof["comprehensive_real_life_simulation"]
    official_bytes=(ROOT/"artifacts/v14/official_world_state_frozen_v13.json").read_bytes()
    assert proof["official_sha256"]==hashlib.sha256(official_bytes).hexdigest()
    print("Verified v17-v26 real OSM derived node bytes, manifest and frozen sandbox report")
# v27-v33 verified source-data derivatives. A URL without bytes never passes.
for label,filename in (("v27-v30","manifest_v27_30.json"),
                       ("v31-v33","manifest_v31_33.json")):
    meta_path=ROOT/"data/derived"/filename
    if meta_path.exists():
        meta=json.loads(meta_path.read_text(encoding="utf-8"))
        src=next(x for x in docs if x["id"]=="beijing_osm_2026_10_01")
        assert meta["source_sha256"]==src["sha256"],"OSM source lineage conflict"
        for item in meta["outputs"].values():
            assert item["source_sha256"]==src["sha256"]
            dest=item.get("output")
            if dest is None and filename=="manifest_v27_30.json":
                dest="artifacts/v27_30/turn_restrictions_local.json"
            p=ROOT/dest
            assert p.is_file(),f"missing derived bytes {p}"
            assert p.stat().st_size==item["bytes"],f"derived size mismatch {p}"
            assert hashlib.sha256(p.read_bytes()).hexdigest()==item["sha256"],f"derived sha mismatch {p}"
        if filename=="manifest_v31_33.json":
            checkpoint=json.loads((ROOT/"artifacts/v31_33/milestone_v33.json").read_text())
            assert checkpoint["official_history_written"]==0
            frozen_bytes=(ROOT/"artifacts/v14/official_world_state_frozen_v13.json").read_bytes()
            assert hashlib.sha256(frozen_bytes).hexdigest()==checkpoint["official_frozen_sha256"]
        print(f"Verified {label} real OSM derived files and lineage")
print("Frozen world and source-of-truth checks passed")
