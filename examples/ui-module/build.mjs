import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const {Sketch, Page, Artboard, Rectangle, Text} = require('sketch-constructor');
const JSZip = require('jszip');
const root = path.dirname(fileURLToPath(import.meta.url));
const read = relative => fs.readFile(path.join(root, relative));
const sourceBytes = await read('source/design.json');
const source = JSON.parse(sourceBytes);
const hash = content => crypto.createHash('sha256').update(content).digest('hex');
const uuid = value => {const h=hash(value);return `${h.slice(0,8)}-${h.slice(8,12)}-5${h.slice(13,16)}-a${h.slice(17,20)}-${h.slice(20,32)}`.toUpperCase();};
const esc = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const T=source.tokens,L=source.layout;
const boards=source.modules.flatMap(module=>module.features.flatMap(feature=>feature.boards.map(board=>({...board,module:module.id,feature:feature.id,featureName:feature.name}))));
if (new Set(boards.map(b=>b.id)).size!==boards.length) throw new Error('Duplicate board ID');
const out=path.join(root,'generated');
await fs.mkdir(path.join(out,'screens'),{recursive:true});
await fs.mkdir(path.join(out,'exports'),{recursive:true});
await fs.mkdir(path.join(out,'docs'),{recursive:true});

function scene(board){
 const nodes=[];
 const rect=(name,x,y,w,h,fill,r=T.radius)=>nodes.push({type:'rect',name,x,y,w,h,fill,r});
 const text=(name,value,x,y,size=14,color=T.text,w=780)=>nodes.push({type:'text',name,value,x,y,size,color,w,h:size+10});
 const button=(name,value,x,y,w=120)=>{rect(name,x,y,w,40,T.primary);text(name+' label',value,x+16,y+9,14,T.surface,w-20);};
 const content=L.sidebar+L.padding;
 rect('Canvas',0,0,L.width,L.height,T.background,0);
 rect('Sidebar',0,0,L.sidebar,L.height,T.sidebar,0);
 text('Brand','Trellis 工作台',24,28,19,T.sidebarText,180);
 text('Workspace label','个人项目 / 示例',24,72,12,'#A0BFC4',170);
 rect('Selected menu',16,136,L.sidebar-32,44,T.primary,8);
 text('Navigation','需求管理',32,149,14,T.surface,160);
 text('Other menu','新建需求',32,213,14,'#A0BFC4',160);
 text('Other menu 2','重置演示数据',24,705,12,'#A0BFC4',160);
 text('Sidebar footer','设计先行 · 同版交付',24,740,12,'#A0BFC4',180);
 rect('Topbar',L.sidebar,0,L.width-L.sidebar,L.header,T.surface,0);
 text('Breadcrumb','工作空间  /  需求管理',content,26,13,T.muted,600);
 text('User','演示用户',L.width-118,26,13,T.muted,95);
 text('Page title',board.state==='success'?'需求管理':board.state==='detail'?'需求详情':board.feature==='F02'?'新建需求':'需求管理',content,L.contentTop,26);
 text('Subtitle',board.feature==='F02'?'描述目标与业务范围，提交后进入设计流程。':'记录需求，确认设计，再进入实施。',content,L.contentTop+44,14,T.muted);
 if((board.feature==='F01' && board.state!=='detail') || board.state==='success'){
   button('Create','新建需求',L.width-L.padding-136,104,136);
   rect('Table',content,198,L.width-content-L.padding,478,T.surface);
   text('List title','需求列表',content+24,219,16,T.text);
   text('Count',board.state==='success'?'共 4 项需求':'共 3 项需求',L.width-140,221,13,T.muted,110);
   text('Search label','搜索需求',content+24,261,12,T.muted);
   rect('Search',content+24,290,450,42,T.background);text('Search hint','输入需求标题或编号',content+40,301,14,T.muted);
   rect('Clear',content+490,290,116,42,T.background);text('Clear label','清空筛选',content+506,301,14,T.text,90);
   if(board.state==='normal' || board.state==='success'){
     rect('Table header',content,348,L.width-content-L.padding,42,T.background,0);
     ['需求 / 编号','所属模块','推进状态'].forEach((title,i)=>text('Column '+i,title,content+24+[0,490,650][i],360,12,T.muted,180));
     (board.state==='success'?[source.success_sample,...source.seed]:source.seed).forEach((row,i)=>{
       const y=402+i*L.rowHeight;rect('Divider '+i,content+20,y-10,L.width-content-L.padding-40,1,T.line,0);
       text('Title '+row.id,row.title,content+24,y,15,T.text,480);text('ID '+row.id,row.id,content+24,y+27,12,T.muted,180);
       text('Description '+row.id,row.description.slice(0,21)+'…',content+110,y+27,12,T.muted,360);
       text('Module '+row.id,row.module,content+514,y+10,13,T.muted,150);
       const theme=source.statusStyles[row.status]??source.statusStyles['待讨论'];
       rect('Status '+row.id,content+672,y+2,94,28,T[theme.background],6);text('Status label '+row.id,row.status,content+686,y+6,12,T[theme.foreground],80);
     });
     if(board.state==='success'){rect('Success banner',content,710,L.width-content-L.padding,50,T.primarySoft);text('Success','需求已创建，可以开始需求讨论与设计。',content+20,725,14,T.primaryText);}
   }else{
     const messages={empty:['没有找到匹配需求','调整关键词，或清空筛选重新查看。','清空筛选'],error:['需求加载失败','当前服务暂不可用，已保留搜索条件。','重新加载'],denied:['当前账号无访问权限','请联系项目负责人开通需求管理权限。','返回工作空间']};
     const [title,detail,action]=messages[board.state];text('State title',title,content+240,408,20,T.text,500);text('State detail',detail,content+240,455,14,T.muted,500);button('Recovery',action,content+240,502,150);
   }
 }else{
   const isDetail=board.state==='detail';
   rect('Form card',content,198,L.width-content-L.padding,478,T.surface);
   text('Section',isDetail?'REQ-001 · 设计中':'基本信息',content+28,223,17);
   const fields=[['需求名称',isDetail?source.seed[0].title:board.state==='success'?'统一设计交付流程':'请输入需求名称'],['所属模块',isDetail?'规范库':'选择所属模块'],['需求说明',isDetail?source.seed[0].description:'描述项目背景、用户目标和业务范围']];
   fields.forEach(([label,value],i)=>{const y=277+i*104;text('Field label '+i,label,content+28,y,13);rect('Field '+i,content+28,y+30,Math.min(690,L.width-content-L.padding-56),i===2?80:42,T.background,7);text('Field value '+i,value,content+42,y+42,14,isDetail?T.text:T.muted,650);});
   if(board.state==='invalid')text('Validation','请填写需求名称（2–50 个字符）',content+28,354,12,T.danger);
   if(board.state==='success'){rect('Success banner',content,710,L.width-content-L.padding,50,T.primarySoft);text('Success','需求已创建，可以开始需求讨论与设计。',content+20,725,14,T.primaryText);}
   button('Submit',isDetail?'返回列表':'创建需求',content+28,614,140);text('Cancel',isDetail?'':'取消',content+190,625,14,T.muted,100);
 }
 return nodes.map((node,i)=>({...node,id:uuid(board.id+'/'+i+'/'+node.name)}));
}

