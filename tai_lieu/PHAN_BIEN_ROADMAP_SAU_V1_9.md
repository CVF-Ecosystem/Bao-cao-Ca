# Phản biện roadmap sau 1.9 và định hướng chuẩn bị chạy web

Ngày: 2026-11-06. Người phản biện: Codex.

Tài liệu được phản biện: [ROADMAP_SAU_V1_9.md](ROADMAP_SAU_V1_9.md).

**Đính chính sau kiểm thử Đợt 0/1 (2026-11-06):** nhận định cần sửa lỗi thiếu/sai `month` ở PB-05 được rút lại. `KIEM_THU_API.ApiContract.test_query_parameter_validation` xác nhận thiếu/sai tháng đã trả 400; không sửa endpoint này trong 1.9.1. Benchmark bản 1 ghi revision trực tiếp bằng SQL nên 40 revision/ca có thật; lưu ý ở PB-04 về bỏ qua payload giống nhau áp dụng cho kịch bản dùng Store.save, không phủ nhận số dòng SQL của bản 1. Kế hoạch hiện hành là roadmap bản 2.2 và [báo cáo Đợt 1](BAO_CAO_CODEX_DOT1.md); các đề xuất bên dưới giữ lại theo ngữ cảnh phản biện bản 1.

Phạm vi: đối chiếu roadmap với mã Python, giao diện JavaScript và công cụ chạy/build hiện tại. Các số đo 1,15 GB, 65,6 giây và kết quả 116 kiểm thử Python/5 bộ JS là số liệu do roadmap cung cấp; chưa tái lập trong lượt phản biện này. Đây là đề xuất để Claude sửa kế hoạch trước khi triển khai, chưa phải quyết định đổi kiến trúc hay thay đổi mã nguồn.

## 1. Kết luận gửi Claude

Roadmap đúng hướng về tối ưu dựa trên phép đo, bảo toàn dữ liệu, duy trì chạy ngoại tuyến và trì hoãn chuyển kiến trúc lớn. Có thể dùng làm cơ sở chia việc sau khi sửa các điều kiện an toàn ở P1-1, P1-2, P1-3 và tách thao tác dọn blob khỏi bản vá API nhỏ.

Nên bổ sung một nhánh chuẩn bị kiến trúc ngay từ bây giờ: làm rõ ranh giới giao diện, API, dịch vụ ứng dụng và lưu trữ; tách phần chạy trên máy cá nhân. Giữ một kho mã, một ứng dụng triển khai và giao diện JavaScript hiện tại. Chuyển sang web nhiều người dùng cần một giai đoạn riêng có đăng nhập, phân quyền, trạng thái theo phiên và kiểm thử đồng thời.

## 2. Các nội dung đồng ý

- Đưa benchmark tái lập được vào kho, đo trên máy vận hành trước khi chốt ngưỡng hiệu năng.
- Giữ kiểm tra đầy đủ khi tiếp nhận/khôi phục DB, bảo toàn lịch sử sau chốt và kiểm tra xung đột khi nhập bổ sung.
- Bổ sung truy vết bản EXE, kiểm thử khói, hướng dẫn xử lý sự cố và khôi phục thử.
- Tiếp tục dùng giao diện hiện tại; việc đổi framework phải có lợi ích và tiêu chí cụ thể.
- Giữ nguyên lịch sử cũ khi thử nghiệm gộp tự lưu mới.

## 3. Các điểm cần sửa trước khi code

### PB-01 — P1-3: Không tự xóa mọi DB kiểm tra theo tuổi tệp

**Bằng chứng:** `MAY_CHU.py` cho phép `/api/enable-corrections` chuyển bản sao trong `DB_KIEM_TRA` thành DB có thể ghi. Phần sửa bổ sung được lưu vào chính bản sao này. File không đang mở vẫn có thể là nơi duy nhất chứa phần bổ sung chưa xuất.

