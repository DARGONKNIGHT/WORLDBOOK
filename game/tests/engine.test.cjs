/* node --test game/tests/engine.test.cjs  ·  无第三方依赖 */
const test=require("node:test");
const assert=require("node:assert/strict");
const E=require("../engine.js");
const create=(overrides={})=>E.makeGame({name:"测试角色",age:25,district:"海淀",occupation:"经营事务",cash:"200",start:"09:00",...overrides});
test("31位NPC均来自世界书索引，样本村不是可选玩家出生地",()=>{
  assert.equal(E.NPCS.length,31);
  assert.equal(E.NPCS[0].name,"陈国平");
  assert.equal(E.NPCS[30].name,"范晴");
  assert.equal(E.DISTRICTS.includes("前礼务村"),false);
});
test("游戏从用户创建角色开始；原始世界书不存在于该运行状态",()=>{
  const s=create();
  assert.equal(s.time,Date.parse("2026-10-09T09:00:00+08:00"));
  assert.equal(s.player.district,"海淀");
  assert.equal(s.player.contacts.length,0);
  assert.equal(s.world.length,0);
  assert.equal(s.mode,"S_INDEPENDENT_PLAYTHROUGH");
});
test("未知现金保持null，不能默认为零",()=>{
  const s=create({cash:""});
  assert.equal(s.player.cash,null);
  assert.throws(()=>E.act(s,"travel",{destination:"朝阳",minutes:60,fare:5}),/未知/);
});
test("校验不允许未成年角色、负资金与非北京区域",()=>{
  assert.throws(()=>create({age:8}),/年龄/);
  assert.throws(()=>create({cash:-1}),/现金/);
  assert.throws(()=>create({district:"前礼务村"}),/请选择/);
});
test("旅行先消耗时间，抵达后变更地点；资金不足拒绝",()=>{
  const s=create();const start=s.time;
  E.act(s,"travel",{destination:"丰台",minutes:80,fare:8});
  assert.equal(s.time,start+80*60000);
  assert.equal(s.player.district,"丰台");
  assert.equal(s.player.cash,192);
  assert.equal(s.journal.at(-1).kind,"arrival");
  assert.throws(()=>E.act(s,"travel",{destination:"海淀",minutes:60,fare:300}),/不足/);
  assert.equal(s.player.district,"丰台");
});
test("工作不自动生成工资、养老金和合同",()=>{
  const s=create();
  E.act(s,"work");
  assert.equal(s.player.cash,200);
  assert.equal(s.time,Date.parse("2026-10-09T11:00:00+08:00"));
  const unknown=create({occupation:""});
  assert.throws(()=>E.act(unknown,"work"),/职业/);
});
test("消息不能发给陌生人，发送与送达分离",()=>{
  const s=create();
  assert.throws(()=>E.act(s,"message",{recipient:"P001",text:"你好"}),/尚未建立/);
  E.act(s,"social");const id=s.player.contacts[0];
  E.act(s,"message",{recipient:id,text:"你好"});
  assert.equal(s.npc[id].knowledge.length,0);
  E.act(s,"wait",{minutes:480});
  assert.equal(s.npc[id].knowledge.length,1);
  assert.equal(s.npc[id].knowledge[0].topic,"你好");
  assert.ok(s.queue.every(e=>e.at>=s.time));
});
test("NPC只在时钟推进后自主生成后台动作，知识不自动共享",()=>{
  const s=create();E.act(s,"wait",{minutes:480});
  assert.ok(s.world.length>0);
  assert.equal(s.player.knowledge.length,0);
  assert.ok(s.world.every(x=>x.visibility==="out_of_character"&&x.grade==="S"));
});
test("跨多次推进的回复队列保持时间有序",()=>{
  const s=create();
  E.act(s,"social");const id=s.player.contacts[0];
  for(let i=0;i<16;i++)E.act(s,"message",{recipient:id,text:"事件"+i});
  E.act(s,"wait",{minutes:480});
  assert.ok(s.queue.every(x=>x.at>=s.time));
  assert.equal(s.npc[id].knowledge.length,16);
});
test("相同输入与序列产生确定性重放",()=>{
  function run(){
    const s=create();
    for(const kind of ["social","study","rest","explore","wait"])E.act(s,kind,kind==="wait"?{minutes:480}:{});
    return s;
  }
  assert.deepEqual(run(),run());
});
test("JSON导出再导入可恢复，篡改结构拒绝",()=>{
  const s=create();E.act(s,"social");
  const copy=JSON.parse(JSON.stringify(s));
  assert.deepEqual(E.validateGame(copy),s);
  delete copy.npc.P031;
  assert.throws(()=>E.validateGame(copy),/NPC/);
});
test("120步连续操作无需服务端，结果依旧可验",()=>{
  const s=create();
  E.act(s,"social");
  const id=s.player.contacts[0];
  for(let i=0;i<120;i++){
    if(i%5===0)E.act(s,"message",{recipient:id,text:"第"+i+"条"});
    else if(i%5===1)E.act(s,"rest");
    else if(i%5===2)E.act(s,"explore");
    else if(i%5===3)E.act(s,"study");
    else E.act(s,"wait",{minutes:480});
  }
  assert.ok(s.world.length>=31);
  assert.ok(s.time>Date.parse("2026-10-10T00:00:00+08:00"));
  assert.equal(E.validateGame(s),s);
});