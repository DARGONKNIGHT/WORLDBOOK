const test=require("node:test");
const assert=require("node:assert/strict");
const E=require("../engine.js");
const S=require("../society.js");
const F=require("../economy.js");
const A=require("../agent_ai.js");
function setup(){
 const s=E.makeGame({name:"沙盒测试",age:25,district:"顺义",start:"09:00",cash:"",occupation:"经营"});
 A.ensure(s);F.ensure(s);S.ensure(s);
 A.commit(s,"P014",{choice:"coordinate_work",provider:"rules"});
 E.act(s,"wait",{minutes:15});
 A.commit(s,"P015",{choice:"review_case",provider:"rules"});
 E.act(s,"wait",{minutes:10});
 return s;
}
function stage(s,amount=120,owner=500,provider=50){
 const id=S.ensure(s).cases[0].id;
 F.opening(s,{caseId:id,priceYuan:amount,payerOpeningYuan:owner,providerOpeningYuan:provider});
 return id;
}
function offered(s){
 A.commit(s,"P015",{choice:"issue_quote",provider:"rules"});
 const id=F.ensure(s).quotes[0].id;
 E.act(s,"wait",{minutes:15});
 return id;
}
function accepted(s){
 const id=offered(s);
 A.commit(s,"P014",{choice:"accept_quote",provider:"rules"});
 E.act(s,"wait",{minutes:10});
 return id;
}
function reported(s){
 const id=accepted(s);
 A.commit(s,"P015",{choice:"report_work",provider:"rules"});
 E.act(s,"wait",{minutes:15});
 return id;
}
test("未讨论、信息未送达、无明确S级价格时禁止报价",()=>{
 const s=E.makeGame({name:"a",age:25,district:"顺义",start:"09:00",cash:""});
 A.ensure(s);
 assert.deepEqual(F.available(s,"P015"),[]);
 assert.throws(()=>F.opening(s,{caseId:"CASE-999",priceYuan:100,payerOpeningYuan:300,providerOpeningYuan:0}),/先完成/);
 assert.throws(()=>A.commit(s,"P015",{choice:"issue_quote",provider:"ollama"}),/候选行动之外/);
 assert.equal(F.ensure(s).quotes.length,0);
});
test("协商双方消息先后、已知关系和S级测试条件完整生效",()=>{
 const s=setup(),id=stage(s);
 assert.match(F.ensure(s).fixtures[id].source,/S_EXPLICIT/);
 assert.equal(s.player.cash,null);
 assert.equal(F.ensure(s).accounts.P014,50000);
 assert.equal(F.ensure(s).accounts.P015,5000);
 assert.ok(A.choices(s,"P015").options.some(x=>x.id==="issue_quote"));
 assert.throws(()=>F.opening(s,{caseId:id,priceYuan:120,payerOpeningYuan:500,providerOpeningYuan:50}),/已设定/);
 assert.deepEqual(F.audit(s),[]);
});
test("报价先送达，付款方才能同意或拒绝",()=>{
 const s=setup();stage(s);A.commit(s,"P015",{choice:"issue_quote",provider:"rules"});
 assert.equal(F.ensure(s).quotes[0].status,"offered");
 assert.equal(A.choices(s,"P014").options.some(x=>x.id==="accept_quote"),false);
 E.act(s,"wait",{minutes:15});
 assert.ok(A.choices(s,"P014").options.some(x=>x.id==="accept_quote"));
 assert.ok(A.choices(s,"P014").options.some(x=>x.id==="decline_quote"));
 A.commit(s,"P014",{choice:"decline_quote",provider:"ollama"});
 assert.equal(F.ensure(s).quotes[0].status,"declined");
 assert.equal(F.ensure(s).transfers.length,0);
 assert.throws(()=>F.settle(s,{quoteId:F.ensure(s).quotes[0].id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"}),/必须先确认/);
});
test("不足资金不能接受、不能自动借钱；拒绝可行",()=>{
 const s=setup();stage(s,600,500,0);const id=offered(s);
 assert.equal(A.choices(s,"P014").options.some(x=>x.id==="accept_quote"),false);
 assert.equal(A.choices(s,"P014").options.some(x=>x.id==="decline_quote"),true);
 assert.throws(()=>A.commit(s,"P014",{choice:"accept_quote",provider:"ollama"}),/候选行动之外/);
 assert.equal(F.ensure(s).accounts.P014,50000);
 assert.equal(F.ensure(s).quotes[0].id,id);
});
test("无人确认模拟履约时不能转账或将供应方自报完成当成证据",()=>{
 const s=setup();stage(s);const id=reported(s);
 assert.equal(F.getQuote(s,id).status,"reported");
 assert.throws(()=>F.settle(s,{quoteId:id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"}),/先确认模拟履约/);
 assert.throws(()=>F.verifyDelivery(s,{quoteId:id,confirmation:"real"}),/明确确认/);
 assert.equal(F.ensure(s).ledger.length,0);
});
test("经过明确核验和外视角授权后才产生双边守恒S级记账",()=>{
 const s=setup();stage(s,120,500,50);const id=reported(s);
 F.verifyDelivery(s,{quoteId:id,confirmation:"S_SIMULATED_DELIVERY_VERIFIED"});
 assert.equal(F.getQuote(s,id).status,"verified");
 assert.throws(()=>F.settle(s,{quoteId:id,confirmation:"NOT_APPROVED"}),/明确授权/);
 const before=F.ensure(s).accounts.P014+F.ensure(s).accounts.P015;
 const t=F.settle(s,{quoteId:id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"});
 assert.ok(t.txId.startsWith("TX-"));
 assert.equal(F.getQuote(s,id).status,"settled");
 assert.equal(F.ensure(s).accounts.P014,38000);
 assert.equal(F.ensure(s).accounts.P015,17000);
 assert.equal(F.ensure(s).accounts.P014+F.ensure(s).accounts.P015,before);
 assert.equal(F.ensure(s).ledger.length,2);
 assert.equal(F.ensure(s).transfers.length,1);
 assert.deepEqual(F.audit(s),[]);
 assert.throws(()=>F.settle(s,{quoteId:id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"}),/先确认模拟履约/);
 assert.equal(s.player.cash,null);
 assert.equal(s.player.knowledge.length,0);
});
test("模拟账本、报价、人物记忆和时间经过JSON保存恢复后保持一致",()=>{
 const s=setup();stage(s);const id=reported(s);
 F.verifyDelivery(s,{quoteId:id,confirmation:"S_SIMULATED_DELIVERY_VERIFIED"});
 F.settle(s,{quoteId:id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"});
 const copy=JSON.parse(JSON.stringify(s));
 E.validateGame(copy);A.ensure(copy);S.ensure(copy);F.ensure(copy);
 assert.deepEqual(copy.economy,s.economy);
 assert.deepEqual(F.audit(copy),[]);
 assert.equal(copy.society.cases[0].status,"discussed");
});
test("有明确工作事务但无经济假设仍只可以协商，不得自动生成工资、合同或付款",()=>{
 const s=setup();
 for(let i=0;i<8;i++){
  E.act(s,"wait",{minutes:30});
  A.runRules(s,31);
 }
 assert.equal(F.ensure(s).quotes.length,0);
 assert.equal(F.ensure(s).ledger.length,0);
 assert.equal(F.ensure(s).transfers.length,0);
 assert.equal(s.player.cash,null);
});
test("余额单方篡改即使历史借贷平衡也会被发现并拒绝继续结算",()=>{
 const s=setup();stage(s);const id=reported(s);
 F.verifyDelivery(s,{quoteId:id,confirmation:"S_SIMULATED_DELIVERY_VERIFIED"});
 F.ensure(s).accounts.P014+=100;
 assert.ok(F.audit(s).some(x=>x.includes("does not reconcile")));
 assert.throws(()=>F.settle(s,{quoteId:id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"}),/审计失败/);
 assert.equal(F.ensure(s).ledger.length,0);
});
test("即使双方账本守恒，篡改交易价格或收款身份仍被审计拒绝",()=>{
 const s=setup();stage(s,120,500,50);const id=reported(s);
 F.verifyDelivery(s,{quoteId:id,confirmation:"S_SIMULATED_DELIVERY_VERIFIED"});
 F.settle(s,{quoteId:id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"});
 F.ensure(s).transfers[0].amountCents=1;
 assert.ok(F.audit(s).some(x=>x.includes("agreed quote")));
});
test("审计能检测存档篡改造成的失衡条目",()=>{
 const s=setup();stage(s);const id=reported(s);
 F.verifyDelivery(s,{quoteId:id,confirmation:"S_SIMULATED_DELIVERY_VERIFIED"});
 F.settle(s,{quoteId:id,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"});
 F.ensure(s).ledger[0].deltaCents=-1;
 assert.ok(F.audit(s).some(x=>x.includes("unbalanced")));
});
