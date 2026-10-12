"""Earth Realism Windows launcher (game 6.0).

PyInstaller --onedir binary is flattened to Work/EarthRealism.exe, with _internal
in the *same* Work directory. No onefile extraction in an external temp folder.

The executable serves bundled HTML/JS locally and opens the default browser.
Ollama is optional and is not bundled into the executable.
"""
from __future__ import annotations
import logging
import json
import os
from pathlib import Path
import sys
import threading
import webbrowser
import urllib.request
import tkinter as tk
from tkinter import messagebox
from http.server import ThreadingHTTPServer

from game.agent_server import Handler

APP_NAME="地球：现实人生"
APP_PORT=8765

def game_version():
    folder=(Path(sys._MEIPASS) if getattr(sys,"frozen",False) else Path(__file__).resolve().parent)/"game"
    return (folder/"VERSION").read_text(encoding="utf-8").strip()

MAX_SAVE=3*1024*1024
class DesktopHandler(Handler):
    """Desktop-only save endpoint; fixed Work/saves location and atomic writes."""
    def allowed(self):
        origin=self.headers.get("Origin","")
        return not origin or origin in (f"http://127.0.0.1:{APP_PORT}",f"http://localhost:{APP_PORT}")

    def saved_path(self):
        return app_root()/"saves"/"autoplay.json"

    def do_GET(self):
        if self.path!="/api/save":
            return super().do_GET()
        path=self.saved_path()
        if not path.is_file():
            return self.send_json(404,{"error":"No desktop save yet"})
        data=path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path!="/api/save":
            return super().do_POST()
        if not self.allowed():
            return self.send_json(403,{"error":"Cross-origin save request rejected"})
        if self.headers.get("Content-Type","").split(";")[0].strip()!="application/json":
            return self.send_json(415,{"error":"Expected JSON"})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length<2 or length>MAX_SAVE:
                return self.send_json(413,{"error":"Save exceeds limit"})
            raw=self.rfile.read(length)
            payload=json.loads(raw)
            if not isinstance(payload,dict) or payload.get("mode")!="S_INDEPENDENT_PLAYTHROUGH" or not isinstance(payload.get("player"),dict):
                return self.send_json(422,{"error":"Invalid local game save"})
            target=self.saved_path()
            target.parent.mkdir(parents=True,exist_ok=True)
            # Unique staging name is under Work/saves, never system TMP.
            temp_name=target.parent/("."+target.name+".stage")
            temp_name.write_bytes(raw)
            os.replace(temp_name,target)
            return self.send_json(200,{"saved":True})
        except (OSError,TypeError,ValueError) as exc:
            return self.send_json(422,{"error":str(exc)[:120]})

    def do_DELETE(self):
        if self.path!="/api/save":
            return self.send_json(404,{"error":"Unknown endpoint"})
        if not self.allowed():
            return self.send_json(403,{"error":"Cross-origin delete request rejected"})
        self.saved_path().unlink(missing_ok=True)
        return self.send_json(200,{"deleted":True})


def app_root():
    return Path(sys.executable).resolve().parent if getattr(sys,"frozen",False) else Path(__file__).resolve().parent / "Work"

def prepare_directories(root=None):
    root=Path(root or app_root()).resolve()
    for name in ("logs","saves","cache","tmp"):
        (root/name).mkdir(parents=True,exist_ok=True)
    return root

def self_test():
    """Headless smoke test of the actual frozen .exe's bundled local web service."""
    root=prepare_directories()
    logging.basicConfig(filename=root/"logs"/"launcher.log",level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s",encoding="utf-8",force=True)
    assets=(Path(sys._MEIPASS) if getattr(sys,"frozen",False) else Path(__file__).parent)/"game"
    for name in ("index.html","engine.js","society.js","economy.js","agent_ai.js","simulation.js","app.js","VERSION"):
        if not (assets/name).is_file():
            raise RuntimeError(f"Bundled asset missing: {name}")
    service=ThreadingHTTPServer(("127.0.0.1",0),DesktopHandler)
    thread=threading.Thread(target=service.serve_forever,daemon=True)
    thread.start()
    try:
        base=f"http://127.0.0.1:{service.server_port}"
        with urllib.request.urlopen(base+"/api/health",timeout=5) as response:
            if response.status!=200:raise RuntimeError("Local health check failed")
        with urllib.request.urlopen(base+"/index.html",timeout=5) as response:
            page=response.read(300000)
            if b'<script src="./simulation.js"></script>' not in page:
                raise RuntimeError("Local frontend missing society wiring")
        logging.info("Frozen executable self-test passed; assets=%s",assets)
    finally:
        service.shutdown()
        service.server_close()
    return 0

def main():
    root=prepare_directories()
    logging.basicConfig(filename=root/"logs"/"launcher.log",level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",encoding="utf-8")
    window=tk.Tk()
    window.title(APP_NAME+" · Windows")
    window.geometry("470x220")
    window.minsize(430,200)
    window.configure(bg="#121d26")
    panel=tk.Frame(window,bg="#121d26",padx=24,pady=18)
    panel.pack(fill="both",expand=True)
    tk.Label(panel,text=APP_NAME+"  v"+game_version(),font=("Microsoft YaHei",18,"bold"),
             bg="#121d26",fg="#e3eecf").pack(anchor="w")
    tk.Label(panel,text="31名S级自主人物 · 无回合连续时间 · 本地AI可选",
             font=("Microsoft YaHei",10),bg="#121d26",fg="#aac3c9",pady=10).pack(anchor="w")
    url=f"http://127.0.0.1:{APP_PORT}/"
    tk.Button(panel,text="打开游戏窗口（浏览器）",font=("Microsoft YaHei",11),
              bg="#9fc69c",fg="#15252a",command=lambda:webbrowser.open(url)).pack(fill="x",pady=8)
    status=tk.Label(panel,text=f"本机服务：{url}    |    数据目录：Work/saves",
                    bg="#121d26",fg="#aac3c9",font=("Microsoft YaHei",9))
    status.pack(anchor="w",pady=5)
    try:
        server=ThreadingHTTPServer(("127.0.0.1",APP_PORT),DesktopHandler)
    except OSError as exc:
        logging.exception("Port conflict")
        messagebox.showerror("启动失败",f"本机端口 {APP_PORT} 无法使用。请关闭其他游戏实例或本地代理服务。\n{exc}")
        window.destroy()
        return 1
    server_thread=threading.Thread(target=server.serve_forever,daemon=True)
    server_thread.start()
    def close():
        server.shutdown()
        server.server_close()
        window.destroy()
    window.protocol("WM_DELETE_WINDOW",close)
    window.after(600,lambda:webbrowser.open(url))
    window.mainloop()
    return 0

if __name__=="__main__":
    try:
        if "--self-test" in sys.argv:
            raise SystemExit(self_test())
        raise SystemExit(main())
    except Exception:
        root=prepare_directories()
        logging.exception("Launcher failed unexpectedly")
        raise
