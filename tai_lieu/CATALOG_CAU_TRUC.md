# Catalog cấu trúc — Sổ báo cáo ca 1.9.1

Dành cho agent/người mới đọc để nắm dự án nhanh. Đọc file này trước khi sửa mã.

- Quét lần 1: 2026-11-06, commit `d14d902`.
- Cập nhật 1.9.1: 2026-11-06, D1-1…D1-4; xem [BAO_CAO_CODEX_DOT1.md](BAO_CAO_CODEX_DOT1.md) để biết số đo, kiểm thử và giới hạn. Chưa phát hành EXE mới.
- Phạm vi đã đọc toàn bộ: `ma_nguon/*.py`, `giao_dien/giao_dien.html`, `giao_dien/tai_nguyen/*.js`, `kiem_thu/*`, `cong_cu/*.bat`, `MO_BAO_CAO_CA.pyw`, `KHOI_PHUC_DU_LIEU.pyw`, `SO_BAO_CAO_CA.spec`, `pyproject.toml`, `.gitignore`, `tai_lieu/THAY_DOI_V1_9.txt`, `HUONG_DAN.txt`.
- Chưa đọc chi tiết: `giao_dien/tai_nguyen/style.css` (81 dòng), `tai_lieu/` các bản 1.7–1.8.2 và `DANH_GIA_UNG_DUNG_V1_8_1.md`, nội dung `mau/MAU_BAO_CAO.xlsx` (chỉ biết có `sheet1`), dữ liệu trong `DU_LIEU/`.

## 1. Tổng quan

- **Ngôn ngữ/runtime:** Python 3.9+, chỉ thư viện chuẩn (`sqlite3`, `http.server`, `zipfile`, `xml`, `tkinter` cho hộp thoại). Không có dependency ngoài.
- **Giao diện:** một trang HTML + JS thuần (không framework), chạy trên trình duyệt, gọi API HTTP trên `127.0.0.1` cổng ngẫu nhiên.
- **Dữ liệu:** một file SQLite `DU_LIEU/BAO_CAO_CA.db`, `schema_version = 3`. Mọi thời gian theo múi giờ +07 (`THIET_LAP.VN`).
- **Đóng gói:** `cong_cu/TAO_FILE_EXE.bat` gọi PyInstaller, tạo `SO_BAO_CAO_CA.exe` và `.spec` ở gốc. EXE không tự cập nhật theo mã nguồn; phải build lại.
- **Import:** các module import nhau bằng tên trần, vì `ma_nguon/` được đưa vào `sys.path` (xem `MO_BAO_CAO_CA.pyw`).

## 2. Phụ thuộc giữa module

```text
THIET_LAP          (không import module nội bộ nào)
NGHIEP_VU          ← THIET_LAP
LUU_TRU  (Store)   ← THIET_LAP, NGHIEP_VU
BAO_VE_DU_LIEU     ← THIET_LAP, NGHIEP_VU   (import LUU_TRU trong hàm, tránh vòng lặp)
MAU_PHAN_CONG      ← NGHIEP_VU
QUAN_LY_DANH_MUC   ← THIET_LAP, NGHIEP_VU, MAU_PHAN_CONG
XUAT_EXCEL         (chỉ stdlib; import trong hàm từ BAO_CAO_EXCEL)
BAO_CAO_EXCEL      ← THIET_LAP, NGHIEP_VU   (+ XUAT_EXCEL trong hàm)
MAY_CHU  (Handler) ← tất cả ở trên
BAO_CAO_CA         ← THIET_LAP, NGHIEP_VU, MAY_CHU, BAO_VE_DU_LIEU   (điểm vào chính)
```

## 3. Bảng module mã nguồn (`ma_nguon/`)

