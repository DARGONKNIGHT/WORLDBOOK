#!/usr/bin/env python3
"""Minimum realism-first release gate. This is a structural guard, not evidence verification.

Rejects releases silently removing realism charter, physics checks, financial
audit, frozen-world separation or EXE containment.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
def content(p):
    path=ROOT/p
    assert path.is_file(),f"Required realism artifact missing: {p}"
    return path.read_text(encoding="utf-8")

policy=content("docs/REALISM_CONSTITUTION.md")
agent=content("AGENTS.md")
master=content("docs/WORLDBOOK_MASTER.md")
version=content("game/VERSION").strip()
readme=content("README.md")
changelog=content("CHANGELOG.md")
world=content("worldbook/v36.md")
sim=content("game/simulation.js")
engine=content("game/engine.js")
tests=content("game/tests/realism.test.cjs")
win=content(".github/workflows/windows-exe.yml")
linux=content(".github/workflows/game-tests.yml")
exe=content("scripts/build_windows_exe.py")

for phrase in ["真实性优先于", "R", "S", "U", "时间", "未知", "NPC", "EXE", "2026-10-09"]:
    assert phrase in policy,f"Realism constitution missing {phrase}"
assert agent.index("docs/REALISM_CONSTITUTION.md") < agent.index("## 强制工作流"),"Realism must be at the top of AGENTS"
assert "真实性" in master and "docs/REALISM_CONSTITUTION.md" in readme
assert "最高" in world and "中断" in world and "未知" in world
assert "positionGrade:\"U\"" in sim and "resumeTravel" in sim and 'status:"stranded"' in sim
assert "在途" in engine and "mobility" in engine
assert tests.count('test("') >= 7, "Need realistic counterexample/regression tests"
assert version=="7.0.0" or re.fullmatch(r"[1-9]\d*\.\d+\.\d+",version),"Unexpected game version"
assert f"## [Game {version}]" in changelog
assert "Work/EarthRealism.exe" in exe or "Work/EarthRealism.exe" in content("docs/REALISM_CONSTITUTION.md")
for name,workflow in [("Linux",linux),("Windows",win)]:
    assert "check_realism.py" in workflow,f"{name} CI must enforce realism charter"
    assert "realism.test.cjs" in workflow or "game/tests/*.test.cjs" in workflow,f"{name} CI must run physical realism regression"
    assert "AGENTS.md" in workflow and "docs/REALISM_CONSTITUTION.md" in workflow, f"{name} CI must trigger on core policy changes"
assert "Build Windows EXE entirely within Work" in win and "Smoke-test the frozen Windows EXE" in win
print(f"Realism-first gate passed: Game {version}; charter, physical-action regression, worldbook, EXE layout and dual CI workflows")
