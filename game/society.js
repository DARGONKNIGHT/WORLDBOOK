/* Bounded social execution in independent S-grade simulation, not real contract/payment. */
(function(root,factory){
  const api=factory(typeof module==="object"&&module.exports?require("./engine.js"):root.EarthGame);
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.EarthSociety=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(E){
  "use strict";
  const MINUTE=60000,DAY=86400000;
  const TIES={
    P001:{to:"P002",type:"family"},P002:{to:"P001",type:"family"},
    P005:{to:"P006",type:"family"},P006:{to:"P005",type:"family"},
    P008:{to:"P009",type:"family"},P009:{to:"P008",type:"family"},
    P011:{to:"P013",type:"work"},P013:{to:"P011",type:"work"},
    P014:{to:"P015",type:"work"},P015:{to:"P014",type:"work"}
  };
  const VALID=new Set(E.NPCS.map(n=>n.id));
  function assert(ok,msg){if(!ok)throw Error(msg);}
  function ensure(s){
    assert(s&&s.npc&&Number.isFinite(s.time),"世界存档不可用");
    if(!s.society||s.society.version!==1)s.society={
      version:1,serial:0,cases:[],history:[],recent:{},moneyTransfers:[]
    };
    return s.society;
  }
  function tieFor(actor){return TIES[actor]||null;}
  function caseFor(s,actor){
    return ensure(s).cases.find(c=>(c.to===actor||c.from===actor)&&c.status==="awaiting_response")||null;
  }
  function opportunities(s,actor,at=s.time){
    ensure(s);
    const tie=tieFor(actor);
    if(!tie)return [];
    const relevant=E.plan(s,actor,at).kind===tie.type;
    const pending=caseFor(s,actor);
    if(pending && pending.to===actor && relevant && s.npc[actor].knowledge.some(k=>k.source===pending.from && String(k.topic).includes(pending.id))){
      return [{id:"review_case",label:"审查收到的协商请求后决定回应"}];
    }
    const day=E.localDay(at),last=ensure(s).recent[actor];
    if(!pending && relevant && last!==day)return [{
      id:tie.type==="family"?"coordinate_family":"coordinate_work",
      label:tie.type==="family"?"向已知家人提出事务协调":"向已知同事提出事务协调"
    }];
    return [];
  }
  function log(s,record){
    const w=ensure(s),n=E.NPCS.find(x=>x.id===record.npcId);
    const line={...record,at:s.time,grade:"S",visibility:"out_of_character",kind:"society",
      text:(n?n.name:"NPC")+" · "+record.text};
    w.history.push(line);if(w.history.length>320)w.history.shift();
    s.world.push(line);if(s.world.length>4000)s.world.shift();
    return line;
  }
  function apply(s,actor,action){
    const w=ensure(s),tie=tieFor(actor);
    assert(tie&&VALID.has(actor)&&VALID.has(tie.to),"人物没有已确认的关系网");
    assert(opportunities(s,actor).some(x=>x.id===action),"当前日程、信息或事件阶段不允许执行此行动");
    if(action==="coordinate_family"||action==="coordinate_work"){
      const type=action==="coordinate_family"?"family":"work";
      assert(tie.type===type,"不能越权建立事务关系");
      const id="CASE-"+String(++w.serial).padStart(5,"0"),day=E.localDay(s.time);
      // Purpose is deliberately generic. No unknown employer, customer, account or address is created.
      const title=type==="family"?"协商既有家庭责任与可用时间":"协商既有工作分工与可用时间";
      const c={id,type,from:actor,to:tie.to,title,status:"awaiting_response",
        createdAt:s.time,respondedAt:null,result:null,grade:"S",amountCents:null,contractId:null,
        deliveries:0};
      w.cases.push(c);
      if(w.cases.length>500)w.cases.shift();
      w.recent[actor]=day;
      s.queue.push({type:"peerDeliver",at:s.time+15*MINUTE,from:actor,to:tie.to,
        text:id+"："+title+"；尚无约定或同意。",order:s.sequence+w.serial});
      return log(s,{npcId:actor,caseId:id,action,text:"提出"+id+"，等待"+E.NPCS.find(x=>x.id===tie.to).name+"收到并决定；尚无合同、工资或付款。"});
    }
    const c=caseFor(s,actor);
    assert(c&&c.to===actor,"没有可以回应的协商事项");
    // Informal response, NOT an enforceable agreement; leave concrete commitment unknown.
    const result=E.plan(s,actor).kind==="family"?"愿意继续商量，具体时间待确认":"建议进一步核对岗位与时间安排";
    c.status="discussed";c.respondedAt=s.time;c.result=result;
    s.queue.push({type:"peerDeliver",at:s.time+10*MINUTE,from:actor,to:c.from,
      text:c.id+"："+result+"；不构成正式合同或完成工作。",order:s.sequence+w.serial+1});
    return log(s,{npcId:actor,caseId:c.id,action,text:"已审阅"+c.id+"，回复："+result+"。尚未自动执行任何财务、合同或到场行为。"});
  }
  function audit(s){
    const w=ensure(s),problems=[];
    const ids=w.cases.map(x=>x.id);
    if(ids.length!==new Set(ids).size)problems.push("duplicate case id");
    for(const c of w.cases){
      if(!TIES[c.from]||TIES[c.from].to!==c.to)problems.push("invalid tie "+c.id);
      if(!["awaiting_response","discussed"].includes(c.status))problems.push("bad status "+c.id);
      if(c.amountCents!==null||c.contractId!==null)problems.push("unverified financial/contract mutation "+c.id);
      if(c.respondedAt!==null&&c.respondedAt<c.createdAt)problems.push("backdated response "+c.id);
    }
    return problems;
  }
  return Object.freeze({ensure,tieFor,caseFor,opportunities,apply,audit});
});
