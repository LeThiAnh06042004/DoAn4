from AI.prompt_runner import run_prompt

PROMPT = """
Chức năng: Bình luận sản phẩm

- Cấu trúc mỗi item:
  + noi_dung
  + ho_ten
  + so_dien_thoai

- Quy tắc dữ liệu:
  + noi_dung có thể rỗng
  + noi_dung tối đa 255 ký tự
  + ho_ten có thể rỗng
  + so_dien_thoai có thể rỗng
  + so_dien_thoai tối đa 11 chữ số
  + Có dữ liệu hợp lệ và không hợp lệ

- Tên folder: BinhLuan

- Sinh các file dữ liệu: csv
"""

if __name__ == "__main__":
    run_prompt(PROMPT)
