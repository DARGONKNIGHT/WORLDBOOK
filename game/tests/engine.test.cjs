/* node --test game/tests/engine.test.cjs · Browser game v2 */
const test=require("node:test");
const assert=require("node:assert/strict");
const E=require("../engine.js");
const create=(over={})=>E.makeGame({name:"测试角色",age:25,district:"海淀",occupation:"经营事务",cash:"200",start:"09:00",...over});
test("31名S级人物与世界书索引一致；样本村不是区",()=>{
 assert.equal(E.NPCS.length,31);
 assert.equal(E.NPCS[0].name,"陈国平");
 assert.equal(E.NPCS.at(-1).name,"范晴");
 assert.equal(E.DISTRICTS.includes("前礼务村"),false);
});
test("创建独立分支时无既定关系，保留正式世界书冻结",()=>{
 const s=create();
 assert.equal(s.schema,2);assert.equal(s.mode,"S_INDEPENDENT_PLAYTHROUGH");
 assert.equal(s.time,Date.parse("2026-10-09T09:00:00+08:00"));
 assert.deepEqual(s.player.contacts,[]);assert.deepEqual(s.player.met,[]);
 assert.equal(s.world.length,0);
});
test("未知现金保留null，负数与位置输入被拒",()=>{
 const s=create({cash:""});
 assert.equal(s.player.cash,null);
 assert.throws(()=>E.act(s,"travel",{destination:"朝阳",minutes:60,fare:7}),/未知/);
 assert.throws(()=>create({district:"前礼务村"}),/请选择/);
 assert.throws(()=>create({cash:-1}),/现金/);
});
test("区际时间后抵达，已知支出扣款，余额不足无移动",()=>{
 const s=create();const old=s.time;
 E.act(s,"travel",{destination:"丰台",minutes:60,fare:6});
 assert.equal(s.time,old+3600000);assert.equal(s.player.cash,194);
 assert.equal(s.player.district,"丰台");
 assert.throws(()=>E.act(s,"travel",{destination:"海淀",minutes:60,fare:300}),/资金不足/);
 assert.equal(s.player.district,"丰台");
});
test("人物白天事务、家庭和夜间休息优先",()=>{
 const s=create();
 const at=(hour)=>Date.parse("2026-10-09T"+String(hour).padStart(2,"0")+":30:00+08:00");
 assert.equal(E.plan(s,"P003",at(10)).kind,"work");
 assert.equal(E.plan(s,"P003",at(23)).kind,"sleep");
 assert.equal(E.plan(s,"P007",at(10)).kind,"school");
 assert.equal(E.plan(s,"P013",at(20)).kind,"family");
 assert.equal(E.plan(s,"P010",at(10)).location,"外省（未知）");
});
test("自主NPC在时间推进后独立决策且不自动分享秘密",()=>{
 const s=create();
 E.act(s,"wait",{minutes:240});
 assert.ok(s.world.length>15);
 assert.ok(s.world.every(x=>x.visibility==="out_of_character"&&x.grade==="S"));
 assert.equal(s.player.knowledge.length,0);
 assert.ok(s.npc.P003.decisions.length>0);
 assert.equal(s.npc.P003.stage.kind,"work");
});
test("已有家庭与同事网络自主联络，但消息不向玩家自动共享",()=>{
 const s=create({district:"顺义",start:"17:00"});
 E.act(s,"wait",{minutes:240}); // 17:00 → 21:00, family changes and sends peer messages
 const initiated=s.world.filter(x=>x.kind==="coordination");
 const delivered=s.world.filter(x=>x.kind==="peerDelivered");
 assert.ok(initiated.length>0);
 assert.ok(delivered.length>0);
 assert.ok(s.npc.P002.knowledge.some(x=>x.source==="P001")||s.npc.P006.knowledge.some(x=>x.source==="P005"));
 assert.equal(s.player.knowledge.length,0);
});
test("NPC开关与审计详细程度可控制，设置不消耗时间",()=>{
 const s=create(),at=s.time;
 E.act(s,"npc_autonomy",{enabled:false,detail:"detailed"});
 assert.equal(s.time,at);
 E.act(s,"wait",{minutes:120});assert.equal(s.world.length,0);
 E.act(s,"npc_autonomy",{enabled:true,detail:"detailed"});
 E.act(s,"wait",{minutes:120});assert.ok(s.world.length>=62);
});
test("交谈不自动变成联系人，拒绝交换后不允许骚扰",()=>{
 const s=create();s.player.met.push({id:"P030",at:s.time,district:"海淀"});
 assert.equal(s.player.contacts.length,0);
 E.act(s,"request_contact",{recipient:"P030"});
 assert.equal(s.player.contacts.length+s.player.declined.length,1);
 if(s.player.declined.length)assert.throws(()=>E.act(s,"request_contact",{recipient:"P030"}),/拒绝/);
 else assert.throws(()=>E.act(s,"request_contact",{recipient:"P030"}),/已经有/);
});
test("跨区或已经离开场景不能获得联系方式",()=>{
 const s=create();
 s.player.met.push({id:"P030",at:s.time,district:"海淀"});
 E.act(s,"travel",{destination:"朝阳",minutes:60,fare:0});
 assert.throws(()=>E.act(s,"request_contact",{recipient:"P030"}),/已离开/);
});
test("公共活动只能遇到同区且正处公开事务窗口的成年人",()=>{
 const s=create(),at=s.time;
 E.act(s,"social");
 for(const m of s.player.met){
   assert.equal(m.district,"海淀");
   assert.equal(E.districtFor(E.NPCS.find(x=>x.id===m.id)),"海淀");
   assert.ok(E.NPCS.find(x=>x.id===m.id).age>=18);
 }
 assert.equal(s.player.contacts.length,0);
 assert.equal(s.time,at+45*60000);
});
test("发送到送达不等于阅读，角色知识具有时间边界",()=>{
 const s=create();s.player.contacts.push("P014");
 E.act(s,"message",{recipient:"P014",text:"能借钱吗？"});
 assert.equal(s.npc.P014.knowledge.length,0);
 E.act(s,"wait",{minutes:480});
 assert.equal(s.npc.P014.knowledge.length,1);
 assert.ok(s.npc.P014.lastRead===null||s.npc.P014.lastRead>=s.npc.P014.knowledge[0].at);
 assert.ok(s.queue.every(x=>x.at>=s.time));
});
test("回答根据消息意图与责任选择，不是统一话术",()=>{
 const s=create();s.player.contacts.push("P014");
 for(let i=0;i<8;i++){
   E.act(s,"message",{recipient:"P014",text:i%2?"维修报价需要哪些信息":"能借钱给我吗"});
 }
 // P014 is on a hypothetical business shift; at 17:00 he may not have read.
 E.act(s,"wait",{minutes:480});
 E.act(s,"wait",{minutes:480});
 const replies=s.messages.map(x=>x.content);
 assert.ok(replies.length>0);
 assert.ok(replies.some(x=>/借款|转账|维修|故障|报价/.test(x)));
 assert.ok(!replies.some(x=>x.includes("消息收到了。我还得处理自己的事情")));
});
test("未认识不能私信，未建模的工作不会自动发钱",()=>{
 const s=create();
 assert.throws(()=>E.act(s,"message",{recipient:"P014",text:"你好"}),/尚未建立/);
 E.act(s,"work");
 assert.equal(s.player.cash,200);
});
test("旧版存档迁移保留日志、财产与原有联系人",()=>{
 const s=create();s.schema=1;delete s.autonomy;
 delete s.player.met;delete s.player.declined;
 s.player.contacts.push("P005");for(const n of E.NPCS){delete s.npc[n.id].stage;delete s.npc[n.id].decisions;delete s.npc[n.id].relation;}
 const migrated=E.upgradeGame(JSON.parse(JSON.stringify(s)));
 assert.equal(migrated.schema,2);
 assert.equal(migrated.player.cash,200);
 assert.deepEqual(migrated.player.contacts,["P005"]);
 assert.equal(migrated.npc.P005.relation,2);
});
test("存档往返确定性，无后台真实时间推进",()=>{
 function simulate(){
  const s=create();for(let i=0;i<50;i++){
    if(i%4===0)E.act(s,"rest");
    else if(i%4===1)E.act(s,"study");
    else if(i%4===2)E.act(s,"explore");
    else E.act(s,"wait",{minutes:240});
  }return s;
 }
 const a=simulate(),b=simulate();
 assert.deepEqual(a,b);
 assert.deepEqual(E.upgradeGame(JSON.parse(JSON.stringify(a))),a);
 assert.ok(a.world.length>0);
});
test("连续120次自主结算无冲突或过期待办",()=>{
 const s=create();s.player.contacts.push("P014");
 for(let i=0;i<120;i++){
  if(i%5===0)E.act(s,"message",{recipient:"P014",text:"事项"+i});
  else if(i%5===1)E.act(s,"rest");
  else if(i%5===2)E.act(s,"study");
  else if(i%5===3)E.act(s,"explore");
  else E.act(s,"wait",{minutes:480});
 }
 assert.equal(E.validateGame(s),s);
 assert.ok(s.queue.every(q=>q.at>=s.time));
 assert.ok(s.world.length>0);
});
