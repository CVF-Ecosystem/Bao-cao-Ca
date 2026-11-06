function personOptions(current=''){
  const names=[...(info.people||[])];
  if(current&&!names.includes(current))names.unshift(current);
  return '<option value="">— Chọn họ tên —</option>'+names.map(name=>'<option value="'+esc(name)+'" '+(name===current?'selected':'')+'>'+esc(name)+'</option>').join('')
}
let personResolver=null;
function chooseSinglePerson(title,current=''){
  return new Promise(resolve=>{
    personResolver=resolve;
    modal('<h2>'+esc(title)+'</h2><p class="muted">Chọn tên trong danh sách nhân sự, không cần gõ lại.</p><select id="singlePerson">'+personOptions(current)+'</select><div class="row" style="justify-content:flex-end;margin-top:20px"><button onclick="finishPerson(null)">Hủy</button><button class="primary" onclick="finishPerson(document.getElementById(\'singlePerson\').value)">Chọn tên này</button></div>')
  })
}
function finishPerson(value){
  if(value!==null&&!value)return toast('Chọn một họ tên trong danh sách.',true);
  const resolve=personResolver;
  personResolver=null;
  closeModal();
  if(resolve)resolve(value)
}
let staffPickerIndex=null;
function openStaffPicker(index){
 if(info.readonly)return;
 if(saving||uploading)return toast('Đợi lưu/tải tệp xong rồi chọn người.');
 clearTimeout(timer);
  collect();
  staffPickerIndex=index;
 const staff=report.staffing[index],selected=(staff.people||'').split(/\s*;\s*/).filter(Boolean);
 const names=[...new Set([...(info.people||[]),...selected])];
 const vessel=(staff.ships||[]).join('; ');
 modal('<h2>Chọn người: '+esc(staff.role)+(vessel?' · '+esc(vessel):'')+'</h2>'+
 '<p class="muted">Chọn đúng người cho dòng này. Đổi tổ chỉ lọc danh sách; người đã chọn ở tổ khác vẫn giữ.</p>'+
 '<label>Tổ / ca nhân sự<select id="pickerTeam" onchange="changePickerTeam(this.value)">'+staffTeamOptions(selectedStaffTeam())+'</select></label>'+
 '<p id="teamHint" class="note"></p><input id="peopleSearch" placeholder="Tìm tên… gõ có dấu hoặc không dấu" oninput="filterPeople()">'+
 '<div id="peopleChoices" style="max-height:390px;overflow:auto;margin-top:14px">'+
 names.map(name=>'<label class="row peopleChoice" data-person="'+esc(name)+'" style="padding:9px;border-bottom:1px solid var(--line);font-weight:500"><input type="checkbox" value="'+esc(name)+'" '+(selected.includes(name)?'checked':'')+' onchange="filterPeople()"><span>'+esc(name)+'</span></label>').join('')+
 '</div><p id="peopleEmpty" class="muted hide">Không có tên phù hợp. Kiểm tra tổ đã cấu hình hoặc xóa từ tìm kiếm.</p>'+
 '<div class="row between" style="margin-top:18px"><button class="small" onclick="document.querySelectorAll(\'#peopleChoices input\').forEach(x=>x.checked=false);filterPeople()">Bỏ chọn tất cả</button><div class="row"><button onclick="closeModal()">Hủy</button><button class="primary" onclick="applyPeople()">Dùng các tên đã chọn</button></div></div>');
 filterPeople();
}
function changePickerTeam(id){
  setStaffTeam(id);
  filterPeople()
}
function pickerPersonVisible(name,checked,team,query){
 const fold=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[đĐ]/g,'d').toLowerCase();
 return (!team||team.people.includes(name)||checked)&&fold(name).includes(fold(query));
}
function filterPeople(){
 const id=$('pickerTeam').value,team=(info.teams||[]).find(t=>t.id===id),query=$('peopleSearch').value;
 let visible=0;
 document.querySelectorAll('.peopleChoice').forEach(row=>{
  const input=row.querySelector('input');
  const show=pickerPersonVisible(row.dataset.person,input.checked,team,query);
  row.classList.toggle('hide',!show);
    if(show)visible++;

  });
 $('peopleEmpty').classList.toggle('hide',visible>0);
 $('teamHint').textContent=team?(team.people.length?'Đang hiện '+team.people.length+' người của '+team.name+'. Người đã chọn ngoài tổ cũng được giữ.':team.name+' chưa có danh sách. Vào Danh mục nhân sự / công việc để điền người cho tổ này.'):'Đang hiện tất cả nhân viên và các tên đã lưu trong dòng này.';
}