| File | Dòng | Vai trò | Hàm/lớp chính |
|---|---|---|---|
| `THIET_LAP.py` | 42 | Hằng số: `VERSION='1.9.1'`, giới hạn file (100 MB) và DB (8 GB), `ROOT`, múi giờ, `KEYS = f20,f40,e20,e40`. Nạp danh mục mặc định và metadata build | `PEOPLE, ROLES, JOBS, SHIPS`, `build_info` |
| `NGHIEP_VU.py` | 172 | Nghiệp vụ dùng chung: gợi ý ca theo giờ (`suggest`, ca ngày 06–18), làm sạch chữ, nhận dạng loại tệp (PNG/JPEG/WEBP/HEIC/PDF, còn lại là nhị phân), chuẩn hóa báo cáo, lỗi nghiệp vụ | `AppError`, `normalize`, `clean_text`, `file_type`, `ship_names`, `report_ships`, `chief_people`, `ClosingConnection`, `database_error` |
| `LUU_TRU.py` | 400 | **Lớp dữ liệu.** Tạo/nâng schema, đọc/ghi báo cáo, lịch sử, tệp đính kèm, tàu, người; đối chiếu và nhập bổ sung | `Store` (`save`, `list`, `page`, `overview`, `history`, `add_attachment`, `enable_corrections`, `correction_plan`, `apply_corrections`, `backup`) |
| `BAO_VE_DU_LIEU.py` | 498 | Sao lưu SQLite đã kiểm tra (WAL-safe), kiểm tra dung lượng, kết quả kiểm tra khởi động có dấu thay đổi, chính sách giữ bản, khôi phục, khóa phiên và hộp thoại tkinter | `snapshot`, `inspect_db`, `Protection`, `SessionLock`, `recovery_dialog`, `adoption_dialog`, `choose_directory` |
| `QUAN_LY_DANH_MUC.py` | 222 | Danh mục nhập liệu từ file `DANH_MUC/*.txt` và `*.json`; snapshot trong DB để khôi phục; kiểm tra digest khi ghi | `Catalogs` (`sync`, `read`, `save`, `editor_data`, `snapshot`) |
| `MAU_PHAN_CONG.py` | 78 | Bốn mẫu phân công (`team1`, `team2`, `team3`, `day`); kiểm tra; gộp người của mẫu vào tổ (trả bản sao) | `parse_templates`, `validate_templates`, `merge_team_members` |
| `MAY_CHU.py` | 495 | **Máy chủ HTTP nội bộ và toàn bộ API.** Kiểm Host/cookie/header, xả thân request từ chối có giới hạn, build metadata; xuất ZIP; lịch sao lưu | `Handler`, `make_server`, `daily_backup`, `int_param` |
| `BAO_CAO_EXCEL.py` | 130 | Tổng hợp tháng, bảng dữ liệu báo cáo; bộ xuất XLSX tối giản (dùng khi không có khuôn) | `aggregate`, `monthly_tables`, `report_table`, `xlsx_bytes`, `styled_xlsx` |
| `XUAT_EXCEL.py` | 304 | Xuất Excel **theo khuôn** `mau/MAU_BAO_CAO.xlsx`, giữ kiểu dáng; số dòng khuôn là hằng số | `Template`, `export_workbook`, `TemplateError` |
| `BAO_CAO_CA.py` | 139 | Điểm vào: mở phiên, kiểm tra bảo vệ dữ liệu, chạy máy chủ, xoay log; parser chung với launcher | `main`, `parse_args`, `running_session`, `rotate_log`, `show_error` |

Các file gốc chạy:
- `MO_BAO_CAO_CA.pyw`: mở app, ghi log vào `--data-dir` (mặc định `DU_LIEU/`), gọi `main(['--quiet'])` và truyền exit code.
- `KHOI_PHUC_DU_LIEU.pyw`: gọi `main(['--restore','--quiet'])`.
- `CHAY_KIEM_TRA_LOI.bat`: chạy `ma_nguon\BAO_CAO_CA.py` để xem lỗi trên console.

## 4. Khởi động và vòng đời phiên

