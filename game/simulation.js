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
 return Object.freeze({advance});
});
