# Đối chiếu tan-thuan-port và roadmap bổ sung nhân sự

Status: SOURCE_ACCEPTED_NATIVE_PENDING

Ngày: 2026-11-08. Đối chiếu/thiết kế đã được audit độc lập; PNI E1–E6 đang triển khai theo work order được chấp nhận. Roadmap sản phẩm gốc vẫn là [ROADMAP_SAU_V1_9.md](../../tai_lieu/ROADMAP_SAU_V1_9.md). Phiên bản ứng viên1.9.2 chưa được nghiệm thu/phát hành. Các phần khảo sát bên dưới giữ lại quyết định và giới hạn quan sát ban đầu.

## Tiếp tục được yêu cầu — 2026-11-08

Chủ dự án đã yêu cầu orchestrator audit và tiến hành làm, cho phép Terra triển khai, Sol xử lý phần khó và Astra review độc lập. Phạm vi PNI được Local chọn là E1–E6 nhập danh mục người dạng phẳng, giữ nguyên các bước xem trước/xác nhận và nghiệm thu EXE. Các câu mô tả chưa có quyền triển khai trong khảo sát ban đầu ở các mục sau là lịch sử thiết kế; quyền thực thi hiện tại chỉ có khi SPEC/work order mới và exact-action assessment được chấp nhận. E7, định danh, bảng phân ca và đồng bộ vẫn chưa được mở. Phiên bản ứng viên1.9.2 dùng cho đợt nhập này; D2 tối ưu sao lưu vẫn là việc riêng, số1.9.2 trước đó chỉ dự kiến và cần đặt lại khi đợt D2 được giao.

Căn cứ độc lập: `docs/reviews/personnel-import-20261108/audit-astra.md`; SPEC và ADR tại `docs/specs/PERSONNEL_EXCEL_IMPORT.md`, `docs/decisions/ADR_PERSONNEL_EXCEL_READER.md`. Gói thực thi: `docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md`. Những quy tắc bảo toàn/khôi phục còn chưa chắc ở khảo sát được cụ thể hóa bằng phép thêm có giới hạn trong owner: chỉ ghi file người, từ chối trạng thái inactive/không nhất quán, không đè thay đổi ngoài khi rollback và kiểm tra thực tế các giới hạn reader.

## 1. Kết luận về tính phù hợp

**Phù hợp nhất: nhập danh mục nhân sự từ Excel có xem trước, kiểm tra lỗi và xác nhận.** Nên tận dụng cơ chế danh mục và mẫu phân công sẵn có của Sổ báo cáo ca. Lợi ích kỳ vọng là giảm nhập lại danh sách người và tổ; chưa có số đo thời gian tiết kiệm hoặc tần suất cập nhật để định lượng.

Việc này phù hợp hướng một ứng dụng desktop/web dùng chung nghiệp vụ. Không cần mang theo React, IndexedDB, hệ thống đồng bộ hay toàn bộ mô-đun nhân sự của tan-thuan-port. Khác biệt dữ liệu quan trọng nhất là Sổ báo cáo ca hiện nhận diện người bằng họ tên; dự án tham khảo có mã nhân viên. Vì vậy, đợt nhập đầu chỉ bổ sung danh mục theo mô hình hiện tại, phải từ chối trường hợp không thể phân biệt an toàn.

Không gom nhập danh sách nhân viên, đọc bảng phân công nhiều ô gộp và nhập báo cáo lịch sử thành một hạng mục. Chúng có đầu vào, quy tắc và tác động khác nhau.

## 2. Nguồn và độ chắc chắn

Đối chiếu các tệp nguồn hiện có trên máy ngày 2026-11-08 và cấu trúc OOXML của bốn workbook. Danh sách đường dẫn, SHA-256, HEAD và giới hạn quan sát được giữ tại [source-observations.json](../reviews/tan-thuan-port-fit/source-observations.json). Cây làm việc tan-thuan-port có thay đổi chưa commit: kết luận gắn với hash tệp đã đọc, không chỉ với HEAD `9dc4ff8`. Không sao chép họ tên, mã nhân viên hoặc dữ liệu ca vào tài liệu này.

