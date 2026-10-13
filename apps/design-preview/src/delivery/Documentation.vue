<script setup lang="ts">
import {nextTick,onBeforeUnmount,onMounted,ref,watch} from 'vue';
import {marked} from 'marked';
import DOMPurify from 'dompurify';
import mermaid from 'mermaid';
const selected=ref<'prd'|'tdd'|'review'>('prd');
const base=import.meta.env.BASE_URL+'design/';
const html=ref(''),error=ref(''),busy=ref(true),content=ref<HTMLElement>();
let generation=0;
let controller:AbortController|undefined;
mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral',flowchart:{htmlLabels:false}});
async function load(){
 controller?.abort();controller=new AbortController();const current=++generation;busy.value=true;error.value='';
 try{
  const response=await fetch(base+'docs/'+selected.value+'.zh-CN.md',{signal:controller.signal});
  if(!response.ok)throw new Error('Document unavailable');
  const text=await response.text();if(current!==generation)return;
  html.value=DOMPurify.sanitize(await marked.parse(text));await nextTick();
  for(const link of content.value?.querySelectorAll<HTMLAnchorElement>('a')||[]){
   if(link.getAttribute('href')==='../source/design.json')link.href=base+'design.json';
  }
  const diagrams=Array.from(content.value?.querySelectorAll<HTMLElement>('pre > code.language-mermaid')||[]);
  for(const [index,code] of diagrams.entries()){
   if(current!==generation)return;
   const result=await mermaid.render('design-document-'+current+'-'+index,code.textContent||'');
   if(current!==generation||!code.isConnected)return;
   const target=code.parentElement!;target.innerHTML=DOMPurify.sanitize(result.svg,{USE_PROFILES:{svg:true}});target.className='preview-diagram';
  }
 }catch(cause){if(current===generation&&!(cause instanceof DOMException&&cause.name==='AbortError'))error.value='文档或图表未能加载，可下载原始 Markdown 查看。';}
 finally{if(current===generation)busy.value=false;}
}
function follow(event:MouseEvent){
 const link=(event.target instanceof Element?event.target.closest('a'):null);
 const href=link?.getAttribute('href')||'';
 if(href==='prd.zh-CN.md'||href==='tdd.zh-CN.md'||href==='review.zh-CN.md'){event.preventDefault();selected.value=href.startsWith('prd')?'prd':href.startsWith('tdd')?'tdd':'review';}
}
watch(selected,load);onMounted(load);onBeforeUnmount(()=>{generation++;controller?.abort();});
</script>
<template><section class="preview-page"><p class="preview-eyebrow">需求与方案</p><h1>中文设计文档</h1><p>PRD 描述背景、业务全景、模块职责和逐功能业务；TDD 用十二章展开实现与图示。</p><div class="design-actions"><button :class="selected==='prd'?'design-primary':'design-secondary'" @click="selected='prd'">PRD</button><button :class="selected==='tdd'?'design-primary':'design-secondary'" @click="selected='tdd'">TDD 技术方案</button><button :class="selected==='review'?'design-primary':'design-secondary'" @click="selected='review'">设计技能应用记录</button><a :href="base+'docs/'+selected+'.zh-CN.md'" download>下载当前 Markdown 文档</a></div><p v-if="busy" role="status">正在加载文档和图表…</p><p v-if="error" role="alert">{{error}}</p><article ref="content" class="preview-markdown" @click="follow" v-html="html"></article></section></template>