const sketch=new Sketch({document:{id:uuid(source.id+'/document')}});
const page=new Page({id:uuid(source.id+'/page'),name:'M01 需求管理 / F01 浏览 / F02 新建'});
const sceneRecords=[];
for(const [index,board] of boards.entries()){
 const nodes=scene(board);sceneRecords.push({board:board.id,nodes});
 const elements=nodes.map(n=>n.type==='rect'?`<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="${n.r}" fill="${n.fill}"/>`:`<text x="${n.x}" y="${n.y+n.size}" font-size="${n.size}" fill="${n.color}">${esc(n.value)}</text>`);
 await fs.writeFile(path.join(out,'screens',board.id+'.svg'),`<svg xmlns="http://www.w3.org/2000/svg" width="${L.width}" height="${L.height}" viewBox="0 0 ${L.width} ${L.height}"><title>${esc(board.name)}</title><g font-family="${T.font},Noto Sans CJK SC,sans-serif">${elements.join('')}</g></svg>\n`);
 const artboard=new Artboard({id:uuid(board.id),name:`${board.feature} / ${board.id} ${board.name}`,frame:{x:(index%2)*(L.width+80),y:Math.floor(index/2)*(L.height+100),width:L.width,height:L.height},backgroundColor:T.background});
 nodes.forEach(n=>artboard.addLayer(n.type==='rect'?new Rectangle({id:n.id,name:n.name,x:n.x,y:n.y,width:n.w,height:n.h,cornerRadius:n.r,style:{fills:[{color:n.fill}]}}):new Text({id:n.id,name:n.name,string:n.value,fontName:T.font,fontSize:n.size,color:n.color,textBehaviour:'fixed',frame:{x:n.x,y:n.y,width:n.w,height:n.h}})));
 page.addArtboard(artboard);
}
sketch.addPage(page);
const sketchPath=path.join(out,'exports/requirements.sketch');
// Serialize the public ZIP/JSON format directly: the old constructor's streaming writer corrupts CJK text on current Node.
// Its model objects remain useful. Normalize nested style IDs and ZIP timestamps for reproducible outputs.
const entries=[['document.json',sketch.document],['meta.json',sketch.meta],['user.json',sketch.user],
 ...sketch.pages.map(p=>['pages/'+p.do_objectID+'.json',p])].map(([name,value])=>[name,JSON.parse(JSON.stringify(value))]).sort(([a],[b])=>a.localeCompare(b));
