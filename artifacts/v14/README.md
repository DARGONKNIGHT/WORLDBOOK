# v14 可执行沙盒文件清单

- [engine_v14.py](engine_v14.py)：离散事件模拟引擎。
- [scenario_v14.py](scenario_v14.py)：30天沙盒场景，输出日志与快照。
- [test_v14.py](test_v14.py)：14项自动一致性测试。
- [official_world_state_frozen_v13.json](official_world_state_frozen_v13.json)：用于防篡改检查的冻结状态副本。
- [sandbox_30day_journal.json](sandbox_30day_journal.json)：完整30日事件日志。
- [sandbox_30day_final_state.json](sandbox_30day_final_state.json)：沙盒最终状态。
- [sandbox_30day_summary.json](sandbox_30day_summary.json)：摘要与统计。
- [audit_report_v14.md](audit_report_v14.md)、[worldbook_protocol_v14.md](worldbook_protocol_v14.md)：中文审计及协议。
- [重新生成的v14 ZIP](../earth_realism_v14_bundle.zip)。

测试：548处理＝530次无动作例行检查+18次具体事件/反例；542完成、6拒绝；14/14测试通过。**不是**31人全部真实日常行为的逐日模拟。正式时间不推进。

本目录可通过`python scripts/build_archives.py`（在仓库根目录）重跑测试并重新生成日志及ZIP；运行依赖Python标准库。
