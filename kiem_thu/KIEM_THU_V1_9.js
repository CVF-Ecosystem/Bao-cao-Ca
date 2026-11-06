// node KIEM_THU_V1_9.js — kiểm thử hành vi giao diện bản 1.9 bằng Node VM, không cần trình duyệt.
'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');

// Nút DOM giả: nhớ lớp CSS để kiểm tra hiện/ẩn.
function makeNode() {
  const node = { classes: new Set(), attrs: {} };
  node.classList = {
    toggle(name, force) { (force === undefined ? !node.classes.has(name) : force) ? node.classes.add(name) : node.classes.delete(name); },
    add: name => node.classes.add(name), remove: name => node.classes.delete(name), contains: name => node.classes.has(name),
  };
  node.setAttribute = (key, value) => { node.attrs[key] = value; };
  node.getAttribute = key => node.attrs[key];
  return node;
}
const nodes = {};
const sandbox = {
  history: { replaceState() {} },
  window: { addEventListener() {} },
  document: { addEventListener() {}, querySelectorAll: () => [], getElementById: id => nodes[id] || (nodes[id] = makeNode()) },
  URLSearchParams, encodeURIComponent, setTimeout, clearTimeout,
  sessionStorage: { getItem: () => null, setItem() {} },
};
vm.createContext(sandbox);
const assets = __dirname + '/../giao_dien/tai_nguyen/';
vm.runInContext(fs.readFileSync(assets + 'ung_dung.js', 'utf8'), sandbox);
vm.runInContext('go=()=>{}', sandbox);
vm.runInContext(fs.readFileSync(assets + 'danh_muc.js', 'utf8'), sandbox);
const run = code => vm.runInContext(code, sandbox);

