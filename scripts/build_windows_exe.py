#!/usr/bin/env python3
"""Build Windows executable. All intermediates and output are inside Work/.

Usage:
    python scripts/build_windows_exe.py --output Work
    python scripts/build_windows_exe.py --output Work --dry-run
    python scripts/build_windows_exe.py --output Work --verify-layout

A Windows runner with Python, Tk and PyInstaller is required for a real .exe.
We intentionally use --onedir then flatten its contents: no unpack-to-TEMP
at runtime; EXE lives at Work/EarthRealism.exe, dependencies at Work/_internal.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
ASSETS=["index.html","style.css","engine.js","society.js","economy.js","agent_ai.js","app.js","VERSION"]
NAME="EarthRealism"

def is_beneath(path,root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def build_plan(output):
    output=Path(output).resolve()
    # For safety all temporary/cache paths MUST be beneath output (never repo root/tmp).
    spots={name:output/name for name in (".build",".spec",".stage",".cache","tmp","logs","saves")}
    assert all(is_beneath(v,output) for v in spots.values())
    args=[sys.executable,"-m","PyInstaller","--noconfirm","--clean",
          "--windowed","--onedir","--contents-directory","_internal",
          "--name",NAME,"--distpath",str(spots[".stage"]),
          "--workpath",str(spots[".build"]),"--specpath",str(spots[".spec"])]
    for asset in ASSETS:
        args+=["--add-data",str(ROOT/"game"/asset)+os.pathsep+"game"]
    args.append(str(ROOT/"desktop_launcher.py"))
    return spots,args

def verify(output):
    output=Path(output).resolve()
    exe=output/(NAME+".exe")
    internal=output/"_internal"
    assert exe.is_file(),f"missing Windows executable: {exe}"
    assert internal.is_dir(),"missing colocated _internal dependencies"
    for asset in ASSETS:
        assert (internal/"game"/asset).is_file(),f"missing packaged asset {asset}"
    assert not (output/NAME).exists(),"executable must be directly under Work/, not Work/Name/"
    assert not (output/".stage"/NAME).exists(),"unflattened staging directory present"
    print(f"Verified {exe}; libraries/data/intermediates all under {output}")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="Work")
    parser.add_argument("--dry-run",action="store_true")
    parser.add_argument("--verify-layout",action="store_true")
    opts=parser.parse_args()
    out=Path(opts.output).resolve()
    spots,cmd=build_plan(out)
    if opts.dry_run:
        print("EXE:",out/(NAME+".exe"))
        for key,value in spots.items():print(key+":",value)
        print("Assets:",", ".join(ASSETS))
        return
    if opts.verify_layout:
        verify(out)
        return
    if os.name!="nt":
        parser.error("Windows .exe must be built on Windows, e.g. GitHub Actions windows-latest")
    out.mkdir(parents=True,exist_ok=True)
    for value in spots.values():value.mkdir(parents=True,exist_ok=True)
    environment=os.environ.copy()
    environment.update({
        "TMP":str(spots["tmp"]),"TEMP":str(spots["tmp"]),
        "TMPDIR":str(spots["tmp"]),"PYINSTALLER_CONFIG_DIR":str(spots[".cache"]),
        "PYTHONPYCACHEPREFIX":str(out/".pycache")
    })
    subprocess.run(cmd,cwd=ROOT,env=environment,check=True)
    bundle=spots[".stage"]/NAME
    if not (bundle/(NAME+".exe")).is_file():
        raise RuntimeError("PyInstaller succeeded but exe was not created")
    # All destination paths stay under Work. Dependencies remain *next* to EXE.
    for entry in bundle.iterdir():
        dest=out/entry.name
        if dest.is_dir():shutil.rmtree(dest)
        elif dest.exists():dest.unlink()
        shutil.move(str(entry),str(dest))
    shutil.rmtree(bundle)
    verify(out)
    (out/"README.txt").write_text(
        "EARTH REALISM "+(ROOT/"game"/"VERSION").read_text(encoding="utf-8").strip()+" / 地球：现实人生\n"
        "Double-click EarthRealism.exe. Keep Work/_internal next to the .exe.\n"
        "The launcher opens your web browser at http://127.0.0.1:8765/ .\n"
        "Do not move only the .exe out of Work. Optional Ollama runs separately.\n"
        "Build caches are stored inside Work/.build, Work/.spec, Work/.cache and Work/tmp.\n"
        "Game state is local to the browser; export JSON regularly.\n",
        encoding="utf-8")
if __name__=="__main__":
    main()