| Nguồn | Sự thật quan sát từ nguồn | Giới hạn |
|---|---|---|
| `tan-thuan-port/apps/web/src/lib/personnelParser.ts` | Tìm hàng tiêu đề trong tối đa 10 hàng đầu; nhận mã/tên/bộ phận/ca; cảnh báo thiếu mã/tên hoặc trùng mã trong file; cập nhật theo mã vào IndexedDB. | Hai hàm chuẩn hóa bộ phận/ca chỉ trả lại đầu vào. Bộ dò dùng chuỗi con, chưa phải hợp đồng nhập đáng tin cậy cho mọi workbook. |
| `tan-thuan-port/apps/web/src/app/admin/personnel/page.tsx` | Luồng nhập nhân sự hiện hành đọc file rồi gọi `parseEmployeeExcel` và `importEmployees`; hiển thị số mới/cập nhật. | Không có bước xác nhận bảng thay đổi trước khi ghi trong handler đã đọc. Kết quả lỗi từng người chưa được trình bày đầy đủ ở thông báo tổng. |
| `tan-thuan-port/apps/web/src/components/ExcelImport.tsx` | Có chọn cột, xem trước và ghép theo mã nhân viên. | Không tìm thấy nơi import/sử dụng thành phần trong `apps/web/src`. Không coi đây là luồng hiện hành đã nghiệm thu. Chức danh không khớp bị mặc định sang Ban Chỉ Huy; không tiếp nhận quy tắc này. |
| `tan-thuan-port/apps/web/src/components/personnel/EmployeeSelector.tsx` | Chọn một/nhiều người, tìm tên/mã/bộ phận, lọc theo bộ phận và ca. | Khi bộ lọc không có kết quả, logic có thể dùng lại tập rộng hơn. Không dùng hành vi nới lọc ngầm cho nhập phân tổ. |
| `tan-thuan-port/apps/web/src/app/start-shift/page.tsx`, `end-shift/page.tsx` | Có ý tưởng phân công theo bộ phận, Tally theo tàu và nội dung cuối ca. | Các `handleSubmit` đang ghi log và báo Demo; không có bằng chứng lưu bền từ hai handler này. Không suy rộng thành mọi báo cáo của tan-thuan-port đều là demo. |
| `tan-thuan-port/apps/web/src/lib/syncService.ts`, `apps/api/src/routes/employees.ts` | Có đường đồng bộ nhân viên và API bulk riêng. | Sự tồn tại không chứng minh luồng nhập admin đã đồng bộ đầu cuối, cũng không tạo nhu cầu đồng bộ cho Sổ báo cáo ca. Chưa chạy thử. |
| `ma_nguon/QUAN_LY_DANH_MUC.py` | Danh mục người theo họ tên; đúng ba tổ; kiểm tra tham chiếu; digest chống ghi đè; sao lưu trước lưu và phục hồi khi lỗi. | Không có mã nhân viên/bộ phận trong mô hình danh mục người hiện tại. Giới hạn 500 tên, 120 ký tự/tên; không chứa dấu `;`. |
| `ma_nguon/MAU_PHAN_CONG.py`, `giao_dien/tai_nguyen/phan_cong_mau.js` | Đã có ba mẫu tổ và mẫu ca ngày; xem trước rồi xác nhận; kiểm tra nguồn/báo cáo đổi trước áp dụng; giữ báo cáo cũ. | Cấu hình mẫu khác với một lần phân công thực tế và không tự chạy theo giờ. |
| `giao_dien/tai_nguyen/danh_muc.js`, `ma_nguon/NGHIEP_VU.py` | Đã tìm người không dấu, lọc tổ, giữ người đang chọn ngoài tổ. Kỳ báo cáo là `DAY`/`NIGHT`. | Tổ nhân sự Ca 1–2–3 không đồng nghĩa với kỳ báo cáo ngày/đêm. |

### Cấu trúc file Excel đã kiểm tra

| File trong tan-thuan-port | Quan sát cấu trúc | Ý nghĩa cho phạm vi |
|---|---|---|
| `apps/web/public/Template_DanhSach_NhanVien.xlsx` | Một sheet `DanhSachNhanVien`, A1:D6; tiêu đề: `MSCĐ`, `Họ và Tên`, `Chức danh`, `Nhóm/Ca`; không có ô gộp/công thức. | Ứng viên đầu vào cho nhập danh mục. Đây là mẫu, chưa chứng minh tương đương file nhân sự đơn vị đang dùng. |
| `data/Bai cont ca.xlsx` | Sheet `N09-9`, A1:I27; tiêu đề báo cáo sản xuất cuối ca Bãi container; có ô gộp, không có công thức. | Mẫu báo cáo khác bảng danh sách nhân viên; không hứa nhập bằng bộ nhập danh mục. |
| `data/Thu tuc ca.xlsx` | Sheet `T10`, A3:F581; tiêu đề báo cáo ca Thủ tục; nhiều ô gộp; 151 phần tử công thức. | Cần khảo sát riêng nếu có nhu cầu nhập dữ liệu nghiệp vụ Thủ tục; không thuộc ứng dụng Bãi hiện tại. Chưa kiểm tra kết quả tính/công thức trong Excel. |
| `data/Dieu hanh ca.xlsx` | Sheet `10.2025`, A1:G77; có cột STT/CA và ô gộp; không có công thức. | Bố cục riêng; không tự suy thành danh sách nhân viên hay tổ luân phiên. |

