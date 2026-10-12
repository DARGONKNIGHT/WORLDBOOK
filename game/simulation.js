/* Game5 bounded deterministic clock with agent decisions at intermediate intervals.
 * Works on S_INDEPENDENT_PLAYTHROUGH only, not on canonical world.
 */
(function(root,factory){
 const api=factory(typeof module==="object"&&module.exports?require("./engine.js"):root.EarthGame,
   typeof module==="object"&&module.exports?require("./agent_ai.js"):root.EarthAgents);
 if(typeof module==="object"&&module.exports)module.exports=api;
 else root.EarthSimulation=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(E,A){
 "use strict";
 function advance(s,minutes,{record=true}={}){
  E.validateGame(s);
  if(!Number.isInteger(minutes)||minutes<1||minutes>480)throw Error("推进游戏时间必须为1至480分钟");
  const started=s.time,was=A.ensure(s);
  if(!s.autonomy.enabled){
    // Explicit NPC pause: world time may move but no agent choices are injected.
    let left=minutes;
    while(left){let step=Math.min(left,10);E.act(s,"background_tick",{minutes:step});left-=step;}
  }else{
    let left=minutes;
    while(left){
      let step=Math.min(left,10);
      E.act(s,"background_tick",{minutes:step});
      A.runRules(s,31);
      left-=step;
    }
  }
  if(record){
    s.sequence++;
    s.journal.push({id:s.sequence,at:s.time,kind:"wait",grade:"S",visible:true,
      text:"你让这条独立S级世界分支推进"+minutes+"分钟。NPC按照独立时钟与已知消息逐步处理事务；幕后消息不会自动成为你的知识。"});
    if(s.journal.length>3000)s.journal.shift();
  }
  E.validateGame(s);
  return {minutes,started,ended:s.time,agents:was.minds};
 }

 const MINUTE=60000, MAX_CATCHUP_MINUTES=480;
 const ACTION_MINUTES={explore:35,social:45,study:60,work:120,rest:60,request_contact:5,message:5};
 const safe=(ok,msg)=>{if(!ok)throw Error(msg);};
 function ensureLive(s,wallMs=Date.now()){
   E.validateGame(s);
   if(!s.live||s.live.version!==1){
     s.live={version:1,running:true,rate:1,lastWallMs:wallMs,carryMs:0,task:null,
       omittedMinutes:0,completed:0,interrupted:0};
   }
   A.ensure(s).realtime=s.live.running;
   return s.live;
 }
 function setRate(s,rate,wallMs=Date.now()){
   syncLive(s,wallMs);
   safe([1,60,300].includes(rate),"无回合时钟只能为真实速度、60倍或300倍");
   s.live.rate=rate;
   return s.live;
 }
 function taskDuration(kind,payload){
   if(kind==="travel"){
     const m=Number(payload.minutes);
     safe(Number.isInteger(m)&&m>=15&&m<=480,"行程时间为15至480分钟");
     return m;
   }
   safe(Object.prototype.hasOwnProperty.call(ACTION_MINUTES,kind),"该动作不能建立持续日程");
   return ACTION_MINUTES[kind];
 }
 function canStart(s,kind,payload){
   const p=s.player,energy=p.energy;
   if(kind==="travel"){
     safe(E.DISTRICTS.includes(payload.destination)&&payload.destination!==p.district,"出行目的区无效");
     const fare=Number(payload.fare??0);
     safe(Number.isSafeInteger(fare)&&fare>=0,"行程支出必须为非负整数元");
     safe(fare===0||(p.cash!==null&&p.cash>=fare),"余额未知或不足，禁止登记该行程费用");
     safe(energy>=8,"当前精力不足以出行");
   }else if(kind==="explore")safe(energy>=6,"精力不足");
   else if(kind==="study")safe(energy>=12,"精力不足");
   else if(kind==="work")safe(!!p.occupation&&energy>=22,"缺少明确职业或精力不足");
   else if(kind==="social")safe(energy>=9,"精力不足");
   else if(kind==="request_contact"){
     safe(p.met.some(m=>m.id===payload.recipient),"必须先有过实际相遇");
     safe(!p.contacts.includes(payload.recipient),"已有联系方式");
     const meet=p.met.filter(m=>m.id===payload.recipient).at(-1);
     safe(meet.district===p.district && s.time-meet.at<=100*MINUTE,"已不在有效相遇场景");
     safe(!p.declined.some(x=>x.id===payload.recipient&&x.at>=meet.at),"请尊重此前拒绝");
     safe(energy>=2,"精力不足");
   }else if(kind==="message"){
     safe(p.contacts.includes(payload.recipient)&&String(payload.text||"").trim().length>0,"必须使用已同意的联系人并填写消息");
     safe(energy>=1,"精力不足");
   }
 }
 function startTask(s,kind,payload={},wallMs=Date.now()){
   syncLive(s,wallMs);
   safe(s.live.running,"世界时钟已停止");
   safe(!s.live.task,"你正在执行另一项需要占用时间的活动，可以随时打断");
   const minutes=taskDuration(kind,payload);canStart(s,kind,payload);
   // Copy only serializable intent; do not mutate global time on initiation.
   const task={id:"ACT-"+String(++s.sequence).padStart(6,"0"),kind,payload:JSON.parse(JSON.stringify(payload)),
     startedAt:s.time,endsAt:s.time+minutes*MINUTE,minutes};
   s.live.task=task;
   s.journal.push({id:++s.sequence,at:s.time,kind:"action_started",visible:true,grade:"S",
     text:"你开始"+({travel:"前往其他区",explore:"观察街区",social:"参加公共活动",study:"整理计划",
       work:"处理已有工作",rest:"休息",message:"撰写并发送消息",request_contact:"询问联系方式"}[kind]||kind)+"，预计占用"+minutes+"游戏分钟。期间世界不会暂停。"});
   if(s.journal.length>3000)s.journal.shift();
   return task;
 }
 function interruptTask(s,wallMs=Date.now()){
   syncLive(s,wallMs);
   const live=ensureLive(s,wallMs),task=live.task;
   safe(task,"当前没有可打断的玩家活动");
   const elapsed=Math.min(task.minutes,Math.max(0,Math.floor((s.time-task.startedAt)/MINUTE)));
   const costs={travel:8,explore:6,social:9,study:12,work:22,message:1,request_contact:2};
   let energyEffect=0;
   if(task.kind==="rest")energyEffect=Math.floor(25*elapsed/task.minutes);
   else energyEffect=-Math.ceil((costs[task.kind]||0)*elapsed/task.minutes);
   s.player.energy=Math.min(100,Math.max(0,s.player.energy+energyEffect));
   live.task=null;live.interrupted++;
   s.journal.push({id:++s.sequence,at:s.time,kind:"action_interrupted",visible:true,grade:"S",
     text:"你中止了"+task.kind+"；已进行"+elapsed+"分钟，精力变化"+energyEffect+"。已经流逝的时间不会倒流，未完成任务不兑现结果。"});
   return task;
 }
 function finishTask(s){
   const live=s.live,task=live.task;
   if(!task||s.time<task.endsAt)return null;
   // Completion first clears the reservation; legacy E.act applies a bounded
   // outcome without skipping time. NPCs did not wait for this player action.
   live.task=null;
   try{
     E.act(s,task.kind,{...task.payload,__realtimeComplete:true});
     live.completed++;
   }catch(err){
     s.journal.push({id:++s.sequence,at:s.time,kind:"action_unfulfilled",grade:"S",visible:true,
       text:"行动"+task.kind+"在完成时不再满足条件，未兑现原定结果："+String(err.message).slice(0,120)});
   }
   return task;
 }
 function syncLive(s,wallMs=Date.now()){
   const live=ensureLive(s,wallMs);
   safe(Number.isFinite(wallMs)&&wallMs>=0,"现实时间无效");
   if(!live.running){live.lastWallMs=wallMs;return {advancedMinutes:0,task:live.task};}
   // Moving the host clock backwards must never make the simulation regress.
   if(wallMs<=live.lastWallMs)return {advancedMinutes:0,task:live.task};
   const elapsed=(wallMs-live.lastWallMs)*live.rate+live.carryMs;
   let available=Math.floor(elapsed/MINUTE);
   live.carryMs=elapsed%MINUTE;live.lastWallMs=wallMs;
   if(available>MAX_CATCHUP_MINUTES){
     live.omittedMinutes+=available-MAX_CATCHUP_MINUTES;
     const dropped=available-MAX_CATCHUP_MINUTES;
     available=MAX_CATCHUP_MINUTES;
     s.journal.push({id:++s.sequence,at:s.time,kind:"catchup_limit",visible:true,grade:"S",
       text:"设备/页面停顿过久，超过单次8游戏小时可验证结算上限，未模拟的"+dropped+"分钟明确记为U，不虚构完整离线生活。"});
   }
   const total=available;
   while(available>0){
     const untilTask=live.task?Math.max(0,Math.ceil((live.task.endsAt-s.time)/MINUTE)):10;
     if(live.task&&untilTask===0){finishTask(s);continue;}
     const step=Math.min(10,available,untilTask||10);
     E.act(s,"background_tick",{minutes:step});
     available-=step;
     if(live.task&&s.time>=live.task.endsAt)finishTask(s);
     if(s.autonomy.enabled)A.runRules(s,31);
   }
   return {advancedMinutes:total,task:live.task,omittedMinutes:live.omittedMinutes};
 }
 function stopLive(s,wallMs=Date.now()){
   syncLive(s,wallMs);s.live.running=false;A.ensure(s).realtime=false;
 }
 function resumeLive(s,wallMs=Date.now()){
   ensureLive(s,wallMs);s.live.running=true;s.live.lastWallMs=wallMs;
   A.ensure(s).realtime=true;
 }
 function checkAction(s,kind,payload={}){taskDuration(kind,payload);canStart(s,kind,payload);return true;}
 return Object.freeze({advance,ensureLive,syncLive,startTask,interruptTask,setRate,stopLive,resumeLive,checkAction});
});
