# ADR · 2026-10-10 · 把世界书制作成离线可游玩的浏览器游戏

## 任务与权威来源
用户要求以云端仓库 DARGONKNIGHT/WORLDBOOK 为源，提供可以直接打开游玩的游戏。修改前核验 main 分支起点提交 11326d059c91850a0d91e15ef9e9c0fc878bb7ce；读取 AGENTS.md、README.md、docs/WORLDBOOK_MASTER.md、docs/VERSIONS.md、docs/NPC_ROSTER.md、docs/SYNC_STATUS.md、data/manifest.json、artifacts/v14/engine_v14.py、原始冻结世界状态与近期提交记录。

- R：仓库存在北京2026-10-01 OSM原始快照，但当前资料不支持全北京市实时导航；现实资料的时效和许可须独立核验。
- S：31名NPC系世界书虚构人物；由玩家输入的初始角色状态、局部偶遇、通信回应、后台活动均为模拟。
- U：玩家尚未创建、正式世界时刻尚未确定、私人财务和NPC精确位置未知；不为正式存档补齐。

## 技术选择
选择纯前端独立静态单机页，不依赖云服务器、密钥、外部字体/CDN。两种分发：game/index.html + 同目录资源，及合并后的 game/earth-realism.html 单文件。增加 Python标准库合并脚本、Node标准库自动测试、GitHub Pages发布工作流。

未采用立即给v14 Python事件引擎增加Web后端的路线：本阶段无后端服务/持续运行的授权或维护条件。浏览器引擎重现关键原则（明确起始时刻、行动推进时间、地点先出发后到达、未知余额不默认为0、消息送达后认知、后台NPC状态与玩家信息隔离），**不声称与v14同一个事件计算器、哈希审计等价，也不声称移植所有v15—v33模块**。

## 游戏设计边界
1. 本地新建角色将只建立 mode=S_INDEPENDENT_PLAYTHROUGH 分支；artifacts/v14/official_world_state_frozen_v13.json 完全不修改。
2. 北京16区选择为真实地理概念，但界面地图为非比例示意；出行耗时、票价和首次遇见的NPC均为S级输入或情节，不能称现实定位。
3. 31人来自 docs/NPC_ROSTER.md，模拟自动活动不标识真实居住点，不自动告知主角。游戏时间以玩家操作为唯一触发；浏览器关闭时不会“后台继续运行”。
4. 工作行为不得在缺失劳动合同、工资数据时凭空发薪；未知现金保留 null；目前消费是玩家个人记账，不假称实现完整银行双边守恒。
5. JSON导出可移植，但浏览器 localStorage 因运行环境/设置可能失效，遇此情况需要手动导出。导入仅作基本结构校验，不具备签名认证，不能信任来自陌生来源的存档内容。
6. GitHub Pages部署依赖仓库Pages设置；CI测试通过与公开站点上线为不同状态。

## 文件与检验
新增 game/index.html、game/style.css、game/app.js、game/engine.js、game/earth-realism.html、game/tests/engine.test.cjs、game/README.md、scripts/build_standalone_game.py、.github/workflows/game-pages.yml；更新根README导航与同步状态说明。

校验项包括角色输入、31NPC名单、时间、出行与资金拒绝、消息延迟、NPC后台信息边界、重放确定性、JSON恢复和120步连续事件，以及静态脚本语法与单文件重建一致性。GitHub Actions实际通过与否须基于该分支对应workflow run再汇报，不能仅因已提交工作流就宣称CI通过。

## 后续差距
要推进可信的真实世界模拟，仍需接入来源明确的路线和行政/就业/经济资料，构建事件审计可回放、劳动财务双边账本，以及更完整的NPC计划模型，并保留隐私合规与R/S/U分级。未在本任务中引入未经核实的私营、家庭或行政信息。