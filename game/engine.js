/* 《地球：现实人生》独立离线试玩引擎 · 所有人物与偶遇事件均为S级模拟。
   仅在用户操作后结算游戏时间；不修改artifacts/v14/official_world_state_frozen_v13.json。 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.EarthGame = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const VERSION = 1;
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
      player:{name,age,district,homeDistrict:district,occupation:occupation||null,goal:goal||null,cash,energy:80,contacts:[],knowledge:[]},
      npc:Object.fromEntries(NPCS.map(n=>[n.id,{lastActivity:null,knowledge:[]}])),
      queue:[], messages:[], journal:[], world:[], cycles:0
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
    assert(s.queue.every(q=>Number.isFinite(q.at)&&q.at>=s.time&&typeof q.type==="string"),"待办队列有过期或非法事件");
    return s;
  }
  function dueEvents(s, until) {
    // A delivered message may generate a reply before 'until'.
    // Drain recursively in chronological order so no past-due event remains.
    s.queue.sort((a,b)=>a.at-b.at||a.order-b.order);
    let processed=0;
    while(s.queue.length && s.queue[0].at<=until){
      assert(++processed<=2000,"单轮待办事件过多");
      const q=s.queue.shift();
      if(q.type==="deliver"){
        const n=NPCS.find(x=>x.id===q.to);
        if(!n) continue;
        s.npc[n.id].knowledge.push({at:q.at,topic:q.text,source:"player"});
        event(s,q.at,"发送给"+n.name+"的消息已经送达，但不意味着对方同意任何请求。","message");
        if(pseudorand(q.seed)>0.49){
          const responseAt=q.at+(15+Math.floor(pseudorand(q.seed+17)*90))*MINUTE;
          s.queue.push({type:"reply",at:responseAt,from:n.id,order:s.sequence+1});
        }
      } else if(q.type==="reply"){
        const n=NPCS.find(x=>x.id===q.from);
        if(!n) continue;
        const text=n.name+"：消息收到了。我还得处理自己的事情，具体情况之后再商量。";
        s.messages.push({at:q.at,from:n.id,content:text,grade:"S"});
        event(s,q.at,"你收到来自"+n.name+"的一条消息。","message");
      }
    }
    s.queue.sort((a,b)=>a.at-b.at||a.order-b.order);
  }
  function autonomousWorld(s, start, end) {
    const from=dayNumber(start), to=dayNumber(end);
    for(let day=from;day<=to;day++){
      for(let i=0;i<NPCS.length;i++){
        const n=NPCS[i], fraction=pseudorand(day*131+i*104729);
        const hour=7+Math.floor(fraction*11);
        const minute=Math.floor(pseudorand(day*79+i*4391)*60);
        const at=day*DAY-OFFSET+hour*HOUR+minute*MINUTE;
        if(at<=start||at>end) continue;
        const possibilities=[
          "围绕既有职业与责任整理一项待办（具体结果未知）",
          "为家庭或个人生活安排一段时间（具体细节未知）",
          "因既有约定调整计划（内容不自动公开）",
          "判断眼前事务尚无足够信息，暂不作出决定"
        ];
        const text=n.name+"："+possibilities[Math.floor(pseudorand(i+day*97)*possibilities.length)];
        s.npc[n.id].lastActivity={at,text,grade:"S"};
        s.world.push({at,npcId:n.id,text,grade:"S",visibility:"out_of_character"});
      }
    }
    if(s.world.length>1500) s.world=s.world.slice(-1500);
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
      const unknown=NPCS.filter(n=>!p.contacts.includes(n.id));
      if(!unknown.length){event(s,s.time,"你参加了一场S级公共活动。31名档案角色都已成为你的可联系对象。","scene");}
      else{
        const index=Math.floor(pseudorand(s.sequence*9137+dayNumber(s.time))*unknown.length);
        const n=unknown[index];
        p.contacts.push(n.id);
        p.knowledge.push({at:s.time,npc:n.id,topic:"在模拟公共活动中认识",grade:"S"});
        event(s,s.time,"模拟场景：你在"+p.district+"区的公共活动中认识"+n.name+"（"+n.occupation+"）。这次偶遇是新生成的S级情节，不能据此推断其现实住址或当日行踪。","contact");
      }
    }else if(kind==="message"){
      const to=validText(payload.recipient,8), text=validText(payload.text,200);
      assert(p.contacts.includes(to),"主角尚未建立该联系人关系");
      assert(text.length>0,"消息不能为空");
      assert(p.energy>=1,"精力不足");
      advance(s,5);p.energy-=1;
      const n=NPCS.find(x=>x.id===to);
      const delay=10+Math.floor(pseudorand(s.sequence*83+to.length)*35);
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
    makeGame,validateGame,act,summary,dayNumber,localDay});
});
