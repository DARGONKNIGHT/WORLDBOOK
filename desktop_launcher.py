"""Earth Realism Windows launcher (game 4.0).

PyInstaller --onedir binary is flattened to Work/EarthRealism.exe, with _internal
in the *same* Work directory. No onefile extraction in an external temp folder.

The executable serves bundled HTML/JS locally and opens the default browser.
Ollama is optional and is not bundled into the executable.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox
from http.server import ThreadingHTTPServer

from game.agent_server import Handler

APP_NAME="地球：现实人生"
APP_PORT=8765

def app_root():
    return Path(sys.executable).resolve().parent if getattr(sys,"frozen",False) else Path(__file__).resolve().parent / "Work"

def prepare_directories(root=None):
    root=Path(root or app_root()).resolve()
    for name in ("logs","saves","cache","tmp"):
        (root/name).mkdir(parents=True,exist_ok=True)
    return root

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
    tk.Label(panel,text=APP_NAME+"  v4",font=("Microsoft YaHei",18,"bold"),
             bg="#121d26",fg="#e3eecf").pack(anchor="w")
    tk.Label(panel,text="31名S级自主人物 · 家庭与工作协商 · 本地AI可选",
             font=("Microsoft YaHei",10),bg="#121d26",fg="#aac3c9",pady=10).pack(anchor="w")
    url=f"http://127.0.0.1:{APP_PORT}/"
    tk.Button(panel,text="打开游戏窗口（浏览器）",font=("Microsoft YaHei",11),
              bg="#9fc69c",fg="#15252a",command=lambda:webbrowser.open(url)).pack(fill="x",pady=8)
    status=tk.Label(panel,text=f"本机服务：{url}    |    数据目录：Work/saves",
                    bg="#121d26",fg="#aac3c9",font=("Microsoft YaHei",9))
    status.pack(anchor="w",pady=5)
    try:
        server=ThreadingHTTPServer(("127.0.0.1",APP_PORT),Handler)
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
        raise SystemExit(main())
    except Exception:
        root=prepare_directories()
        logging.exception("Launcher failed unexpectedly")
        raise
