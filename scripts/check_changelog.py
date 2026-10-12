#!/usr/bin/env python3
"""Guard repository CHANGELOG.md: newest dated entry first, game versions descending."""
import re
from pathlib import Path
from datetime import date

path=Path(__file__).resolve().parents[1]/"CHANGELOG.md"
text=path.read_text(encoding="utf-8")
rows=re.findall(r"^## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})\s*$",text,re.M)
assert rows, "Missing dated changelog entries"
assert len(rows)==len(set(rows)), "Duplicate dated changelog entries"
dates=[date.fromisoformat(d) for _,d in rows]
assert dates==sorted(dates,reverse=True), "CHANGELOG must list newest dates first"
versions=[]
for title,_ in rows:
    if title.startswith("Game "):
        token=title[5:]
        assert re.fullmatch(r"\d+\.\d+\.\d+",token), "Game must have semver"
        versions.append(tuple(map(int,token.split("."))))
assert versions==sorted(versions,reverse=True), "Game versions must be newest first"
current=(path.parent/"game"/"VERSION").read_text(encoding="utf-8").strip()
assert versions and current==".".join(map(str,versions[0])), "game/VERSION must match the newest CHANGELOG game release"
print(f"Validated {len(rows)} release notes in reverse chronological order")
