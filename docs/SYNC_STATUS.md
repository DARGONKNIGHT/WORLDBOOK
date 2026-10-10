# GitHub同步状态（2026-10-10）

## 已完成
- [x] 主世界书、版本索引、31名虚构NPC和同步政策
- [x] v2—v12 各章节的对话整理版（**不是原始聊天逐字备份**）
- [x] v13 完整核心文本：JSON状态、Python校验器、审计报告与校验记录
- [x] v14 引擎、测试与情景生成源码、正式冻结副本、结果摘要、完整30天事件日志及最终状态
- [x] 仓库生成的两个可下载ZIP：[v13](../artifacts/earth_realism_v13_bundle.zip)、[v14](../artifacts/earth_realism_v14_bundle.zip)
- [x] 可重复运行的打包脚本：[scripts/build_archives.py](../scripts/build_archives.py)
- [x] GitHub Actions自动测试与归档工作流：[build-worldbook.yml](../.github/workflows/build-worldbook.yml)
- [x] 43项资源索引：[sources/catalog.json](../sources/catalog.json)，含地图、路网、经济、住房、交通、医疗、教育、法律等

## 保真与限制
- v13/v14 GitHub ZIP为**从仓库内容重新生成的归档**，并非聊天中原ZIP文件的逐字节复制；ZIP文件大小、元数据与SHA256可能不同。核心文本已从聊天附件转录，v14完整30日日志由原沙盒代码重新生成。
- 官方游戏世界日期2026-10-09，具体时刻未设，玩家未创建，历史空；所有沙盒事件不属于正式历史。
- 43项来源仍以**索引**方式维护；其中Geofabrik北京2026-10-01 OSM PBF和World Bank中国4个指标已经以5份真实原始字节文件存入GitHub并用SHA-256校验。其他来源大多未实际入库，不应误称为全量。
- 早期v2—v12当前为整理稿；若需要逐字聊天存档，请另行从对话导出原文并校对。
- **同步是会话内提交操作**，不是ChatGPT在无人交互时自动监测或后台提交。Github Actions仅在已入库代码变化时执行测试/打包，并不会自动获得ChatGPT新生成的章节。

## 当前测试
GitHub Actions工作流： https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38036402157 （状态：成功）。

## 2026-10-10 实际新增数据
- [x] [36,823,056字节北京2026-10-01 OSM原始数据](../data/raw/osm/beijing-2026-10-01.osm.pbf)，© OpenStreetMap contributors，ODbL 1.0
- [x] [四份中国2020—2025 World Bank年度指标原始JSON](../data/raw/worldbank/)
- [x] [5份文件的下载来源、字节数和SHA256清单](../data/manifest.json)
- [x] [GitHub-first工作协议](../AGENTS.md)、[公开的设计决策记录](decisions/)、[缺口台账](FULL_DATA_GAP_REGISTER.md)
- [x] [自动数据校验与决策日志要求](../.github/workflows/governance.yml)
- [x] [自动采集运行成功](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38037144842)，实际数据提交 `2e8954a04c388f3d3186510586e50cec39645181`
- [ ] v2—v12聊天原文逐字存档；需要原始导出校对，现有章节仍是摘要
- [ ] 其余地图数据、北京市完整统计、学校医疗/住房/实时交通原始数据及许可审计

**数据采集成功并不意味着现实地球“全量数据”已入库**。统计数据首次发布日期仍需核查；真实个人信息不得写入公开仓库。

## v15.0自主决策与日程调度（2026-10-10）
- [x] [v15规则](../worldbook/v15.md)、[规划器](../artifacts/v15/planner_v15.py)、[18项新测试](../artifacts/v15/test_v15.py)
- [x] [决策日志](../artifacts/v15/sandbox_v15_decisions.json)、[执行日志](../artifacts/v15/sandbox_v15_journal.json)、[汇总JSON](../artifacts/v15/sandbox_v15_summary.json)和[可再建ZIP](../artifacts/earth_realism_v15_bundle.zip)
- [x] [GitHub Actions验收](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38037749491)：旧版14/14＋新版18/18，合计32项测试通过
- [x] S级沙盒18次候选，9次预排、9次拒绝或不作为；底层执行13条，转账0笔，正式历史0条
- [ ] 31名NPC的完整实际日程/个人财务/认知和长期行为校准未完成；原v2-v12仍缺逐字原文