function applyPeople(){
  collect();
  report.staffing[staffPickerIndex].people=[...document.querySelectorAll('#peopleChoices input:checked')].map(x=>x.value).join('; ');
  closeModal();
  renderStaff();
  touch()
}


function allReportShips(r){
  return [...new Set([...(r.ships||[]),...r.staffing.flatMap(x=>x.ships||[]),...r.jobs.flatMap(x=>x.ships||[])])]
}
let shipTarget=null,shipSelection=new Set();
function chooseShips(kind,index=null){
  if(info.readonly)return;
  if(saving||uploading)return toast('Đợi thao tác đang chạy hoàn tất.');
  collect();
  if(kind!=='staff'||!canChooseStaffShip(report.staffing[index]?.role))return toast('Chỉ chọn tàu tại TALLY TÀU hoặc XUẤT TÀU.');
  clearTimeout(timer);
  shipTarget={kind,index};
  shipSelection=new Set((report.staffing[index].ships||[]).length===1?report.staffing[index].ships:[]);
  renderShipPicker()
}
function renderShipPicker(){
 const names=[...new Set([...(info.ships||[]),...(report.staffing[shipTarget.index].ships||[]),...shipSelection])];
 modal('<h2>Chọn 1 tàu cho '+esc(report.staffing[shipTarget.index].role)+'</h2>'+
 '<p class="note">Một dòng = một tàu và người thực hiện. Tàu thứ hai, thứ ba dùng nút “＋ Thêm tàu” trong cùng khung.</p>'+
 '<input id="shipSearch" placeholder="Tìm tên tàu…" oninput="filterShipChoices()">'+
 '<div id="shipChoices" style="max-height:330px;overflow:auto;margin-top:12px">'+names.map(name=>
 '<label class="row shipChoice" style="padding:10px;border-bottom:1px solid var(--line)"><input type="radio" name="staffVessel" value="'+esc(name)+'" '+(shipSelection.has(name)?'checked':'')+' onchange="shipSelection=new Set([this.value])"><span>'+esc(name)+'</span></label>').join('')+'</div>'+
 '<div class="row" style="margin-top:14px"><input id="newShipName" placeholder="Tên tàu mới"><button onclick="addShipFromPicker()">Thêm tàu mới</button></div>'+
 '<div class="row between" style="margin-top:18px"><button onclick="shipSelection.clear();renderShipPicker()">Không gắn tàu</button><div class="row"><button onclick="closeModal()">Hủy</button><button class="primary" onclick="applyShips()">Dùng tàu đã chọn</button></div></div>');
}

function filterShipChoices(){
  const q=$('shipSearch').value.toUpperCase().trim();
  document.querySelectorAll('.shipChoice').forEach(el=>el.classList.toggle('hide',!el.textContent.toUpperCase().includes(q)))
}
async function addShipFromPicker(){
  const name=$('newShipName').value.trim();
  if(!name)return toast('Điền tên tàu mới.',true);
  try{
    const d=await api('/api/ships-add',{name,context:info.context});
    info.ships=d.ships;
    shipSelection=new Set([name.toUpperCase().replace(/\s+/g,' ')]);
    renderShipPicker();
    toast('Đã lưu tàu mới vào danh sách.')
  }catch(e){
    error(e)
  }
}
function applyShips(){
  if(info.readonly)return;
  collect();
  if(!shipTarget||shipTarget.kind!=='staff'||!canChooseStaffShip(report.staffing[shipTarget.index]?.role))return toast('Chỉ chọn tàu tại TALLY TÀU hoặc XUẤT TÀU.');
  if(shipSelection.size>1)return toast('Mỗi dòng chỉ chọn 1 tàu. Thêm dòng riêng cho tàu khác.',true);
  report.staffing[shipTarget.index].ships=[...shipSelection];
  closeModal();
  renderStaff();
  $('reportShipNames').textContent=allReportShips(report).join('; ')||'Chưa chọn tàu';
  touch()
}
async function manageShips(){
  if(saving||uploading)return toast('Đợi thao tác đang chạy hoàn tất.');
  if(page==='edit'&&report)collect();
  clearTimeout(timer);
  try{
    await refreshInfo();
    modal('<h2>Danh sách tàu</h2><p class="muted">Danh sách được lưu trong DB. Thêm tàu mới tại đây, không cần sửa code.</p><div style="max-height:330px;overflow:auto">'+(info.ships||[]).map(name=>'<p>'+esc(name)+'</p>').join('')+'</div><div class="row"><input id="catalogShipName" placeholder="Tên tàu mới" '+(info.readonly?'disabled':'')+'><button onclick="addCatalogShip()" '+(info.readonly?'disabled':'')+'>Thêm tàu</button></div><div style="text-align:right;margin-top:16px"><button onclick="closeModal()">Đóng</button></div>')
  }catch(e){
    error(e)
  }
}
async function addCatalogShip(){
  try{
    const d=await api('/api/ships-add',{name:$('catalogShipName').value,context:info.context});
    info.ships=d.ships;
    await manageShips();
    toast('Đã lưu tàu mới.')
  }catch(e){
    error(e)
  }
}

