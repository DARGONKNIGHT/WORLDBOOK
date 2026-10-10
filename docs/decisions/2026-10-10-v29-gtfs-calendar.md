# ADR-v29 GTFS服务日、调休日与跨午夜时刻

- **GitHub基线**：2026-10-10主分支提交`9f44a006a7fe974e4b88e54b84a8df57ecc4ee8d`，已读取v26主档案、完整资源缺口清单、数据manifest与v16—v26过程源码。
- **问题**：避免v17演示车辆时刻误被推广为北京真实公交；规范服务日、班次日期异常和跨午夜的GTFS时刻。
- **采用方案**：引入GTFS service_id、calendar周循环、calendar_dates增删例外；没有真实经授权的GTFS feed时，服务状态是U而非‘没有车’。
- **其他方案与拒绝理由**：立即把OSM站点/设施标注当作真实运营数据会引入伪事实；缺来源的交通时间和历史经济价格只能保留U；不得编造私人生活。
- **程序与数据**：`artifacts/v27_30/calendar_v29.py`，共享测试`artifacts/v27_30/test_v27_30.py`；实际字节必须由GitHub Actions写回并核对SHA256。
- **资料依据**：GTFS Schedule规范（calendar.txt/calendar_dates.txt/stop_times.txt）https://gtfs.org/documentation/schedule/reference/
- **验收状态**：待GitHub CI实际运行；正式世界仍冻结。
