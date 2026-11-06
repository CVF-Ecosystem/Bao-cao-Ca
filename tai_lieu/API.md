# Hợp đồng API — Sổ báo cáo ca 1.9.1

Mô tả giao diện HTTP giữa `giao_dien/` và `ma_nguon/MAY_CHU.py`. Viết dựa trên mã nguồn và **đã đối chiếu bằng cách chạy máy chủ thật**; hành vi ghim lại trong [kiem_thu/KIEM_THU_API.py](../kiem_thu/KIEM_THU_API.py) (14 kiểm thử). Đây là tài liệu mô tả **hiện trạng**, không phải thiết kế mong muốn: những chỗ chưa nhất quán được ghi ở mục 7 để các đợt sau cân nhắc.

Cột **Phạm vi** dùng cho lộ trình bản web ([ROADMAP_SAU_V1_9.md](ROADMAP_SAU_V1_9.md), K0):

- **Chung**: giữ lại ở bản web.
- **Desktop**: chỉ có ý nghĩa khi máy chủ chạy trên máy người dùng; bản web sẽ bỏ hoặc thay thế.
- **Quản trị**: giữ lại ở bản web nhưng chỉ vai trò quản trị được gọi.

## 1. Quy ước chung

**Địa chỉ.** Máy chủ nghe `127.0.0.1:<cổng ngẫu nhiên>`. Mọi request phải có `Host: 127.0.0.1:<cổng>`, khác đi thì 403.

**Phiên.** Truy cập lần đầu bằng `GET /?launch=<token>`. Token đúng thì trả trang HTML và đặt cookie `ca_session_<cổng>=<token>; HttpOnly; SameSite=Strict; Path=/`. Mọi request sau phải mang cookie này, thiếu hoặc sai thì 403. Không có tài khoản người dùng: **tên người nhập là chuỗi tự khai** trong báo cáo.

**POST.** Bắt buộc header `X-Ca-Request: 1` (403 nếu thiếu). Nếu có header `Origin` thì phải bằng `http://127.0.0.1:<cổng>` (403 nếu khác). Nội dung là JSON, trừ các tuyến nhận tệp nhị phân. Giới hạn thân request:

| Loại | Giới hạn |
|---|---|
| JSON | 4 MB |
| `/api/attachment-upload` | 100 MB |
| `/api/open-viewer`, `/api/corrections-preview` | 8 GB |

Vượt giới hạn thì trả 400 JSON; `Content-Length` âm hoặc không phải số cũng trả 400 JSON. Khi từ chối trước khi đọc thân, máy chủ xả tối đa 4 MiB, với hạn chờ tổng 0,5 giây; thân lớn hơn được trả phản hồi và đóng chiều ghi trước khi xả. Giao diện đã kiểm tra 100 MB và 8 GB ở phía trình duyệt.

**Phương thức khác.** `PUT`, `DELETE`, `HEAD`... trả 501 theo định dạng thư viện chuẩn, không phải JSON (HEAD không có thân phản hồi). PUT/DELETE/HEAD xả thân có giới hạn; nếu Content-Length không hợp lệ thì trả 400 thay vì xử lý phương thức.

**Dạng lỗi.** Mọi lỗi của ứng dụng là JSON `{"error": "<thông báo tiếng Việt>"}`:

| Mã | Ý nghĩa |
|---|---|
| 400 | Dữ liệu sai: JSON hỏng, thiếu khóa, sai kiểu, vi phạm nghiệp vụ, tham số ngoài khoảng, vượt giới hạn thân request |
| 403 | Host/cookie/header/Origin không hợp lệ; DB chỉ xem không được ghi |
| 404 | Không có tuyến, không có báo cáo hoặc tệp |
| 409 | **Xung đột**: sai `context`, sai `version`, danh mục hoặc phiên đối chiếu đã đổi |
| 500 | Lỗi không lường trước (chi tiết ở `DU_LIEU/LOI_CHUONG_TRINH.log`) |
| 503 | SQLite báo `locked` |

Phía POST, `ValueError/KeyError/TypeError/AttributeError` được gộp thành 400 `Dữ liệu gửi lên không hợp lệ.`; `sqlite3.Error/OSError` thành 500 hoặc 503. Phía GET, ngoài lỗi ứng dụng, mọi ngoại lệ thành 500.

