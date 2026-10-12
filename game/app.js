/* Offline UI. Browser localStorage is the only automatic persistence layer.
   No network APIs, no cloud accounts, and no write access to the canonical worldbook. */
(() => {
  "use strict";
  const E=window.EarthGame;
  const A=window.EarthAgents;
  const S=window.EarthSociety;
  const KEY="earth-realism-playable-v1"; // v1 key retained for non-destructive migration
  let state=null, activeTab="life", toastTimeout=null;
  let autoClock=null, modelBusy=false, modelCursor=0, tickCount=0, modelStatus="本地模型未连接";
  const $=(id)=>document.getElementById(id);
  const escapeHTML=(text)=>String(text??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const fmt=(n)=>n===null?"未知（U）":"¥"+Number(n).toLocaleString("zh-CN");
  const NPC=(id)=>E.NPCS.find(n=>n.id===id);
  function toast(message,error=false){
    const el=$("toast");el.textContent=message;el.style.borderColor=error?"#b86868":"#5d806e";el.classList.add("show");
    clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>el.classList.remove("show"),3600);
  }
  function save(silent=false){
    if(!state)return;
    try{E.validateGame(state);localStorage.setItem(KEY,JSON.stringify(state));if(!silent)toast("已保存到本机浏览器。");}
    catch(err){toast("无法自动保存：" +err.message,true);}
  }
  function restore(){
    try{const raw=localStorage.getItem(KEY);if(!raw)return null;const loaded=E.upgradeGame(JSON.parse(raw));A.ensure(loaded);loaded.agentAI.realtime=false;return loaded;}
    catch(err){toast("已有本地存档校验失败，可通过导入JSON恢复。",true);return null;}
  }
  function selectTab(tab){
    activeTab=tab;
    document.querySelectorAll(".nav-btn").forEach(el=>el.classList.toggle("active",el.dataset.tab===tab));
    document.querySelectorAll(".tab-panel").forEach(el=>el.hidden=el.id!=="tab-"+tab);
    if(tab==="world")renderWorld();
    if(tab==="archive")renderArchive();
    if(tab==="people")renderPeople();
  }
  function logs(items,limit=20){
    if(!items.length)return '<p class="micro">暂无记录。行动或推进时间后，这里会更新。</p>';
    return items.slice(-limit).reverse().map(it=>
      '<article class="log-line"><div class="meta">'+escapeHTML(E.clock(it.at))+' · '+escapeHTML(it.grade||"S")+' · '+escapeHTML(it.kind||"NPC活动")+'</div><p>'+escapeHTML(it.text)+'</p></article>'
    ).join("");
  }
  function render(){
    if(!state)return;
    $("play-layout").hidden=false;
    const p=state.player;
    $("avatar").textContent=p.name.slice(0,1);
    $("player-name").textContent=p.name;
    $("player-job").textContent=p.occupation||"职业未设定（U）";
    $("stat-time").textContent=E.clock(state.time);
    $("stat-district").textContent="北京 · "+p.district;
    $("stat-cash").textContent=fmt(p.cash);
    $("stat-energy").textContent=p.energy+"/100";
    $("scene-title").textContent=p.district+"区 · 你所在的城市";
    $("scene-desc").textContent=E.AREAS[p.district]+(p.goal?" 你当前希望："+p.goal+"。":" 你尚未设定具体目标，可以自行决定下一步。");
    $("map-location").textContent=p.district.toUpperCase()+" DISTRICT";
    $("travel-destination").value=E.DISTRICTS.find(d=>d!==p.district);
    const recent=state.journal.filter(x=>x.visible).slice(-7).reverse();
    $("recent-log").innerHTML=recent.map(x=>'<div class="log-item"><time>'+escapeHTML(E.clock(x.at))+'</time><span class="log-kind">'+escapeHTML(x.kind)+' · '+escapeHTML(x.grade)+'</span><p>'+escapeHTML(x.text)+'</p></div>').join("");
    document.querySelector('[data-kind="work"]').disabled=!p.occupation;
    if(activeTab==="people")renderPeople();
    if(activeTab==="world")renderWorld();
    if(activeTab==="archive")renderArchive();
  }
  function renderPeople(){
    const p=state.player;
    $("contact-count").textContent=p.contacts.length;
    const to=$("message-to"),selected=to.value;
    to.innerHTML=p.contacts.length?p.contacts.map(id=>'<option value="'+escapeHTML(id)+'">'+escapeHTML(NPC(id).name)+'</option>').join(""):'<option value="">尚无可联系人物</option>';
    if(p.contacts.includes(selected))to.value=selected;
    const metIds=[...new Set(p.met.map(m=>m.id))];
    const knownIds=[...new Set([...p.contacts,...metIds])];
    $("people-list").innerHTML=knownIds.length?knownIds.map(id=>{
      const n=NPC(id),known=p.contacts.includes(id),m=p.met.filter(x=>x.id===id).at(-1);
      return '<div class="person"><div><div class="person-id">'+escapeHTML(n.id)+' · S级相遇档案</div><strong>'+escapeHTML(n.name)+'</strong><small>'+escapeHTML(n.occupation)+'</small></div><span class="'+(known?"known":"")+'">'+(known?"● 可联系":"○ 曾交谈")+'</span></div>';
    }).join(""):'<p class="micro">尚未与任何世界书人物实际交谈。其他人物依旧存在并自主行动，但你不能直接读取他们的身份档案。</p>';
    const encounters=p.met.slice(-8).reverse();
    $("encounter-list").innerHTML=encounters.length?encounters.map(m=>{
      const n=NPC(m.id),isKnown=p.contacts.includes(m.id),declined=p.declined.some(x=>x.id===m.id&&x.at===m.at);
      const nearby=state.time-m.at<=100*60000&&m.district===p.district;
      return '<div class="encounter"><div><strong>'+escapeHTML(n.name)+'</strong><small>'+escapeHTML(E.clock(m.at))+' · '+escapeHTML(m.district)+'区</small></div>'+
      (isKnown?'<span class="known">已互留联系方式</span>':declined?'<span>对方已拒绝，请勿纠缠</span>':nearby?'<button type="button" class="ghost ask-contact" data-contact="'+escapeHTML(m.id)+'">礼貌询问联系方式</button>':'<span>已离开相遇场景</span>')+'</div>';
    }).join(""):'<p class="micro">前往公共场所不保证认识某个人。相遇后，是否交换联系方式仍由对方决定。</p>';
    $("inbox").innerHTML=state.messages.length?state.messages.slice().reverse().map(m=>'<article class="inbox-item"><time>'+escapeHTML(E.clock(m.at))+' · S级模拟回复</time><p>'+escapeHTML(m.content)+'</p></article>').join(""):'<p class="micro">暂未收到回复。发送、送达和阅读是不同阶段，对方有权不回应。</p>';
    $("message-to").disabled=!p.contacts.length;
    $("message-text").disabled=!p.contacts.length;
    $("message-form").querySelector("button").disabled=!p.contacts.length;
  }
  function renderWorld(){
    const select=$("world-npc"),current=select.value;
    if(!select.options.length){
      select.innerHTML='<option value="all">全部31名人物</option>'+E.NPCS.map(n=>'<option value="'+escapeHTML(n.id)+'">'+escapeHTML(n.name)+' · '+escapeHTML(n.id)+'</option>').join("");
    }else if(current)select.value=current;
    $("autonomy-enabled").value=String(state.autonomy.enabled);
    const ai=A.ensure(state);
    $("ai-provider").value=ai.mode;
    $("ai-speed").value=String(ai.speed);
    $("ai-status").textContent=(ai.realtime?"运行中":"已暂停")+" · "+(ai.mode==="ollama"?"Ollama模型":"离线有限决策器")+" · "+modelStatus;
    $("autonomy-detail").value=state.autonomy.detail;
    const id=select.value;
    const records=id==="all"?state.world:state.world.filter(x=>x.npcId===id);
    const society=S.ensure(state);
    $("society-count").textContent=society.cases.length;
    $("society-list").innerHTML=society.cases.length?society.cases.slice(-35).reverse().map(x=>
      '<article class="log-line"><div class="meta">'+escapeHTML(E.clock(x.createdAt))+' · '+escapeHTML(x.id)+' · '+escapeHTML(x.status)+'</div><p>'+escapeHTML(x.title)+' · '+escapeHTML(NPC(x.from)?.name||x.from)+' → '+escapeHTML(NPC(x.to)?.name||x.to)+(x.result?'；'+escapeHTML(x.result):'；等待对方知情并决定')+'</p></article>').join(""):'<p class="micro">尚无模拟协商事务。开启自主NPC模拟、推进游戏时间后，既有家人/同事才可能发起事务。</p>';
    $("world-total").textContent=records.length;
    $("world-list").innerHTML=logs(records.map(x=>({...x,kind:x.kind||"自主活动"})),150);
    if(id==="all"){
      $("npc-preview").textContent="选择具体人物查看这一时刻的S级候选事务、地点假设和决策原因。这是审计视角，主角不会自动得知。";
      return;
    }
    const n=NPC(id),c=E.plan(state,id),latest=state.npc[id].lastActivity;
    const mind=A.ensure(state).minds[id];
    const agentThought=mind.history.at(-1);
    $("npc-preview").innerHTML='<strong>'+escapeHTML(n.name)+' · '+escapeHTML(c.kind)+'</strong><p>当前判断：'+escapeHTML(c.reason)+'；优先事务：'+escapeHTML(c.focus)+'。</p><p>假设所在地区：'+escapeHTML(c.location)+' · 状态评分：'+escapeHTML(c.score)+'（S级规则权重，不代表人的心理测量）</p>'+
    '<p>最近结算：'+(latest?escapeHTML(E.clock(latest.at))+' · '+escapeHTML(latest.text):'尚无执行记录')+'</p>'+
    '<p>个人目标：'+escapeHTML(mind.goals.join('；'))+' · 休息需求：'+mind.needs.rest+' · 社交需求：'+mind.needs.social+'</p>'+
    '<p>最近自主选择：'+(agentThought?escapeHTML(A.LABEL[agentThought.choice])+' · '+escapeHTML(agentThought.provider)+' · '+escapeHTML(agentThought.reason):'尚未形成独立思考记录')+'</p>';
  }
  function renderArchive(){
    $("archive-player").textContent=state.player.name+"（"+state.player.age+"岁）";
    $("archive-time").textContent=E.clock(state.time);
    $("archive-events").textContent=state.journal.length+"条玩家可见记录";
    $("full-log").innerHTML=logs(state.journal.filter(x=>x.visible),250);
  }
  function execute(kind,payload={}){
    if(!state)return;
    try{E.act(state,kind,payload);save(true);render();toast(kind==="npc_autonomy"?"NPC自主活动设置已保存":"行动完成 · 时间已推进");}
    catch(err){toast(err.message,true);}
  }
  function stopRealtime(){
    if(autoClock!==null){clearInterval(autoClock);autoClock=null;}
    if(state)A.settings(state,{realtime:false});
    if(state){save(true);render();}
  }
  async function runOneModel(){
    if(modelBusy||!state||!state.agentAI.realtime||state.agentAI.mode!=="ollama")return;
    if(location.protocol==="file:"){modelStatus="单文件模式不支持大模型；请用本地Python服务";return;}
    const id=E.NPCS[modelCursor++%E.NPCS.length].id;
    const source=state,observedAt=source.time, payload=A.snapshot(source,id);
    modelBusy=true;
    const ctl=new AbortController();
    const abort=setTimeout(()=>ctl.abort(),45000);
    try{
      const response=await fetch("/api/ai/decide",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload),signal:ctl.signal
      });
      const result=await response.json();
      if(!response.ok)throw Error(result.error||"本地模型未就绪");
      if(source!==state||!state.agentAI.realtime)return;
      A.commit(state,id,result,observedAt);
      modelStatus="模型在线 · 最近成功："+NPC(id).name;
      save(true);
    }catch(err){
      // Never pretend rules are language model output.
      modelStatus="模型调用失败："+String(err.message).slice(0,85)+"；其余NPC仍以规则持续运行";
    }finally{
      clearTimeout(abort);modelBusy=false;
      if(state&&activeTab==="world")renderWorld();
    }
  }
  function pulse(){
    if(!state||!state.agentAI.realtime)return;
    try{
      const speed=state.agentAI.speed;
      E.act(state,"background_tick",{minutes:speed});
      A.runRules(state,31); // all 31 local agents replan when due; model results are separate audited refinements
      if(state.agentAI.mode==="ollama")void runOneModel();
      tickCount++;
      if(tickCount%5===0)save(true);
      render();
    }catch(err){
      modelStatus="实时模拟停止："+err.message;
      stopRealtime();
      toast(modelStatus,true);
    }
  }
  async function startRealtime(){
    if(!state)return;
    const mode=$("ai-provider").value,speed=Number($("ai-speed").value);
    if(mode==="ollama"){
      if(speed!==1){toast("本地大模型请使用每秒推进1游戏分钟，以免推理期间的日程过期。",true);return;}
      if(location.protocol==="file:"){
        toast("大模型模式需要运行 python3 game/agent_server.py，并打开本地服务的网址。",true);
        return;
      }
      try{
        const response=await fetch("/api/health",{cache:"no-store"});
        if(!response.ok)throw Error("没有本地模型服务");
        const status=await response.json();
        if(status.provider!=="ollama")throw Error("不是Ollama代理");
        modelStatus="代理已连接；请确保Ollama和模型已启动";
      }catch(err){toast("无法连接本地模型代理："+err.message,true);return;}
    }else modelStatus="规则模拟正常；不调用语言模型";
    A.settings(state,{realtime:true,mode,speed});
    if(autoClock!==null)clearInterval(autoClock);
    tickCount=0;
    autoClock=setInterval(pulse,1000);
    save(true);render();toast("已启动31名NPC实时模拟，关闭网页后停止。");
  }
  function setup(){
    $("new-district").innerHTML=E.DISTRICTS.map(d=>'<option value="'+d+'">'+d+'区</option>').join("");
    $("new-district").value="海淀";
    $("travel-destination").innerHTML=E.DISTRICTS.map(d=>'<option value="'+d+'">'+d+'区</option>').join("");
    $("setup-form").addEventListener("submit",ev=>{
      ev.preventDefault();
      try{
        const form=new FormData(ev.currentTarget);
        state=E.makeGame(Object.fromEntries(form.entries()));
        A.ensure(state);
        save(true);
        $("setup").close();
        selectTab("life");render();
        toast("新游戏已创建。世界时钟开始按你的行动推进。");
      }catch(err){$("setup-error").textContent=err.message;}
    });
    document.querySelectorAll(".nav-btn").forEach(b=>b.addEventListener("click",()=>selectTab(b.dataset.tab)));
    document.querySelectorAll(".action-card").forEach(b=>b.addEventListener("click",()=>{
      const kind=b.dataset.kind;
      if(kind!=="wait"){execute(kind);return;}
      const input=window.prompt("本次等待多少分钟？（1—480，时间不会在后台自行流逝）","60");
      if(input===null)return;
      execute("wait",{minutes:Number(input)});
    }));
    $("travel-form").addEventListener("submit",ev=>{
      ev.preventDefault();
      execute("travel",{destination:$("travel-destination").value,minutes:$("travel-minutes").value,fare:$("travel-fare").value});
    });
    $("encounter-list").addEventListener("click",ev=>{
      const btn=ev.target.closest(".ask-contact");
      if(btn)execute("request_contact",{recipient:btn.dataset.contact});
    });
    $("autonomy-form").addEventListener("submit",ev=>{
      ev.preventDefault();
      execute("npc_autonomy",{enabled:$("autonomy-enabled").value==="true",detail:$("autonomy-detail").value});
    });
    $("world-npc").addEventListener("change",()=>renderWorld());
    $("ai-form").addEventListener("submit",ev=>{ev.preventDefault();void startRealtime();});
    $("ai-stop").addEventListener("click",()=>{stopRealtime();toast("实时世界已暂停。");});
    $("world-step-60").addEventListener("click",()=>execute("wait",{minutes:60}));
    $("world-step-240").addEventListener("click",()=>execute("wait",{minutes:240}));
    $("message-form").addEventListener("submit",ev=>{
      ev.preventDefault();
      execute("message",{recipient:$("message-to").value,text:$("message-text").value});
      $("message-text").value="";
    });
    $("btn-save").addEventListener("click",()=>save(false));
    $("btn-export").addEventListener("click",()=>{
      if(!state){toast("尚无游戏存档",true);return;}
      try{
        const file=new Blob([JSON.stringify(state,null,2)],{type:"application/json;charset=utf-8"});
        const url=URL.createObjectURL(file),a=document.createElement("a");
        a.href=url;a.download="earth-realism-"+E.localDay(state.time)+".json";
        document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
        toast("存档JSON已生成；请自行妥善保存。");
      }catch(err){toast(err.message,true);}
    });
    $("btn-import").addEventListener("click",()=>$("import-file").click());
    $("import-file").addEventListener("change",async ev=>{
      const file=ev.target.files?.[0];if(!file)return;
      try{
        if(file.size>3*1024*1024)throw new Error("存档超过3MB，拒绝导入");
        const candidate=E.upgradeGame(JSON.parse(await file.text()));
        if(!window.confirm("导入将覆盖本机当前试玩存档。是否继续？"))return;
        state=candidate;A.ensure(state);state.agentAI.realtime=false;save(true);$("setup").close();selectTab("life");render();
        toast("已导入并验证存档结构。");
      }catch(err){toast("导入失败："+err.message,true);}
      finally{ev.target.value="";}
    });
    $("btn-reset").addEventListener("click",()=>{
      if(state&&!window.confirm("创建新游戏将替换当前本地存档。请先导出旧存档，确认继续？"))return;
      stopRealtime();state=null;localStorage.removeItem(KEY);$("play-layout").hidden=true;$("setup-error").textContent="";
      $("setup-form").reset();$("new-district").value="海淀";$("setup").showModal();
    });
    window.addEventListener("beforeunload",()=>{if(state)save(true);});
    state=restore();
    if(state){selectTab("life");render();}
    else{$("setup").showModal();}
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",setup);else setup();
})();