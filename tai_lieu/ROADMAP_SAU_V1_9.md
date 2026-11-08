# Roadmap sau 1.9.0 — Sổ báo cáo ca (bản 2)

- Bản 1: 2026-11-06, Claude, từ đánh giá độc lập góc nhìn kiến trúc doanh nghiệp trên commit `baebda2`.
- Bản 2: 2026-11-06, sửa theo [PHAN_BIEN_ROADMAP_SAU_V1_9.md](PHAN_BIEN_ROADMAP_SAU_V1_9.md) (Codex) và định hướng của chủ dự án về bản web.
- Bản 2.1: 2026-11-06, sau khi làm Đợt 0: cập nhật trạng thái, **sửa một nhận định sai của bản 1** (lỗi `month`, xem mục 2) và thêm một lỗi mới tìm ra khi viết kiểm thử API (D1-1).
- Bản 2.2: 2026-11-06, Codex điều phối/review, Terra 6.1 thực hiện D1-1…D1-3, Sol 6.1 Medium review phần khó và thực hiện D1-4. Kết quả/lệnh chạy: [BAO_CAO_CODEX_DOT1.md](BAO_CAO_CODEX_DOT1.md).
- Bản 2.3: 2026-11-06, chốt yêu cầu bản in (Trưởng ca = Phụ trách chung, chỗ ký ở trang cuối), thêm danh sách **việc Codex kiểm chứng V1–V8**, ghi chú chuyển project vào CVF-Workspace (mục 10). Phản hồi người dùng thật: tính sau vì đang là bản MVP / protocol.

Dùng file này làm cơ sở chia việc. Mỗi hạng mục có tiêu chí nghiệm thu; xong hạng mục nào thì đánh dấu và ghi số đo thật. Đợt 0 đã làm xong (chỉ thêm công cụ, tài liệu và kiểm thử; **chưa đổi mã trong `ma_nguon/` hay `giao_dien/`**).

## 1. Định hướng đã chốt với chủ dự án

**Hiện tại — 2026-11-08:** bản local **1.10.1/schema4** đã được nghiệm thu kỹ thuật nội bộ cho đợt bổ sung [FLEX](../docs/work_orders/WO_IMPORT_FLEX.md), kế thừa bản LOCAL 1.10.0 đã chốt. [Review độc lập](../docs/reviews/import-flex-20261108/final-review.json) xác nhận file nhân sự thực tế 63 người nhập được, 14 mã số được xử lý, nhập lại không trùng và mở lại giữ nguyên; thêm nút ×, bấm ngoài và Esc để đóng hộp thoại. EXE từ `563c4b83eb23`, SHA `72c30e35…cf45796f`, đã đặt tại `SO_BAO_CAO_CA_1_10_1.exe` cạnh thư mục dữ liệu; đóng bản cũ trước khi mở. Dọn thêm 44 hồ sơ trình duyệt thử, giải phóng khoảng 1,08 GB, giữ nguyên dữ liệu thật, file Excel và bản cũ. Chỉ kiểm thử tập trung và một luồng EXE mới; không chạy lại toàn bộ ma trận. Nghiệm thu máy bãi/vận hành và các số đo chi tiết V8 hoãn giữ nguyên; chưa triển khai web.

**Đợt bổ sung đã nghiệm thu kỹ thuật (2026-11-08):** [Đối chiếu tan-thuan-port và roadmap nhân sự](../docs/roadmaps/TAN_THUAN_PORT_ADOPTION.md). PNI E1–E6 nhập danh mục nhân sự Excel có xem trước được giao Terra/Sol, Astra review độc lập; phiên bản ứng viên1.9.2. Nguồn/kiểm thử191Python và6JS, build/smoke và luồng Chrome có giao diện trên Windows của EXE1.9.2 từ7ce0305b6000 đã được Astra nghiệm thu độc lập bằng dữ liệu giả lập; hộp chọn file Windows, Python3.9, in và nghiệm thu nghiệp vụ vẫn chưa thử. Tái sử dụng bộ chọn người và tổ/mẫu hiện có; tự phân tổ, định danh mã nhân viên và đồng bộ nằm ngoài đợt này. Đây là hồ sơ PNI lịch sử; trạng thái D2–D4 hiện tại theo nghiệm thu LOCAL ở trên. D5/web cần phạm vi riêng.

| Câu hỏi | Trả lời | Hệ quả cho roadmap |
|---|---|---|
| Có nhu cầu web thật không? | Có, vì thuận tiện | Bản web là đích đến; bản desktop là giai đoạn chuyển tiếp |
| Web nội bộ hay Internet? | **Internet** | Yêu cầu bảo mật, xác thực, HTTPS và phê duyệt vận hành cao hơn hẳn bản cục bộ |
| Số điểm nhập đồng thời? | 1–2, phân theo quyền đăng nhập | SQLite vẫn đủ; không cần đổi hệ quản trị dữ liệu |
| Cần chạy ngoại tuyến khi mất mạng? | Không | Luồng "DB mang đi / DB bổ sung" sẽ được thay bằng quyền sửa trực tuyến |
| K3, K4 (tách giao diện, danh tính/quyền)? | Hướng phát triển về sau | **Thiết kế chừa chỗ ngay**, chưa triển khai đầy đủ |

**Nguyên tắc rút ra:**

1. Bản desktop đang chứa dữ liệu thật, nên sửa an toàn dữ liệu và hiệu năng vẫn làm trước.
2. **Không mở rộng các luồng chỉ có ở desktop**: DB mang đi, DB bổ sung, chọn ổ dự phòng bằng tkinter, nút Thoát tool. Với các luồng này chỉ sửa an toàn.
3. Mọi thay đổi có chạm schema, API hoặc audit phải dùng được cho cả bản web, để tránh làm hai lần.

Các mục lịch sử phía dưới giữ nguyên bối cảnh và kết quả từng thời điểm; không dùng nhận định "chưa thử/chưa làm" cũ thay cho trạng thái LOCAL hiện hành. Với dữ liệu tổng hợp gần1,25GB, khởi động trên máy hiện tại từng ghi nhận74–123giây; không có cam kết tăng tốc. In PDF Chrome/Edge đã thử với A4 ngang, lề mặc định, nền tắt; in giấy và ổ dự phòng vật lý độc lập chưa nghiệm thu.

## 2. Phản hồi phản biện của Codex