let catalogEditor=null;
function teamEditorHTML(){
 let teams;
  try{
    teams=JSON.parse(catalogEditor.teams)
  }catch(e){
    teams=info.teams
  }
 if(!Array.isArray(teams)||teams.length!==3)teams=info.teams||[];
 return '<div class="row between" style="margin-top:24px"><h3>3 tổ nhân sự để lọc danh sách</h3></div><p class="note">Muốn chọn ca rồi tự điền người vào vị trí: dùng nút Mẫu phân công Ca 1–2–3 / ca ngày ở menu bên trái sau khi lưu danh mục này.</p><p class="muted">Đặt tên Ca 1 / Ca 2 / Ca 3 hoặc theo tổ của anh. Mỗi dòng một người, đúng họ tên có trong danh mục Nhân viên bên trên. Đây là nhóm chọn người, không đổi ca báo cáo ngày / đêm.</p><div class="catalogColumns">'+teams.map((team,i)=>
 '<div class="input"><label>Tên tổ<input id="team_name_'+i+'" maxlength="80" value="'+esc(team.name)+'"></label><label style="margin-top:12px">Nhân viên của tổ<textarea id="team_people_'+i+'" rows="10" placeholder="Mỗi dòng một họ tên">'+esc(team.people.join('\n'))+'</textarea></label></div>').join('')+'</div>';
}
async function manageCatalogs(){
  if(!leave())return;
  if(info.review)return toast('Về DB chính của máy để sửa danh mục.',true);
  try{
    catalogEditor=await api('/api/catalogs');
    modal('<div class="row between"><div><div class="sectionno">CÀI ĐẶT DÙNG CHUNG</div><h2>Danh mục nhập báo cáo</h2></div><button onclick="closeModal()">Đóng</button></div><p class="muted">Mỗi dòng một tên. Áp dụng cho lần chọn tên và ca mới; báo cáo cũ giữ nguyên. Cũng có thể mở các file trong thư mục DANH_MUC để sửa bằng Notepad, lưu UTF-8.</p><div class="catalogColumns">'+[['people','Nhân viên','NHAN_VIEN.txt'],['roles','Vị trí phân công','VI_TRI.txt'],['jobs','Công việc','CONG_VIEC.txt']].map(([key,label,file])=>'<label class="input">'+label+'<span class="muted subtle">'+file+'</span><textarea id="catalog_'+key+'" rows="15">'+esc(catalogEditor[key])+'</textarea></label>').join('')+'</div>'+teamEditorHTML()+'<div class="note" style="margin-top:16px">Giữ vị trí PHỤ TRÁCH CHUNG để chốt ca. Không nhập trùng tên; không dùng dấu chấm phẩy trong tên. Tàu vẫn quản lý tại nút Danh sách tàu.</div><div class="row" style="justify-content:flex-end"><button onclick="closeModal()">Hủy</button><button class="primary" onclick="saveCatalogs()">Lưu danh mục</button></div>',true)
  }catch(e){
    error(e)
  }
}
async function saveCatalogs(){
  try{
    const text=Object.fromEntries(['people','roles','jobs'].map(key=>[key,$('catalog_'+key).value]));
    text.teams=JSON.stringify([0,1,2].map(i=>({id:'team'+(i+1),name:$('team_name_'+i).value,people:$('team_people_'+i).value.split(/\r?\n/).map(v=>v.trim()).filter(Boolean)})));
    await api('/api/catalogs-save',{context:info.context,digest:catalogEditor.digest,text});
    await refreshInfo();
    closeModal();
    toast('Đã lưu danh mục. Báo cáo cũ giữ nguyên.')
  }catch(e){
    error(e)
  }
}
go('home');
