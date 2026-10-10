# ADR-v32 路网障碍节点与出行不确定性约束

- **基线**：已读取GitHub最新v26世界状态及v27-v30归档和`data/derived/manifest_v27_30.json`；在此基础上继续，不从对话想象新历史。
- **问题**：OSM路网中的gate、bollard、barrier等对象会影响通行；在缺少实际开放状态时，本层保守标记而非宣称‘道路可达’。
- **方案**：提取真实北京OSM PBF中的barrier节点，仅将与v16局部路网共享OSM节点ID的条目纳入路由候选约束。
- **约束与反例**：门、道闸、隔离柱等障碍物须按步行/驾车分别评估；标签存在不一定代表永久关闭。 此外保留用户指定的2026-10-09冻结时间、31名NPC与玩家不存在事实。
- **外部依据**：OSM barriers and mode-specific passage https://wiki.openstreetmap.org/wiki/Key:barrier；bollard foot access https://wiki.openstreetmap.org/wiki/Tag:barrier%3Dbollard。
- **证据等级**：OSM众包R来源不是现实机构许可；个人财务/学校容量/U不得补全，S级情景不升级成正式事件。
- **验收门槛**：GitHub Actions需验证源PBF SHA256、实际产出与独立测试，再提交派生清单和完整测试；CI未完成前状态PENDING。
