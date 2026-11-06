'use strict';

// Build a proposed copy only. Opening a preview never changes the current report.
function splitStaffNames(value){return String(value||'').split(/\s*;\s*/).map(s=>s.trim()).filter(Boolean)}
function mergeStaffNames(current,added){
 const names=splitStaffNames(current),seen=new Set(names.map(n=>n.normalize('NFC').toLowerCase()));
 for(const name of added){const key=name.normalize('NFC').toLowerCase();if(!seen.has(key)){names.push(name);seen.add(key)}}
 return names.join('; ');
}
function planStaffing(staffing,template,mode){
 if(!['replace','append'].includes(mode))throw new Error('Cách áp dụng mẫu không hợp lệ.');
 const rows=JSON.parse(JSON.stringify(staffing)),changes=[],skipped=[];
 for(const item of template){
  const matches=rows.map((row,index)=>({row,index})).filter(x=>x.row.role.trim().toUpperCase()===item.role.trim().toUpperCase());
  if(matches.length>1||(matches.length===1&&(matches[0].row.ships||[]).length>1)){
   skipped.push(item.role+': có nhiều dòng hoặc nhiều tàu, giữ nguyên để anh phân công riêng.');continue;
  }
  if(mode==='append'&&!item.people.length)continue;
  const existing=matches[0]?.row,before=existing?.people||'';
  const after=mode==='append'?mergeStaffNames(before,item.people):item.people.join('; ');
  if(after.length>3000)throw new Error(item.role+': danh sách người quá dài.');
  if(before===after)continue;
  if(existing)existing.people=after;
  else rows.push({role:item.role,people:after});
  changes.push({role:item.role,ships:existing?.ships||[],before,after});
 }
 if(rows.length>200)throw new Error('Áp dụng mẫu sẽ vượt 200 dòng nhân sự. Giảm số dòng rồi thử lại.');
 return {staffing:rows,changes,skipped};
}

let pendingStaffPlan=null;
function templateLabel(id){return id==='day'?'Nhân sự ca ngày':(info.teams||[]).find(t=>t.id===id)?.name||id}
function applyShiftTemplate(id){if(id)previewStaffTemplate(id,'replace')}
function applyDayStaff(){previewStaffTemplate('day','append')}
function previewStaffTemplate(id,mode){
 if(!report||info.readonly||saving||uploading||conflict)return toast('Chưa thể áp dụng. Đợi lưu/tải tệp xong; nếu có xung đột hãy tải lại báo cáo.',true);
 collect();const template=(info.staff_templates||{})[id]||[];
 if(!template.some(row=>row.people.length))return toast(templateLabel(id)+' chưa có mẫu phân công. Bấm Cài mẫu phân công để chọn người cho từng vị trí.',true);
 try{
  const plan=planStaffing(report.staffing,template,mode);
  if(!plan.changes.length)return toast(plan.skipped.length?'Không tự đổi các dòng nhiều tàu / nhiều người phân công riêng. Chọn người trực tiếp tại từng dòng.':'Phân công hiện tại đã giống mẫu, không cần thay đổi.');
  clearTimeout(timer);
  pendingStaffPlan={...plan,id,mode,base:JSON.stringify(report.staffing),context:info.context,key:report.date+'_'+report.shift};
  modal('<h2>'+esc(mode==='append'?'Bổ sung nhân sự ca ngày':'Áp dụng '+templateLabel(id))+'</h2>'+
   '<p class="note">'+(mode==='append'?'Chỉ thêm người còn thiếu vào đúng vị trí, không xóa hoặc thay người đang có.':'Các vị trí trong bảng dưới sẽ đổi theo mẫu, kể cả ô mẫu để trống. Vị trí không có trong mẫu giữ nguyên.')+'</p>'+
   (report.status==='closed'||info.review?'<p class="note warn">Ca đã chốt / bản bổ sung: sau khi áp dụng phải Lưu chỉnh sửa kèm lý do.</p>':'')+
   '<div class="scroll"><table><thead><tr><th>Vị trí / tàu</th><th>Hiện tại</th><th>Sau áp dụng</th></tr></thead><tbody>'+
   plan.changes.map(row=>'<tr><td>'+esc(row.role)+(row.ships.length?'<br>'+esc(row.ships.join('; ')):'')+'</td><td>'+esc(row.before||'—')+'</td><td>'+esc(row.after||'(Để trống)')+'</td></tr>').join('')+'</tbody></table></div>'+
   (plan.skipped.length?'<div class="note warn" style="margin-top:14px">'+plan.skipped.map(esc).join('<br>')+'</div>':'')+
   '<div class="row" style="justify-content:flex-end;margin-top:18px"><button onclick="cancelStaffPlan()">Hủy</button><button class="primary" onclick="confirmStaffPlan()">Xác nhận áp dụng</button></div>',true);
 }catch(e){error(e)}
}
function cancelStaffPlan(){pendingStaffPlan=null;closeModal()}
function confirmStaffPlan(){
 const plan=pendingStaffPlan;if(!plan)return;
 if(info.readonly||saving||uploading||conflict)return toast('Chưa thể áp dụng lúc này.',true);
 collect();
 if(plan.context!==info.context||plan.key!==report.date+'_'+report.shift||plan.base!==JSON.stringify(report.staffing)){
  pendingStaffPlan=null;return toast('Báo cáo hoặc nguồn DB vừa đổi. Đóng cửa sổ và xem trước lại.',true);
 }
 report.staffing=plan.staffing;
 if(plan.id!=='day')setStaffTeam(plan.id);
 pendingStaffPlan=null;closeModal();renderStaff();touch();
 $('reportShipNames').textContent=allReportShips(report).join('; ')||'Chưa chọn tàu';
 toast(plan.mode==='append'?'Đã bổ sung nhân sự ca ngày; giữ người đang có.':'Đã điền phân công mẫu. Anh kiểm tra người nghỉ / thay ca trước khi chốt.');
}