| Mục | Kết luận | Ghi chú |
|---|---|---|
| PB-01: không dọn `DB_KIEM_TRA` theo tuổi tệp | **Đồng ý; lỗi của bản 1** | `enable_corrections` mở chính bản sao trong `DB_KIEM_TRA` ở chế độ ghi ([LUU_TRU.py:257](../ma_nguon/LUU_TRU.py#L257)). Điều kiện "trừ file đang mở" của bản 1 có thể làm mất phần bổ sung chưa xuất. Sửa ở mục D4-1. |
| PB-02: giữ bản đã kiểm tra đầy đủ | **Đồng ý** | Mức rủi ro thấp hơn mô tả, vì `prune` đã giữ bản cuối mỗi ngày trong 30 ngày ([BAO_VE_DU_LIEU.py:191-214](../ma_nguon/BAO_VE_DU_LIEU.py#L191-L214)). Tuy vậy, khi ứng dụng lâu không chạy hoặc full liên tục thất bại thì rủi ro là thật. Ghim bản full tốt chi phí thấp. Sửa ở mục D2-1. |
| PB-03: ngữ nghĩa tự lưu | **Đồng ý; lỗi thiết kế của bản 1** | Giao diện không gửi loại thao tác lưu ([ung_dung.js:467](../giao_dien/tai_nguyen/ung_dung.js#L467)). `normalize()` bỏ trường lạ, nên metadata nhét vào payload sẽ mất, và nếu giữ được thì làm sai phép so sánh trong `correction_plan()`. Chấp nhận nâng schema. Sửa ở mục D3-1. |
| PB-04: phép đo và ngưỡng | **Đồng ý một phần** | Rút lại ngưỡng "sao lưu ≤ 5 s" vì riêng `quick_check` đã mất 6,8 s. **Đính chính 1:** benchmark bản 1 ghi revision thẳng bằng SQL, không qua `Store.save`, nên 40 dòng/ca là có thật. Điểm yếu đúng là payload giống hệt nhau, không giống dữ liệu thật. **Đính chính 2:** 65,6 s đi đúng đường gọi của `main()`, trong đó `guard_startup` thật sự chạy hai lần; không cộng trùng số đo. Sửa ở mục D0-1. |
| PB-05: tách sửa `month` khỏi dọn blob | **Đồng ý phần dọn blob; phần `month` không còn đúng** | Dọn blob tách thành D4-2. Phần `month`: xem dòng "Tự sửa bản 1" ngay dưới. |
| **Tự sửa bản 1:** "thiếu `month` gây `KeyError` và 500" | **Sai, đã rút lại** | Bản 1 suy ra từ việc đọc [MAY_CHU.py:165-166](../ma_nguon/MAY_CHU.py#L165-L166) mà **không chạy thử**. Thực tế `monthly_tables` kiểm tra tháng ngay đầu hàm ([BAO_CAO_EXCEL.py:26-31](../ma_nguon/BAO_CAO_EXCEL.py#L26-L31)): thiếu hoặc sai `month` trả **400 có thông báo rõ**, đã đo và ghim trong `KIEM_THU_API.py`. Codex dựa vào nhận định này ở PB-05. Hạng mục sửa `month` bị bỏ. |
| PB-06: điều chỉnh kết luận | **Đồng ý** | Sửa ở mục 3. |
| Mục 4: chuẩn bị ranh giới cho web | **Đồng ý, có giới hạn** | K0 làm ngay; K1/K2 làm tại phần đang sửa; K3/K4 chừa chỗ trong thiết kế. Xem mục 5. |

## 3. Đánh giá hiện trạng (đã chỉnh)

- Nhận xét tham khảo, chưa có thang chấm chính thức: khá tốt nếu xem là công cụ cấp tổ/đội; chưa sẵn sàng làm dịch vụ Internet.
- Các vấn đề **quan sát được** tập trung ở hiệu năng và dung lượng khi dữ liệu tích lũy. **Chưa loại trừ** lỗi tính đúng đắn; kiểm thử hiện có không chứng minh điều đó.
- Điểm mạnh cần giữ: bảo toàn dữ liệu nhiều lớp, không tự tạo DB trắng, chống ghi đè bằng version, transaction báo cáo + revision, không phụ thuộc thư viện ngoài.
- Khoảng cách lớn nhất tới bản web: trạng thái nguồn dữ liệu (`store`, `context`, `pending_import`) đang **dùng chung toàn máy chủ** ([MAY_CHU.py:287](../ma_nguon/MAY_CHU.py#L287)). Máy chủ xử lý tuần tự, chưa có đăng nhập, và người nhập là tên tự khai.

### Số đo tham khảo (bản 1, chưa tái lập)

DB **giả lập** 1,15 GB (2.190 ca, 40 revision/ca ghi thẳng bằng SQL với **payload giống nhau**, 200 blob ~2 MB). Đo trên máy đánh giá, **chưa ghi nhận loại ổ đĩa**.

| Thao tác | Số đo |
|---|---:|
| Khởi động theo đường gọi của `main()` | 65,6 s (guard_startup 10,0 + needs_adoption 8,9 + make_server 46,6) |
| Một lần `Protection.backup` | 13,6 s |
| Mở `Store` (`quick_check`) | 6,8 s |
| Tìm kiếm toàn văn | 0,66 s |
| Bảng `revisions` | ~659 MB |

Chỉ dùng các số này để định hướng; chúng **không tái lập được** vì benchmark bản 1 ghi thẳng SQL với payload giống nhau.

### Số đo tái lập (D0-1, `cong_cu/DO_HIEU_NANG.py --profile vua`)

Máy: Windows 11, Python 3.11.9, 16 luồng, ổ chưa xác định loại. Dữ liệu qua `Store.save`: 240 ca × 20 lần lưu = 4.800 revision (4.800 payload khác nhau), 40 tệp × 2 MB; DB **125 MB**; không có dự phòng ngoài; lặp 3 lần.

| Thành phần | Lần 1 | Các lần sau |
|---|---:|---:|
| Chép DB bằng Backup API (không kiểm tra) | 0,57 s | 0,46 s |
| `quick_check` | 0,14 s | 0,12 s |
| `integrity_check` | 0,14 s | 0,12 s |
| Duyệt JSON (reports + revisions) | 0,45 s | 0,43 s |
| Hash SHA-256 mọi tệp đính kèm | 0,17 s | 0,19 s |
| `snapshot()` đầy đủ | 1,28 s | 1,70 s |
| `Protection.backup()` toàn bộ | 1,52 s | 1,86 s |
| **Khởi động** (guard 0,9 + needs_adoption 1,0 + make_server 2,7) | | **4,5 s** |
| **HTTP `/api/save` lưu thường** (sao lưu bị hoãn) | | 0,03 s |
| **HTTP `/api/save` chốt ca** (sao lưu ngay) | | **1,34 s** |
| Tìm kiếm toàn văn (230 ca khớp) | | 0,09 s |

Nhận xét ban đầu, **chưa phải kết luận** vì mới có một cỡ dữ liệu:

- Khởi động 4,5 s ở 125 MB, tỷ lệ phù hợp với 65,6 s ở 1,15 GB của bản 1 (DB lớn hơn ~9 lần, thời gian lớn hơn ~15 lần). Cần chạy `--profile lon` để xác nhận đường cong.
- **Chốt ca chặn giao diện ~1,3 s ở 125 MB**, vì API sao lưu rồi mới trả kết quả. Đây là con số người dùng thực sự cảm nhận; cần đo ở cỡ lớn và trên ổ bãi.
- Ở cỡ này `integrity_check` rẻ ngang `quick_check`; khoản đáng kể là chép DB và duyệt JSON. Điều này **chưa ủng hộ** giả định "bỏ `integrity_check` sẽ tiết kiệm nhiều" của D2-1; cần đo lại ở cỡ lớn trước khi chọn cách giảm kiểm tra.

## 4. Bất biến phải giữ

1. Mọi ghi báo cáo đi qua `Store.save` / `_save_report`, một transaction gồm báo cáo và revision.
2. Ca đã chốt: mỗi lần sửa có lý do, không mở lại bằng bản sửa.
3. Tiếp nhận và khôi phục DB **luôn kiểm tra đầy đủ**.
4. Không xóa `BAO_VE_DB_*.json`, `KHOA_DB_*.lock`; không tự tạo DB trắng.
5. Không xóa dữ liệu có thể là bản duy nhất (DB bổ sung chưa xuất, blob còn tham chiếu, bản full tốt gần nhất).
6. Nâng schema phải có migration, giữ bản sao trước nâng cấp và quy tắc tương thích rõ.
7. Thêm dependency ngoài cần quyết định ghi bằng văn bản (ADR).
8. Sau mỗi bản: tăng `VERSION`, chạy `cong_cu\CHAY_KIEM_THU.bat`, cập nhật `tai_lieu/THAY_DOI_<phiên bản>.txt` và đầu `HUONG_DAN.txt`, build lại EXE nếu dùng.

## 5. Ranh giới kiến trúc cho web (K0–K4)

Mục tiêu: **một kho mã, một ứng dụng**, chạy được ở hai chế độ (desktop hiện tại và web sau này) nhờ ranh giới rõ. Chưa tách dự án, chưa thêm framework frontend, giữ tên thư mục hiện tại.

```text
Trình duyệt: giao diện + API client
        |
HTTP adapter: đọc request, xác thực, kiểm quyền, ánh xạ lỗi
        |
Dịch vụ ứng dụng: lưu/chốt ca, sửa có lý do, xuất, sao lưu
        +-- NGHIEP_VU (quy tắc)   +-- LUU_TRU (Store, transaction)
        +-- Tác vụ nền tảng: tệp, bản sao, đồng hồ, danh tính người thực hiện
Khởi chạy desktop: trình duyệt, tkinter, khóa phiên, Thoát tool
Khởi chạy web (sau): cấu hình máy chủ, phiên người dùng, tác vụ nền
```

| ID | Phạm vi bây giờ | Chừa chỗ cho web | Nghiệm thu |
|---|---|---|---|
| **K0**: hợp đồng API | Viết `tai_lieu/API.md`: request/response, mã lỗi 400/403/404/409/500, `version` chống ghi đè, `context`, **loại thao tác lưu** (D3-1), upload/download. | Đánh dấu endpoint nào **chỉ dành cho desktop** (shutdown, protection-directory, open-viewer, corrections-*) và endpoint nào cần quyền quản trị. | Tài liệu khớp mã; có test hành vi cho `/api/save` và các lỗi 409. |
| **K1**: dịch vụ ứng dụng | Tách từ luồng đang sửa: `/api/save` (D3-1) và lịch sao lưu (D2-1). Handler chỉ đọc request và gọi dịch vụ. | Dịch vụ nhận **người thực hiện** và **nguồn dữ liệu** làm tham số, không đọc từ biến toàn cục. | Gọi được ca sử dụng trong test không cần HTTP; transaction giữ nguyên. |
| **K2**: tách phần desktop | Đường dẫn dữ liệu/tài nguyên vào cấu hình khởi tạo; tkinter, mở trình duyệt, khóa phiên chỉ ở lớp khởi chạy desktop. | Lớp khởi chạy web thay được mà không sửa dịch vụ. | Khởi chạy bằng thư mục tạm; dịch vụ không gọi hộp thoại. |
| **K3**: tách giao diện | **Chưa triển khai.** Khi chạm vào phần nào thì tách API client và logic thuần khỏi phần dựng DOM, bỏ dần `onclick` nội tuyến ở khu vực đó. | Mọi gọi máy chủ đi qua một API client, để sau này thêm xử lý hết phiên/đăng nhập ở một chỗ. | Luồng cũ qua kiểm thử; không mất nội dung đang nhập. |
| **K4**: danh tính và quyền | **Chưa triển khai đăng nhập.** Chừa cột danh tính trong schema 4 (D3-1) và trả về `capabilities` từ máy chủ thay vì giao diện tự suy ra từ chế độ. | Audit phân biệt *tên tự khai*, *tài khoản máy* (desktop) và *người dùng đã xác thực* (web). | Bản desktop chạy như cũ; giao diện bật/tắt nút theo `capabilities`. |

Không dựng sẵn hệ thống plugin, repository tổng quát cho mọi bảng hay đổi tên thư mục sang tiếng Anh.

## 6. Các đợt triển khai

Số phiên bản chỉ là **dự kiến**, chốt theo phạm vi và tương thích DB khi hoàn thiện thiết kế. Không gom tối ưu, gộp lịch sử, dọn dữ liệu và refactor vào một lần phát hành.

### Đợt 0: Chuẩn bị (chưa phát hành)

**Trạng thái Đợt 0 (2026-11-06):** D0-1 ✅ đã làm. D0-3 ✅ đã làm. D0-4 ✅ đã có (xem dưới). D0-2 ⏳ chờ máy bãi. Còn thiếu cho D0-1: chạy `--profile lon` để có số ở cỡ gần 1 GB.

**D0-1. Benchmark tái lập được**, đặt tại `cong_cu/DO_HIEU_NANG.py`, chỉ dùng thư mục tạm. ✅ Có ba cỡ (`nho`, `vua`, `lon`), tạo dữ liệu qua `Store.save`, đo tách từng thành phần, đo khởi động theo đường gọi của `main()`, đo độ trễ HTTP, in cấu hình máy và nhận `--disk-label`, `--external`, `--json`. Lệnh: `python cong_cu\DO_HIEU_NANG.py --profile vua --disk-label "SSD"`.
- Xuất cấu hình: CPU/ổ nếu biết, phiên bản Python, kích thước và phân bố dữ liệu, có bật dự phòng ngoài hay không, số lần lặp, lần đầu (cold) hay các lần sau (warm).
- Dữ liệu giả lập: payload **thay đổi giữa các revision**, tạo qua `Store.save` (đúng đường ghi thật); ghi rõ cỡ payload, số revision, số blob duy nhất.
- Đo tách: chép DB, `quick_check`, `integrity_check`, duyệt JSON, hash blob, chép ra ổ ngoài; khởi động theo đúng đường gọi của `main()`; **độ trễ từ bấm Lưu/Chốt đến khi có phản hồi** qua HTTP (vì API sao lưu trước khi trả kết quả).
- Nghiệm thu: chạy một lệnh ra bảng số đo; ghi kết quả vào mục 3.

**D0-2.** Đo trên máy bãi thật bằng bản sao DB thật. Thời gian tiếp cận máy bãi không tính trong ước lượng.

**D0-3. K0**: hợp đồng API. ✅ [API.md](API.md) và [kiem_thu/KIEM_THU_API.py](../kiem_thu/KIEM_THU_API.py) (11 kiểm thử, chạy ổn định 8/8 lần riêng và 3/3 lần trong toàn bộ 127 kiểm thử). Tài liệu đánh dấu phạm vi từng tuyến (chung, desktop, quản trị) và liệt kê 8 điểm chưa nhất quán ở mục 7.

**D0-4. Kiểm thử hiện trạng cho các luồng sẽ đổi.** ✅ Rà lại kiểm thử hiện có thì phần lớn đã được phủ, nên chỉ bổ sung phần thiếu:

| Luồng | Nơi đã kiểm thử |
|---|---|
| Lưu nội dung không đổi: không tăng version | `KIEM_THU_API.py` (mới) |
| Sai `version` (cũ, kiểu chuỗi, `null`) và sai/thiếu `context`: 409 | `KIEM_THU_API.py` (mới) |
| Hai cửa sổ cùng version: một bên bị 409 | `KIEM_THU.py` (`test_http_workflow_and_source_switch_protection`, `test_conflict_does_not_overwrite_and_whole_batch_rolls_back`) |
| Vòng xuất DB → bật bổ sung → sửa → nhập lại | `KIEM_THU.py` (`test_review_edit_...`, `test_merge_preserves_new_shifts_and_reviewer_history`) |
| Hình dạng phản hồi tệp đính kèm và lỗi thống nhất | `KIEM_THU_API.py` (mới) |

Chưa có test cho *lưu tay không đổi nội dung đóng mốc tự lưu*; test này thuộc D3-1 vì hành vi đó chỉ tồn tại sau khi thiết kế xong.

**Chốt đợt:** tái lập được số đo; thống nhất chính sách giữ bản (D2-1) và ngữ nghĩa lịch sử (D3-1) bằng văn bản trước khi code.

### Đợt 1: Bản vá ổn định (dự kiến 1.9.1)

Không giảm mức kiểm tra, không đổi schema.

**Hoàn tất mã nguồn 1.9.1 ngày 2026-11-06:** D1-1 ✅; D1-2 ✅; D1-3 ✅; D1-4 ✅ phần nguồn/cổng build, **EXE chưa build/nghiệm thu** vì cây Git bẩn. Sau tăng VERSION: **3 lượt liên tiếp 154/154 Python**, **5/5 bộ JS**, smoke launcher nguồn `python -O cong_cu/KIEM_THU_KHOI.py` qua trên Windows. Toàn bộ dữ liệu thử trong thư mục tạm. Chi tiết/số đo/lỗi lúc phát triển: báo cáo Đợt 1.

- **D1-1:** 10 lần full suite liên tiếp đều 129/129, 5 bộ JS qua. Xả tối đa 4 MiB/0,5 giây; thân lớn hoặc độ dài không hợp lệ được trả lỗi/đóng chiều ghi trước khi xả. Test 100 POST từ chối, 5 MiB, 100 GET có body và độ dài sai với thân thật đều qua.
- **D1-2:** dùng lại kết quả kiểm tra khi dấu DB/WAL/journal còn khớp; luôn kiểm tra lại sau khôi phục/tiếp nhận. Luồng main ổn định giảm từ 4 inspect/6 validate xuống 2 inspect/3 validate: DB nguồn full một lần và snapshot đích full một lần. Ngoại lệ cần thiết: SQLite tự tạo WAL rỗng khi đọc lần đầu thì full lại tối đa một lần, chỉ chấp nhận khi sau đó ổn định; các thay đổi khác báo dừng. Benchmark `--profile vua --repeat 3` cùng DB giả lập 125 MB: **3,1 s → 1,7 s** (khoảng 45%); đây là một mẫu startup cho mỗi lệnh, không phải thống kê nhiều lần khởi động.
- **D1-3:** kiểm tra trước bằng `ceil(1,2 × max(DB+WAL, page_count×page_size))`; thiếu tại máy giữ trạng thái đang chờ sao lưu, cảnh báo cụ thể; thiếu ngoài giữ bản tại máy và mốc ngoài cũ. Test mất ổ đích, đủ đúng ngưỡng/thiếu một byte, byte DB/bản cũ không đổi và thông báo API đều qua. Hệ số 20% là dự phòng, chưa bảo đảm dung lượng không bị tiến trình khác chiếm sau kiểm tra.
- **D1-4:** metadata `{commit,built_at,version}`, footer build, Git gate trước cài công cụ/build, metadata chỉ trong TEMP; launcher log đúng data-dir và trả exit code. Test nguồn/metadata/cổng Git qua, `DONG_GOI.py --check` trả 1 đúng cây bẩn. Script smoke EXE đã có, chưa chạy EXE 1.9.1; cần build từ cây sạch và truyền đúng `--commit` để nghiệm thu phần đóng gói.
- **Số đo cuối 1.9.1:** cùng lệnh/profile cho startup **2,8 s**; quick_check/chép DB/JSON cũng chậm hơn lượt trước, chưa xác định nguyên nhân biến động máy. Không cam kết mức giảm 45% cố định từ một lượt D1-2; báo cáo có cả hai bảng đo để đối chiếu.
- **Đối chiếu bổ sung luân phiên:** cùng DB giả lập 131.039.232 byte, ba cặp mã cũ từ HEAD/mã 1.9.1, gọi main thật nhưng mock riêng vòng phục vụ để tự thoát: trung vị **3,797 → 1,835 s (giảm 51,7%)**. Đây là đo tác động mã trên cùng điều kiện gần nhau, chưa phải số máy bãi/HDD. Chi tiết và thứ tự chạy trong báo cáo.

| ID | Việc | Nghiệm thu |
|---|---|---|
| D1-1 | **Từ chối sớm làm ngắt kết nối.** `do_POST` trả 403/400 trước khi đọc thân request (thiếu `X-Ca-Request`, sai `Origin`, hết phiên, thân quá lớn). Trên Windows, đóng kết nối còn dữ liệu chưa đọc có thể gửi RST, nên client nhận `ConnectionAbortedError` thay vì JSON lỗi ([MAY_CHU.py:190-204](../ma_nguon/MAY_CHU.py#L190-L204)). **Tái hiện:** làm bộ kiểm thử API chập chờn 2/6 lần chạy toàn bộ (thân chỉ ~300 byte); luôn xảy ra với thân 5 MB. **Ảnh hưởng thực tế:** khi phiên hết hạn (ví dụ khởi động lại ứng dụng) trình duyệt có thể báo lỗi mạng chung chung thay vì "Phiên làm việc hết hạn. Mở lại tool.", kể cả khi tự lưu. **Hướng sửa:** xả (đọc bỏ) phần thân đã khai báo, có trần, trước khi trả lỗi sớm; thân vượt trần thì trả lỗi rồi đóng chiều ghi và xả có giới hạn thời gian. Chốt phương án khi làm. | Test nhỏ: 100 lần POST bị từ chối sớm với thân vài trăm byte đều nhận đúng 403 JSON. Test lớn: thân 5 MB nhận 400 JSON. Bỏ chú thích "thân rỗng" trong `KIEM_THU_API.py` và dùng thân thật. |
| D1-2 | Bỏ kiểm tra **trùng lặp** khi khởi động: `guard_startup` chạy ở cả `main` lẫn `make_server`; `needs_adoption` gọi lại `inspect_db`. Mỗi DB chỉ kiểm tra đầy đủ **một lần** mỗi lần khởi động, giữ nguyên mức kiểm tra. | Khởi động nhanh hơn rõ so với D0-1; mọi test bảo vệ hiện có qua. |
| D1-3 | Kiểm tra dung lượng trống trước khi sao lưu (cần khoảng 1,2 × DB, chốt hệ số sau đo). Không đủ thì báo lỗi, không để bản dở làm đầy ổ. | Test giả lập ổ đầy: thông báo đúng, DB chính không đổi. |
| D1-4 | Truy vết phát hành: nhúng mã commit và ngày build vào `/api/info`; `TAO_FILE_EXE.bat` từ chối build khi cây làm việc có thay đổi chưa commit; kiểm thử khói EXE (`--no-browser`, gọi `/api/info`, thoát). CI Windows là tùy chọn, tùy chính sách kho. | EXE hiển thị đúng commit; kiểm thử khói qua. |

### Đợt giao diện (U): bản vá giao diện máy tính

Nguồn: [DANH_GIA_GIAO_DIEN_V1_9.md](DANH_GIA_GIAO_DIEN_V1_9.md) (đo và chạy thao tác thật trên Chrome, cỡ 1366×657). **Chỉ máy tính**; chủ dự án xác nhận không cần tối ưu cho điện thoại. Không đổi API, dữ liệu hay framework; chỉ sửa `ung_dung.js`, `style.css`, `giao_dien.html`. Có thể làm xen kẽ với Đợt 2 vì không chạm sao lưu.

| ID | Việc | Nghiệm thu |
|---|---|---|
| U1 | Gộp tiêu đề trang và thẻ thông tin ca thành một dải gọn; dải tab dính khi cuộn. Hiện ô nhập đầu tiên ở y = 704 px, ngoài vùng nhìn 657 px. | Đo lại ở 1366×657: ô nhập đầu tiên nằm trong vùng nhìn khi mở ca |
| U2 | Ô số lượng sai: đánh dấu đỏ tại ô, chặn dấu thập phân, Tổng chỉ cộng giá trị hợp lệ, thông báo nêu tên công việc và cột. | Test JS: gõ `1.5` thì ô có `aria-invalid`, Tổng không đổi, thông báo nêu đúng dòng và cột |
| U3 | Chốt ca: kiểm tra điều kiện **trước** khi hỏi xác nhận và chuyển tới tab/ô còn thiếu; sửa câu "Chốt Ca ngày ngày". | Test JS: thiếu PHỤ TRÁCH CHUNG thì không hiện hộp xác nhận, chuyển sang tab Nhân sự; câu hỏi không lặp chữ |
| U4 | Esc đóng hộp thoại; liên kết bỏ qua tới nội dung; phím tắt chuyển tab; hộp chọn tàu đưa con trỏ vào ô tìm. | Test JS: Esc đóng hộp; số lần Tab tới ô đầu tiên giảm rõ so với 22 |
| U7 | Bỏ chữ "Phiên bản 1.9.0" cố định trong `giao_dien.html`. | Không còn chuỗi phiên bản cố định trong HTML |
| U8 | Bản in: (a) ca thông thường (9 nhân sự, 6 công việc) vừa 1 trang; (b) dòng nhận diện ca, số trang "Trang x/y" và **ngày giờ in dạng `hh:mm dd/mm/yyyy`** ở lề mọi trang (lề trang CSS; JS gán biến lúc `beforeprint`, đã thử khả thi trên Chrome 156); (c) **một khối chỗ ký "Trưởng ca (Phụ trách chung)" ở trang cuối**, tên in sẵn lấy từ vị trí PHỤ TRÁCH CHUNG của báo cáo (nhiều người thì mỗi người một ô ký), không bị tách khỏi nội dung. Yêu cầu do chủ dự án chốt. | Xuất PDF ca mẫu: 1 trang, có chỗ ký; ca dài: mỗi trang có "ca/ngày · Trang x/y" và giờ in đúng giờ máy, chỗ ký chỉ ở trang cuối. Kiểm chứng ở hộp thoại in thật: xem V1 |
| U5 | Lịch sử sửa hiện khác biệt giữa hai phiên bản liền nhau. **Làm cùng Đợt 3.** | Ca đã chốt sửa 1 số liệu: lịch sử hiện đúng "trước → sau" |
| U6 | Giải quyết xung đột: thêm lựa chọn giữ ghi chú đã gõ sau khi tải lại. Ưu tiên thấp, làm khi chạm vào. | — |
| U9 | Danh sách tàu: thêm nút **Ẩn** từng tàu (hiện chỉ thêm được; tên tàu gõ sai trong báo cáo cũng tự vào danh sách và ở lại mãi). **Không đổi schema**: cột `ships.active` đã có. Cần một tuyến API mới. | Ẩn một tàu: biến khỏi hộp chọn, báo cáo cũ giữ tên; `API.md` và `KIEM_THU_API.py` cập nhật |
| U10 | Hộp thoại dài (mẫu phân công cao 1307 px trong vùng nhìn 591 px; danh mục, bảo vệ dữ liệu): tiêu đề và hàng nút dính khi cuộn. | Đo lại: nút Lưu luôn trong vùng nhìn ở cả ba hộp |
| U11 | So sánh bản bổ sung: tô nổi chỗ khác nhau, bỏ nút in/đóng dư thừa. **Làm cùng U5, chung một thành phần so sánh, cùng Đợt 3.** | Ca mẫu sửa 1 số liệu: hộp so sánh chỉ ra đúng chỗ đổi |
| U12 | Xem trước khôi phục: hiện "Chưa có báo cáo nào" thay cho "Từ đến" trống khi bản sao 0 ca. | Test JS cho bản sao 0 ca |
| U13 | Chữ giao diện xưng "anh" (3 chỗ) đổi sang cách nói trung tính. | Không còn "anh" trong chữ giao diện |
| U14 | Thông báo nổi đặt ở góc dưới, đóng bằng một lần bấm (hiện che các nút phía trên trong 4,5–10 giây). | Thông báo không che nút thao tác |

**Đã chốt (chủ dự án, 2026-11-06):** bản in có sẵn chỗ ký và ngày giờ in dạng `hh:mm dd/mm/yyyy`. **"Trưởng ca" chính là người giữ vị trí PHỤ TRÁCH CHUNG**, nên bản in có một khối ký "Trưởng ca (Phụ trách chung)", **chỉ ở trang cuối**. **Phản hồi người dùng thật: tính sau** (đang là bản MVP / protocol), nên thứ tự ưu tiên U1–U14 hiện là nhận định kỹ thuật và không chặn việc làm.

Phạm vi đánh giá đã phủ cả các màn hình phụ (tab Ảnh & biên bản, chọn tàu, danh sách tàu, mẫu phân công, bảo vệ dữ liệu, DB kiểm tra, đối chiếu bản bổ sung). Phần còn lại giao Codex kiểm chứng ở mục dưới.

#### Việc Codex kiểm chứng (V1–V8)

Đây là các phần **chưa được kiểm chứng** khi đánh giá giao diện ([DANH_GIA_GIAO_DIEN_V1_9.md](DANH_GIA_GIAO_DIEN_V1_9.md) mục 1). Chỉ **kiểm chứng và ghi nhận**, không sửa mã trong các việc này; chỗ nào phát hiện lỗi thì thêm hạng mục mới (U15 trở đi) vào tài liệu đánh giá. Quy tắc như [GIAO_VIEC_CODEX_DOT1.md](GIAO_VIEC_CODEX_DOT1.md) mục 0: chạy thật trên dữ liệu trong thư mục tạm, ghi lệnh và kết quả vào báo cáo, **không khẳng định điều chưa chạy được** (ghi "chưa kiểm chứng" và nêu lý do).

| ID | Việc kiểm chứng | Cách làm | Kết quả cần ghi lại |
|---|---|---|---|
| V1 | **In ở hộp thoại in thật** (Chrome và Edge trên Windows) | Mở Xem / In một ca mẫu, in bằng nút "In / Lưu PDF" và bằng Ctrl+P; thử "Headers and footers" bật/tắt và "Background graphics" tắt (mặc định). In ra máy in nếu có, hoặc "Microsoft Print to PDF" qua hộp thoại thật. Chạy một lần trên bản in hiện tại làm mốc, và một lần sau khi làm U8. | Đầu/chân trang tự thêm của trình duyệt (URL `127.0.0.1:cổng`, ngày, số trang) có xuất hiện và có chồng lên lề trang CSS không; khổ giấy, giờ in đúng `hh:mm dd/mm/yyyy`, chỗ ký ở trang cuối. Lưu ảnh chụp hoặc PDF. Nếu không điều khiển được hộp thoại in (không có phiên có giao diện) thì ghi rõ "chưa kiểm chứng", **không suy từ PDF tạo bằng script** |
| V2 | **"Nhập các ca đã chọn"** chạy đến cùng | Mở DB bổ sung bằng giao diện, chọn ca "Có thể nhập", bấm nhập | Ca vào DB chính; lịch sử của người kiểm tra giữ nguyên; có bản sao ở `TRUOC_KHI_NHAP_BO_SUNG`; ca "Xung đột" không bị ghi đè; thông báo kết quả đúng |
| V3 | **"Bật chỉnh sửa / bổ sung"** và **"Xuất DB đã bổ sung"** qua giao diện | Từ chế độ chỉ xem: bật chỉnh sửa (nhập tên), sửa 1 ca kèm lý do, xuất DB đã bổ sung (không tạo bằng mã) | Tệp tải về nhập lại được ở V2; thông báo và nút ở mỗi bước đúng |
| V4 | **"Sao lưu mang đi"** | Bấm ở menu Dữ liệu, tải tệp `.db`; thử cả DB cỡ `--profile vua` | Tên tệp; tệp mở được bằng "Mở DB kiểm tra"; thời gian chờ và giao diện có đứng không |
| V5 | **"Xuất Excel cả tháng"** | Mở hộp chọn tháng, thử tháng có ca, tháng không có ca, tháng có cả ca nháp | Tệp XLSX tải về và mở được (Excel thật nếu có; nếu không, kiểm cấu trúc bằng thư viện và ghi rõ); thông báo ở tháng không có ca |
| V6 | **"Tải tất cả tệp"** | Ca có tệp trùng tên, tên có ký tự đặc biệt, ca không có tệp | ZIP đúng số tệp, tên tệp, `GHI_CHU_DINH_KEM.txt`; thông báo khi ca không có tệp |
| V7 | **"Lấy việc chưa xong từ ca trước"** | Ca trước có việc chưa xong, không có, và ca đầu tiên; bấm hai lần | Hành vi từng trường hợp; có trùng việc khi bấm hai lần không; hộp xác nhận đúng |
| V8 | **Hiển thị khi dữ liệu lớn** | Dùng `cong_cu\DO_HIEU_NANG.py --profile lon` tạo dữ liệu; mở danh sách vài trăm báo cáo, tìm kiếm, tổng hợp một năm, tab Ảnh & biên bản với 40 tệp | Thời gian từ lúc bấm đến lúc hiện; phân trang và bộ lọc còn dùng được; giao diện có đứng không. Ghi số đo |

V1 phần "sau khi làm U8" phụ thuộc U8; V2–V8 làm được ngay. Kết quả ghi thành "Lượt 3" trong [DANH_GIA_GIAO_DIEN_V1_9.md](DANH_GIA_GIAO_DIEN_V1_9.md), kèm danh sách hạng mục U mới nếu có.

### Đợt 2: Tối ưu sao lưu (đặt lại phiên bản khi giao việc)

**D2-1. Kiểm tra theo bậc, có ghim bản full tốt** (sửa P1-1 theo PB-02).

Hai mức kiểm tra:
- `quick`: `quick_check`, khớp ngày/ca, JSON hợp lệ, và hash các blob **chưa có trong cache đã xác minh**.
- `full`: `integrity_check` cộng hash **lại toàn bộ** blob, không dùng cache.

| Thao tác | Mức kiểm tra |
|---|---|
| Tiếp nhận DB, khôi phục, xem trước khôi phục | **full**, luôn luôn |
| Sao lưu ngay (người dùng bấm) | **full** |
| Khởi động, chốt ca | quick; chuyển sang full nếu lần full thành công gần nhất đã quá hạn |
| Tự lưu, thêm tệp, sửa danh mục | quick (vẫn giới hạn 5 phút như hiện nay) |

Quy tắc:
- Thao tác bắt buộc full **được ưu tiên** hơn giới hạn lịch tự động.
- **Quá hạn** nghĩa là đã trôi qua ít nhất 24 giờ kể từ lần full thành công gần nhất, kể cả thời gian ứng dụng không chạy. Full được thực hiện ở lần khởi động hoặc thao tác kế tiếp; không có bộ hẹn giờ chạy khi ứng dụng đã tắt. Mốc thiếu, hỏng hoặc đồng hồ lùi buộc kiểm tra full.
- Ghi riêng **bản full tốt gần nhất** (tên, thời điểm, `database_id`) vào cấu hình bảo vệ. `prune` **không được xóa** bản này cho tới khi có bản full tốt mới thay thế.
- Full thất bại: không cập nhật mốc full, giữ bản tốt đã ghim, báo lỗi mức `error`, không gắn nhãn "đã kiểm tra đầy đủ" cho bản quick.
- Cache hash khóa theo `database_id`; xóa cache khi khôi phục hoặc tiếp nhận. Cache chỉ hỗ trợ quick; full luôn đọc lại mọi blob.
- Giao diện Bảo vệ dữ liệu hiển thị **lần full thành công gần nhất**.
- Làm cùng **K1** cho phần lịch sao lưu: tách quyết định mức kiểm tra khỏi handler HTTP. Đây cũng là nền cho tác vụ nền ở bản web.

**Nghiệm thu:**
- Tạo bản full tốt → làm hỏng một blob → tạo nhiều bản quick và chạy `prune` qua nhiều ngày giả lập: bản full tốt vẫn còn; full mới thất bại; trạng thái báo đúng.
- Test khởi động sau nhiều ngày không chạy, và test thay nguồn DB (cache bị xóa).
- Ngưỡng thời gian: đặt sau D0-1, theo **tỷ lệ cải thiện so với baseline và thời gian thực trên máy bãi**.

### Đợt 3: Lịch sử và schema 4 (dự kiến 1.10)

**D3-1. Loại thao tác lưu và gộp tự lưu** (sửa P1-2 theo PB-03). Gộp một lần nâng schema cho cả K4.

API: `/api/save` nhận `save_kind` thuộc `auto | manual | close | correction`. Máy chủ **kiểm tra lại theo trạng thái**, không tin giao diện: ca đã chốt thì không chấp nhận `auto`; DB bổ sung thì chỉ chấp nhận `correction`.

Schema 4: thêm vào `revisions`:
- `kind TEXT NOT NULL DEFAULT 'legacy'`
- `os_user TEXT` (desktop)
- `auth_user TEXT` (web, để trống ở bản desktop)

Migration dùng cơ chế sẵn có: giữ bản `_TRUOC_NANG_CAP_3_4.db` trước khi nâng. Revision cũ mang `kind='legacy'` và **không bao giờ bị gộp**.

Quy tắc gộp. Một lần lưu `auto` **thay thế** revision liền trước của cùng ca (cập nhật `payload`, `saved_at`, `version` = version mới của báo cáo) chỉ khi đủ **tất cả** các điều kiện:
- revision liền trước có `kind='auto'`;
- ca đang `draft`;
- cùng người nhập (`actor`) và cùng `os_user`/`auth_user`;
- không phải DB bổ sung.

Mọi trường hợp khác tạo revision mới.

Lưu tay khi nội dung không đổi: **không tăng version**, chỉ đổi `kind` của revision liền trước từ `auto` sang `manual`. Như vậy lần tự lưu kế tiếp không ghi đè mốc người dùng vừa chủ động lưu.

`reports.version` vẫn tăng mỗi lần lưu, phục vụ chống ghi đè. Cột `version` trong `revisions` vì vậy **có khoảng trống**; revision cuối luôn khớp `reports.version` và `reports.payload`.

Nhập bổ sung từ DB schema 3 vào DB chính schema 4: các revision nhập về mang `kind='correction'` và giữ `actor` gốc. `apply_corrections` dùng `version > base_version` nên khoảng trống không ảnh hưởng. Cần test riêng.

Tương thích: bản 1.9.x **từ chối** mở DB schema 4 (hành vi sẵn có với schema lạ). Ghi rõ trong hướng dẫn rằng mọi máy phải nâng cùng lúc.

**Chuỗi nghiệm thu cụ thể** (một ca, một người nhập):

| Thao tác | Revision sau thao tác |
|---|---|
| 10 lần tự lưu có thay đổi | v10 `auto` |
| Lưu tay có thay đổi | v10 `auto`, v11 `manual` |
| 5 lần tự lưu có thay đổi | …, v16 `auto` |
| Lưu tay không đổi nội dung | …, v16 đổi thành `manual` |
| 3 lần tự lưu có thay đổi | …, v19 `auto` |
| Đổi người nhập, tự lưu | …, v19 `auto`, v20 `auto` (không gộp vì khác người) |
| Chốt ca | …, v21 `close` |

Kết quả mong đợi là **6 dòng**: v10, v11, v16, v19, v20, v21.

**Test bổ sung:** hai cửa sổ cùng version (một bên nhận 409); xem lịch sử có khoảng trống version; xuất DB → bật bổ sung → sửa → nhập lại; mọi bản sửa sau chốt được giữ; migration 3→4 trên bản sao DB thật giữ đủ số báo cáo và revision.

**D3-2. Ghi `os_user` phía máy chủ** (`getpass.getuser()`), không nhận từ giao diện. Hiển thị trong Lịch sử sửa. Đây chỉ là dấu vết hỗ trợ: máy dùng chung một tài khoản Windows thì không phân biệt được người, và trên web cột này vô nghĩa (là tài khoản dịch vụ). Danh tính thật ở bản web là `auth_user`.

### Đợt 4: Bảo trì dữ liệu (dự kiến 1.10.x)

**D4-1. `DB_KIEM_TRA`** (sửa P1-3 theo PB-01).

| Loại tệp | Cách nhận biết | Xử lý |
|---|---|---|
| Bản chỉ xem | `review_copy` khác `1`, không phải nguồn của lần nhập đang chờ | Được tự dọn sau N ngày |
| Nguồn đối chiếu nhập (`corrections-preview`) | Là nguồn của `pending_import` hiện tại | Không dọn khi đang chờ; sau khi nhập xong mới được dọn |
| **Bản đã bật bổ sung** | `review_copy = 1` | **Không tự dọn.** Chỉ dọn khi người vận hành chủ động chọn, sau khi đã xuất bản có xác minh hoặc đã nhập về DB chính |

Không dựa vào tuổi tệp hay trạng thái đang mở để quyết định bản đã bật bổ sung.

Nghiệm thu: sửa bản bổ sung → thoát → giả lập quá hạn → khởi động lại: dữ liệu vẫn còn. Nguồn của lần nhập đang chờ không bị dọn.

Vì luồng này sẽ bị bỏ ở bản web, chỉ làm phần an toàn ở trên, không thêm tính năng.

**D4-2. Dọn blob không còn tham chiếu** (tách từ P1-4 theo PB-05).
- Tham chiếu tính từ `reports`, `revisions` và `correction_base`.
- Bảo vệ blob đang chờ gắn vào báo cáo: chỉ xét blob không tham chiếu và **quá ngưỡng tuổi**. Vì `INSERT OR IGNORE` giữ nguyên `uploaded_at` cũ khi tải lại cùng hash, cần cập nhật mốc này khi tải lại.
- Kiểm tra tham chiếu và xóa trong cùng một transaction `BEGIN IMMEDIATE`, sau một bản full đã xác minh.
- Chạy theo lệnh bảo trì, **không** tự chạy trong mỗi lần full.
- Xóa hàng chỉ giải phóng chỗ bên trong file; muốn trả dung lượng cho ổ đĩa phải `VACUUM`. Đó là thao tác bảo trì riêng, cần thời gian và chỗ trống khoảng bằng kích thước DB.

**D4-3.** Khôi phục thử định kỳ mỗi quý vào thư mục tạm; mục "Sự cố và cách xử lý" trong `HUONG_DAN.txt`.

### Đợt 5: Bản web Internet (dự kiến 2.0)

#### Cổng điều kiện trước khi code

| ID | Quyết định | Ghi chú |
|---|---|---|
| W0-1 | **Phê duyệt của đơn vị** cho việc đưa dữ liệu ca (có tên nhân sự, là dữ liệu cá nhân) lên Internet: nơi đặt máy chủ, ai quản trị, quy định bảo vệ dữ liệu cá nhân hiện hành | Không có phê duyệt thì không mở cổng ra Internet |
| W0-2 | **Nơi chạy**: máy chủ của đơn vị hay VPS/đám mây | Ảnh hưởng sao lưu ngoài, HTTPS, chi phí |
| W0-3 | **Mô hình truy cập**: khuyến nghị đặt ứng dụng sau một lớp xác thực có sẵn (VPN của đơn vị hoặc cổng truy cập zero-trust), rồi mới đến đăng nhập của ứng dụng | Với 1–2 người nhập, cách này giảm mạnh phần bảo mật phải tự viết. Ứng dụng vẫn cần danh tính và quyền riêng cho audit |
| W0-4 | **Máy chủ HTTP**: `http.server` của Python không dành cho môi trường Internet. Cần reverse proxy có TLS phía trước, và chọn máy chủ ứng dụng phù hợp | Đây là dependency mới, cần ADR theo bất biến 7 |

#### Phạm vi

1. **Bỏ trạng thái dùng chung:** `store`, `context`, `pending_import` gắn theo phiên người dùng, hoặc bỏ hẳn cùng luồng DB bổ sung.
2. **Đăng nhập và vai trò:**

   | Vai trò | Quyền |
   |---|---|
   | Người nhập | Tạo, lưu, chốt ca |
   | Người kiểm tra | Sửa ca đã chốt **có lý do**, thay cho luồng DB mang đi |
   | Người xem | Chỉ đọc |
   | Quản trị | Sao lưu, khôi phục, danh mục |

   Mật khẩu băm bằng `hashlib.scrypt`; cookie `Secure`, `HttpOnly`, `SameSite`; giới hạn số lần đăng nhập sai.
3. **Audit:** ghi `auth_user` (đã có cột từ D3-1). Lịch sử nhập từ desktop giữ nguyên người sửa gốc.
4. **Chức năng quản trị:**
   - Khôi phục cần chế độ bảo trì, chặn mọi phiên khác.
   - Bỏ nút Thoát tool; người thường không dừng được máy chủ.
   - Thư mục dự phòng cấu hình phía máy chủ, không chọn qua trình duyệt.
5. **Tác vụ dài:** sao lưu và full check chạy nền, có báo trạng thái; dùng lịch của D2-1. SQLite chạy chế độ WAL. Ghi vẫn tuần tự; kiểm tra 409 khi hai người sửa cùng ca.
6. **Tệp đính kèm:**
   - Hạn mức upload theo vai trò.
   - Cân nhắc tách blob ra kho tệp theo hash (P3-1 của bản 1). Việc này chỉ giải quyết phần ảnh, **không** giải quyết revision. Nếu làm thì cần manifest, kiểm tra, giữ phiên bản và gói khôi phục nhất quán với DB.
7. **Chuyển dữ liệu:** đưa DB desktop lên máy chủ bằng luồng tiếp nhận có kiểm tra full. Chạy song song một thời gian rồi mới dừng bản desktop.
8. **Vận hành:** HTTPS, nhật ký truy cập, sao lưu ra ngoài máy chủ, khôi phục thử, kiểm thử bằng trình duyệt thật với hai người dùng.

#### Nghiệm thu bản web

- Hai người thao tác độc lập không lẫn dữ liệu.
- Ghi đồng thời cùng ca thì một bên nhận 409.
- Người thường không khôi phục hay dừng được máy chủ.
- Truy cập không đăng nhập bị chặn.
- Khôi phục thử thành công.
- Kiểm tra bảo mật cơ bản trước khi mở Internet: quét cổng, thử đăng nhập sai nhiều lần, thử truy cập endpoint quản trị bằng vai trò thường.

Mốc dung lượng ~3 GB chỉ là **tín hiệu để đo lại**, không phải điều kiện đổi kiến trúc. Với 1–2 người nhập, SQLite được giữ trừ khi phép đo chứng minh ngược lại.

## 7. Việc không làm (có chủ đích)

- Không mở rộng luồng DB mang đi / DB bổ sung; ở bản web, luồng này được thay bằng vai trò người kiểm tra.
- Không thêm framework frontend; K3 làm dần theo phần được chạm.
- Không gộp lịch sử cũ đã có; gộp chỉ áp dụng cho revision mới từ schema 4.
- Không mở cổng ra LAN/Internet bằng cách đổi địa chỉ lắng nghe của bản hiện tại.
- Không tối ưu giao diện cho điện thoại (chủ dự án xác nhận 2026-11-06); mọi đánh giá giao diện chỉ xét màn hình máy tính.

## 8. Tóm tắt thứ tự

| Đợt | Nội dung | Điều kiện bắt đầu |
|---|---|---|
| 0 | D0-1…D0-4 (benchmark, K0, test hiện trạng) | Ngay |
| 1 (1.9.1) | D1-1…D1-4 (bản vá ổn định) | Có baseline |
| U (bản vá giao diện) | U1…U4, U7, U8, U10, U12…U14; U9 cần tuyến API mới; U5 và U11 đi cùng Đợt 3; U6 khi chạm vào | Yêu cầu bản in đã chốt; có thể xen kẽ Đợt 2 |
| 2 (phiên bản chưa chốt) | D2-1 + K1/K2 phần sao lưu | Chính sách giữ bản đã thống nhất |
| 3 (1.10) | D3-1, D3-2 + K1 phần lưu, K4 chừa cột | Ngữ nghĩa lịch sử đã thống nhất |
| 4 (1.10.x) | D4-1…D4-3 (bảo trì dữ liệu) | Sau đợt 3 |
| 5 (2.0) | Bản web Internet | W0-1…W0-4 có quyết định |

## 9. Giới hạn

Hiện tại (2026-11-08): bộ dữ liệu giả lập tạo qua Store.save đạt khoảng 1,25 GB; đã ghi số đo và cấu hình máy trong [bằng chứng LOCAL](../docs/reviews/local-completion-20261108/). Thời gian khởi động/kiểm tra full có thể kéo dài hàng chục giây; không có kết luận tăng tốc. Nghiệm thu giao diện trên bộ dữ liệu lớn và toàn bộ L1–L8 vẫn chờ review độc lập. Máy bãi khác được chủ dự án để nghiệm thu sau; dữ liệu thật và máy in vật lý chưa được kiểm chứng.

- **Giới hạn lịch sử đến 1.9.1:** Số đo bản 1 (1,15 GB) dùng payload giống nhau, không tái lập được bằng kịch bản đã lưu. Đợt 0 và Đợt 1 đã đo DB giả lập 125 MB có 4.800 payload khác nhau qua Store.save; loại ổ đĩa vẫn chưa xác định. Chưa đo trên máy bãi hoặc DB cỡ gần 1 GB.
- **Tình trạng lịch sử đến 1.9.1:** chưa chạy EXE Windows, hộp thoại tkinter, trình duyệt thật. Đợt PNI 1.9.2 và ứng viên 1.10.0 đã có bằng chứng EXE/Chrome có giao diện riêng; không dùng dòng lịch sử này làm kết luận hiện tại. Hộp thoại tkinter/Windows và máy in vật lý vẫn chưa được nghiệm thu.
- Chưa đọc các công cụ khác ở thư mục cha và dữ liệu thật trong `DU_LIEU/`.
- Các yêu cầu pháp lý về dữ liệu cá nhân ở W0-1 cần bộ phận phụ trách của đơn vị xác nhận; tài liệu này không phải ý kiến pháp lý.


## 10. Chuyển project vào CVF-Workspace

Chủ dự án dự định chuyển project vào `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace` để áp dụng chuẩn CVF. Đã thử và đọc mã để biết ảnh hưởng (2026-11-06):

| Hạng mục | Ảnh hưởng khi đổi đường dẫn | Đã kiểm chứng |
|---|---|---|
| Dữ liệu `DU_LIEU` (DB, bản sao lưu) | Đi theo thư mục; nếu chuyển cả thư mục thì nguyên vẹn | Thử chuyển một project giả có 2 ca: khởi động ở vị trí mới, đủ 2 ca, thấy lại 2 bản sao cũ |
| **Nơi dự phòng bên ngoài** | **Bị quên.** Tên `BAO_VE_DB_<mã>.json` và `KHOA_DB_<mã>.lock` lấy mã băm từ **đường dẫn tuyệt đối** của `DU_LIEU` ([BAO_VE_DU_LIEU.py](../ma_nguon/BAO_VE_DU_LIEU.py)). Đổi đường dẫn thì ứng dụng không thấy file cấu hình cũ, tạo file mới và báo "Chưa chọn nơi dự phòng bên ngoài" | Có: `external_directory` về rỗng, cảnh báo mức `info`, file cấu hình cũ còn nằm cạnh (vô hại, đừng xóa) |
| Git | `.git` đi theo thư mục dự án; `CVF-Workspace` không phải kho git ở gốc nên không lồng kho. Dự án hiện không có remote | Đã kiểm tra |
| EXE | `ROOT` lấy từ thư mục chứa EXE, không phụ thuộc đường dẫn cố định | Chỉ đọc mã, chưa chạy EXE ở vị trí mới |

**Việc cần làm sau khi chuyển:** mở "Bảo vệ dữ liệu / Khôi phục", chọn lại thư mục dự phòng bên ngoài và bấm "Lưu nơi dự phòng"; kiểm tra "Bên ngoài" có thời gian thành công mới.

**Hồ sơ lịch sử CVF ngày 2026-11-06 (được giữ để đối chiếu, đã có hồ sơ thay thế):** xem `.cvf/manifest.json`, `.cvf/policy.json`, `AGENTS.md` và handoff đang hoạt động. Core công khai được ghim `c4c8767ac8861854f40d466ba338ffd11eb9558e`; nguồn bổ sung operator-local có source commit rút gọn `f8175616c`, standard `project-development-application-standard` SHA-256 `d06b62387e015160a77658f333882a2a316d54ffd0421071354cf63a3730dd7a`. Profile bổ sung 1.4 và thiết lập local đã được review độc lập, nghiệm thu theo bốn tiêu chí WSA trong `docs/roadmaps/WORKSPACE_ACTIVATION.md`; bản lock/workflow cũ và các lần thất bại được giữ tại `docs/reviews/activation-history/`. Lệnh `python -B scripts/check_project_workspace.py --json` trả `COMPATIBLE_ASSESSED`, kiểm tra kích hoạt trả `CURRENT_ASSESSED` cho hồ sơ REVIEW đã chốt. Doctor Core cũ giữ nguyên chẩn đoán phiên bản đã review (FAIL 27/28 trên Git sạch, hoặc 26/28 khi hai hồ sơ mới vào phạm vi); lệnh của project đối chiếu riêng bằng nguồn bổ sung đã ghim và từ chối mọi lỗi khác. Sáu nhóm kiểm thử adapter đạt, gồm xác minh trên Git sạch tại commit đã lưu (bổ sung ngày 2026-11-07; xem `docs/reviews/workspace-activation-postcommit-review.md`). Đây là nghiệm thu thiết lập phát triển local; việc BUILD tiếp theo phải có action và receipt mới, còn nghiệm thu sản phẩm giữ nguyên các giới hạn ở mục 9.

**Tình trạng CVF hiện tại (2026-11-08):** Core được ghim `68a7446cc35b7f4bfd2e6ca4029d4ee389c8a5b6`, profile1.4, thực thi PINNED_CORE; nguồn bổ sung được xem xét riêng. Doctor của project trả `CORE_ASSESSED`: 29/29 kiểm tra gốc và bốn kiểm tra bootstrap với work order cụ thể đều đạt, không miễn trừ lỗi doctor cũ. Receipt chỉ ràng buộc đúng action đã được đánh giá. Các kiểm tra cơ học này không chứng minh điều khiển AI qua provider hoặc hosted CI. Hồ sơ hiện hành: [Core reconciliation](../docs/reviews/core-reconciliation/) và [LOCAL](../docs/reviews/local-completion-20261108/).

### Áp dụng quy tắc phát triển CVF

Baseline chung: kế thừa Core và policy của project; dùng các pha INTAKE → DESIGN → SPEC → WORK_ORDER → BUILD → REVIEW → FREEZE, bằng chứng theo phạm vi, review độc lập khi rủi ro cao, nghiệm thu nội bộ trước khi yêu cầu người dùng đánh giá. Chọn lại các dòng liên quan khi mở từng việc; giữ nguyên tiêu chí, kết quả và giới hạn đã ghi ở roadmap và báo cáo. Không xem kiểm tra tĩnh là bằng chứng CVF điều khiển hành vi AI.

| Nguồn / nguy cơ | Kiểm soát cụ thể, thời điểm và người chịu trách nhiệm | Bằng chứng / trạng thái |
|---|---|---|
| Mục 4: dữ liệu thật, transaction, DB bổ sung và bản full | Trước thay đổi lưu trữ, worker xác định bất biến và đường khôi phục; reviewer đối chiếu kiểm thử trên dữ liệu giả lập, không tự xóa bản có thể duy nhất. | Áp dụng theo từng work order; chưa nghiệm thu thay đổi mới. |
| Mục 4 và các đợt 2–4: schema, backup và hiệu năng | Khi sửa, worker ghi migration, bản sao trước nâng cấp, tương thích và số đo tái lập; reviewer kiểm tra phục hồi và giới hạn phép đo. | Các kết quả Đợt 0–1 giữ nguyên giá trị và giới hạn đã ghi; chưa chứng minh các đợt sau. |
| Mục 6, W0-1–W0-4: Internet và dữ liệu cá nhân | Orchestrator giữ cổng đưa lên Internet cho tới khi có quyết định/phê duyệt nghiệp vụ; nhóm phát triển kiểm thử phân quyền, cách ly phiên và khôi phục trước phát hành. | Các quyết định W0 còn mở; không suy diễn phê duyệt từ bootstrap. |
| Mục 9 và 10: sử dụng thực tế sau di chuyển | Khi nghiệm thu phiên bản, nhóm phát triển kiểm tra EXE, trình duyệt và luồng phù hợp; người vận hành chọn lại nơi dự phòng ngoài và kiểm tra thời gian thành công. | Chưa kiểm chứng EXE và nơi dự phòng ngoài sau chuyển; không đọc hoặc thay dữ liệu thật trong đợt bootstrap. |
| Kích hoạt workspace | Orchestrator dùng doctor của project, lập action và receipt có review trước BUILD hoặc dispatch mới; giữ pin và lịch sử. | Thiết lập local đã được review: COMPATIBLE_ASSESSED / CURRENT_ASSESSED cho hồ sơ REVIEW hiện tại; chưa có bằng chứng live. |

Mỗi việc tiếp theo ghi phạm vi, tiêu chí, owner, kết quả thực tế, phiên bản và phần còn lại trong hồ sơ hiện hữu; cập nhật bảng khi phạm vi hoặc rủi ro thay đổi.

**Bộ nhớ của trợ lý Claude không đi theo thư mục.** Bộ nhớ lưu theo **đường dẫn dự án**; đổi đường dẫn thì phiên mới bắt đầu với bộ nhớ trống. Các quyết định quan trọng đã nằm trong tài liệu của project (roadmap, `API.md`, đánh giá giao diện, `CATALOG_CAU_TRUC.md`), nên đi theo project.
