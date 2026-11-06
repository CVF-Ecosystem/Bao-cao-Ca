# Báo cáo Codex — Đợt 1, bản 1.9.1

Ngày thực hiện: 2026-11-06. Phạm vi: [GIAO_VIEC_CODEX_DOT1.md](GIAO_VIEC_CODEX_DOT1.md).

Điều phối/review: Codex. Worker: Terra 6.1; Sol 6.1 Medium hỗ trợ khi cần.

## 1. Trạng thái

D1-1…D1-4 đã hoàn thành và được review. Mã nguồn đã tăng lên **1.9.1**, schema vẫn **3**. Sau tăng phiên bản: **3 lượt liên tiếp đều 154/154 Python**, **5/5 bộ JS**, smoke launcher nguồn qua. Chưa commit/push hoặc phát hành EXE.

| Hạng mục | Trạng thái | Phạm vi còn lại |
|---|---|---|
| D1-1 | Đã làm, nghiệm thu mã nguồn | Chưa thử request cỡ 100 MiB/8 GiB; không thuộc tiêu chí test 5 MiB đợt này. |
| D1-2 | Đã làm, nghiệm thu mã nguồn và benchmark | Chưa đo trên HDD/máy bãi. |
| D1-3 | Đã làm, nghiệm thu mô phỏng ổ đầy và API | Chưa làm đầy ổ đĩa vật lý thật. |
| D1-4 | Mã nguồn/cổng build xong; nghiệm thu EXE còn một phần | Build và smoke EXE khi cây Git sạch; không commit/build lách cổng. |

## 2. Benchmark trước thay đổi

Lệnh: `python cong_cu\DO_HIEU_NANG.py --profile vua --repeat 3 --json <TEMP>/codex_dot1_baseline.json`.

Windows build 26200 (Python in chuỗi nền tảng `Windows-10-10.0.26200-SP0`), Python 3.11.9, 16 luồng CPU; loại ổ chưa xác định. DB giả lập trong thư mục tạm: 240 ca, 4.800 revision/4.800 payload khác nhau, 40 blob duy nhất, DB 125 MB. Không có dự phòng ngoài. Seed 20261106. Lần 1 không bảo đảm bộ nhớ đệm nguội hoàn toàn.

| Thành phần | Trước: lần 1 | Trước: trung vị các lần sau |
|---|---:|---:|
| Chép DB bằng SQLite Backup API | 0,40 s | 0,31 s |
| quick_check | 0,09 s | 0,08 s |
| integrity_check | 0,09 s | 0,09 s |
| Duyệt JSON reports + revisions | 0,34 s | 0,33 s |
| SHA-256 toàn bộ blob | 0,12 s | 0,13 s |
| Chép byte sang thư mục tạm khác trên cùng ổ | 0,08 s | 0,07 s |
| snapshot đầy đủ | 1,12 s | 0,97 s |
| Protection.backup | 1,12 s | 0,94 s |

| Khởi động theo đường gọi main | Trước |
|---|---:|
| guard_startup | 0,6 s |
| needs_adoption | 0,7 s |
| make_server | 1,8 s |
| Tổng | 3,1 s |

Độ trễ HTTP trước: lưu thường trung vị 0,03 s/tối đa 0,04 s; chốt ca trung vị 1,02 s/tối đa 1,07 s. Tìm kiếm 0,05 s, 230 ca khớp.

## 3. Kết quả sau thay đổi và kiểm thử

### D1-1 — Đã làm

