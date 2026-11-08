
'use strict';
history.replaceState(null,'','/');
const $=id=>document.getElementById(id), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const keys=['f20','f40','e20','e40'];
let uploading=false,printBusy=false;
let info,report=null,page='home',dirty=false,saving=false,conflict=false,timer=null,toastTimer=null,listRows=[];
function dateLabel(s){
  return s?.split('-').reverse().join('/')||''
}
function timeLabel(s){
  return s?new Date(s).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'}):''
}
function shiftName(s){
  return s==='DAY'?'Ca ngày':'Ca đêm'
}
function period(r){
  const end=new Date(r.date+'T12:00:00+07:00');
  end.setUTCDate(end.getUTCDate()+1);
  return r.shift==='DAY'?'06:00–18:00 ngày '+dateLabel(r.date):'18:00 ngày '+dateLabel(r.date)+' → 06:00 ngày '+dateLabel(end.toISOString().slice(0,10))
}
function badge(s){
  return '<span class="badge '+(s==='closed'?'':'draft')+'">'+(s==='closed'?'Đã chốt':'Nháp')+'</span>'
}
function toast(s,error=false){
  clearTimeout(toastTimer);
  $('toast').className='toast'+(error?' error':'');
  $('toast').textContent=s;
  toastTimer=setTimeout(()=>$('toast').classList.add('hide'),error?10000:4500)
}
async function api(path,body){
  const res=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Ca-Request':'1'},body:JSON.stringify(body)});
  const data=await res.json();
  if(!res.ok){
    const e=new Error(data.error||'Chưa hoàn tất thao tác.');
    e.status=res.status;
    e.code=data.code;e.backupName=data.backupName;
    throw e
  }
  return data
}
function error(e){
  toast((e.message||String(e))+(e.code==='RECOVERY_REQUIRED'?' · Cần phục hồi từ bản sao đã giữ'+(e.backupName?': '+e.backupName:'')+'. Dừng thay đổi dữ liệu.':''),true)
}
function modal(content,wide=false){
  if(typeof prepareLocalModal==='function')prepareLocalModal();
  if(typeof invalidateLocalDialog==='function')invalidateLocalDialog();
  $('modalBody').className='modal'+(wide?' wide':'');
  $('modalBody').innerHTML=content;
  $('modal').classList.remove('hide');
  if(typeof decorateLocalModal==='function')decorateLocalModal()
}
function closeModal(){
  $('modal').classList.add('hide');
  if(typeof finishLocalModal==='function')finishLocalModal();
  if(dirty&&report?.status==='draft'&&!info?.readonly&&!info?.review&&!saving&&!uploading){
    clearTimeout(timer);
    timer=setTimeout(()=>save(false),1600)
  }
}
function leave(){
  if(uploading){
    toast('Đang tải tệp, vui lòng đợi.');
    return false
  }
  if(saving){
    toast('Đang lưu, vui lòng đợi.');
    return false
  }
  if(dirty&&!confirm('Có nội dung chưa lưu. Rời màn hình sẽ bỏ phần chưa lưu này. Tiếp tục?'))return false;
  clearTimeout(timer);
  return true
}
async function refreshInfo(){
  info=await api('/api/info');
  if(info.migrationRequired){$('mode').textContent='CẦN NÂNG CẤP DỮ LIỆU';$('appVersion').textContent='Phiên bản '+info.version;return}
  $('mode').innerHTML=info.review?(info.readonly?'<span class="badge viewbadge">CHỈ XEM · DB KIỂM TRA</span>':'<span class="badge draft">ĐANG BỔ SUNG · BẢN SAO DB</span>'):'<span class="badge">MÁY NHẬP BÁO CÁO</span>';
  $('viewerNote').classList.toggle('hide',!info.review);
  $('viewerNote').innerHTML=info.readonly?'Đang xem bản sao DB. Muốn sửa báo cáo ngày cũ, bấm <button class="small" onclick="enableCorrections()">Bật chỉnh sửa / bổ sung</button> <button class="small" onclick="returnMain()">Về DB chính của máy</button>':'Đang chỉnh sửa trên <strong>bản sao DB</strong>. Lưu từng ca kèm lý do, sau đó <button class="small" onclick="backup()">Xuất DB đã bổ sung</button> để mang về máy chính nhập lại. <button class="small" onclick="returnMain()">Về DB chính của máy</button>';
  $('today').textContent='Báo cáo sản xuất cuối ca · '+dateLabel(info.now.slice(0,10));
  const hardWarning=[info.backup_level==='info'?'':info.backup_warning,info.catalog_warning].filter(Boolean).join(' ');
  $('backupWarning').textContent=hardWarning;
  $('backupWarning').classList.toggle('hide',!hardWarning);
  $('navAlert').classList.toggle('hide',!info.backup_warning);
  $('appVersion').textContent='Phiên bản '+info.version+' · '+(info.build?.commit||'nguon')
}
function setPage(name){
  page=name;
  for(const x of ['home','edit','list','summary'])$(x).classList.toggle('hide',x!==name);
  document.querySelectorAll('nav [data-page]').forEach(b=>b.classList.toggle('active',b.dataset.page===name));
  $('title').textContent=({home:'Tổng quan báo cáo',edit:'Báo cáo ca',list:'Tra cứu báo cáo',summary:'Tổng hợp số liệu'})[name]
}
async function go(name){
  if(!leave())return;
  dirty=false;
  setPage(name);
  try{
    await refreshInfo();
    if(info.migrationRequired){renderMigration();return}
    if(name==='home')await renderHome();
    if(name==='list'){
      renderFilters('filters','l');
      await loadList()
    }
    if(name==='summary'){
      renderFilters('summaryFilters','s');
      $('sstatus').value='closed';
      await loadSummary()
    }
  }catch(e){
    error(e)
  }
}
async function renderHome(){
  const ov=await api('/api/overview'),rows=ov.recent,s=info.suggestion,current=ov.current_status,tasks=rows[0]?.handover.filter(t=>!t.done)||[];
  $('home').innerHTML=`
<div class="grid"><div class="card metric"><span>CA ĐƯỢC GỢI Ý THEO GIỜ</span><strong style="font-size:24px">${shiftName(s.shift)}</strong><span>${dateLabel(s.date)} · ${current?(current==='closed'?'Đã chốt':'Đã có bản nháp'):'Chưa có báo cáo'}</span></div><div class="card metric"><span>BÁO CÁO THÁNG NÀY</span><strong>${ov.month_count}</strong><span>Số ca đã lưu, gồm cả nháp</span></div><div class="card metric"><span>BẢN NHÁP</span><strong>${ov.draft_count}</strong><span>Chưa chốt trong toàn bộ dữ liệu</span></div><div class="card metric"><span>BÀN GIAO CHƯA XỬ LÝ</span><strong>${tasks.length}</strong><span>Theo báo cáo gần nhất</span></div></div>
<div class="two"><div class="card"><div class="sectionno">BẮT ĐẦU LÀM VIỆC</div><h2>Nhập gọn. Lưu rõ. Tìm lại dễ.</h2><p class="muted">Chọn đúng ngày và ca trước khi nhập. Nhập trễ vẫn có thể chọn ca trước hoặc nhập bù.</p><div class="row"><button class="primary" onclick="newShift()" ${info.readonly||info.review?'disabled':''}>＋ Nhập ca mới</button><button onclick="go('list')">Xem báo cáo</button></div></div><div class="card"><div class="sectionno">BÀN GIAO TỪ BÁO CÁO GẦN NHẤT</div><h2>${rows[0]?dateLabel(rows[0].date)+' · '+shiftName(rows[0].shift):'Chưa có báo cáo'}</h2>${tasks.length?tasks.map(t=>'<p>□ '+esc(t.text)+'</p>').join(''):'<p class="muted">Không có việc chưa xử lý được ghi nhận.</p>'}<p class="muted subtle">Các việc được theo dõi theo từng bản báo cáo; không phải trạng thái thời gian thực.</p></div></div>
<div class="card"><div class="row between"><h2>Báo cáo gần đây</h2><button class="small" onclick="go('list')">Xem tất cả</button></div>${reportRows(rows.slice(0,6))}</div>
${info.backup_level==='info'&&info.backup_warning?'<div class="note warn"><strong>Khuyến nghị:</strong> '+esc(info.backup_warning)+' <button class="small" onclick="openProtection()">Chọn nơi dự phòng</button></div>':''}
<div class="note">DB đang mở: <strong>${esc(info.database)}</strong>. Số lượng trong báo cáo là <strong>lượt công việc</strong>, không phải số container duy nhất.</div>`
}
function chiefPeople(staffing){
  return [...new Set(staffing.filter(s=>s.role.trim().toUpperCase()==='PHỤ TRÁCH CHUNG').map(s=>s.people.trim()).filter(Boolean))].join('; ')
}
function reportRows(rows){
  return rows.length?'<div class="scroll"><table><thead><tr><th>Ngày / Ca</th><th>Phụ trách chung</th><th>Người lưu gần nhất</th><th>Trạng thái</th><th>Lưu lần cuối</th><th></th></tr></thead><tbody>'+rows.map(r=>`<tr><td><strong>${dateLabel(r.date)}</strong><br><span class="muted subtle">${shiftName(r.shift)}</span></td><td>${esc(chiefPeople(r.staffing)||'—')}</td><td>${esc(r.actor)}</td><td>${badge(r.status)}</td><td class="subtle">${timeLabel(r.updated_at)}</td><td><button class="small" data-id="${esc(r.id)}" onclick="loadReport(this.dataset.id)">Mở báo cáo</button></td></tr>`).join('')+'</tbody></table></div>':'<div class="empty">Chưa có báo cáo. Bấm “Nhập ca mới” để bắt đầu.</div>'
}
async function newShift(){
  if(info?.migrationRequired)return renderMigration();
  if(info.readonly||info.review){
    toast('Bản kiểm tra chỉ bổ sung ca đã có. Về DB chính để nhập ca mới.',true);
    return
  }
  if(!leave())return;
  await refreshInfo();
  const s=info.suggestion;
  modal(`<div class="sectionno">TẠO / MỞ BÁO CÁO</div><h2>Xác nhận ngày và ca</h2><p class="muted">Ca chỉ được gợi ý theo giờ. Có thể đổi để nhập trễ hoặc nhập bù.</p><div class="row"><label class="input">Ngày bắt đầu ca<input type="date" id="newDate" value="${s.date}" onchange="shiftHint()"></label><label class="input">Ca<select id="newShift" onchange="shiftHint()"><option value="DAY">Ca ngày</option><option value="NIGHT">Ca đêm</option></select></label></div><div class="note" id="shiftHint" style="margin-top:18px"></div><div class="row" style="justify-content:flex-end"><button onclick="closeModal()">Hủy</button><button class="primary" onclick="beginShift()">Vào ca này</button></div>`);
  $('newShift').value=s.shift;
  shiftHint()
}
function shiftHint(){
  const r={date:$('newDate').value,shift:$('newShift').value};
  $('shiftHint').textContent=r.date?period(r):'Chọn ngày báo cáo.'
}
function resetOpeningScroll(){
  document.querySelector('.layout')?.scrollTo(0,0);
  window.scrollTo(0,0)
}
async function beginShift(){
  const day=$('newDate').value,shift=$('newShift').value;
  if(!day)return toast('Chọn ngày báo cáo.',true);
  try{
    const rows=await api('/api/reports?from='+day+'&to='+day+'&shift='+shift);
    if(rows.length){
      closeModal();
      dirty=false;
      return loadReport(rows[0].id)
    }
    report={date:day,shift,version:0,status:'draft',actor:sessionStorage.getItem('ca_actor')||'',notes:'',staffing:info.roles.map(role=>({role,people:''})),jobs:info.jobs.map(name=>({name,detail:'',xn:false,rtg:false,f20:null,f40:null,e20:null,e40:null})),handover:[]};
    dirty=false;
    conflict=false;
    editTab='staff';
    closeModal();
    renderEditor();
    resetOpeningScroll()
  }catch(e){
    error(e)
  }
}
async function loadReport(id){
  if(!leave())return;
  try{
    report=await api('/api/report?id='+encodeURIComponent(id));
    if(info.review&&!info.readonly)report.actor=info.reviewer||report.actor;
    dirty=false;
    conflict=false;
    editTab='staff';
    renderEditor();
    resetOpeningScroll()
  }catch(e){
    error(e)
  }
}
// ---- Trang nhập ca: header, thanh tab, 4 khung nội dung và thanh lưu cố định ----
let editTab='staff';
const EDIT_TABS=[['staff','Nhân sự'],['jobs','Công việc'],['notes','Ghi chú & bàn giao'],['files','Ảnh & biên bản']];
function tabBadges(){
  const staff=report?.staffing||[],jobs=report?.jobs||[],tasks=report?.handover||[],files=report?.attachments||[];
  const hasChief=staff.some(s=>String(s.role||'').trim().toUpperCase()==='PHỤ TRÁCH CHUNG'&&String(s.people||'').trim());
  return {
    staff:hasChief?{text:String(staff.filter(s=>String(s.people||'').trim()).length)}:{text:'!',warn:true,title:'Chưa điền PHỤ TRÁCH CHUNG (bắt buộc để chốt ca)'},
    jobs:{text:String(jobs.filter(j=>keys.some(k=>Number(j[k])>0)).length)},
    notes:{text:String(tasks.filter(t=>!t.done).length),title:'Việc bàn giao chưa xử lý'},
    files:{text:String(files.length)}
  }
}
function tabBadgeHTML(id){
  const b=tabBadges()[id];
  return '<span class="tabBadge'+(b.warn?' warn':'')+'" id="tabBadge_'+id+'"'+(b.title?' title="'+esc(b.title)+'"':'')+'>'+b.text+'</span>'
}
function refreshTabBadges(){
  try{
    const all=tabBadges();
    for(const [id] of EDIT_TABS){
      const el=$('tabBadge_'+id);
      if(!el)continue;
      el.textContent=all[id].text;
      el.classList?.toggle('warn',!!all[id].warn)
    }
  }catch(e){}
}
function showEditTab(name){
  if(!EDIT_TABS.some(t=>t[0]===name))name='staff';
  editTab=name;
  for(const [id] of EDIT_TABS){
    $('panel_'+id)?.classList.toggle('hide',id!==name);
    const tab=$('tab_'+id);
    if(!tab)continue;
    tab.classList.toggle('active',id===name);
    tab.setAttribute('aria-selected',String(id===name))
  }
}
function editorHeader(dis){
  return `<div class="card editorCompact"><div class="row between"><div><div class="sectionno">${dateLabel(report.date)} · ${shiftName(report.shift).toUpperCase()}</div><h2 style="margin-bottom:4px">${period(report)}</h2><span>${badge(report.status)} <span class="muted subtle">Phiên bản ${report.version||'chưa lưu'}</span></span></div><div class="row noprint"><button onclick="showHistory()" ${report.version?'':'disabled'}>Lịch sử sửa</button><button onclick="showPreview()" ${report.version?'':'disabled'}>Xem / In</button><button onclick="exportReport()" ${report.version?'':'disabled'}>Xuất Excel</button></div></div><div style="max-width:380px;margin-top:16px"><label>Người đang nhập / chỉnh sửa<select id="actor" ${dis} onchange="touch()">${personOptions(report.actor)}</select></label></div></div>`
}
function editorNotice(){
  return (report.status==='closed'||info.review)&&!info.readonly?'<div class="note warn">Chỉnh sửa cần lưu thủ công kèm lý do. Nội dung cũ vẫn giữ trong lịch sử phiên bản.</div>':''
}
function editorTabs(){
  return '<div class="tabs noprint" role="tablist">'+EDIT_TABS.map(([id,label])=>
    `<button class="tab${id===editTab?' active':''}" id="tab_${id}" role="tab" aria-selected="${id===editTab}" onclick="showEditTab('${id}')">${label} ${tabBadgeHTML(id)}</button>`).join('')+'</div>'
}
function staffSection(dis){
  const hasKHB=report.staffing.some(x=>/^KHB\b/i.test(x.role));
  return `<div class="shipSummary"><strong>Tàu trong ca:</strong> <span id="reportShipNames">${esc(allReportShips(report).join('; '))||'Chưa chọn tàu'}</span></div>
<div class="row between"><div><div class="sectionno">NHÂN SỰ</div><h2>Phân công trong ca</h2></div><div class="row">${hasKHB?'':'<button class="small" onclick="addKHB()" '+dis+'>＋ Thêm KHB</button>'}<button class="small" onclick="addStaff()" ${dis}>＋ Thêm vị trí</button></div></div>
<div class="templateToolbar"><label>Điền mẫu phân công<select id="templateTeam" onchange="applyShiftTemplate(this.value)" ${dis}><option value="">— Chọn Ca 1 / Ca 2 / Ca 3 —</option>${(info.teams||[]).map(t=>`<option value="${esc(t.id)}">${esc(t.name)}</option>`).join('')}</select></label><button class="small" onclick="applyDayStaff()" ${dis}>＋ Thêm nhân sự ca ngày</button><label>Lọc người theo tổ<select id="staffTeam" onchange="setStaffTeam(this.value)">${staffTeamOptions(selectedStaffTeam())}</select></label><button class="small" onclick="manageStaffTemplates()">Cài mẫu phân công</button><span class="muted subtle">Mẫu chỉ điền sau khi xem trước và xác nhận. Lọc tổ chỉ thu hẹp danh sách khi bấm Chọn người, không tự đổi người đã lưu. Mỗi tàu một dòng TALLY TÀU / XUẤT TÀU.</span></div>
<div id="staffRows"></div>`
}
function jobsSection(dis){
  return `<div class="row between"><div><div class="sectionno">CÔNG VIỆC THỰC TẾ</div><h2>Số lượt theo từng loại container</h2></div><div class="row"><button class="small" onclick="updateJobsTemplate()" ${dis}>Cập nhật mẫu dời dọn</button><button class="small" onclick="addJob()" ${dis}>＋ Thêm công việc</button></div></div>
<div class="scroll"><table class="worktable"><thead><tr><th>Công việc</th><th>Chi tiết / Tàu / Vị trí</th><th>XN</th><th>RTG</th><th>F20</th><th>F40</th><th>E20</th><th>E40</th><th></th></tr></thead><tbody id="jobRows"></tbody><tfoot id="jobTotal"></tfoot></table></div>
<p class="muted subtle" style="margin-top:12px">XN / RTG giữ theo cột đánh dấu trong mẫu gốc. Tổng là lượt công việc, có thể có cùng cont qua nhiều công việc.</p>`
}
function notesSection(dis){
  return `<div class="row between"><div><div class="sectionno">GHI CHÚ VÀ BÀN GIAO</div><h2>Để ca sau tiếp tục công việc</h2></div><button class="small" onclick="carry()" ${dis}>Lấy việc chưa xong từ ca trước</button></div>
<label>Ghi chú chung<textarea id="notes" oninput="touch()" ${dis}>${esc(report.notes)}</textarea></label><div id="taskRows"></div><button class="small" onclick="addTask()" ${dis}>＋ Thêm việc bàn giao</button>`
}
function filesSection(dis){
  return `<div class="row between"><div><div class="sectionno">ẢNH VÀ BIÊN BẢN</div><h2>Tệp đính kèm của ca ${dateLabel(report.date)} · ${shiftName(report.shift)}</h2></div><div class="row"><button class="small" onclick="exportAttachments()" ${report.version?'':'disabled'}>Tải tất cả tệp</button><button class="primary small" onclick="chooseAttachments()">＋ Thêm tệp</button></div></div>
<p class="muted subtle">Tối đa 40 tệp/ca, 100 MB/tệp; nhận mọi loại tệp. Thêm tệp là lưu ngay, không cần bật chỉnh sửa hay nhập lý do.</p>
<details class="fileOptions"><summary>Tùy chọn thu nhỏ ảnh</summary><label class="row" style="margin:10px 0;font-weight:500"><input type="checkbox" id="optimizePhotos" ${dis}>Thu nhỏ ảnh trước khi lưu (cạnh dài tối đa 2.560 px; tệp khác giữ nguyên)</label><p class="muted subtle">Mặc định giữ nguyên tệp gốc. Bật thu nhỏ sẽ lưu bản ảnh đã tối ưu, có thể giảm chi tiết và bỏ thông tin máy ảnh; ảnh/biên bản cần giữ làm bằng chứng nên để nguyên.</p></details>
<input class="hide" type="file" multiple id="attachmentFiles" onchange="uploadAttachments(this)"><p id="uploadState" class="muted subtle"></p><div class="attachmentGrid" id="attachmentRows"></div>`
}
function editorToolbar(dis){
  return `<div class="toolbar"><div id="saveState" class="muted subtle">${report.updated_at?'Đã lưu lúc '+timeLabel(report.updated_at):'Chưa lưu · điền người nhập để bật tự lưu'}</div><div class="row"><button onclick="manualSave()" ${dis}>${info.review?'Lưu bổ sung':report.status==='closed'?'Lưu chỉnh sửa':'Lưu nháp'}</button>${report.status!=='closed'&&!info.review?'<button class="primary" onclick="closeShift()" '+dis+'>Chốt ca</button>':''}</div></div>`
}
function renderEditor(){
  $('edit').inert=false;
  report.attachments=report.attachments||[];
  setPage('edit');
  if(!EDIT_TABS.some(t=>t[0]===editTab))editTab='staff';
  const dis=info.readonly?'disabled':'';
  const panel=(id,body)=>`<section class="tabPanel card${id===editTab?'':' hide'}" id="panel_${id}" role="tabpanel">${body}</section>`;
  $('edit').innerHTML=editorHeader(dis)+editorNotice()+editorTabs()
    +panel('staff',staffSection(dis))+panel('jobs',jobsSection(dis))+panel('notes',notesSection(dis))+panel('files',filesSection(dis))
    +editorToolbar(dis);
  renderStaff();
  renderJobs();
  renderTasks();
  renderAttachments()
}
function canChooseStaffShip(role){
  const name=String(role||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/\s+/g,' ').trim();
  return /^(TALLY TAU|XUAT TAU)(?:\s|:|$)/.test(name)
}
function staffShipControl(s,i,dis=''){
 if(!canChooseStaffShip(s.role))return (s.ships||[]).length?'<div class="muted subtle">Tàu đã lưu: '+esc(s.ships.join('; '))+'</div>':'';
 const legacy=(s.ships||[]).length>1;
 return `<div class="shipAssignment"><strong>${esc((s.ships||[]).join('; '))||'Chưa chọn tàu'}</strong>
 <div class="row" style="margin-top:8px"><button class="small" onclick="chooseShips('staff',${i})" ${dis}>Chọn 1 tàu</button>
 <button class="small" onclick="addShipStaff(${i})" ${dis}>＋ Tàu / người khác</button></div>
 ${legacy?'<p class="note warn">Phân công cũ đang dùng chung cho nhiều tàu. Chọn lại 1 tàu, chỉnh người của tàu đó rồi thêm dòng cho từng tàu còn lại. Chưa chọn lại thì dữ liệu cũ vẫn được giữ.</p>':''}</div>`;
}
function addShipStaff(index){
 if(info.readonly||saving||uploading)return;
 collect();
  const source=report.staffing[index];
 if(!source||!canChooseStaffShip(source.role))return;
 if(report.staffing.length>=200)return toast('Tối đa 200 dòng nhân sự.',true);
 report.staffing.splice(index+1,0,{role:source.role,people:'',ships:[]});
 renderStaff();
  touch();
  chooseShips('staff',index+1);
}
function staffTeamOptions(current=''){
 return '<option value="">Tất cả nhân viên</option>'+(info.teams||[]).map(t=>'<option value="'+esc(t.id)+'" '+(t.id===current?'selected':'')+'>'+esc(t.name)+' ('+t.people.length+' người)</option>').join('');
}
function selectedStaffTeam(){
 const id=sessionStorage.getItem('ca_staff_team')||'';
 return (info.teams||[]).some(t=>t.id===id)?id:'';
}
function setStaffTeam(id){
 sessionStorage.setItem('ca_staff_team',id);
 const select=$('staffTeam');
  if(select)select.value=id;
}