**Điểm chưa khớp ngay cả trong dự án tham khảo:** mẫu có cột `Chức danh`, trong khi bộ nhập đang dùng dò cột bộ phận, không ánh xạ chức danh thành bộ phận. Như vậy không được mô tả hệ thống kia là đã tự phân loại bộ phận đúng từ mẫu này. Đây là nhận xét từ mã và tiêu đề, chưa phải kết quả chạy parser.

## 3. Đánh giá lựa chọn

Đánh giá định tính dựa trên khoảng trống thực tế, khả năng dùng chung desktop/web, ảnh hưởng dữ liệu và chi phí trùng lặp; không dùng điểm số/ước lượng tiết kiệm chưa đo.

| Hạng mục | Mức phù hợp | Quyết định đề xuất | Lý do và điều kiện |
|---|---|---|---|
| Nhập danh sách người từ Excel, xem trước lỗi/thay đổi | Cao | Ưu tiên đầu tiên sau baseline 1.9.1 | Bổ sung đúng phần còn thiếu; ghi qua chủ sở hữu danh mục hiện tại; không cần đổi schema báo cáo. |
| Tự gợi ý cột, chọn sheet/hàng tiêu đề/cột thủ công | Cao | Làm cùng đợt nhập | Chịu được tiêu đề khác nhau; hiển thị và xác nhận ánh xạ; không dò nhầm bằng chuỗi con rồi ghi ngay. |
| Gợi ý thêm người vào ba tổ từ cột Nhóm/Ca | Khá, có điều kiện | Bước tiếp theo | Chỉ ánh xạ nhãn được xác nhận vào `team1..3`; giá trị không rõ để chưa phân tổ; không đổi DAY/NIGHT. |
| Nhập vị trí/người thành mẫu phân công | Trung bình | Hoãn, chỉ mở khi có bảng đầu vào phù hợp | Mẫu Excel hiện kiểm tra không có cột vị trí phân công cụ thể. Chức danh nghề nghiệp không mặc nhiên là vị trí trong ca. Tally theo tàu là phân công thực tế, không được nhập bừa vào mẫu chung. |
| Mã nhân viên làm định danh bền vững | Trung bình ở hiện tại, hữu ích dài hạn | Thiết kế riêng khi có nhu cầu phân biệt trùng tên/đổi tên | Chạm danh mục, tổ, mẫu, lịch sử, xuất và trao đổi DB. Không đồng nhất mã nhân viên với `auth_user`/tài khoản đăng nhập. |
| Bộ chọn người, tìm không dấu, lọc tổ, mẫu có xem trước | Đã có tương đương | Tái sử dụng của dự án này | Không thêm một thành phần hoặc luồng phân công cạnh tranh. |
| Mở rộng nhiều bộ phận, nghỉ phép, dashboard nhân sự | Thấp trong phạm vi hiện tại | Để ngoài roadmap bổ sung | Sổ báo cáo ca đang tập trung Bãi container; chưa có quyết định mở rộng nghiệp vụ. |
| Đồng bộ trực tiếp hai ứng dụng, dùng chung DB/API | Thấp trong phạm vi hiện tại | Để ngoài; không tích hợp trong đợt Excel | Phải có chủ dữ liệu chuẩn, quyền truy cập, xung đột, audit và phục hồi; không cần để giải quyết nhập danh sách ban đầu. |
| Mang nguyên React/IndexedDB/bộ nhập TS sang | Không phù hợp | Không tiếp nhận | Khác nền Python/SQLite/JS thuần; học quy tắc và UX, không thêm kho dữ liệu song song. |

## 4. Design Control Gate

**Authority:** yêu cầu 2026-11-08 của chủ dự án là đối chiếu, tạo roadmap và đánh giá phù hợp trước khi làm. Đây là quyền phân tích/tài liệu, không phải phê duyệt tính năng, dependency, migration hay BUILD. Giữ mọi định hướng/bất biến đã chốt ở roadmap gốc. Các đề xuất dưới đây chưa được đăng ký như milestone triển khai đã duyệt.