function migrate(value,key){
 if(!value || typeof value!=='object')return;
 if(['page','artboard','rectangle','text'].includes(value._class))value.isTemplate=false;
 if(value._class==='page'){value.horizontalRulerData={_class:'rulerData',base:0,guides:[]};value.verticalRulerData={_class:'rulerData',base:0,guides:[]};}
 if(value._class==='artboard')delete value.includeInCloudUpload;
 if(value._class==='rectangle')value.needsConvertionToNewRoundCorners=false;
 if(value._class==='curvePoint')value.cornerStyle=0;
 if(key.includes('/attributedString/attributes/'))for(const attr of ['MSAttributedStringTextTransformAttribute','underlineStyle','strikethroughStyle'])delete value[attr];
 if(value._class==='text'){delete value.layers;value.lineSpacingBehaviour=2;value.textBehaviour=1;value.glyphBounds=`{{0, 0}, {${value.frame.width}, ${value.frame.height}}}`;}
 if(value._class==='style'){value.borderOptions={_class:'borderOptions',isEnabled:true,dashPattern:[],lineCapStyle:0,lineJoinStyle:0};value.colorControls={_class:'colorControls',isEnabled:false,brightness:0,contrast:1,hue:0,saturation:1};}
 if(value._class==='fill'&&!value.gradient)value.gradient={_class:'gradient',elipseLength:0,from:'{0.5, 0}',to:'{0.5, 1}',gradientType:0,stops:[{_class:'gradientStop',position:0,color:value.color}]};
 for(const [name,child] of Object.entries(value))migrate(child,key+'/'+name);
}
entries.forEach(([name,value])=>migrate(value,name));
const documentEntry=entries.find(([name])=>name==='document.json')[1];
documentEntry.perDocumentLibraries=[];
Object.assign(documentEntry.assets,{do_objectID:uuid(source.id+'/assets'),colorAssets:[],gradientAssets:[],exportPresets:[]});
const meta=entries.find(([name])=>name==='meta.json')[1];delete meta.fonts;
meta.version=146;meta.compatibilityVersion=99;
const user=entries.find(([name])=>name==='user.json')[1];user.document.pageListHeight=120;user.document.pageListCollapsed=0;
const ids=new Map();
const stableIds=new Set([uuid(source.id+'/document'),uuid(source.id+'/page'),...boards.map(b=>uuid(b.id)),...sceneRecords.flatMap(s=>s.nodes.map(n=>n.id))]);
function visit(value,key){if(!value || typeof value!=='object')return;if(value.do_objectID)ids.set(value.do_objectID,stableIds.has(value.do_objectID)?value.do_objectID:uuid(key));for(const [name,child] of Object.entries(value))visit(child,key+'/'+name);}
entries.forEach(([name,value])=>visit(value,name));
function normalize(value){if(typeof value==='string')return ids.get(value)||value;if(Array.isArray(value))return value.map(normalize);if(value && typeof value==='object')return Object.fromEntries(Object.keys(value).sort().map(key=>[ids.get(key)||key,normalize(value[key])]));return value;}
const canonical=new JSZip();
entries.forEach(([name,value])=>canonical.file(name,JSON.stringify(normalize(value)),{date:new Date('1980-01-01T00:00:00Z'),createFolders:false}));
await fs.writeFile(sketchPath,await canonical.generateAsync({type:'nodebuffer',compression:'STORE'}));
await fs.writeFile(path.join(out,'scenes.json'),JSON.stringify(sceneRecords,null,2)+'\n');
await fs.writeFile(path.join(out,'design.json'),sourceBytes);
const tokens=':root{'+Object.entries(T).map(([key,value])=>`--${key}:${typeof value==='number'?value+'px':value}`).join(';')+';--sidebarWidth:'+L.sidebar+'px;--padding:'+L.padding+'px;}\n';
await fs.writeFile(path.join(out,'tokens.css'),tokens);
const productContext=`# 需求工作台产品上下文\n\n<!-- personal-ui-module-generated -->\n\n权威来源：[中文 PRD](docs/prd.zh-CN.md)；源版本 ${source.version}。此文件为工具读取投影，更新设计源与 PRD 后重新生成。\n\n## Users\n\n管理个人项目需求的演示成员，需要快速查找、阅读和登记需求。\n\n## Product Purpose\n\n先记录业务问题，再讨论、设计和实现。当前仅有浏览/详情与新建两功能。\n\n## Operating Context\n\n本地 Vue/Storybook 或静态原型，使用演示数据，未连接真实后台。桌面表格与窄屏条目读取同一记录。\n\n## Constraints\n\n保留现有青绿色设计语言；不新增真实登录、权限、多人协作、删除、编辑或排期。需求、技术、UI 和验收使用同版 ID。用户可读内容使用中文。\n`;
const designContext=`---\nname: 需求工作台\ndescription: 需求管理示例的设计工具投影\ncolors:\n${Object.entries(T).filter(([,value])=>typeof value==='string'&&value.startsWith('#')).map(([key,value])=>`  ${key}: "${value}"`).join('\n')}\ntypography:\n${Object.entries(source.typeScale).map(([key,size])=>`  ${key}:\n    fontFamily: "${T.font}, system-ui, sans-serif"\n    fontSize: "${size}px"\n    fontWeight: 400\n    lineHeight: 1.6`).join('\n')}\nrounded:\n${Object.entries(source.radiusScale).map(([key,size])=>`  ${key}: "${size}px"`).join('\n')}\nspacing:\n  unit: "${T.space}px"\n---\n\n<!-- personal-ui-module-generated -->\n\n权威来源：[design.json](design.json) 与 [PRD](docs/prd.zh-CN.md)，源版本 ${source.version}。本文件从设计源生成，不独立编辑。\n\n## Overview\n\n以快速完成任务为目标，沿用青绿色和深色侧栏，优先可扫描的信息和清晰操作。\n\n## Colors\n\n主色表示主要操作；推进状态使用 statusStyles 对应语义色，并保留文字。失败使用错误色，普通提示不抢占主操作。\n\n## Typography\n\n中文系统字体，标题、正文与辅助信息层级清晰。编号使用等宽数字特性，说明允许换行。\n\n## Layout\n\n桌面为侧栏、顶部导航和主内容；搜索与计数属于列表。${L.mobileBreakpoint}px 及以下列表改为条目，同一功能信息与操作保持一致。\n\n## Shapes\n\n沿用设计源中的圆角和间距尺度；同职责组件保持一致。\n\n## Components\n\n主操作、文本输入和需求列表引用设计源组件合同；提交互斥、首错聚焦、失败保留输入。\n\n## Do's and Don'ts\n\n沿用已有身份；不为了技能默认风格更换调色板；不增添无业务依据的图表或指标；不以检测通过代替真实行为验收。\n`;
await fs.writeFile(path.join(out,'PRODUCT.md'),productContext);
await fs.writeFile(path.join(out,'DESIGN.md'),designContext);
for(const name of ['gallery.html','gallery.js','prototype.html','prototype.js','styles.css','requirements.css'])await fs.copyFile(path.join(root,'runtime',name),path.join(out,name));
// 导出目录使用自己的设计文件，正文仍由权威文档投影。
for(const name of ['prd.zh-CN.md','tdd.zh-CN.md','review.zh-CN.md']){
 const document=(await read('docs/'+name)).toString().replaceAll('(../source/design.json)','(../design.json)');
 await fs.writeFile(path.join(out,'docs',name),document);
}
const readme=(await read('README.md')).toString()
 .replaceAll('[source/design.json](source/design.json)','[design.json](design.json)')
 .replace('\n','\n\n<!-- personal-ui-module-generated -->\n\n> 本说明从源库 README 生成，不独立编辑。本目录是可单独复制的静态导出；以下依赖安装、构建和校验命令须在完整源库的 `examples/ui-module/` 中执行。\n');