- Terra tái hiện trên Windows, máy chủ/dữ liệu tạm: thân 300 byte thiếu header và thân 5 MiB tới tuyến JSON gây WinError 10053 trước sửa. `Content-Length=abc` trước đó đã thành 400 do khối bắt ValueError chung; thay đổi mới chuẩn hóa thông báo và xử lý thân thật còn dư.
- Xả tối đa 4 MiB và hạn tổng 0,5 giây. Với thân lớn/độ dài không hợp lệ: gửi, flush, đóng chiều ghi trước khi xả. Áp dụng cho GET có body và giữ phản hồi 501 cho PUT/DELETE/HEAD.
- Bỏ cách né dùng thân rỗng ở test API. Có test 100 POST bị từ chối (thiếu header, sai Origin, thiếu cookie), 5 MiB, 100 GET có body, độ dài âm/không số/5.000 chữ số với thân thật, và test trần byte/deadline.
- Lệnh `python -m unittest discover -s kiem_thu -t . -p "KIEM_THU*.py"`: 10/10 lượt đều **129/129 OK**. Thời gian lần lượt: 28,910; 29,700; 31,746; 31,776; 30,855; 29,609; 24,288; 23,580; 24,901; 23,723 giây.
- Cả 5 file `node kiem_thu/KIEM_THU*.js` exit 0 sau hạng mục.
- Hai đợt chạy trước chuỗi nghiệm thu được chủ động dừng để bổ sung kiểm thử theo review; đợt đầu chưa có kết quả, đợt thứ hai có một lượt **128/128 OK** trước khi thêm test deadline thành 129. Không tính các đợt này vào 10 lượt nghiệm thu.
- Thử client gửi thiếu body trên socket thật: yêu cầu khai báo 300 byte bị từ chối nhận 403 JSON sau 0,515 giây; trường hợp khai báo 5 MiB hoặc `abc` được phản hồi trước khi xả. Không suy rộng kết quả 5 MiB thành bảo đảm cho mọi client gửi 100 MiB/8 GiB; máy chủ chủ đích giới hạn việc xả.

### D1-2 — Đã làm

- `guard_startup` trả kết quả kiểm tra kèm dấu thay đổi của DB/WAL/journal. `needs_adoption` và `make_server` dùng lại kết quả khi nguồn chưa đổi; thiếu hoặc dấu cũ thì kiểm tra đầy đủ. Sau hộp thoại khôi phục/tiếp nhận, tạo Protection và kiểm tra lại. `initialize` dùng Store vừa mở, vẫn giữ kiểm tra Store sau khi mở writable/nâng schema.
- Test chạy `main()` thật với vòng phục vụ được mock và gọi `make_server()` trực tiếp: trường hợp ổn định đều **2 lần inspect_db** (DB nguồn một lần, snapshot đích một lần), **3 lần Store.validate/quick_check**. Không giảm kiểm tra snapshot. Root kiểm chứng độc lập mã trước sửa: dùng `git show HEAD:ma_nguon/<file>.py` chép các module vào thư mục tạm, chạy script `python -` bọc đếm lời gọi và mock vòng phục vụ HTTP; kết quả main **4 inspect/6 validate**, direct **2/4**, exit 0. Không đổi working tree hay dữ liệu vận hành để chạy mã cũ.
- Thử thực tế phát hiện SQLite có thể tự tạo WAL rỗng khi inspect một DB WAL đang yên. Cho phép kiểm tra full lại tối đa một lần duy nhất nếu WAL từ không có thành 0 byte, còn DB/journal không đổi. Phải ổn định sau lần hai; mọi thay đổi khác báo dừng. Đây là ngoại lệ có chủ đích với mục tiêu “mỗi DB một lần”, nhằm giữ kiểm tra an toàn.
- Test thêm: nguồn bị ghi, WAL thật có cập nhật, journal, thay DB, đường khác, mất/hỏng DB, DB đổi ngay trong inspect, idle WAL và guard lại sau dialog. Dấu file phát hiện thay đổi thông thường; không thay thế khóa chống tác nhân cố tình khôi phục cả dấu thời gian/file.
- Lệnh benchmark sau sửa: `python cong_cu\DO_HIEU_NANG.py --profile vua --repeat 3`. Cùng bộ dữ liệu/tham số với trước; script đã sửa đường gọi để dùng receipt như main thực tế. Startup **1,7 s**, giảm khoảng **45%** so với 3,1 s. `--repeat 3` lặp từng thành phần; phần startup trong mỗi lệnh chỉ đo một lần, nên chưa phải phân bố thống kê nhiều lần khởi động.

| Thành phần | Sau D1-2: lần 1 | Sau D1-2: trung vị các lần sau |
|---|---:|---:|
| Chép DB bằng SQLite Backup API | 0,35 s | 0,29 s |
| quick_check | 0,08 s | 0,08 s |
| integrity_check | 0,08 s | 0,08 s |
| Duyệt JSON reports + revisions | 0,33 s | 0,33 s |
| SHA-256 toàn bộ blob | 0,13 s | 0,14 s |
| Chép byte sang thư mục tạm khác trên cùng ổ | 0,11 s | 0,09 s |
| snapshot đầy đủ | 0,98 s | 0,95 s |
| Protection.backup | 0,90 s | 0,90 s |

