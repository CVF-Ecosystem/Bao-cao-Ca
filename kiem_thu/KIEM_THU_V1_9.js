// node KIEM_THU_V1_9.js — kiểm thử hành vi giao diện bản 1.9 bằng Node VM, không cần trình duyệt.
'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');

const nodes = {};
const sandbox = {
  history: { replaceState() {} },
  window: { addEventListener() {} },
  document: { addEventListener() {}, getElementById: id => nodes[id] || (nodes[id] = {}) },
  URLSearchParams, encodeURIComponent, setTimeout, clearTimeout,
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(__dirname + '/../tai_nguyen/ung_dung.js', 'utf8'), sandbox);
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

  console.log('4 kiểm tra giao diện 1.9 đạt: escape id, thanh trang, loadList, trang chủ.');
})().catch(e => { console.error(e); process.exitCode = 1; });
