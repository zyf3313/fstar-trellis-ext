import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
async function fixture(t){
 const dir=await fs.mkdtemp(path.join(os.tmpdir(),'design-preview-'));
 t.after(()=>fs.rm(dir,{recursive:true,force:true}));
 const consumer=path.join(dir,'consumer'),source=path.join(dir,'generated');
 await fs.mkdir(path.join(consumer,'scripts'),{recursive:true});await fs.mkdir(source);
 await fs.copyFile(path.join(root,'scripts/sync-design.mjs'),path.join(consumer,'scripts/sync-design.mjs'));
 const files={'design.json':'{"version":"fixture"}','tokens.css':':root{--primary:#177E74;}'};
 for(const [name,bytes] of Object.entries(files))await fs.writeFile(path.join(source,name),bytes);
 const manifest={version:'fixture',boards:[{id:'fixture-board'}],source_sha256:sha(files['design.json']),outputs:Object.entries(files).map(([name,bytes])=>({path:'generated/'+name,sha256:sha(bytes)}))};
 const save=()=>fs.writeFile(path.join(source,'manifest.json'),JSON.stringify(manifest));await save();
 return {consumer,source,manifest,save,dir,run:()=>spawnSync(process.execPath,[path.join(consumer,'scripts/sync-design.mjs'),source],{encoding:'utf8',timeout:10000})};
}
test('standalone consumer syncs without the author checkout',async t=>{
 const f=await fixture(t);const result=f.run();assert.equal(result.status,0,result.stderr);
 assert.equal((await fs.readFile(path.join(f.consumer,'src/design/design.json'),'utf8')),'{"version":"fixture"}');
 assert.equal(JSON.parse(await fs.readFile(path.join(f.consumer,'public/design/manifest.json'),'utf8')).version,'fixture');
});
test('stale source output is rejected before changing an existing preview',async t=>{
 const f=await fixture(t);assert.equal(f.run().status,0);
 const before=await fs.readFile(path.join(f.consumer,'public/design/design.json'));
 await fs.writeFile(path.join(f.source,'design.json'),'{"version":"changed"}');
 assert.notEqual(f.run().status,0);assert.deepEqual(await fs.readFile(path.join(f.consumer,'public/design/design.json')),before);
});
test('manifest traversal cannot copy outside design output',async t=>{
 const f=await fixture(t);f.manifest.outputs.push({path:'generated/../private.txt',sha256:'irrelevant'});await f.save();
 const result=f.run();assert.notEqual(result.status,0);assert.match(result.stderr,/Invalid source path/);
 await assert.rejects(fs.stat(path.join(f.consumer,'public')));
});
test('symlink outside design output is rejected',async t=>{
 const f=await fixture(t);const outside=path.join(f.dir,'outside.txt');await fs.writeFile(outside,'outside');
 await fs.symlink(outside,path.join(f.source,'alias.txt'));f.manifest.outputs.push({path:'generated/alias.txt',sha256:sha('outside')});await f.save();
 const result=f.run();assert.notEqual(result.status,0);assert.match(result.stderr,/escapes design directory/);
});
test('provider projections update with the source and preserve local edits',async t=>{
 const f=await fixture(t);
 const initial='<!-- personal-ui-module-generated -->\n[Source](design.json)\n';
 await fs.writeFile(path.join(f.source,'DESIGN.md'),initial);
 f.manifest.outputs.push({path:'generated/DESIGN.md',sha256:sha(initial)});await f.save();
 assert.equal(f.run().status,0);
 const target=path.join(f.consumer,'DESIGN.md');
 assert.match(await fs.readFile(target,'utf8'),/src\/design\/design.json/);
 const updated=initial+'Source version 2\n';
 await fs.writeFile(path.join(f.source,'DESIGN.md'),updated);
 f.manifest.outputs.find(row=>row.path==='generated/DESIGN.md').sha256=sha(updated);await f.save();
 assert.equal(f.run().status,0);assert.match(await fs.readFile(target,'utf8'),/Source version 2/);
 await fs.appendFile(target,'My local rule\n');
 const before=await fs.readFile(target);
 const result=f.run();assert.notEqual(result.status,0);assert.match(result.stderr,/locally modified/);
 assert.deepEqual(await fs.readFile(target),before);
});