| Khởi động theo đường gọi main | Trước | Sau D1-2 |
|---|---:|---:|
| guard_startup | 0,6 s | 0,7 s |
| needs_adoption | 0,7 s | 0,0 s |
| make_server | 1,8 s | 1,0 s |
| Tổng | 3,1 s | 1,7 s |

HTTP sau D1-2: lưu thường trung vị 0,02 s/tối đa 0,03 s; chốt ca trung vị 1,02 s/tối đa 1,06 s. Tìm kiếm 0,06 s.

- Kiểm thử sau hạng mục: 8/8 test khởi động, full **137/137 Python OK** (21,682 s), **5/5 JS exit 0**.
- Các lần lỗi khi phát triển đã sửa: lần đầu chạy 4 test có một lỗi cleanup vì kết nối SQLite chưa đóng; lần 7 test đầu có một fail và hai error liên quan mutation ghi cùng giá trị, socket chưa đóng và WAL rỗng; lần 7 test tiếp còn một error WAL rỗng. Có một full run bị dừng theo review trước khi có kết quả. Không tính các lần này là nghiệm thu thành công.

### D1-3 — Đã làm

- Preflight dùng `ceil(1,2 × max(DB + WAL trên đĩa, page_count × page_size))`, kiểm tra `shutil.disk_usage` ở tổ tiên đang tồn tại của thư mục đích trước khi tạo snapshot. Tính cả WAL để tránh chỉ lấy file DB chính chưa checkpoint.
- Thiếu tại máy: trả None, cảnh báo error kèm đường đích/số byte cần/còn; giữ cấu hình, last_local/last_external và bản sao cũ, không tạo tmp/prune. `daily_backup` giữ thông báo chi tiết, không cập nhật thời điểm thành công, đánh dấu còn chờ sao lưu. Thiếu ngoài: giữ bản tại máy mới thành công và bản ngoài cũ, cập nhật last_local nhưng giữ last_external.
- Đo nhỏ với DB giả lập 5 blob × 1 MiB đang có WAL: tổng DB+WAL **10.614.936 byte**, snapshot **5.320.704 byte**, tỷ lệ **0,5012**; yêu cầu **12.737.924 byte**. Chọn hệ số 1,2 làm biên dự phòng 20%, chưa phải chứng minh đủ cho mọi tình huống. Dung lượng trống có thể bị tiến trình khác sử dụng sau preflight; lỗi thực tế khi ghi vẫn đi qua xử lý lỗi sao lưu hiện có.
- Test mới mô phỏng đầy tại máy/ngoài, giữ nguyên byte DB và bản sao cũ, không có tmp, cảnh báo `/api/info` đúng và ước lượng có WAL. Targeted 3/3; bộ bảo vệ + V1_9 cũ 38/38; full trước vòng review cuối **142/142 OK** (26,589 s), **5/5 JS exit 0**. Hai test bổ sung lazy WAL của D1-2 có trong lượt 142 này (10 test khởi động tổng cộng).
- Root phát hiện vòng tìm tổ tiên có thể lặp vô hạn nếu root của ổ đích không tồn tại; đã bổ sung chặn ném OSError và test mô phỏng `Path.exists=False` ở mọi cấp. Test biên xác nhận đủ đúng ngưỡng thì sao lưu thành công, thiếu một byte thì từ chối. Sau sửa cuối: targeted **5/5**, full **144/144 Python OK** (22,885 s), **5/5 JS exit 0**.

### D1-4 — Đã làm