function staffRoleInput(i,value){
  report.staffing[i].role=value;
  touch();
  const box=$('staffShipChoice'+i);
  if(box)box.innerHTML=staffShipControl(report.staffing[i],i,info.readonly?'disabled':'')
}
function staffGroupRoleInput(indices,value){
 for(const i of indices){
  report.staffing[i].role=value;
  const input=document.querySelector('[data-staff-role="'+i+'"]');
    if(input)input.value=value;

  }
 touch();
}
function vesselStaffRow(s,i,dis){
 const legacy=(s.ships||[]).length>1;
 return `<div class="vesselStaffRow">
 <input type="hidden" data-staff-role="${i}" value="${esc(s.role)}">
 <button class="vesselChoice" title="Chọn 1 tàu cho dòng này" onclick="chooseShips('staff',${i})" ${dis}>${esc((s.ships||[]).join('; '))||'Chọn tàu…'}</button>
 <input aria-label="Người thực hiện ${esc(s.role)} ${esc((s.ships||[]).join('; '))}" data-staff-people="${i}" value="${esc(s.people)}" title="${esc(s.people)}" placeholder="Chọn người làm tàu này" oninput="touch()" ${dis}>
 <button class="small" onclick="openStaffPicker(${i})" ${dis}>Chọn người</button>
 <button class="small danger" title="Xóa dòng phân công tàu này" onclick="removeStaff(${i})" ${dis}>×</button>
 ${legacy?'<p class="legacyStaffNote">Phân công cũ đang chung nhiều tàu. Chọn lại 1 tàu và thêm dòng cho tàu còn lại; chưa sửa thì giữ nguyên.</p>':''}
 </div>`;
}
function renderStaff(){
 const dis=info.readonly?'disabled':'',done=new Set(),blocks=[];
 report.staffing.forEach((s,i)=>{
  if(done.has(i))return;
  if(canChooseStaffShip(s.role)){
   const group=report.staffing.map((row,index)=>({row,index})).filter(x=>x.row.role.trim().toUpperCase()===s.role.trim().toUpperCase());
   for(const item of group)done.add(item.index);
   const indices=group.map(x=>x.index),last=indices[indices.length-1];
   blocks.push(`<div class="vesselStaffGroup"><div class="row between vesselGroupHeader">
   <input aria-label="Vị trí phân công tàu" value="${esc(s.role)}" oninput="staffGroupRoleInput([${indices.join(',')}],this.value)" onchange="renderStaff()" ${dis}>
   <button class="small" onclick="addShipStaff(${last})" ${dis}>＋ Thêm tàu</button></div>
   <div class="vesselColumnLabels"><span>Tàu</span><span>Người thực hiện</span></div>
   ${group.map(x=>vesselStaffRow(x.row,x.index,dis)).join('')}</div>`);

    }else{
   done.add(i);
   blocks.push(`<div class="standardStaffCard"><div class="row" style="flex-wrap:nowrap">
   <input aria-label="Vị trí" value="${esc(s.role)}" style="font-size:12px;background:#f4f7f6" data-staff-role="${i}" oninput="staffRoleInput(${i},this.value)" ${dis}>
   <button class="small danger" title="Xóa vị trí" onclick="removeStaff(${i})" ${dis}>×</button></div>
   <div class="row" style="margin-top:8px;flex-wrap:nowrap"><input aria-label="Nhân sự ${esc(s.role)}" oninput="touch()" title="${esc(s.people)}" value="${esc(s.people)}" placeholder="Bấm Chọn người" data-staff-people="${i}" ${dis}>
   <button class="small" style="white-space:nowrap" onclick="openStaffPicker(${i})" ${dis}>Chọn người</button></div>
   <div id="staffShipChoice${i}">${staffShipControl(s,i,dis)}</div></div>`);

    }

  });
 $('staffRows').innerHTML='<div class="staffCards">'+blocks.join('')+'</div>';
}

