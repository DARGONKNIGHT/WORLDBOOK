/* Desktop/browser UI for an S-grade continuous-time independent sandbox.
   Browser storage plus optional localhost EXE disk mirror; no canonical worldbook mutations. */
(() => {
  "use strict";
  const E=window.EarthGame;
  const A=window.EarthAgents;
  const S=window.EarthSociety;
  const F=window.EarthEconomy;
  const Sim=window.EarthSimulation;
  const KEY="earth-realism-playable-v1"; // v1 key retained for non-destructive migration
  let state=null, activeTab="life", toastTimeout=null;
  let autoClock=null, modelBusy=false, modelCursor=0, tickCount=0, modelStatus="离线有限决策器 · 世界钟不依赖玩家操作";
  let diskQueue=Promise.resolve();
  const $=(id)=>document.getElementById(id);
  const escapeHTML=(text)=>String(text??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const fmt=(n)=>n===null?"未知（U）":"¥"+Number(n).toLocaleString("zh-CN");
  const NPC=(id)=>E.NPCS.find(n=>n.id===id);
  function toast(message,error=false){
    const el=$("toast");el.textContent=message;el.style.borderColor=error?"#b86868":"#5d806e";el.classList.add("show");
    clearTimeout(toastTimeout);toastTimeout=setTimeout(()=>el.classList.remove("show"),3600);
  }
  const desktopServer=()=>location.protocol==="http:" && ["localhost","127.0.0.1"].includes(location.hostname) && location.port==="8765";
  function queueDesktopSave(method,payload){
    if(!desktopServer())return;
    const body=payload||"";
    diskQueue=diskQueue.catch(()=>{}).then(async()=>{
      const res=await fetch("/api/save",{method,headers:method==="POST"?{"Content-Type":"application/json"}:{},body:method==="POST"?body:undefined});
      if(!res.ok&&res.status!==404)throw Error("Work/saves写入失败："+res.status);
    }).catch(err=>{console.warn("Desktop save failed:",err);});
  }
  function save(silent=false){
    if(!state)return;
    try{
      E.validateGame(state);
      if(F.audit(state).length)throw Error("S级经济账本未通过守恒核验");
      const snapshot=JSON.stringify(state);
      localStorage.setItem(KEY,snapshot);
      queueDesktopSave("POST",snapshot);
      if(!silent)toast(desktopServer()?"浏览器已保存，正在同步Work/saves。":"已保存到本机浏览器。");
    }catch(err){toast("无法自动保存：" +err.message,true);}
  }
  function restore(){
    try{const raw=localStorage.getItem(KEY);if(!raw)return null;const loaded=E.upgradeGame(JSON.parse(raw));A.ensure(loaded);if(F.audit(loaded).length)throw Error("经济账本未通过核验");Sim.ensureLive(loaded,Date.now());return loaded;}
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
    $("stat-time").textContent=new Date(state.time+(state.live?.carryMs||0)).toLocaleString("zh-CN",{timeZone:"Asia/Shanghai",hour12:false,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit"});
    const mobility=p.mobility;
    $("stat-district").textContent=mobility?(mobility.status==="en_route"?"在途 · 实际所在区未知 (U)":"行程中断 · 位置待核实 (U)"):"北京 · "+p.district;
    $("stat-cash").textContent=fmt(p.cash);
    $("stat-energy").textContent=p.energy+"/100";
    const task=state.live?.task;
    $("live-state").textContent=state.live?.running?
      "世界连续运行 · "+state.live.rate+"×现实时间"+(state.live.omittedMinutes?" · 尚未模拟"+state.live.omittedMinutes+"分钟(U)，模拟钟与现实存在缺口":""):
      "世界已被管理员冻结";
    const remaining=task?Math.max(0,Math.ceil((task.endsAt-state.time-(state.live?.carryMs||0))/60000)):0;
    $("player-task").textContent=task?"当前行动："+task.kind+" · 剩余约"+remaining+"游戏分钟 · 预计完成 "+E.clock(task.endsAt):"当前空闲 · 可随时开始行动";
    $("interrupt-task").disabled=!task;
    $("resume-travel").hidden=!(mobility?.status==="stranded");
    $("scene-title").textContent=mobility?(mobility.status==="en_route"?"正在从"+mobility.from+"区前往"+mobility.to+"区":"旅程中断 · 具体所在区未知"):p.district+"区 · 你所在的城市";
    $("scene-desc").textContent=mobility?
      ("最后确认位置："+mobility.lastKnownDistrict+"区；原目的地："+mobility.to+"区。由于未核实路线与GPS，不能把出发区或目的区当作你此刻确切的位置。"+
       (mobility.status==="stranded"?" 请使用「继续原行程」；不允许凭空切换地区或在未知地点进行现场活动。":" 世界继续运行，预计抵达后才能确认目的区。")):
      (E.AREAS[p.district]+(p.goal?" 你当前希望："+p.goal+"。":" 你尚未设定具体目标，可以自行决定下一步。"));
    $("map-location").textContent=mobility?"TRANSIT · UNKNOWN":p.district.toUpperCase()+" DISTRICT";
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
    $("ai-speed").value=String(state.live?.rate||1);
    $("ai-status").textContent=(state.live?.running?"世界时钟持续流动":"模拟已冻结")+" · "+(ai.mode==="ollama"?"Ollama模型":"离线决策器")+" · "+modelStatus;
    $("autonomy-detail").value=state.autonomy.detail;
    const id=select.value;
    const records=id==="all"?state.world:state.world.filter(x=>x.npcId===id);
    const society=S.ensure(state);
    const economy=F.ensure(state), caseselect=$("economy-case"), quoteSelect=$("economy-quote");
    const oldCase=caseselect.value,oldQuote=quoteSelect.value;
    const paired=society.cases.filter(c=>c.type==="work"&&c.status==="discussed"&&
      [c.from,c.to].sort().join(":")==="P014:P015");
    caseselect.innerHTML=paired.map(c=>'<option value="'+escapeHTML(c.id)+'">'+escapeHTML(c.id)+' · '+escapeHTML(c.title)+'</option>').join("");
    if(paired.some(c=>c.id===oldCase))caseselect.value=oldCase;
    const quotes=economy.quotes.slice(-50);
    quoteSelect.innerHTML=quotes.map(q=>'<option value="'+escapeHTML(q.id)+'">'+escapeHTML(q.id)+' · '+escapeHTML(q.status)+'</option>').join("");
    if(quotes.some(q=>q.id===oldQuote))quoteSelect.value=oldQuote;
    const balance=(id)=>economy.accounts[id]===undefined?"未知（U）":"¥"+(economy.accounts[id]/100).toLocaleString("zh-CN")+"（S）";
    $("economy-status").innerHTML='<p class="micro">马志强测试余额：'+balance("P014")+'；高鹏测试余额：'+balance("P015")+'。该余额仅属游戏试验，与现实财产及玩家资产无关。</p>'+
      (quotes.length?quotes.slice(-10).reverse().map(q=>'<article class="log-line"><div class="meta">'+escapeHTML(q.id)+' · '+escapeHTML(q.status)+' · S级模拟</div><p>价格：¥'+(q.priceCents/100).toLocaleString("zh-CN")+'；'+escapeHTML(q.caseId)+' · '+(q.verifiedAt?"已核验模拟交付；":"真实履约未证明；")+(q.paidAt?"已S级成对记账":"未付款")+'</p></article>').join(""):'<p class="micro">暂无报价。须先完成工作协商并建立显式S级测试条件。</p>')+
      economy.transfers.slice(-15).reverse().map(t=>'<article class="log-line"><div class="meta">'+escapeHTML(t.id)+' · 成对账本 · '+escapeHTML(E.clock(t.at))+'</div><p>¥'+(t.amountCents/100).toLocaleString("zh-CN")+' · P014减少 / P015增加，均为S级测试；分录数：'+economy.ledger.filter(l=>l.txId===t.id).length+'</p></article>').join("");
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
    try{
      Sim.syncLive(state,Date.now());
      if(kind==="npc_autonomy"){E.act(state,kind,payload);}
      else if(kind==="wait")throw Error("连续世界没有等待/结束回合，时间自然流逝");
      else {
        Sim.checkAction(state,kind,payload);
        if(state.live?.task){
          if(!window.confirm("目前正在执行 "+state.live.task.kind+"。要现在中断，并开始新的行动吗？已花费时间不会倒流。"))return;
          Sim.interruptTask(state,Date.now());
        }
        Sim.startTask(state,kind,payload,Date.now());
      }
      save(true);render();toast(kind==="npc_autonomy"?"NPC设置已更新":"已开始行动；世界不会暂停，你可以随时介入或打断。");
    }catch(err){toast(err.message,true);}
  }
  function startWorldTimer(){
    if(autoClock!==null)clearInterval(autoClock);
    autoClock=setInterval(pulse,1000);
    window.addEventListener("focus",pulse);
    document.addEventListener("visibilitychange",()=>{if(!document.hidden)pulse();});
  }
  function stopRealtime(){
    if(!state)return;
    try{Sim.stopLive(state,Date.now());save(true);render();}
    catch(err){toast(err.message,true);}
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
    if(!state)return;
    try{
      const output=Sim.syncLive(state,Date.now());
      if(state.live?.running&&state.agentAI.mode==="ollama"&&tickCount%10===0)void runOneModel();
      tickCount++;
      if(tickCount%10===0)save(true);
      render();
    }catch(err){
      modelStatus="世界同步受阻："+err.message;
      toast(modelStatus,true);
    }
  }
  async function startRealtime(){
    if(!state)return;
    try{
      const mode=$("ai-provider").value,rate=Number($("ai-speed").value);
      if(mode==="ollama"){
        if(!desktopServer()){
          toast("真实模型推理需要运行本机服务，普通静态网页仍可用规则模式",true);return;
        }
        const response=await fetch("/api/health",{cache:"no-store"});
        const info=await response.json();
        if(!response.ok||info.provider!=="ollama")throw Error("本机Ollama代理不可用");
        modelStatus="代理已连接，模型调用会异步进行";
      }else modelStatus="31名NPC采用有限决策规则";
      Sim.setRate(state,rate,Date.now());
      A.settings(state,{mode,realtime:true,speed:1});
      Sim.resumeLive(state,Date.now());
      save(true);render();toast("世界持续运行中；切换模式无需结束回合。");
    }catch(err){toast(err.message,true);}
  }
  async function setup(){
    $("new-district").innerHTML=E.DISTRICTS.map(d=>'<option value="'+d+'">'+d+'区</option>').join("");
    $("new-district").value="海淀";
    $("travel-destination").innerHTML=E.DISTRICTS.map(d=>'<option value="'+d+'">'+d+'区</option>').join("");
    $("setup-form").addEventListener("submit",ev=>{
      ev.preventDefault();
      try{
        const form=new FormData(ev.currentTarget);
        state=E.makeGame(Object.fromEntries(form.entries()));
        A.ensure(state);Sim.ensureLive(state,Date.now());
        save(true);
        $("setup").close();
        selectTab("life");render();
        toast("新游戏已创建。世界现在连续流动；你可以随时参与。");
      }catch(err){$("setup-error").textContent=err.message;}
    });
    document.querySelectorAll(".nav-btn").forEach(b=>b.addEventListener("click",()=>selectTab(b.dataset.tab)));
    document.querySelectorAll(".action-card").forEach(b=>b.addEventListener("click",()=>{
      const kind=b.dataset.kind;
      execute(kind);
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
    $("economy-fixture-form").addEventListener("submit",ev=>{
      ev.preventDefault();
      if(!state)return;
      try{
        F.opening(state,{caseId:$("economy-case").value,priceYuan:Number($("economy-price").value),
          payerOpeningYuan:Number($("economy-payer").value),providerOpeningYuan:Number($("economy-provider").value)});
        save(true);render();toast("已录入一次性S级假设，NPC可自行决定是否提出报价。");
      }catch(err){toast(err.message,true);}
    });
    $("economy-verify").addEventListener("click",()=>{
      if(!state)return;
      if(!window.confirm("这仅确认沙盒内的模拟履约，不代表现实服务。确认继续？"))return;
      try{F.verifyDelivery(state,{quoteId:$("economy-quote").value,confirmation:"S_SIMULATED_DELIVERY_VERIFIED"});
        save(true);render();toast("S级模拟履约已核验，尚未支付。");}catch(err){toast(err.message,true);}
    });
    $("economy-settle").addEventListener("click",()=>{
      if(!state)return;
      if(!window.confirm("将从经营者S级测试账户扣除，并向合作方S级测试账户增加同额款项；非真实银行支付。确认？"))return;
      try{F.settle(state,{quoteId:$("economy-quote").value,confirmation:"S_AUTHORIZE_DOUBLE_ENTRY"});
        save(true);render();toast("模拟双边记账已完成，实际世界余额未变。");}catch(err){toast(err.message,true);}
    });
    $("world-npc").addEventListener("change",()=>renderWorld());
    $("ai-form").addEventListener("submit",ev=>{ev.preventDefault();void startRealtime();});
    $("ai-stop").addEventListener("click",()=>{stopRealtime();toast("管理员已冻结本地模拟（正常游玩无需此操作）。");});
    $("interrupt-task").addEventListener("click",()=>{if(!state)return;try{Sim.interruptTask(state,Date.now());save(true);render();toast(state.player.mobility?.status==="stranded"?"行程已中断：位置仍未知(U)，不能瞬间返回出发区。":"当前行动已中断，NPC仍按自己的安排活动。");}catch(err){toast(err.message,true);}});
    $("resume-travel").addEventListener("click",()=>{if(!state)return;try{Sim.resumeTravel(state,Date.now());save(true);render();toast("已继续剩余S级预计行程；实际途中位置仍未知。");}catch(err){toast(err.message,true);}});

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
        if(F.audit(candidate).length)throw Error("导入账本金额不守恒，无法恢复");
        if(!window.confirm("导入将覆盖本机当前试玩存档。是否继续？"))return;
        state=candidate;A.ensure(state);Sim.ensureLive(state,Date.now());save(true);$("setup").close();selectTab("life");render();
        toast("已导入并验证存档结构。");
      }catch(err){toast("导入失败："+err.message,true);}
      finally{ev.target.value="";}
    });
    $("btn-reset").addEventListener("click",()=>{
      if(state&&!window.confirm("创建新游戏将替换当前本地存档。请先导出旧存档，确认继续？"))return;
      stopRealtime();state=null;localStorage.removeItem(KEY);queueDesktopSave("DELETE");$("play-layout").hidden=true;$("setup-error").textContent="";
      $("setup-form").reset();$("new-district").value="海淀";$("setup").showModal();
    });
    window.addEventListener("beforeunload",()=>{if(state)save(true);});
    state=restore();
    // Desktop-saved snapshots live next to EXE. Recovery takes precedence over
    // browser localStorage, and never downloads anything from a cloud service.
    if(desktopServer()){
      try{
        const res=await fetch("/api/save",{cache:"no-store"});
        if(res.ok){
          const candidate=E.upgradeGame(await res.json());
          A.ensure(candidate);if(F.audit(candidate).length)throw Error("桌面存档账本无法通过核验");Sim.ensureLive(candidate,Date.now());
          const localWall=state?.live?.lastWallMs||0, diskWall=candidate.live?.lastWallMs||0;
          if(!state||diskWall>=localWall){state=candidate;localStorage.setItem(KEY,JSON.stringify(state));}
          else queueDesktopSave("POST",JSON.stringify(state));
        }
      }catch(err){console.warn("Work/saves恢复不可用，回退浏览器存档：",err);}
    }
    if(state){Sim.syncLive(state,Date.now());selectTab("life");render();}
    else{$("setup").showModal();}
    startWorldTimer();
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",setup);else setup();
})();