**Yêu cầu sửa:** phân loại bản xem tạm, bản đang đối chiếu nhập và bản đã bật bổ sung. Chỉ tự dọn loại được chứng minh là có thể tạo lại. Bản đã bật bổ sung cần được giữ, hoặc lưu trữ/xuất có xác minh trước khi người vận hành chủ động dọn. Không chỉ dựa vào thời gian sửa tệp hoặc trạng thái đang mở.

**Nghiệm thu:** sửa bản bổ sung → thoát ứng dụng → giả lập quá hạn → khởi động lại: dữ liệu vẫn còn. Không dọn nguồn của lần nhập đang chờ. Test chỉ dùng thư mục tạm.

### PB-02 — P1-1: Giảm mức kiểm tra phải kèm giữ bản đã kiểm tra đầy đủ

**Bằng chứng:** `Protection.backup()` tạo snapshot rồi gọi `prune()`. Nếu snapshot chỉ kiểm tra nhanh, blob hỏng có thể được chép sang bản mới, còn các bản tốt cũ bị chính sách giữ bản loại dần.

**Yêu cầu sửa:**

- Ghi nhận riêng bản và thời điểm vượt kiểm tra đầy đủ thành công; quy tắc dọn phải giữ bản này đến khi có bản thay thế đã kiểm tra đầy đủ.
- Quy định hành vi khi full thất bại: không cập nhật mốc thành công, giữ bản tốt đã biết, báo lỗi rõ; không quảng bá bản kiểm tra nhanh thành bản đã kiểm tra đầy đủ.
- Thay cam kết “phát hiện trong tối đa khoảng một ngày” bằng lịch kiểm tra khi ứng dụng hoạt động. Quá hạn thì thực hiện ở lần chạy/thao tác tiếp theo; thể hiện lần kiểm tra thành công gần nhất.
- Làm rõ “tối đa một lần/ngày” so với thao tác Sao lưu ngay, tiếp nhận và khôi phục. Kiểm tra bắt buộc theo thao tác phải được ưu tiên hơn giới hạn lịch tự động.
- Nếu cache hash đã kiểm tra, cache chỉ hỗ trợ kiểm tra tăng thêm; kiểm tra đầy đủ định kỳ vẫn phải đọc lại mọi blob. Khóa cache theo nguồn DB và vô hiệu hóa khi khôi phục/tiếp nhận; tên hash không chứng minh byte hiện tại vẫn nguyên vẹn.

**Nghiệm thu:** tạo bản full tốt → làm hỏng blob → tạo nhiều bản quick và chạy prune → bản full tốt vẫn còn, full mới thất bại và trạng thái phản ánh đúng. Có test qua ngày, khởi động sau nhiều ngày và thay nguồn DB.

### PB-03 — P1-2: Chốt ngữ nghĩa tự lưu và mốc lưu tay

**Bằng chứng:** `save(manual, reason)` ở giao diện hiện gửi report/version/reason, chưa gửi loại lưu. `_save_report()` dùng cùng lý do mặc định “Lưu nháp” cho tự lưu và lưu tay. Khi payload không đổi, hàm trả về trước khi thêm revision.

**Yêu cầu sửa:**

- Truyền loại thao tác rõ qua API; máy chủ kiểm tra trạng thái để quyết định thao tác nào được gộp. Không suy luận từ câu chữ trong `reason`.
- Quy định lưu tay khi nội dung không đổi có đóng mốc tự lưu hiện tại hay không. Khuyến nghị giữ mốc đó, để tự lưu kế tiếp không ghi đè mốc người dùng vừa lưu tay.
- Quy định biên gộp khi đổi người nhập/phiên làm việc; không gộp qua lưu tay, thêm tệp, chốt ca, sửa sau chốt hoặc trong DB bổ sung.
- Giữ `reports.version` phục vụ chống ghi đè. Đặc tả cách cập nhật version của revision được gộp để bản cuối vẫn khớp báo cáo và luồng nhập bổ sung không bị sai.
- Sửa nghiệm thu “40 lần tự lưu còn ≤ 3 revision”: số dòng phụ thuộc số mốc lưu tay/đính kèm/chốt và các biên gộp. Hãy mô tả một chuỗi thao tác cụ thể và số revision mong đợi.