1. `main()` đọc `DU_LIEU/PHIEN_DANG_CHAY.json`. Nếu máy chủ cũ còn chạy: cùng version thì mở lại trình duyệt rồi thoát; khác version thì báo lỗi "Thoát tool trên bản cũ".
2. Nếu `--restore`: hộp thoại chọn bản sao, xác nhận rồi khôi phục.
3. `Protection.guard_startup()`: DB trống hoặc thiếu nhưng có dấu vết dữ liệu cũ thì **không tạo DB trắng**, báo cần khôi phục. Trả kết quả kiểm tra đầy đủ cùng dấu DB/WAL/journal; nguồn đổi trong lúc kiểm tra thì chặn, riêng WAL tự tạo rỗng cho phép full lại một lần.
4. `needs_adoption(startup_check)`: dùng kết quả còn khớp để đối chiếu nguồn → hộp thoại "Tiếp nhận DB đang có" nếu khác (sao lưu trước khi đổi). Sau khôi phục/tiếp nhận, nạp cấu hình và kiểm tra lại.
5. `make_server(startup_check=...)`: thiếu hoặc dấu cũ thì guard đầy đủ như khi gọi trực tiếp; khóa phiên (`KHOA_DB_<hash>.lock`), mở `Store` (nâng schema, seed người/tàu một lần), `Protection.initialize(store)` dùng Store đã mở, `Catalogs.sync()`, sao lưu ban đầu đầy đủ. Trường hợp ổn định: nguồn full một lần và snapshot đích full một lần.
6. Ghi `PHIEN_DANG_CHAY.json` (port + token), mở `http://127.0.0.1:<port>/?launch=<token>`.
7. Thoát: nút "Thoát tool" → `/api/shutdown` → sao lưu bù → đóng server → xóa file phiên.

**Xác thực cục bộ:** token ngẫu nhiên trên URL chỉ dùng một lần ở `/?launch=`, sau đó cấp cookie `ca_session_<port>` (HttpOnly, SameSite=Strict). Mọi request kiểm `Host`; mọi POST cần header `X-Ca-Request: 1`, và nếu có header `Origin` thì phải đúng `http://127.0.0.1:<port>`. Không có đăng nhập người dùng: tên người nhập là tự khai.

## 5. Dữ liệu

### 5.1 Schema SQLite (`LUU_TRU.SCHEMA`, schema 3)

| Bảng | Nội dung |
|---|---|
| `meta` | `schema_version`, `database_id`, `*_seeded`, `review_copy` (1 = DB bổ sung), `reviewer_name`, `catalog_*` và `catalog_digest` (snapshot danh mục) |
| `reports` | `id = 'YYYY-MM-DD_DAY' \| 'YYYY-MM-DD_NIGHT'`, `version`, `status` (`draft`/`closed`), `payload` (JSON báo cáo) |
| `revisions` | Lịch sử: `(report_id, version)` duy nhất, kèm `reason` và `payload` đầy đủ của từng lần lưu |
| `correction_base` | Mốc đối chiếu khi bật bổ sung (`report_id`, `version`, `payload`) |
| `attachment_blobs` | Tệp gốc theo `hash` SHA-256, `mime`, `data` (BLOB) |
| `people`, `ships` | Danh sách nhân sự và tàu (`active`) |

### 5.2 Payload báo cáo (JSON trong `reports.payload`)

```text
date, shift(DAY|NIGHT), actor, status, notes,
ships[]                       (tàu cấp báo cáo, tùy chọn)
staffing[{role, people, ships?}]
jobs[{name, detail, xn, rtg, f20, f40, e20, e40, ships?}]
handover[{text, done}]
attachments[{hash, name, caption}]
```

Giới hạn: 200 dòng mỗi phần; 40 tệp mỗi ca; số lượng 0–9.999.999; chốt ca bắt buộc có `PHỤ TRÁCH CHUNG`.

### 5.3 Thư mục ngoài `DU_LIEU/` (đều được gitignore)