// Edit all four reusable templates without writing to any report.
let staffingEditor=null,staffingDraft=null,staffingProfile='team1';
function newTemplateDraft(source){
 const result={};
 for(const id of ['team1','team2','team3','day']){
  const rows=source[id]||[];
  result[id]=rows.length?rows.flatMap(row=>row.people.length?row.people.map(person=>({role:row.role,person})):[{role:row.role,person:''}]):info.roles.map(role=>({role,person:''}));
 }
 return result;
}
async function manageStaffTemplates(){
 if(!leave())return;
 if(info.review)return toast('Về DB chính để cài mẫu phân công dùng chung.',true);
 try{
  await refreshInfo();staffingEditor=await api('/api/catalogs');
  let source;try{source=JSON.parse(staffingEditor.staff_templates)}catch(e){source=info.staff_templates||{}}
  if(!source||typeof source!=='object'||!['team1','team2','team3','day'].every(id=>Array.isArray(source[id])&&source[id].every(row=>row&&typeof row.role==='string'&&Array.isArray(row.people)&&row.people.every(name=>typeof name==='string'))))source=info.staff_templates||{};
  staffingDraft=newTemplateDraft(source);staffingProfile='team1';renderStaffTemplateEditor();
 }catch(e){error(e)}
}
function templateRoleOptions(current){
 const roles=[...new Set([...(info.roles||[]),current].filter(Boolean))];
 return roles.map(role=>'<option value="'+esc(role)+'" '+(role===current?'selected':'')+'>'+esc(role)+'</option>').join('');
}
function collectStaffTemplate(){
 if(!staffingDraft)return;
 document.querySelectorAll('[data-template-role]').forEach(el=>staffingDraft[staffingProfile][+el.dataset.templateRole].role=el.value);
 document.querySelectorAll('[data-template-person]').forEach(el=>staffingDraft[staffingProfile][+el.dataset.templatePerson].person=el.value);
}
function switchStaffTemplate(id){collectStaffTemplate();staffingProfile=id;renderStaffTemplateEditor()}
function addTemplatePerson(){collectStaffTemplate();if(staffingDraft[staffingProfile].length>=200)return toast('Tối đa 200 dòng mỗi mẫu.',true);staffingDraft[staffingProfile].push({role:info.roles[0]||'',person:''});renderStaffTemplateEditor()}
function removeTemplatePerson(index){collectStaffTemplate();staffingDraft[staffingProfile].splice(index,1);renderStaffTemplateEditor()}
function renderStaffTemplateEditor(){
 const ids=['team1','team2','team3','day'];
 modal('<div class="row between"><h2>Mẫu phân công theo ca</h2><button onclick="closeModal()">Đóng</button></div>'+
 '<p class="note">Chọn vị trí và người thường làm. Một vị trí nhiều người: thêm dòng và chọn lại cùng vị trí. Ô người trống có nghĩa là để trống vị trí đó khi áp dụng mẫu ca. Không thay đổi báo cáo cũ khi lưu mẫu.</p>'+
 '<label>Đang sửa mẫu<select id="staffingProfile" onchange="switchStaffTemplate(this.value)">'+ids.map(id=>'<option value="'+id+'" '+(id===staffingProfile?'selected':'')+'>'+esc(templateLabel(id))+'</option>').join('')+'</select></label>'+
 '<p class="muted subtle">Nhân sự ca ngày là nhóm riêng; chỉ bổ sung khi anh bấm nút, không tự chạy theo giờ máy. Có thể đổi tên 3 ca tại Danh mục nhân sự / công việc.</p>'+
 '<div class="scroll"><table class="templateEditorTable"><thead><tr><th>Vị trí</th><th>Người thực hiện</th><th></th></tr></thead><tbody>'+
 staffingDraft[staffingProfile].map((row,i)=>'<tr><td><select aria-label="Vị trí mẫu dòng '+(i+1)+'" data-template-role="'+i+'">'+templateRoleOptions(row.role)+'</select></td><td><select aria-label="Người mẫu dòng '+(i+1)+'" data-template-person="'+i+'">'+personOptions(row.person)+'</select></td><td><button class="small danger" onclick="removeTemplatePerson('+i+')">×</button></td></tr>').join('')+'</tbody></table></div>'+
 '<div class="row between" style="margin-top:16px"><button onclick="addTemplatePerson()">＋ Thêm vị trí / người</button><button class="primary" onclick="saveStaffTemplates()">Lưu cả 4 mẫu</button></div>',true);
}
function compileStaffTemplates(draft){
 const result={};
 for(const id of ['team1','team2','team3','day']){
  const groups=new Map();
  for(const row of draft[id]){
   if(!row.role)throw new Error('Chọn vị trí hợp lệ trong '+templateLabel(id));
   if(!groups.has(row.role))groups.set(row.role,[]);
   const names=groups.get(row.role);if(row.person&&!names.includes(row.person))names.push(row.person);
  }
  result[id]=[...groups].map(([role,people])=>({role,people}));
 }
 return result;
}
async function saveStaffTemplates(){
 try{
  collectStaffTemplate();const text={...staffingEditor,staff_templates:JSON.stringify(compileStaffTemplates(staffingDraft))};delete text.digest;
  await api('/api/catalogs-save',{context:info.context,digest:staffingEditor.digest,text});
  await refreshInfo();closeModal();toast('Đã lưu 3 mẫu ca và mẫu nhân sự ca ngày. Báo cáo cũ giữ nguyên.');
 }catch(e){error(e)}
}