Không ép yêu cầu “không đổi schema” nếu metadata cần cấu trúc rõ. `normalize()` hiện dựng lại payload theo danh sách trường cho phép, nên metadata tự thêm sẽ bị bỏ nếu không thay thiết kế. Nhét metadata vào payload còn có thể tác động phép so sánh nội dung ở `correction_plan()`. Nếu dùng schema mới, phải có migration, bản sao trước nâng cấp và quy tắc tương thích DB mang đi giữa các phiên bản.

**Nghiệm thu:** thêm test tự lưu → lưu tay không đổi nội dung → tự lưu tiếp; đổi người nhập; hai cửa sổ cùng version; lịch sử version có khoảng trống; xuất bản sao/bật bổ sung/nhập lại; mọi bản sửa sau chốt được giữ.

### PB-04 — P0/P1-1: Làm rõ phép đo và ngưỡng nghiệm thu

Roadmap ghi riêng `Store`/`quick_check` mất 6,8 giây nhưng đặt mục tiêu toàn bộ sao lưu thường ≤ 5 giây, vẫn có chép DB và kiểm tra nhanh. Chưa có căn cứ để coi ngưỡng này đạt được trên cùng điều kiện.

**Yêu cầu sửa:**

- Benchmark xuất cấu hình máy/ổ nếu biết, phiên bản Python, kích thước và phân bố dữ liệu, có bật dự phòng ngoài hay không, số lần lặp và điều kiện lần chạy đầu/các lần sau.
- Dữ liệu giả lập cần ghi rõ kích thước payload, số revision, số blob duy nhất và tần suất thay đổi; 40 lần lưu không đổi sẽ không tạo đủ revision vì code đã bỏ qua payload giống nhau.
- Đo tách: chép DB, quick_check, integrity_check, duyệt JSON, hash blob và chép ra ổ ngoài. Đo cả luồng khởi động thực tế, tránh cộng số đo bị trùng đường gọi.
- Đo thời gian từ bấm Lưu/Chốt đến nhận phản hồi. API hiện gọi sao lưu trước khi trả kết quả, nên độ trễ này ảnh hưởng trực tiếp thao tác của người dùng.
- Chốt ngưỡng sau khi tái lập, so cả tỷ lệ cải thiện và thời gian thực trên máy vận hành. “Nửa ngày” ở P0 chỉ là ước lượng, chưa bao gồm thời gian tiếp cận máy bãi.

### PB-05 — P1-4: Tách bản vá API và dọn blob

Sửa thiếu/sai `month` là bản vá nhỏ, cần kiểm tra chuỗi năm-tháng hợp lệ và trả lỗi 400. Dọn blob là thay đổi xóa dữ liệu, nên có mã hạng mục và kiểm thử riêng.

Trước khi xóa blob, xét tham chiếu từ reports, revisions và correction_base; bảo vệ blob đang chờ gắn vào báo cáo; xử lý trường hợp cùng hash được tải lại nhưng `uploaded_at` vẫn cũ do `INSERT OR IGNORE`. Thực hiện kiểm tra tham chiếu và xóa trong transaction phù hợp, có bản sao được xác minh trước đợt dọn. Không mặc định xóa ngay trong mỗi lần full.

Xóa hàng SQLite không đồng nghĩa kích thước file giảm ngay. Phải phân biệt dung lượng được tái sử dụng trong DB với dung lượng trả lại ổ đĩa; thao tác thu gọn file, nếu cần, là việc bảo trì riêng có yêu cầu thời gian và chỗ trống.

### PB-06 — Điều chỉnh các kết luận và điều kiện kiến trúc

