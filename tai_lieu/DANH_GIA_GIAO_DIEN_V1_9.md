# Đánh giá giao diện (máy tính) — Sổ báo cáo ca 1.9.x

Ngày: 2026-11-06. Người đánh giá: Claude. Phạm vi: **chỉ giao diện trên máy tính**, theo quyết định của chủ dự án (nhập và xem đều làm trên máy tính; không tối ưu cho điện thoại).

Kết luận ngắn: **không cần làm lại giao diện và không cần đổi framework.** Có 14 chỗ nên sửa (U1–U14), nặng nhất ở trang nhập ca và bản in. Kế hoạch triển khai: [ROADMAP_SAU_V1_9.md](ROADMAP_SAU_V1_9.md), mục "Đợt giao diện".

## 1. Cách đánh giá và giới hạn

- Chạy máy chủ thật trên thư mục tạm với dữ liệu mẫu (14 ngày × 2 ca, có ca nháp, ca chốt, ca thiếu phụ trách chung), điều khiển Chrome bằng Playwright ở cỡ **1366×657** (vùng trình duyệt trên màn hình 1366×768). Không đụng vào `DU_LIEU` thật, không sửa mã.
- Đã chạy thao tác thật: mở ca, đổi tab, mở hộp chọn người, gõ số sai, tạo xung đột hai cửa sổ, chốt ca thiếu phụ trách, xem lịch sử, xem tổng hợp, mở danh mục, tạo ca mới. Đã in thử bằng cách xuất PDF theo CSS in của ứng dụng (A4 ngang).
- **Lượt 2 (cùng ngày) đã đánh giá thêm:** tab "Ảnh & biên bản" (tải 3 tệp thật: ảnh PNG, PDF, tệp nhị phân), hộp chọn người và chọn tàu, danh sách tàu, trình sửa mẫu phân công, hộp Bảo vệ dữ liệu và xem trước khôi phục, mở DB kiểm tra (chế độ chỉ xem), đối chiếu và so sánh bản bổ sung (tạo bản bổ sung có 1 ca nhập được và 1 ca xung đột).
- **Vẫn chưa đánh giá:** bước "Nhập các ca đã chọn" chạy đến cùng; "Bật chỉnh sửa / bổ sung" và "Xuất DB đã bổ sung" qua giao diện (lượt 2 tạo bản bổ sung bằng mã); "Sao lưu mang đi"; hộp "Xuất Excel cả tháng"; "Tải tất cả tệp"; "Lấy việc chưa xong từ ca trước"; hiển thị khi dữ liệu rất lớn (hàng trăm báo cáo, 40 tệp trong một ca). **Đã giao Codex kiểm chứng: V2–V8 trong roadmap.**
- **Chưa lấy phản hồi người dùng thật: tính sau**, vì đang là bản MVP / protocol (chủ dự án quyết định 2026-11-06). Mức ưu tiên U1–U14 là nhận định kỹ thuật; khi có người dùng thật thì đối chiếu lại (bước nào mất thời gian nhất, chỗ nào hay nhập sai).
- **Chưa in ra máy in thật**, chưa xem phần đầu/chân trang mà trình duyệt tự thêm.

## 2. Điểm tốt nên giữ

