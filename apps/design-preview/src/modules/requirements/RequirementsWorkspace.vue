<script setup lang="ts">
import {computed,nextTick,onBeforeUnmount,onMounted,reactive,ref,watch} from 'vue';
import design from '../../design/design.json';
type Route='list'|'create'|'detail';
type Scenario='normal'|'empty'|'error'|'denied';
type Requirement={id:string;title:string;module:string;status:string;description:string};
const props=withDefaults(defineProps<{initialRoute?:Route;initialScenario?:Scenario;initialInvalid?:boolean;initialSuccess?:boolean}>(),{initialRoute:'list',initialScenario:'normal',initialInvalid:false,initialSuccess:false});
const rows=ref<Requirement[]>(structuredClone(props.initialSuccess?[design.success_sample,...design.seed]:design.seed));
const route=ref<Route>(props.initialRoute),scenario=ref<Scenario>(props.initialScenario);
const query=ref(props.initialScenario==='empty'?'无匹配的演示关键词':''),selected=ref<Requirement>(rows.value[0]);
const form=reactive({title:'',module:'规范库',description:'',failure:false});
const errors=reactive({title:'',description:''});
const titleInput=ref<HTMLInputElement>(),descriptionInput=ref<HTMLTextAreaElement>();
const feedback=ref(props.initialSuccess?'需求已创建，可以开始需求讨论与设计。':''),submitting=ref(false);
let generation=0;
const matches=computed(()=>rows.value.filter(row=>(row.title+' '+row.id).toLowerCase().includes(query.value.toLowerCase())));
function statusStyle(status:string){
 const theme=design.statusStyles[status as keyof typeof design.statusStyles]??design.statusStyles['待讨论'];
 return {color:`var(--${theme.foreground})`,backgroundColor:`var(--${theme.background})`};
}
function reset(){generation++;submitting.value=false;rows.value=structuredClone(design.seed);query.value='';scenario.value='normal';route.value='list';feedback.value='演示数据已重置';}
async function navigate(next:Route){generation++;submitting.value=false;route.value=next;if(next==='create'){Object.assign(form,{title:'',module:'规范库',description:'',failure:false});Object.assign(errors,{title:'',description:''});feedback.value='';await nextTick();titleInput.value?.focus();}}
function detail(row:Requirement){selected.value=row;void navigate('detail');}
function validate(){errors.title=form.title.trim().length<2||form.title.trim().length>50?'请填写需求名称（2–50 个字符）':'';errors.description=form.description.trim().length<5?'请填写至少 5 个字符的需求说明':'';if(errors.title||errors.description){(errors.title?titleInput.value:descriptionInput.value)?.focus();return false;}return true;}
async function submit(){
 if(submitting.value||!validate())return;
 const request={title:form.title.trim(),module:form.module,description:form.description.trim(),failure:form.failure};
 const current=++generation;submitting.value=true;feedback.value='正在创建…';
 await new Promise(resolve=>setTimeout(resolve,350));
 // 离开表单或切换故事后，旧提交结果不能创建记录。
 if(current!==generation)return;
 if(request.failure){submitting.value=false;feedback.value='提交失败，输入已保留。取消失败演示后重试。';return;}
 const id='REQ-'+String(Math.max(0,...rows.value.map(row=>Number(row.id.slice(4))||0))+1).padStart(3,'0');
 rows.value.unshift({id,title:request.title,module:request.module,description:request.description,status:'待讨论'});
 submitting.value=false;query.value='';scenario.value='normal';route.value='list';feedback.value='需求已创建，可以开始需求讨论与设计。';
}
watch(()=>[props.initialRoute,props.initialScenario,props.initialInvalid,props.initialSuccess],()=>{reset();route.value=props.initialRoute;scenario.value=props.initialScenario;query.value=props.initialScenario==='empty'?'无匹配的演示关键词':'';if(props.initialInvalid)validate();if(props.initialSuccess)rows.value.unshift(structuredClone(design.success_sample));feedback.value=props.initialSuccess?'需求已创建，可以开始需求讨论与设计。':'';});
onMounted(async()=>{if(props.initialInvalid){await nextTick();validate();}else if(route.value==='create'){await nextTick();titleInput.value?.focus();}});
onBeforeUnmount(()=>generation++);
</script>