- Điểm 7,3/10 và 3,5/10 cần thang chấm nếu giữ lại; hiện phù hợp làm nhận xét tham khảo.
- Sửa “rủi ro không phải tính đúng đắn” thành “các vấn đề quan sát được tập trung ở hiệu năng/dung lượng; chưa loại trừ lỗi tính đúng đắn”.
- Tách ảnh ra file không xử lý phần revisions ~659 MB trong baseline. Chép thêm ảnh mới cũng chưa tạo thành cơ chế sao lưu hoàn chỉnh: cần manifest, kiểm tra, giữ phiên bản và gói khôi phục nhất quán với DB.
- Mốc ~3 GB là tín hiệu đo lại, chưa đủ để quyết định chuyển máy chủ hoặc đổi DB. Cần căn cứ số người ghi đồng thời, thời gian phản hồi, sao lưu/khôi phục và khả năng vận hành.
- P2-1: `os_user` có ích ở bản chạy cá nhân; trên web nó thường là tài khoản chạy dịch vụ. Cần dành chỗ cho danh tính người dùng đã xác thực khi thiết kế audit.

## 4. Có nên refactor frontend/backend ngay bây giờ?

**Có: chuẩn bị ranh giới kiến trúc bằng những bước nhỏ ngay trong các phần đang sửa.** Dự án đã có frontend HTML/CSS/JS và backend Python giao tiếp HTTP. Phần cần cải thiện là trách nhiệm bên trong hai phía, đặc biệt việc handler đang điều phối cả dữ liệu, phiên làm việc và tác vụ trên máy cá nhân.

Mục tiêu trước mắt: một ứng dụng có các module rõ trách nhiệm, chạy được như hiện tại và có thể thay lớp phục vụ HTTP sau này. Một máy chủ vẫn có thể phục vụ cả giao diện lẫn `/api` trên cùng địa chỉ. Chưa cần tách hai dự án, hai máy chủ triển khai hay thêm bộ công cụ frontend.

### 4.1. Ranh giới đề xuất

```text
Trình duyệt
  Giao diện: điều hướng, nhập liệu, trạng thái màn hình
  API client: JSON, upload/download, lỗi và xung đột
          |
          v
HTTP adapter: đọc request, xác thực, kiểm quyền, ánh xạ lỗi
          |
          v
Dịch vụ ứng dụng: lưu/chốt ca, bổ sung, xuất, sao lưu
          |
          +-- Nghiệp vụ: chuẩn hóa và các quy tắc báo cáo
          +-- Lưu trữ: Store/SQLite và transaction
          +-- Tác vụ nền tảng: tệp, bản sao, đồng hồ, thông tin người thực hiện

Khởi chạy trên máy cá nhân: mở trình duyệt, tkinter, khóa phiên, thoát tool
Khởi chạy máy chủ web sau này: cấu hình máy chủ, phiên người dùng, vận hành dịch vụ
```

Giữ tên và vị trí thư mục hiện tại khi chưa cần đổi. Một cấu trúc tên tiếng Anh hoặc nhiều interface mới tự nó không làm ứng dụng dễ triển khai web hơn.

### 4.2. Việc nên chuẩn bị ngay