- Bố cục và thứ bậc thông tin rõ; menu chia nhóm (Cài đặt, Dữ liệu) gọn.
- Trang nhập ca chia 4 tab, có số đếm ("Nhân sự 9", "Công việc 6") và dấu "!" khi thiếu thông tin bắt buộc.
- Thanh **Lưu nháp / Chốt ca** dính ở cuối màn hình, kèm trạng thái "Đã lưu lúc …".
- Hộp chọn người có ô tìm gõ có dấu hoặc không dấu và tích chọn rõ ràng.
- Áp dụng mẫu phân công phải qua bước xem trước và xác nhận.
- Xung đột hai cửa sổ: báo rõ nguyên nhân và **giữ nguyên chữ người dùng đang gõ** để sao chép.
- Danh sách báo cáo, tổng hợp, bộ lọc: rõ ràng, đủ dùng.
- Bản in: khổ A4 ngang đúng, menu và nút không lọt vào bản in, dấu tiếng Việt đúng, tiêu đề bảng lặp lại ở mỗi trang, không dòng nào bị cắt đôi, ảnh in kèm chú thích. Tắt "in màu nền" (mặc định của trình duyệt) vẫn đọc tốt nhờ có viền bảng.
- Tab "Ảnh & biên bản": thẻ tệp rõ ràng (xem trước ảnh, ô chú thích, Tải tệp, Gỡ khỏi ca có xác nhận); tải 3 tệp (PNG, PDF, tệp nhị phân) lưu ngay, báo "Đã lưu 3 tệp vào báo cáo, không cần bấm lưu thêm"; tùy chọn thu nhỏ ảnh mặc định tắt, lời giải thích thận trọng ("ảnh/biên bản cần giữ làm bằng chứng nên để nguyên").
- Hộp chọn tàu: có ô tìm, nút chọn một tàu, hướng dẫn "một dòng = một tàu"; từ chối chọn tàu ở dòng không phải TALLY TÀU/XUẤT TÀU kèm thông báo rõ.
- Hộp Bảo vệ dữ liệu: nêu rõ cảnh báo chưa có nơi dự phòng ngoài, thời điểm sao lưu tại máy / bên ngoài; khôi phục bắt buộc gõ `KHOI PHUC` và nói rõ DB cũ được giữ ở đâu.
- Chế độ DB kiểm tra: biểu ngữ "Đang xem bản sao DB" kèm hai nút rõ ràng, nút lưu bị vô hiệu, huy hiệu "CHỈ XEM · DB KIỂM TRA".
- Đối chiếu bản bổ sung: bảng chọn từng ca với trạng thái "Có thể nhập" / "Xung đột · không tự ghi đè"; ca xung đột không được chọn sẵn.

## 3. Các chỗ nên sửa

Ưu tiên: **Cao** = gặp mỗi ca; **TB** = tiện hơn, chi phí thấp; **Thấp** = hiếm gặp hoặc chỉ là tinh chỉnh.

### U1 — Vùng làm việc của trang nhập ca quá hẹp (Cao)

Đo ở cỡ 1366×657: dải tab bắt đầu ở y = 357 px, thanh Lưu nháp / Chốt ca dính ở y = 586 px, còn **ô nhập đầu tiên nằm ở y = 704 px, ngoài màn hình**. Mở ca ra chưa thấy ô nhập nào; vùng cuộn thực tế chỉ còn khoảng 230 px. Nguyên nhân: tiêu đề trang cộng thẻ thông tin ca chiếm hơn nửa chiều cao.

Hướng sửa: gộp tiêu đề trang và thẻ thông tin ca thành một dải gọn (ngày/ca, trạng thái, người nhập, các nút Lịch sử / Xem-In / Xuất Excel), và cho dải tab dính khi cuộn. Ước tính lấy lại khoảng 200 px, **cần đo lại sau khi sửa**.

Lượt 2 xác nhận vấn đề lan sang mọi tab: ở tab "Ảnh & biên bản", sau khi tải 3 tệp chỉ thấy một vệt nhỏ của ảnh đầu tiên sát mép dưới (y ≈ 620 px); phải cuộn mới thấy các thẻ tệp.

### U2 — Ô số sai không được chỉ ra và làm báo cáo không lưu được (Cao)

Gõ `1.5` vào ô F20: máy chủ từ chối ("Số lượng phải là số nguyên từ 0 đến 9.999.999"), thanh trạng thái báo "Chưa lưu: …" nhưng **ô sai không được đánh dấu** (không có lớp lỗi hay `aria-invalid`) và thông báo không nói rõ công việc nào, cột nào. Trong lúc đó dòng Tổng vẫn hiện **26,5**: giao diện cộng cả số lẻ mà máy chủ không chấp nhận.

