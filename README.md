# Sổ Báo Cáo Ca • Bãi Container Tân Thuận

[![Phiên bản](https://img.shields.io/badge/phiên_bản-1.10.1-blue.svg)](tai_lieu/THAY_DOI_V1_10_1.txt)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Phụ thuộc](https://img.shields.io/badge/phụ_thuộc-Zero_Dependencies-success.svg)](#yêu-cầu-hệ-thống)
[![Cơ sở dữ liệu](https://img.shields.io/badge/CSDL-SQLite3_WAL-orange.svg)](#cơ-chế-bảo-vệ-và-an-toàn-dữ-liệu)
[![Hệ điều hành](https://img.shields.io/badge/HĐH-Windows_Desktop-informational.svg)](#hướng-dẫn-sử-dụng)

Ứng dụng quản lý ca trực, ghi chép nhật ký, bàn giao ca, theo dõi sản lượng xếp dỡ container và xuất báo cáo biểu mẫu chuyên dụng tại **Bãi Container Cảng Tân Thuận**.

---

## Mục lục

- [Tổng quan](#tổng-quan)
- [Tính năng nổi bật](#tính-năng-nổi-bật)
- [Cơ chế bảo vệ và an toàn dữ liệu](#cơ-chế-bảo-vệ-và-an-toàn-dữ-liệu)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
  - [1. Khởi động ứng dụng](#1-khởi-động-ứng-dụng)
  - [2. Thiết lập ban đầu](#2-thiết-lập-ban-đầu)
  - [3. Nhập và chốt báo cáo ca](#3-nhập-và-chốt-báo-cáo-ca)
  - [4. Xuất báo cáo và tổng hợp tháng](#4-xuất-báo-cáo-và-tổng-hợp-tháng)
  - [5. Khôi phục dữ liệu](#5-khôi-phục-dữ-liệu)
- [Đóng gói thành tệp thực thi (.EXE)](#đóng-gói-thành-tệp-thực-thi-exe)
- [Kiểm thử phần mềm](#kiểm-thử-phần-mềm)
- [Lịch sử các phiên bản](#lịch-sử-các-phiên-bản)
- [Tác giả và thông tin dự án](#tác-giả-và-thông-tin-dự-án)

---

## Tổng quan

**Sổ Báo Cáo Ca** được phát triển nhằm giải quyết triệt để bài toán bàn giao và quản lý số liệu ca trực tại hiện trường cảng biển:
- **100% Hoạt động Offline**: Không phụ thuộc đường truyền Internet hoặc máy chủ đám mây, đảm bảo vận hành ổn định 24/7 tại các trạm/bãi máy tính hiện trường.
- **Không cài đặt phức tạp (Zero External Dependencies)**: Ứng dụng chạy thuần túy bằng thư viện chuẩn của Python 3.9+ kết hợp giao diện Web cục bộ (Local Web UI), hoặc chạy dưới dạng 1 file EXE độc lập.
- **An toàn dữ liệu tuyệt đối**: Tích hợp cơ chế bảo vệ, chống ghi đè nhầm dữ liệu trắng, sao lưu đa tầng (Snapshot SQLite, giữ lịch sử phiên bản, kiểm tra mã băm tệp đính kèm).

---

## Tính năng nổi bật

### 1. Giao diện nhập ca chia tab trực quan
- **4 Tab chức năng**:
  - **Nhân sự**: Phân công vị trí, tổ trưởng, phụ trách chung, các bộ phận trực thuộc (hiện dấu cảnh báo nếu chưa phân công phụ trách chung).
  - **Công việc**: Ghi nhận chi tiết các hạng mục công việc trong ca, phương tiện, thiết bị, sản lượng container (`f20`, `f40`, `e20`, `e40`).
  - **Ghi chú & Bàn giao**: Ghi chú sự vụ phát sinh, tồn bãi, nội dung bàn giao chi tiết cho ca sau.
  - **Ảnh & Biên bản**: Đính kèm hình ảnh hiện trường, biên bản sự vụ (lưu trực tiếp trong SQLite dạng BLOB mã hóa băm an toàn).
- **Phím tắt thao tác nhanh**:
  - `Alt + 1 / 2 / 3 / 4`: Chuyển nhanh giữa các tab.
  - `Ctrl + S`: Lưu nháp ca trực.
  - `Ctrl + P`: Xem trước và in ấn báo cáo chuẩn A4 ngang.
  - `Esc` hoặc bấm ra ngoài nền / nút `×`: Đóng nhanh hộp thoại.
- **Thanh tác vụ ghim đáy**: Luôn cố định nút **Lưu nháp** và **Chốt ca**, giúp thao tác thuận tiện dù trang báo cáo dài.

### 2. Nghiệp vụ ca trực chặt chẽ
- Hỗ trợ linh hoạt: **Ca 1**, **Ca 2**, **Ca 3** và **Ca ngày**.
- **Chốt ca & Quản lý lịch sử**:
  - Sau khi chốt ca, mọi thao tác sửa đổi bắt buộc phải nhập lý do và được lưu thành một phiên bản lịch sử (revision) riêng.
  - Tự động gộp các lần lưu nháp liên tiếp nhằm tối ưu hóa dung lượng cơ sở dữ liệu.
- **Mẫu phân công ca**: Thiết lập sẵn danh sách nhân sự theo tổ đội, tự động điền nhanh cho từng ca trực chỉ với một thao tác.

### 3. Nhập danh mục nhân sự thông minh từ Excel
- Hỗ trợ nhập trực tiếp tệp danh sách nhân sự từ Excel thông thường (`.xlsx`).
- Tự động nhận diện cột họ tên, mã nhân viên (hỗ trợ số nguyên, chuỗi có số 0 ở đầu), chức vụ.
- Có màn hình **Xem trước (Preview)**, chọn lọc dòng, kiểm tra trùng lặp trước khi xác nhận ghi vào danh mục.

### 4. Xuất biểu mẫu báo cáo chuẩn
- **Xuất Excel chi tiết từng ca**: Điền tự động vào tệp mẫu `mau/MAU_BAO_CAO.xlsx`, giữ nguyên công thức và định dạng chuẩn của cảng.
- **Xuất tổng hợp cả tháng**: Trích xuất dữ liệu sản lượng và phân công toàn bộ ca trực trong tháng ra bảng tính tổng hợp.
- **In ấn chuẩn A4 ngang**: Hỗ trợ in trực tiếp từ trình duyệt ra máy in hoặc lưu PDF, có đầy đủ tiêu đề, chân trang, đánh số trang `Trang x/y` và khối chữ ký bàn giao.

---

## Cơ chế bảo vệ và an toàn dữ liệu

Cơ chế an toàn dữ liệu là một trong những điểm trọng tâm nhất của hệ thống:

```
[Máy tính bãi / Local PC]
       │
       ├─► [DB Chính: DU_LIEU/BAO_CAO_CA.db] (SQLite WAL mode + OS File Lock)
       │         │
       │         ├─► [Sao lưu nhanh (Quick Backup)] ──► DU_LIEU/SAO_LUU_AN_TOAN/
       │         │
       │         └─► [Sao lưu đầy đủ (Full Backup)] ──► Ổ đĩa ngoài / Thư mục Cloud đồng bộ
       │
       └─► [Cơ chế khôi phục độc lập: KHOI_PHUC_DU_LIEU.pyw]
```

1. **Khóa chống xung đột đa phiên (OS File Lock)**: Ngăn chặn việc mở cùng lúc 2 phiên ứng dụng trên cùng một thư mục dữ liệu, triệt tiêu nguy cơ ghi đè làm hỏng tệp tin.
2. **Sao lưu đa tầng thông minh (Tiered Retention)**:
   - Giữ tối đa 10 bản sao lưu trong ngày.
   - Giữ bản sao lưu cuối cùng của mỗi ngày trong 30 ngày gần nhất.
   - Giữ bản sao lưu cuối tháng cho các tháng trước đó.
3. **Tiếp nhận cơ sở dữ liệu an toàn**:
   - Khi chuyển dữ liệu từ máy khác sang, hệ thống tự động đối chiếu mã nhận diện (Database ID), hiển thị số lượng báo cáo và phạm vi ngày để người dùng xác nhận trước khi tiếp nhận, tuyệt đối không âm thầm tạo DB trắng đè lên dữ liệu cũ.
4. **Chế độ xem DB kiểm tra / bổ sung (Read-Only Viewer)**:
   - Cho phép mở một bản sao DB bất kỳ để tra cứu số liệu mà không làm thay đổi hoặc ảnh hưởng đến DB vận hành chính.
5. **Xoay vòng nhật ký (Log Rotation)**:
   - Các tệp nhật ký trong `DU_LIEU/*.log` tự động xoay vòng khi đạt 1 MB, lưu giữ 3 bản cũ, không làm đầy ổ đĩa.

---

## Cấu trúc thư mục

```
SO_BAO_CAO_CA/
├── MO_BAO_CAO_CA.pyw        # Điểm khởi chạy chính (giao diện ẩn console CMD)
├── KHOI_PHUC_DU_LIEU.pyw    # Công cụ khôi phục dữ liệu độc lập
├── CHAY_KIEM_TRA_LOI.bat    # Khởi động kèm cửa sổ dòng lệnh để xem lỗi (nếu có)
├── HUONG_DAN.txt            # Hướng dẫn chi tiết vận hành & cập nhật phiên bản
├── pyproject.toml           # Cấu hình ruff linter
├── requirements.txt         # Thông tin yêu cầu môi trường
│
├── ma_nguon/                # Mã nguồn xử lý nghiệp vụ chính (Python)
│   ├── BAO_CAO_CA.py        # Điểm vào chương trình, quản lý vòng đời ứng dụng
│   ├── BAO_VE_DU_LIEU.py    # Quản lý sao lưu, snapshot, khôi phục và tiếp nhận DB
│   ├── LUU_TRU.py           # Quản lý CSDL SQLite, schema 4, lưu trữ tệp đính kèm
│   ├── MAY_CHU.py           # Máy chủ HTTP nội bộ (localhost API, token bảo mật)
│   ├── NGHIEP_VU.py         # Kiểm tra tính hợp lệ dữ liệu, định dạng số lượng
│   ├── PERSONNEL_XLSX.py    # Xử lý đọc & nhận diện danh sách nhân sự từ Excel
│   ├── QUAN_LY_DANH_MUC.py  # Quản lý danh mục nhân viên, vị trí, công việc, tàu
│   ├── MAU_PHAN_CONG.py     # Quản lý mẫu phân công ca trực
│   ├── BAO_CAO_EXCEL.py     # Xuất bảng báo cáo ca và tổng hợp tháng
│   ├── XUAT_EXCEL.py        # Điền dữ liệu vào biểu mẫu Excel mẫu
│   └── THIET_LAP.py         # Cấu hình hệ thống, phiên bản, hằng số
│
├── giao_dien/               # Giao diện người dùng Web cục bộ (HTML/CSS/JS)
│   ├── giao_dien.html       # Bộ khung HTML giao diện chính
│   └── tai_nguyen/          # Tệp tĩnh: CSS, JavaScript tương tác, phím tắt
│
├── mau/                     # Biểu mẫu và danh mục mẫu khởi tạo ban đầu
│   ├── MAU_BAO_CAO.xlsx     # Mẫu bảng báo cáo ca chuẩn
│   └── DANH_MUC_MAU/        # Tệp danh mục mẫu (NHAN_VIEN, CONG_VIEC, TAU, VI_TRI)
│
├── cong_cu/                 # Tiện ích đóng gói và kiểm thử
│   ├── CHAY_KIEM_THU.bat    # Kịch bản chạy toàn bộ bộ kiểm thử tự động
│   └── TAO_FILE_EXE.bat     # Kịch bản đóng gói thành file SO_BAO_CAO_CA.exe
│
├── kiem_thu/                # Bộ kiểm thử tự động (Python unittest & JavaScript)
│
└── tai_lieu/                # Tài liệu phân tích kỹ thuật, API và nhật ký thay đổi
```

---

## Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10, Windows 11 hoặc Windows Server.
- **Môi trường chạy**:
  - **Dùng file EXE**: Không cần cài đặt bất kỳ phần mềm nào khác.
  - **Dùng mã nguồn Python**: Cần **Python 3.9** trở lên (chỉ dùng thư viện chuẩn có sẵn, không cần `pip install` thêm gói phụ thuộc).
- **Trình duyệt**: Microsoft Edge hoặc Google Chrome (để hiển thị giao diện Web cục bộ).

---

## Hướng dẫn sử dụng

### 1. Khởi động ứng dụng
- **Cách 1 (Khuyên dùng)**: Bấm đúp chuột vào tệp `MO_BAO_CAO_CA.pyw`. Ứng dụng sẽ tự động kích hoạt máy chủ nội bộ và mở giao diện trên trình duyệt mặc định mà không hiện cửa sổ đen dòng lệnh.
- **Cách 2**: Bấm đúp vào tệp `CHAY_KIEM_TRA_LOI.bat` để chạy kèm cửa sổ dòng lệnh (hữu ích khi muốn theo dõi chi tiết lỗi khởi động).
- **Cách 3**: Chạy tệp `SO_BAO_CAO_CA.exe` nếu đã đóng gói.

### 2. Thiết lập ban đầu
1. Truy cập menu **Cài đặt**:
   - Cập nhật danh sách nhân sự, vị trí làm việc, các đầu mục công việc tại mục **Danh mục nhân sự / công việc**.
   - Thiết lập các mẫu phân công sẵn cho từng ca tại mục **Mẫu phân công Ca 1–2–3 / ca ngày**.
   - Cập nhật danh sách tàu làm hàng tại mục **Danh sách tàu**.
2. Thiết lập bảo vệ dữ liệu:
   - Vào menu **Dữ liệu** > **Bảo vệ dữ liệu / Khôi phục**.
   - Bấm **Chọn thư mục...** và chọn một thư mục trên ổ đĩa khác (hoặc thư mục Google Drive / OneDrive đồng bộ trên máy).
   - Bấm **Lưu nơi dự phòng**.

### 3. Nhập và chốt báo cáo ca
1. Bấm nút **＋ Nhập ca mới** trên thanh điều hướng bên trái.
2. Chọn Ngày và Ca làm việc (Ca 1, Ca 2, Ca 3 hoặc Ca ngày).
3. Điền thông tin qua 4 tab:
   - Tab **Nhân sự**: Chọn mẫu phân công để điền nhanh hoặc điều chỉnh từng vị trí.
   - Tab **Công việc**: Nhập sản lượng container theo từng kích cỡ và trạng thái (`f20`, `f40`, `e20`, `e40`), phương tiện thực hiện.
   - Tab **Ghi chú & bàn giao**: Ghi nhận các vấn đề kỹ thuật, tai nạn, sự vụ hoặc lưu ý quan trọng.
   - Tab **Ảnh & biên bản**: Tải lên hình ảnh hiện trường hoặc tài liệu sự vụ đính kèm.
4. Bấm **Lưu nháp** trong quá trình nhập liệu (hệ thống cũng có cơ chế tự động lưu).
5. Khi kết thúc ca trực, kiểm tra lại số liệu và bấm **Chốt ca**.

### 4. Xuất báo cáo và tổng hợp tháng
- **Xem / In báo cáo**: Tại danh sách báo cáo, chọn ca cần in và bấm **Xem / In** (hoặc nhấn `Ctrl + P`).
- **Xuất Excel từng ca**: Chọn ca cần xuất và bấm **Xuất Excel** để tạo file `.xlsx` theo mẫu chuẩn.
- **Xuất Excel cả tháng**: Vào **Dữ liệu** > **Xuất Excel cả tháng**, chọn tháng cần báo cáo để trích xuất toàn bộ dữ liệu.

### 5. Khôi phục dữ liệu
Trong trường hợp cần quay lại một bản sao lưu trước đó hoặc khôi phục sau sự cố:
- **Khôi phục trong ứng dụng**: Vào **Dữ liệu** > **Bảo vệ dữ liệu / Khôi phục**, chọn bản sao lưu muốn dùng, kiểm tra số ca và phạm vi ngày, gõ chữ `KHOI PHUC` vào ô xác nhận và bấm **Khôi phục**.
- **Khôi phục độc lập khi không mở được ứng dụng chính**: Thoát hẳn chương trình, bấm đúp vào tệp `KHOI_PHUC_DU_LIEU.pyw` để mở công cụ phục hồi chuyên dụng.

---

## Đóng gói thành tệp thực thi (.EXE)

Để đóng gói ứng dụng thành một tệp `.exe` duy nhất cho người dùng cuối không có sẵn môi trường Python:

1. Đảm bảo máy tính đã cài Python và có kết nối Internet để tải PyInstaller.
2. Bấm đúp vào tệp `cong_cu\TAO_FILE_EXE.bat`.
3. Kịch bản sẽ tự động đóng gói và xuất file `SO_BAO_CAO_CA.exe` ngay tại thư mục gốc của chương trình.

> **Lưu ý**: Thư mục dữ liệu `DU_LIEU` và danh mục `DANH_MUC` luôn nằm bên ngoài cạnh tệp `.exe`. Khi nâng cấp phiên bản EXE mới, chỉ cần thay thế tệp `.exe` mà không làm mất dữ liệu cũ.

---

## Kiểm thử phần mềm

Ứng dụng được trang bị bộ kiểm thử tự động toàn diện kiểm tra cả logic backend Python và hành vi frontend JavaScript:

```bash
# Chạy toàn bộ kiểm thử tự động
cong_cu\CHAY_KIEM_THU.bat

# Hoặc kiểm tra cú pháp và tính toàn vẹn mã nguồn (Python tiêu chuẩn)
python kiem_thu\KIEM_THU_MA_NGUON.py
```

---

## Lịch sử các phiên bản

- **Bản 1.10.1 (08/11/2026)**:
  - Linh hoạt hóa trình nhập Excel nhân sự thông thường: Hỗ trợ tiêu đề không dấu, tự gợi ý hàng/cột, nhận diện mã nhân viên dạng chuỗi/số, giữ nguyên số 0 đầu.
  - Cải tiến trải nghiệm hộp thoại (Modal UX): Bổ sung nút đóng `×`, hỗ trợ phím `Esc` và bấm ra ngoài nền (backdrop) để thoát nhanh có cảnh báo nếu biểu mẫu đã sửa.
- **Bản 1.10.0 (08/11/2026)**:
  - Nâng cấp Schema 4 CSDL, tối ưu hóa lưu vết lịch sử phiên bản.
  - Bổ sung phím tắt toàn diện (`Alt+1..4`, `Ctrl+S`, `Ctrl+P`).
  - Chuẩn hóa in ấn khổ A4 ngang chuyên nghiệp (tiêu đề, chân trang, khối chữ ký).
  - Phân tầng bảo vệ dữ liệu Quick Backup và Full Backup.
- **Bản 1.9.0 (08/11/2026)**:
  - Tái cấu trúc thư mục gọn gàng (`ma_nguon/`, `giao_dien/`, `mau/`, `tai_lieu/`, `cong_cu/`, `kiem_thu/`).
  - Giao diện chia 4 tab thông minh, thanh tác vụ ghim đáy.
  - Phân trang danh sách báo cáo và tối ưu hóa xử lý khi cơ sở dữ liệu lớn.
- **Các bản 1.8.x**:
  - Bổ sung hệ thống bảo vệ dữ liệu, sao lưu định kỳ, kiểm tra toàn vẹn DB bằng SQLite Backup API, xử lý tương thích lỗi file descriptor trên Windows.

---

## Tác giả và thông tin dự án

- **Phát triển bởi**: Mr Ân / Tân Thuận
- **Đơn vị**: Bãi Container • Cảng Tân Thuận
- **Hệ sinh thái**: [CVF Ecosystem](https://github.com/CVF-Ecosystem)
- **Kho lưu trữ chính thức**: [https://github.com/CVF-Ecosystem/Bao-cao-Ca.git](https://github.com/CVF-Ecosystem/Bao-cao-Ca.git)
