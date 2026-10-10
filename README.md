# 地球：现实人生 · Earth Realism Worldbook

> 当前版本：**v33.0** · 完全现实社会模拟世界书 · 冻结基准：2026-10-09

本仓库归档从真实地球世界背景（v2）到中国、北京、顺义区北小营镇前礼务村观察样本以及全国/全球社会联动的世界书。人物、家庭、企业、公共机构均具有独立目标、限制和信息边界；不引入超自然、不预设主角特殊待遇。

## 核心保护
- **正式游戏尚未开始**，玩家角色、住所、职业、家庭、存款均未创建；游戏钟点未确定，正式历史为空。
- 北京为当前高精度城市；**前礼务村只是随机观察样本，不是玩家住所**。
- 31个NPC（15核心+16候选）全部为虚构S级人物，**不冒充真实居民**。
- 事实等级：R=核实的现实事实、S=虚构模拟、U=未知/未核实。
- 沙盒不会修改正式世界；没有离线持续运行的完整现实数字孪生。

## 导航

| 内容 | 链接 |
|---|---|
| 世界书总纲 | [docs/WORLDBOOK_MASTER.md](docs/WORLDBOOK_MASTER.md) |
| v2—v33版本与内容保真 | [docs/VERSIONS.md](docs/VERSIONS.md) |
| v2—v12整理版章节 | [worldbook/](worldbook/) |
| 31名模拟NPC索引 | [docs/NPC_ROSTER.md](docs/NPC_ROSTER.md) |
| v13审计资料 | [artifacts/v13/](artifacts/v13/) |
| v13可下载ZIP（仓库重建） | [earth_realism_v13_bundle.zip](artifacts/earth_realism_v13_bundle.zip) |
| v14沙盒引擎、测试和完整日志 | [artifacts/v14/](artifacts/v14/) |
| v14可下载ZIP（仓库重建） | [earth_realism_v14_bundle.zip](artifacts/earth_realism_v14_bundle.zip) |
| **43项现实资源总索引** | [sources/README.md](sources/README.md) |
| 机器可读来源目录 | [sources/catalog.json](sources/catalog.json) |
| 已引用事实/数据用途账本 | [sources/usage_ledger.csv](sources/usage_ledger.csv) |
| 数据、地图许可与时间快照政策 | [sources/DATA_GOVERNANCE.md](sources/DATA_GOVERNANCE.md) |
| 实际GitHub同步状态 | [docs/SYNC_STATUS.md](docs/SYNC_STATUS.md) |
| 今后交互中同步规范 | [docs/SYNC_POLICY.md](docs/SYNC_POLICY.md) |

## v13/v14自动测试和归档

在仓库根目录执行：

```bash
python scripts/build_archives.py
```

该脚本运行v14的14项校验，重新生成30日沙盒完整事件日志，并生成v13与v14 ZIP。GitHub Actions [自动打包工作流](.github/workflows/build-worldbook.yml) 已实际成功运行过。

**生成ZIP不是原聊天附件的逐字节备份**，但包含仓库中的源码、配置和重建的数据。v2—v12的当前章节是根据对话进行的内容重构，不是假称逐字录入的聊天导出。

## 现实资源使用

已建立43项来源索引，**并已实际保存并校验第一批5份原始数据**：[北京2026-10-01 OSM PBF](data/raw/osm/beijing-2026-10-01.osm.pbf)（36,823,056字节）及[四份2020—2025年中国World Bank API原始JSON](data/raw/worldbank/)，完整来源/哈希见[data/manifest.json](data/manifest.json)。北京ODbL地理数据不是实时可驾驶路网，四项全国指标不等于北京市全量统计。其他资源仍以索引为主，**尚不构成全量数据覆盖**。实际使用前须核实来源有效时间、授权、坐标系、数据口径及采集日期。

本仓库是公开仓库：不上传真实私人身份资料、密钥、病历和未经公开的现实居民信息。

## 后续维护

后续每次通过ChatGPT建设本世界书，将优先在当前会话中使用连接的GitHub提交相关变更，并在报告中附上版本和提交结果。此约定**不是**后台自动监视；没有当前会话或GitHub连接时，新内容不会凭空写入仓库。


## GitHub优先的研发和归档

请先阅读[AGENTS.md](AGENTS.md)和[全量数据缺口清单](docs/FULL_DATA_GAP_REGISTER.md)。每次建设先读取仓库已有档案及最后提交，再以可审计的[设计决策记录](docs/decisions/)保存证据、取舍、变更和测试。模型内部未输出的推理过程不是可导出材料；可核验的公开分析与结论必须入库。

实际数据快照可以通过[GitHub Actions采集任务](.github/workflows/ingest-open-data.yml)和校验器重复获取；不属于已有许可的官方地图影像或真实私密记录不能直接复制入公开仓库。

## v15.0 NPC自主调度（沙盒）

[v15规则](worldbook/v15.md) · [决策引擎](artifacts/v15/planner_v15.py) · [18项测试](artifacts/v15/test_v15.py) · [决策记录](artifacts/v15/sandbox_v15_decisions.json) · [执行日志](artifacts/v15/sandbox_v15_journal.json) · [汇总](artifacts/v15/sandbox_v15_summary.json) · [v15 ZIP](artifacts/earth_realism_v15_bundle.zip) · [公开设计依据](docs/decisions/2026-10-10-v15-limited-agent-scheduling.md)

沿用v14事件引擎新增候选评分、承诺优先、信息先决、日程与位置预约、技能/未知资金约束和合理不作为。原v14 14项回归测试与v15 18项测试全部通过；18个候选9项进入队列、9项拒绝或不作为，最终13条实际执行事件，无资金付款。以上仅为显式S级沙盒输入，不代表31名NPC真实全天生活或正式历史发生变化。