**Phạm vi đề xuất đợt đầu:** đọc `.xlsx` bảng danh sách phẳng; chọn sheet/hàng/cột; tạo bản kế hoạch nhập; phân loại dòng; thêm tên chưa có sau xác nhận; tái sử dụng danh mục hiện tại. Cột mã, bộ phận, nhóm của nguồn được dùng để kiểm tra/lọc có hiển thị; không hứa lưu đầy đủ thành hồ sơ nhân sự chuẩn. Phải thông báo rõ trường nào được lưu và trường nào chỉ dùng trong lần nhập. Không tự mang toàn bộ nhân sự bộ phận khác vào danh mục Bãi.

**Ngoài phạm vi đợt đầu:** `.xls`, macro, file mã hóa, bảng phân ca ô gộp, tính lại công thức, nhập báo cáo sản xuất/lịch sử, đổi tên/xóa hàng loạt, định danh nhân viên chuẩn, tự thay mẫu phân công, đồng bộ mạng, thay framework hoặc auth. Nếu đầu vào là báo cáo ca thì nhận diện không hỗ trợ và dừng, không lọc đại vài tên để báo nhập thành công.

**Hướng thiết kế đề xuất:** tách đọc file, chuẩn hóa, lập kế hoạch nhập và xác nhận ghi. Tái sử dụng `Catalogs.save` và hợp đồng context/digest của danh mục; máy chủ kiểm tra lại dữ liệu/nguồn trước ghi. Không tạo cơ chế ghi thẳng bảng `people` hay thêm IndexedDB. Chốt thư viện đọc Excel bằng ADR trước SPEC/BUILD: so sánh thư viện có bảo trì với rủi ro tự viết bộ đọc OOXML giới hạn; kiểm tra giấy phép, giới hạn, đóng gói EXE và khả năng dùng trên web. Hiện chưa chọn hoặc cài dependency.

Quy tắc cần khóa trong SPEC:

1. Chuẩn hóa NFC và khoảng trắng; đối chiếu tên theo quy tắc danh mục hiện tại. Tên khớp là giữ nguyên, tên mới là thêm; không tự sửa tên gần giống. Trùng tên khác mã hoặc cùng mã khác tên trong nguồn là trường hợp cần xử lý rõ, không hợp nhất ngầm. So tên không dấu chỉ để tìm/gợi ý, không làm khóa định danh.
2. Khi hệ thống hiện chưa lưu mã, không cam kết phát hiện một người đổi tên giữa hai lần nhập. Mã có số 0 đầu phải bảo toàn khi đọc được; nếu nguồn số/định dạng không xác định được thì báo rõ, không tự bù số. Nếu cần bảo đảm danh tính qua nhiều lần nhập, mở đợt định danh riêng trước khi hứa đồng bộ cập nhật.
3. Cột nhóm/ca nguồn chỉ gợi ý tổ nhân sự; ba tổ và nhân sự ca ngày là khái niệm cấu hình riêng với kỳ DAY/NIGHT. Không xếp người theo giờ máy hoặc suy từ tên file.
4. Xem trước theo nhóm mới/đã có/không rõ/lỗi, có sheet và số dòng nguồn; lỗi không được biến mất trong thông báo tổng. Đợt đầu đề xuất từ chối xác nhận toàn bộ tập đang chọn khi còn lỗi chưa xử lý; người dùng có thể sửa file hoặc loại dòng có ghi nhận rồi xem trước lại. Hủy hoặc xem trước không ghi gì.
5. Nhập lặp cùng danh sách không tạo tên/tổ trùng. Người thiếu trong file không bị xóa/vô hiệu hóa. Không tự kích hoạt lại người hoặc thay cấu hình mẫu. Không sửa báo cáo và revision cũ.
6. Giữ giới hạn danh mục hiện tại; định nghĩa thêm trần kích thước nén/giải nén, sheet, hàng/cột, thời gian xử lý. Không chạy macro/công thức hoặc tải liên kết ngoài. File không hỗ trợ/công thức tại ô định danh phải trả lỗi rõ theo SPEC; không dùng giá trị rỗng mặc định để che thiếu dữ liệu.
7. Ghi có sao lưu, kiểm tra digest/context mới nhất, đối chiếu thay đổi trước khi xác nhận; lưu thất bại không báo thành công. Khả năng phục hồi qua nhiều file/dữ liệu phải được thử lỗi ở từng ranh giới; mã rollback đang có không thay thế bằng chứng chịu lỗi mới.

Các quy tắc này là phương án thiết kế cần review; không coi đã tồn tại trong ứng dụng. Ngày đánh giá không phải mốc bắt buộc phát hành.

## 5. Roadmap đề xuất và điểm quyết định

