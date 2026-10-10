# ADR-0002：v15有限理性决策与日程预约

**日期**：2026-10-10 · **状态**：接受，须通过CI验收后关闭测试事项

## 仓库依据
基线提交`a706a04cdca9225a63c7cd0848c20bfd92bf76be`，已有v14事件引擎、正式v13冻结世界状态、31人虚构名册、5份真实原始数据及2026-10-01 OSM路网数据清单。实际读取`AGENTS.md`、`docs/WORLDBOOK_MASTER.md`、`docs/NPC_ROSTER.md`、`docs/SYNC_STATUS.md`、`data/manifest.json`、v14源码和测试。

## 备选与选择
A. 直接给每个NPC每天生成完整生活：会在工资、住址、学校日程未知时大规模捏造。
B. 在v14约束引擎上增加有限决策候选、信息先决、日程预约和可选择的不作为（选用）。

这种策略优先提高因果一致性，而不是制造戏剧事件。模拟效用权重属于人为假设，没有现实人口校准，不输出“NPC真实会如此做”的结论。

## 实际改动
- `artifacts/v15/planner_v15.py`：候选效用评分、条件拒绝、时间预约、低优先级不行动；
- `artifacts/v15/scenario_v15.py`：仅S级商店/修理/家庭信息/教师个人日程示例；
- `artifacts/v15/test_v15.py`：消息延迟、无自动采购、预算未知、时间冲突、地点、哈希链、重复编号等自动测试；
- `artifacts/v15/worldbook_protocol_v15.md` 和`worldbook/v15.md`：新规则；
- CI工作流：运行v14回归测试、v15测试和独立沙盒，生成JSON报告；生产数据不混入官方存档。

## 验收条件
- v14原14项测试仍通过。
- v15至少18项独立测试通过。
- `official_world_state_frozen_v13.json`测试前后原始字节完全一致。
- 只有满足信息、预算、时间和位置条件的候选事项进入事件队列。
- 没有模拟款项自动支付，没有新增玩家或正式游戏历史。
- GitHub CI与提交SHA核实后在本文件后续补充实际运行结果；未实际验证前保持待验收。

## 自动验收记录（GitHub Actions）
- 旧版v14回归14项及v15回归18项测试通过。
- 规划候选 18 项：接受 9 项，拒绝/不作为 9 项。
- 决策摘要SHA256: 306eaf56466e5a7ebd7cbce7817d5e0b99983b4750d47b20d9c139b698b4503f。
- 正式冻结状态SHA256: 75d97ad9960e195f1ce21f23424c784682e5f635456277647166a66829299087，正式历史新增0。
- v15归档SHA256: b0e9db309f740b46fdfcbadd731989601a9a5edaf94dc83b9427f1f5783130ce。
- 以上只描述S级沙盒测试，不能解释为真实NPC职业与心理行为。

## 已核实的GitHub验收

- [GitHub Actions运行38037749491](https://github.com/DARGONKNIGHT/WORLDBOOK/actions/runs/38037749491) 成功，v14原14项与v15新18项测试全部通过。
- [提交c3f1a51](https://github.com/DARGONKNIGHT/WORLDBOOK/commit/c3f1a51c2bc33944b43a32f70462ce51b26679fd) 存入完整沙盒决策、事件日志和ZIP。决策18项：9个预排、9个拒绝/不作为；实际底层事件13条，零资金过账。
- 正式世界的冻结文件保持不变；世界书不存在角色创建和时间推进。