- `PHIEN_BAN.json` gồm commit, built_at UTC và version; chỉ sinh trong thư mục tạm khi build và được nhúng qua `--add-data`. API thêm `build{commit,built_at,version}`, nguồn dùng commit `nguon`, EXE thiếu/hỏng metadata dùng `khong-ro`. Giao diện hiện commit cạnh phiên bản bằng textContent.
- `TAO_FILE_EXE.bat` gọi `DONG_GOI.py`: chặn cây bẩn, Git lỗi hoặc HEAD không hợp lệ trước khi cài PyInstaller/tạo metadata; kiểm tra lại trước build. Test repo Git tạm không có HEAD, untracked/staged, Git mất/lỗi và metadata tạm đều qua; không tạo commit để thử.
- Launcher dùng parser chung để ghi log theo đúng `--data-dir`, hỗ trợ cả hai dạng tham số và trả exit code của main. Đổi hướng stdout/stderr có phục hồi khi đóng log. `--no-browser` báo lỗi qua log/console thay cho hộp thoại; `--help` an toàn cp1252 nhờ reconfigure trước parse.
- `python -O cong_cu/KIEM_THU_KHOI.py`: launcher nguồn thật với cwd/data-dir tạm, lấy cookie, gọi info, kiểm tra version/build/log, gọi shutdown, kiểm tra exit 0 và dọn file phiên. Smoke EXE mới yêu cầu `--exe ... --commit <hash> --version 1.9.1` để kiểm đúng commit. Các kiểm tra trong công cụ không bị bỏ qua bởi `python -O`; Windows chạy child ẩn.
- Trước tăng VERSION, full **152/152**, rồi **154/154**, rồi full cuối **154/154 OK** (25,785 s); targeted phát hành cuối **9/9**, 5 bộ JS qua. Không có failure trong các lần Sol chạy; các lượt đầu có ít test hơn vì đang bổ sung theo review. Probe riêng của root với subprocess `--help` không thu được kết quả khi tool yield, không tính là pass; bằng chứng chính là test runpy cp1252 có stub hộp thoại, đã qua.
- `python cong_cu/DONG_GOI.py --check` đã trả exit 1 đúng thông báo cây Git chưa sạch. Chưa build/chạy EXE, không khẳng định smoke EXE đã qua. Đây là giới hạn theo chính cổng build mới, không phải thiếu nền tảng Windows.

### Benchmark toàn bộ mã 1.9.1 cuối đợt

Lệnh: `python cong_cu\DO_HIEU_NANG.py --profile vua --repeat 3 --json <TEMP>/codex_dot1_final.json`. Cùng seed/dataset và không dự phòng ngoài. Máy/loại ổ như trước; lúc đo lượng trống được báo là 13 GB, khác 25 GB ở baseline.

| Thành phần | Trước: lần 1 / sau | 1.9.1 cuối: lần 1 / sau |
|---|---:|---:|
| Chép DB SQLite Backup API | 0,40 / 0,31 s | 0,73 / 0,68 s |
| quick_check | 0,09 / 0,08 s | 0,15 / 0,14 s |
| integrity_check | 0,09 / 0,09 s | 0,15 / 0,13 s |
| Duyệt JSON | 0,34 / 0,33 s | 0,48 / 0,50 s |
| Hash mọi blob | 0,12 / 0,13 s | 0,19 / 0,20 s |
| Chép byte sang thư mục khác cùng ổ | 0,08 / 0,07 s | 0,10 / 0,10 s |
| snapshot full | 1,12 / 0,97 s | 1,57 / 2,24 s |
| Protection.backup | 1,12 / 0,94 s | 1,72 / 1,60 s |

| Khởi động | Trước | Sau D1-2 | 1.9.1 cuối |
|---|---:|---:|---:|
| guard | 0,6 s | 0,7 s | 1,0 s |
| needs_adoption | 0,7 s | 0,0 s | 0,0 s |
| make_server | 1,8 s | 1,0 s | 1,8 s |
| Tổng | 3,1 s | 1,7 s | 2,8 s |

HTTP cuối: lưu thường trung vị 0,01 s/tối đa 0,03 s; chốt ca trung vị 2,23 s/tối đa 2,70 s; tìm kiếm 0,14 s. Seed cuối 51 s so với 22 s trước. Các thành phần đọc/chép/JSON đều chậm hơn ở lượt cuối, chưa xác định nguyên nhân thay đổi điều kiện máy. Không coi mức giảm 45% của lượt D1-2 là cam kết ổn định; số cuối chỉ nhanh hơn khoảng 10%. Số lần kiểm tra đã giảm được ghim bằng test, còn thời gian thực cần kiểm tra trên máy bãi.

### Đối chiếu bổ sung luân phiên trước/sau để giảm ảnh hưởng biến động máy