| Bước | Đầu ra phục vụ người dùng | Phụ thuộc / cổng ra | Chủ trì và nơi tiếp tục |
|---|---|---|---|
| R0 — Chốt baseline hiện tại | Bản 1.9.1 có bằng chứng đóng gói/khởi chạy và các luồng bị ảnh hưởng làm mốc. | Tái sử dụng chứng cứ hợp lệ; xử lý phần EXE và UI còn mở theo roadmap gốc. Thiết kế Excel được làm ngay; không cần chờ benchmark máy bãi hoặc D2 để viết SPEC. | ORCHESTRATOR; D1-4 và V1–V8 của roadmap gốc. |
| R1 — Khóa phạm vi/định dạng | SPEC cho bảng nhân sự, quy tắc thêm/giữ/lỗi, trường được lưu, bảng ca không hỗ trợ, giới hạn và API; ADR bộ đọc Excel. | Xác định file/bộ phận đầu vào đại diện bằng nguồn đã có; giải quyết ý nghĩa cột Nhóm/Ca; phân biệt mã/tên/tổ/kỳ báo cáo. Reviewer kiểm tra trước work order. | SPEC_AUTHOR/WORK_ORDER_AUTHOR; `docs/specs/`, `docs/decisions/`, sau đó `docs/work_orders/`. |
| R2 — Nhập danh mục có xem trước | Người dùng chọn Excel, xem đúng thay đổi, xác nhận thêm người, hủy an toàn và nhập lặp không trùng. | Thiết kế được chốt, milestone đầy đủ được Local admit, exact-action assessment và work order; triển khai ghi danh mục/đọc file ở mức tối thiểu R2 và review độc lập. Đủ E1–E6 bên dưới mới đề xuất phát hành riêng. | IMPLEMENTATION_WORKER + REVIEWER độc lập; đường code danh mục hiện tại, không giao triển khai bằng tài liệu này. |
| R3 — Gợi ý tổ từ Nhóm/Ca | Sau xem trước, chỉ thêm thành viên vào tổ được chỉ rõ; người ca ngày/chưa rõ không bị tự gán tổ. | R2 ổn định, quy tắc ánh xạ và E7 được khóa. Có thể ghép vào cùng bản nếu phạm vi/evidence vẫn gọn; không bắt buộc đợt đầu mang theo. | SPEC_AUTHOR rồi worker/reviewer; tái sử dụng `TO_NHAN_SU.json` và mẫu hiện có. |
| R4 — Đánh giá định danh/mẫu nâng cao | Đề xuất riêng về mã nhân viên hoặc nhập mẫu phân công khi có đầu vào và nhu cầu thực. | Chỉ mở khi có trường hợp trùng tên/đổi tên hoặc bảng vị trí-người cụ thể và lợi ích được xác nhận; giải quyết migration, lịch sử, xuất/nhập DB. | ORCHESTRATOR; không gộp mặc định vào schema 4 vì schema đó đang phục vụ revision/audit. |

Thứ tự sản phẩm đề xuất: hoàn tất nghiệm thu 1.9.1 → đợt Excel nhỏ R1/R2 khi thiết kế được chốt → R3 nếu cần; đợt U và D2 tiếp tục theo ưu tiên roadmap gốc. Đây không phải yêu cầu hoãn D2 hoặc điều kiện phải hoàn thành mọi V1–V8 trước khi phân tích Excel. R4 chưa có lịch/phiên bản. Không mở rộng thành HRM hoặc nhiều bộ phận khi chỉ cần nhập danh mục Bãi.

### Tiêu chí sản phẩm dự kiến cho R2/R3

Đây là tập tiêu chí đề xuất, chưa là authority được duyệt. R2 cần đầy đủ E1–E6; E7 thuộc R3 và không được tính là đã xong khi chỉ giao R2. Mỗi work order phải kế thừa trọn tập tiêu chí của mốc được duyệt và chỉ rõ phần còn lại.

