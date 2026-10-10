# 真实OSM派生路网索引

本目录保存已入库的派生数据元信息，实际图文件位于[artifacts/v16/osm_graph_sample.json](../../artifacts/v16/osm_graph_sample.json)。[manifest.json](manifest.json)提供原始PBF SHA256、图SHA256、生成源码、依赖、OSM地点节点、道路范围、质量边界和许可。可以用[extract_v16.py](../../artifacts/v16/extract_v16.py)从仓库[真实PBF](../raw/osm/beijing-2026-10-01.osm.pbf)重新生成。

该图是前礼务村OSM地点节点周围2.8km实验性有向图，**不能当作真实道路导航或旅行时间**；尚未实现转向限制、部分障碍、动态限制与实时交通。© OpenStreetMap contributors, ODbL 1.0。

## 衍生几何后续批次
- [v27-v30](manifest_v27_30.json) 包括公共设施ways、有限转向限制关系、无北京真实GTFS的明确U标记。
- [v31-v33](manifest_v31_33.json) 包括公共设施relation面积对象与道路障碍节点、真实来源和SHA256。
- [v33证据收束](../../artifacts/v31_33/milestone_v33.json)仍标记部分技术可扩展、历史GTFS和法律资料缺失，绝非“全部现实数据齐备”。

**几何对象计数不能直接加总成现实设施数量**：同一设施可能被OSM node、way、relation重复表示。
