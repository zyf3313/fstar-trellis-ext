import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const JSZip=require('jszip');
const Ajv=require('ajv');
const schemas=require('@sketch-hq/sketch-file-format').default;
const root=path.dirname(fileURLToPath(import.meta.url));
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const read=relative=>fs.readFile(path.join(root,relative));
const manifest=JSON.parse(await read('generated/manifest.json'));
const source=JSON.parse(await read('source/design.json'));
function checkHash(actual,expected,file){assert.equal(sha(actual),expected,'Design evidence is stale: '+file);}
for(const item of [...manifest.inputs,...manifest.outputs])checkHash(await read(item.path),item.sha256,item.path);
async function checkDocumentLinks(directory){
 const exportRoot=await fs.realpath(directory);
 let checked=0;
 for(const item of manifest.outputs){
  const relative=item.path.replace(/^generated\//,'');
  checkHash(await fs.readFile(path.join(exportRoot,relative)),item.sha256,relative);
  if(!relative.endsWith('.md'))continue;
  const file=path.join(exportRoot,relative);
  const markdown=await fs.readFile(file,'utf8');
  // 当前导出文档使用行内 Markdown 链接；外部 URL 与页内锚点不属于文件门禁。
  const links=markdown.matchAll(/!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+["'][^\n]*?["'])?\s*\)/g);
  for(const match of links){
   const reference=match[1]||match[2];
   if(reference.startsWith('#')||reference.startsWith('//')||/^[a-z][a-z\d+.-]*:/i.test(reference))continue;
   const target=path.resolve(path.dirname(file),decodeURIComponent(reference.split(/[?#]/,1)[0]));
   assert.ok(target.startsWith(exportRoot+path.sep),'Document link escapes export: '+relative+' -> '+reference);
   const actual=await fs.realpath(target).catch(()=>null);
   assert.ok(actual&&actual.startsWith(exportRoot+path.sep),'Missing local document link: '+relative+' -> '+reference);
   assert.ok((await fs.stat(actual)).isFile(),'Document link is not a file: '+relative+' -> '+reference);
   checked++;
  }
 }
 return checked;
}
const documentLinks={generated:await checkDocumentLinks(path.join(root,'generated'))};
const syncedIndex=process.argv.indexOf('--synced');
if(syncedIndex!==-1){
 const directory=process.argv[syncedIndex+1];
 assert.ok(directory&&!directory.startsWith('--'),'--synced requires an exported design directory');
 documentLinks.synced=await checkDocumentLinks(path.resolve(directory));
}
assert.equal(manifest.version,source.version);
assert.equal(manifest.source_sha256,sha(await read('source/design.json')));
const boards=source.modules.flatMap(m=>m.features.flatMap(f=>f.boards));
assert.equal(boards.length,8);
assert.deepEqual(manifest.boards.map(b=>b.id),boards.map(b=>b.id));
for(const feature of source.modules.flatMap(m=>m.features)){
 for(const reference of [feature.prd,feature.tdd]){
  const [file,anchor]=reference.split('#');
  assert.ok((await read(file)).toString().includes('id="'+anchor+'"'),reference);
 }
}
const zip=await JSZip.loadAsync(await read('generated/exports/requirements.sketch'));
// The official draft-07 schema has literal unescaped braces in patterns, so use
// its non-Unicode regular expressions while checking every required property.
const ajv=new Ajv({strict:false,allErrors:true,unicodeRegExp:false});
const decoded={};
for(const [name,file] of Object.entries(zip.files))if(name.endsWith('.json'))decoded[name]=JSON.parse(await file.async('string'));
for(const [name,schema] of [['meta.json',schemas.meta],['document.json',schemas.document],['user.json',schemas.user]]){
 const validate=ajv.compile(schema);assert.ok(validate(decoded[name]),name+': '+JSON.stringify(validate.errors));
}
const pages=Object.entries(decoded).filter(([name])=>name.startsWith('pages/')).map(([,value])=>value);
const validatePage=ajv.compile(schemas.page);
pages.forEach(page=>assert.ok(validatePage(page),JSON.stringify(validatePage.errors)));
const importedBoards=pages.flatMap(p=>p.layers);
assert.equal(importedBoards.length,boards.length);
assert.equal(new Set(importedBoards.map(b=>b.do_objectID)).size,boards.length);
assert.ok(importedBoards.every(b=>b.layers.some(l=>l._class==='text')&&b.layers.some(l=>l._class==='rectangle')));
assert.ok(importedBoards.flatMap(b=>b.layers).some(l=>l.attributedString?.string==='需求管理'));
const parsed=await require('sketch-constructor').Sketch.fromFile(path.join(root,'generated/exports/requirements.sketch'));
assert.equal(parsed.pages.length,pages.length);
// A source change must invalidate the old evidence without accepting a stale build.
assert.throws(()=>checkHash(Buffer.from(JSON.stringify({...source,version:'changed'})),manifest.source_sha256,'source/design.json'));
if(process.argv.includes('--rebuild')){
 const prior=await read('generated/manifest.json');
 for(let i=0;i<2;i++){
  const built=spawnSync(process.execPath,['build.mjs'],{cwd:root,encoding:'utf8',timeout:60000});
  assert.equal(built.status,0,built.stderr||'Build failed or timed out');
  assert.equal((await read('generated/manifest.json')).toString(),prior.toString(),'Manifest not reproducible');
  for(const item of manifest.outputs)checkHash(await read(item.path),item.sha256,item.path);
 }
}
console.log(JSON.stringify({status:'passed',format:decoded['meta.json'].version,boards:boards.length,
 editable_layers:importedBoards.reduce((n,b)=>n+b.layers.length,0),chinese_roundtrip:'passed',
 document_links:'passed',local_document_links:documentLinks,drift_rejected:true,rebuilds:process.argv.includes('--rebuild')?2:0,
 platforms:manifest.platforms,user_confirmation:manifest.user_confirmation}));
