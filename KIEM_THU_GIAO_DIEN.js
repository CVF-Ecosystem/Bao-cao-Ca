// Optional: node KIEM_THU_GIAO_DIEN.js. Uses Node built-ins only; no browser.
'use strict';
const assert=require('node:assert/strict'), fs=require('node:fs'), vm=require('node:vm');
const sandbox={history:{replaceState(){}},window:{addEventListener(){}},document:{addEventListener(){},getElementById(){return {}}},URLSearchParams,encodeURIComponent,setTimeout,clearTimeout};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(__dirname+'/tai_nguyen/ung_dung.js','utf8'),sandbox);
vm.runInContext(`
info={context:'context-151',version:'1.5.1'}; report={id:'2026-11-02_DAY'}; dirty=false;
var capturedURL=''; download=url=>{capturedURL=url};
exportReport();
`,sandbox);
let url=new URL(vm.runInContext('capturedURL',sandbox),'http://localhost');
assert.equal(url.searchParams.get('context'),'context-151');
assert.equal(url.searchParams.get('id'),'2026-11-02_DAY');
vm.runInContext("filterQuery=()=> 'status=closed'; exportSummary()",sandbox);
url=new URL(vm.runInContext('capturedURL',sandbox),'http://localhost');
assert.equal(url.searchParams.get('context'),'context-151');
assert.equal(url.searchParams.get('status'),'closed');
assert.equal(vm.runInContext("chiefPeople([{role:'PHỤ TRÁCH CHUNG',people:''},{role:'PHỤ TRÁCH CHUNG',people:'Chief'},{role:'PHỤ TRÁCH CHUNG',people:'Chief'}])",sandbox),'Chief');
vm.runInContext("leave=()=>true; error=()=>{}; var capturedBody;",sandbox);
sandbox.fetch=async(_url, options)=>{sandbox.capturedBackup=JSON.parse(options.body);return {ok:false,json:async()=>({error:'stop after request capture'})}};
(async()=>{
 await vm.runInContext('backup()',sandbox);
 assert.equal(sandbox.capturedBackup.context,'context-151');
 console.log('4 JavaScript checks passed: chief, report export, summary export, backup context.');
})().catch(e=>{console.error(e);process.exitCode=1});