await fs.writeFile(path.join(out,'README.md'),readme);
const outputs=['design.json','scenes.json','tokens.css','PRODUCT.md','DESIGN.md','README.md','gallery.html','gallery.js','prototype.html','prototype.js','styles.css','requirements.css','exports/requirements.sketch','docs/prd.zh-CN.md','docs/tdd.zh-CN.md','docs/review.zh-CN.md',...boards.map(b=>'screens/'+b.id+'.svg')];
const inputs=['source/design.json','build.mjs','package-lock.json','README.md','docs/prd.zh-CN.md','docs/tdd.zh-CN.md','docs/review.zh-CN.md',...['gallery.html','gallery.js','prototype.html','prototype.js','styles.css','requirements.css'].map(n=>'runtime/'+n)];
const manifest={id:source.id,version:source.version,status:source.status,source_sha256:hash(sourceBytes),generator_sha256:hash(await read('build.mjs')),inputs:await Promise.all(inputs.map(async file=>({path:file,sha256:hash(await read(file))}))),boards:boards.map(b=>({...b,preview:'screens/'+b.id+'.svg'})),outputs:await Promise.all(outputs.map(async file=>({path:'generated/'+file,sha256:hash(await fs.readFile(path.join(out,file)))}))),platforms:{figma:'manual_import_file_ready',mastergo:'manual_import_file_ready'},platform_feedback:'not_recorded_by_user',user_confirmation:'pending_review'};
await fs.writeFile(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({status:'generated',boards:boards.length,features:2,source_sha256:manifest.source_sha256,platforms:manifest.platforms}));
