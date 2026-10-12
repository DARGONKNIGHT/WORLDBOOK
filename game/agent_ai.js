/* Game 3.0: bounded agent cognition, optional model arbitration.
 * Local rules are NOT an LLM. Ollama can propose a constrained choice via agent_server.py.
 * S-grade characters, goals, memories and locations are synthetic, not real people.
 */
(function(root,factory){
  const api=factory(typeof module==="object"&&module.exports?require("./engine.js"):root.EarthGame,
    typeof module==="object"&&module.exports?require("./society.js"):root.EarthSociety,
    typeof module==="object"&&module.exports?require("./economy.js"):root.EarthEconomy);
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.EarthAgents=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(E,S,F){
  "use strict";
  const MINUTE=60000,MAX_MEMORY=12;
  const TIES={
    P001:"P002",P002:"P001",P003:"P002",P004:"P001",
    P005:"P006",P006:"P005",P008:"P009",P009:"P008",
    P010:"P008",P011:"P013",P013:"P011",P014:"P015",P015:"P014"
  };
  const ACTIONS={
    work:["continue_work","short_break"],
    family:["family_care","check_relatives","rest"],
    personal:["personal_planning","rest","check_relatives","defer"],
    rest:["recover","personal_planning"],
    errand:["run_errand","defer","rest"],
    sleep:["sleep"],
    school:["attend_school"]
  };
  const LABEL={
    continue_work:"继续完成原有工作",short_break:"在既有工作间隙短暂休息",
    family_care:"处理既有家庭事务",check_relatives:"联系已知亲友/同事",
    rest:"安排个人休息",personal_planning:"整理私事与下一步计划",
    defer:"暂缓非紧急事务",recover:"恢复体力与调整作息",
    run_errand:"处理力所能及的日常杂务",sleep:"按作息休息",
    attend_school:"遵循当前教育/监护安排",
    coordinate_family:"提出家庭事务协调",coordinate_work:"提出工作事务协调",review_case:"审阅待处理的协商消息",
    issue_quote:"提出已有价格假设的合作报价",accept_quote:"审阅并原则同意报价",decline_quote:"拒绝当前报价",
    report_work:"报告模拟合作事项，等待核验"
  };
  const GOALS={
    F01:["兼顾家庭责任","保持生活事务稳定"],F02:["稳定职业责任","照顾家庭"],
    F03:["协调生活和工作","维持已知亲属关系"],F04:["保持工作质量","保留个人时间"],
    F05:["合理完成已接事务","维护工作信用"],
    E01:["处理既有经营或生活任务","保留必要休息"],
    E02:["完成岗位责任","避免时间冲突"],E03:["协调服务/运输事务","合理安排休息"],
    E04:["履行职业与家庭责任","重视个人休息"]
  };
  const within=(n,a,b)=>Number.isFinite(n)&&n>=a&&n<=b;
  const guard=(v,m)=>{if(!v)throw Error(m);};
  function stable(id){return Number(id.slice(1));}
  function newMind(n,now){
    return {id:n.id,goals:[...(GOALS[n.group]||["维持日常生活"])],
      needs:{rest:40+(stable(n.id)*11)%37,social:30+(stable(n.id)*7)%31},
      memory:[],lastAt:null,nextAt:now+(stable(n.id)-1)*MINUTE,
      intent:null,thoughts:0,history:[],lastPeerAt:null};
  }
  function ensure(s){
    guard(s&&s.player&&s.npc&&Number.isFinite(s.time),"存档不存在");
    if(!s.agentAI||s.agentAI.version!==1){
      s.agentAI={version:1,mode:"rules",realtime:false,speed:1,
        minds:Object.fromEntries(E.NPCS.map(n=>[n.id,newMind(n,s.time)]))};
    }else{
      for(const n of E.NPCS)if(!s.agentAI.minds[n.id])s.agentAI.minds[n.id]=newMind(n,s.time);
    }
    return s.agentAI;
  }
  function choices(s,id,at=s.time){
    ensure(s);
    const n=E.NPCS.find(x=>x.id===id);guard(n,"人物不存在");
    const stage=E.plan(s,id,at);
    let options=[...(ACTIONS[stage.kind]||["defer"])];
    if(!TIES[id])options=options.filter(x=>x!=="check_relatives");
    // A child cannot enter contractual work, make payments, or bypass guardians.
    if(n.age<18)options=options.filter(x=>!["continue_work","check_relatives"].includes(x));
    options.push(...S.opportunities(s,id,at).map(x=>x.id));
    options.push(...F.available(s,id,at).map(x=>x.id));
    return {npc:n,stage,options:options.map(id=>({id,label:LABEL[id]}))};
  }
  function snapshot(s,id,at=s.time){
    const mind=ensure(s).minds[id],c=choices(s,id,at),priv=s.npc[id];
    return {
      npc_id:id,name:c.npc.name,age:c.npc.age,occupation:c.npc.occupation,
      time:E.clock(at),location:c.stage.location,obligation:c.stage.kind,
      schedule_reason:c.stage.reason,goals:[...mind.goals],needs:{...mind.needs},
      known_messages:priv.knowledge.slice(-4).map(x=>({topic:String(x.topic).slice(0,160),source:x.source})),
      memories:mind.memory.slice(-4).map(x=>x.text),intent:mind.intent,
      candidates:c.options,source_grade:"S"
    };
  }
  function chooseRules(s,id,at=s.time){
    const c=choices(s,id,at),m=ensure(s).minds[id],p=stable(id);
    let best=null;
    const weight=(item)=>{
      let score=5+((p*37+Math.floor(at/(30*MINUTE))+item.id.length*19)%9);
      if(["sleep","attend_school","continue_work","family_care"].includes(item.id))score+=50;
      if(item.id==="rest"||item.id==="recover")score+=Math.round(m.needs.rest*0.65);
      if(item.id==="check_relatives")score+=Math.round(m.needs.social*0.45);
      if(item.id==="short_break")score+=m.needs.rest>70?20:0;
      if(item.id==="defer")score+=12;
      if(item.id==="review_case")score+=100;
      if(["issue_quote","accept_quote","report_work"].includes(item.id))score+=95;
      if(item.id==="decline_quote")score+=34;
      if(item.id==="coordinate_family"||item.id==="coordinate_work")score+=75;
      if(m.intent===item.id)score-=8;
      return score;
    };
    for(const item of c.options){const score=weight(item);if(!best||score>best.score)best={choice:item.id,score};}
    return {choice:best.choice,reason:"先检查"+c.stage.kind+"时段责任，再比较个人休息、联系需求与可选事项；没有超出已知条件的授权。",provider:"rules"};
  }
  function remember(m,at,text){m.memory.push({at,text:String(text).slice(0,180)});if(m.memory.length>MAX_MEMORY)m.memory.shift();}
  function commit(s,id,result,observedAt=s.time){
    const ai=ensure(s),m=ai.minds[id];
    guard(typeof result==="object"&&result!==null,"模型输出无效");
    guard(within(observedAt,s.time-60*MINUTE,s.time),"过期决策不写入世界");
    guard(E.plan(s,id,observedAt).kind===E.plan(s,id,s.time).kind,"人物当前日程已变化，旧模型结果已丢弃");
    const allowed=choices(s,id,s.time).options.map(x=>x.id);
    guard(allowed.includes(result.choice),"候选行动之外的命令被拒绝");
    const source=result.provider==="ollama"?"ollama":"rules";
    if(["coordinate_family","coordinate_work","review_case"].includes(result.choice))S.apply(s,id,result.choice);
    if(["issue_quote","accept_quote","decline_quote","report_work"].includes(result.choice))F.apply(s,id,result.choice);
    const reason=String(result.reason||"没有追加理由").replace(/[\r\n\t]+/g," ").slice(0,180);
    const now=s.time,prev=m.lastAt,elapsed=prev===null?30:Math.max(1,Math.min(120,Math.round((now-prev)/MINUTE)));
    m.needs.rest=Math.max(0,Math.min(100,m.needs.rest+Math.round(elapsed/7)-(result.choice==="rest"||result.choice==="sleep"||result.choice==="recover"?27:0)));
    m.needs.social=Math.max(0,Math.min(100,m.needs.social+Math.round(elapsed/11)-(result.choice==="check_relatives"?24:0)));
    m.intent=result.choice;m.lastAt=now;m.nextAt=now+30*MINUTE;m.thoughts++;
    const item={at:now,npcId:id,kind:"agent_decision",action:result.choice,
      text:E.NPCS.find(n=>n.id===id).name+" 自主决定："+LABEL[result.choice]+"；依据："+reason,
      reason,provider:source,grade:"S",visibility:"out_of_character"};
    m.history.push({at:now,choice:result.choice,reason,provider:source});
    if(m.history.length>80)m.history.shift();
    remember(m,now,LABEL[result.choice]+(source==="ollama"?"（模型选择）":"（规则选择）"));
    s.world.push(item);if(s.world.length>4000)s.world.shift();
    // A known and consented tie is required; create a delayed NPC-only message.
    if(result.choice==="check_relatives"&&TIES[id]&&
       (m.lastPeerAt===null||now-m.lastPeerAt>=6*60*MINUTE)){
      const to=TIES[id],msg="询问已知亲友/同事近期可协调的事务（S级模拟）";
      m.lastPeerAt=now;
      s.queue.push({type:"peerDeliver",at:now+15*MINUTE,from:id,to,
        text:msg,order:s.sequence+m.thoughts});
    }
    return item;
  }
  function due(s,limit=4){
    const ai=ensure(s);
    if(!s.autonomy.enabled)return [];
    const ready=E.NPCS.map(n=>({id:n.id,at:ai.minds[n.id].nextAt}))
      .filter(x=>x.at<=s.time).sort((a,b)=>a.at-b.at||a.id.localeCompare(b.id));
    return ready.slice(0,Math.max(0,Math.min(31,limit))).map(x=>x.id);
  }
  function runRules(s,limit=4){
    const ids=due(s,limit),records=[];
    for(const id of ids){const result=chooseRules(s,id);records.push(commit(s,id,result,s.time));}
    return records;
  }
  function settings(s,changes){
    const ai=ensure(s);
    if(changes.realtime!==undefined){guard(typeof changes.realtime==="boolean","实时开关必须布尔值");ai.realtime=changes.realtime;}
    if(changes.speed!==undefined){guard([1,5,10].includes(changes.speed),"实时速度只能是1、5或10游戏分钟/秒");ai.speed=changes.speed;}
    if(changes.mode!==undefined){guard(["rules","ollama"].includes(changes.mode),"推理后端只支持规则或Ollama");ai.mode=changes.mode;}
    return ai;
  }
  return Object.freeze({ensure,choices,snapshot,chooseRules,commit,due,runRules,settings,LABEL});
});
