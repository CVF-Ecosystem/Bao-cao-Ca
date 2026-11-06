# Đánh giá giao diện (máy tính) — Sổ báo cáo ca 1.9.x

Ngày: 2026-11-06. Người đánh giá: Claude. Phạm vi: **chỉ giao diện trên máy tính**, theo quyết định của chủ dự án (nhập và xem đều làm trên máy tính; không tối ưu cho điện thoại).

Kết luận ngắn: **không cần làm lại giao diện và không cần đổi framework.** Có 8 chỗ nên sửa, tập trung ở trang nhập ca và bản in. Kế hoạch triển khai: [ROADMAP_SAU_V1_9.md](ROADMAP_SAU_V1_9.md), mục "Đợt giao diện".

## 1. Cách đánh giá và giới hạn

- Chạy máy chủ thật trên thư mục tạm với dữ liệu mẫu (14 ngày × 2 ca, có ca nháp, ca chốt, ca thiếu phụ trách chung), điều khiển Chrome bằng Playwright ở cỡ **1366×657** (vùng trình duyệt trên màn hình 1366×768). Không đụng vào `DU_LIEU` thật, không sửa mã.
- Đã chạy thao tác thật: mở ca, đổi tab, mở hộp chọn người, gõ số sai, tạo xung đột hai cửa sổ, chốt ca thiếu phụ trách, xem lịch sử, xem tổng hợp, mở danh mục, tạo ca mới. Đã in thử bằng cách xuất PDF theo CSS in của ứng dụng (A4 ngang).
- **Chưa đánh giá:** tab "Ảnh & biên bản" (chưa chụp), hộp chọn tàu, trình sửa mẫu phân công, hộp Bảo vệ dữ liệu / Khôi phục, luồng nhập bổ sung từ DB, bản xem trước trên màn hình ngoài lúc in.
- **Chưa kiểm chứng với người dùng thật.** Đây là điều quan trọng nhất còn thiếu: mức ưu tiên dưới đây là nhận định kỹ thuật, nên đối chiếu với 1–2 người nhập ca thật (bước nào mất thời gian nhất, chỗ nào hay nhập sai).
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

## 3. Các chỗ nên sửa

Ưu tiên: **Cao** = gặp mỗi ca; **TB** = tiện hơn, chi phí thấp; **Thấp** = hiếm gặp hoặc chỉ là tinh chỉnh.

### U1 — Vùng làm việc của trang nhập ca quá hẹp (Cao)

Đo ở cỡ 1366×657: dải tab bắt đầu ở y = 357 px, thanh Lưu nháp / Chốt ca dính ở y = 586 px, còn **ô nhập đầu tiên nằm ở y = 704 px, ngoài màn hình**. Mở ca ra chưa thấy ô nhập nào; vùng cuộn thực tế chỉ còn khoảng 230 px. Nguyên nhân: tiêu đề trang cộng thẻ thông tin ca chiếm hơn nửa chiều cao.

Hướng sửa: gộp tiêu đề trang và thẻ thông tin ca thành một dải gọn (ngày/ca, trạng thái, người nhập, các nút Lịch sử / Xem-In / Xuất Excel), và cho dải tab dính khi cuộn. Ước tính lấy lại khoảng 200 px, **cần đo lại sau khi sửa**.

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

Hướng sửa: Esc đóng hộp thoại (trừ khi đang lưu), thêm liên kết "bỏ qua tới nội dung", phím tắt chuyển tab (ví dụ Alt+1…4).

### U5 — Lịch sử sửa không cho thấy đã sửa gì (TB)

Màn hình chỉ có danh sách phiên bản, người lưu, lý do và nút "Xem nội dung" cho từng bản. Với ca đã chốt bị sửa kèm lý do, người kiểm tra phải mở hai bản và so bằng mắt. Nên hiện **khác biệt giữa hai phiên bản liền nhau** (ví dụ "F20 dòng TRẢI LÓT PHÁO: 25 → 28"). Hợp với Đợt 3 vì bảng lịch sử thay đổi ở đó, và có ích cho kiểm tra khi lên web.

### U6 — Chỉ có một cách giải quyết xung đột (Thấp)

Khi hai cửa sổ cùng sửa một ca, giao diện báo rõ và giữ chữ đang gõ, nhưng chỉ có nút "Tải lại báo cáo" (bỏ phần đang gõ). Có thể thêm lựa chọn giữ lại ghi chú đã gõ sau khi tải lại. Với 1–2 người nhập thì hiếm gặp.

### U7 — Chữ phiên bản cố định trong HTML (Thấp)

[giao_dien.html](../giao_dien/giao_dien.html) còn chữ "Phiên bản 1.9.0" cố định, JS thay bằng phiên bản thật sau khi tải thông tin. Với bản 1.9.1 sẽ hiện sai một thoáng, và hiện sai hẳn nếu JS lỗi. Nên để trống chữ mặc định.

### U8 — Bản in (hai việc, TB)

**U8a. Ca nhỏ tràn sang 2 trang.** Ca 9 nhân sự và 6 công việc in ra 2 trang; trang 2 chỉ còn 1 dòng công việc, dòng Tổng và phần ghi chú. Khối tiêu đề chiếm khoảng 25% chiều cao trang và các dòng bảng khá cao. Mục tiêu: ca thông thường vừa **1 tờ** bằng cách thu gọn tiêu đề và giảm khoảng cách dòng khi in.

**U8b. Từ trang 2 trở đi không có gì cho biết đây là ca nào.** Ca dài (24 dòng nhân sự, 30 công việc) in 5 trang; các trang sau chỉ có tiêu đề bảng, không có ngày/ca, không có số trang. Mục tiêu: dòng nhỏ lặp ở mỗi trang, ví dụ "Báo cáo ca đêm 06/11/2026 · Trang 2/5".

**Cần chủ dự án xác nhận:** bản in có cần chỗ ký tên (trưởng ca, phụ trách chung) không, và có cần in ngày giờ in không. Tôi không biết yêu cầu của giấy tờ thực tế.

## 4. Không cần làm

- Đổi framework hoặc làm lại giao diện.
- Giao diện tối.
- Trình sửa danh mục dạng ô văn bản: chấp nhận được vì là việc của quản trị.
- Tối ưu cho điện thoại: chủ dự án đã xác nhận không cần.

## 5. Thứ tự đề xuất

| Gói | Gồm | Ghi chú |
|---|---|---|
| Bản vá giao diện | U1, U2, U3, U4, U7, U8 | Chỉ sửa `ung_dung.js`, `style.css`, `giao_dien.html`; không đổi API hay dữ liệu |
| Cùng Đợt 3 | U5 | Phụ thuộc thiết kế bảng lịch sử mới |
| Khi chạm vào | U6 | Ưu tiên thấp |

Trước khi làm nên hỏi 1–2 người nhập ca thật để xếp lại thứ tự, và in thử một lần ra máy in thật để kiểm tra phần đầu/chân trang của trình duyệt.
