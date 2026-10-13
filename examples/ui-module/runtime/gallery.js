const design=await fetch('design.json').then(r=>r.json());
const manifest=await fetch('manifest.json').then(r=>r.json());
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const gallery=document.querySelector('#gallery');
document.querySelector('#module-nav').innerHTML=design.modules.map(m=>`<h2>${esc(m.name)}</h2>${m.features.map(f=>`<button data-view="${f.id}">${f.id} ${esc(f.name)} <small>· ${f.boards.length} 个状态</small></button>`).join('')}`).join('');
function render(view){
 if(view==='baseline'){
  gallery.innerHTML=`<h1>设计语言与应用框架</h1><p class="muted">浅灰工作区、深色导航和青绿色主操作。8px 间距基线，圆角 ${design.tokens.radius}px；桌面侧栏 208px，窄屏改为顶部导航。</p><div class="tokens">${['primary','background','surface','text','danger'].map(k=>`<div class="swatch"><i style="background:${design.tokens[k]}"></i><span>${k}<br><small>${design.tokens[k]}</small></span></div>`).join('')}</div><h2>组件与状态合同</h2><div class="components">${design.components.map(c=>`<article class="card"><h2>${esc(c.label)}</h2><p>${esc(c.contract)}</p><p class="component-states">${c.states.join(' · ')}</p></article>`).join('')}</div><h2 style="margin-top:32px">整体布局</h2><div class="board-card"><a href="#" data-board="B01"><img src="screens/B01.svg" alt="整体应用布局"></a></div>`;
 }else{
  const feature=design.modules.flatMap(m=>m.features).find(f=>f.id===view);
  if(!feature)return render('baseline');
  gallery.innerHTML=`<h1>${feature.id} ${esc(feature.name)}</h1><p class="muted">${feature.boards.length} 张页面/状态图 · ${design.version} · 待评审</p><p><a href="prototype.html#${feature.id==='F02'?'create':'list'}">操作该功能原型 ↗</a></p><div class="board-grid">${feature.boards.map(b=>`<article class="board-card"><a href="#" data-board="${b.id}"><img src="screens/${b.id}.svg" alt="${esc(b.name)}"></a><div class="board-caption"><span>${esc(b.name)}<small>${b.id} · ${b.state}</small></span><a href="screens/${b.id}.svg" target="_blank">原尺寸</a></div></article>`).join('')}</div>`;
 }
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
}
document.addEventListener('click',event=>{
 const view=event.target.closest('[data-view]');if(view){render(view.dataset.view);return;}
 const item=event.target.closest('[data-board]');if(item){event.preventDefault();const board=manifest.boards.find(b=>b.id===item.dataset.board);document.querySelector('#board-title').textContent=board.id+' '+board.name;const img=document.querySelector('#board-image');img.src=board.preview;img.alt=board.name;document.querySelector('#board-dialog').showModal();}
});
document.querySelector('#close-board').addEventListener('click',()=>document.querySelector('#board-dialog').close());
render('baseline');
