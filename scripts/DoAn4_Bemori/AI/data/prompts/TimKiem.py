from AI.data.prompt_runner import run_prompt

PROMPT = """Chức năng: Tìm kiếm sản phẩm gấu bông

Cấu trúc mỗi item:
- keyword (từ khoá tìm kiếm): string

Yêu cầu:
- Sinh các item keyword đa dạng, bao gồm rỗng, chữ, số, ký tự đặc biệt, tiếng Việt có dấu, độ dài gần hoặc vượt 255 ký tự.
- Có cả hợp lệ và không hợp lệ.
- Không lặp lại các item giống nhau.

Tên folder: TimKiem
Sinh các file dữ liệu: yaml, json, txt"""

if __name__ == "__main__":
    run_prompt(PROMPT)