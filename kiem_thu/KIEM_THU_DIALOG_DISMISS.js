'use strict';
// Real modal/cancellation functions, deterministic DOM and transport; no governance claims.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const events={},nodes={};let fields=[],template=false,closeCount=0,confirmCount=0,allowDiscard=false;
function node(id){return nodes[id]??={id,value:'',children:[],dataset:{},isConnected:true,disabled:false,
 classList:{values:new Set(),add(x){this.values.add(x)},remove(x){this.values.delete(x)},contains(x){return this.values.has(x)},toggle(){}},
 setAttribute(k,v){this[k]=v},getClientRects(){return [{}]},closest(){return null},focus(){doc.activeElement=this;this.focused=true},
 querySelector(){return null},querySelectorAll(){return []}}}
const body=node('modalBody');let html='';
Object.defineProperty(body,'innerHTML',{get(){return html},set(v){html=v;this.children=[];fields=v.includes('Re-render template')?[node('role')]:[];template=v.includes('Re-render template');doc.activeElement=node('body')}});
body.prepend=function(n){this.children.unshift(n)};
body.contains=n=>fields.includes(n)||body.children.includes(n);
body.querySelector=s=>s==='.modalClose'?body.children.find(n=>n.className==='modalClose noprint')||null:s==='#staffingProfile'&&template?node('profile'):null;
body.querySelectorAll=s=>s==='[data-template-role]'?fields.filter(n=>n.dataset.templateRole!==undefined):s==='[data-template-person]'?fields.filter(n=>n.dataset.templatePerson!==undefined):fields.filter(n=>n.id.startsWith('catalog_')||n.id.startsWith('team_')||n.id==='catalogShipName');
const doc={activeElement:node('opener'),getElementById:id=>id==='personnelRoot'?null:node(id),createElement:()=>({...node('button'+(++closeCount))}),addEventListener(k,fn){(events[k]??=[]).push(fn)},querySelectorAll(){return []},querySelector(){return null},documentElement:{style:{setProperty(){}}},body:node('body')};
const box={console,document:doc,window:{addEventListener(){}},history:{replaceState(){}},URLSearchParams,setTimeout,clearTimeout,encodeURIComponent,confirm(){confirmCount++;return allowDiscard}};
vm.createContext(box);const run=s=>vm.runInContext(s,box);
for(const f of ['ung_dung.js','local_ui.js','danh_muc.js'])run(fs.readFileSync(__dirname+'/../giao_dien/tai_nguyen/'+f,'utf8').replace(/^go\('home'\);$/m,''));
run("info={context:'ctx',people:['SYNTH']};api=async()=>({});personnelApi=async()=>({})");
function fire(type,target,extra={}){for(const fn of events[type]||[])fn({type,target,button:0,pointerId:1,isTrusted:true,...extra})}
function shown(){return !node('modal').classList.contains('hide')}
function open(){run("modal('<h2>Temporary chooser</h2>')")}
function business(id='catalog_people',value='original'){const f=node(id);f.value=value;f.matches=()=>true;fields=[f];run('decorateLocalModal()');return f}
let passed=0;
function check(name,fn){fn();passed++;console.log('PASS '+name)}
(async()=>{
 node('modal').classList.add('hide');open();
 check('one accessible X, duplicate decoration avoided',()=>{run('decorateLocalModal()');assert.equal(body.children.length,1);assert.equal(body.children[0].type,'button');assert.equal(body.children[0]['aria-label'],'Đóng hộp thoại')});
 body.children[0].onclick();check('X immediately closes unchanged temporary chooser',()=>assert.equal(shown(),false));
 open();fire('keydown',body,{key:'Escape',preventDefault(){}});check('Escape uses dismissal and closes chooser',()=>assert.equal(shown(),false));
 open();fire('pointerdown',node('modal'));fire('pointerup',node('modal'));check('backdrop down and up closes',()=>assert.equal(shown(),false));
 open();fire('pointerdown',body);fire('pointerup',node('modal'));check('inside-to-backdrop drag does not close',()=>assert.equal(shown(),true));
 fire('pointerdown',node('modal'));fire('pointerup',body);check('backdrop-to-inside drag does not close',()=>assert.equal(shown(),true));
 fire('pointerdown',node('modal'));fire('pointerup',node('modal'),{pointerId:2});check('different pointer does not close',()=>assert.equal(shown(),true));
 fire('pointerdown',node('modal'));fire('pointercancel',node('modal'));fire('pointerup',node('modal'));check('cancelled pointer does not close',()=>assert.equal(shown(),true));
 run('safeEscape()');
 for(const flag of ['saving','uploading','localBusy','printBusy']){open();run(flag+'=true');assert.equal(run('safeEscape()'),false);assert.equal(shown(),true);run(flag+'=false;closeModal()')}
 check('save upload local-confirm and print busy block dismissal',()=>{});
 open();run('personnelImport={confirming:true}');assert.equal(run('safeEscape()'),false);assert.equal(shown(),true);run('personnelImport=null;closeModal()');
 check('personnel confirm cannot be cancelled',()=>{});
 open();let f=business();f.value='edited';fire('input',f);assert.equal(run('safeEscape()'),false);assert.equal(shown(),true);assert.equal(f.value,'edited');allowDiscard=true;run('safeEscape()');
 check('actual catalog edit asks discard, decline preserves DOM, accept closes',()=>assert.equal(shown(),false));
 allowDiscard=false;const count=confirmCount;open();f=business();f.value='programmatic suggestion';fire('click',f);run('safeEscape()');assert.equal(confirmCount,count);
 open();f=business();fire('input',f);run('safeEscape()');assert.equal(confirmCount,count);
 open();f=business();f.value='changed';fire('input',f);f.value='original';run('safeEscape()');assert.equal(confirmCount,count);
 check('default programmatic and reverted values do not prompt',()=>{});
 open();const search=node('search');search.matches=()=>false;fields=[search];fire('input',search);run('safeEscape()');check('search choice does not become business edit',()=>assert.equal(confirmCount,count));
 open();run("globalThis.staffingDraft={DAY:[{role:'original',person:'SYNTH'}]};globalThis.staffingProfile='DAY'");template=true;const role=node('role');role.dataset.templateRole='0';role.value='original';role.matches=()=>true;fields=[role];run('decorateLocalModal()');role.value='edited';fire('change',role);run("staffingDraft.DAY[0].role='edited';modal('<h2>Re-render template</h2>')");template=true;fields=[role];run('decorateLocalModal()');assert.equal(run('safeEscape()'),false);assert.equal(shown(),true);allowDiscard=true;run('safeEscape()');
 check('template edits retain original baseline across rerender',()=>{});
 const opener=node('originalOpener');doc.activeElement=opener;open();assert.equal(doc.activeElement,node('body'));doc.activeElement=node('nested');run("modal('<h2>Nested</h2>');closeModal()");check('opener captured before mount and retained through nested render',()=>assert.equal(doc.activeElement,opener));
 doc.activeElement=opener;open();opener.isConnected=false;run('closeModal()');check('disconnected opener returns focus to main content',()=>assert.equal(doc.activeElement,node('mainContent')));opener.isConnected=true;
 const pending=run("chooseSinglePerson('Synthetic picker')");run('safeEscape()');assert.equal(await pending,null);check('single-person promise resolves null through actual owner',()=>assert.equal(run('personResolver'),null));
 open();run("personnelImport={context:'ctx',generation:2,confirming:false};globalThis.oldImport=personnelImport");run('safeEscape()');check('PNI owner invalidates generation and closes',()=>{assert.equal(run('oldImport.generation'),3);assert.equal(run('personnelImport'),null);assert.equal(shown(),false)});
 open();run("localPlan={kind:'schema_upgrade',context:'ctx',nonce:'nonce'};globalThis.before=localGeneration");run('safeEscape()');check('local owner clears nonce plan and advances generation',()=>{assert.equal(run('localPlan'),null);assert.ok(run('localGeneration>before'));assert.equal(shown(),false)});
 const css=fs.readFileSync(__dirname+'/../giao_dien/tai_nguyen/style.css','utf8');check('close control scoped sticky reserved heading and hidden for print',()=>{assert.match(css,/\.modalClose\{[^}]*position:sticky/);assert.match(css,/\.modal \.modalHead\{padding-right:52px/);assert.match(css,/@media print\{\.modalClose\{display:none!important\}\}/)});
 console.log(passed+' focused dialog-dismiss checks PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
