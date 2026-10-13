import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const source=await fs.realpath(path.resolve(process.argv[2]||path.join(root,'../../examples/ui-module/generated')));
const manifest=JSON.parse(await fs.readFile(path.join(source,'manifest.json'),'utf8'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const planned=[];
// Validate the entire input set before touching the preview. Existing snapshots
// remain useful when the source checkout is unavailable or outdated.
for(const item of manifest.outputs){
 const relative=item.path.replace(/^generated\//,'');
 if(path.isAbsolute(relative)||relative.split(/[\\/]/).includes('..'))throw new Error('Invalid source path');
 const sourceFile=await fs.realpath(path.join(source,relative));
 if(!sourceFile.startsWith(source+path.sep))throw new Error('Source file escapes design directory');
 const bytes=await fs.readFile(sourceFile);
 if(sha(bytes)!==item.sha256)throw new Error('Stale design output: '+relative);
 planned.push([relative,bytes]);
}
for(const name of ['design.json','tokens.css'])if(!planned.some(([file])=>file===name))throw new Error('Missing required design output: '+name);
const projections=[];
const projectLinks=bytes=>bytes.toString().replaceAll('(design.json)','(src/design/design.json)').replaceAll('(docs/prd.zh-CN.md)','(public/design/docs/prd.zh-CN.md)');
for(const name of ['PRODUCT.md','DESIGN.md']){
 const item=planned.find(([file])=>file===name);if(!item)continue;
 const target=path.join(root,name);
 try{if((await fs.lstat(target)).isSymbolicLink())throw new Error('Provider context path is a symlink: '+name);}catch(error){if(error.code!=='ENOENT')throw error;}
 let previous='';try{previous=await fs.readFile(target,'utf8');}catch(error){if(error.code!=='ENOENT')throw error;}
 let baseline='';try{baseline=projectLinks(await fs.readFile(path.join(root,'public/design',name)));}catch(error){if(error.code!=='ENOENT')throw error;}
 if(previous&&previous!==projectLinks(item[1])&&(!previous.includes('<!-- personal-ui-module-generated -->')||previous!==baseline))throw new Error('Existing provider context is locally modified or not owned: '+name);
 projections.push([target,projectLinks(item[1])]);
}
for(const [file,bytes] of planned){
 const target=path.join(root,'public/design',file);
 await fs.mkdir(path.dirname(target),{recursive:true});await fs.writeFile(target,bytes);
}
await fs.mkdir(path.join(root,'src/design'),{recursive:true});
for(const name of ['design.json','tokens.css'])await fs.copyFile(path.join(source,name),path.join(root,'src/design',name));
await fs.copyFile(path.join(source,'manifest.json'),path.join(root,'public/design/manifest.json'));
for(const [target,text] of projections)await fs.writeFile(target,text);
console.log(JSON.stringify({status:'synced',version:manifest.version,boards:manifest.boards.length,source_sha256:manifest.source_sha256}));
