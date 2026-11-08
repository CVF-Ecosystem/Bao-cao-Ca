'use strict';
// Behavioral tests execute product functions with a minimal DOM, no external packages.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const nodes={},events={};
function element(id){return nodes[id]??=( {value:'',checked:false,textContent:'',innerHTML:'',dataset:{},children:[],classList:{add(){},remove(){},contains(){return false},toggle(){}},focus(){this.focused=true},setAttribute(k,v){this[k]=v},querySelector(){return null}} )}
const doc={addEventListener(k,fn){events[k]=fn},getElementById:element,querySelectorAll(){return []},querySelector(){return null},documentElement:{style:{setProperty(k,v){nodes[k]=v}}},body:{classList:{add(){},remove(){}}}};
const box={console,document:doc,window:{addEventListener(k,fn){events[k]=fn}},history:{replaceState(){}},URLSearchParams,setTimeout,clearTimeout,encodeURIComponent};vm.createContext(box);
for(const file of ['bao_ve.js','ung_dung.js','local_ui.js'])vm.runInContext(fs.readFileSync(__dirname+'/../giao_dien/tai_nguyen/'+file,'utf8'),box);
const run=code=>vm.runInContext(code,box);let passed=0;
function check(name,fn){fn();passed++;console.log('PASS '+name)}
(async()=>{
 // Isolated opening harness retains the real open/render/save owners, stubbing only IO and section HTML.
 const openingEvents=[],openingNodes={};
 const layout={scrollTop:185.6,scrollTo(x,y){this.scrollTop=y;openingEvents.push(['layout',x,y])}};
 let documentScroll=700;
 const seedScroll=()=>{layout.scrollTop=185.6;documentScroll=700};
 const assertRetained=()=>assert.deepEqual([layout.scrollTop,documentScroll],[185.6,700]);
 const assertReset=()=>assert.deepEqual([layout.scrollTop,documentScroll],[0,0]);
 const openingNode=id=>openingNodes[id]??={value:'',innerHTML:'',textContent:'',classList:{toggle(){},add(){},contains(){return true}},contains(){return false}};
 const opening={console,history:{replaceState(){}},document:{getElementById:openingNode,querySelector(selector){return selector==='.layout'?layout:null},querySelectorAll(){return []},addEventListener(){},activeElement:null},window:{addEventListener(){},scrollTo(x,y){documentScroll=y;openingEvents.push(['scroll',x,y])}},sessionStorage:{getItem(){return 'SYNTH ACTOR'},setItem(){}},clearTimeout,setTimeout,encodeURIComponent,confirm(){return false}};
 vm.createContext(opening);
 for(const file of ['ung_dung.js','local_ui.js'])vm.runInContext(fs.readFileSync(__dirname+'/../giao_dien/tai_nguyen/'+file,'utf8'),opening);
 const opened=code=>vm.runInContext(code,opening);
 opening.markRender=()=>openingEvents.push(['render']);
 opened("info={roles:[],jobs:[],context:'ctx'};editorHeader=editorNotice=editorTabs=staffSection=jobsSection=notesSection=filesSection=editorToolbar=()=>'';renderStaff=()=>markRender();renderJobs=renderTasks=renderAttachments=()=>{};error=e=>{globalThis.openError=e.message};toast=()=>{}");
 const fixture={id:'2026-11-08_DAY',date:'2026-11-08',shift:'DAY',version:1,status:'draft',actor:'SYNTH ACTOR',staffing:[],jobs:[],handover:[]};
 let finishOpen;opening.response=()=>new Promise(resolve=>{finishOpen=resolve});opened('api=()=>response()');
 const openingPending=opened("loadReport('2026-11-08_DAY')");assert.equal(openingEvents.length,0);assertRetained();finishOpen(structuredClone(fixture));await openingPending;
 check('existing report resets scroll only after successful render',()=>{assert.deepEqual(openingEvents,[['render'],['layout',0,0],['scroll',0,0]]);assertReset()});
 openingEvents.length=0;seedScroll();opened('dirty=true');await opened("loadReport('cancelled')");
 check('declined dirty navigation preserves scroll and editor',()=>{assert.deepEqual(openingEvents,[]);assertRetained()});
 opened("dirty=false;api=async()=>{throw new Error('read failed')}");await opened("loadReport('failed')");
 check('failed report read preserves scroll and editor',()=>{assert.deepEqual(openingEvents,[]);assert.equal(opening.openError,'read failed');assertRetained()});
 openingNode('newDate').value='2026-11-09';openingNode('newShift').value='DAY';opened('api=async()=>[]');await opened('beginShift()');
 check('new shift resets scroll after rendering',()=>{assert.deepEqual(openingEvents,[['render'],['layout',0,0],['scroll',0,0]]);assertReset()});
 openingEvents.length=0;seedScroll();openingNode('newDate').value='';await opened('beginShift()');
 openingNode('newDate').value='2026-11-09';opened("api=async()=>{throw new Error('lookup failed')}");await opened('beginShift()');
 check('invalid or failed new-shift lookup does not scroll',()=>{assert.deepEqual(openingEvents,[]);assertRetained()});
 opening.fixture=fixture;opened("api=async path=>path.startsWith('/api/reports?')?[fixture]:fixture");await opened('beginShift()');
 check('new-shift dialog opening an existing shift resets once',()=>{assert.deepEqual(openingEvents,[['render'],['layout',0,0],['scroll',0,0]]);assertReset()});
 openingEvents.length=0;seedScroll();opened('renderEditor()');
 check('same-editor rerender preserves document scroll',()=>{assert.deepEqual(openingEvents,[['render']]);assertRetained()});
 openingEvents.length=0;opened("collect=()=>{};validateJobInputs=()=>true;refreshInfo=async()=>{};api=async()=>({id:report.id,version:2,updated_at:'2026-11-08T12:00:00Z',created_at:'2026-11-08T11:00:00Z'})");assert.equal(await opened('save(false)'),true);
 check('actual autosave rerender preserves scroll',()=>{assert.deepEqual(openingEvents,[['render']]);assertRetained()});
 openingEvents.length=0;opened('touch=()=>{};addKHB()');
 check('add-row editor rerender preserves scroll',()=>{assert.deepEqual(openingEvents,[['render']]);assertRetained()});
 opening.document.querySelector=()=>null;openingEvents.length=0;documentScroll=700;opened('resetOpeningScroll()');
 check('document fallback resets when layout container is absent',()=>{assert.equal(documentScroll,0);assert.deepEqual(openingEvents,[['scroll',0,0]])});
 check('integer bounds and invalid syntax',()=>{for(const val of ['1.5','-1','1e3','NaN','10000000'])assert.equal(run('quantityValid('+JSON.stringify(val)+')'),false);for(const val of ['',null,'0','9999999'])assert.equal(run('quantityValid('+JSON.stringify(val)+')'),true)});
 check('invalid job marks field, focuses and names exact cell',()=>{const input=element('q');input.value='2.5';input.dataset={job:'0',key:'f20'};doc.querySelectorAll=()=>[input];run("report={jobs:[{name:'SYNTH JOB'}]};showEditTab=x=>{globalThis.tab=x};toast=x=>{globalThis.message=x};validateJobInputs(true)");assert.equal(input['aria-invalid'],'true');assert.equal(input.focused,true);assert.equal(box.tab,'jobs');assert.match(box.message,/SYNTH JOB.*F20/);doc.querySelectorAll=()=>[]});
 check('revision diff distinguishes missing and empty, escapes HTML',()=>{const html=run("reportDiffHTML({notes:'<script>'},{notes:'',newValue:''})");assert.match(html,/&lt;script&gt;/);assert.doesNotMatch(html,/<script>/);assert.match(html,/Không có trường/);assert.match(html,/chuỗi rỗng/)});
 check('signature deduplicates chiefs and escapes names',()=>{const html=run("signatureHTML({staffing:[{role:'PHỤ TRÁCH CHUNG',people:'A; B; A; <C>'}]})");assert.equal((html.match(/<strong>A<\/strong>/g)||[]).length,1);assert.match(html,/&lt;C&gt;/);assert.equal((html.match(/class="signature"/g)||[]).length,3)});
 check('machine print stamp exact shape',()=>assert.equal(run('printStamp(new Date(2026,10,8,7,3))'),'07:03 08/11/2026'));
 check('Escape cannot cancel active save or confirmation',()=>{run("var closed=0;closeModal=()=>closed++;saving=true;safeEscape();saving=false;localBusy=true;safeEscape();localBusy=false");assert.equal(run('closed'),0)});
 check('Escape routes PNI through its cancellation owner',()=>{run("var cancelled=0;personnelImport={confirming:false};personnelCancel=()=>cancelled++;safeEscape();personnelImport=null");assert.equal(run('cancelled'),1)});
 let resolvePreview,calls=[];box.apiMock=(path,body)=>{calls.push({path,body});if(path.endsWith('-preview'))return new Promise(r=>resolvePreview=r);return Promise.resolve({cancelled:true})};run("info={context:'ctx',capabilities:{maintenance:true}};api=(p,b)=>apiMock(p,b);modal=()=>{globalThis.opened=(globalThis.opened||0)+1};error=e=>{throw e};closeModal=()=>{};");
 const pending=run('previewUpgrade()');await run('cancelLocalOperation()');resolvePreview({nonce:'late',sourceSchema:'3',targetSchema:'4',migrationSteps:[]});await pending;
 check('cancelled late schema preview cannot revive plan',()=>{assert.equal(run('localPlan'),null);assert.equal(box.opened,undefined);assert.equal(calls.filter(c=>c.path==='/api/schema-upgrade-cancel').length,2);assert.deepEqual(JSON.parse(JSON.stringify(calls[1].body)),{context:'ctx'})});
 calls=[];const maintenance=run("openMaintenance('orphan_blobs')");await run('cancelLocalOperation()');resolvePreview({nonce:'late',items:[],count:0});await maintenance;
 check('maintenance late preview invalidated and cancelled',()=>{assert.equal(run('localPlan'),null);assert.equal(calls.filter(c=>c.path==='/api/maintenance-cancel').length,2)});
 check('readonly capability rejects maintenance before request',()=>{calls=[];run("info.readonly=true;openMaintenance('viewer_cleanup');info.readonly=false");assert.equal(calls.length,0)});
 calls=[];run("localPlan={kind:'schema_upgrade',context:'ctx',nonce:'n'};info.context='other'");await run('confirmLocalOperation()');check('stale context cannot confirm',()=>assert.equal(calls.length,0));
 run("info.context='ctx';localPlan={kind:'schema_upgrade',context:'ctx',nonce:'n'}");element('upgradeConsent').checked=false;await run('confirmLocalOperation()');check('schema upgrade requires explicit consent',()=>assert.equal(calls.length,0));
 run("report={id:'r',notes:'UNSAVED',jobs:[]};conflict=true;saving=false;uploading=false;collect=()=>{};renderEditor=()=>{};api=async()=>({id:'r',notes:'WINNER',version:9,actor:'WINNER ACTOR',jobs:[{name:'winner'}]})");await run('reloadConflict(true)');check('conflict preserves winner and explicitly pending local notes',()=>{assert.equal(run('report.version'),9);assert.equal(run('report.actor'),'WINNER ACTOR');assert.equal(run('report.jobs[0].name'),'winner');assert.equal(run('report.notes'),'UNSAVED');assert.equal(run('dirty'),true);assert.equal(run('conflict'),false);assert.match(element('saveState').textContent,/chưa được lưu/)});
 check('revision comparison uses actual adjacent items despite version gaps',()=>{run("window.revisions=[{version:10,payload:{notes:'new'}},{version:4,payload:{notes:'old'}}];modal=html=>{globalThis.diffDialog=html};revisionPreview(0)");assert.match(box.diffDialog,/10 so với 4/);assert.match(box.diffDialog,/<del>old<\/del>/);assert.match(box.diffDialog,/<ins>new<\/ins>/)});
 check('keyboard shortcut selects matching tab and focuses it',()=>{run("page='edit';showEditTab=x=>{globalThis.selectedTab=x}");let prevented=false;events.keydown({key:'2',altKey:true,preventDefault(){prevented=true}});assert.equal(box.selectedTab,'jobs');assert.equal(element('tab_jobs').focused,true);assert.equal(prevented,true)});
 calls=[];box.apiMock=async(path,body)=>{calls.push({path,body});return path==='/api/restore-preview'?{reports:0,revisions:0,nonce:'restore-nonce'}:{cancelled:true}};
 run("info={context:'restore-ctx',migrationRequired:true};protectionData={backups:[{id:'opaque-id',name:'known-copy.db'}]};api=(p,b)=>apiMock(p,b);modal=html=>{globalThis.recoveryDialog=html};go=async()=>{};toast=()=>{}");
 await run("previewRecovery('opaque-id')");check('recovery preview shows empty data and stores only server nonce',()=>{assert.match(box.recoveryDialog,/Chưa có báo cáo nào/);assert.equal(run('localPlan.nonce'),'restore-nonce');assert.equal(run('localPlan.kind'),'recovery')});
 element('confirmRecovery').value='wrong';await run('confirmLocalOperation()');check('recovery requires exact destructive consent',()=>assert.equal(calls.filter(c=>c.path==='/api/restore').length,0));
 await run('cancelLocalOperation()');check('recovery cancel clears local and server plan',()=>{assert.equal(run('localPlan'),null);assert.deepEqual(JSON.parse(JSON.stringify(calls.at(-1))),{path:'/api/restore-cancel',body:{context:'restore-ctx'}})});
 await run("previewRecovery('opaque-id')");element('confirmRecovery').value='KHOI PHUC';await run('confirmLocalOperation()');check('recovery confirm sends context nonce consent only',()=>assert.deepEqual(JSON.parse(JSON.stringify(calls.find(c=>c.path==='/api/restore').body)),{context:'restore-ctx',nonce:'restore-nonce',confirmation:'KHOI PHUC'}));
 run("info={context:'ctx',capabilities:{maintenance:true}};leave=()=>true;modal=html=>{globalThis.protectionHTML=html};api=async()=>({backups:[],external_directory:'',restore_drill_due:true,last_restore_drill:null})");
 await run('openProtection()');check('quarterly restore reminder renders due state and action',()=>{assert.match(box.protectionHTML,/Chưa thực hiện/);assert.match(box.protectionHTML,/Đã đến hạn kiểm tra khôi phục định kỳ 90 ngày/);assert.match(box.protectionHTML,/openMaintenance.*restore_drill/)});
 run("api=async()=>({backups:[],external_directory:'',restore_drill_due:false,last_restore_drill:'2026-11-08T12:00:00+07:00'})");
 await run('openProtection()');check('recent successful drill shows date without overdue warning',()=>{assert.match(box.protectionHTML,/Chưa đến hạn kiểm tra định kỳ 90 ngày/);assert.doesNotMatch(box.protectionHTML,/Đã đến hạn kiểm tra khôi phục/);assert.doesNotMatch(box.protectionHTML,/Khôi phục thử gần nhất: Chưa thực hiện/)});
 // Unit fixtures exercise the event contract; only subsequent headed proof asserts real trusted keys.
 const originalPreview={getClientRects(){return [{}]}};element('modalBody').querySelector=()=>originalPreview;element('modal').classList.contains=()=>false;
 let prints=0;box.window.print=()=>{prints++};let resolveImage;doc.querySelectorAll=selector=>selector==='#modal img'?[{decode:()=>new Promise(resolve=>{resolveImage=resolve})}]:[];
 const firstPrint=run('printReport()');assert.equal(run('printBusy'),true);assert.equal(await run('printReport()'),false);resolveImage();await firstPrint;
 check('deferred image decode owns print once and blocks reentry',()=>{assert.equal(prints,1);assert.equal(run('printBusy'),false)});
 for(const mode of ['closed','replaced']){
  element('modalBody').querySelector=()=>originalPreview;element('modal').classList.contains=()=>false;
  const deferred=run('printReport()');
  if(mode==='closed')element('modal').classList.contains=()=>true;else element('modalBody').querySelector=()=>({getClientRects(){return [{}]}});
  resolveImage();assert.equal(await deferred,false);assert.equal(prints,1);assert.equal(run('printBusy'),false);
 }
 check('closed or replaced preview during image decode aborts print safely',()=>assert.equal(prints,1));
 element('modalBody').querySelector=()=>originalPreview;element('modal').classList.contains=()=>false;
 doc.querySelectorAll=()=>[];box.window.print=()=>{throw new Error('printer rejected')};await assert.rejects(run('printReport()'),/printer rejected/);box.window.print=()=>{prints++};await run('printReport()');
 check('print error releases owner for next deliberate print',()=>{assert.equal(prints,2);assert.equal(run('printBusy'),false)});
 const visiblePreview={getClientRects(){return [{}]}};element('modalBody').querySelector=()=>visiblePreview;element('modal').classList.contains=()=>false;
 run('saving=false;uploading=false;localBusy=false;localPending=null;localPlan=null;printBusy=false');
 const key=(overrides={})=>({key:'p',isTrusted:true,ctrlKey:true,metaKey:false,altKey:false,shiftKey:false,repeat:false,prevented:false,preventDefault(){this.prevented=true},...overrides});
 const accepted=key();box.shortcutEvent=accepted;assert.equal(run('previewPrintShortcut(shortcutEvent)'),true);await new Promise(resolve=>setImmediate(resolve));
 check('visible trusted preview CtrlP invokes existing print owner',()=>{assert.equal(accepted.prevented,true);assert.equal(prints,3)});
 for(const override of [{isTrusted:false},{repeat:true},{ctrlKey:false},{metaKey:true},{altKey:true},{shiftKey:true},{key:'s'}]){const event=key(override);box.shortcutEvent=event;assert.equal(run('previewPrintShortcut(shortcutEvent)'),false);assert.equal(event.prevented,false)}
 check('synthetic repeat and other modifiers preserve browser default',()=>assert.equal(prints,3));
 for(const [name,value] of [['saving','true'],['uploading','true'],['localBusy','true'],['localPending','{}'],['localPlan','{}'],['printBusy','true']]){run(name+'='+value);const event=key();box.shortcutEvent=event;assert.equal(run('previewPrintShortcut(shortcutEvent)'),false);assert.equal(event.prevented,false);run(name+'='+(['localPending','localPlan'].includes(name)?'null':'false'))}
 check('save upload pending confirmation and print busy reject shortcut',()=>assert.equal(prints,3));
 for(const mode of ['closed','nonpreview','hidden']){element('modal').classList.contains=()=>mode==='closed';element('modalBody').querySelector=()=>mode==='nonpreview'?null:{getClientRects(){return mode==='hidden'?[]:[{}]}};const event=key();box.shortcutEvent=event;assert.equal(run('previewPrintShortcut(shortcutEvent)'),false);assert.equal(event.prevented,false)}
 check('hidden stale and unrelated dialogs never intercept CtrlP',()=>assert.equal(prints,3));
 element('keyboardPrint').remove=()=>{};run('printBusy=true');events.afterprint();
 check('afterprint lifecycle releases print guard',()=>assert.equal(run('printBusy'),false));
 console.log(passed+' local UI behavioral checks passed.');
})().catch(e=>{console.error(e);process.exitCode=1});
