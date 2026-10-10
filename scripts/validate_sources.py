#!/usr/bin/env python3
"""Validate the worldbook's external-data SOURCE INDEX only.

No scraping and no API access. Tests metadata schema and avoids pretending
that a source URL means dataset contents were downloaded or licensed.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

CATALOG = Path(__file__).resolve().parents[1] / "sources" / "catalog.json"
REQUIRED = {"id", "category", "title", "url", "authority", "purpose",
            "scope", "cadence", "license", "notes",
            "repository_status", "verified_or_discovered_as_of", "game_cutoff"}


def validate() -> list[str]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    sources = data["sources"]
    errors, ids = [], set()
    if data.get("game_baseline") != "2026-10-09":
        errors.append("Game baseline must remain 2026-10-09")
    for i, row in enumerate(sources):
        missing = REQUIRED - set(row)
        if missing:
            errors.append(f"source[{i}] missing fields: {sorted(missing)}")
            continue
        sid = row["id"]
        if sid in ids:
            errors.append(f"duplicate source ID: {sid}")
        ids.add(sid)
        if not re.fullmatch(r"[A-Z]{3,4}-\d{3}", sid):
            errors.append(f"invalid source ID format: {sid}")
        url = urlsplit(row["url"])
        if url.scheme != "https" or not url.netloc:
            errors.append(f"source {sid} has non-https/invalid URL")
        if row["repository_status"] != "INDEX_ONLY":
            errors.append(f"source {sid} implies dataset ingestion without an approved ingest ledger")
        if row["game_cutoff"] != "2026-10-09":
            errors.append(f"source {sid} has inconsistent game cutoff")
        for key in ("category", "title", "authority", "purpose", "scope", "license"):
            if not str(row[key]).strip():
                errors.append(f"source {sid} has empty {key}")
    if len(sources) != 43:
        print(f"NOTE: source count is now {len(sources)} (original v1.0 index has 43)")
    return errors


if __name__ == "__main__":
    problems = validate()
    print(f"Catalog: {CATALOG}")
    if problems:
        for item in problems:
            print("ERROR:", item)
        raise SystemExit(1)
    print("PASS: resource index metadata, IDs, URLs, and 2026 cutoff; not a license/content verification")