function renderJobs(){
  const dis=info.readonly?'disabled':'';
  $('jobRows').innerHTML=report.jobs.map((j,i)=>`<tr><td><input aria-label="Tên công việc" data-job="${i}" data-key="name" value="${esc(j.name)}" oninput="touch()" ${dis}></td><td><input aria-label="Chi tiết công việc" data-job="${i}" data-key="detail" value="${esc(j.detail)}" placeholder="Vị trí, lý do…" oninput="touch()" ${dis}>${(j.ships||[]).length?'<div class="muted subtle" style="margin-top:6px">Tàu đã lưu: '+esc(j.ships.join('; '))+'</div>':''}</td>${['xn','rtg'].map(k=>`<td><input type="checkbox" aria-label="${k.toUpperCase()}" data-job="${i}" data-key="${k}" ${j[k]?'checked':''} onchange="touch()" ${dis}></td>`).join('')}${keys.map(k=>`<td><input type="number" min="0" max="9999999" step="1" aria-label="${k.toUpperCase()}" data-job="${i}" data-key="${k}" value="${j[k]??''}" onkeydown="quantityKey(event)" oninput="touch()" ${dis}></td>`).join('')}<td><button class="small danger" title="Xóa công việc" onclick="removeJob(${i})" ${dis}>×</button></td></tr>`).join('');
  totals()
}
function renderTasks(){
  const dis=info.readonly?'disabled':'';
  $('taskRows').innerHTML=report.handover.map((t,i)=>`<div class="handover"><input type="checkbox" aria-label="Đã xử lý" data-task="${i}" data-key="done" ${t.done?'checked':''} onchange="touch()" ${dis}><input type="text" aria-label="Nội dung bàn giao" data-task="${i}" data-key="text" value="${esc(t.text)}" placeholder="Việc cần ca sau tiếp tục…" oninput="touch()" ${dis}><button class="small danger" title="Xóa việc bàn giao" onclick="removeTask(${i})" ${dis}>×</button></div>`).join('')
}
function collect(){
  if(!$('actor'))return;
  report.actor=$('actor').value;
  report.notes=$('notes').value;
  document.querySelectorAll('[data-attachment-caption]').forEach(el=>report.attachments[+el.dataset.attachmentCaption].caption=el.value);
  document.querySelectorAll('[data-staff-role]').forEach(el=>report.staffing[+el.dataset.staffRole].role=el.value);
  document.querySelectorAll('[data-staff-people]').forEach(el=>report.staffing[+el.dataset.staffPeople].people=el.value);
  document.querySelectorAll('[data-job]').forEach(el=>report.jobs[+el.dataset.job][el.dataset.key]=el.type==='checkbox'?el.checked:el.value);
  document.querySelectorAll('[data-task]').forEach(el=>report.handover[+el.dataset.task][el.dataset.key]=el.type==='checkbox'?el.checked:el.value)
}
function totals(){
  if(!$('jobTotal'))return;
  const sums=keys.map(k=>report.jobs.reduce((n,j)=>n+(quantityValid(j[k])?(Number(j[k])||0):0),0));
  validateJobInputs(false);
  $('jobTotal').innerHTML='<tr class="totalrow"><td colspan="4">Tổng lượt công việc</td>'+sums.map(v=>'<td style="text-align:right">'+v.toLocaleString('vi-VN')+'</td>').join('')+'<td></td></tr>'
}
function touch(){
  if(info.readonly)return;
  collect();
  dirty=true;
  totals();
  refreshTabBadges();
  $('saveState').textContent=conflict?'Có xung đột · tải lại trước khi lưu':(report.status==='closed'||info.review)?'Có sửa đổi chưa lưu · cần ghi lý do':'Có thay đổi · đang chờ tự lưu';
  clearTimeout(timer);
  if(report.actor.trim()&&report.status==='draft'&&!info.review&&!uploading&&!conflict)timer=setTimeout(()=>save(false),1600)
}
function addKHB(){
  if(info.readonly)return;
  collect();
  if(report.staffing.some(x=>/^KHB\b/i.test(x.role)))return toast('Ca này đã có vị trí KHB.');
  report.staffing.push({role:'KHB (KẾ HOẠCH BÃI)',people:''});
  renderEditor();
  touch()
}
function addStaff(){
  collect();
  report.staffing.push({role:'VỊ TRÍ KHÁC',people:''});
  renderStaff();
  touch()
}
function removeStaff(i){
  collect();
  if(!confirm('Xóa dòng phân công này?'))return;
  report.staffing.splice(i,1);
  renderStaff();
  touch()
}
function addJob(){
  collect();
  report.jobs.push({name:'',detail:'',xn:false,rtg:false,...Object.fromEntries(keys.map(k=>[k,null]))});
  renderJobs();
  touch()
}
function removeJob(i){
  collect();
  if(!confirm('Xóa dòng công việc này?'))return;
  report.jobs.splice(i,1);
  renderJobs();
  touch()
}
function addTask(){
  collect();
  report.handover.push({text:'',done:false});
  renderTasks();
  touch()
}
function removeTask(i){
  collect();
  report.handover.splice(i,1);
  renderTasks();
  touch()
}
async function carry(){
  try{
    collect();
    const rows=await api('/api/reports?to='+report.date);
    const rank=r=>r.date+'_'+(r.shift==='DAY'?'0':'1');
    const previous=rows.find(r=>rank(r)<rank(report));
    if(!previous)return toast('Chưa có ca trước để lấy bàn giao.');
    const tasks=previous.handover.filter(t=>!t.done);
    if(!tasks.length)return toast('Ca trước không có việc chưa xử lý.');
    if(!confirm('Lấy '+tasks.length+' việc từ '+dateLabel(previous.date)+' '+shiftName(previous.shift)+'?'))return;
    for(const t of tasks)if(!report.handover.some(x=>x.text===t.text))report.handover.push({text:t.text,done:false});
    renderTasks();
    touch()
  }catch(e){
    error(e)
  }
}
async function save(manual=true,reason='',saveKind=null){
  if(info.readonly||saving||uploading)return false;
  if(!validateJobInputs(true))return false;
  if(conflict){
    toast('Có xung đột. Sao chép phần chưa lưu nếu cần rồi tải lại báo cáo.',true);
    return false
  }
  clearTimeout(timer);
  collect();
  if(!report.actor.trim()){
    toast('Điền người nhập trước khi lưu.',true);
    return false
  }
  if((report.status==='closed'||info.review)&&!reason){
    return false
  }
  saving=true;
  const before=JSON.stringify(report);
  $('saveState').textContent='Đang lưu vào DB…';
  try{
    const saved=await api('/api/save',{report:JSON.parse(before),version:report.version,reason,context:info.context,save_kind:saveKind||(info.review?'correction':report.status==='closed'||manual?'manual':'auto')});
    collect();
    const changed=JSON.stringify(report)!==before;
    report.version=saved.version;
    report.id=saved.id;
    report.updated_at=saved.updated_at;
    report.created_at=saved.created_at;
    dirty=changed;
    sessionStorage.setItem('ca_actor',report.actor);
    $('saveState').textContent=changed?'Có thay đổi mới · đang chờ lưu':'Đã lưu lúc '+timeLabel(saved.updated_at);
    if(manual)toast('Đã lưu báo cáo.');
    if(!changed){
      const active=document.activeElement;
      const protectedFocus=active&&$('edit').contains(active)&&['INPUT','TEXTAREA','SELECT'].includes(active.tagName);
      if(!protectedFocus&&$('modal').classList.contains('hide'))renderEditor();
    }else if(report.status==='draft'&&!info.review&&!uploading)timer=setTimeout(()=>save(false),1600);
    await refreshInfo();
    return true
  }catch(e){
    dirty=true;
    if(e.status===409)conflict=true;
    $('saveState').innerHTML='<span class="issue">Chưa lưu: '+esc(e.message)+'</span>'+(conflict?' <button class="small" data-id="'+esc(report.date+'_'+report.shift)+'" onclick="reloadConflict(false)">Tải bản mới, bỏ thay đổi</button> <button onclick="reloadConflict(true)">Tải bản mới, giữ ghi chú chưa lưu</button>':'');
    error(e);
    return false
  }finally{
    saving=false
  }
}
async function manualSave(){
  if(uploading||saving)return toast('Đợi tải tệp/lưu xong trước khi tiếp tục.');
  if(report.status==='closed'||info.review){
    const reason=prompt('Lý do chỉnh sửa / bổ sung báo cáo:');
    if(!reason?.trim())return;
    await save(true,reason)
  }else await save(true)
}
async function closeShift(){
  if(saving||uploading)return toast('Đợi lưu xong rồi chốt ca.');
  collect();
  if(!validateJobInputs(true))return;
  if(!report.actor?.trim()||!report.staffing.some(s=>s.role.trim().toUpperCase()==='PHỤ TRÁCH CHUNG'&&s.people.trim())){showEditTab('staff');toast('Điền người nhập và PHỤ TRÁCH CHUNG trước khi chốt ca.',true);const chiefIndex=report.staffing.findIndex(s=>s.role.trim().toUpperCase()==='PHỤ TRÁCH CHUNG');($('actor')?.value?document.querySelector('[data-staff-people="'+chiefIndex+'"]'):$('actor'))?.focus();return}
  if(!confirm('Chốt '+shiftName(report.shift).toLowerCase()+' '+dateLabel(report.date)+'? Sau khi chốt, mỗi lần sửa cần ghi lý do.'))return;
  report.status='closed';
  if(!await save(true,'Chốt ca','close')){
    report.status='draft';
    renderEditor();
    $('saveState').textContent='Chưa chốt thành công · kiểm tra thông tin và lưu lại'
  }
}
function renderFilters(target,prefix){
  const today=info.now.slice(0,10),start=today.slice(0,8)+'01';
  $(target).innerHTML=`<div class="row"><label class="input">Từ ngày<input type="date" id="${prefix}from" value="${start}"></label><label class="input">Đến ngày<input type="date" id="${prefix}to" value="${today}"></label><label class="input">Ca<select id="${prefix}shift"><option value="">Tất cả ca</option><option value="DAY">Ca ngày</option><option value="NIGHT">Ca đêm</option></select></label><label class="input">Trạng thái<select id="${prefix}status"><option value="">Tất cả</option><option value="closed">Đã chốt</option><option value="draft">Nháp</option></select></label><label class="input">Tìm nội dung<input id="${prefix}q" placeholder="Người, tàu, công việc…"></label><button class="primary" onclick="${prefix==='l'?'loadList()':'loadSummary()'}">${prefix==='l'?'Tìm báo cáo':'Xem tổng hợp'}</button></div>`
}
function filterQuery(p){
  if($(p+'from').value&&$(p+'to').value&&$(p+'from').value>$(p+'to').value)throw new Error('Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.');
  return new URLSearchParams(Object.fromEntries(['from','to','shift','status','q'].map(k=>[k,$(p+k).value]))).toString()
}
const LIST_PAGE=50;
function listPager(d){
  if(d.total<=LIST_PAGE)return '';
  const prev=d.offset>0,next=d.offset+LIST_PAGE<d.total;
  return '<div class="row between noprint" style="margin-top:12px"><button class="small" onclick="loadList('+Math.max(0,d.offset-LIST_PAGE)+')" '+(prev?'':'disabled')+'>← Trang trước</button><span class="muted subtle">Trang '+(Math.floor(d.offset/LIST_PAGE)+1)+'/'+Math.ceil(d.total/LIST_PAGE)+'</span><button class="small" onclick="loadList('+(d.offset+LIST_PAGE)+')" '+(next?'':'disabled')+'>Trang sau →</button></div>'
}
async function loadList(offset=0){
  try{
    const d=await api('/api/reports-page?'+filterQuery('l')+'&limit='+LIST_PAGE+'&offset='+(Number(offset)||0));
    listRows=d.rows;
    $('listCount').textContent=d.total+' báo cáo'+(d.total>LIST_PAGE?' · hiển thị '+(d.offset+1)+'–'+(d.offset+d.rows.length):'');
    $('reportList').innerHTML=reportRows(d.rows)+listPager(d)
  }catch(e){
    error(e)
  }
}
function agg(rows){
  const m=new Map;
  for(const r of rows)for(const j of r.jobs){
    if(!j.name.trim())continue;
    if(!m.has(j.name))m.set(j.name,{name:j.name,...Object.fromEntries(keys.map(k=>[k,0]))});
    for(const k of keys)m.get(j.name)[k]+=Number(j[k])||0
  }
  return [...m.values()]
}
async function loadSummary(){
  try{
    const rows=await api('/api/reports?'+filterQuery('s')),groups=agg(rows),sums=keys.map(k=>groups.reduce((n,j)=>n+j[k],0));
    $('summaryData').innerHTML=`<div class="note">Đang tổng hợp <strong>${rows.length} ca</strong>, trong đó <strong>${rows.filter(r=>r.status==='draft').length} ca nháp</strong>. Số lượng là lượt công việc đã báo cáo, không phải số container duy nhất. Tìm kiếm chọn ca phù hợp rồi cộng toàn bộ công việc trong các ca đó.</div><div class="grid">${keys.map((k,i)=>`<div class="card metric"><span>${k.toUpperCase()}</span><strong>${sums[i].toLocaleString('vi-VN')}</strong><span>Lượt công việc</span></div>`).join('')}</div><div class="card"><div class="row between"><h2>Chi tiết theo loại công việc</h2><button onclick="exportSummary()">Xuất Excel</button></div><div class="scroll"><table><thead><tr><th>Công việc</th>${keys.map(k=>'<th>'+k.toUpperCase()+'</th>').join('')}</tr></thead><tbody>${groups.map(j=>'<tr><td>'+esc(j.name)+'</td>'+keys.map(k=>'<td>'+j[k].toLocaleString('vi-VN')+'</td>').join('')+'</tr>').join('')||'<tr><td colspan="5" class="empty">Chưa có số liệu trong bộ lọc.</td></tr>'}</tbody></table></div></div>`
  }catch(e){
    error(e)
  }
}
function download(url){
  const a=document.createElement('a');
  a.href=url;
  a.download='';
  document.body.appendChild(a);
  a.click();
  a.remove()
}
function exportReport(){
  if(dirty)return toast('Lưu báo cáo trước khi xuất.',true);
  download('/api/export?'+new URLSearchParams({id:report.id,context:info.context}))
}
function exportSummary(){
  try{
    download('/api/export?'+filterQuery('s')+'&context='+encodeURIComponent(info.context))
  }catch(e){
    error(e)
  }
}
async function backup(){
  if(!leave())return;
  try{
    const res=await fetch('/api/backup',{method:'POST',headers:{'X-Ca-Request':'1'},body:JSON.stringify({context:info.context})});
    if(!res.ok)throw new Error((await res.json()).error);
    const blob=await res.blob(),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;
    a.download=(res.headers.get('Content-Disposition')||'').match(/filename="([^"]+)"/)?.[1]||'BAO_CAO_CA.db';
    a.click();
    setTimeout(()=>URL.revokeObjectURL(url),60000);
    toast('Đã tạo bản sao. File tải xuống và bản lưu tại DU_LIEU/SAO_LUU_MANG_DI.')
  }catch(e){
    error(e)
  }
}
function openViewer(){
  if(!leave())return;
  $('dbFile').value='';
  $('dbFile').click()
}
async function readDB(el){
  const f=el.files[0];
  if(!f)return;
  if(f.size>8*1024*1024*1024)return toast('DB tối đa 8 GB ở bản này.',true);
  try{
    const res=await fetch('/api/open-viewer',{method:'POST',headers:{'X-Ca-Request':'1'},body:f});
    const data=await res.json();
    if(!res.ok)throw new Error(data.error);
    dirty=false;
    report=null;
    await go('home');
    toast('Đã mở bản sao DB ở chế độ chỉ xem.')
  }catch(e){
    error(e)
  }
}
async function returnMain(){
  if(!leave())return;
  try{
    await api('/api/main-db',{});
    dirty=false;
    report=null;
    await go('home')
  }catch(e){
    error(e)
  }
}
function preview(r){
  return `<div class="row between noprint"><h2>Xem báo cáo</h2><div class="row"><button onclick="printReport()">In / Lưu PDF</button><button onclick="closeModal()">Đóng</button></div></div><div class="preview" data-print-ca="${esc(dateLabel(r.date)+' · '+shiftName(r.shift))}"><h2>BÁO CÁO SẢN XUẤT CUỐI CA<br>BỘ PHẬN BÃI CONTAINER</h2><p><strong>${esc(period(r))}</strong> · ${r.status==='closed'?'Đã chốt':'BẢN NHÁP'}</p><p>Tàu trong ca: ${esc(allReportShips(r).join('; '))||'—'}</p><p class="subtle">Người lưu: ${esc(r.actor)} · ${timeLabel(r.updated_at)} · Phiên bản ${r.version||''}</p><table><thead><tr><th>Phân công</th><th>Nhân sự</th></tr></thead><tbody>${r.staffing.filter(s=>s.people).map(s=>'<tr><td>'+esc(s.role)+(s.ships?.length?'<br>'+esc(s.ships.join('; ')):'')+'</td><td>'+esc(s.people)+'</td></tr>').join('')}</tbody></table><br><table><thead><tr><th>Công việc</th><th>Chi tiết</th><th>XN</th><th>RTG</th>${keys.map(k=>'<th>'+k.toUpperCase()+'</th>').join('')}</tr></thead><tbody>${r.jobs.filter(j=>j.detail||j.xn||j.rtg||keys.some(k=>j[k]!==null&&j[k]!==''&&j[k]!==undefined)).map(j=>'<tr><td>'+esc(j.name)+'</td><td>'+esc([...(j.ships||[]),j.detail].filter(Boolean).join('; '))+'</td><td>'+(j.xn?'X':'')+'</td><td>'+(j.rtg?'X':'')+'</td>'+keys.map(k=>'<td>'+esc(j[k])+'</td>').join('')+'</tr>').join('')}<tr><th colspan="4">Tổng lượt</th>${keys.map(k=>'<th>'+r.jobs.reduce((n,j)=>n+(Number(j[k])||0),0)+'</th>').join('')}</tr></tbody></table><br><strong>Ghi chú bàn giao</strong><p style="white-space:pre-wrap">${esc(r.notes)||'—'}</p>${r.handover.map(t=>'<p>'+(t.done?'☑ Đã xử lý: ':'□ Chưa xử lý: ')+esc(t.text)+'</p>').join('')}${attachmentPreview(r)}<p class="muted subtle">Số lượng là lượt công việc đã báo cáo, không phải số container duy nhất.</p>${typeof signatureHTML==='function'?signatureHTML(r):''}</div>`
}
async function enableCorrections(){
  if(!leave())return;
  const reviewer=await chooseSinglePerson('Chọn người kiểm tra / bổ sung',sessionStorage.getItem('ca_actor')||'');
  if(!reviewer?.trim())return;
  try{
    await api('/api/enable-corrections',{context:info.context,reviewer});
    await refreshInfo();
    if(page==='edit'&&report?.id){
      report.actor=reviewer;
      renderEditor()
    }else await go('home');
    toast('Đã bật bổ sung trên bản sao. Mỗi lần lưu cần ghi lý do.')
  }catch(e){
    error(e)
  }
}
function openImport(){
  if(info.review){
    toast('Về DB chính của máy bãi trước khi nhập bổ sung.',true);
    return
  }
  if(!leave())return;
  $('importFile').value='';
  $('importFile').click()
}
let importPlan=null,importSelection=new Set();
const importLabels={ready:'Có thể nhập',conflict:'Xung đột · không tự ghi đè',same:'Đã có nội dung này',missing:'Không có ca gốc · không nhập'};
async function previewImport(el){
  const f=el.files[0];
  if(!f)return;
  if(f.size>8*1024*1024*1024)return toast('DB tối đa 8 GB.',true);
  try{
    const res=await fetch('/api/corrections-preview',{method:'POST',headers:{'X-Ca-Request':'1'},body:f});
    const data=await res.json();
    if(!res.ok)throw new Error(data.error);
    importPlan=data;
    importSelection=new Set(data.items.filter(r=>r.state==='ready').map(r=>r.id));
    renderImport()
  }catch(e){
    error(e)
  }
}
function renderImport(){
  modal('<div class="row between"><h2>Đối chiếu bản bổ sung</h2><button onclick="closeModal()">Đóng</button></div><p class="muted">Chỉ các ca được chọn và không có xung đột mới nhập về DB chính. Các ca khác giữ nguyên. Tool tạo bản sao trước khi nhập.</p><div class="scroll"><table><thead><tr><th>Chọn</th><th>Ngày / Ca</th><th>Người sửa</th><th>Đối chiếu</th><th></th></tr></thead><tbody>'+importPlan.items.map((r,i)=>'<tr><td><input type="checkbox" class="mergeChoice" onchange="importSelection[this.checked?\'add\':\'delete\'](this.value)" value="'+esc(r.id)+'" '+(r.state==='ready'?(importSelection.has(r.id)?'checked':''):'disabled')+'></td><td>'+dateLabel(r.date)+' · '+shiftName(r.shift)+'</td><td>'+esc(r.actor)+'</td><td>'+importLabels[r.state]+'</td><td><button class="small" onclick="compareImport('+i+')">Xem hai bản</button></td></tr>').join('')+'</tbody></table></div>'+(!importPlan.items.length?'<p>Không có nội dung bổ sung cần nhập.</p>':'')+'<div class="row" style="justify-content:flex-end;margin-top:18px"><button class="primary" onclick="applyImport()">Nhập các ca đã chọn</button></div>',true)
}
function compareImport(i){
  const item=importPlan.items[i];
  modal('<div class="row between"><h2>Đối chiếu '+dateLabel(item.date)+' · '+shiftName(item.shift)+'</h2><button onclick="renderImport()">Về danh sách đối chiếu</button></div>'+reportDiffHTML(item.current,item.incoming),true)
}
async function applyImport(){
  const selected=[...document.querySelectorAll('.mergeChoice:checked')].map(x=>x.value);
  if(!selected.length)return toast('Chọn ít nhất một ca có thể nhập.',true);
  if(!confirm('Nhập bổ sung '+selected.length+' ca vào DB chính?'))return;
  try{
    const result=await api('/api/corrections-apply',{nonce:importPlan.nonce,selected});
    closeModal();
    dirty=false;
    await go('list');
    toast('Đã nhập bổ sung '+result.count+' ca. Các ca khác giữ nguyên.')
  }catch(e){
    error(e)
  }
}
function showPreview(){
  if(dirty)return toast('Lưu trước khi xem bản in.',true);
  modal(preview(report),true)
}
async function showHistory(){
  try{
    const rows=await api('/api/history?id='+encodeURIComponent(report.id)+'&context='+encodeURIComponent(info.context));
    window.revisions=rows;
    modal('<div class="row between"><h2>Lịch sử chỉnh sửa</h2><button onclick="closeModal()">Đóng</button></div><p class="muted">Tên người nhập do người dùng chọn; tài khoản máy chỉ hỗ trợ đối chiếu, không định danh người thật trên máy dùng chung. Phiên bản có thể có khoảng trống do gộp tự lưu.</p><div class="scroll"><table><thead><tr><th>Phiên bản</th><th>Thời gian</th><th>Loại lưu</th><th>Người lưu / tài khoản máy</th><th>Lý do</th><th></th></tr></thead><tbody>'+rows.map((r,i)=>`<tr><td>${r.version}</td><td>${esc(timeLabel(r.saved_at))}</td><td>${esc(r.kind||'legacy')}</td><td>${esc(r.actor)}<br><small>${esc(r.os_user||'Không ghi tài khoản máy')}</small></td><td>${esc(r.reason)}</td><td><button class="small" onclick="revisionPreview(${i})" ${info.capabilities?.revisionDiff?'':'disabled'}>Xem thay đổi</button></td></tr>`).join('')+'</tbody></table></div>',true)
  }catch(e){error(e)}
}
function revisionPreview(i){
  const current=window.revisions[i],previous=window.revisions[i+1];
  modal('<div class="row between"><h2>Phiên bản '+esc(current.version)+(previous?' so với '+esc(previous.version):' · bản đầu tiên')+'</h2><button onclick="showHistory()">Về lịch sử</button></div>'+(previous?reportDiffHTML(previous.payload,current.payload):'<p>Không có phiên bản liền trước để so sánh.</p>'),true)
}