| Đường dẫn | Ý nghĩa |
|---|---|
| `DU_LIEU/BAO_CAO_CA.db` | DB chính |
| `DU_LIEU/SAO_LUU_AN_TOAN/<database_id>/` | Bản sao lưu tự động; giữ 10 bản hôm nay, bản cuối mỗi ngày trong 30 ngày, bản cuối mỗi tháng |
| `DU_LIEU/SAO_LUU_MANG_DI/` | Bản sao "Sao lưu mang đi" (`BAO_CAO_CA_*.db` hoặc `DB_BO_SUNG_*.db`) |
| `DU_LIEU/TRUOC_KHOI_PHUC/`, `TRUOC_TIEP_NHAN/`, `TRUOC_KHI_NHAP_BO_SUNG/` | DB cũ được giữ trước khi khôi phục, tiếp nhận hoặc nhập bổ sung |
| `DU_LIEU/DB_KIEM_TRA/` | DB đã tải lên để xem hoặc bổ sung |
| `DU_LIEU/XUAT_DINH_KEM/` | ZIP tạm khi tải tất cả tệp (xóa sau khi gửi) |
| `DU_LIEU/*.log` | Nhật ký; xoay vòng khi quá 1 MB, giữ 3 bản |
| `DANH_MUC/` | `NHAN_VIEN.txt`, `VI_TRI.txt`, `CONG_VIEC.txt`, `TO_NHAN_SU.json`, `MAU_PHAN_CONG.json`; `SAO_LUU/` giữ 20 bản |
| `BAO_VE_DB_<hash>.json` | Cấu hình bảo vệ (nơi dự phòng ngoài, `database_id`), nằm **cạnh** `DU_LIEU`. Không xóa |
| `KHOA_DB_<hash>.lock` | Khóa OS; tự nhả khi thoát, file còn lại là bình thường |

### 5.4 Luồng bổ sung (DB kiểm tra → DB chính)

1. Máy chính: "Sao lưu mang đi" → `DB_BO_SUNG_*` hoặc `BAO_CAO_CA_*`.
2. Máy kiểm tra mở file: `/api/open-viewer` (chỉ đọc).
3. Bật bổ sung: `/api/enable-corrections`, tạo `correction_base` và `review_copy=1`. Mỗi lần lưu phải có lý do.
4. Xuất DB bổ sung rồi đưa về máy chính.
5. Máy chính: `/api/corrections-preview` → chọn ca (`ready`) → `/api/corrections-apply`. Trước khi nhập: sao lưu `TRUOC_KHI_NHAP_BO_SUNG`; kiểm xung đột; giữ toàn bộ lịch sử `revisions`; kiểm sha256 của tệp đính kèm.

## 6. API HTTP (`MAY_CHU.Handler`)

Bảng dưới là danh sách nhanh. **Hợp đồng đầy đủ** (tham số, hình dạng phản hồi, mã lỗi, phạm vi chung/desktop/quản trị, điểm chưa nhất quán): [API.md](API.md), được ghim bằng `kiem_thu/KIEM_THU_API.py`.

**GET** (cần cookie; `context` là token đổi mỗi lần đổi nguồn DB, sai → 409):

- `/` (có `?launch=`), `/tai_nguyen/{bao_ve,ung_dung,danh_muc,phan_cong_mau}.js`, `/tai_nguyen/style.css`
- `/api/info`, `/api/protection`, `/api/catalogs` (chỉ DB chính)
- `/api/overview`, `/api/reports`, `/api/reports-page?limit&offset` (limit tối đa 200)
- `/api/report?id`, `/api/history?id`
- `/api/attachment?hash&context[&download=1]`, `/api/attachments-zip?id&context`
- `/api/export?id|from,to,shift,status,q&context`, `/api/export-month?month&context`

**POST** (cần header `X-Ca-Request: 1`):

- Bảo vệ dữ liệu: `/api/protection-directory`, `/api/protection-config`, `/api/protection-backup`, `/api/restore-preview`, `/api/restore` (cần `confirmation: "KHOI PHUC"`)
- Danh mục: `/api/catalogs-save`
- Báo cáo: `/api/save`, `/api/attachment-upload?id&version|name|actor|caption`, `/api/ships-add`
- Sao lưu: `/api/backup`, `/api/shutdown`
- Bản kiểm tra và bổ sung: `/api/open-viewer` (body là file DB), `/api/main-db`, `/api/enable-corrections`, `/api/corrections-preview` (body là file DB), `/api/corrections-apply`