**Tiêu đề phản hồi.** `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer` và `Content-Security-Policy` (còn `unsafe-inline`).

**Thời gian.** Chuỗi ISO 8601 múi giờ +07, độ chính xác giây. `date` là `YYYY-MM-DD`. `shift` là `DAY` hoặc `NIGHT`. `id` báo cáo là `<date>_<shift>`.

## 2. Hai cơ chế chống ghi đè

**`version` (từng báo cáo).** Mỗi báo cáo có số phiên bản nguyên, tăng 1 mỗi lần nội dung thay đổi; báo cáo mới có version 0 trước lần lưu đầu. `POST /api/save` phải gửi đúng version hiện tại, **kiểu số nguyên** (chuỗi `"1"` hay `null` đều bị 409). Lưu nội dung giống hệt thì không tăng version và trả lại bản hiện có.

**`context` (cả nguồn dữ liệu).** Một token do máy chủ phát, lấy từ `GET /api/info`. Token **đổi khi nguồn dữ liệu đổi**: `open-viewer`, `main-db`, `enable-corrections`, `restore`. **Không đổi** sau mỗi lần lưu thường. Các tuyến có kèm `context` sai hoặc thiếu trả 409, để một cửa sổ cũ không ghi nhầm vào DB khác.

| Tuyến | `context` đặt ở |
|---|---|
| `/api/save`, `/api/ships-add`, `/api/backup`, `/api/catalogs-save`, `/api/enable-corrections`, nhóm bảo vệ dữ liệu | Thân JSON |
| `/api/attachment-upload` | Query |
| `/api/attachment`, `/api/attachments-zip`, `/api/export`, `/api/export-month` | Query |
| `/api/open-viewer`, `/api/main-db`, `/api/corrections-preview`, `/api/corrections-apply` | Không dùng (xem `nonce`, mục 5) |

## 3. Tuyến GET

| Tuyến | Tham số | Phản hồi | Phạm vi |
|---|---|---|---|
| `/` | `launch` (token, lần đầu) | HTML giao diện; đặt cookie | Chung |
| `/tai_nguyen/{bao_ve,ung_dung,danh_muc,phan_cong_mau}.js`, `/tai_nguyen/style.css` | | Tệp tĩnh | Chung |
| `/api/info` | | Xem 3.1 | Chung |
| `/api/overview` | | `{month_count, draft_count, recent[], current_status}` | Chung |
| `/api/reports` | `from,to,shift,status,q` | Mảng báo cáo (cả nội dung) | Chung |
| `/api/reports-page` | cùng trên + `limit` (1–200, mặc định 50), `offset` (0–10.000.000) | `{rows[], total, limit, offset}`; có `q` thì lọc trong bộ nhớ | Chung |
| `/api/report` | `id` | Một báo cáo; 404 nếu chưa có | Chung |
| `/api/history` | `id` | `[{version, saved_at, actor, reason, payload}]`, mới nhất trước | Chung |
| `/api/attachment` | `hash`(64 hex), `context`, `name?`, `download=1?` | Byte tệp. PNG/JPEG/WEBP hiển thị tại chỗ; loại khác luôn tải về | Chung |
| `/api/attachments-zip` | `id`, `context` | ZIP `DINH_KEM_<id>.zip` | Chung |
| `/api/export` | `id` **hoặc** `from,to,shift,status,q`; `context` | XLSX `BAO_CAO_CA.xlsx` | Chung |
| `/api/export-month` | `month` (`YYYY-MM`), `context` | XLSX `BAO_CAO_THANG_<month>.xlsx`; `month` thiếu hoặc sai là 400 | Chung |
| `/api/catalogs` | | Nội dung các tệp danh mục dạng văn bản + `digest`; chỉ khi đang ở DB chính | Quản trị |
| `/api/protection` | | Trạng thái bảo vệ dữ liệu, gồm danh sách bản sao | Quản trị |

### 3.1 `/api/info`

`suggestion{date,shift}`, `jobs[]`, `roles[]`, `people[]`, `teams[]`, `staff_templates`, `ships[]`, `catalog_warning`, `version`, `build{commit,built_at,version}`, `readonly`, `database`, `now`, **`context`**, `review`, `reviewer`, `backup_warning`, `backup_level` (`""`, `info` hoặc `error`).

