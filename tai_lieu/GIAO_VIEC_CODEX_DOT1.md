# Giao việc cho Codex: Đợt 1, bản vá ổn định 1.9.1

Ngày giao: 2026-11-06. Người giao: Claude (theo yêu cầu của chủ dự án). Người thực hiện: Codex.

Đọc trước, theo thứ tự: [ROADMAP_SAU_V1_9.md](ROADMAP_SAU_V1_9.md) (mục 1, 4, 6 Đợt 1), [API.md](API.md), [CATALOG_CAU_TRUC.md](CATALOG_CAU_TRUC.md) mục 9 (bất biến). File này chỉ chốt phạm vi và cách làm; thiết kế nằm ở roadmap.

## 0. Quy tắc làm việc (bắt buộc)

1. **Chạy thử trước khi khẳng định.** Roadmap bản 1 từng kết luận sai về lỗi `month` vì chỉ đọc mã mà không chạy; Codex cũng đã dựa vào kết luận đó ở phản biện PB-05. Mọi nhận định "X xảy ra" trong báo cáo kết quả phải kèm lệnh hoặc test đã chạy. Nếu mô tả trong roadmap không khớp thực tế, **sửa roadmap và báo lại**, không làm theo mô tả sai.
2. **Không chạm dữ liệu thật.** Không đọc, ghi, di chuyển `DU_LIEU/`, `DANH_MUC/`, `BAO_VE_DB_*.json`, `KHOA_DB_*.lock`. Ứng dụng có thể đang chạy trên thư mục này. Mọi thử nghiệm dùng thư mục tạm.
3. **Không đổi schema DB, không đổi định dạng DB mang đi.** Đợt 1 là bản vá; schema 4 thuộc Đợt 3.
4. **Không giảm mức kiểm tra** của sao lưu, tiếp nhận hoặc khôi phục (D2-1 làm sau, và số đo ban đầu đang làm yếu giả định của nó).
5. **Không thêm thư viện ngoài.** Chỉ thư viện chuẩn Python 3.9+.
6. **Không commit, không push, không tạo PR** trừ khi chủ dự án yêu cầu. Cây làm việc hiện có file chưa commit (xem mục 5).
7. **Một hạng mục, một nhóm thay đổi rõ ràng**, chạy toàn bộ kiểm thử sau mỗi hạng mục, không dồn đến cuối.
8. Gặp điểm cần quyết định mà roadmap chưa chốt thì **dừng và hỏi chủ dự án**, không tự chọn rồi coi như đã được duyệt.

## 1. Phạm vi

| ID | Việc | Ưu tiên |
|---|---|---|
| D1-1 | Xả thân request trước khi từ chối sớm (lỗi ngắt kết nối trên Windows) | Làm đầu tiên |
| D1-2 | Bỏ kiểm tra trùng lặp khi khởi động | Sau D1-1 |
| D1-3 | Kiểm tra dung lượng trống trước khi sao lưu | Sau D1-2 |
| D1-4 | Truy vết phát hành (mã commit trong `/api/info`, chặn build khi cây bẩn, kiểm thử khói) | Cuối |

**Ngoài phạm vi, không làm:** gộp lịch sử tự lưu (Đợt 3), kiểm tra theo bậc và ghim bản full (Đợt 2), dọn `DB_KIEM_TRA` hay blob (Đợt 4), mọi thứ về web, đổi giao diện, CI (cần chủ dự án quyết định).

## 2. Chi tiết từng hạng mục

### D1-1. Xả thân request trước khi từ chối sớm