| ID | Kết quả nghiệm thu quan sát được | Phần còn thiếu / chủ sở hữu |
|---|---|---|
| E1 | Nhận file nhân sự `.xlsx` được hỗ trợ; chọn đúng sheet/hàng/cột. Mẫu hiện có nhận đủ bốn tiêu đề. Ba workbook báo cáo ca khác được từ chối rõ; không tạo tên rác. | SPEC định dạng/giới hạn và bộ mẫu kiểm thử; SPEC_AUTHOR. |
| E2 | Xem trước thống kê/dòng nguồn/trường sẽ lưu đúng; xử lý thiếu tên, trùng tên/mã, tên gần giống và xung đột mã–tên; hủy không thay danh mục/DB. | Thiết kế ánh xạ và bộ kế hoạch nhập; worker/reviewer. |
| E3 | Thêm đúng tên hợp lệ; nhập cùng tập hai lần không tạo trùng; người vắng trong nguồn, tổ/mẫu và báo cáo/revision cũ giữ nguyên. Cảnh báo giới hạn nhận diện chỉ theo tên. | Luồng xác nhận và đối chiếu trước/sau bằng dữ liệu tạm; worker/reviewer. |
| E4 | Danh mục đổi giữa xem trước và xác nhận trả xung đột; đổi context/nguồn DB không ghi nhầm. Lỗi ghi/mất quyền/thiếu chỗ không báo thành công; khôi phục được danh mục trước nhập. | Test lỗi ở ranh giới file/DB/sao lưu và recovery end-to-end; worker/reviewer. |
| E5 | File rỗng/sai định dạng/quá giới hạn/công thức tại ô định danh/đầu vào không hỗ trợ trả lỗi có vị trí; kiểm tra lại phía máy chủ. Không thực thi nội dung từ workbook. | SPEC và chứng cứ lỗi/biên theo đúng bộ đọc chọn trong ADR; worker/reviewer. |
| E6 | Bản đóng gói Windows thực tế: mở ứng dụng → nhập Excel → kiểm tra Chọn người → tạo/lưu ca → thoát/mở lại → xuất báo cáo; danh mục mới tồn tại và ca cũ giữ nguyên. Bộ release áp dụng qua; không có skip bị tính là PASS. | Nhóm phát triển tự nghiệm thu và reviewer độc lập trước khi mời người dùng góp ý; commit/EXE/platform và file thử gắn với kết quả. |
| E7 | Ánh xạ tổ được xác nhận; người ca ngày/nhãn lạ không bị tự đưa vào Ca 1–2–3; nhập lặp không trùng; mẫu áp dụng vẫn xem trước và giữ kỳ DAY/NIGHT của báo cáo. | SPEC R3 và kiểm chứng bằng tổ/mẫu giả lập; worker/reviewer. |

## 6. Kiểm chứng và nghiệm thu do nhóm phát triển sở hữu

Trước BUILD, nhóm phát triển chuẩn bị fixture giả lập không có dữ liệu cá nhân và kết quả mong đợi xác định bằng hợp đồng/đếm thủ công: người mới, người đã có, trùng mã, trùng tên khác mã, thiếu tên, Unicode tổ hợp, mã có 0 đầu, nhiều sheet/hàng tiêu đề, nhãn ca lạ, file vượt trần, công thức tại ô định danh. Nguồn nhân sự thực tế chỉ được dùng theo phạm vi được phép; không đưa dữ liệu cá nhân vào repo.

Ba lớp nghiệm thu: (1) parser/kế hoạch nhập/API/lưu/recovery đúng tiêu chí, (2) nhóm phát triển chạy luồng người dùng trên đúng artifact Windows đóng gói và review độc lập, (3) sau đó mới mời người dùng nhận xét độ phù hợp nghiệp vụ. Người dùng không phải tự thiết kế test kỹ thuật hoặc dò lỗi parser.

Giá trị cần đo tại R2: số thao tác và thời gian đưa cùng một danh sách giả lập vào danh mục bằng cách hiện tại so với nhập Excel; số dòng mới/giữ/lỗi phải khớp oracle đã chốt. Chưa đặt ngưỡng thời gian hoặc hứa phần trăm cải thiện khi chưa đo. Mã nhân viên chuẩn và khả năng nhập các bảng ca khác chưa được chứng minh bởi kết quả R2.

Chi phí khảo sát hiện tại: thời gian chuẩn bị/review toàn phiên chưa đo đầy đủ, giữ UNKNOWN; không quy đổi ra tiền. Dừng khảo sát sau 20 tệp nguồn và bốn workbook trong snapshot, không khảo sát toàn bộ hệ thống cảng. Không viết thêm trình đọc thử hoặc benchmark chỉ để hoàn thiện đánh giá; bước tiếp theo là SPEC có giới hạn. Nếu SPEC phát hiện phải đổi mô hình người/lịch sử mới giải quyết được yêu cầu, dừng phần ghi danh mục và đưa quyết định vào R4 thay vì vá tiếp theo tên.

## 7. Trạng thái khảo sát ban đầu và phần chưa biết

