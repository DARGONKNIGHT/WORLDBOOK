# 《地球：现实人生》· 离线可玩浏览器版

本项目以 WORLDBOOK v33 为只读依据，新增独立 **S级单机试玩游戏**。这是一个可操作的游戏原型，不是实时地球数字孪生，也不会改动正式冻结状态。原生 HTML / CSS / JS，无需账号或安装依赖。

## 开始游玩

**单文件方法（推荐）**：下载 [earth-realism.html](earth-realism.html)（GitHub 文件页右上角 Download raw file，或从 [raw 地址](https://raw.githubusercontent.com/DARGONKNIGHT/WORLDBOOK/main/game/earth-realism.html)保存为同名 .html），双击用现代浏览器打开，按提示创建角色。

**在线部署**：GitHub Pages 成功启用且手动触发发布工作流成功后，预计网址是 https://dargonknight.github.io/WORLDBOOK/ 。实际是否可用须以 GitHub Pages/Actions 状态为准；若发布工作流因为 Pages 尚未启用而失败，先进入 Settings → Pages → Build and deployment，将 Source 设为 GitHub Actions，再手动运行 Game · Publish to Pages (after enablement)。

**源代码方法**：下载本仓库 ZIP，解压后双击 game/index.html；该入口会引用同目录 engine.js、app.js、style.css。两个入口都可离线玩。

## 已实现功能

- 创建角色：姓名、年龄、北京16区开局地点、具体开局时刻、职业、目标、可支配现金（可留空，未知不是零）。
- 行动：观察街区、S级公共活动偶遇、整理计划、处理既有工作、休息、等待；只有主动操作才推进游戏时钟。
- 出行：玩家给出假设耗时与登记的支出，先出发，时间经过后才抵达；无实时路况/真实票价承诺。
- NPC：从世界书导入31人名单、年龄与职业，进行有限、可重现的后台任务选择；其行为属于模拟，未推断真实住址、工资或私密关系。
- 联系与消息：不自动认识人物；模拟认识后才能发消息；发送与延迟送达分离；回复并非必然。幕后活动不自动变成玩家知识。
- 保存：尝试在浏览器 localStorage 自动保存，可导出JSON和导入恢复；完全离线，不会同步云端。
- 玩家视角事件日志与可选的社会后台审计视角分离。

## 尚未实现的范围

这是可游玩的首版，不是将原有 v14 Python引擎、v15—v33 所有模块全部移植。暂不具备真实 OSM 全北京市寻路、真实 GTFS 时刻、签证社保税务核算、可信银行转账、住房合同处理、完整跨域资金守恒、实时生活资料及31人全面自主日常。对于未核实数据严格保持 U 级，而不是捏造数值。v2—v12世界书早期全文仍有来源缺口。

浏览器存档模式为 S_INDEPENDENT_PLAYTHROUGH，原始正式世界仍被冻结：2026年10月9日，玩家不存在、未指定具体游戏时刻、历史账本为空。**只有你在新游戏里明确创建的分支才推进时间。** 顺义区前礼务村是观察样本，不是预设玩家住址。

**事实等级**：R=已核实的真实信息；S=明确的模拟设定、人物和剧情；U=未知或未核实。游戏中的偶遇、NPC活动及路线耗时均为S。

## 自检与可重复构建

在仓库根目录运行以下命令：

- node --check game/engine.js
- node --check game/app.js
- node --test game/tests/engine.test.cjs
- python3 scripts/build_standalone_game.py --check

编辑多文件源码后，运行 python3 scripts/build_standalone_game.py 更新独立单文件发布版。自动测试工作流见 .github/workflows/game-tests.yml；Pages发布为独立手动工作流 .github/workflows/game-pages.yml。单机游戏属于界面层，不自动升级核心世界书版本。