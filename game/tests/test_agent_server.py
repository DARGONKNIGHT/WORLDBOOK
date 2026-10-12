"""Local Ollama proxy contract tests; no Ollama installation or network access."""
import http.client
import importlib.util
import io
import json
from pathlib import Path
import threading
import unittest
from unittest import mock
from http.server import ThreadingHTTPServer

MODULE=Path(__file__).resolve().parents[1]/"agent_server.py"
spec=importlib.util.spec_from_file_location("agent_server_under_test",MODULE)
server=importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv=ThreadingHTTPServer(("127.0.0.1",0),server.Handler)
        cls.thread=threading.Thread(target=cls.srv.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.thread.join(timeout=2)
    def request(self,path,body=None,headers=None):
        conn=http.client.HTTPConnection("127.0.0.1",self.srv.server_port,timeout=4)
        data=json.dumps(body).encode("utf-8") if body is not None else None
        conn.request("POST" if data else "GET",path,data,
          headers or ({"Content-Type":"application/json"} if data else {}))
        res=conn.getresponse()
        obj=json.loads(res.read())
        status=res.status
        conn.close()
        return status,obj
    def payload(self):
        return {"npc_id":"P003","name":"陈雨","source_grade":"S",
          "known_messages":[],"candidates":[{"id":"continue_work","label":"继续工作"},{"id":"short_break","label":"休息"}]}
    def test_health(self):
        status,result=self.request("/api/health")
        self.assertEqual(status,200)
        self.assertEqual(result["provider"],"ollama")
        self.assertEqual(result["server"],"local")
    def test_model_allowed_choice(self):
        fake={"message":{"content":json.dumps({"choice":"continue_work","reason":"需要完成工作事务"})}}
        with mock.patch.object(server.urllib.request,"urlopen",return_value=io.BytesIO(json.dumps(fake).encode())):
            status,result=self.request("/api/ai/decide",self.payload())
        self.assertEqual(status,200)
        self.assertEqual(result["choice"],"continue_work")
        self.assertEqual(result["provider"],"ollama")
    def test_model_invalid_choice_rejected(self):
        fake={"message":{"content":json.dumps({"choice":"withdraw_money","reason":"拿走现金"})}}
        with mock.patch.object(server.urllib.request,"urlopen",return_value=io.BytesIO(json.dumps(fake).encode())):
            status,result=self.request("/api/ai/decide",self.payload())
        self.assertEqual(status,422)
        self.assertNotIn("choice",result)
    def test_cross_origin_blocked(self):
        headers={"Content-Type":"application/json","Origin":"https://evil.example"}
        status,_=self.request("/api/ai/decide",self.payload(),headers)
        self.assertEqual(status,403)
    def test_nons_grade_context_blocked(self):
        data=self.payload();data["source_grade"]="R"
        status,_=self.request("/api/ai/decide",data)
        self.assertEqual(status,422)

if __name__=="__main__":
    unittest.main()
