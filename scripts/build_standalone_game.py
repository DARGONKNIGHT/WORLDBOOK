#!/usr/bin/env python3
"""Build/check one-file offline distribution from game sources (stdlib only).

Usage:
  python scripts/build_standalone_game.py
  python scripts/build_standalone_game.py --check
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "game"
OUT = GAME / "earth-realism.html"

def read(name):
    return (GAME / name).read_text(encoding="utf-8")

def build():
    html = read("index.html")
    substitutions = [
        ('<link rel="stylesheet" href="./style.css">', "<style>\n" + read("style.css") + "\n</style>"),
        ('<script src="./engine.js"></script>', "<script>\n" + read("engine.js") + "\n</script>"),
        ('<script src="./agent_ai.js"></script>', "<script>\n" + read("agent_ai.js") + "\n</script>"),
        ('<script src="./app.js"></script>', "<script>\n" + read("app.js") + "\n</script>"),
    ]
    for source, replacement in substitutions:
        assert html.count(source) == 1, f"Missing or duplicated tag: {source}"
        html = html.replace(source, replacement)
    assert '<script src="./' not in html
    assert '<link rel="stylesheet"' not in html
    return html

if __name__ == "__main__":
    expected = build()
    if "--check" in sys.argv:
        assert OUT.is_file(), "standalone HTML is missing"
        assert OUT.read_text(encoding="utf-8") == expected, "standalone HTML is stale"
        print("Standalone game matches source files.")
    else:
        OUT.write_text(expected, encoding="utf-8")
        print(f"Wrote {OUT} ({len(expected.encode('utf-8'))} bytes).")