Đã có bản đối chiếu và roadmap nháp để xem xét. Chưa chốt nhu cầu cập nhật danh sách thực tế/tần suất, file nào là nguồn nhân sự chuẩn, phạm vi bộ phận của đầu vào và các ca không rõ có cần đưa vào tổ nào. Đây là các đầu vào nghiệp vụ cần xác định trước khi khóa SPEC tương ứng, không chặn việc lập kế hoạch từ các file đã có. Đội phát triển tự chốt cách đọc file, API, lỗi và test trong phạm vi được duyệt; không chuyển lựa chọn kỹ thuật sang người dùng.

Phần nhập Excel, gợi ý tổ, mã nhân viên và nhập bảng phân ca đều chưa được triển khai/nghiệm thu. EXE/UI và các đợt D2–D5 của roadmap gốc giữ phần tồn đọng riêng. Chưa có review độc lập R2 cho triển khai, chưa có quyền BUILD/dependency/migration/network hoặc đồng bộ hai dự án từ tài liệu này. Trạng thái sản phẩm không được nâng bằng kết quả kiểm tra tài liệu.

Cập nhật thực thi: WO exact SHA fbc56001358dc6ada77207a780b9d213d8c152b8ee808b95a5a9efdce7419f20 đã được Astra chấp nhận; pre-dispatch7/7 và doctor29/29 đạt, Terra/Sol đã nhận BUILD. Hồ sơ giao việc tại commit c855598. Chưa tiêu chí E1–E6 nào được tính hoàn tất trước khi nhận bằng chứng triển khai và E6 Windows. Phần khảo sát mục7 ở trên là lịch sử, không phải quyền thực thi hiện tại.

## Acceptance criteria — PNI

Milestone này chỉ nhận đợt nhập danh mục E1–E6, không thay kết luận của toàn bộ roadmap sản phẩm. Các tiêu chí bắt buộc được ghi theo SPEC hiện hành; reviewer không hạ E6 thành headless/source-only để đóng việc.

| ID | Required observable result |
|---|---|
| E1 | Flat personnel XLSX inspect, sheet/header/column selection and positive four-header eligibility work; unsupported formats and the three report-shaped inputs are refused without writes. |
| E2 | Source-row preview, exact counts, exclusions, ambiguity/errors, transient fields and name-only limitation are visible and correct; inspect/cancel are write-free. |
| E3 | Additive owner saves only selected new names, repeated input is no-op, inactive/inconsistent state refuses safely, unrelated catalog bytes/team/template semantics and historical report/revisions are preserved. |
| E4 | Main-store/auth/context/digest/single-use300s plan checks hold; backup/write/DB/restore/concurrent-edit failures report honest verified recovery or recovery-required state with retained backup. |
| E5 | Bounded actual ZIP/XML and transport parsing, strict relationships/formulas/types/physical limits and escaped rendering are verified, including actual hardened parser provenance in packaged runtime. |
| E6 | Applicable full release groups and real exact clean committed Windows EXE headed import/picker/report/save/restart/export flow pass against synthetic oracle, with old-report preservation, artifact hashes, skips disclosed and independent reviewer acceptance; manual/import time and steps compared without invented threshold. |

## Current PNI coverage