Hướng sửa: đánh dấu đỏ ngay tại ô; ngăn gõ dấu thập phân ở ô số lượng; dòng Tổng chỉ cộng giá trị hợp lệ; thông báo nêu tên công việc và cột (ví dụ "Dòng 'TRẢI LÓT PHÁO', cột F20: cần số nguyên").

### U3 — Chốt ca hỏi xác nhận trước khi kiểm tra, và câu hỏi bị lặp chữ (Cao)

Chốt ca thiếu PHỤ TRÁCH CHUNG: ứng dụng hỏi "Chốt Ca ngày ngày 06/11/2026?", người dùng bấm đồng ý rồi mới nhận lỗi "Điền PHỤ TRÁCH CHUNG trước khi chốt ca". Lỗi lặp chữ do ghép `shiftName()` (đã có chữ "Ca ngày") với chuỗi ' ngày ' ([ung_dung.js:506](../giao_dien/tai_nguyen/ung_dung.js#L506)). Điểm tốt: tab Nhân sự đã hiện dấu "!".

Hướng sửa: kiểm tra điều kiện chốt **trước** khi hỏi; nếu thiếu thì chuyển thẳng sang tab Nhân sự và đưa con trỏ tới ô còn thiếu; sửa câu hỏi thành "Chốt ca ngày 06/11/2026?".

### U4 — Thao tác bàn phím còn thiếu (TB)

- Phím **Esc không đóng** hộp thoại (đo: hộp vẫn mở sau khi bấm Esc).
- Phải bấm Tab **22 lần** mới tới ô nhân sự đầu tiên từ đầu trang.
- Chỉ có một phím tắt (Ctrl+S); chưa có phím chuyển tab.
- Hộp chọn tàu không đưa con trỏ vào ô tìm khi mở (đo: tiêu điểm vẫn ở thân trang), trong khi hộp chọn người thì có.

Hướng sửa: Esc đóng hộp thoại (trừ khi đang lưu), thêm liên kết "bỏ qua tới nội dung", phím tắt chuyển tab (ví dụ Alt+1…4).

### U5 — Lịch sử sửa không cho thấy đã sửa gì (TB)

Màn hình chỉ có danh sách phiên bản, người lưu, lý do và nút "Xem nội dung" cho từng bản. Với ca đã chốt bị sửa kèm lý do, người kiểm tra phải mở hai bản và so bằng mắt. Nên hiện **khác biệt giữa hai phiên bản liền nhau** (ví dụ "F20 dòng TRẢI LÓT PHÁO: 25 → 28"). Hợp với Đợt 3 vì bảng lịch sử thay đổi ở đó, và có ích cho kiểm tra khi lên web.

### U6 — Chỉ có một cách giải quyết xung đột (Thấp)

Khi hai cửa sổ cùng sửa một ca, giao diện báo rõ và giữ chữ đang gõ, nhưng chỉ có nút "Tải lại báo cáo" (bỏ phần đang gõ). Có thể thêm lựa chọn giữ lại ghi chú đã gõ sau khi tải lại. Với 1–2 người nhập thì hiếm gặp.

### U7 — Chữ phiên bản cố định trong HTML (Thấp)

[giao_dien.html](../giao_dien/giao_dien.html) còn chữ "Phiên bản 1.9.0" cố định, JS thay bằng phiên bản thật sau khi tải thông tin. Với bản 1.9.1 sẽ hiện sai một thoáng, và hiện sai hẳn nếu JS lỗi. Nên để trống chữ mặc định.

### U8 — Bản in (ba việc, TB)

**U8a. Ca nhỏ tràn sang 2 trang.** Ca 9 nhân sự và 6 công việc in ra 2 trang; trang 2 chỉ còn 1 dòng công việc, dòng Tổng và phần ghi chú. Khối tiêu đề chiếm khoảng 25% chiều cao trang và các dòng bảng khá cao. Mục tiêu: ca thông thường vừa **1 tờ** bằng cách thu gọn tiêu đề và giảm khoảng cách dòng khi in.

**U8b. Từ trang 2 trở đi không có gì cho biết đây là ca nào.** Ca dài (24 dòng nhân sự, 30 công việc) in 5 trang; các trang sau chỉ có tiêu đề bảng, không có ngày/ca, không có số trang. Mục tiêu: dòng nhỏ lặp ở mỗi trang, ví dụ "Báo cáo ca đêm 06/11/2026 · Trang 2/5".

**U8c. Chỗ ký tên và ngày giờ in (yêu cầu đã chốt, chủ dự án 2026-11-06).** Bản in phải có sẵn **chỗ ký**, và in **ngày giờ in theo dạng `hh:mm dd/mm/yyyy`** (24 giờ, ví dụ `22:50 06/11/2026`). Chủ dự án xác nhận **Trưởng ca chính là người giữ vị trí PHỤ TRÁCH CHUNG**: bản in có **một khối ký "Trưởng ca (Phụ trách chung)" chỉ ở trang cuối**, tên in sẵn lấy từ vị trí PHỤ TRÁCH CHUNG của báo cáo (nhiều người ở vị trí này thì mỗi người một ô ký).

Cách làm đã thử khả thi trên Chrome 156 bằng PDF: dùng lề trang của CSS (`@page` với `@top-left`, `@bottom-left`, `@bottom-right`).
- Số trang tự động: `"Trang " counter(page) "/" counter(pages)` hiện đúng ("Trang 2/4").
- Ngày giờ in và dòng nhận diện ca: JS gán biến CSS trong sự kiện `beforeprint`, lề trang đọc `var(--in-luc)` và `var(--ca)`. Đã thử: kết quả đúng giờ máy lúc in, đúng định dạng yêu cầu, lặp ở **mọi trang**. Gán lúc `beforeprint` (không gán lúc mở bản xem trước) để Ctrl+P cũng ra giờ thật.
- Khối chữ ký đặt ở cuối báo cáo, không bị tách rời khỏi nội dung (`break-inside: avoid`).
- **Chưa kiểm chứng:** hộp thoại in thật. Chrome/Edge mặc định tự thêm đầu/chân trang riêng (URL, ngày); chưa biết có chồng lên lề trang của ứng dụng không. Cũng chưa thử trên phiên bản trình duyệt cũ hơn (lề trang cần trình duyệt Chrome/Edge đủ mới). **Đã giao Codex kiểm chứng: V1 trong roadmap.**

**Đã chốt, không còn câu hỏi mở:** Trưởng ca = Phụ trách chung; chỗ ký chỉ ở trang cuối. Còn lại là việc kiểm chứng ở hộp thoại in thật (V1 trong roadmap).

### U9 — Danh sách tàu chỉ thêm được, không sửa hay ẩn được (TB)

Hộp "Danh sách tàu" chỉ có ô "Tên tàu mới" và nút "Thêm tàu". Trong mã không có thao tác ẩn, xóa hay đổi tên tàu. Đồng thời mọi tên tàu xuất hiện trong báo cáo đã lưu đều **tự được thêm vào danh sách** ([LUU_TRU.py:154](../ma_nguon/LUU_TRU.py#L154), và khi nhập bổ sung ở dòng 317). Một lần gõ sai tên tàu sẽ nằm trong danh sách mãi, và danh sách chỉ dài thêm. Danh sách mẫu đã có sẵn dạng gần trùng ("BIEN DONG STAR" và "BIENDONG NAVIGATOR").

Hướng sửa: thêm nút **Ẩn** cho từng tàu. **Không cần đổi schema:** bảng `ships` đã có cột `active`, hàm `ships()` đã lọc `active=1` và `add_ship` đã kích hoạt lại tàu bị ẩn. Cần thêm một tuyến API mới (ghi vào `API.md` và `KIEM_THU_API.py`). Báo cáo cũ giữ nguyên tên tàu đã lưu.

### U10 — Hộp thoại dài làm nút lưu khuất khỏi màn hình (TB)

Trình sửa mẫu phân công cao **1307 px trong vùng nhìn 591 px**; nút "Lưu cả 4 mẫu" và "+ Thêm vị trí / người" nằm ở cuối, phải cuộn mới thấy. Hộp Danh mục và hộp Bảo vệ dữ liệu cũng dài hơn vùng nhìn (danh sách bản sao khôi phục nằm ngoài màn hình lúc mở).

Hướng sửa: tiêu đề và hàng nút của hộp thoại dính khi cuộn (`position: sticky`), phần giữa cuộn.

### U11 — So sánh bản bổ sung hiện hai báo cáo đầy đủ, không chỉ ra chỗ khác (TB, đi cùng U5)

Bấm "Xem hai bản" hiện lần lượt hai báo cáo đầy đủ, không đánh dấu dòng nào khác nhau; người kiểm tra phải cuộn và so bằng mắt. Hộp so sánh còn dùng lại bản xem trước nên có thêm nút "In / Lưu PDF" và "Đóng" bên cạnh "Về danh sách đối chiếu" (nút "Đóng" tắt cả hộp thay vì quay lại).

Hướng sửa: dùng **chung một thành phần so sánh** với U5 (lịch sử sửa), tô nổi các ô đã đổi; bỏ nút in/đóng dư thừa trong hộp so sánh.

### U12 — Xem trước khôi phục hiện "Từ đến" trống khi bản sao chưa có ca (Thấp)

Khi bản sao có 0 ca, hộp "Bản sao đã qua kiểm tra" hiện "0 ca · 0 lần lưu lịch sử" rồi dòng "Từ đến" không có ngày, trông như bị lỗi. Nên hiện "Chưa có báo cáo nào".

### U13 — Chữ giao diện xưng "anh" (Thấp)

Có 3 chỗ xưng "anh" ([danh_muc.js:155](../giao_dien/tai_nguyen/danh_muc.js#L155) "của anh", [phan_cong_mau.js:105](../giao_dien/tai_nguyen/phan_cong_mau.js#L105) "khi anh bấm nút", [ung_dung.js:130](../giao_dien/tai_nguyen/ung_dung.js#L130) "Anh em có thể đổi"). Khi nhiều người dùng (kể cả bản web), nên dùng cách nói trung tính. Chữ trong `HUONG_DAN.txt` cũng nên rà cùng lúc.

### U14 — Thông báo nổi che các nút phía trên (Thấp)

Thông báo hiện ở góc trên phải, che nút "Tải tất cả tệp" / "+ Thêm tệp" (và các nút Lịch sử / Xem-In / Xuất Excel) trong 4,5 giây, thông báo lỗi 10 giây. Nên đặt ở góc dưới và cho đóng bằng một lần bấm.

## 4. Không cần làm

- Đổi framework hoặc làm lại giao diện.
- Giao diện tối.
- Trình sửa danh mục dạng ô văn bản: chấp nhận được vì là việc của quản trị.
- Tối ưu cho điện thoại: chủ dự án đã xác nhận không cần.

## 5. Thứ tự đề xuất

| Gói | Gồm | Ghi chú |
|---|---|---|
| Bản vá giao diện | U1, U2, U3, U4, U7, U8, U10, U12, U13, U14 | Chỉ sửa `ung_dung.js`, `danh_muc.js`, `phan_cong_mau.js`, `style.css`, `giao_dien.html`; không đổi API hay dữ liệu |
| Cần tuyến API mới | U9 | Không đổi schema (cột `active` đã có); cập nhật `API.md` và `KIEM_THU_API.py` |
| Cùng Đợt 3 | U5 và U11 | Chung một thành phần so sánh, phụ thuộc thiết kế bảng lịch sử mới |
| Khi chạm vào | U6 | Ưu tiên thấp |

Phản hồi người dùng thật tính sau (bản MVP / protocol). Việc kiểm chứng còn lại (hộp thoại in thật, các màn hình chưa đánh giá) đã giao Codex: V1–V8 trong [roadmap](ROADMAP_SAU_V1_9.md).
