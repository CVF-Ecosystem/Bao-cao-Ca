'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
(async()=>{
 const calls=[],nodes={backupDirectory:{value:'D:/DuPhong'},confirmRestore:{value:'KHOI PHUC'},doRestore:{disabled:false}};
 const data={warning:'Chưa chọn nơi dự phòng',backups:[{id:'abc123',name:'Bản <sao>.db',location:'D:/backup',modified:'2026-11-06',bytes:100}],external_directory:''};
 let content='',left=true;
 const c={info:{context:'old',review:false},dirty:true,timer:null,report:{},clearTimeout(){},leave:()=>left,
 esc:s=>String(s??'').replace(/</g,'&lt;'),timeLabel:s=>s,dateLabel:s=>s,$:id=>nodes[id],
 modal:s=>content=s,toast:s=>calls.push(['toast',s]),error:e=>{throw e},closeModal:()=>calls.push(['closed']),
 refreshInfo:async()=>{},go:async name=>calls.push(['go',name]),
 api:async(path,body)=>{calls.push([path,body]);if(path==='/api/protection')return data;if(path==='/api/restore-preview')return {reports:3,revisions:74,sha256:'digest',first_day:'2026-11-04',last_day:'2026-11-05'};if(path==='/api/protection-directory')return {directory:'E:/Chon'};return data;}};
 vm.createContext(c);vm.runInContext(fs.readFileSync(__dirname+'/../tai_nguyen/bao_ve.js','utf8'),c);
 await c.openProtection();assert(content.includes('Chưa chọn nơi dự phòng'));assert(content.includes('Bản &lt;sao>.db'));assert.strictEqual(c.dirty,false);
 await c.previewRestore('abc123');assert(content.includes('3 ca'));assert(content.includes('KHOI PHUC'));
 await c.performRestore();let request=calls.find(x=>x[0]==='/api/restore')[1];assert.strictEqual(request.context,'old');assert.strictEqual(request.sha256,'digest');assert.strictEqual(request.confirmation,'KHOI PHUC');assert(calls.some(x=>x[0]==='go'&&x[1]==='home'));assert.strictEqual(c.report,null);
 await c.chooseProtectionDirectory();assert.strictEqual(nodes.backupDirectory.value,'E:/Chon');
 c.info.review=true;let count=calls.length;await c.openProtection();assert.strictEqual(calls.length,count+1);c.info.review=false;
 left=false;count=calls.length;await c.openProtection();assert.strictEqual(calls.length,count);
 console.log('6 protection UI behavior checks passed: state, escaping, preview, restore/context, directory picker, review/unsaved guard.');
})().catch(e=>{console.error(e);process.exit(1)});