```cvf-milestone-coverage-json
{
  "schemaVersion": "cvf.milestoneCoverage@1.0.0",
  "authority": {
    "path": "docs/roadmaps/TAN_THUAN_PORT_ADOPTION.md",
    "heading": "## Acceptance criteria — PNI",
    "sha256": "4ecc56d72ee80a5c2b3af7be5e4a41bf1e54cda5d3f292d3150c4441f33f4008"
  },
  "milestone": {
    "id": "PNI",
    "consumer": "Bai-container shift-report operator",
    "outcome": "Safely add selected people from flat Excel and use them in a persisted/exported shift report",
    "checkpoint": {
      "trigger": "Before independent implementation dispatch and before exact Windows EXE acceptance",
      "owner": "Root orchestrator with independent Astra review",
      "decision": "Require all E1-E6 scope/evidence and exact admission; keep E7 and unrelated product gaps open"
    }
  },
  "phase": "PLAN",
  "action": {
    "kind": "PLAN",
    "selected": [
      "E1",
      "E2",
      "E3",
      "E4",
      "E5",
      "E6"
    ],
    "owner": "Root orchestrator",
    "output": "docs/specs/PERSONNEL_EXCEL_IMPORT.md and docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md",
    "budgetMinutes": 30,
    "stop": "Stop on changed business/data/effect boundary or unresolved independent design blocker",
    "next": "Independently assess exact implementation packet and require successful fresh pre-dispatch"
  },
  "rows": [
    {
      "id": "E1",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Source independently accepted and full technical suite passed; packaged/native E6 corroboration and product criterion disposition pending",
      "owner": "Terra integration / Sol reader and native proof / Astra independent review",
      "destination": "docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md",
      "evidence": [
        {
          "path": "docs/reviews/personnel-import-20261108/source-candidate-review.json",
          "sha256": "ae28f86112f1a4a649efeeddba6d0cecb878d03030bf13632d118b3ae6652563"
        },
        {
          "path": "docs/reviews/personnel-import-20261108/release-final.json",
          "sha256": "88c6174142b1c3ad1bf52c02d06ee16456f906078bafa61a302938b08f25a2e2"
        }
      ]
    },
    {
      "id": "E2",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Source independently accepted and full technical suite passed; packaged/native E6 corroboration and product criterion disposition pending",
      "owner": "Terra integration / Sol reader and native proof / Astra independent review",
      "destination": "docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md",
      "evidence": [
        {
          "path": "docs/reviews/personnel-import-20261108/source-candidate-review.json",
          "sha256": "ae28f86112f1a4a649efeeddba6d0cecb878d03030bf13632d118b3ae6652563"
        },
        {
          "path": "docs/reviews/personnel-import-20261108/release-final.json",
          "sha256": "88c6174142b1c3ad1bf52c02d06ee16456f906078bafa61a302938b08f25a2e2"
        }
      ]
    },
    {
      "id": "E3",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Source independently accepted and full technical suite passed; packaged/native E6 corroboration and product criterion disposition pending",
      "owner": "Terra integration / Sol reader and native proof / Astra independent review",
      "destination": "docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md",
      "evidence": [
        {
          "path": "docs/reviews/personnel-import-20261108/source-candidate-review.json",
          "sha256": "ae28f86112f1a4a649efeeddba6d0cecb878d03030bf13632d118b3ae6652563"
        },
        {
          "path": "docs/reviews/personnel-import-20261108/release-final.json",
          "sha256": "88c6174142b1c3ad1bf52c02d06ee16456f906078bafa61a302938b08f25a2e2"
        }
      ]
    },
    {
      "id": "E4",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Source independently accepted and full technical suite passed; packaged/native E6 corroboration and product criterion disposition pending",
      "owner": "Terra integration / Sol reader and native proof / Astra independent review",
      "destination": "docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md",
      "evidence": [
        {
          "path": "docs/reviews/personnel-import-20261108/source-candidate-review.json",
          "sha256": "ae28f86112f1a4a649efeeddba6d0cecb878d03030bf13632d118b3ae6652563"
        },
        {
          "path": "docs/reviews/personnel-import-20261108/release-final.json",
          "sha256": "88c6174142b1c3ad1bf52c02d06ee16456f906078bafa61a302938b08f25a2e2"
        }
      ]
    },
    {
      "id": "E5",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Source independently accepted and full technical suite passed; packaged/native E6 corroboration and product criterion disposition pending",
      "owner": "Terra integration / Sol reader and native proof / Astra independent review",
      "destination": "docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md",
      "evidence": [
        {
          "path": "docs/reviews/personnel-import-20261108/source-candidate-review.json",
          "sha256": "ae28f86112f1a4a649efeeddba6d0cecb878d03030bf13632d118b3ae6652563"
        },
        {
          "path": "docs/reviews/personnel-import-20261108/release-final.json",
          "sha256": "88c6174142b1c3ad1bf52c02d06ee16456f906078bafa61a302938b08f25a2e2"
        }
      ]
    },
    {
      "id": "E6",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Build tooling/source accepted; exact clean committed Windows EXE and headed consumer/persistence/export/time evidence not yet executed",
      "owner": "Terra integration / Sol reader and native proof / Astra independent review",
      "destination": "docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md",
      "evidence": [
        {
          "path": "docs/reviews/personnel-import-20261108/source-candidate-review.json",
          "sha256": "ae28f86112f1a4a649efeeddba6d0cecb878d03030bf13632d118b3ae6652563"
        },
        {
          "path": "docs/reviews/personnel-import-20261108/release-final.json",
          "sha256": "88c6174142b1c3ad1bf52c02d06ee16456f906078bafa61a302938b08f25a2e2"
        }
      ]
    }
  ],
  "supportingWork": [],
  "conclusions": {
    "tranche": "PENDING",
    "trancheSummary": "Source candidate independently accepted; clean commit, exact EXE and E6 native evidence remain required before terminal disposition",
    "trancheEvidence": [],
    "product": "PENDING",
    "productSummary": "PNI first slice not yet product-accepted; E7 and original roadmap gaps separately owned",
    "acceptance": [],
    "owner": "Root orchestrator"
  }
}
```
