const test=require("node:test");
const assert=require("node:assert/strict");
const E=require("../engine.js");
const S=require("../society.js");
const F=require("../economy.js");
const A=require("../agent_ai.js");
const Sim=require("../simulation.js");
const create=()=>E.makeGame({name:"连续时钟测试",age:28,district:"顺义",start:"09:00",cash:""});
test("等待90分钟会分10分钟阶段运行独立决策与延期信息",()=>{
 const s=create(),at=s.time;
 Sim.advance(s,90);
 assert.equal(s.time,at+90*60000);
 assert.ok(Object.values(s.agentAI.minds).every(m=>m.thoughts>=1));
 assert.ok(S.ensure(s).cases.length>=1);
 assert.ok(S.ensure(s).cases.some(c=>c.status==="discussed"));
 assert.equal(s.player.knowledge.length,0);
 assert.ok(s.journal.some(x=>x.kind==="wait"&&x.visible));
});
test("同一输入与行动序列在独立分支中可重放",()=>{
 function run(){const s=create();Sim.advance(s,50);Sim.advance(s,140);return s;}
 assert.deepEqual(run(),run());
});
test("NPC暂停时仅推进时间，不偷偷执行自主行为",()=>{
 const s=create();A.ensure(s);E.act(s,"npc_autonomy",{enabled:false,detail:"balanced"});
 Sim.advance(s,120);
 assert.equal(Object.values(s.agentAI.minds).reduce((a,m)=>a+m.thoughts,0),0);
 assert.deepEqual(S.ensure(s).cases,[]);
 assert.equal(s.player.knowledge.length,0);
});
test("非法推进分钟数拒绝，正式存档不受修改",()=>{
 const s=create(),original=s.time;
 assert.throws(()=>Sim.advance(s,0),/1至480/);
 assert.throws(()=>Sim.advance(s,481),/1至480/);
 assert.throws(()=>Sim.advance(s,0.5),/1至480/);
 assert.equal(s.time,original);
});
test("没有显式S级资金条件，即使推进整天也不自动提款或报价",()=>{
 const s=create();Sim.advance(s,480);
 assert.equal(F.ensure(s).transfers.length,0);
 assert.equal(F.ensure(s).quotes.length,0);
 assert.deepEqual(F.audit(s),[]);
 assert.equal(s.player.cash,null);
});
