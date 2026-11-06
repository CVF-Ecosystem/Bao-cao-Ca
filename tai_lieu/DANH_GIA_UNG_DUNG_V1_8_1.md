# Đánh giá Sổ báo cáo ca 1.8.1

Ngày đánh giá: 06/11/2026. Phát triển bởi Mr Ân / Tân Thuận.

**Điểm tự đánh giá: 8,3/10**, dựa trên mã nguồn và kiểm thử trong môi trường Linux. Điểm này là nhận định kỹ thuật, chưa phải chứng nhận vận hành trên máy bãi Windows.

| Tiêu chí | Điểm | Căn cứ và giới hạn |
|---|---:|---|
| Đúng nghiệp vụ và dữ liệu cũ | 8,5 | Giữ schema 3, báo cáo chốt cần lý do khi sửa, chống lưu đè phiên bản; các kiểm thử cũ qua. |
| Bảo vệ và phục hồi dữ liệu | 8,5 | Snapshot SQLite đã kiểm tra, nhiều phiên bản, nơi lưu ngoài, giữ DB cũ trước phục hồi, khóa phiên chạy; vẫn phụ thuộc ổ dự phòng và bản sao đã có. |
| Dễ dùng cho nhân viên | 8,0 | Menu bảo vệ, chọn thư mục, trạng thái lần thành công, xem trước bản phục hồi và xác nhận rõ. Chưa đánh giá thao tác thực tế bởi nhân viên bãi. |
| Vận hành thực tế | 8,0 | Không tự sinh DB trắng khi phát hiện dữ liệu đã dùng bị mất; cảnh báo sao lưu lỗi. Chưa kiểm thử EXE/hộp thoại Windows hoặc tải DB nhiều GB. |
| Bảo trì và kiểm thử | 8,5 | Tách module bảo vệ, 92 kiểm thử Python qua và các bộ kiểm thử JavaScript qua. Chưa có CI tự chạy trên Windows. |

Trung bình 8,3/10 (làm tròn một chữ số).

## Những phần đã làm tốt

- Dữ liệu báo cáo nhiều tháng, lịch sử và tệp đính kèm nằm chung trong snapshot nhất quán.
- Khôi phục không âm thầm trộn dữ liệu; nhân viên nhìn số ca và phạm vi ngày trước khi quyết định thay toàn bộ DB.
- DB nguồn của bản kiểm tra/bổ sung được phân biệt với DB chính; sai nguồn bị chặn thay thế.
- Thư mục dự phòng có cảnh báo riêng. Thành công tại máy không được trình bày như đã thành công ở ổ ngoài.
- Mất DB trong phiên đang chạy không làm Store tự tạo file mới khi đọc/ghi tiếp.
- Khóa hệ điều hành tránh hai phiên ứng dụng cùng nhập và phục hồi một thư mục.

## Rủi ro và ưu tiên tiếp theo

| Ưu tiên | Việc cần làm | Vì sao |
|---|---|---|
| P1 trước khi dùng chính thức | Trên Windows, cập nhật vào thư mục cũ, chọn ổ dự phòng thật; chốt ca thử trên bản sao rồi khôi phục thử. | Hộp thoại Windows và EXE chưa được chạy trong môi trường đánh giá này. |
| P1 khi DB tăng lớn | Đo tốc độ với DB có ảnh/PDF thực tế, theo dõi dung lượng ổ sao lưu. | Bản sao đầy đủ; mỗi lần kiểm tra toàn vẹn và đọc hash tệp đính kèm có thể chậm. |
| P2 | Bổ sung chỉ báo tiến trình cho bản sao/khôi phục lớn và ngưỡng dung lượng ổ. | Server xử lý tuần tự; đang sao lưu lâu sẽ làm thao tác tiếp theo phải chờ. |
| P2 | Đưa danh mục cấu hình bên ngoài vào gói khôi phục riêng. | Snapshot hiện bảo vệ DB; các tệp DANH_MUC và cấu hình ngoài DB cần giữ thêm bản sao thư mục. |
| P2 | Kiểm tra khôi phục định kỳ sang thư mục thử. | File có mặt hoặc ghi được chưa bảo đảm người vận hành chọn đúng bản khi có sự cố. |

Không đề xuất chuyển ngay sang hệ quản trị dữ liệu lớn hoặc bắt buộc Internet: với nhu cầu một máy nhập và mang DB đi kiểm tra, SQLite cùng sao lưu/khôi phục rõ ràng vẫn đơn giản hơn. Nếu sau này nhiều máy cùng nhập trực tiếp, cần thiết kế một máy chủ dùng chung thay vì đồng bộ nóng file DB bằng đám mây.

## Bằng chứng kiểm thử

- 92 kiểm thử Python thành công: nghiệp vụ cũ, danh mục, mẫu ca, đính kèm, API và 22 kiểm thử bảo vệ mới.
- Các bộ JavaScript cũ và 6 kiểm tra hành vi giao diện bảo vệ mới thành công bằng Node VM.
- Trên bản sao DB anh cung cấp: xóa DB rồi phục hồi vẫn đủ 3 báo cáo và 74 lần lưu lịch sử. File DB gốc không bị thay đổi.
- Đã mô phỏng: DB mất/hỏng, bản sao hỏng, sai nguồn, DB bổ sung, bản thay đổi sau xem trước, tệp giao dịch còn mở, ổ dự phòng ngắt kết nối, lỗi sao lưu, lưu bản nháp so với chốt ca, khóa hai phiên, lưu giữ bản ngày/tháng, phục hồi qua API và chặn yêu cầu từ ngữ cảnh cũ.
- Chưa chạy kiểm thử trình duyệt đầy đủ: môi trường có Playwright nhưng không có Chromium. Kiểm tra giao diện nêu trên là kiểm tra hành vi JavaScript bằng mô phỏng, không phải kiểm tra hiển thị bằng ảnh chụp.
- Chưa đo mất điện vật lý, hỏng phần cứng, độ bền dịch vụ đám mây, DB hàng GB và EXE Windows.

## Sửa lỗi 1.8.1

Bản 1.8 chặn nguồn DB khác quá cứng khi người dùng chép DB cũ vào thư mục từng tạo DB trắng. Bản 1.8.1 thêm bước tiếp nhận file hiện hành có xác nhận số ca/phạm vi ngày; sao lưu DB đầu vào và cấu hình trước khi đăng ký nguồn mới. Các snapshot tự động mới được tách theo mã nguồn để việc giữ/xóa phiên bản không ảnh hưởng DB trước. Đã kiểm tra hủy/không tiếp nhận giữ nguyên DB và cấu hình, lỗi sao lưu chặn tiếp nhận, dữ liệu hỏng/DB bổ sung bị từ chối và dữ liệu thật 3 báo cáo/74 lịch sử được giữ nguyên.

## Bản vá 1.8.2: khác biệt Windows/Linux

Lỗi fsync file mở chỉ đọc bị bỏ sót trong kiểm thử Linux trước đó. Bản vá đổi riêng file sao tạm sang r+b, giữ DB nguồn ở mode=ro. Kiểm thử hồi quy dùng phép ghi 0 byte để mô phỏng yêu cầu quyền ghi: code cũ báo đúng Errno 9, code mới qua. Toàn bộ 93 kiểm thử Python thành công. Vẫn chưa chạy thực tế Windows hoặc EXE; không xem kiểm thử mô phỏng là thay thế cho kiểm tra trên máy bãi.