function attachmentURL(a,downloadFile=false){
  return '/api/attachment?'+new URLSearchParams({hash:a.hash,name:a.name,context:info.context,...(downloadFile?{download:'1'}:{})})
}
function isPreviewImage(a){
  return /\.(jpg|jpeg|png|webp)$/i.test(a.name)
}
function renderAttachments(){
  const arr=report.attachments||[];
  $('attachmentRows').innerHTML=arr.length?arr.map((a,i)=>`<div class="attachmentCard">${isPreviewImage(a)?'<a href="'+esc(attachmentURL(a))+'" target="_blank" rel="noopener"><img src="'+esc(attachmentURL(a))+'" alt="'+esc(a.name)+'"></a>':'<div class="fileIcon">'+esc((a.name.split('.').pop()||'TỆP').slice(0,8).toUpperCase())+'</div>'}<div class="fileBody"><div class="filename">${esc(a.name)}</div><input aria-label="Chú thích tệp" data-attachment-caption="${i}" value="${esc(a.caption)}" placeholder="Biên bản gì? Khu vực, sự việc…" oninput="touch()" ${info.readonly?'disabled':''}><div class="row between" style="margin-top:10px"><a href="${esc(attachmentURL(a,true))}" download>Tải tệp</a><button class="small danger" onclick="removeAttachment(${i})" ${info.readonly?'disabled':''}>Gỡ khỏi ca</button></div></div></div>`).join(''):'<p class="muted">Chưa có tệp đính kèm. Chọn ảnh hiện trường hoặc biên bản để lưu cùng ca này.</p>'
}
async function chooseAttachments(){
  if(saving||uploading)return toast('Đợi thao tác đang chạy hoàn tất.');
  collect();
  try{
    if(info.readonly){
      const actor=await chooseSinglePerson('Chọn người thêm tệp',sessionStorage.getItem('ca_actor')||'');
      if(!actor?.trim())return;
      await api('/api/enable-corrections',{context:info.context,reviewer:actor.trim()});
      await refreshInfo();
      report.actor=actor.trim();
      sessionStorage.setItem('ca_actor',report.actor);
      renderEditor()
    }
    if(!report.actor.trim())return toast('Điền tên người nhập trước khi thêm tệp.',true);
    $('attachmentFiles').value='';
    $('attachmentFiles').click()
  }catch(e){
    error(e)
  }
}
function fileSize(n){
  return (n/(1024*1024)).toLocaleString('vi-VN',{maximumFractionDigits:2})+' MB'
}
async function optimizePhoto(f){
 if(!/\.(jpe?g|png|webp)$/i.test(f.name))return {file:f,caption:''};
 const bitmap=await createImageBitmap(f,{imageOrientation:'from-image'});
 try{
  const scale=Math.min(1,2560/Math.max(bitmap.width,bitmap.height));
  const canvas=document.createElement('canvas');
    canvas.width=Math.max(1,Math.round(bitmap.width*scale));
    canvas.height=Math.max(1,Math.round(bitmap.height*scale));
  const ctx=canvas.getContext('2d');
    if(!ctx)throw new Error('Trình duyệt chưa hỗ trợ thu nhỏ ảnh. Tắt tùy chọn để lưu tệp gốc.');
  if(!/\.png$/i.test(f.name)){
      ctx.fillStyle='#fff';
      ctx.fillRect(0,0,canvas.width,canvas.height)
    }
  ctx.drawImage(bitmap,0,0,canvas.width,canvas.height);
  const png=/\.png$/i.test(f.name),mime=png?'image/png':'image/jpeg';
  const blob=await new Promise((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(new Error('Không tạo được ảnh tối ưu. Tắt tùy chọn để lưu tệp gốc.')),mime,0.9));
  if(blob.size>=f.size)return {file:f,caption:''};
  const name=f.name.replace(/\.[^.]+$/,'')+'_toi_uu'+(png?'.png':'.jpg');
  return {file:new File([blob],name,{type:mime}),caption:'Ảnh tối ưu từ '+f.name+' ('+fileSize(f.size)+' → '+fileSize(blob.size)+', '+canvas.width+'×'+canvas.height+' px). Tệp gốc không được lưu trong DB.'};

  }finally{
    bitmap.close()
  }
}
async function uploadAttachments(el){
 if(!el.files.length||saving||uploading)return;
 collect();
  const files=[...el.files],optimize=$('optimizePhotos').checked;
 if((report.attachments?.length||0)+files.length>40)return toast('Mỗi ca tối đa 40 tệp.',true);
 if(files.some(f=>f.size>100*1024*1024))return toast('Mỗi tệp tối đa 100 MB.',true);
 if(!report.actor.trim())return toast('Điền tên người nhập trước khi thêm tệp.',true);
 clearTimeout(timer);
 if(dirty||!report.id){
    if(!await save(false,'Lưu nội dung trước khi thêm tệp đính kèm'))return
  }
 uploading=true;
  $('edit').inert=true;
  let added=0,duplicates=0,failed='';
 try{
    for(let i=0;i<files.length;i++){
  const source=files[i];
      $('uploadState').textContent='Đang tải '+(i+1)+'/'+files.length+': '+source.name+' ('+fileSize(source.size)+')';
  let prepared={file:source,caption:''};
  if(optimize){
        try{
          prepared=await optimizePhoto(source)
        }catch(e){
          prepared={file:source,caption:''}
        }
      }
  const f=prepared.file;
  const qs=new URLSearchParams({context:info.context,id:report.id,version:report.version,name:f.name,actor:report.actor,caption:prepared.caption});
  const res=await fetch('/api/attachment-upload?'+qs,{method:'POST',headers:{'X-Ca-Request':'1'},body:f});
  const text=await res.text();
      let result;
      try{
        result=JSON.parse(text)
      }catch(e){
        throw new Error('Máy xử lý trả lỗi HTTP '+res.status+'. Đóng phiên tool cũ và mở bản mới để thử lại.')
      }
  if(!res.ok)throw new Error(result.error||'Không lưu được tệp '+f.name);
  if(!result.report)throw new Error('Tool nền còn là phiên bản cũ. Bấm Thoát tool, sau đó mở lại bản '+info.version+'.');
  report=result.report;
      dirty=false;
      conflict=false;
      if(result.added)added++;
      else duplicates++;
  renderEditor();
      $('edit').inert=true;

    }
  }catch(e){
    failed=e.message;
    error(e)
  }finally{
  uploading=false;
    $('edit').inert=false;
  $('uploadState').textContent=(added?'Đã lưu ngay '+added+' tệp vào ca. ':'')+(duplicates?duplicates+' tệp đã có, không thêm trùng. ':'')+(failed?'Chưa hoàn tất: '+failed:'');
  if(added&&!failed)toast('Đã lưu '+added+' tệp vào báo cáo, không cần bấm lưu thêm.');

  }
}
function removeAttachment(i){
  if(info.readonly)return;
  collect();
  if(!confirm('Gỡ tệp khỏi báo cáo hiện tại? Tệp vẫn giữ trong phiên bản lịch sử đã lưu.'))return;
  report.attachments.splice(i,1);
  renderAttachments();
  touch()
}
function exportAttachments(){
  if(dirty)return toast('Lưu báo cáo trước khi tải bộ tệp.',true);
  download('/api/attachments-zip?'+new URLSearchParams({id:report.id,context:info.context}))
}
function attachmentPreview(r){
  if(!r.attachments?.length)return '';
  return '<h3 style="margin-top:18px">Ảnh / Biên bản đính kèm ('+r.attachments.length+')</h3>'+r.attachments.map(a=>'<div class="printAttachment">'+(isPreviewImage(a)?'<img src="'+esc(attachmentURL(a))+'" alt="'+esc(a.name)+'">':'')+'<p><strong>'+esc(a.name)+'</strong><br>'+esc(a.caption||'')+' <a class="noprint" href="'+esc(attachmentURL(a,true))+'" download>Tải tệp gốc</a></p></div>').join('')
}
async function printReport(){
  const previewNode=$('modalBody').querySelector('.preview[data-print-ca]');
  const stillVisible=()=>!$('modal').classList.contains('hide')&&previewNode&&previewNode.getClientRects().length&&$('modalBody').querySelector('.preview[data-print-ca]')===previewNode;
  if(printBusy||!stillVisible())return false;
  printBusy=true;
  try{
    await Promise.all([...document.querySelectorAll('#modal img')].map(img=>img.decode().catch(()=>{})));
    if(!stillVisible())return false;
    window.print();
    return true
  }finally{printBusy=false}
}
async function exitTool(){
  if(!leave())return;
  if(!confirm('Thoát tool trên máy này? Bấm mở lại chương trình khi cần sử dụng tiếp.'))return;
  try{
    await api('/api/shutdown',{});
    dirty=false;
    document.body.innerHTML='<main style="padding:60px;font:18px Segoe UI"><h2>Đã thoát Sổ báo cáo ca.</h2><p>Có thể đóng tab này. Bấm mở lại chương trình khi cần làm việc tiếp.</p></main>'
  }catch(e){
    error(e)
  }
}


