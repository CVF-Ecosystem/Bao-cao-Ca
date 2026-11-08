# Review tài liệu đối chiếu và roadmap

Status: DRAFT_REVIEW
Risk: R1
Worker: Root
Reviewer: Root

Ngày: 2026-11-08. Đây là review tài liệu do cùng một agent chuyển vai trò từ ORCHESTRATOR sang REVIEWER sau khi rehydrate trạng thái DESIGN. Không phải review độc lập cho triển khai R2, không phải nghiệm thu tính năng.

## Căn cứ và kết luận

Đã rà bản nháp `docs/roadmaps/TAN_THUAN_PORT_ADOPTION.md` với nguồn/hash trong `source-observations.json`, roadmap gốc và các phần danh mục/tổ/mẫu đang có. Bản nháp phù hợp để tiếp tục thiết kế SPEC có giới hạn. Phạm vi sản phẩm vẫn là đề xuất; mọi tiêu chí E1–E7 chưa được chốt/nghiệm thu. Machine coverage dùng PLAN/VERIFY với authority null để tránh tạo quyền triển khai từ khảo sát.

Các điểm đã kiểm tra: không lặp bộ chọn người/tìm không dấu/mẫu phân công; không đánh đồng tổ Ca 1–2–3 với DAY/NIGHT; không suy chức danh thành vị trí phân công; phân biệt component Excel có preview với handler admin đang dùng; không coi log Demo là lưu báo cáo đầu/cuối ca bền vững; thừa nhận bộ nhập chưa chắc tương thích ngay với mẫu nhân viên; không mang các bảng nghiệp vụ ô gộp vào bộ nhập danh mục phẳng; không hứa định danh/cập nhật qua nhiều lần nhập khi chỉ lưu họ tên.

Kiểm tra trường được lưu, dữ liệu nguồn không giữ lại, kiểm soát trùng/đổi tên, hủy/xung đột/nhập lặp, giới hạn file và phục hồi đã có đích xử lý trong SPEC và tiêu chí dự kiến. Không làm thêm parser thử hoặc chuyển chi phí QA kỹ thuật sang người dùng. Không có ước lượng tiết kiệm hay cam kết phát hành được suy từ việc tồn tại mã nguồn.

## Phần còn mở và nơi xử lý

- Chọn file nguồn nhân sự chuẩn, phạm vi Bãi và ý nghĩa nhãn nhóm/ca: chủ nghiệp vụ cùng SPEC_AUTHOR, trước khi khóa R1. Mẫu đã có đủ để lập đề xuất, chưa đủ chứng minh cách dùng thực tế.
- ADR bộ đọc Excel, định dạng/giới hạn/API, xử lý source ID và failure boundaries: đội phát triển, trước work order R2. Chưa chọn dependency hay sửa schema.
- Nhu cầu trùng tên/đổi tên cần danh tính chuẩn và bảng vị trí-người cho nhập mẫu: R4, chưa mở triển khai.
- Bằng chứng runtime parser, Windows/native/EXE, hiệu năng thao tác và review độc lập: thực hiện trong đợt triển khai được phép, chưa có ở khảo sát này.

## Phạm vi kiểm tra tài liệu

Kiểm tra JSON/coverage/continuity/catalog và diff phục vụ tài liệu. Snapshot trước/sau cho 36 tệp nguồn/kiểm thử của ứng dụng không đổi; các tệp nguồn tham khảo đã hash không đổi trong cửa sổ khảo sát. Không chạy lại suite ứng dụng vì không sửa mã; không dùng kiểm tra tài liệu làm bằng chứng ứng dụng chạy đúng hoặc provider governance. Các kết quả lệnh tài liệu được giữ tại `document-checks.json`; bằng chứng bộ đọc workbook chỉ là cấu trúc và tiêu đề đã lọc, không phải tính toán bằng Excel.

Sai sót công cụ trong khảo sát được giữ đúng giới hạn: lần in đầu của script đọc cấu trúc workbook gặp lỗi encoding cp1252; lần sau xuất JSON ASCII thành công. Không có workbook được ghi lại. Một lần chèn acknowledgment dùng ngữ cảnh patch không khớp và không sửa tệp; patch sau chèn đúng. Đây không phải lỗi/tái sửa chức năng sản phẩm.

## Trả lại vai trò điều phối

Root trở lại ORCHESTRATOR/SESSION_SYNC_STEWARD sau review tài liệu và đồng bộ hồ sơ; COMMIT_STEWARD chỉ giữ bộ thay đổi tài liệu được nêu rõ. Tài liệu vẫn DRAFT, trạng thái hoạt động DESIGN. Không có yêu cầu chờ operator xác nhận kỹ thuật và không có quyền BUILD từ review này.
