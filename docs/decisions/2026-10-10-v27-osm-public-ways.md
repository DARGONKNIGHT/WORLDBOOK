# ADR-v27 公共设施道路Way与闭合几何覆盖

- **GitHub基线**：2026-10-10主分支提交`9f44a006a7fe974e4b88e54b84a8df57ecc4ee8d`，已读取v26主档案、完整资源缺口清单、数据manifest与v16—v26过程源码。
- **问题**：将此前只能识别OSM node的设施目录扩展到真实OSM way对象（直线/闭合轮廓），避免把“当地只有一个设施节点”误读成“当地只有一家设施”。
- **采用方案**：从GitHub中实际保存的2026-10-01北京OSM PBF读取公共服务、公交设施及生活商业的way标签；入库前再次核验PBF来源和SHA256。
- **其他方案与拒绝理由**：立即把OSM站点/设施标注当作真实运营数据会引入伪事实；缺来源的交通时间和历史经济价格只能保留U；不得编造私人生活。
- **程序与数据**：`artifacts/v27_30/ways_v27.py`，共享测试`artifacts/v27_30/test_v27_30.py`；实际字节必须由GitHub Actions写回并核对SHA256。
- **资料依据**：PyOsmium SimpleHandler way + locations=true: https://docs.osmcode.org/pyosmium/latest/reference/Handler-Processing/；© OpenStreetMap contributors/Geofabrik。
- **验收状态**：待GitHub CI实际运行；正式世界仍冻结。
