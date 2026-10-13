const design=await fetch('design.json').then(r=>r.json());
const KEY='personal-trellis-ui-v1';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let data;try{data=JSON.parse(localStorage.getItem(KEY))||structuredClone(design.seed);if(!Array.isArray(data))throw new Error();}catch{data=structuredClone(design.seed);}
let query='',scenario='normal',toast='',submitting=false;
const app=document.querySelector('#app');
function navigate(hash){location.hash=hash;if(location.hash.slice(1)===hash)render();}
const filtered=()=>data.filter(r=>(r.title+' '+r.id).toLowerCase().includes(query.toLowerCase()));
function statusBadge(status){const theme=design.statusStyles[status]??design.statusStyles['待讨论'];return `<span class="status" style="color:var(--${esc(theme.foreground)});background:var(--${esc(theme.background)})">${esc(status)}</span>`;}
function table(){const matches=filtered();return matches.length?`<div class="table-scroll"><table aria-label="需求列表"><thead><tr><th scope="col">需求 / 编号</th><th scope="col">所属模块</th><th scope="col">推进状态</th></tr></thead><tbody>${matches.map(r=>`<tr><td><button class="title-button" data-id="${esc(r.id)}">${esc(r.title)}</button><div class="row-meta"><small>${esc(r.id)}</small><span>${esc(r.description)}</span></div></td><td>${esc(r.module)}</td><td>${statusBadge(r.status)}</td></tr>`).join('')}</tbody></table></div><ul class="mobile-list" aria-label="需求列表">${matches.map(r=>`<li><div class="mobile-heading"><small>${esc(r.id)}</small>${statusBadge(r.status)}</div><button class="title-button" data-id="${esc(r.id)}">${esc(r.title)}</button><p>${esc(r.description)}</p><small>所属模块：${esc(r.module)}</small></li>`).join('')}</ul>`:empty('没有找到匹配需求','调整关键词，或清空筛选重新查看。','清空筛选','clear');}
function empty(title,detail,label,action){return `<div class="empty"><h2>${title}</h2><p>${detail}</p><button data-action="${action}">${label}</button></div>`;}
function body(){if(scenario==='error')return empty('需求加载失败','当前服务暂不可用，已保留搜索条件。','重新加载','retry');if(scenario==='denied')return empty('当前账号无访问权限','请联系项目负责人开通需求管理权限。','返回工作空间','retry');return table();}
function refresh(){document.querySelector('#list-card').innerHTML=body();document.querySelector('#count').textContent=`共 ${filtered().length} 项需求`;}
function render(){
 const hash=location.hash.slice(1)||'list';
 if(hash==='create'){
  app.innerHTML=`<div class="title-row"><div><h1>新建需求</h1><p class="muted">描述目标与业务范围，提交后进入设计流程。</p></div></div><form id="create-form" class="card form-card" novalidate><h2>基本信息</h2><label class="field"><span>需求名称 *</span><input id="title" name="title" maxlength="50" required aria-describedby="title-error" placeholder="请输入需求名称"><small id="title-error" class="error"></small></label><label class="field"><span>所属模块 *</span><select name="module"><option>规范库</option><option>设计交付</option><option>工具接入</option></select></label><label class="field"><span>需求说明 *</span><textarea id="description" name="description" maxlength="1000" aria-describedby="description-error" placeholder="描述项目背景、用户目标和业务范围"></textarea><small id="description-error" class="error"></small></label><label><input type="checkbox" name="simulateFailure"> 演示提交失败及恢复</label><div class="actions"><button type="submit">创建需求</button><button type="button" class="secondary" data-action="list">取消</button><span id="submit-state" role="status"></span></div></form>`;
  document.querySelector('#title').focus();return;
 }
 if(hash.startsWith('detail/')){const row=data.find(r=>r.id===decodeURIComponent(hash.slice(7)));if(!row)return navigate('list');app.innerHTML=`<h1>需求详情</h1><p class="muted">编号 ${esc(row.id)} · ${esc(row.status)}</p><article class="card form-card"><h2>${esc(row.title)}</h2><p>所属模块：${esc(row.module)}</p><p class="detail">${esc(row.description)}</p><button data-action="list">返回列表</button></article>`;return;}
 app.innerHTML=`${toast?`<div class="toast" role="status">${esc(toast)}</div>`:''}<div class="title-row"><div><h1>需求管理</h1><p class="muted">记录需求，确认设计，再进入实施。</p></div><button data-action="create">新建需求</button></div><div class="card"><div class="list-heading"><h2>需求列表</h2><span id="count" class="muted">共 ${filtered().length} 项需求</span></div><div class="toolbar"><label class="search-field"><span>搜索需求</span><input id="search" class="search" placeholder="输入需求标题或编号" value="${esc(query)}"></label><button class="secondary" data-action="clear">清空筛选</button></div><div id="list-card">${body()}</div></div><div class="state-controls"><span>评审状态演示：</span><button class="secondary" data-action="normal">正常</button><button class="secondary" data-action="error">加载失败</button><button class="secondary" data-action="denied">无权限</button></div>`;
 document.querySelector('#search').addEventListener('input',event=>{query=event.target.value;refresh();});
}
document.addEventListener('click',event=>{
 const row=event.target.closest('[data-id]');if(row){navigate('detail/'+encodeURIComponent(row.dataset.id));return;}
 const action=event.target.closest('[data-action]')?.dataset.action;if(!action)return;
 if(action==='create')navigate('create');
 else if(action==='list')navigate('list');
 else if(action==='clear'){query='';scenario='normal';render();document.querySelector('#search')?.focus();}
 else if(['error','denied','normal'].includes(action)){scenario=action;refresh();}
 else if(action==='retry'){scenario='normal';refresh();}
 else if(action==='reset'){data=structuredClone(design.seed);query='';scenario='normal';toast='演示数据已重置';try{localStorage.removeItem(KEY);}catch{}navigate('list');}
});
document.addEventListener('submit',async event=>{
 if(event.target.id!=='create-form')return;event.preventDefault();if(submitting)return;
 const form=event.target;const values=new FormData(form);const title=String(values.get('title')).trim();const description=String(values.get('description')).trim();
 const invalidTitle=title.length<2||title.length>50,invalidDescription=description.length<5;
 document.querySelector('#title-error').textContent=invalidTitle?'请填写需求名称（2–50 个字符）':'';document.querySelector('#description-error').textContent=invalidDescription?'请填写至少 5 个字符的需求说明':'';
 document.querySelector('#title').setAttribute('aria-invalid',String(invalidTitle));document.querySelector('#description').setAttribute('aria-invalid',String(invalidDescription));
 if(invalidTitle||invalidDescription){document.querySelector(invalidTitle?'#title':'#description').focus();return;}
 submitting=true;const submit=form.querySelector('[type=submit]');submit.disabled=true;document.querySelector('#submit-state').textContent='正在创建…';
 await new Promise(resolve=>setTimeout(resolve,350));
 if(!form.isConnected){submitting=false;return;}
 if(values.get('simulateFailure')){document.querySelector('#submit-state').textContent='提交失败，输入已保留。取消失败演示后重试。';submit.disabled=false;submitting=false;return;}
 const row={id:'REQ-'+String(Math.max(0,...data.map(r=>Number(r.id.slice(4))||0))+1).padStart(3,'0'),title,module:String(values.get('module')),description,status:'待讨论'};
 data.unshift(row);try{localStorage.setItem(KEY,JSON.stringify(data));toast='需求已创建，可以开始需求讨论与设计。';}catch{toast='需求已创建；浏览器存储不可用，本次内容仅保留在当前会话。';}
 query='';scenario='normal';submitting=false;navigate('list');
});
addEventListener('hashchange',render);render();
