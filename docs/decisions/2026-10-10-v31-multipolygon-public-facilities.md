# ADR-v31 OSM多边形关系与公共设施轮廓

- **基线**：已读取GitHub最新v26世界状态及v27-v30归档和`data/derived/manifest_v27_30.json`；在此基础上继续，不从对话想象新历史。
- **问题**：以PyOsmium的面积组装器补足v27未处理的多边形relation，避免把OSM way与设施实际数量混为一谈。
- **方案**：读取GitHub保存的2026-10-01北京PBF并校验SHA256；由PyOsmium两遍扫描组装areas，只对来自relation的公共服务和商业设施采样。
- **约束与反例**：真实公共设施种类采取明确白名单，不抓取私人住宅或具体住户；每个relation保存osm_id、类别、外环数量、包围框和粗略代表点。 此外保留用户指定的2026-10-09冻结时间、31名NPC与玩家不存在事实。
- **外部依据**：PyOsmium Working with Geometries: https://docs.osmcode.org/pyosmium/latest/user_manual/03-Working-with-Geometries/；OSM © contributors ODbL。
- **证据等级**：OSM众包R来源不是现实机构许可；个人财务/学校容量/U不得补全，S级情景不升级成正式事件。
- **验收门槛**：GitHub Actions需验证源PBF SHA256、实际产出与独立测试，再提交派生清单和完整测试；CI未完成前状态PENDING。

## GitHub Actions实际验收
- 旧版v14—v30 117项测试回归＋v31—v33新增13项测试，共130项通过。
- 本地OSM relation公共多边形数量：0；局部路网上实际带barrier标签节点数量：3。
- 正式世界SHA256：75d97ad9960e195f1ce21f23424c784682e5f635456277647166a66829299087；正式历史0条。
- 源于单个2026-10-01 OSM众包快照；现实交通通行、学校医疗容量和私人生活仍未验证。
