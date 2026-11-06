'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements=new Map(),sessions=new Map();
function el(id){if(!elements.has(id))elements.set(id,{value:'',textContent:'',innerHTML:'',classList:{add(){},remove(){},toggle(){}}});return elements.get(id)}
const sandbox={history:{replaceState(){}},window:{addEventListener(){}},document:{addEventListener(){},getElementById:el,querySelectorAll(){return []}},sessionStorage:{getItem:k=>sessions.get(k)||null,setItem:(k,v)=>sessions.set(k,v)},URLSearchParams,encodeURIComponent,setTimeout,clearTimeout};
vm.createContext(sandbox);const run=code=>vm.runInContext(code,sandbox),copy=code=>JSON.parse(run('JSON.stringify('+code+')'));
run(fs.readFileSync(__dirname+'/tai_nguyen/ung_dung.js','utf8'));run('go=()=>{}');
run(fs.readFileSync(__dirname+'/tai_nguyen/phan_cong_mau.js','utf8'));
run(fs.readFileSync(__dirname+'/tai_nguyen/danh_muc.js','utf8'));
function reset(){run(`info={context:'main',readonly:false,review:false,roles:['PHỤ TRÁCH CHUNG','GATE','TALLY TÀU'],teams:[{id:'team1',name:'Ca 1',people:['An']},{id:'team2',name:'Ca 2',people:['Bình']},{id:'team3',name:'Ca 3',people:[]}],staff_templates:{team1:[{role:'GATE',people:['An']}],team2:[{role:'GATE',people:['Bình']}],team3:[],day:[{role:'GATE',people:['Chi']}]}};
report={date:'2026-11-05',shift:'DAY',status:'draft',actor:'An',staffing:[{role:'GATE',people:'Old'}],jobs:[],notes:'keep'};
saving=false;uploading=false;conflict=false;pendingStaffPlan=null;collect=()=>{};renderStaff=()=>{};closeModal=()=>{};var touchCount=0;touch=()=>{touchCount++};var shown='';modal=html=>{shown=html};var messages=[];toast=s=>messages.push(s);error=e=>{throw e};`)}
const tests=[];const test=(name,fn)=>tests.push([name,fn]);
test('preview and cancel never mutate report',()=>{
 run("applyShiftTemplate('team1')");assert.equal(run("report.staffing[0].people"),'Old');assert.ok(run('shown').includes('Xác nhận áp dụng'));
 run('cancelStaffPlan()');assert.equal(run('pendingStaffPlan'),null);assert.equal(run('touchCount'),0);
});
test('confirm replaces only configured positions and preserves other data',()=>{
 run("report.staffing.push({role:'OTHER',people:'Keep'});applyShiftTemplate('team1');confirmStaffPlan()");
 assert.equal(run('report.staffing[0].people'),'An');assert.equal(run('report.staffing[1].people'),'Keep');
 assert.equal(run('report.notes'),'keep');assert.equal(run('report.actor'),'An');assert.equal(run('touchCount'),1);
 assert.equal(sessions.get('ca_staff_team'),'team1');
});
test('switch rotating crew then append day staff without duplication',()=>{
 run("applyShiftTemplate('team1');confirmStaffPlan();applyShiftTemplate('team2');confirmStaffPlan();applyDayStaff();confirmStaffPlan()");
 assert.equal(run('report.staffing[0].people'),'Bình; Chi');
 run('applyDayStaff();confirmStaffPlan()');assert.equal(run('report.staffing[0].people'),'Bình; Chi');assert.equal(run('touchCount'),3);
});
test('day append preserves manual people and uses exact name deduplication',()=>{
 assert.equal(run("mergeStaffNames('An; Chi',['an','Chi','Bình'])"),'An; Chi; Bình');
 run('applyDayStaff();confirmStaffPlan()');assert.equal(run('report.staffing[0].people'),'Old; Chi');
});
test('multiple ship assignments remain separate for both rotating and day templates',()=>{
 run("report.staffing=[{role:'TALLY TÀU',ships:['A'],people:'An'},{role:'TALLY TÀU',ships:['B'],people:'Bình'}];var before=JSON.stringify(report.staffing);var p=planStaffing(report.staffing,[{role:'TALLY TÀU',people:['Chi']}],'replace');var d=planStaffing(report.staffing,[{role:'TALLY TÀU',people:['Chi']}],'append')");
 assert.equal(run('JSON.stringify(p.staffing)'),run('before'));assert.equal(run('JSON.stringify(d.staffing)'),run('before'));assert.equal(run('p.skipped.length'),1);
});
test('single ship keeps its vessel while receiving people',()=>{
 run("var p=planStaffing([{role:'TALLY TÀU',ships:['A'],people:'Old'}],[{role:'TALLY TÀU',people:['An']}],'replace')");
 assert.equal(run('p.staffing[0].people'),'An');assert.deepEqual(copy('p.staffing[0].ships'),['A']);
});
test('explicit empty slot clears only after confirmation',()=>{
 run("info.staff_templates.team1=[{role:'GATE',people:[]},{role:'PHỤ TRÁCH CHUNG',people:['An']}];applyShiftTemplate('team1')");
 assert.equal(run('report.staffing[0].people'),'Old');assert.ok(run('shown').includes('(Để trống)'));
 run('confirmStaffPlan()');assert.equal(run('report.staffing[0].people'),'');
});
test('changed report or DB after preview blocks application',()=>{
 run("applyShiftTemplate('team1');report.staffing[0].people='Concurrent';confirmStaffPlan()");assert.equal(run('report.staffing[0].people'),'Concurrent');assert.equal(run('touchCount'),0);
 run("applyShiftTemplate('team1');info.context='other';confirmStaffPlan()");assert.equal(run('report.staffing[0].people'),'Concurrent');
});
test('readonly and in-flight save block application',()=>{
 run("info.readonly=true;applyShiftTemplate('team1')");assert.equal(run('pendingStaffPlan'),null);
 run("info.readonly=false;saving=true;applyDayStaff()");assert.equal(run('pendingStaffPlan'),null);
});
test('closed report stays closed and preview requires reason at save',()=>{
 run("report.status='closed';applyShiftTemplate('team1')");assert.ok(run('shown').includes('kèm lý do'));
 run('confirmStaffPlan()');assert.equal(run('report.status'),'closed');
});
test('empty crew template cannot clear report',()=>{
 run("applyShiftTemplate('team3')");assert.equal(run('pendingStaffPlan'),null);assert.equal(run('report.staffing[0].people'),'Old');
});
test('template editor groups multiple people per position and preserves blank positions',()=>{
 run("var d=newTemplateDraft({team1:[{role:'GATE',people:['An','Bình']},{role:'TALLY TÀU',people:[]}],team2:[],team3:[],day:[{role:'GATE',people:['Chi']}]});var c=compileStaffTemplates(d)");
 assert.deepEqual(copy('c.team1'),[{role:'GATE',people:['An','Bình']},{role:'TALLY TÀU',people:[]}]);
 assert.deepEqual(copy('c.day'),[{role:'GATE',people:['Chi']}]);assert.deepEqual(copy('c.team2').map(x=>x.role),['PHỤ TRÁCH CHUNG','GATE','TALLY TÀU']);
});
test('plan is a copy and rejects exceeding staff capacity',()=>{
 run("var original=JSON.stringify(report.staffing);var planned=planStaffing(report.staffing,[{role:'GATE',people:['An']}],'replace')");assert.equal(run('JSON.stringify(report.staffing)'),run('original'));
 assert.throws(()=>run("planStaffing(Array.from({length:200},(_,i)=>({role:'R'+i,people:'An'})),[{role:'NEW',people:['Chi']}],'append')"),/200/);
});
(async()=>{for(const [name,fn] of tests){reset();await fn();console.log('OK',name)}console.log(tests.length+' template behavior tests passed (Node VM).')})().catch(e=>{console.error(e);process.exitCode=1});