function openMonthExport(){
  if(!leave())return;
  modal('<h2>Xuất Excel nguyên tháng</h2><p class="muted">Một file gồm sheet tổng hợp tháng và mỗi ca đã lưu một sheet. Có cả nháp và đã chốt, ghi rõ trạng thái. Ca chưa nhập được ghi trong danh sách tháng.</p><label>Chọn tháng<input type="month" id="exportMonth" value="'+info.now.slice(0,7)+'"></label><div class="row" style="justify-content:flex-end;margin-top:20px"><button onclick="closeModal()">Hủy</button><button class="primary" onclick="downloadMonth()">Xuất cả tháng</button></div>')
}
function downloadMonth(){
  const month=$('exportMonth').value;
  if(!month)return toast('Chọn tháng cần xuất.',true);
  download('/api/export-month?'+new URLSearchParams({month,context:info.context}));
  closeModal()
}
function updatedJobs(jobs,defaults){
  const kept=jobs.slice();
  for(const name of defaults)if(!kept.some(j=>j.name===name))kept.push({name,detail:'',xn:false,rtg:false,...Object.fromEntries(keys.map(k=>[k,null]))});
  return kept
}
function updateJobsTemplate(){
  if(info.readonly)return;
  collect();
  if(!confirm('Áp dụng danh mục công việc hiện tại? Chỉ thêm công việc còn thiếu; mọi dòng đã có trong ca được giữ nguyên.'))return;
  report.jobs=updatedJobs(report.jobs,info.jobs);
  renderJobs();
  touch()
}