(async () => {
  // 1. id báo cáo không bao giờ được ghép vào chuỗi JavaScript trong onclick.
  const evil = "2026-11-01_DAY');alert(1);('";
  sandbox.evil = evil;
  const html = run(`reportRows([{id:evil,date:'2026-11-01',shift:'DAY',staffing:[],actor:'A',status:'draft',updated_at:'2026-11-01T10:00:00+07:00'}])`);
  assert(!html.includes("loadReport('"), 'id không được nằm trong chuỗi JS');
  assert(html.includes('onclick="loadReport(this.dataset.id)"'));
  assert(html.includes('data-id="2026-11-01_DAY&#39;);alert(1);(&#39;"'), 'id phải được escape trong thuộc tính');

  // 2. Thanh chuyển trang.
  assert.equal(run("listPager({total:10,offset:0,rows:[]})"), '');
  const middle = run("listPager({total:120,offset:50,rows:[]})");
  assert(middle.includes('loadList(0)') && middle.includes('loadList(100)') && middle.includes('Trang 2/3'));
  assert(!/disabled/.test(middle));
  assert(/loadList\(0\)" disabled/.test(run("listPager({total:120,offset:0,rows:[]})")), 'trang đầu khóa nút trước');
  assert(/loadList\(150\)" disabled/.test(run("listPager({total:120,offset:100,rows:[]})")), 'trang cuối khóa nút sau');

  // 3. loadList gọi API phân trang với bộ lọc, limit và offset.
  run("var requested='';filterQuery=()=>'status=closed';reportRows=rows=>'ROWS'+rows.length;" +
      "api=async path=>{requested=path;return {rows:[{},{}],total:120,limit:50,offset:50}}");
  await run("loadList(50)");
  const requested = run('requested');
  assert(requested.startsWith('/api/reports-page?status=closed'));
  assert(requested.includes('limit=50') && requested.includes('offset=50'));
  assert(nodes.listCount.textContent.includes('120 báo cáo') && nodes.listCount.textContent.includes('51–52'));
  assert(nodes.reportList.innerHTML.startsWith('ROWS2'));

  // 4. Trang chủ dùng /api/overview, không tải toàn bộ danh sách báo cáo.
  run("var calls=[];api=async path=>{calls.push(path);return {recent:[],month_count:7,draft_count:3,current_status:'draft'}};" +
      "info={suggestion:{date:'2026-11-06',shift:'DAY'},now:'2026-11-06T10:00:00+07:00',readonly:false,review:false,database:'x.db'}");
  await run("renderHome()");
  assert.equal(JSON.stringify(run('calls')), '["/api/overview"]');
  const home = nodes.home.innerHTML;
  assert(home.includes('<strong>7</strong>') && home.includes('<strong>3</strong>') && home.includes('Đã có bản nháp'));

  // 5. Cảnh báo sao lưu theo mức độ: 'info' chỉ chấm nhỏ ở menu, 'error' mới hiện dải cảnh báo.
  const infoBase = "review:false,readonly:false,now:'2026-11-06T10:00:00+07:00',version:'1.9.0',catalog_warning:''";
  const level = async (lv, text) => {
    run(`api=async()=>({${infoBase},backup_warning:${JSON.stringify(text)},backup_level:${JSON.stringify(lv)}})`);
    await run('refreshInfo()');
    return { banner: !nodes.backupWarning.classes.has('hide'), dot: !nodes.navAlert.classes.has('hide'), text: nodes.backupWarning.textContent };
  };
  assert.deepEqual(await level('info', 'Chưa chọn nơi dự phòng'), { banner: false, dot: true, text: '' });
  assert.deepEqual(await level('error', 'Sao lưu bên ngoài thất bại'), { banner: true, dot: true, text: 'Sao lưu bên ngoài thất bại' });
  assert.deepEqual(await level('', ''), { banner: false, dot: false, text: '' });
  assert.equal(nodes.appVersion.textContent, 'Phiên bản 1.9.0 · nguon');
  run(`api=async()=>({${infoBase},build:{commit:'abcdef123456'}})`);
  await run('refreshInfo()');
  assert.equal(nodes.appVersion.textContent, 'Phiên bản 1.9.0 · abcdef123456');
  run(`api=async()=>({${infoBase},build:{commit:'<img src=x onerror=alert(1)>'}})`);
  await run('refreshInfo()');
  assert.equal(nodes.appVersion.textContent, 'Phiên bản 1.9.0 · <img src=x onerror=alert(1)>');
  assert.equal(nodes.appVersion.innerHTML, undefined);

  // 6. Trang nhập ca: 4 tab, chỉ tab đang chọn hiện, số trên tab cập nhật khi sửa.
  run(`info={readonly:false,review:false,people:['An'],teams:[],ships:[],roles:[],jobs:[]};
report={date:'2026-11-06',shift:'DAY',version:0,status:'draft',actor:'',notes:'',
 staffing:[{role:'PHỤ TRÁCH CHUNG',people:''},{role:'TALLY',people:'An'}],
 jobs:[{name:'X',detail:'',xn:false,rtg:false,f20:3,f40:null,e20:null,e40:null}],
 handover:[{text:'a',done:false},{text:'b',done:true}],attachments:[]};editTab='staff'`);
  run('renderEditor()');
  const editor = nodes.edit.innerHTML;
  for (const id of ['staff', 'jobs', 'notes', 'files']) {
    assert(editor.includes(`id="tab_${id}"`) && editor.includes(`id="panel_${id}"`), 'thiếu tab/khung ' + id);
  }
  assert(editor.includes('class="tabPanel card" id="panel_staff"'));
  assert(editor.includes('class="tabPanel card hide" id="panel_jobs"'));
  assert(editor.includes('class="tabBadge warn" id="tabBadge_staff"'), 'chưa có phụ trách chung phải cảnh báo');
  assert(editor.includes('id="tabBadge_jobs">1<') && editor.includes('id="tabBadge_notes" title="Việc bàn giao chưa xử lý">1<'));
  run("showEditTab('jobs')");
  assert(!nodes.panel_jobs.classes.has('hide') && nodes.panel_staff.classes.has('hide') && nodes.panel_notes.classes.has('hide'));
  assert.equal(nodes.tab_jobs.attrs['aria-selected'], 'true');
  run("showEditTab('khong-co')");
  assert.equal(run('editTab'), 'staff');
  run("report.staffing[0].people='Trưởng ca';refreshTabBadges()");
  assert.equal(nodes.tabBadge_staff.textContent, '2');
  assert(!nodes.tabBadge_staff.classes.has('warn'));

  console.log('6 kiểm tra giao diện 1.9 đạt: escape id, thanh trang, loadList, trang chủ, cảnh báo theo mức độ, tab nhập ca.');
})().catch(e => { console.error(e); process.exitCode = 1; });
