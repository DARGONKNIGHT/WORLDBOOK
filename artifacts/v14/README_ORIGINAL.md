# EARTH REALITY — v14.0 沙盒模拟与审计包

本包在 v13.0 冻结世界档案上开发独立的 **S 级虚构沙盒**，不创建玩家角色，不推进正式游戏时间。仅用 Python 标准库。

## 文件

- `official_world_state_frozen_v13.json` — v13.0 原件副本，已冻结，绝不能写入测试事件。
- `validate_v13_reference.py` — v13.0 校验程序只读参考副本；正式 v13 资料需从前版保留。
- `engine_v14.py` — 时间队列、旅行、占用、消息、资金、权限与可重放日志。
- `scenario_v14.py` — 30天测试，初始金额、地点、通信均为明示的 S 级假设。
- `test_v14.py` — 14 项标准库 `unittest` 自动测试。
- `world_manifest_v14.json` — 世界书版本、冻结语义、文件关系与模型局限。
- `worldbook_protocol_v14.md` — 中文正式世界书 v14.0 协议。
- `sandbox_30day_summary.json` — 沙盒运行结果与摘要。
- `sandbox_30day_journal.json` — 测试事件日志（不是真实游戏历史）。
- `sandbox_30day_final_state.json` — 沙盒30天后的模拟状态。
- `audit_report_v14.md` — 验收报告。
- `test_results_v14.txt` — 14项单元测试实际输出。
- `scenario_stdout_v14.txt` — 实际执行过程的摘要输出。

## 执行

在本目录运行：

```bash
python -m unittest -v test_v14
python scenario_v14.py
```

需要 Python 3.10+，不联网、不安装第三方库、不接入真实账户和地理导航。

## 测试事实和世界事实的区别

- 正式基准仍是 `2026-10-09`，时钟为空，玩家为空，正式事件账本为空。
- 测试时间假设采用 `2026-10-09T09:00:00+08:00`，只属于隔离的沙盒。
- 原始 31 位 NPC 的生日、钱款、精确住址等资料仍未知。
- 沙盒金额为虚拟测试分单位，地点均标记 `TEST_*`。
- 不能将测试结果描述为在现实前礼务村实际发生的事情。