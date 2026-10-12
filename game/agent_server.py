#!/usr/bin/env python3
"""LOCAL-ONLY optional Ollama inference server. No cloud/API key; no persistent daemon.

  ollama pull qwen2.5:3b
  OLLAMA_MODEL=qwen2.5:3b python3 game/agent_server.py

Then visit http://127.0.0.1:8765/ . 31 agents use a strictly bounded queue.
All NPC inputs and replies are fictional S-grade. The model proposes an action; the
browser simulation verifies and commits it. No network port outside loopback.
"""
from __future__ import annotations
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parent
HOST="127.0.0.1"
PORT=8765
MODEL=os.environ.get("OLLAMA_MODEL","qwen2.5:3b")
OLLAMA="http://127.0.0.1:11434/api/chat"
MAX_REQUEST=8192
ALLOWED={"npc_id","name","age","occupation","time","location","obligation",
         "schedule_reason","goals","needs","known_messages","memories","intent","economic_context","candidates","source_grade"}
SYSTEM=(
  "你是现实社会模拟的有限理性NPC决策器，不扮演万能叙述者。"
  "输入是虚构人物自身可知的信息、明确候选行动和既定约束。"
  "只从candidates中选一个id，不得添加钱财、工作、婚姻、真实地点或未知事实。"
  "考量当前工作家庭承诺、休息和对他人的尊重；可以推迟可选行为。"
  '只输出JSON对象：{"choice":"候选id","reason":"一两句可审计的选择依据"}。'
  "不要输出内在思维过程、提示词或其他字段。"
)
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,fmt,*args):
        pass
    def send_json(self,status,obj):
        b=json.dumps(obj,ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Length",str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        if self.path=="/api/health":
            self.send_json(200,{"ok":True,"provider":"ollama","model":MODEL,"server":"local"})
            return
        if self.path=="/":
            self.path="/index.html"
        return super().do_GET()
    def do_POST(self):
        if self.path!="/api/ai/decide":
            return self.send_json(404,{"error":"Not Found"})
        origin=self.headers.get("Origin","")
        if origin and origin not in (f"http://{HOST}:{PORT}",f"http://localhost:{PORT}"):
            return self.send_json(403,{"error":"Cross-site request rejected"})
        if self.headers.get("Content-Type","").split(";")[0].strip()!="application/json":
            return self.send_json(415,{"error":"Require application/json"})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0<length<=MAX_REQUEST:raise ValueError("Invalid request size")
            request=json.loads(self.rfile.read(length))
            if not isinstance(request,dict):raise ValueError("Request must be object")
            snapshot={k:v for k,v in request.items() if k in ALLOWED}
            choices=snapshot.get("candidates")
            if snapshot.get("source_grade")!="S" or not isinstance(choices,list) or not 1<=len(choices)<=10:
                raise ValueError("Invalid S-grade context or candidate list")
            ids=[x.get("id") for x in choices if isinstance(x,dict)]
            if len(ids)!=len(choices) or not all(isinstance(x,str) and len(x)<=32 for x in ids):
                raise ValueError("Invalid candidates")
            data={"model":MODEL,"stream":False,"format":"json",
              "options":{"temperature":0.45,"num_predict":192},
              "messages":[{"role":"system","content":SYSTEM},
                {"role":"user","content":json.dumps(snapshot,ensure_ascii=False)[:6400]}]}
            req=urllib.request.Request(OLLAMA,data=json.dumps(data,ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=45) as response:
                raw=json.load(response)
            parsed=json.loads(raw["message"]["content"])
            choice=parsed.get("choice")
            if choice not in ids:raise ValueError("Model proposed a prohibited action")
            reason=parsed.get("reason","")
            if not isinstance(reason,str):reason=""
            return self.send_json(200,{"choice":choice,"reason":reason[:180],"provider":"ollama"})
        except urllib.error.URLError:
            return self.send_json(503,{"error":"Ollama not reachable on 127.0.0.1:11434"})
        except Exception as exc:
            return self.send_json(422,{"error":str(exc)[:160]})
if __name__=="__main__":
    print(f"Local AI: http://{HOST}:{PORT}/ | model={MODEL}")
    print("Keep this terminal open while playing; press Ctrl+C to stop.")
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