## 7. Giao diện (`giao_dien/`)

- **`giao_dien.html`** (33 dòng): khung sidebar và các section `#home`, `#edit`, `#list`, `#summary`, modal và toast. Thứ tự nạp script: `bao_ve.js`, `ung_dung.js`, `phan_cong_mau.js`, `danh_muc.js` (đều `defer`). `danh_muc.js` gọi `go('home')` ở cuối.
- **`tai_nguyen/ung_dung.js`** (890 dòng, lõi giao diện):
  - Biến toàn cục: `info`, `report`, `page`, `dirty`, `saving`, `uploading`, `conflict`, `editTab`.
  - Điều hướng và trang chủ: `go`, `setPage`, `refreshInfo`, `renderHome`.
  - Mở ca: `newShift`, `beginShift`, `loadReport`.
  - Trang nhập ca 4 tab: `renderEditor`, `staffSection`, `jobsSection`, `notesSection`, `filesSection`, `tabBadges`.
  - Lưu: `touch` (tự lưu sau 1,6 s), `save`, `manualSave`, `closeShift`. Ctrl+S gọi `manualSave`.
  - Danh sách và tổng hợp: `loadList`, `loadSummary`, `agg`, `listPager`.
  - Đính kèm: `uploadAttachments`, `optimizePhoto` (thu nhỏ ảnh tùy chọn trên canvas, ≤ 2.560 px).
  - Xuất, in và bản sao: `exportReport`, `exportSummary`, `openMonthExport`, `preview`, `printReport`, `backup`, `readDB`, `previewImport`, `applyImport`, `exitTool`.
- **`tai_nguyen/phan_cong_mau.js`** (129 dòng): `planStaffing` (chế độ `replace` hoặc `append`), `previewStaffTemplate`, `confirmStaffPlan`, quản lý 4 mẫu (`manageStaffTemplates`, `saveStaffTemplates`).
- **`tai_nguyen/danh_muc.js`** (180 dòng): chọn người (`openStaffPicker`, `filterPeople`, `applyPeople`), chọn tàu (`chooseShips`, `applyShips`, `addShipFromPicker`), danh sách tàu, danh mục (`manageCatalogs`, `saveCatalogs`).
- **`tai_nguyen/bao_ve.js`** (30 dòng): bảng bảo vệ dữ liệu, sao lưu ngay, khôi phục (`openProtection`, `previewRestore`, `performRestore`).

## 8. Kiểm thử

Chạy: `cong_cu\CHAY_KIEM_THU.bat` (Python và, nếu có Node, các bộ JS).

- **Python — 154 test, 13 file** (đếm `def test_`): `KIEM_THU.py` 31, `KIEM_THU_API.py` 14 (hợp đồng API), `KIEM_THU_BAN_CHOT.py` 8, `KIEM_THU_BAO_VE.py` 23, `KIEM_THU_DANH_MUC.py` 6, `KIEM_THU_DUNG_LUONG.py` 5, `KIEM_THU_KHOI_DONG.py` 10, `KIEM_THU_MAU_CA.py` 13, `KIEM_THU_MA_NGUON.py` 4 (cú pháp, import thừa), `KIEM_THU_PHAN_CONG.py` 12, `KIEM_THU_PHAT_HANH.py` 9, `KIEM_THU_V1_9.py` 15, `KIEM_THU_XUAT_EXCEL.py` 4.
- **JavaScript — 5 bộ** (Node VM, không cần trình duyệt): `KIEM_THU_BAO_VE.js`, `KIEM_THU_GIAO_DIEN.js`, `KIEM_THU_MAU_CA.js`, `KIEM_THU_PHAN_CONG.js`, `KIEM_THU_V1_9.js`.
- **Kết quả 1.9.1 ngày 2026-11-06:** Python **154/154 OK, 3 lần liên tiếp**, JS **5/5 OK**, smoke launcher nguồn qua trên Windows. Chi tiết [BAO_CAO_CODEX_DOT1.md](BAO_CAO_CODEX_DOT1.md). Test dùng thư mục tạm, không chạm dữ liệu vận hành.
- **Công cụ đo:** `cong_cu/DO_HIEU_NANG.py` (không phải kiểm thử): tạo DB giả lập qua `Store.save` trong thư mục tạm, đo sao lưu, khởi động và độ trễ HTTP. Kế hoạch dùng số đo: `ROADMAP_SAU_V1_9.md`.
- **Công cụ phát hành:** `cong_cu/DONG_GOI.py` chặn Git bẩn/lỗi HEAD trước cài PyInstaller, tạo `PHIEN_BAN.json` trong thư mục tạm và nhúng vào EXE. `/api/info.build` là `{commit,built_at,version}`. `cong_cu/KIEM_THU_KHOI.py` thử launcher nguồn; EXE mới cần `--exe <path> --commit <hash> --version 1.9.1`. Launcher ghi log theo data-dir tạm; no-browser không mở hộp thoại lỗi.
- **Chưa kiểm thử:** EXE Windows, hộp thoại tkinter, mở file xuất trong Excel thật, DB nhiều GB, ảnh/PDF lớn, trình duyệt thật (ngoài bộ JS giả lập).