Từ 1.9.1, `build.commit` là mã Git ngắn, `build.built_at` là thời điểm đóng gói UTC (ISO 8601), `build.version` khớp `version`. Chạy mã nguồn không có metadata dùng `{commit:"nguon",built_at:"",version:VERSION}`; EXE thiếu hoặc có metadata không hợp lệ dùng `commit:"khong-ro"`, ngày rỗng. Giao diện hiển thị mã build cạnh phiên bản.

Kiểm thử khói nguồn: `python cong_cu/KIEM_THU_KHOI.py`. Với EXE mới đã đóng gói: `python cong_cu/KIEM_THU_KHOI.py --exe <duong-dan-EXE> --commit <ma-Git-ngan> --version <phien-ban>`. Script mở launcher với `--no-browser`, thư mục dữ liệu và log tạm, kiểm tra API rồi gọi `/api/shutdown`; EXE phải là bản đã sửa launcher để log tuân theo `--data-dir`.

`readonly`, `review` và `reviewer` do **trạng thái toàn máy chủ** quyết định (mục 7). Giao diện hiện suy ra chức năng được dùng từ các trường này, chưa có trường `capabilities`.

## 4. Tuyến POST (JSON và tệp)

| Tuyến | Thân | Phản hồi | Lỗi đặc trưng | Phạm vi |
|---|---|---|---|---|
| `/api/save` | `{report, version:int, reason:str, context}` | Báo cáo đã lưu: các trường chuẩn hóa + `id, version, created_at, updated_at` | 400 sai dữ liệu hoặc ca chốt thiếu lý do hoặc mở lại ca chốt; 403 DB chỉ xem; 409 sai `version`/`context` | Chung |
| `/api/attachment-upload` | Byte tệp. Query: `context`, `name`, `actor` (không rỗng), tùy chọn `id`+`version`+`caption` | **Có `id`**: `{attachment{hash,name,caption}, report, added:bool}`. **Không có `id`**: `attachment{hash,name,caption}` | 400 tệp rỗng, quá 100 MB, thiếu `actor`, đủ 40 tệp; 409 sai `context`/`version` | Chung |
| `/api/ships-add` | `{name, context}` | `{ships:[...]}` toàn bộ danh sách | 403 DB chỉ xem | Chung |
| `/api/backup` | `{context}` | Tải về tệp `.db` (`BAO_CAO_CA_<stamp>_<hex>.db` hoặc `DB_BO_SUNG_...`) | | Desktop |
| `/api/catalogs-save` | `{context, text{people,roles,jobs,teams?,staff_templates?}, digest}`; `teams`, `staff_templates` bỏ qua thì giữ bản hiện có | Danh mục đã đọc lại (`people, roles, jobs, teams, staff_templates, digest`) | 409 `digest` lỗi thời; chỉ DB chính | Quản trị |
| `/api/shutdown` | `{}` | `{ok:true}` rồi máy chủ dừng | | Desktop |

Khi `id` có trong `attachment-upload` thì tệp được gắn vào báo cáo và **tạo một phiên bản mới** (lý do `Thêm tệp đính kèm: <tên>`); tệp trùng hash trong cùng ca thì `added:false`, không tăng version. Không có `id` thì chỉ lưu tệp, chờ lần lưu báo cáo sau.

## 5. Luồng DB mang đi và bổ sung (chỉ desktop)

Không dùng `context` làm khóa; trạng thái nằm trong **biến toàn máy chủ**.

| Tuyến | Thân | Phản hồi | Ghi chú |
|---|---|---|---|
| `/api/open-viewer` | Byte tệp DB (≤ 8 GB) | `{ok:true}` | Đổi nguồn dữ liệu và `context` của **mọi** cửa sổ |
| `/api/main-db` | `{}` | `{ok:true}` | Về DB chính; đổi `context` |
| `/api/enable-corrections` | `{context, reviewer}` | `{ok:true}` | Chỉ trên bản sao trong `DB_KIEM_TRA`; đổi `context` |
| `/api/corrections-preview` | Byte tệp DB | `{nonce, items[{id, state, date, shift, actor, current, incoming, base_version}]}` | `state` là `ready`, `same`, `missing` hoặc `conflict`; chỉ khi đang ở DB chính |
| `/api/corrections-apply` | `{nonce, selected:[id,...]}` | `{ok:true, count}` | 409 nếu `nonce` hoặc nguồn đã đổi; chỉ nhập được các ca `ready` |

