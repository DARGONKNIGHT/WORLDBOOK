# ADR-v28 OSM转向限制与带历史道路的保守路由

- **GitHub基线**：2026-10-10主分支提交`9f44a006a7fe974e4b88e54b84a8df57ecc4ee8d`，已读取v26主档案、完整资源缺口清单、数据manifest与v16—v26过程源码。
- **问题**：弥补v16只依赖有向路段、可能允许OSM明确禁止的转向这一缺口；不宣称已达正式导航或交通法规全覆盖。
- **采用方案**：只解析type=restriction且有且仅有1个from-way、1个via-node、1个to-way的本地OSM关系记录。
- **其他方案与拒绝理由**：立即把OSM站点/设施标注当作真实运营数据会引入伪事实；缺来源的交通时间和历史经济价格只能保留U；不得编造私人生活。
- **程序与数据**：`artifacts/v27_30/turns_v28.py`，共享测试`artifacts/v27_30/test_v27_30.py`；实际字节必须由GitHub Actions写回并核对SHA256。
- **资料依据**：OSM restriction from-via-to relation: https://wiki.openstreetmap.org/wiki/Relation:restriction ; https://wiki.openstreetmap.org/wiki/Key:restriction
- **验收状态**：待GitHub CI实际运行；正式世界仍冻结。

## 已运行的GitHub验收
- 原95项跨版本测试回归＋本批22项新测试均通过；输出测试日志见artifacts/v27_30/test_run_v27_30.txt。
- 正式冻结状态SHA256: 75d97ad9960e195f1ce21f23424c784682e5f635456277647166a66829299087，游戏事件新增0。
- v27实际OSM way数量: 11；v28受支持的本地node-via限制: 0。这并不等于完整POI/转向限制覆盖。
- 缺少真实历史GTFS、地方实际交通法规、NPC财务/历史全文等资料时保持U，不从沙盒反填真实历史。