<template>
 <div class="design-app">
  <aside class="design-sidebar"><strong>Trellis 工作台</strong><small>个人项目 / 示例</small><nav aria-label="业务导航"><button :class="{active:route!=='create'}" :aria-current="route!=='create'?'page':undefined" @click="navigate('list')">需求管理</button><button :class="{active:route==='create'}" :aria-current="route==='create'?'page':undefined" @click="navigate('create')">新建需求</button></nav><footer><button class="design-reset" @click="reset">重置演示数据</button><span>设计先行 · 同版交付</span></footer></aside>
  <main class="design-main"><header class="design-topbar"><span>工作空间 <span aria-hidden="true">/</span> <strong>需求管理</strong></span><span>演示用户</span></header><div class="design-notice"><strong>本地原型</strong><span>数据仅在当前预览会话中保存，未连接业务后台。</span></div>
   <section class="design-content">
    <div v-if="feedback" class="design-toast" :class="{failure:feedback.startsWith('提交失败')}" :role="feedback.startsWith('提交失败')?'alert':'status'">{{feedback}}</div>
    <template v-if="route==='list'">
     <div class="design-title-row"><div><h1>需求管理</h1><p>记录需求，确认设计，再进入实施。</p></div><button class="design-primary design-create-button" @click="navigate('create')"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 5v14M5 12h14"/></svg>新建需求</button></div>
     <div class="design-card design-list-card">
      <div class="design-list-heading"><h2>需求列表</h2><span class="design-muted" aria-live="polite">共 {{matches.length}} 项需求</span></div>
      <div class="design-toolbar"><label class="design-search-field"><span>搜索需求</span><input v-model="query" placeholder="输入需求标题或编号"></label><button class="design-secondary" @click="query='';scenario='normal'">清空筛选</button></div>
      <div v-if="scenario==='error'||scenario==='denied'" class="design-empty" role="alert"><h2>{{scenario==='error'?'需求加载失败':'当前账号无访问权限'}}</h2><p>{{scenario==='error'?'当前服务暂不可用，已保留搜索条件。':'请联系项目负责人开通需求管理权限。'}}</p><button class="design-primary" @click="scenario='normal'">{{scenario==='error'?'重新加载':'返回工作空间'}}</button></div>
      <div v-else-if="!matches.length" class="design-empty" role="status"><h2>没有找到匹配需求</h2><p>调整关键词，或清空筛选重新查看。</p><button class="design-primary" @click="query='';scenario='normal'">清空筛选</button></div>
      <template v-else>
       <div class="design-table-scroll"><table aria-label="需求列表"><thead><tr><th scope="col">需求 / 编号</th><th scope="col">所属模块</th><th scope="col">推进状态</th></tr></thead><tbody><tr v-for="row in matches" :key="row.id"><td><button class="design-title-button" @click="detail(row)">{{row.title}}</button><div class="design-row-meta"><small>{{row.id}}</small><span>{{row.description}}</span></div></td><td>{{row.module}}</td><td><span class="design-status" :style="statusStyle(row.status)">{{row.status}}</span></td></tr></tbody></table></div>
       <ul class="design-mobile-list" aria-label="需求列表"><li v-for="row in matches" :key="row.id"><div class="design-mobile-heading"><small>{{row.id}}</small><span class="design-status" :style="statusStyle(row.status)">{{row.status}}</span></div><button class="design-title-button" @click="detail(row)">{{row.title}}</button><p>{{row.description}}</p><small>所属模块：{{row.module}}</small></li></ul>
      </template>
     </div>
     <div class="design-state-controls"><span>评审状态演示：</span><button class="design-secondary" @click="scenario='normal'">正常</button><button class="design-secondary" @click="scenario='error'">加载失败</button><button class="design-secondary" @click="scenario='denied'">无权限</button></div>
    </template>
    <template v-else-if="route==='detail'"><h1>需求详情</h1><p class="design-muted">编号 {{selected.id}} <span class="design-status" :style="statusStyle(selected.status)">{{selected.status}}</span></p><article class="design-card design-form"><h2>{{selected.title}}</h2><p>所属模块：{{selected.module}}</p><p class="design-detail">{{selected.description}}</p><button class="design-primary" @click="navigate('list')">返回列表</button></article></template>
    <template v-else><h1>新建需求</h1><p class="design-muted">描述目标与业务范围，提交后进入设计流程。</p><form class="design-card design-form" novalidate @submit.prevent="submit"><h2>基本信息</h2>
     <label for="requirement-title">需求名称 *</label><input id="requirement-title" ref="titleInput" v-model="form.title" :disabled="submitting" maxlength="50" aria-describedby="requirement-title-error" :aria-invalid="!!errors.title" placeholder="请输入需求名称"><small id="requirement-title-error" class="design-field-error">{{errors.title}}</small>
     <label for="requirement-module">所属模块 *</label><select id="requirement-module" v-model="form.module" :disabled="submitting"><option>规范库</option><option>设计交付</option><option>工具接入</option></select>
     <label for="requirement-description">需求说明 *</label><textarea id="requirement-description" ref="descriptionInput" v-model="form.description" :disabled="submitting" maxlength="1000" aria-describedby="requirement-description-error" :aria-invalid="!!errors.description" placeholder="描述项目背景、用户目标和业务范围"></textarea><small id="requirement-description-error" class="design-field-error">{{errors.description}}</small>
     <label class="design-checkbox"><input v-model="form.failure" type="checkbox" :disabled="submitting">演示提交失败及恢复</label><div class="design-actions"><button class="design-primary" type="submit" :disabled="submitting">{{submitting?'正在创建…':'创建需求'}}</button><button class="design-secondary" type="button" @click="navigate('list')">取消</button></div>
    </form></template>
   </section>
  </main>
 </div>
</template>
