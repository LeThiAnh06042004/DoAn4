from AI.keywords.kw_runner import run_keyword_prompt

PROMPT = """Bạn là AI chuyên sinh keyword test automation cho hệ thống KDT.

YÊU CẦU BẮT BUỘC (PHẢI TUÂN THỦ 100%):
- CHỈ TRẢ VỀ MỘT JSON ARRAY THUẦN TÚY. KHÔNG CÓ BẤT KỲ CHỮ NÀO KHÁC TRƯỚC/SAU.
- Mỗi phần tử là object JSON với đúng 4 field:
  - "method_name": TÊN KEYWORD IN HOA bằng TIẾNG ANH (dùng _ nối từ).
  - "display_name_vi": Tên tiếng Việt ngắn gọn.
  - "arguments": Mảng tham số (rỗng [] nếu không có).
  - "description_vi": Mô tả chi tiết bằng tiếng Việt.
- Bắt đầu ngay bằng [ và kết thúc bằng ]. Không giải thích, không bảng, không markdown.

Yêu cầu sinh keyword:
- PHẢI sinh ĐỦ 1 keyword cho mỗi ràng buộc dưới đây (theo đúng số thứ tự).
- Nếu ràng buộc có nhiều trường hợp (ví dụ thiếu + chứa ký tự đặc biệt), sinh keyword riêng cho từng trường hợp.
- Ưu tiên keyword mang tính nghiệp vụ cao, dễ hiểu.

Ràng buộc nghiệp vụ (PHẢI sinh đủ cho từng số):
1. Nội dung bình luận không được bỏ trống hoặc chỉ toàn ký tự trắng → xác minh thông báo "Bạn chưa nhập bình luận."
2. Họ tên không được bỏ trống hoặc chỉ toàn ký tự trắng → xác minh thông báo "Bạn chưa nhập tên."
3. Họ tên tối đa 255 ký tự → kiểm tra vượt quá độ dài.
4. Số điện thoại không được bỏ trống hoặc chỉ toàn ký tự trắng → xác minh thông báo "Bạn chưa nhập số điện thoại."
5. Số điện thoại chỉ được chứa số (không ký tự khác) → xác minh thông báo "Số điện thoại chỉ bao gồm những số."
6. Số điện thoại phải từ 10 ký tự trở lên → xác minh thông báo "Số điện thoại phải có ít nhất 10 số."
7. Nhập đầy đủ hợp lệ → nhấn Gửi bình luận → hiển thị thông báo "Gửi bình luận thành công."

Hãy sinh keyword ĐẦY ĐỦ theo từng ràng buộc trên."""

if __name__ == "__main__":
    run_keyword_prompt(PROMPT, __file__)