## 6. Bảo vệ dữ liệu (quản trị; hai tuyến đầu là desktop)

Tất cả yêu cầu `context` đúng **và** đang ở DB chính, nếu không thì 409.

| Tuyến | Thân | Phản hồi |
|---|---|---|
| `/api/protection-directory` | `{context}` | `{directory}`. **Mở hộp thoại tkinter trên máy chủ**; chỉ có nghĩa khi máy chủ là máy người dùng |
| `/api/protection-config` | `{context, directory}` | Trạng thái bảo vệ. Đặt thư mục dự phòng ngoài, rồi sao lưu ngay |
| `/api/protection-backup` | `{context}` | Trạng thái bảo vệ. Sao lưu ngay |
| `/api/restore-preview` | `{context, id}` | `{database_id, reports, first_day, last_day, revisions, sha256}` |
| `/api/restore` | `{context, id, sha256, confirmation:"KHOI PHUC"}` | `{restored, preserved}`; thay DB chính, đổi `context` |

## 7. Điểm chưa nhất quán và hạn chế (đã quan sát)

Ghi lại để quyết định ở các đợt sau; không phải lỗi cần sửa ngay.

1. **Trạng thái dùng chung toàn máy chủ.** `store`, `context`, `pending_import` là biến chung của tiến trình. Một người mở DB kiểm tra sẽ đổi nguồn cho mọi cửa sổ. Phù hợp một người dùng, **không dùng được nguyên trạng cho nhiều người** (roadmap K1/K4, đợt 5).
2. **Khớp tuyến POST theo cả chuỗi truy vấn.** Các tuyến JSON so khớp `self.path`, nên `POST /api/save?x=1` trả 404; riêng `/api/attachment-upload` so khớp phần đường dẫn và nhận query. Được ghim trong kiểm thử.
3. **Từ chối sớm khi còn thân request (đã sửa trong 1.9.1, ROADMAP D1-1).** Máy chủ xả có giới hạn khi từ chối; với thân vượt 4 MiB, phản hồi được gửi và đóng chiều ghi trước khi xả. Kiểm thử Windows đã xác nhận trường hợp thân 5 MiB nhận JSON và các yêu cầu thân nhỏ bị từ chối nhận 403 JSON. Client gửi chậm hoặc không gửi đủ dữ liệu vẫn chịu giới hạn thời gian xả 0,5 giây.
4. **Gộp lỗi chương trình vào 400.** `KeyError/TypeError/AttributeError` trong xử lý POST đều thành `Dữ liệu gửi lên không hợp lệ.`, che khuất lỗi thật của máy chủ; chi tiết không vào nhật ký.
5. **Giả định máy chủ là máy người dùng.** `shutdown`, `protection-directory`, `open-viewer` (ghi file vào `DB_KIEM_TRA` trên đĩa máy chủ) và `backup` (tải file DB) đều ngầm coi người gọi là chủ máy.
6. **`context` không đổi khi lưu thường**, nên chỉ chống ghi nhầm khi đổi nguồn, không thay cho `version`.
7. **Chưa có trường `capabilities`** trong `/api/info`; giao diện tự suy ra quyền từ `readonly`/`review`.
8. **Chưa có phiên bản API** trong đường dẫn hay tiêu đề; thay đổi hợp đồng phải đi cùng thay đổi giao diện trong cùng bản phát hành.

## 8. Khi sửa API

1. Cập nhật tài liệu này và `kiem_thu/KIEM_THU_API.py` trong cùng thay đổi.
2. Tuyến mới ghi dữ liệu cần chọn rõ: dùng `context` hay `version`, phạm vi (chung, desktop, quản trị) và mã lỗi.
3. Giao diện gọi qua hàm `api()` trong `ung_dung.js` cho JSON; các lần tải lên/tải xuống dùng `fetch` riêng và cần tự xử lý lỗi theo bảng ở mục 1.
