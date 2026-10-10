# 地球：现实人生 · Earth Realism Worldbook

> 当前版本：**v14.0** · 完全现实社会模拟世界书 · 冻结基准：2026-10-09

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
| v2—v14版本与内容保真 | [docs/VERSIONS.md](docs/VERSIONS.md) |
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

已建立行政地理、道路网络/地图、地理编码、公交地铁、宏观经济、商品住房、劳动就业、法律政策、教育医疗、气象、国际贸易与金融等来源索引。**目录表示已找到入口，不代表已将全部路网和经济数据库抓取到仓库。**实际使用前须核实来源有效时间、授权、坐标系、数据口径及采集日期。

本仓库是公开仓库：不上传真实私人身份资料、密钥、病历和未经公开的现实居民信息。

## 后续维护

后续每次通过ChatGPT建设本世界书，将优先在当前会话中使用连接的GitHub提交相关变更，并在报告中附上版本和提交结果。此约定**不是**后台自动监视；没有当前会话或GitHub连接时，新内容不会凭空写入仓库。
