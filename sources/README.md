# 现实资源索引（含路网、城市地图、经济、公共服务）

此目录是**数据来源索引**，不是已下载的完整数据库。每个条目保留来源、用途、范围、更新频率、许可与需要核查的风险。
**游戏时间截止2026-10-09：** 资料在2026-10-10检索不代表其中每一项2026-10-10之后更新内容可以进入初始历史。实际使用必须核实资料发生日、发布时间及适用日期。

## 优先级
1. 中国行政区和公开地图：天地图·北京2026标准底图、北京市民政局区划代码。
2. 路网分析：OSM/Geofabrik 北京PBF；遵守ODbL署名和数据库许可。
3. 统计与经济：国家数据、北京统计局及明确统计期的年度公报。
4. 学校、医疗、住房、政策：各主管机关原始文件；逐年核对。
5. 国际数据：World Bank、IMF、WTO；不得把宏观指标直接当人物属性。

## 源目录

| 编号 | 类型 | 来源 | 用途范围 | 许可/限制 |
|---|---|---|---|---|
| MAP-001 | map | [天地图·北京](https://beijing.tianditu.gov.cn/) | Beijing：北京市底图、影像、地图API及地名 | platform_terms |
| MAP-002 | map | [2026版北京标准地图](https://beijing.tianditu.gov.cn/bzdt/) | Beijing：行政区与城市底图、标准地图下载 | official_map_terms |
| MAP-003 | map | [2026版北京市行政区域界线基础地理底图通告](https://ghzrzyw.beijing.gov.cn/zhengwuxinxi/tzgg/sj/202609/t20260911_4859523.html) | Beijing：北京市16区界线和主干道路 | download_terms_verify |
| MAP-004 | administrative | [北京市2026行政区划名称与代码](https://mzj.beijing.gov.cn/art/2026/7/16/art_9984_692516.html) | Beijing：行政区县、街镇代码与隶属关系 | official_reuse_verify |
| MAP-005 | map | [OpenStreetMap地图与道路](https://www.openstreetmap.org/) | Global：道路、POI、建筑、路径几何 | ODbL-1.0 |
| MAP-006 | roads | [Geofabrik 北京OSM数据下载](https://download.geofabrik.de/asia/china/beijing.html) | Beijing：北京道路、路径、铁路及POI导出PBF/GPKG | ODbL-1.0 |
| MAP-007 | roads | [Geofabrik 中国OSM数据下载](https://download.geofabrik.de/asia/china.html) | China：中国地区路网与地理要素 | ODbL-1.0 |
| MAP-008 | roads | [OpenStreetMap版权许可](https://www.openstreetmap.org/copyright) | Global：地图和道路数据归属及许可 | ODbL-1.0 |
| MAP-009 | geocoding | [Nominatim公共实例使用政策](https://operations.osmfoundation.org/policies/nominatim/) | Global：地理编码API使用限制 | usage_policy |
| MAP-010 | map | [北京市政务服务地图](https://map.beijing.gov.cn/zwfwmap) | Beijing：政务服务点、街镇机构查询 | official_reuse_verify |
| MAP-011 | map | [天地图国家节点](https://www.tianditu.gov.cn/) | China：全国公共地图、地理服务 | platform_terms |
| MAP-012 | map | [北京市公共数据开放平台](https://data.beijing.gov.cn/) | Beijing：交通、房屋、医疗、价格、行政、企业等数据集目录 | dataset_specific |
| TRN-001 | transport | [北京市交通委员会](https://jtw.beijing.gov.cn/) | Beijing：轨道、道路、公交、交通政策与公告 | official_reuse_verify |
| TRN-002 | transport | [北京市公共数据开放平台交通服务专题](https://data.beijing.gov.cn/) | Beijing：交通服务专题数据与接口搜索 | dataset_specific |
| TRN-003 | transport | [高德地图](https://ditu.amap.com/) | China：实际路线及POI人工核验备选 | commercial_terms |
| TRN-004 | transport | [百度地图](https://map.baidu.com/) | China：交通导航与POI交叉校验 | commercial_terms |
| ECO-001 | economy | [国家数据](https://data.stats.gov.cn/) | China：GDP、CPI、人口、居民收入、就业等 | official_reuse_verify |
| ECO-002 | economy | [北京市统计局](https://tjj.beijing.gov.cn/) | Beijing：北京统计年鉴、GDP、就业与价格、区级数据 | official_reuse_verify |
| ECO-003 | economy | [北京市2025年统计公报](https://www.beijing.gov.cn/zhengce/zhengcefagui/202603/t20260325_4565678.html) | Beijing：2025年GDP、人口和公共资源基准 | official_reuse_verify |
| ECO-004 | economy | [北京市宏观数据库](https://hgk.tjj.beijing.gov.cn/) | Beijing：北京宏观经济数据库 | official_reuse_verify |
| ECO-005 | economy | [世界银行Open Data](https://data.worldbank.org/) | Global：跨国收入、人口、产业、发展指标 | dataset_specific |
| ECO-006 | economy | [World Bank API v2](https://api.worldbank.org/v2/country/CHN/indicator/SP.POP.TOTL?format=json) | Global：人口指标API查询示例 | worldbank_terms |
| ECO-007 | economy | [IMF数据门户](https://data.imf.org/) | Global：汇率、国际收支、宏观金融数据 | imf_terms |
| ECO-008 | trade | [WTO统计门户](https://stats.wto.org/) | Global：国际贸易和关税统计 | wto_terms |
| ECO-009 | jobs | [北京市人力资源和社会保障局](https://rsj.beijing.gov.cn/) | Beijing：工资、最低工资、劳动、招聘与社保政策 | official_reuse_verify |
| HOU-001 | housing | [北京市住房和城乡建设委员会](https://zjw.beijing.gov.cn/) | Beijing：房产、租赁、保障住房政策与通知 | official_reuse_verify |
| HOU-002 | housing | [北京市公共数据开放平台房屋住宅专题](https://data.beijing.gov.cn/) | Beijing：房屋住宅类别数据检索 | dataset_specific |
| HOU-003 | housing | [中国住房统计（国家统计局）](https://data.stats.gov.cn/) | China：住宅价格指数、投资、房地产市场统计 | official_reuse_verify |
| LEG-001 | law | [国家法律法规数据库](https://flk.npc.gov.cn/search) | China：民法典、劳动合同、继承与地方性法规 | official_reuse_verify |
| LEG-002 | law | [中国政府网政策](https://www.gov.cn/zhengce/) | China：国务院及部门政策原文 | official_reuse_verify |
| LEG-003 | law | [北京市政府政策文件](https://www.beijing.gov.cn/zhengce/) | Beijing：地方性政策、实施细则和公告 | official_reuse_verify |
| EDU-001 | education | [北京市教育委员会](https://jw.beijing.gov.cn/) | Beijing：学校、招生、校历、学籍政策 | official_reuse_verify |
| MED-001 | medical | [北京市卫生健康委员会](https://wjw.beijing.gov.cn/) | Beijing：医院、卫生服务机构、服务时间和医疗政策 | official_reuse_verify |
| MED-002 | medical | [北京市医保局](https://ybj.beijing.gov.cn/) | Beijing：参保规则、药品目录、异地就医 | official_reuse_verify |
| MED-003 | medical | [北京市公共数据开放平台定点医疗机构目录](https://data.beijing.gov.cn/) | Beijing：定点医院、医保药品和药店信息 | dataset_specific |
| WEA-001 | weather | [中国气象数据网](https://data.cma.cn/) | China：历史观测、气象资料和数据产品 | dataset_specific |
| WEA-002 | weather | [NASA Earthdata](https://www.earthdata.nasa.gov/) | Global：地球观测、气候、自然环境 | dataset_specific |
| GEO-001 | places | [Wikidata](https://www.wikidata.org/) | Global：地名、机构、实体ID与公共知识图谱 | CC0_or_item_specific |
| GEO-002 | places | [OpenStreetMap Overpass API说明](https://wiki.openstreetmap.org/wiki/Overpass_API) | Global：道路、POI、小区域OSM要素查询 | ODbL-1.0 |
| LAW-004 | international | [OECD税收协定资源](https://www.oecd.org/en/topics/tax-treaties.html) | Global：国际税收协定框架 | official_reuse_verify |
| FIN-001 | foreign_exchange | [国家外汇管理局](https://www.safe.gov.cn/) | China：个人结售汇、跨境支付与外汇制度 | official_reuse_verify |
| TRA-001 | international_trade | [海关总署](https://www.customs.gov.cn/) | China：进出口监管、税则及数据 | official_reuse_verify |
| AGR-001 | agriculture | [农业农村部](https://www.moa.gov.cn/) | China：农业生产、农产品价格及农村政策 | official_reuse_verify |

## 实际下载与使用规则

- 本索引全部标为 `INDEX_ONLY`，不代表路网、影像、人口或企业数据库已经下载到仓库。
- 对每个实际被使用的数据创建独立`sources/usage_ledger.csv`记录指标、原始链接、版本、抓取时间、适用截止日期、处理脚本及许可证。
- OSM基于ODbL，必须保留署名；不要未经授权批量调用 Nominatim 公共API。
- 官方标准地图直接使用应显示审图号；改动地图可能触发重新送审要求。地图浏览API、矢量数据和图片的再分发授权不是同一回事。
- 高德GCJ-02、百度BD-09、OSM常用WGS84数据，不可把坐标数值直接当同一坐标系合并；需依法、按许可转换。
- 道路图不等于实时交通：单行、限行、封路、信号灯、运力、班次和拥堵需额外的有效数据。
- 官方网站“可访问”不等于允许整站抓取或复制；按条目许可和特定数据集条款核查。
- NPC全部是S级虚构档案；不收集私人身份证号、住址、病历或非公开个人信息。

