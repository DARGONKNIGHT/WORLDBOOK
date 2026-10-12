const test=require("node:test");
const assert=require("node:assert/strict");
const E=require("../engine.js");
const A=require("../agent_ai.js");
const create=()=>E.makeGame({name:"游戏测试",age:25,district:"海淀",start:"09:00",cash:"",occupation:"开发"});
test("31名人物独立持有目标、需求、隐私记忆和决策计划",()=>{
 const s=create(),x=A.ensure(s);
 assert.equal(Object.keys(x.minds).length,31);
 assert.notEqual(x.minds.P001,x.minds.P002);
 assert.ok(x.minds.P001.goals.length>0);
 assert.deepEqual(x.minds.P001.memory,[]);
 assert.equal(x.realtime,false);
});
test("无人浏览游戏操作时不会自行推进世界钟",()=>{
 const s=create();A.ensure(s);
 assert.equal(s.time,Date.parse("2026-10-09T09:00:00+08:00"));
 assert.equal(s.world.length,0);
});
test("模型只能从岗位日程允许的候选行动中选择",()=>{
 const s=create();A.ensure(s);
 const work=A.choices(s,"P003");
 assert.ok(work.options.some(x=>x.id==="continue_work"));
 assert.ok(!work.options.some(x=>x.id==="sleep"));
 assert.throws(()=>A.commit(s,"P003",{choice:"transfer_money",reason:"马上汇款",provider:"ollama"}),/候选行动之外/);
 assert.equal(s.player.cash,null);
});
test("夜间不允许模型要求工作或绕过学校/监护",()=>{
 const s=create();A.ensure(s);
 E.act(s,"background_tick",{minutes:10});
 E.act(s,"wait",{minutes:480});
 E.act(s,"wait",{minutes:360});
 const child=A.choices(s,"P007");
 assert.ok(!child.options.some(x=>["continue_work","transfer_money","check_relatives"].includes(x.id)));
 const options=A.choices(s,"P003").options;
 assert.ok(options.length>0);
});
test("对模型只披露该NPC个人已知消息，其他人的消息保持隔离",()=>{
 const s=create();A.ensure(s);
 s.npc.P002.knowledge.push({at:s.time,topic:"私密家庭事项",source:"P001"});
 const snap=A.snapshot(s,"P005");
 assert.equal(snap.known_messages.length,0);
 assert.ok(!JSON.stringify(snap).includes("私密家庭事项"));
 assert.equal(snap.source_grade,"S");
 assert.ok(snap.candidates.every(x=>typeof x.id==="string"));
});
test("实际模型选择写入带提供者标签的私有审计而不改主角知识",()=>{
 const s=create();A.ensure(s);
 const candidate=A.choices(s,"P003").options[0].id;
 const out=A.commit(s,"P003",{choice:candidate,provider:"ollama",reason:"当前工作责任优先"},s.time);
 assert.equal(out.provider,"ollama");
 assert.equal(s.agentAI.minds.P003.history[0].choice,candidate);
 assert.equal(s.player.knowledge.length,0);
 assert.equal(s.world.at(-1).visibility,"out_of_character");
});
test("缺失/过期/倒序推理一律拒绝，状态不写入",()=>{
 const s=create();A.ensure(s);const at=s.time;
 E.act(s,"wait",{minutes:70});
 const candidate=A.choices(s,"P003").options[0].id;
 assert.throws(()=>A.commit(s,"P003",{choice:candidate,provider:"ollama"},at),/过期/);
 assert.equal(s.agentAI.minds.P003.thoughts,0);
});
test("模型响应若跨越不可变的日程界限则丢弃，而非伪造到岗",()=>{
 const s=create();A.ensure(s);const start=s.time;
 const first=A.choices(s,"P003",start).options.find(x=>x.id==="continue_work");
 assert.ok(first);
 E.act(s,"wait",{minutes:240}); // 09:00 to 13:00; still work.
 assert.throws(()=>A.commit(s,"P003",{choice:first.id,provider:"ollama"},start),/过期/);
});
test("已知亲属/同事协商使用延迟消息而非瞬时共享",()=>{
 const s=create();A.ensure(s);
 E.act(s,"wait",{minutes:480});
 const at=s.time;
 const allowed=A.choices(s,"P001").options.map(x=>x.id);
 if(allowed.includes("check_relatives")){
  const before=s.npc.P002.knowledge.length;
  A.commit(s,"P001",{choice:"check_relatives",provider:"rules",reason:"主动联络家人"});
  const pending=s.queue.filter(q=>q.type==="peerDeliver"&&q.from==="P001");
  assert.ok(pending.some(q=>q.at>at));
  assert.equal(s.npc.P002.knowledge.length,before);
 }
});
test("实时刻钟可以推进，无需每分钟写一条玩家日志",()=>{
 const s=create();A.ensure(s);const start=s.time,logs=s.journal.length;
 E.act(s,"background_tick",{minutes:10});
 assert.equal(s.time-start,600000);
 assert.equal(s.journal.length,logs);
});
test("连续自主思考、私有记忆限长并能JSON恢复",()=>{
 const s=create();A.ensure(s);
 A.settings(s,{realtime:true,speed:10,mode:"rules"});
 for(let i=0;i<260;i++){
  E.act(s,"background_tick",{minutes:10});
  A.runRules(s,8);
 }
 const thoughts=Object.values(s.agentAI.minds).reduce((sum,x)=>sum+x.thoughts,0);
 assert.ok(thoughts>=31);
 assert.ok(Object.values(s.agentAI.minds).every(x=>x.memory.length<=12));
 const copy=JSON.parse(JSON.stringify(s));
 E.validateGame(copy);A.ensure(copy);
 assert.deepEqual(copy.agentAI.minds.P001,s.agentAI.minds.P001);
});
test("设置限制模式速度及持续运行显式开关",()=>{
 const s=create();A.ensure(s);
 assert.throws(()=>A.settings(s,{speed:999}),/实时速度/);
 assert.throws(()=>A.settings(s,{mode:"unsupported"}),/推理后端/);
 A.settings(s,{speed:5,mode:"ollama",realtime:true});
 assert.equal(s.agentAI.mode,"ollama");
 assert.equal(s.agentAI.realtime,true);
});