**Vấn đề đã tái hiện.** [MAY_CHU.py:190-204](../ma_nguon/MAY_CHU.py#L190-L204): `do_POST` kiểm tra cookie, `X-Ca-Request`, `Origin`, độ dài rồi mới đọc thân. Từ chối sớm xong là đóng kết nối khi còn dữ liệu chưa đọc; trên Windows có thể gửi RST và client nhận `ConnectionAbortedError` thay vì JSON lỗi.

- Thân ~300 byte bị từ chối vì thiếu header: bộ kiểm thử chập chờn khoảng 2/6 lần chạy toàn bộ.
- Thân 5 MB tới tuyến JSON: luôn bị ngắt kết nối thay vì nhận 400.

**Việc cần làm.**

1. Trước khi trả lỗi sớm, đọc bỏ (xả) phần thân đã khai báo trong `Content-Length`, **có trần** (đề xuất 4 MB, bằng giới hạn JSON). Không xả thân 100 MB hay 8 GB.
2. Thân vượt trần: trả lỗi JSON, đóng chiều ghi của socket rồi xả có giới hạn thời gian ngắn, để client nhận được phản hồi. Chốt phương án cụ thể sau khi thử; nếu phương án nào không giải quyết được, nói rõ.
3. `Content-Length` sai (âm, không phải số) cũng phải trả JSON lỗi, không ném ngoại lệ chung. Kiểm tra hiện trạng trước.
4. Áp dụng cả cho phía GET nếu có đường từ chối sớm tương tự (kiểm tra bằng thử, không đoán).

**Nghiệm thu.**

- Test: 100 lần POST bị từ chối sớm (thiếu `X-Ca-Request`, sai `Origin`, không cookie) với thân vài trăm byte, **đều** nhận 403 JSON, không lần nào ngắt kết nối.
- Test: thân 5 MB tới `/api/save` nhận 400 JSON có `error`.
- Chạy bộ test 10 lần liên tiếp, không chập chờn.
- Trong [KIEM_THU_API.py](../kiem_thu/KIEM_THU_API.py): **bỏ các chú thích và cách né "thân rỗng"** (ở `test_post_requires_header_origin_and_host` và `test_unknown_routes_and_methods`), dùng thân thật.
- Cập nhật [API.md](API.md) mục 1 và mục 7 điểm 3 (chuyển từ "lỗi" sang "đã sửa trong 1.9.1").

### D1-2. Bỏ kiểm tra trùng lặp khi khởi động

**Hiện trạng cần tự xác minh bằng đo, không tin mô tả.** Trên DB lớn, khởi động đã đo 65,6 s ở 1,15 GB (bản 1, không tái lập) và 4,5 s ở 125 MB. Các lần kiểm tra thấy trong mã:

- `main()` gọi `Protection.guard_startup()` (kiểm tra đầy đủ DB) và `needs_adoption()` (gọi lại `inspect_db`).
- `make_server()` gọi lại `guard_startup()`, rồi mở `Store` (`quick_check`), rồi `initialize()` (mở `Store` chỉ đọc, thêm một `quick_check`), rồi sao lưu đầu tiên (`snapshot` kiểm tra lần nữa).

**Việc cần làm.** Mỗi lần khởi động chỉ kiểm tra đầy đủ **một lần** cho mỗi DB, **giữ nguyên mức kiểm tra** đó. Gợi ý: để `main()` truyền kết quả hoặc cờ "đã kiểm tra" xuống `make_server()`; hoặc ngược lại. Lưu ý:

- `guard_startup` trong `main()` nằm trong khối bắt ngoại lệ để mở hộp thoại khôi phục (`recovery_dialog`); luồng đó **phải còn nguyên**.
- `make_server()` cũng được dùng trực tiếp trong kiểm thử và có thể được gọi mà không qua `main()`; hành vi an toàn khi gọi trực tiếp **không được yếu đi**.
- Không bỏ kiểm tra giữa hai thời điểm mà DB có thể bị thay (ví dụ sau hộp thoại tiếp nhận).

**Nghiệm thu.**

- Đo bằng `python cong_cu\DO_HIEU_NANG.py --profile vua --repeat 3` trước và sau, dán cả hai bảng vào báo cáo. Khởi động phải nhanh hơn rõ rệt; nếu không, nói rõ vì sao.
- Một test đếm số lần `inspect_db`/`quick_check` trong một lần khởi động (patch hoặc đếm gọi) và khẳng định đúng số mong muốn.
- Test cũ về khởi động, khôi phục, tiếp nhận DB đều qua; không sửa test cũ để cho qua (nếu buộc phải sửa, giải thích).

### D1-3. Kiểm tra dung lượng trống trước khi sao lưu

**Việc cần làm.** Trong `Protection.backup()` ([BAO_VE_DU_LIEU.py:216](../ma_nguon/BAO_VE_DU_LIEU.py#L216)), trước khi tạo snapshot, kiểm tra `shutil.disk_usage` của thư mục đích (cả máy lẫn nơi dự phòng ngoài). Cần ít nhất khoảng **1,2 × kích thước DB** (hệ số là điểm khởi đầu; đo lại bằng benchmark và ghi hệ số bạn chọn cùng lý do).

- Không đủ chỗ: báo `warning_level='error'` với thông báo tiếng Việt nói rõ ổ nào, cần bao nhiêu, còn bao nhiêu. **Không** tạo file dở, **không** làm hỏng các bản sao hiện có, **không** làm hỏng DB chính, **không** làm hàm ném ngoại lệ làm treo luồng lưu.
- Đường đi qua `daily_backup` ([MAY_CHU.py:355](../ma_nguon/MAY_CHU.py#L355)) đã bắt ngoại lệ chung; xác minh thông báo cuối cùng người dùng thấy có đúng nội dung.
- Với nơi dự phòng ngoài: thiếu chỗ ở ổ ngoài không được làm mất kết quả sao lưu tại máy đã thành công (giữ đúng hành vi hiện tại: máy thành công, ngoài thất bại, cảnh báo riêng).

**Nghiệm thu.** Test mô phỏng ổ đầy bằng cách patch `shutil.disk_usage`: thông báo đúng, không có file `.tmp` còn sót, DB chính nguyên byte, bản sao cũ còn nguyên, trạng thái `warning_level='error'`. Thêm một test cho ổ ngoài đầy trong khi ổ máy đủ.

### D1-4. Truy vết phát hành

**Việc cần làm.**

1. `TAO_FILE_EXE.bat` ([cong_cu/TAO_FILE_EXE.bat](../cong_cu/TAO_FILE_EXE.bat)): trước khi build, kiểm tra `git status --porcelain` rỗng; nếu có thay đổi chưa commit thì **từ chối build** với thông báo rõ. Sinh `PHIEN_BAN.json` (mã commit ngắn, ngày build, `VERSION`) và đóng gói cùng EXE qua `--add-data`.
2. `/api/info` thêm trường `build` đọc từ `PHIEN_BAN.json` nếu có (chạy từ mã nguồn thì ghi `"nguon"` hoặc rỗng). **Thêm trường là thay đổi tương thích**, nhưng cập nhật [API.md](API.md) mục 3.1 và test hợp đồng.
3. Hiển thị `build` ở chân giao diện cạnh số phiên bản (sửa nhỏ, theo cách giao diện đang hiển thị phiên bản).
4. Kiểm thử khói: một script (ví dụ `cong_cu/KIEM_THU_KHOI.py`) khởi chạy ứng dụng với `--no-browser --data-dir <thư mục tạm>`, gọi `/api/info`, kiểm tra `version` và `build`, rồi thoát bằng `/api/shutdown`. Chạy được cả từ mã nguồn lẫn từ EXE nếu truyền đường dẫn EXE.

**Hạn chế phải nói rõ trong báo cáo.** Nếu môi trường của Codex không phải Windows hoặc không có PyInstaller, **không được khẳng định đã build/chạy thử EXE**. Ghi "chưa chạy trên Windows" đúng như các bản trước vẫn làm.

**Nghiệm thu.** Chạy từ mã nguồn: kiểm thử khói qua. `TAO_FILE_EXE.bat` với cây bẩn: từ chối (thử bằng cách mô phỏng, không build thật nếu thiếu công cụ). Phần CI Windows **không làm** (chờ quyết định).

## 3. Hoàn tất bản 1.9.1

Sau khi cả bốn hạng mục xong (hoặc một số hạng mục được chủ dự án dừng lại):

1. Tăng `VERSION` trong [THIET_LAP.py](../ma_nguon/THIET_LAP.py) lên `1.9.1`. Lưu ý `running_session` từ chối khi tiến trình nền khác phiên bản; ghi chú này vào THAY_DOI.
2. Tạo `tai_lieu/THAY_DOI_V1_9_1.txt` theo phong cách các file THAY_DOI trước: **chỉ ghi điều đã làm và đã kiểm chứng**, ghi rõ điều chưa kiểm chứng.
3. Cập nhật phần đầu [HUONG_DAN.txt](../HUONG_DAN.txt) và các số kiểm thử trong HUONG_DAN và [CATALOG_CAU_TRUC.md](CATALOG_CAU_TRUC.md).
4. Cập nhật tiêu đề và các chỗ nhắc "1.9.0" trong [API.md](API.md) nếu hợp đồng đổi.
5. Cập nhật trạng thái trong [ROADMAP_SAU_V1_9.md](ROADMAP_SAU_V1_9.md) (đánh dấu ✅ kèm số đo thật; sửa mô tả nếu thực tế khác).
6. Chạy đầy đủ: `python -m unittest discover -s kiem_thu -t . -p "KIEM_THU*.py"` (**ít nhất 3 lần liên tiếp**) và cả 5 bộ `kiem_thu/KIEM_THU*.js` bằng Node.

## 4. Báo cáo kết quả (định dạng)

Trả lại cho chủ dự án một báo cáo ngắn gồm:

- Từng hạng mục: **đã làm / làm một phần / không làm**, và lý do.
- Số đo trước/sau của D1-2 (dán bảng từ benchmark).
- Kết quả kiểm thử: số lượng và số lần chạy, kể cả lần thất bại nếu có.
- **Điểm roadmap sai hoặc mô tả không khớp thực tế** mà bạn phát hiện.
- Việc chưa kiểm chứng (Windows, EXE, ổ HDD, trình duyệt thật).
- Quyết định đang chờ chủ dự án.

## 5. Trạng thái cây làm việc lúc giao

Các file sau **chưa được commit** (do Claude tạo hoặc Codex đã tạo trước đó), nằm trên nhánh `docs/catalog-and-version-cleanup`:

- `cong_cu/DO_HIEU_NANG.py`, `kiem_thu/KIEM_THU_API.py`
- `tai_lieu/API.md`, `tai_lieu/ROADMAP_SAU_V1_9.md`, `tai_lieu/PHAN_BIEN_ROADMAP_SAU_V1_9.md`, `tai_lieu/GIAO_VIEC_CODEX_DOT1.md`
- Sửa số kiểm thử trong `HUONG_DAN.txt` và `tai_lieu/CATALOG_CAU_TRUC.md`

Không dọn, không `git checkout`, không `git stash` các file này. Nếu cần tách thay đổi theo hạng mục, hỏi chủ dự án về việc commit trước.
