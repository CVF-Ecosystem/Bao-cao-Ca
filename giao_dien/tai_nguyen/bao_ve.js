'use strict';
let protectionData=null,restoreChoice=null;
async function openProtection(){
 if(!leave())return;if(info.review){toast('Về DB chính trước khi bảo vệ hoặc khôi phục.',true);return}
 dirty=false;clearTimeout(timer);
 try{
 protectionData=await api('/api/protection');const d=protectionData,last=x=>x?esc(timeLabel(x.at)):'Chưa có lần thành công';
 modal(`<h2>Bảo vệ dữ liệu báo cáo ca</h2><p>Mỗi bản sao chứa báo cáo nhiều tháng, lịch sử chỉnh sửa và ảnh/PDF đã lưu trong DB.</p>
 <div class="note ${d.warning?'warn':''}">${esc(d.warning||'Kiểm tra ngày giờ sao lưu thành công bên dưới.')}</div>
 <p><strong>Tại máy:</strong> ${last(d.last_local)}<br><strong>Bên ngoài:</strong> ${last(d.last_external)}</p>
 <p class="muted subtle">Tự sao lưu khi mở ứng dụng, sau chốt/sửa chốt; bản nháp sao lưu tối đa mỗi 5 phút khi có thao tác lưu. Giữ tối đa 10 bản hôm nay, bản cuối mỗi ngày trong 30 ngày và bản cuối mỗi tháng lâu hơn. Bản mang đi và DB trước khôi phục không tự xóa.</p>
 <label>Thư mục dự phòng ngoài DU_LIEU<input id="backupDirectory" placeholder="Ví dụ: D:\\DuPhongBaoCao" value="${esc(d.external_directory)}"></label>
 <p class="muted subtle">Thư mục phải có sẵn. Chọn ổ khác hoặc thư mục đám mây đã đồng bộ trên máy. Ứng dụng kiểm tra ghi file, không xác minh đã tải lên đám mây.</p>
 <div class="row"><button onclick="chooseProtectionDirectory()">Chọn thư mục…</button><button onclick="saveProtectionDirectory()">Lưu nơi dự phòng</button><button onclick="backupProtectionNow()">Sao lưu ngay</button><button onclick="closeModal()">Đóng</button></div>
 <h3>Khôi phục từ bản sao</h3><p class="note warn">Khôi phục thay toàn bộ DB hiện tại. Các thay đổi sau thời điểm bản sao sẽ không có trong DB được phục hồi. DB cũ được giữ riêng trước khi thay.</p>
 <p class="muted subtle">Chọn file ở nơi khác: Thoát tool rồi mở KHOI_PHUC_DU_LIEU.pyw; EXE chạy với --restore. Khi thiếu/hỏng DB, mở ứng dụng sẽ hiện chọn bản sao.</p>
 <div class="scroll"><table><thead><tr><th>Bản sao / nơi lưu</th><th>Thời gian file</th><th></th></tr></thead><tbody>${d.backups.slice(0,100).map(b=>`<tr><td>${esc(b.name)}<br><small>${esc(b.location)}</small></td><td>${esc(timeLabel(b.modified))}<br>${(b.bytes/1024/1024).toFixed(1)} MB</td><td><button data-id="${b.id}" onclick="previewRestore(this.dataset.id)">Kiểm tra / khôi phục</button></td></tr>`).join('')||'<tr><td colspan="3">Chưa có bản sao.</td></tr>'}</tbody></table></div>${d.backups.length>100?'<p>Hiển thị 100 bản mới nhất; các bản còn lại vẫn được giữ trên đĩa.</p>':''}`,true);
 }catch(e){error(e)}
}
async function saveProtectionDirectory(){try{await api('/api/protection-config',{context:info.context,directory:$('backupDirectory').value});await refreshInfo();await openProtection()}catch(e){error(e)}}
async function backupProtectionNow(){try{const d=await api('/api/protection-backup',{context:info.context});await refreshInfo();await openProtection();toast(d.warning||'Đã tạo và kiểm tra bản sao thành công.',!!d.warning)}catch(e){error(e)}}
async function previewRestore(id){try{
 const p=await api('/api/restore-preview',{context:info.context,id});restoreChoice={id,sha256:p.sha256};const b=protectionData.backups.find(x=>x.id===id);
 modal(`<h2>Bản sao đã qua kiểm tra</h2><p><strong>${esc(b.name)}</strong></p><p>${p.reports} ca · ${p.revisions} lần lưu lịch sử<br>Từ ${esc(dateLabel(p.first_day))} đến ${esc(dateLabel(p.last_day))}</p><p class="note warn">DB hiện tại sẽ được thay bằng bản sao này. Các thay đổi sau thời điểm bản sao không nằm trong bản phục hồi. DB cũ được giữ tại TRUOC_KHOI_PHUC.</p><label>Nhập KHOI PHUC để tiếp tục<input id="confirmRestore" autocomplete="off"></label><div class="row"><button class="primary" id="doRestore" onclick="performRestore()">Khôi phục dữ liệu</button><button onclick="openProtection()">Quay lại</button></div>`);
 }catch(e){error(e)}}
async function performRestore(){if(!restoreChoice)return;const button=$('doRestore');button.disabled=true;try{
 await api('/api/restore',{context:info.context,...restoreChoice,confirmation:$('confirmRestore').value});dirty=false;report=null;restoreChoice=null;clearTimeout(timer);closeModal();await go('home');toast('Đã khôi phục. DB cũ được giữ trong TRUOC_KHOI_PHUC.');
 }catch(e){error(e);button.disabled=false}}

async function chooseProtectionDirectory(){try{const d=await api('/api/protection-directory',{context:info.context});if(d.directory)$('backupDirectory').value=d.directory}catch(e){error(e)}}