| Mục | Thay đổi có giới hạn | Tiêu chí hoàn thành |
|---|---|---|
| K0 — Hợp đồng API | Ghi request/response, lỗi 400/403/404/409/500, version chống ghi đè, context nguồn dữ liệu và loại thao tác lưu. Ghi cả upload/download ngoài hàm `api()` hiện tại. | Có tài liệu API và test hành vi trọng yếu; giao diện hiện tại tiếp tục dùng được. |
| K1 — Tách dịch vụ ứng dụng | Bắt đầu từ luồng đang thay đổi như lưu/chốt ca. Handler chuyển request đã đọc sang dịch vụ; dịch vụ gọi Store và chính sách sao lưu. | Gọi được ca sử dụng trong test mà không dựng HTTP; transaction báo cáo + revision giữ nguyên. |
| K2 — Tách cấu hình và tác vụ máy cá nhân | Đưa đường dẫn dữ liệu/tài nguyên vào cấu hình khởi tạo; truyền phần ngữ cảnh cần dùng. Giữ mở trình duyệt/tkinter ở lớp khởi chạy cá nhân. | Khởi chạy bằng thư mục tạm không chạm dữ liệu thật; dịch vụ nghiệp vụ không gọi hộp thoại hay mở trình duyệt. |
| K3 — Tách frontend theo chức năng | Khi sửa phần tương ứng, tách API client và logic thuần về lưu/chốt, phân công, tra cứu/xuất khỏi phần dựng DOM. Thay dần event nội tuyến ở khu vực đã chạm. | Kiểm thử luồng cũ qua; không làm mất nội dung đang nhập, tự lưu, xử lý lỗi hoặc xung đột. |
| K4 — Danh tính và khả năng sử dụng | Dịch vụ nhận thông tin người thực hiện từ phía máy chủ; phân biệt tên tự khai và danh tính xác thực. Giao diện đọc khả năng được cấp thay vì suy ra từ chế độ hiển thị. | Bản cá nhân vẫn hoạt động; máy chủ quyết định quyền, dữ liệu giao diện không tự cấp quyền. |

Triển khai K0 trước P1-2; thực hiện K1/K2 trong các thay đổi có liên quan; chia K3 thành các phần nhỏ. Chỉ thêm lớp trung gian khi có trách nhiệm cụ thể, tránh dựng sẵn hệ thống plugin hoặc repository tổng quát cho mọi bảng.

### 4.3. Điểm phải xử lý riêng trước khi chạy web nhiều người

1. **Trạng thái nguồn dữ liệu đang dùng chung toàn máy chủ.** Hiện `server.app['store']`, `context` và `pending_import` là biến dùng chung. Một người mở DB kiểm tra có thể đổi nguồn cho mọi người. Khi chạy web, gắn workspace/nguồn dữ liệu và lần đối chiếu vào phiên người dùng, kiểm tra quyền trên mỗi request; hoặc giới hạn chức năng này thành công cụ quản trị riêng. Không tái sử dụng nguyên biến toàn cục hiện tại.
2. **Đăng nhập và audit.** Cookie/token khởi chạy hiện phục vụ một phiên cục bộ. Bản web cần phiên riêng, danh tính người dùng, vai trò và quyền với từng thao tác/dữ liệu. Khi nhập lịch sử ngoại tuyến, giữ người sửa gốc và ghi riêng người thực hiện nhập về.
3. **Chức năng quản trị máy chủ.** Khôi phục DB, chọn thư mục dự phòng, tiếp nhận DB và shutdown là quyền quản trị. Nút Thoát tool trên bản web chuyển thành kết thúc phiên; không cho người dùng thông thường dừng máy chủ chung. Khôi phục cần chế độ bảo trì phối hợp mọi phiên.
4. **Đồng thời và độ trễ.** Máy chủ hiện dùng `HTTPServer`, xử lý request tuần tự; sao lưu/full check chạy trong luồng xử lý. Cần chọn cơ chế phục vụ web và điều phối tác vụ dài, kiểm tra transaction, khóa, lỗi version và khả năng báo trạng thái công việc. Không chỉ đổi sang nhiều luồng rồi coi là hoàn tất.
5. **Dữ liệu và tệp ở phía máy chủ.** Trình duyệt không chọn trực tiếp ổ đĩa của máy chủ như người vận hành cục bộ. Thiết kế upload/download, hạn mức, quyền đọc tệp và luồng xuất/nhập theo vai trò. Có thể tiếp tục dùng SQLite nếu phép đo và mô hình ghi đáp ứng; giữ transaction nghiệp vụ khi thay tầng lưu trữ sau này.
6. **Vận hành và kiểm chứng.** Bản web cần HTTPS, cấu hình host phù hợp, quản lý phiên, nhật ký, sao lưu/khôi phục và kiểm thử nhiều người bằng trình duyệt thật. Kiểm thử khói EXE vẫn phục vụ bản cá nhân. Mở cổng ra LAN/Internet chỉ thực hiện sau khi các điều kiện của bản web đã được đáp ứng.

