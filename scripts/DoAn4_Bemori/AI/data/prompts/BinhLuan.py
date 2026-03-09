from AI.data.prompt_runner import run_prompt

PROMPT = """Chức năng: Bình luận sản phẩm

Cấu trúc mỗi item:
- noi_dung (nội dung bình luận): string
- ho_ten (họ tên): string
- so_dien_thoai (số điện thoại): string

Quy tắc dữ liệu (PHẢI SINH ĐẦY ĐỦ CÁC CASE):
- noi_dung: có thể rỗng, chỉ khoảng trắng, chứa tiếng Việt có dấu, chứa ký tự đặc biệt, chứa số, tối đa 255 ký tự
- ho_ten: có thể rỗng, chỉ khoảng trắng, chứa tiếng Việt có dấu, chứa ký tự đặc biệt, tối đa 255 ký tự
- so_dien_thoai: có thể rỗng, chỉ khoảng trắng, chứa chữ cái/ký tự đặc biệt (không hợp lệ), chỉ số nhưng <10 chữ số, chỉ số >=10 chữ số, tối đa 11 chữ số

Yêu cầu:
- Sinh đủ các case hợp lệ và không hợp lệ cho từng field (rỗng, khoảng trắng, Unicode, special char, vượt max_length, SDT <10 số, SDT có chữ...).
- Sinh đa dạng item, không lặp lại.
- Đảm bảo bao phủ hết các ràng buộc trên.

Tên folder: BinhLuan
Sinh các file dữ liệu: csv, json, xml"""

if __name__ == "__main__":
    run_prompt(PROMPT)