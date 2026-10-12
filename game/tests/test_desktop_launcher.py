"""Desktop executable's save API contract. Run on Windows builder and compatible Python."""
import http.client
import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock
import desktop_launcher as L

class DesktopSaveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.folder=Path(self.temp.name)
        self.patch=mock.patch.object(L,"app_root",return_value=self.folder)
        self.patch.start()
        self.server=ThreadingHTTPServer(("127.0.0.1",0),L.DesktopHandler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close()
        self.thread.join(timeout=2)
        self.patch.stop()
        self.temp.cleanup()
    def ask(self,method,path,content=None,origin=None):
        conn=http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=3)
        headers={}
        if content is not None:headers["Content-Type"]="application/json"
        if origin:headers["Origin"]=origin
        data=json.dumps(content).encode("utf-8") if content is not None else None
        conn.request(method,path,data,headers)
        response=conn.getresponse()
        status=response.status
        content=response.read()
        conn.close()
        return status,json.loads(content)
    def test_create_restore_delete_file_inside_exe_root(self):
        state={"schema":2,"mode":"S_INDEPENDENT_PLAYTHROUGH","player":{"name":"Test"}}
        status,result=self.ask("POST","/api/save",state)
        self.assertEqual(status,200)
        self.assertTrue(result["saved"])
        path=self.folder/"saves"/"autoplay.json"
        self.assertTrue(path.is_file())
        self.assertFalse((self.folder.parent/"autoplay.json").exists())
        code,restored=self.ask("GET","/api/save")
        self.assertEqual(code,200)
        self.assertEqual(restored,state)
        code,_=self.ask("DELETE","/api/save")
        self.assertEqual(code,200)
        self.assertFalse(path.exists())
        code,_=self.ask("GET","/api/save")
        self.assertEqual(code,404)
    def test_bad_origin_and_invalid_save_rejected(self):
        state={"mode":"S_INDEPENDENT_PLAYTHROUGH","player":{"name":"Test"}}
        code,_=self.ask("POST","/api/save",state,"https://attacker.example")
        self.assertEqual(code,403)
        self.assertFalse((self.folder/"saves"/"autoplay.json").exists())
        code,_=self.ask("POST","/api/save",{"mode":"invalid","player":{} })
        self.assertEqual(code,422)
        code,_=self.ask("DELETE","/api/save",origin="https://attacker.example")
        self.assertEqual(code,403)
if __name__=="__main__":
    unittest.main()