## 9. Bất biến và quy ước (đọc trước khi sửa)

1. Mọi ghi DB chính đi qua `Store.save` / `_save_report` (một transaction gồm báo cáo và revision). Không ghi DB chính từ DB bổ sung ngoài `apply_corrections`.
2. Báo cáo đã chốt: mỗi lần sửa phải có lý do. Không cho mở lại ca đã chốt bằng bản sửa.
3. Số lượng là **lượt công việc**, không phải số container duy nhất. Ghi rõ ở giao diện và Excel.
4. Schema vẫn là 3. Migration chỉ từ schema 1 và 2, luôn giữ bản gốc `_TRUOC_NANG_CAP_*.db`.
5. Không xóa `BAO_VE_DB_*.json` và `KHOA_DB_*.lock` trong thao tác mã nguồn.
6. Đổi bố cục `mau/MAU_BAO_CAO.xlsx` thì phải đổi các hằng số dòng trong `XUAT_EXCEL.py` (`HEADER_ROWS`, `STAFF_*`, `JOB_*`, `NOTE_*`, `FOOTER`).
7. Sau mọi thay đổi: tăng `VERSION` trong `THIET_LAP.py`, chạy `CHAY_KIEM_THU.bat`, cập nhật `tai_lieu/THAY_DOI_<phiên bản>.txt` và phần đầu `HUONG_DAN.txt`. Nếu dùng EXE thì build lại bằng `TAO_FILE_EXE.bat`.
8. Không chạy hai bản (ví dụ 1.8.2 và 1.9.0) trên cùng một DB.

## 10. Điểm cần lưu ý (ghi nhận khi quét, chưa sửa mã)

- **Đã sửa (2026-11-06):** chuỗi phiên bản cũ trong `LUU_TRU.py` và `MAY_CHU.py` (`server_version` lấy từ `VERSION`); tiêu đề mục "Nghiệp vụ đã có" trong `HUONG_DAN.txt` nay ghi rõ viết theo 1.8.
- **Khuôn Excel:** `XUAT_EXCEL.py` phụ thuộc số dòng cố định. Đổi file mẫu mà quên đổi hằng số thì xuất sai, dù đã có kiểm tra `TemplateError` cho dòng thiếu.
- **Đã sửa từ chối sớm (1.9.1):** xả tối đa 4 MiB/0,5 giây, thân lớn gửi/flush lỗi và đóng chiều ghi trước khi xả; test Windows 100 POST, 5 MiB và 100 GET có body qua. Xem giới hạn tại `API.md` mục 7.
- **`DU_LIEU/PHIEN_DANG_CHAY.json`** chứa token của phiên đang chạy. Không chia sẻ file này.
- **Khóa DB:** khi quét, đọc `KHOA_DB_*.lock` báo *Device or resource busy*, nên có thể app đang mở. Đây chỉ là quan sát, chưa xác minh.