此处的“自主”指人工明确给定需求和候选情况下的有限决策，不代表智能体可以独立发现并完整处理所有现实生活需求。正式游戏继续冻结。

## v16.0 · OSM真实地理数据衍生（2026-10-10）
- [x] [真实派生图](../artifacts/v16/osm_graph_sample.json)、[图统计](../artifacts/v16/osm_graph_report.json)，OSM前礼务村地点节点ID 6410843713，2.8km范围，1,244节点、步行边2,018、机动车边1,905
- [x] [Python提取器](../artifacts/v16/extract_v16.py)、[保守路线算法](../artifacts/v16/network_v16.py)、[18项v16测试](../artifacts/v16/test_v16.py)、[沙盒出行日志](../artifacts/v16/route_sandbox_journal.json)及[ZIP](../artifacts/earth_realism_v16_bundle.zip)
- [x] [派生数据来源、生成脚本、SHA256与ODbL许可](../data/derived/manifest.json)
- [x] [GitHub v14/15/16测试50/50通过](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38038500429)
- [ ] 真实驾驶路线仍缺转向限制、barrier、动态路况、实时速度/ETA、全北京联网拓扑；不是实际导航工具
- [ ] v2—v12逐字对话原文仍缺失，不得冒充全量

正式游戏2026-10-09仍冻结，玩家未创建，NPC实际出行历史零条。


## v17—v26连续十层验收（2026-10-10）
- [x] [十份完整世界书](../worldbook/)与[十份公开决策记录](decisions/)已写入GitHub
- [x] [10个有限过程模型](../artifacts/v17_26/realism_layers.py)、[45项新测试](../artifacts/v17_26/test_realism_layers.py)、[12条S级模拟事件](../artifacts/v17_26/simulation_evidence.json)
- [x] [OSM节点公交相关清单40项](../artifacts/v17_26/osm_transit_nodes.json)、[节点型公共/商业POI 1项](../artifacts/v17_26/osm_civic_poi_nodes.json)及[来源与SHA256](../data/derived/manifest_v17_26.json)
- [x] [十层归档ZIP](../artifacts/earth_realism_v17_to_v26_bundle.zip)；[CI实际95/95项通过](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38039469845)
- [ ] 2026北京实际公交班次/GTFS、城市完整POI/开放服务、真实社保税费与合法机构档案仍缺；现有示例为S等级
- [ ] v2—v12原始聊天逐字全文仍未补齐，当前为整理摘要，不能冒充完整逐字档案

本轮达到用户上限10层，终止于v26；正式游戏仍冻结于2026-10-09，未创建玩家、正式事件历史为空。

## v27—v33增量已同步（2026-10-10）

- [x] [世界书v27—v33](../worldbook/)与逐层设计证据、取舍记录[ADRs](decisions/)；
- [x] [OSM闭合way样本11条](../artifacts/v27_30/osm_public_way_features.json)、[局部node-via restriction候选0条与过滤统计](../artifacts/v27_30/turn_restrictions_report.json)；
- [x] [OSM multipolygon区域relation本地0个、全北京候选42个](../artifacts/v31_33/area_report.json)、[本地barrier节点3项](../artifacts/v31_33/osm_barrier_nodes.json)；
- [x] [v27—v30数据来源、SHA256](../data/derived/manifest_v27_30.json)、[v31—v33数据来源、SHA256](../data/derived/manifest_v31_33.json)；
- [x] [v29 GTFS日历源码](../artifacts/v27_30/calendar_v29.py)，尚无北京真实2026公交班次；
- [x] [完整4层ZIP](../artifacts/earth_realism_v27_to_v30_bundle.zip)、[完整3层ZIP](../artifacts/earth_realism_v31_to_v33_bundle.zip)、[v33阶段审计](../artifacts/v31_33/milestone_v33.json)；
- [x] [实际CI 117项](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38040692649)及[累计130项通过](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38040928956)。
- [ ] 原始v2—v12聊天全文、当时真实公交时刻、统计历史发布版本、具体机构容量、法律通行资格及私人NPC财务仍未知或缺合法来源。

当前版本v33.0。这次自动迭代到达**数据准入暂停点**，没有宣称所有后续层均已穷尽。正式游戏钟点未确定，玩家未创建，事件历史为空。
