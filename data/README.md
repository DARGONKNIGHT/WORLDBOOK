# 世界数据仓库（实际数据，与来源索引分离）

此处`raw/`存储已取得且许可允许再分发的**真实原始字节**，`manifest.json`登记SHA256、文件大小、获取时间、数据版本、源地址、许可与质量检查；`derived/`用于可重建的派生数据。不要将`sources/catalog.json`中的链接误认为已经入库。

第一批选用**历史固定版本**`beijing-261001.osm.pbf`（2026-10-01北京OSM提取，约37MB），不使用“latest”作为2026-10-09游戏背景。数据来自Geofabrik、© OpenStreetMap contributors，按ODbL 1.0提供，使用时署名并遵守衍生数据库义务。它不是实时可驾驶路网；不能从静态几何直接推算具体时刻的旅行时间。

同时获取World Bank中国2020—2025年度人口、GDP、CPI涨幅、模型化失业率API响应原文。**统计年份不等于正式发布日期**；2025数据可能后续修订或在2026-10-09之后首次公布，不能直接回填游戏历史。

运行：
```bash
python scripts/ingest_open_data.py --osm --wdi
python scripts/check_data_manifest.py
```

GitHub Actions可以从公网抓取数据并提交实际字节。如果工作流失败，仍只算采集计划；必须核实`data/raw/`真实存在与哈希一致才算已保存。

**全量的边界**：世界书全文及项目关联数据、许可允许的地图/经济快照和所有可复现派生结果。全球全部原始地图、付费实时交通、未经授权地图影像、真实私人银行/病历等不可能也不应该无条件纳入公开Git；大型文件采用Git LFS、Release或合法对象存储，同时在本仓库留有可验证的完整清单。


## v17—v26实际衍生原始节点数据

真实字节来源仍为2026-10-01北京Geofabrik OSM PBF（在`data/raw/osm/`）。新派生文件`artifacts/v17_26/osm_transit_nodes.json`（40个公交/站台相关OSM节点）及`artifacts/v17_26/osm_civic_poi_nodes.json`（1个公共服务/商业相关OSM节点）已在GitHub保存，[manifest](derived/manifest_v17_26.json)含原始SHA、派生SHA和时间范围。仅含OSM node标签而非全体way/area设施，不提供实际公交班次、营业时间、机构资格、私人信息。© OpenStreetMap contributors，ODbL 1.0。

## v27—v33新增已验证OSM派生对象

- [v27公共服务/商业ways原始对象11条](../artifacts/v27_30/osm_public_way_features.json)，闭合ways 11、线状0；实际数据来自固定2026-10-01北京PBF。
- [v28本地区可直接应用的node-via限制关系0项](../artifacts/v27_30/turn_restrictions_local.json)：缺失/复杂关系排除计数完整保存在报告。
- [v31公共多边形relation筛选0项](../artifacts/v31_33/osm_public_multipolygons.json)，全北京PBF符合标签初筛的已组装候选42项；0不是公共服务不存在的证明。
- [v32局部有来源的路网障碍节点3项](../artifacts/v31_33/osm_barrier_nodes.json)，其通过许可/当前状态未核实。
- [派生manifest v27-v30](derived/manifest_v27_30.json)、[派生manifest v31-v33](derived/manifest_v31_33.json)记录真实字节量、SHA-256、来源与筛选边界。

Geofabrik与OSM原始数据署名遵守 © OpenStreetMap contributors，ODbL 1.0。此处道路或公共设施标签不代表行政许可、法律通行权、地面实时状态或准确到达时间。