window.addEventListener('beforeunload',e=>{
  if(dirty||saving||uploading){
    e.preventDefault();
    e.returnValue=''
  }
});
document.addEventListener('keydown',e=>{
  if((e.ctrlKey||e.metaKey)&&e.key==='s'&&page==='edit'){
    e.preventDefault();
    manualSave()
  }
});


// Integer validation is shared by totals and save, independent of browser number coercion.
function quantityValid(value){return value===null||value===undefined||value===''||(/^\d+$/.test(String(value))&&Number(value)<=9999999)}
function quantityKey(event){if(['.',',','e','E','-','+'].includes(event.key))event.preventDefault()}
function validateJobInputs(notify=false){
 let first=null;
 document.querySelectorAll('[data-job]').forEach(el=>{
  if(!keys.includes(el.dataset.key))return;
  const valid=!el.validity?.badInput&&quantityValid(el.value);
  el.setAttribute?.('aria-invalid',String(!valid));el.classList?.toggle('invalidQuantity',!valid);
  if(!valid&&!first)first=el;
 });
 if(first&&notify){showEditTab('jobs');first.focus?.();toast('Công việc '+(report.jobs[Number(first.dataset.job)]?.name||Number(first.dataset.job)+1)+', cột '+first.dataset.key.toUpperCase()+': cần số nguyên từ 0 đến 9.999.999.',true)}
 return !first;
}
async function reloadConflict(keepNotes){
 if(saving||uploading||!conflict)return;
 collect();const notes=report.notes,id=report.id||(report.date+'_'+report.shift);
 try{
  const fresh=await api('/api/report?id='+encodeURIComponent(id));
  report=fresh;conflict=false;dirty=false;renderEditor();
  if(keepNotes){report.notes=notes;$('notes').value=notes;dirty=true;clearTimeout(timer);$('saveState').textContent='Đã tải bản mới; ghi chú giữ lại chưa được lưu. Kiểm tra rồi bấm Lưu.'}
 }catch(e){error(e)}
}
