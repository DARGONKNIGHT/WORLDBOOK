/* 《地球：现实人生》独立离线试玩引擎 · 所有人物与偶遇事件均为S级模拟。
   仅在用户操作后结算游戏时间；不修改artifacts/v14/official_world_state_frozen_v13.json。 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EarthGame = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const VERSION = 2;
  const BASE_DAY = "2026-10-09";
  const HOUR = 3600000, MINUTE = 60000, DAY = 24 * HOUR, OFFSET = 8 * HOUR;
  const DISTRICTS = ["东城","西城","朝阳","海淀","丰台","石景山","门头沟","房山","通州","顺义","昌平","大兴","怀柔","平谷","密云","延庆"];
  const GROUPS = {
    F01: "陈国平家庭关系组", F02: "李文浩家庭关系组",
    F03: "周明家庭及异地亲属", F04: "吴晓宁朋友同事", F05: "维修合作",
    E01: "商业候选", E02: "制造业候选", E03: "物流生活服务候选", E04: "教育医疗家庭候选"
  };
  // 顺序、年龄和职业来源：docs/NPC_ROSTER.md。不是现实人物名录。
  const RAW = [
    ["陈国平",54,"F01","农业生产及经营事务"],["刘桂芳",51,"F01","生活用品商店经营"],
    ["陈雨",25,"F01","顺义城区行政工作"],["陈建民",78,"F01","退休"],
    ["李文浩",36,"F02","制造企业设备技术工作"],["赵倩",34,"F02","企业会计"],
    ["李晨",8,"F02","在学儿童"],["周明",30,"F03","物流工作；北京租住"],
    ["孙丽",29,"F03","服务业工作"],["周玉兰",57,"F03","外省生活；具体省份未知"],
    ["吴晓宁",27,"F04","教师"],["黄琳",28,"F04","朝阳区工作；行业未知"],
    ["唐洁",31,"F04","吴晓宁同事；已婚"],["马志强",43,"F05","维修业务经营"],
    ["高鹏",32,"F05","维修技术合作"],["郑文芳",64,"E01","退休"],
    ["韩超",38,"E01","农产品批发经营"],["王祺",26,"E01","配送司机"],
    ["吕倩",33,"E01","个体经营"],["宋学峰",47,"E02","制造业班组管理"],
    ["郭媛",32,"E02","企业人事"],["彭超",29,"E02","质量检验技术"],
    ["张树立",52,"E02","货运"],["董航",39,"E03","物流调度"],
    ["崔月",26,"E03","餐饮值班管理"],["杨珂",44,"E03","设施维护"],
    ["孟蕾",37,"E03","客户服务"],["郭敏",42,"E04","教师；单位未知"],
    ["陆琪",30,"E04","护士；机构未知"],["许国忠",66,"E04","退休职工"],
    ["范晴",35,"E04","在职家长"]
  ];
  const NPCS = RAW.map((row, i) => Object.freeze({
    id: "P" + String(i+1).padStart(3,"0"), name: row[0], age:row[1],
    group:row[2], occupation:row[3], grade:"S"
  }));
  const AREAS = {
    东城:"街巷、公共机构与老城生活交织；具体营业与服务状态未知。",
    西城:"传统住区与商务办公并置；个人住址、租金和名额需要逐一核实。",
    朝阳:"就业、商业及居住活动密集；陌生人仍有自己的日程和关系。",
    海淀:"学校、园区与社区相邻；身份和工作资格不因到访而获得。",
    丰台:"住宅、商贸与多种交通需求并存；跨片区移动需要时间。",
    石景山:"工业转型与居民日常并行；具体岗位与营业时间未知。",
    门头沟:"山地地形影响出行；不能假设道路无阻或任意穿越。",
    房山:"区域尺度较大，跨区通勤和服务可达性并非理所当然。",
    通州:"行政办公与居民日常并存，制度服务需要具体权限和材料。",
    顺义:"本世界书的前礼务村观察样本位于顺义，但不是你的默认住所。",
    昌平:"居住、产业与跨区往返交错；行程耗时须由你确认。",
    大兴:"城市社区与区域产业并存；并非所有路程都可短时抵达。",
    怀柔:"山地、社区和区域产业各有约束；服务供给不凭空出现。",
    平谷:"村镇与城区空间分散；具体路况与事件仍属未知。",
    密云:"距离和地形是真实约束；本试玩没有实时交通数据。",
    延庆:"山地和区域边界会影响旅程；未知道路不能当作已验证通路。"
  };
  function assert(ok, msg) { if (!ok) throw new Error(msg); }
  function validText(s, max) { return String(s ?? "").trim().slice(0,max); }
  function clock(ms) { return new Date(ms).toLocaleString("zh-CN",{timeZone:"Asia/Shanghai",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false}); }
  function dayNumber(ms) { return Math.floor((ms+OFFSET)/DAY); }
  function localDay(ms) { return new Date(dayNumber(ms)*DAY).toISOString().slice(0,10); }
  function pseudorand(seed) { let x = (seed >>> 0) + 0x6D2B79F5; x = Math.imul(x ^ x>>>15,x|1); x ^= x + Math.imul(x ^ x>>>7,x|61); return ((x ^ x>>>14)>>>0)/4294967296; }

  // Explicit S-grade scenario assumptions, never real NPC addresses or true schedules.
  // F-family locality is a playable sandbox convention, not a claim about real residents.
  const REGION = {
    F01:"顺义",F02:"顺义",F03:"顺义",F04:"顺义",F05:"顺义",
    E01:"顺义",E02:"昌平",E03:"海淀",E04:"海淀"
  };
  const DISTRICT_OVERRIDE = {P010:"外省（未知）",P012:"朝阳",P014:"顺义",P017:"顺义",P020:"昌平",P028:"海淀"};
  const FOCUS = {
    P001:"田间事务与家庭开支",P002:"小店营业与家中照顾",P003:"单位事务与家人联系",P004:"身体休息与家人来往",
    P005:"设备维修排班与家务",P006:"工作账务与照料孩子",P007:"学校作息与监护安排",
    P008:"物流排班与租住事务",P009:"服务业轮班与家庭",P010:"异地生活和亲属联系",
    P011:"备课与同事协作",P012:"上班与私人生活",P013:"教学协作和婚姻家庭",
    P014:"客户需求与维修合作",P015:"技术维修与工单安排",P016:"家庭日常与健康",
    P017:"进货供货与信用关系",P018:"送货与路线时间",P019:"小店经营与库存",
    P020:"班组进度与安全",P021:"人事材料与工作流程",P022:"质检记录与返工",P023:"货运排班与休息",
    P024:"车队调度与时效",P025:"餐饮轮班与顾客",P026:"现场维修与安全",P027:"客户服务与私人生活",
    P028:"教学准备与家庭",P029:"护理轮班与睡眠",P030:"退休生活与旧友",P031:"家庭照护与在职事务"
  };
  const SHIFT = new Set(["P009","P018","P023","P025","P029"]);
  const RETIRED = new Set(["P004","P016","P030","P010"]);
  const FAMILY = new Set(["P001","P002","P004","P005","P006","P007","P008","P009","P010","P013","P031"]);
  const CIVIL = new Set(["P003","P006","P011","P012","P013","P021","P028"]);
  const CHILDREN = new Set(["P007"]);
  const APPROACH_TTL = 100 * MINUTE;
  function districtFor(n){return DISTRICT_OVERRIDE[n.id] || REGION[n.group];}
  function minuteOfDay(ms){return ((ms+OFFSET)%DAY+DAY)%DAY/MINUTE;}
  function hourOf(ms){return Math.floor(minuteOfDay(ms)/60);}
  function weekday(ms){return new Date(ms+OFFSET).getUTCDay();}
  function stage(n,ms){
    const h=hourOf(ms), weekend=[0,6].includes(weekday(ms));
    if(CHILDREN.has(n.id))return {kind:h>=8&&h<16?"school":h>=21||h<7?"sleep":"family",reason:"未成年人有监护和学校约束"};
    if(h<7||h>=23)return {kind:"sleep",reason:"夜间休息优先，不随时接待"};
    if(RETIRED.has(n.id)){
      if(h===9||h===16)return {kind:"errand",reason:"保留日间外出窗口，非每日必发生"};
      return {kind:h>=18?"family":"personal",reason:"生活安排优先于陌生社交"};
    }
    if(SHIFT.has(n.id)){
      if(h>=14&&h<22)return {kind:"work",reason:"假设性轮班，履行工作责任"};
      if(h===11||h===12)return {kind:"errand",reason:"班前可能处理个人事务"};
      return {kind:h<10?"rest":"personal",reason:"轮班休息与个人时间"};
    }
    if(n.id==="P002"||n.id==="P014"||n.id==="P017"||n.id==="P019"){
      if(h>=9&&h<19 && !weekend)return {kind:"work",reason:"经营营业与既有客户责任"};
      if(h>=9&&h<17)return {kind:"work",reason:"假设周末营业，但不等于真实开门"};
      return {kind:"family",reason:"店务结束后有家庭和休息安排"};
    }
    if(h>=9&&h<12&&!weekend || h>=13&&h<18&&!weekend)return {kind:"work",reason:"假设工作日日间工作安排"};
    if(h===12||h===18)return {kind:"errand",reason:"午间或傍晚可能处理生活事务"};
    if(h>=19&&h<22 && FAMILY.has(n.id))return {kind:"family",reason:"家人和既有承诺优先"};
    return {kind:"personal",reason:weekend?"非工作日个人计划":"下班后个人事务"};
  }
  const STAGE_TEXT={
    work:"投入既有工作／营业安排",family:"处理家庭责任和既定约定",
    errand:"考虑外出办事与日常采购",school:"按监护与学校作息安排活动",
    sleep:"优先休息，不接受临时社交",rest:"恢复体力或处理轮班休息",
    personal:"保留私人时间，不必参与公开活动"
  };
  function choice(s,n,at){
    const base=stage(n,at),seed=dayNumber(at)*133+n.id.charCodeAt(3)*41+hourOf(at)*991;
    // Chance of opting OUT of discretionary errands; no compulsory activity per NPC.
    const skip=base.kind==="errand"&&pseudorand(seed)<0.35;
    return {kind:skip?"personal":base.kind,reason:skip?"评估事务优先级后决定暂不外出":base.reason,
      location:districtFor(n),focus:FOCUS[n.id],score:skip?0:base.kind==="work"?39:base.kind==="family"?31:base.kind==="sleep"?36:16,
      optional:base.kind==="errand"};
  }
  function plan(s,id,at=s.time){
    const n=NPCS.find(x=>x.id===id);assert(n,"未知人物");
    return choice(s,n,at);
  }
  function upgradeGame(s){
    assert(s&&typeof s==="object","存档无效");
    if(s.schema===2)return validateGame(s);
    assert(s.schema===1&&s.mode==="S_INDEPENDENT_PLAYTHROUGH","旧存档无法迁移");
    // Preserve the historical v1 game record; do not retroactively rewrite outcomes.
    s.schema=2;s.autonomy={enabled:true,detail:"balanced"};
    s.player.met=[];s.player.declined=[];
    for(const n of NPCS){
      const prior=s.npc[n.id]||{};
      s.npc[n.id]={...prior,stage:null,decisions:[],relation:s.player.contacts.includes(n.id)?2:0,
        lastRead:null,responded:0,pending:[]};
    }
    return validateGame(s);
  }

  function event(state, at, message, kind="scene", visible=true, grade="S") {
    state.sequence++;
    const item={id:state.sequence,at,kind,text:message,grade,visible};
    state.journal.push(item);
    if(state.journal.length>3000) state.journal.shift();
    return item;
  }
  function makeGame(options) {
    assert(options && typeof options==="object","必须提交角色资料");
    const name=validText(options.name,30);
    assert(name.length>0,"请填写角色姓名");
    const age=Number(options.age);
    assert(Number.isInteger(age)&&age>=16&&age<=100,"角色年龄须在16至100岁之间");
    const district=validText(options.district,10);
    assert(DISTRICTS.includes(district),"请选择北京市的一个区作为开局所在区");
    const start=validText(options.start,5)||"09:00";
    assert(/^([01]\d|2[0-3]):[0-5]\d$/.test(start),"时间须采用24小时制");
    const time=Date.parse(BASE_DAY+"T"+start+":00+08:00");
    const cash=options.cash===""||options.cash===null||options.cash===undefined ? null : Number(options.cash);
    assert(cash===null||(Number.isSafeInteger(cash)&&cash>=0&&cash<=1000000000),"初始可支配现金必须为非负整数元，或留空表示未知");
    const occupation=validText(options.occupation,60);
    const goal=validText(options.goal,100);
    const state={
      schema:VERSION, mode:"S_INDEPENDENT_PLAYTHROUGH", started:true,
      time, sequence:0,
      player:{name,age,district,homeDistrict:district,occupation:occupation||null,goal:goal||null,cash,energy:80,contacts:[],knowledge:[],met:[],declined:[]},
      npc:Object.fromEntries(NPCS.map(n=>[n.id,{lastActivity:null,knowledge:[],stage:null,decisions:[],relation:0,lastRead:null,responded:0,pending:[]}])),
      queue:[], messages:[], journal:[], world:[], cycles:0, autonomy:{enabled:true,detail:"balanced"}
    };
    event(state,time,"你为这一条独立S级游戏分支创建了角色。正式世界书原始存档仍冻结；现有资料不足以宣称实时地球模拟。","system");
    event(state,time,"2026年10月9日，"+name+"从北京"+district+"区开始自己的第一天。你可以探索、安排事务、结识人物或前往其他区。","scene");
    return state;
  }
  function validateGame(s) {
    assert(s && s.schema===VERSION && s.mode==="S_INDEPENDENT_PLAYTHROUGH","存档版本或模式不受支持");
    assert(s.started===true && s.player && typeof s.player.name==="string","存档角色无效");
    assert(Number.isFinite(s.time) && s.time>=Date.parse(BASE_DAY+"T00:00:00+08:00"),"时间字段不合法");
    assert(DISTRICTS.includes(s.player.district)&&DISTRICTS.includes(s.player.homeDistrict),"地点无效");
    assert(Number.isInteger(s.sequence)&&s.sequence>=0,"日志序号无效");
    assert(Array.isArray(s.queue)&&Array.isArray(s.messages)&&Array.isArray(s.journal)&&Array.isArray(s.world),"事件结构无效");
    assert(s.npc && NPCS.every(n=>s.npc[n.id]&&Array.isArray(s.npc[n.id].knowledge)),"NPC索引不完整");
    assert(s.player.cash===null||(Number.isSafeInteger(s.player.cash)&&s.player.cash>=0),"资金字段无效");
    assert(Number.isInteger(s.player.energy)&&s.player.energy>=0&&s.player.energy<=100,"精力字段无效");
    assert(Array.isArray(s.player.contacts)&&s.player.contacts.every(id=>NPCS.some(n=>n.id===id)),"联系人列表无效");
    assert(s.autonomy && typeof s.autonomy.enabled==="boolean" && ["balanced","detailed"].includes(s.autonomy.detail),"NPC自主选项无效");
    assert(Array.isArray(s.player.met)&&Array.isArray(s.player.declined),"相遇状态无效");
    assert(NPCS.every(n=>Number.isInteger(s.npc[n.id].relation)&&Array.isArray(s.npc[n.id].decisions)),"NPC关系/决策数据无效");
    assert(s.queue.every(q=>Number.isFinite(q.at)&&q.at>=s.time&&typeof q.type==="string"),"待办队列有过期或非法事件");
    return s;
  }
  function npcRecord(s,n,at,c,reason,visible=false){
    const state=s.npc[n.id];
    const line={at,npcId:n.id,kind:c.kind,text:n.name+"："+
      STAGE_TEXT[c.kind]+"；"+reason+"。",reason,score:c.score,location:c.location,grade:"S",visibility:"out_of_character"};
    state.lastActivity=line;
    state.stage={kind:c.kind,at,location:c.location};
    state.decisions.push({at,kind:c.kind,reason,score:c.score});
    if(state.decisions.length>96)state.decisions.shift();
    s.world.push(line);if(s.world.length>4000)s.world.shift();
    if(visible)event(s,at,"你注意到"+n.name+"在附近处理日常事务。","observation");
  }
  function autonomousWorld(s,start,end){
    if(!s.autonomy.enabled)return;
    // Tick at hour boundaries. Each NPC has a stable sample location, no teleportation.
    for(let at=Math.floor(start/HOUR)*HOUR+HOUR;at<=end;at+=HOUR){
      for(const n of NPCS){
        const c=choice(s,n,at), prev=s.npc[n.id].stage;
        if(!prev||prev.kind!==c.kind||s.autonomy.detail==="detailed")
          npcRecord(s,n,at,c,c.reason);
      }
    }
  }
  function categorize(text){
    if(/借钱|转账|贷款|周转|给我钱/.test(text))return "money";
    if(/见面|约|一起吃|喝咖啡|拜访/.test(text))return "meet";
    if(/工作|招聘|简历|入职|雇佣/.test(text))return "job";
    if(/维修|报价|修理|订单|采购/.test(text))return "business";
    if(/急|救命|危险|受伤/.test(text))return "urgent";
    if(/你好|早上好|最近如何|在吗|谢谢/.test(text))return "greeting";
    return "general";
  }
  function response(s,n,message,at){
    const kind=categorize(message),c=choice(s,n,at),r=s.npc[n.id].relation;
    // The answer reflects topic and prior relationship, not a random universal template.
    if(kind==="money")return "涉及借款和转账，我不能凭一条消息就答应。你需要另想办法。";
    if(kind==="meet")return c.kind==="work"||c.kind==="family"?
      "我现在有"+(c.kind==="work"?"工作":"家里")+"的安排，今天不能临时约。先把时间和事情说清楚。":
      r<2?"我们还不熟，我暂时不约单独见面。":"先把地点和具体时间说一下，我确认后再答复。";
    if(kind==="job")return CIVIL.has(n.id)?
      "工作上的事情要按正式流程来，我不能私下保证岗位。":
      "我不掌握招聘决定权，最好核对岗位要求和公开渠道。";
    if(kind==="business")return (n.id==="P014"||n.id==="P015")?
      "维修需要先看故障、地址和时间，我目前不能直接承诺上门或报价。":
      "你先说明事项和条件，我不能在不了解情况时确认交易。";
    if(kind==="urgent")return "如果确有即时危险，请优先联系当地紧急服务；我不能保证现在赶到。";
    if(kind==="greeting")return c.kind==="work"?
      "刚看到消息，今天手头事务多，没法聊太久。":
      r>=2?"我看到了。最近还在忙自己的事，你那边怎么样？":"你好。有什么具体事吗？";
    return c.kind==="family"?
      "家里现在有事。你的消息我看了，等事情明确后再回复。":
      c.kind==="work"?"我手上正在处理"+FOCUS[n.id]+"。请把需要我回应的问题讲具体些。":
      r<2?"这件事我还不清楚，不方便立刻表态。":"我得先确认信息，暂时不能答应。";
  }
  function nextAvailable(s,n,at){
    // Delivery does not equal reading. Respect quiet hours, work and family duties.
    let t=Math.ceil(at/(30*MINUTE))*30*MINUTE;
    for(let i=0;i<72;i++,t+=30*MINUTE){
      const c=choice(s,n,t),h=hourOf(t);
      if(h>=8&&h<=22 && !["work","sleep","school"].includes(c.kind) && !(c.kind==="family"&&pseudorand(dayNumber(t)*89+n.id.charCodeAt(3))<0.5))return t;
    }
    return null;
  }
  function dueEvents(s,until){
    let processed=0;
    while(s.queue.length){
      s.queue.sort((a,b)=>a.at-b.at||a.order-b.order);
      if(s.queue[0].at>until)break;
      assert(++processed<=2500,"单轮待办事件过多");
      const q=s.queue.shift(),n=NPCS.find(x=>x.id===(q.to||q.from));
      if(!n)continue;
      const v=s.npc[n.id];
      if(q.type==="deliver"){
        v.knowledge.push({at:q.at,topic:q.text,source:"player"});
        if(v.knowledge.length>160)v.knowledge.shift();
        // No player-visible receipt unless the recipient actually reads the message.
        const readAt=nextAvailable(s,n,q.at);
        if(readAt!==null)s.queue.push({type:"read",at:readAt,to:n.id,text:q.text,order:s.sequence+1,seed:q.seed});
      }else if(q.type==="read"){
        v.lastRead=q.at;
        event(s,q.at,n.name+"已读你之前发出的消息。","message");
        const category=categorize(q.text);
        const outcome=pseudorand(q.seed+v.responded*31+17);
        // People may choose silence; repeated greetings need not yield replies.
        const chance=category==="money"?0.85:category==="urgent"?0.85:category==="meet"?0.75:category==="greeting"?0.6:0.7;
        if(outcome<chance){
          v.responded++;
          const replyAt=q.at+(10+Math.floor(pseudorand(q.seed+37)*26))*MINUTE;
          s.queue.push({type:"reply",at:replyAt,from:n.id,content:response(s,n,q.text,q.at),order:s.sequence+1});
        }else{
          s.world.push({at:q.at,npcId:n.id,kind:"silence",text:n.name+"已读后没有回复；眼前责任或意愿优先。",reason:"可选择不回应",grade:"S",visibility:"out_of_character"});
        }
      }else if(q.type==="reply"){
        s.messages.push({at:q.at,from:n.id,content:n.name+"："+q.content,grade:"S"});
        event(s,q.at,"你收到"+n.name+"的一条回复。","message");
      }
    }
    s.queue.sort((a,b)=>a.at-b.at||a.order-b.order);
    if(s.world.length>4000)s.world=s.world.slice(-4000);
  }
  function advance(s, minutes) {
    assert(Number.isInteger(minutes)&&minutes>=1&&minutes<=480,"每次推进必须为1至480分钟");
    const old=s.time, next=old+minutes*MINUTE;
    autonomousWorld(s,old,next);
    dueEvents(s,next);
    s.time=next;
    s.cycles++;
  }
  function act(s, kind, payload={}) {
    validateGame(s);
    assert(typeof kind==="string"&&payload&&typeof payload==="object","操作无效");
    const p=s.player, at=s.time;
    if(kind==="travel"){
      const to=validText(payload.destination,10), minutes=Number(payload.minutes);
      const fare=payload.fare===""||payload.fare===undefined?0:Number(payload.fare);
      assert(DISTRICTS.includes(to)&&to!==p.district,"请选择不同的目的区");
      assert(Number.isInteger(minutes)&&minutes>=15&&minutes<=480,"请输入15至480分钟的规划行程");
      assert(Number.isSafeInteger(fare)&&fare>=0,"交通支出必须为非负整数元");
      assert(fare===0||p.cash!==null,"现金未知，无法登记已支付交通费");
      assert(fare===0||p.cash>=fare,"资金不足，不能登记这笔支出");
      assert(p.energy>=8,"精力不足，请先休息");
      const from=p.district;
      event(s,at,"从"+from+"区出发，前往"+to+"区。"+minutes+"分钟是玩家设定的S级行程估计，不是导航数据。","travel");
      advance(s,minutes);
      p.district=to;p.energy=Math.max(0,p.energy-8);
      if(fare>0) {p.cash-=fare;event(s,s.time,"你登记了交通支出 ¥"+fare+"。此为单人账本，不表示外部银行已过账。","finance");}
      event(s,s.time,"到达北京"+to+"区。新地点在行程完成后才更新。","arrival");
    }else if(kind==="explore"){
      assert(p.energy>=6,"精力不足，请先休息");
      advance(s,35);p.energy-=6;
      event(s,s.time,"你在"+p.district+"区观察日常环境、留意公开告示。具体营业状态、新闻和服务资格仍需核实。","scene");
    }else if(kind==="study"){
      assert(p.energy>=12,"精力不足，请先休息");
      advance(s,60);p.energy-=12;
      event(s,s.time,"你用一小时整理公开信息与下一步计划。这不构成对非公开事实的自动获知。","scene");
    }else if(kind==="work"){
      assert(p.occupation,"尚未声明职业或业务，不能凭空结算工作");
      assert(p.energy>=22,"精力不足，请先休息");
      advance(s,120);p.energy-=22;
      event(s,s.time,"你投入两小时处理“"+p.occupation+"”相关事务；本系统没有可靠工资、客户和合同数据，因此不自动生成收入。","work");
    }else if(kind==="rest"){
      advance(s,60);p.energy=Math.min(100,p.energy+25);
      event(s,s.time,"你休息了一个小时。精力是S级游戏数值，不代表医学测量。","scene");
    }else if(kind==="wait"){
      const mins=Number(payload.minutes);
      advance(s,mins);
      event(s,s.time,"你按自己的决定等待了"+mins+"分钟。等待期间，部分独立NPC事务已在后台结算，但不会自动进入你的认知。","scene");
    }else if(kind==="social"){
      assert(p.energy>=9,"精力不足，请先休息");
      advance(s,45);p.energy-=9;
      const eligible=NPCS.filter(n=>n.age>=18&&districtFor(n)===p.district
          &&choice(s,n,s.time).kind==="errand"
          &&!p.contacts.includes(n.id)
          &&!p.met.some(m=>m.id===n.id&&m.at>at-2*HOUR));
      const chance=pseudorand(s.sequence*9137+dayNumber(s.time)*37+hourOf(s.time)*79);
      if(!eligible.length||chance<0.3){
        event(s,s.time,"你在附近进行了一次正常的公共活动。路人有自己的安排，没有发生值得建立联系的交谈。","social");
      }else{
        const n=eligible[Math.floor(pseudorand(s.sequence*2381+hourOf(s.time))*eligible.length)];
        p.met.push({id:n.id,at:s.time,district:p.district});
        if(p.met.length>80)p.met.shift();
        event(s,s.time,"你在"+p.district+"区的S级公共场景里与"+n.name+"有过简短交谈。对方没有主动留下联系方式，你可以选择礼貌询问，也可以就此结束。","social");
      }
    }else if(kind==="request_contact"){
      const id=validText(payload.recipient,8);
      const n=NPCS.find(x=>x.id===id), met=p.met.filter(m=>m.id===id).at(-1);
      assert(n&&met,"你们尚未实际见过面");
      assert(!p.contacts.includes(id),"已经有联系方式");
      assert(!p.declined.some(x=>x.id===id&&x.at>=met.at),"同一次相遇已被拒绝，请尊重对方决定");
      assert(met.district===p.district&&s.time-met.at<=APPROACH_TTL,"已离开相遇场景，不能远程索取联系方式");
      assert(p.energy>=2,"精力不足");
      advance(s,5);p.energy-=2;
      const c=choice(s,n,s.time),r=s.npc[id].relation,seed=s.sequence*917+id.charCodeAt(3)+dayNumber(s.time);
      const consents=pseudorand(seed)>0.5 && !["work","sleep","family"].includes(c.kind);
      if(consents){
        p.contacts.push(id);s.npc[id].relation=Math.max(1,r);
        event(s,s.time,n.name+"考虑后同意互留联系方式。双方只是初识，没有其他承诺。","contact");
      }else{
        p.declined.push({id,at:met.at});
        event(s,s.time,n.name+"没有同意交换联系方式。你没有继续纠缠；对方仍按原计划离开。","social");
      }
    }else if(kind==="npc_autonomy"){
      // Choice changes the simulator, not the person's own will or player knowledge.
      if(payload.enabled!==undefined)assert(typeof payload.enabled==="boolean","自动结算开关无效");
      const detail=payload.detail||s.autonomy.detail;
      assert(["balanced","detailed"].includes(detail),"请选择正确的自主活动详细程度");
      s.autonomy={enabled:payload.enabled===undefined?s.autonomy.enabled:payload.enabled,detail};
      event(s,s.time,"【模拟器设置】人物自主活动"+(s.autonomy.enabled?"已启用":"已暂停")+"；观察精度："+(detail==="detailed"?"逐时记录":"只记状态变更")+"。设置不推进游戏时间。","system");
    }else if(kind==="message"){
      const to=validText(payload.recipient,8), text=validText(payload.text,200);
      assert(p.contacts.includes(to),"主角尚未建立该联系人关系");
      assert(text.length>0,"消息不能为空");
      assert(p.energy>=1,"精力不足");
      advance(s,5);p.energy-=1;
      const n=NPCS.find(x=>x.id===to);
      const delay=1+Math.floor(pseudorand(s.sequence*83+to.length)*12);
      s.queue.push({type:"deliver",at:s.time+delay*MINUTE,to,text,order:s.sequence+1,seed:s.sequence*83+to.charCodeAt(1)});
      event(s,s.time,"你向"+n.name+"发出：“"+text+"”。已发出但尚未送达，对方尚未知情。","message");
    }else{
      throw new Error("未实现的玩家行动");
    }
    validateGame(s);
    return s;
  }
  function summary(s) {
    validateGame(s);
    return {
      timestamp:clock(s.time),district:s.player.district,
      contacts:s.player.contacts.length,events:s.journal.length,
      worldEvents:s.world.length,queued:s.queue.length,
      cash:s.player.cash,energy:s.player.energy
    };
  }
  return Object.freeze({VERSION,BASE_DAY,DISTRICTS,GROUPS,NPCS,AREAS,clock,
    makeGame,validateGame,act,summary,dayNumber,localDay,plan,upgradeGame,districtFor});
});
