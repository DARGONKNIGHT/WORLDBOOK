/* Offline UI. Browser localStorage is the only automatic persistence layer.
   No network APIs, no cloud accounts, and no write access to the canonical worldbook. */
(() => {
  "use strict";
  const E=window.EarthGame;
  const KEY="earth-realism-playable-v1";
  let state=null, activeTab="life", toastTimeout=null;
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
    try{const raw=localStorage.getItem(KEY);return raw?E.validateGame(JSON.parse(raw)):null;}
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
    $("people-list").innerHTML=E.NPCS.map(n=>{
      const known=p.contacts.includes(n.id);
      return '<div class="person"><div><div class="person-id">'+escapeHTML(n.id)+' · '+escapeHTML(E.GROUPS[n.group])+'</div><strong>'+escapeHTML(n.name)+' <small style="display:inline">· '+n.age+'岁</small></strong><small>'+escapeHTML(n.occupation)+'</small></div><span class="'+(known?"known":"")+'">'+(known?"● 已认识":"○ 尚未认识")+'</span></div>';
    }).join("");
    $("inbox").innerHTML=state.messages.length?state.messages.slice().reverse().map(m=>'<article class="inbox-item"><time>'+escapeHTML(E.clock(m.at))+' · S级模拟回复</time><p>'+escapeHTML(m.content)+'</p></article>').join(""):'<p class="micro">还没有收到模拟消息。发送后需等待送达，对方可能不回复。</p>';
    $("message-to").disabled=!p.contacts.length;
    $("message-text").disabled=!p.contacts.length;
    $("message-form").querySelector("button").disabled=!p.contacts.length;
  }
  function renderWorld(){
    $("world-total").textContent=state.world.length;
    $("world-list").innerHTML=logs(state.world.map(x=>({...x,kind:x.npcId+" · 后台"})),120);
  }
  function renderArchive(){
    $("archive-player").textContent=state.player.name+"（"+state.player.age+"岁）";
    $("archive-time").textContent=E.clock(state.time);
    $("archive-events").textContent=state.journal.length+"条玩家可见记录";
    $("full-log").innerHTML=logs(state.journal.filter(x=>x.visible),250);
  }
  function execute(kind,payload={}){
    if(!state)return;
    try{E.act(state,kind,payload);save(true);render();toast("行动完成 · 时间已推进");}
    catch(err){toast(err.message,true);}
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
        const candidate=E.validateGame(JSON.parse(await file.text()));
        if(!window.confirm("导入将覆盖本机当前试玩存档。是否继续？"))return;
        state=candidate;save(true);$("setup").close();selectTab("life");render();
        toast("已导入并验证存档结构。");
      }catch(err){toast("导入失败："+err.message,true);}
      finally{ev.target.value="";}
    });
    $("btn-reset").addEventListener("click",()=>{
      if(state&&!window.confirm("创建新游戏将替换当前本地存档。请先导出旧存档，确认继续？"))return;
      state=null;localStorage.removeItem(KEY);$("play-layout").hidden=true;$("setup-error").textContent="";
      $("setup-form").reset();$("new-district").value="海淀";$("setup").showModal();
    });
    state=restore();
    if(state){selectTab("life");render();}
    else{$("setup").showModal();}
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",setup);else setup();
})();