## v16：前礼务村真实OSM路网实验图

[世界书规则](worldbook/v16.md) · [提取器](artifacts/v16/extract_v16.py) · [路由引擎](artifacts/v16/network_v16.py) · [实际派生路网](artifacts/v16/osm_graph_sample.json) · [详细提取报告](artifacts/v16/osm_graph_report.json) · [独立沙盒日志](artifacts/v16/route_sandbox_journal.json) · [可再建ZIP](artifacts/earth_realism_v16_bundle.zip) · [数据来源/哈希/许可清单](data/derived/manifest.json) · [GitHub测试](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38038500429)。

OSM实际识别前礼务村地点节点6410843713（N40.1880155 E116.7077492）；2.8公里范围实验图包含1,244节点与3,923条有向边。v14/v15/v16自动测试50/50通过。地图几何不等于真实可通行导航：未处理转向限制、障碍、动态交通，耗时只是S级假设。地图中心不是玩家或NPC住址，正式世界没有推进。

## v17—v26：连续10层已完成、GitHub验证

[公共交通v17](worldbook/v17.md) · [地理设施v18](worldbook/v18.md) · [家庭住房v19](worldbook/v19.md) · [企业商业v20](worldbook/v20.md) · [劳动工资v21](worldbook/v21.md) · [教育医疗v22](worldbook/v22.md) · [行政法律v23](worldbook/v23.md) · [信息传播v24](worldbook/v24.md) · [宏观经济v25](worldbook/v25.md) · [综合审计v26](worldbook/v26.md)。

[十层源码](artifacts/v17_26/realism_layers.py)、[45项新测试](artifacts/v17_26/test_realism_layers.py)、[12条S级审计记录](artifacts/v17_26/simulation_evidence.json)、[完整ZIP](artifacts/earth_realism_v17_to_v26_bundle.zip)、[真实OSM站点节点数据](artifacts/v17_26/osm_transit_nodes.json)、[设施节点数据](artifacts/v17_26/osm_civic_poi_nodes.json)、[SHA256数据血缘](data/derived/manifest_v17_26.json)、[GitHub Actions 95/95成功验收](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38039469845)。

本次OSM 2026-10-01前礼务村2.8km节点样本：交通相关节点40个，设施/商业相关节点1个（**只计OSM nodes，不包括areas或ways**）。这不是公交班次、实时导航、学校或医院合法资质数据；其他社会过程为明确的S级模拟，不代表31名NPC实际经历。

## v27—v33：实际开放地理对象与来源准入（本轮暂停点）

[公共设施way v27](worldbook/v27.md) · [受限转向关系 v28](worldbook/v28.md) · [GTFS日历 v29](worldbook/v29.md) · [资料缺口审计 v30](worldbook/v30.md) · [OSM多边形关系 v31](worldbook/v31.md) · [道路障碍 v32](worldbook/v32.md) · [证据门槛 v33](worldbook/v33.md)。

- 真实2026-10-01北京OSM PBF局部2.8公里样本：v27额外发现**11个带公共类标签的闭合ways**，v28在现有裁切图中**0个可直接采用的受限简式node-via转向记录**；[源数据+SHA256](data/derived/manifest_v27_30.json)。
- v31完成OSM multipolygon area组装：全北京PBF公共类别初筛42个、本地最终0个；v32定位**3个位于局部OSM路网的barrier标签节点**，均无经核实的实时通行状态；[来源和文件哈希](data/derived/manifest_v31_33.json)。
- v29 GTFS服务日例外和跨日时刻支持，只在明确构造的S级时刻表上测试，没有真实北京2026历史车次。
- v33保留[机器可读证据缺口](artifacts/v31_33/milestone_v33.json)、v2—v12原文缺失、法律/经济版本与个人状态未知。不宣称全地球数字孪生完成。
- [v27—v30源码和日志](artifacts/v27_30/) · [v31—v33源码和日志](artifacts/v31_33/) · [v27—v30 ZIP](artifacts/earth_realism_v27_to_v30_bundle.zip) · [v31—v33 ZIP](artifacts/earth_realism_v31_to_v33_bundle.zip)。
- [117项自动验收](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38040692649)及[后续130项回归全部通过](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38040928956)。

**当前停止原因**：新增可信真实生活事件需要可以合法使用、时点明确的真实GTFS、经济指标历史发布版本、权威服务/法律资料或用户的原始聊天导出；进一步建设可继续，但不应为自动延长版本号而伪造资料。正式游戏继续冻结。


## 可直接游玩的浏览器游戏 · 独立试玩层

新增 [《地球：现实人生》离线单文件](game/earth-realism.html)（在GitHub文件页面下载后双击即可玩）、[游戏启动与操作说明](game/README.md)、[多文件源码](game/)、[自动化测试](game/tests/engine.test.cjs)、[自动测试](.github/workflows/game-tests.yml)及[手动Pages发布工作流](.github/workflows/game-pages.yml)。Pages实际启用和部署成功后可从 https://dargonknight.github.io/WORLDBOOK/ 访问；如果Pages尚未启用，本地单文件不受影响。

当前已支持玩家自行创建角色、北京区际出行、工作/休息/等待、31名虚构NPC有限后台活动、消息发送/送达、浏览器存档与JSON导入导出。**本游戏是S级独立分支**，不是全量真实地球模拟、不是v14 Python沙盒的全模块网页移植；世界书v33与冻结正式世界未被修改。设计决策记录见 [ADR](docs/decisions/2026-10-10-playable-offline-game.md)。
