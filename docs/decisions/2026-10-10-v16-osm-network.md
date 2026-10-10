# ADR-0003：v16以2026-10-01北京OSM原始快照提取可追溯的道路图

**日期**：2026-10-10 · **初始状态**：设计已提交、验收待GitHub Actions运行。

## 已读取的GitHub证据
- 基准提交：`369480b9ade3ee285e7b6b443f4a9867ebdcf609`；已读取`AGENTS.md`、`docs/WORLDBOOK_MASTER.md`、`docs/VERSIONS.md`、`docs/NPC_ROSTER.md`、`docs/SYNC_STATUS.md`、`data/manifest.json`、v14引擎和v15源码/测试。
- 地理原数据 `data/raw/osm/beijing-2026-10-01.osm.pbf`：36,823,056字节，SHA256 `945a6b7967c10dbd40a6e5c59bcae771a9dd44112ee4e37e868e5c544b34762d`；Geofabrik提供，北京2026-10-01 OSM快照于2026-10-02可获得；© OpenStreetMap contributors，ODbL 1.0。
- pyosmium(SimpleHandler,apply_file,locations=True)依据https://docs.osmcode.org/pyosmium/latest/reference/Handler-Processing/；pip依赖固定`osmium==4.3.1`。
- OSM通行标签及单行路语义依据 https://wiki.openstreetmap.org/wiki/Key:access、https://wiki.openstreetmap.org/wiki/Oneway 、https://wiki.openstreetmap.org/wiki/Restriction 。

## 候选方案
A. 直接在虚构坐标网络上完成导航：速度快但不能满足用户全量真实地图数据要求。
B. 读仓库真实PBF、校验SHA、提取来源可追溯的局部OSM图（选用）；附加仅S级速度估计与保守条件判断。
C. 直接声称OSM包含完整实时路况与真实地点交通时间（拒绝；不符合现实与证据）。

## 取舍与边界
- 优先提取前礼务村OSM地名节点，缺失则北小营镇，再顺义市区等；必须返回实际匹配地名和OSM ID。不能捏造前礼务村中心精确坐标。
- 小范围图适合单元测试、地方空间约束；它不是北京全域导航。
- 不计算合法性完备的驾驶路线（缺失relation转向限制、barrier、conditional、本地法规等）。仅产生无法当作真实导航的候选线路。
- 机动车与步行使用不同有向边；显式私有/禁行道路拒绝、步道禁止机动车、典型单行只作用于车辆。
- 维持正式存档原始SHA256，任何测试不能给玩家或NPC指定家庭住址与已经发生的出行。
- 世界书与生成工件、测试均通过GitHub实际提交；产出附带数据授权与缺口清单。

## 验收标准
1. 用 `data/manifest.json`验证PBF真实字节与SHA256。
2. 在GitHub Actions从原始PBF生成真实OSM拓扑图JSON，输出锚点等级与名字；图有正数路网节点、有向步行及机动车边、几何距离和完整来源标签。
3. v14+v15总32项回归不退化；v16不少于18项测试通过，包含单行、私有访问、无路、时间与位置不瞬移、官方冻结不变。
4. 保存图文件、示例路线、时间假设、模拟事件链、校验报告和ZIP；仓库核验存在并有提交SHA。
5. 若锚点不是前礼务村，应明确说明具体提取区域，不伪造匹配成功。
