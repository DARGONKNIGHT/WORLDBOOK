const test=require("node:test");
const assert=require("node:assert/strict");
const E=require("../engine.js"),S=require("../society.js"),A=require("../agent_ai.js");
const Sim=require("../simulation.js");
const t0=2000000000000;
const fresh=()=>E.makeGame({name:"无回合测试",age:27,district:"顺义",start:"09:00",cash:"",occupation:"自营工作"});
test("创建玩家后世界自动进入持续墙钟模式，无需点击等待",()=>{
 const s=fresh(),start=s.time;
 const live=Sim.ensureLive(s,t0);
 assert.equal(live.running,true);
 assert.equal(live.rate,1);
 Sim.syncLive(s,t0+60000);
 assert.equal(s.time,start+60000);
 assert.ok(E.NPCS.some(n=>s.agentAI.minds[n.id].thoughts>0));
 assert.ok(s.journal.every(x=>x.kind!=="wait"));
});
test("玩家可在NPC世界运行时发起工作，工作不会瞬间消耗两小时",()=>{
 const s=fresh();Sim.ensureLive(s,t0);const start=s.time;
 const task=Sim.startTask(s,"work",{},t0);
 assert.equal(s.time,start);
 assert.equal(s.player.energy,80);
 assert.equal(task.endsAt-start,120*60000);
 Sim.syncLive(s,t0+60*60000);
 assert.equal(s.time,start+60*60000);
 assert.equal(s.player.energy,80);
 assert.ok(Object.values(s.agentAI.minds).some(m=>m.thoughts>=1));
 Sim.syncLive(s,t0+120*60000);
 assert.equal(s.live.task,null);
 assert.equal(s.player.energy,58);
 assert.ok(s.journal.some(j=>j.kind==="work"));
});
test("出行期间不能瞬间抵达，也不能同时完成第二项现场行动",()=>{
 const s=fresh();Sim.ensureLive(s,t0);
 const start=s.player.district;
 Sim.startTask(s,"travel",{destination:"海淀",minutes:40,fare:0},t0);
 assert.equal(s.player.district,start);
 assert.throws(()=>Sim.startTask(s,"explore",{},t0+2000),/另一项/);
 Sim.syncLive(s,t0+20*60000);
 assert.equal(s.player.district,start);
 Sim.syncLive(s,t0+40*60000);
 assert.equal(s.player.district,"海淀");
});
test("打断正在进行的行动不会逆转NPC已发生的事件或领取未完成收益",()=>{
 const s=fresh();Sim.ensureLive(s,t0);
 Sim.startTask(s,"rest",{},t0);
 Sim.syncLive(s,t0+20*60000);
 const at=s.time,recorded=s.world.length;
 Sim.interruptTask(s,t0+20*60000);
 assert.equal(s.player.energy,88); // 20/60 of a rest yields part of the benefit
 assert.equal(s.time,at);
 assert.equal(s.world.length,recorded);
 Sim.startTask(s,"explore",{},t0+20*60000);
 Sim.syncLive(s,t0+55*60000);
 assert.equal(s.player.energy,82);
 assert.equal(s.live.interrupted,1);
 assert.ok(s.journal.some(j=>j.kind==="action_interrupted"));
});
test("取消一小时未完成工作仍扣除对应比例精力，但不产生收入或完成日志",()=>{
 const s=fresh();Sim.ensureLive(s,t0);Sim.startTask(s,"work",{},t0);
 Sim.syncLive(s,t0+60*60000);Sim.interruptTask(s,t0+60*60000);
 assert.equal(s.player.energy,69);
 assert.ok(!s.journal.some(j=>j.kind==="work"));
 assert.equal(s.player.cash,null);
});
test("角色无法利用等待回合跳跃；NPC和玩家按同一时间轴结算",()=>{
 const s=fresh();Sim.ensureLive(s,t0);
 assert.throws(()=>Sim.startTask(s,"wait",{minutes:120},t0),/不能建立持续日程/);
 const original=s.time;
 Sim.syncLive(s,t0+990);
 assert.equal(s.time,original);
 Sim.syncLive(s,t0+61000);
 assert.equal(s.time,original+60000);
});
test("重启/存档恢复会基于上次真实时间继续追算，不重复第一段时间",()=>{
 const s=fresh();Sim.ensureLive(s,t0);Sim.syncLive(s,t0+35000);
 const copy=JSON.parse(JSON.stringify(s));
 assert.equal(copy.live.carryMs,35000);
 Sim.syncLive(copy,t0+85000);
 assert.equal(copy.time,s.time+60000);
 Sim.syncLive(copy,t0+85000);
 assert.equal(copy.time,s.time+60000);
 E.validateGame(copy);
});
test("现实时间倒拨不可回溯历史；离线追算过长明确登记未知空白",()=>{
 const s=fresh();Sim.ensureLive(s,t0);const at=s.time;
 Sim.syncLive(s,t0-60000);
 assert.equal(s.time,at);
 const result=Sim.syncLive(s,t0+12*60*60000);
 assert.equal(result.advancedMinutes,480);
 assert.equal(s.live.omittedMinutes,240);
 assert.ok(s.journal.some(j=>j.kind==="catchup_limit"));
});
test("无回合下玩家可随时改变模型速度，模型运行与实际墙钟连续",()=>{
 const s=fresh();Sim.ensureLive(s,t0);
 Sim.setRate(s,60,t0);
 Sim.syncLive(s,t0+1000);
 assert.equal(s.time,Date.parse("2026-10-09T09:01:00+08:00"));
 Sim.setRate(s,1,t0+1000);
 Sim.syncLive(s,t0+61000);
 assert.equal(s.time,Date.parse("2026-10-09T09:02:00+08:00"));
});
test("管理员调试停止与恢复不产生虚构离线历史",()=>{
 const s=fresh();Sim.ensureLive(s,t0);
 Sim.stopLive(s,t0+60000);
 const at=s.time;
 Sim.syncLive(s,t0+900000);
 assert.equal(s.time,at);
 Sim.resumeLive(s,t0+900000);
 Sim.syncLive(s,t0+960000);
 assert.equal(s.time,at+60000);
});
test("场景任务被用户中途打断后仍会保存、信息边界不受破坏",()=>{
 const s=fresh();Sim.ensureLive(s,t0);
 Sim.startTask(s,"explore",{},t0);
 Sim.syncLive(s,t0+11*60000);
 const copy=JSON.parse(JSON.stringify(s));
 Sim.ensureLive(copy,t0+11*60000);
 Sim.interruptTask(copy,t0+11*60000);
 assert.equal(copy.live.task,null);
 assert.deepEqual(copy.player.knowledge,[]);
 assert.ok(S.ensure(copy).cases.length>=0);
});
