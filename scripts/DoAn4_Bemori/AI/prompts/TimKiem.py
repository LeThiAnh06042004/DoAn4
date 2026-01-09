from AI.prompt_runner import run_prompt

PROMPT = """
Chức năng: Tìm kiếm sản phẩm gấu bông

- Cấu trúc mỗi item:
  + keyword

- Quy tắc dữ liệu:
  + keyword có thể rỗng
  + keyword có thể chứa chữ, số
  + keyword có thể chứa ký tự đặc biệt
  + keyword có thể chứa tiếng Việt có dấu
  + keyword có tối đa 255 ký tự

- Tên folder: TimKiem

- Sinh các file dữ liệu: yaml
"""

if __name__ == "__main__":
    run_prompt(PROMPT)