Root chạy script `python -` trên thư mục tạm: lấy mã trước sửa bằng `git show HEAD:ma_nguon/<file>.py`, tạo một DB qua `seed(Store(...), PROFILES['vua'], Random(20261106))`, rồi chép cùng DB **131.039.232 byte** thành sáu nguồn thử. Mỗi child import bộ module cũ hoặc mới, khởi tạo cấu hình trước đồng hồ, gọi `main(['--quiet','--no-browser','--data-dir',...])` thật với riêng vòng `HTTPServer.serve_forever` được mock để tự thoát. Thứ tự: cũ/mới, mới/cũ, cũ/mới; mỗi lần đều sao lưu full. Không đo thời gian mở trình duyệt/launcher. JSON lưu tại TEMP `codex_dot1_paired_startup.json`.

| Cặp | Trước (1.9.0 từ HEAD) | Sau (1.9.1 hiện tại) |
|---|---:|---:|
| 1 | 3,544 s | 1,833 s |
| 2 (đảo thứ tự) | 4,345 s | 1,931 s |
| 3 | 3,797 s | 1,835 s |
| Trung vị | **3,797 s** | **1,835 s** |

Trung vị giảm **51,7%** trong phép đo đối chiếu này. Đây là bằng chứng rõ hơn cho tác động bỏ kiểm tra trùng so với so hai lượt benchmark cách xa nhau; chưa thay cho nghiệm thu trên máy bãi/HDD hoặc cam kết độ trễ cố định.

## 4. Nghiệm thu cuối và giới hạn

- Sau tăng VERSION 1.9.1, root chạy `python -m unittest discover -s kiem_thu -t . -p "KIEM_THU*.py"` bằng ba subprocess mới liên tiếp: **154/154 OK** mỗi lượt, thời gian unittest **24,817 / 27,059 / 25,560 s** (tổng tiến trình **25,040 / 27,234 / 25,725 s**). Log tại TEMP `codex_dot1_final_tests_{1,2,3}.log`.
- Chạy Node lần lượt cả năm `kiem_thu/KIEM_THU*.js`: **5/5 exit 0**. Đã thêm hợp đồng footer build có/không có metadata và ký tự HTML chỉ hiện dạng text trong Node VM.
- `python -O cong_cu/KIEM_THU_KHOI.py`: **exit 0, version=1.9.1, build=nguon**, gọi launcher thật và shutdown trong thư mục tạm.
- `python cong_cu/DONG_GOI.py --check`: **exit 1 như mong đợi**, `Cay Git con thay doi chua commit; tu choi build.` Không cài PyInstaller hoặc build để vượt cổng này.
- `git diff --check`: **exit 0**; có cảnh báo Git chuẩn hóa CRLF sang LF, không có lỗi khoảng trắng. Root kiểm thêm cú pháp UTF-8 và import thừa cho mọi `cong_cu/*.py`: qua.
- Đính chính: thiếu/sai tháng xuất Excel đã trả 400 trước bản vá (`test_query_parameter_validation`); không sửa lỗi không tồn tại. Root đã ghi đính chính vào tài liệu phản biện cũ. Roadmap phần giới hạn từng nói số đo chỉ có payload giống nhau/Đợt 0 chưa đo, nay đã sửa vì đã có 4.800 payload khác nhau qua Store.save.
- “Mỗi DB một full” áp dụng luồng khởi động ổn định: vẫn full snapshot đích mới; có bounded retry khi SQLite tự tạo WAL rỗng, không dùng cờ bỏ kiểm tra hoặc cache yếu hơn.
- Không đọc/ghi dữ liệu vận hành của workspace. Mọi DB/cấu hình/danh mục/log thử thuộc thư mục tạm; không xóa dữ liệu, không commit/push/PR, không làm các đợt 2–5.
- Chưa kiểm chứng: **EXE 1.9.1**, ổ HDD/máy bãi, DB gần 1 GB, hộp thoại tkinter, trình duyệt đồ họa thật và in/mở Excel thật trong đợt này. Đã kiểm chứng mã Python và launcher nguồn trên Windows; không ghi chung “chưa chạy Windows”.
- Không có quyết định thiết kế đợt 1 đang chờ. Để phát hành EXE tiếp theo cần cây Git sạch theo quy tắc mới, rồi build và smoke đúng commit; chưa được yêu cầu commit nên công việc dừng ở mã nguồn đã kiểm chứng.