Mục tiêu “chuẩn bị sẵn để lên web” nên hiểu là tái sử dụng được giao diện và nghiệp vụ với ranh giới rõ, đồng thời biết chính xác phần phải bổ sung. Việc đổi địa chỉ lắng nghe không hoàn thành chuyển đổi này.

## 5. Thứ tự điều chỉnh roadmap đề xuất

| Đợt | Nội dung | Điều kiện nghiệm thu |
|---|---|---|
| Chuẩn bị | P0 benchmark; K0 hợp đồng API; sửa các tiêu chí PB-01 đến PB-06; bổ sung kiểm thử hiện trạng cần thiết. | Tái lập được số đo, thống nhất chính sách giữ bản và ngữ nghĩa lịch sử. |
| Bản vá ổn định | Sửa month; bỏ kiểm tra trùng; kiểm tra dung lượng; truy vết phát hành/kiểm thử khói theo điều kiện kho. | Kiểm thử hồi quy qua, có số đo trước/sau; chưa giảm mức kiểm tra khi chưa có cơ chế giữ bản full tốt. |
| Tối ưu sao lưu | P1-1 đã sửa theo PB-02; K1/K2 tại phần liên quan. | Giữ được bản full tốt khi quick chứa lỗi; xử lý thất bại rõ; đạt ngưỡng đã đo lại. |
| Tối ưu lịch sử | P1-2 đã đặc tả theo PB-03; metadata/migration nếu cần. | Lưu tay, chốt ca, hai cửa sổ và vòng xuất/nhập bổ sung đúng; không gộp lịch sử cũ. |
| Bảo trì dữ liệu | Dọn bản xem tạm/blob theo PB-01/PB-05; khôi phục thử; hoàn thiện hướng dẫn. | Chứng minh giữ được phần bổ sung chưa xuất và mọi blob còn cần. |
| Chuẩn bị web tiếp | Tiếp tục K3/K4 theo phần cần sửa; ghi quyết định cho chế độ local/web. | Có ranh giới sử dụng lại được và bộ tiêu chí web nhiều người, chưa buộc thay framework/DB. |
| Bản web khi có nhu cầu | Xác thực, quyền, nguồn dữ liệu theo phiên, phục vụ đồng thời, tác vụ dài và vận hành. | Hai người thao tác độc lập, không lẫn DB; ghi đồng thời xử lý xung đột; người thường không khôi phục/shutdown máy chủ; thử khôi phục thành công. |

Không nên gom mọi tối ưu, gộp lịch sử, dọn dữ liệu và refactor vào một lần phát hành. Số phiên bản cụ thể chốt theo phạm vi thay đổi và tương thích DB sau khi hoàn thiện thiết kế.

## 6. Đề nghị Claude phản hồi trước triển khai

1. Sửa roadmap theo từng phản biện, nêu rõ điểm đồng ý/không đồng ý và căn cứ mã nguồn hoặc phép đo.
2. Chốt chính sách giữ bản full tốt và quy tắc bảo vệ DB bổ sung chưa xuất.
3. Đặc tả loại lưu, mốc lưu tay không đổi nội dung và lựa chọn lưu metadata/migration trước P1-2.
4. Bổ sung K0–K4 thành các việc nhỏ, giới hạn phạm vi để giữ ứng dụng hiện tại chạy ổn định.
5. Nêu rõ nhu cầu tương lai là web nội bộ hay Internet, số người dùng/điểm nhập đồng thời và có cần tiếp tục dùng ngoại tuyến khi mất mạng. Các yêu cầu này quyết định phạm vi bản web; chưa cần chặn việc chuẩn bị ranh giới kiến trúc hiện tại.

Tài liệu này chỉ bổ sung phản biện và định hướng thiết kế. Chưa thay đổi mã, schema, phiên bản ứng dụng hoặc dữ liệu vận hành.
