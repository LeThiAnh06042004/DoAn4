from AI.keywords.kw_runner import run_keyword_prompt

PROMPT = """Bạn là AI chuyên gia sinh keyword test automation cho hệ thống KDT. 

YÊU CẦU BẮT BUỘC PHẢI TUÂN THỦ 100%:
- CHỈ TRẢ VỀ MỘT JSON ARRAY THUẦN TÚY, KHÔNG CÓ BẤT KỲ CHỮ NÀO KHÁC TRƯỚC HOẶC SAU.
- Mỗi phần tử là một string: "TÊN_KEYWORD_IN_HOA (Nghĩa tiếng Việt ngắn gọn)".
- Tên keyword phải IN HOA toàn bộ, dùng _ nối từ, không dấu cách.
- Ví dụ đúng: ["OPEN_URL (Mở một URL mới)", "INPUT_TEXT (Nhập văn bản vào ô tìm kiếm)"]
- Bắt đầu ngay bằng [ và kết thúc bằng ], không có dấu phẩy thừa, không xuống dòng thừa, không giải thích, không bảng, không markdown.

Yêu cầu sinh keyword ĐẦY ĐỦ:
- PHẢI sinh ít nhất 1 keyword riêng cho MỖI ràng buộc dưới đây (theo đúng số thứ tự).
- Nếu ràng buộc có nhiều trường hợp (ví dụ thiếu + chứa ký tự đặc biệt), sinh keyword riêng cho từng trường hợp.
- Ưu tiên keyword mang tính nghiệp vụ cao, dễ hiểu, phù hợp cho KDT (Keyword Driven Testing).

Ràng buộc nghiệp vụ (PHẢI sinh đủ cho từng số):
1. Ô tìm kiếm không được để trống (validation khi rỗng) → keyword kiểm tra và thông báo lỗi.
2. Ô tìm kiếm không được chỉ chứa khoảng trắng → keyword kiểm tra khoảng trắng.
3. Ô tìm kiếm có độ dài tối đa 255 ký tự → keyword kiểm tra vượt quá giới hạn.
4. Sau khi nhập từ khóa hợp lệ → nhấn nút Search → hiển thị combobox sắp xếp sản phẩm
5. Trường hợp không có sản phẩm khớp → hiển thị thông báo "Không tìm thấy sản phẩm nào khớp với lựa chọn của bạn." → keyword kiểm tra thông báo không kết quả.
6. Tìm kiếm theo chữ hoa/thường (case-insensitive) → keyword kiểm tra kết quả không phân biệt hoa thường.
7. Tìm kiếm với ký tự đặc biệt hoặc dấu → keyword kiểm tra xử lý ký tự đặc biệt.

Hãy sinh danh sách keyword test ĐẦY ĐỦ theo từng ràng buộc trên."""

if __name__ == "__main__":
    run_keyword_prompt(PROMPT, __file__)