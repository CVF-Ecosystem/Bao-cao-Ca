'use strict';
// Local desktop features share existing server/context and modal ownership.
let localPlan=null,localPending=null,localGeneration=0,localBusy=false;
function invalidateLocalDialog(){localGeneration++;localPlan=null;localPending=null}
function diffValue(value,present=true){
 if(!present)return 'Không có trường';
 if(value==='')return '(chuỗi rỗng)';
 if(value===null)return 'null';
 return typeof value==='object'?JSON.stringify(value):String(value);
}
function reportDifferences(before,after,path='',beforePresent=true,afterPresent=true){
 if(beforePresent===afterPresent&&JSON.stringify(before)===JSON.stringify(after))return [];
 if(beforePresent&&afterPresent&&before!==null&&after!==null&&typeof before==='object'&&typeof after==='object'&&Array.isArray(before)===Array.isArray(after)){
  const names=[...new Set([...Object.keys(before),...Object.keys(after)])].sort((a,b)=>/^\d+$/.test(a)&&/^\d+$/.test(b)?Number(a)-Number(b):a.localeCompare(b));
  return names.flatMap(name=>reportDifferences(before[name],after[name],path+(Array.isArray(before)?'['+name+']':(path?'.':'')+name),Object.hasOwn(before,name),Object.hasOwn(after,name)));
 }
 return [{path:path||'Báo cáo',before:diffValue(before,beforePresent),after:diffValue(after,afterPresent)}];
}
function reportDiffHTML(before,after){
 const rows=reportDifferences(before,after);
 return '<section class="revisionDiff"><p>'+rows.length+' khác biệt giữa hai bản liền nhau.</p><div class="scroll"><table><thead><tr><th>Trường</th><th>Trước</th><th>Sau</th></tr></thead><tbody>'+rows.slice(0,500).map(r=>'<tr><th>'+esc(r.path)+'</th><td><del>'+esc(r.before)+'</del></td><td><ins>'+esc(r.after)+'</ins></td></tr>').join('')+'</tbody></table></div>'+(!rows.length?'<p>Không có thay đổi nội dung.</p>':'')+(rows.length>500?'<p>Hiển thị 500 khác biệt đầu trên '+rows.length+'.</p>':'')+'</section>';
}
function signatureHTML(r){
 const names=[...new Set((r.staffing||[]).filter(s=>s.role.trim().toUpperCase()==='PHỤ TRÁCH CHUNG').flatMap(s=>s.people.split(/\s*;\s*/)).map(s=>s.trim()).filter(Boolean))];
 return '<section class="signatureBlock"><h3>Trưởng ca (Phụ trách chung)</h3><div class="signatures">'+(names.length?names:['']).map(name=>'<div class="signature"><p>Ký và ghi rõ họ tên</p><div class="signatureSpace"></div><strong>'+esc(name)+'</strong></div>').join('')+'</div></section>';
}
function printStamp(now=new Date()){
 const pad=n=>String(n).padStart(2,'0');
 return pad(now.getHours())+':'+pad(now.getMinutes())+' '+pad(now.getDate())+'/'+pad(now.getMonth()+1)+'/'+now.getFullYear();
}
function updatePrintIdentity(){
 let node=document.querySelector('.preview[data-print-ca]');
 if(!node&&typeof report!=='undefined'&&report){const block=document.createElement('div');block.id='keyboardPrint';block.innerHTML=preview(report);document.body.appendChild(block);document.body.classList.add('printingReport');node=block.querySelector('.preview')}
 const quote=s=>'"'+String(s).replace(/["\\\n\r]/g,' ')+'"';
 document.documentElement.style.setProperty('--print-ca',quote(node?.dataset.printCa||''));
 document.documentElement.style.setProperty('--print-time',quote('In lúc '+printStamp()));
}
window.addEventListener('beforeprint',updatePrintIdentity);
window.addEventListener('afterprint',()=>{printBusy=false;$('keyboardPrint')?.remove();document.body.classList.remove('printingReport')});
function decorateLocalModal(){
 const body=$('modalBody'),root=$('personnelRoot')||body;
 const heading=root.querySelector?.('h2');
 if(heading)(heading.closest('.row')||heading).classList.add('modalHead');
 const rows=[...(root.children||[])].filter(n=>n.classList?.contains('row')&&n.querySelector('button'));
 if(rows.length)rows[rows.length-1].classList.add('modalActions');
}
function safeEscape(){
 if(saving||uploading||localBusy||typeof personnelImport!=='undefined'&&personnelImport?.confirming)return;
 if(typeof personnelImport!=='undefined'&&personnelImport){personnelCancel();return}
 if(localPlan||localPending){cancelLocalOperation();return}
 localGeneration++;closeModal();
}
function previewPrintShortcut(event){
 if(event.isTrusted!==true||!event.ctrlKey||event.metaKey||event.altKey||event.shiftKey||event.repeat||String(event.key).toLowerCase()!=='p')return false;
 if(saving||uploading||localBusy||localPending||localPlan||printBusy)return false;
 const dialog=$('modal'),node=$('modalBody').querySelector('.preview[data-print-ca]');
 if(!dialog||dialog.classList.contains('hide')||!node||!node.getClientRects().length)return false;
 event.preventDefault();
 printReport().catch(error);
 return true;
}
document.addEventListener('keydown',event=>{
 if(previewPrintShortcut(event))return;
 if(event.key==='Escape'&&(!$('modal').classList.contains('hide')||localPending)){event.preventDefault();safeEscape()}
 if(event.altKey&&/^[1-4]$/.test(event.key)&&page==='edit'){event.preventDefault();showEditTab(EDIT_TABS[Number(event.key)-1][0]);$('tab_'+EDIT_TABS[Number(event.key)-1][0])?.focus()}
 if((event.key==='Enter'||event.key===' ')&&document.activeElement===$('toast'))$('toast').classList.add('hide');
});
async function renderMigration(){
 clearTimeout(timer);report=null;dirty=false;setPage('home');
 document.querySelectorAll('nav button:not(.navexit)').forEach(b=>b.disabled=true);
 $('home').innerHTML='<section class="card"><h2>Nâng cấp dữ liệu trên máy này</h2><p>Dữ liệu hiện tại cần nâng cấp từ schema '+esc(info.schemaVersion)+' lên 4. Chưa thay đổi DB; chỉ tiếp tục khi đã xem đường nâng cấp và bản sao phục hồi.</p><p>Mọi máy dùng cùng dữ liệu phải nâng lên phiên bản mới. Bản 1.9.x không mở được schema 4.</p><div class="row"><button class="primary" onclick="previewUpgrade()">Xem kế hoạch nâng cấp</button><button onclick="openRecovery()">Phục hồi từ bản sao đã giữ</button></div></section>';
}
async function previewUpgrade(){
 const context=info.context,generation=++localGeneration;
 localPending={kind:'schema_upgrade',context};
 try{
  const d=await api('/api/schema-upgrade-preview',{context});
  if(context!==info.context||generation!==localGeneration){if(!localPlan&&!localPending)await cancelLocalPlan({kind:'schema_upgrade',context});return}
  localPending=null;
  modal('<h2>Xác nhận nâng cấp dữ liệu</h2><p>Schema '+esc(d.sourceSchema)+' → '+esc(d.targetSchema)+'</p><ul>'+d.migrationSteps.map(s=>'<li>'+esc(s.fromSchema)+' → '+esc(s.toSchema)+' · bản sao '+esc(s.backupName)+'</li>').join('')+'</ul><p>Bản sao được kiểm tra đầy đủ trước khi nâng. Dữ liệu lịch sử cũ được giữ nguyên; bản cũ không mở được DB đã nâng.</p><label class="row"><input id="upgradeConsent" type="checkbox"> Đã xem kế hoạch và đồng ý nâng cấp DB này.</label><div class="row"><button onclick="cancelLocalOperation()">Hủy</button><button class="primary" onclick="confirmLocalOperation()">Nâng cấp dữ liệu</button></div>');
  localPlan={kind:'schema_upgrade',nonce:d.nonce,context,generation:localGeneration};
 }catch(e){if(generation===localGeneration){localPending=null;error(e)}}
}
async function openMaintenance(kind){
 if(!info.capabilities?.maintenance||info.review||info.readonly)return toast('Chức năng chỉ có trên DB chính cho phép ghi.',true);
 const context=info.context,generation=++localGeneration;
 localPending={kind,context};
 try{
  const d=await api('/api/maintenance-preview',{context,kind});
  if(context!==info.context||generation!==localGeneration){if(!localPlan&&!localPending)await cancelLocalPlan({kind,context});return}
  localPending=null;
  modal('<h2>'+esc(({viewer_cleanup:'Dọn bản chỉ xem cũ',orphan_blobs:'Dọn tệp không còn tham chiếu',restore_drill:'Khôi phục thử vào thư mục riêng'})[kind])+'</h2><p>'+d.count+' mục có thể thực hiện. Những mục không đủ điều kiện được giữ nguyên.</p><div class="scroll"><table><thead><tr><th>Mục</th><th>Trạng thái</th><th>Lý do</th></tr></thead><tbody>'+d.items.map(i=>'<tr><td>'+esc(i.label)+'</td><td>'+(i.eligible?'Có thể thực hiện':'Giữ lại')+'</td><td>'+esc(i.reason)+'</td></tr>').join('')+'</tbody></table></div><p class="note">Trước khi xóa, hệ thống tạo bản sao mới, kiểm tra đầy đủ và kiểm tra lại nguồn. Dọn blob chỉ giải phóng chỗ trong DB; không tự thu nhỏ file.</p><div class="row"><button onclick="cancelLocalOperation()">Hủy</button><button class="primary" onclick="confirmLocalOperation()">'+(kind==='restore_drill'?'Chạy khôi phục thử':'Xác nhận thực hiện')+'</button></div>',true);
  localPlan={kind,nonce:d.nonce,context,generation:localGeneration};
 }catch(e){if(generation===localGeneration){localPending=null;error(e)}}
}
async function cancelLocalPlan(plan){
 return api(plan.kind==='schema_upgrade'?'/api/schema-upgrade-cancel':plan.kind==='recovery'?'/api/restore-cancel':'/api/maintenance-cancel',{context:plan.context,...(['schema_upgrade','recovery'].includes(plan.kind)?{}:{kind:plan.kind})});
}
async function cancelLocalOperation(){
 if(localBusy)return;
 const plan=localPlan||localPending;localPlan=null;localPending=null;localGeneration++;closeModal();
 if(plan)try{await cancelLocalPlan(plan)}catch(e){error(e)}
}
async function confirmLocalOperation(){
 const plan=localPlan;
 if(!plan||localBusy||plan.context!==info.context)return;
 if(plan.kind==='schema_upgrade'&&!$('upgradeConsent')?.checked)return toast('Đánh dấu đồng ý sau khi xem kế hoạch.',true);
 if(plan.kind==='recovery'&&$('confirmRecovery')?.value!=='KHOI PHUC')return toast('Nhập đúng KHOI PHUC để xác nhận phục hồi.',true);
 localBusy=true;
 document.querySelectorAll('#modalBody button,#modalBody input').forEach(b=>b.disabled=true);
 try{
  const result=await api(plan.kind==='schema_upgrade'?'/api/schema-upgrade-confirm':plan.kind==='recovery'?'/api/restore':'/api/maintenance-confirm',{context:plan.context,nonce:plan.nonce,...(plan.kind==='recovery'?{confirmation:$('confirmRecovery').value}:{})});
  localPlan=null;localGeneration++;closeModal();
  document.querySelectorAll('nav button').forEach(b=>b.disabled=false);
  await go('home');toast(result.message||(plan.kind==='recovery'?'Đã phục hồi; DB trước phục hồi được giữ riêng. Nếu còn schema cũ, cần xác nhận nâng cấp riêng.':'Đã nâng cấp dữ liệu; bản sao trước nâng cấp được giữ lại.'));
 }catch(e){localPlan=null;localGeneration++;closeModal();if(e.code==='RECOVERY_REQUIRED'){try{await refreshInfo();if(info.migrationRequired)await renderMigration()}catch(refreshError){error(refreshError)}}error(e)}
 finally{localBusy=false}
}

async function openRecovery(){
 if(localBusy||!info.migrationRequired)return;
 const context=info.context,generation=++localGeneration;localPlan=null;localPending=null;
 try{
  const d=await api('/api/protection');
  if(context!==info.context||generation!==localGeneration)return;
  protectionData=d;
  modal('<h2>Phục hồi từ bản sao đã giữ</h2><p class="note warn">Chỉ chọn bản sao được chương trình xác nhận thuộc dữ liệu này. Phục hồi thay DB hiện tại, giữ DB trước phục hồi riêng. Nâng cấp schema là thao tác xác nhận riêng sau đó.</p><div class="scroll"><table><thead><tr><th>Bản sao</th><th>Thời gian</th><th></th></tr></thead><tbody>'+d.backups.map(b=>'<tr><td>'+esc(b.name)+'</td><td>'+esc(timeLabel(b.modified))+'</td><td><button data-id="'+esc(b.id)+'" onclick="previewRecovery(this.dataset.id)">Kiểm tra / phục hồi</button></td></tr>').join('')+'</tbody></table></div>'+(!d.backups.length?'<p>Chưa có bản sao phục hồi hợp lệ. Giữ nguyên dữ liệu và nhật ký; không tạo DB trắng để thay thế.</p>':'')+'<div class="row"><button onclick="safeEscape()">Đóng</button></div>',true);
 }catch(e){if(generation===localGeneration)error(e)}
}
async function previewRecovery(id){
 if(localBusy||!info.migrationRequired)return;
 const context=info.context,generation=++localGeneration;localPending={kind:'recovery',context};
 try{
  const d=await api('/api/restore-preview',{context,id});
  if(context!==info.context||generation!==localGeneration){if(!localPlan&&!localPending)await cancelLocalPlan({kind:'recovery',context});return}
  localPending=null;
  const selected=protectionData.backups.find(b=>b.id===id);
  modal('<h2>Xác nhận phục hồi bản sao đã kiểm tra</h2><p><strong>'+esc(selected?.name||'Bản sao đã chọn')+'</strong></p><p>'+esc(d.reports)+' ca · '+esc(d.revisions)+' bản lịch sử<br>'+(d.reports?'Từ '+esc(dateLabel(d.first_day))+' đến '+esc(dateLabel(d.last_day)):'Chưa có báo cáo nào')+'</p><p class="note warn">DB hiện tại được giữ riêng trước khi thay. Mọi thay đổi sau bản sao sẽ không nằm trong dữ liệu phục hồi. Không tự nâng cấp sau phục hồi.</p><label>Nhập KHOI PHUC để đồng ý thay DB<input id="confirmRecovery" autocomplete="off"></label><div class="row"><button onclick="cancelLocalOperation()">Hủy</button><button class="primary" onclick="confirmLocalOperation()">Phục hồi bản sao này</button></div>');
  localPlan={kind:'recovery',context,nonce:d.nonce,generation:localGeneration};
 }catch(e){if(generation===localGeneration){localPending=null;error(e)}}
}
